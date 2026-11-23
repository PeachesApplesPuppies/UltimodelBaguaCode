"""Triadic HEX v0.1 — exact ternary tree and deduplicating DAG archiver.

Each internal node joins three consecutive children. Leaves choose the smallest
complete encoding among raw, zlib/Brotli, HEX 6+2, XOR, and bitshuffle views.
Duplicate leaf blocks and identical subtrees are stored once. The archive
carries SHA256 digests, lengths, node references, codec IDs, and a root digest.

This is a byte archive, *not* a new video codec or universal compressor.
Requires brotli and numpy (through transforms.py).
"""
from __future__ import annotations
import argparse, hashlib, json, os, struct, tempfile, zlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import brotli
from transforms import TRANSFORMS
from emergency_break import BreakController, StopRequested, install_break_signals, restore_break_signals
from closed_state import ClosedState

MAGIC = b'ULTRIAD1'
HEADER = struct.Struct('>8sBBQII32s')  # magic, version, max-depth, byte-len, nodes, root, sha256
NODE = struct.Struct('>BQ32s')        # kind, byte-len, sha256 of uncompressed bytes
LEAF = struct.Struct('>BBI')         # transform, compressor, payload length
BRANCH = struct.Struct('>III')       # exactly 3 child node IDs, in source order
MAX_SOURCE = 256 * 1024 * 1024  # single-file prototype, not a large-file streaming codec
MAX_NODES = 1_000_000
MAX_DEPTH = 12
MAX_PAYLOAD = MAX_SOURCE + (1 << 20)
METHODS = {'raw':0, 'hex6+2':1, 'xor':2, 'xor+hex6+2':3, 'bitshuffle':4}
CODECS = {'store':0,'zlib':1,'brotli':2}
R_METHODS = {i:k for k,i in METHODS.items()}
R_CODECS = {i:k for k,i in CODECS.items()}
CANDIDATES = [('raw','store'),('raw','zlib'),('raw','brotli'),('hex6+2','brotli'),
              ('hex6+2','zlib'),('xor','zlib'),('xor+hex6+2','zlib'),('bitshuffle','zlib')]


def digest(raw): return hashlib.sha256(raw).digest()


def compress(raw, codec, q):
    if codec=='store': return raw
    if codec=='zlib': return zlib.compress(raw, 6)
    if codec=='brotli': return brotli.compress(raw, quality=q)
    raise ValueError('Unknown codec')


def decompress(raw,codec,limit):
    if codec == 'store':
        if len(raw)>limit: raise ValueError('Excessive stored payload')
        return raw
    if codec == 'zlib':
        dec=zlib.decompressobj()
        out=dec.decompress(raw,limit+1)
        if len(out)>limit or not dec.eof or dec.unconsumed_tail or dec.unused_data:
            raise ValueError('Invalid, trailing, or excessive zlib payload')
        tail=dec.flush()
        if len(out)+len(tail)>limit: raise ValueError('Excessive zlib output')
        return out+tail
    if codec == 'brotli':
        dec=brotli.Decompressor()
        out=[]; n=0
        for pos in range(0,len(raw),4096):
            part=dec.process(raw[pos:pos+4096]);n+=len(part)
            if n>limit: raise ValueError('Excessive Brotli output')
            out.append(part)
        if not dec.is_finished(): raise ValueError('Truncated Brotli payload')
        return b''.join(out)
    raise ValueError('Unsupported codec')


def best_leaf(raw,q):
    views={'raw':raw}
    best=('raw','store',raw)
    for trans,codec in CANDIDATES[1:]:
        if trans not in views: views[trans]=TRANSFORMS[trans][0](raw)
        payload=compress(views[trans],codec,q)
        if len(payload)<len(best[2]):best=(trans,codec,payload)
    return best


@dataclass
class Entry:
    kind: int
    size: int
    sha: bytes
    trans: int = 0
    codec: int = 0
    payload: bytes = b''
    children: tuple[int,int,int] | None = None


def encode(source, archive, *, depth=5, quality=5, stop=None):
    stop = stop or BreakController()
    stop.check()
    source,archive=Path(source),Path(archive)
    if source.resolve()==archive.resolve(): raise ValueError('Source and archive paths must differ')
    if not (0<=depth<=MAX_DEPTH):raise ValueError('Depth outside supported range')
    if not (0<=quality<=11):raise ValueError('Brotli quality outside supported range')
    if source.stat().st_size>MAX_SOURCE:raise ValueError('Source exceeds prototype memory bound')
    content=source.read_bytes()
    if len(content)>MAX_SOURCE:raise ValueError('Source exceeds prototype memory bound')
    entries=[]
    leaves={}
    branches={}
    cache=Counter()

    def walk(left,right,d):
        stop.check()
        size=right-left
        if d<=0 or size<3:
            block=content[left:right]
            h=digest(block)
            key=(size,h)
            for index, representative_left in leaves.get(key,[]):
                if content[representative_left:representative_left+size]==block:
                    cache['deduplicated_leaves']+=1
                    return index
            transform,codec,packed=best_leaf(block,quality)
            stop.check()
            if len(packed)>MAX_PAYLOAD:raise ValueError('Leaf encoding exceeds maximum')
            index=len(entries)
            entries.append(Entry(0,size,h,METHODS[transform],CODECS[codec],packed))
            leaves.setdefault(key,[]).append((index,left))
            cache[f'{transform}/{codec}']+=1
            return index
        # Three adjacent nonempty ranges; their sizes differ by at most 1.
        a=size//3+(size%3>0)
        b=size//3+(size%3>1)
        ranges=((left,left+a),(left+a,left+a+b),(left+a+b,right))
        children=tuple(walk(x,y,d-1) for x,y in ranges)
        if children in branches:
            cache['deduplicated_branches']+=1
            return branches[children]
        index=len(entries)
        entries.append(Entry(1,size,digest(content[left:right]),children=children))
        branches[children]=index
        return index

    root=walk(0,len(content),depth)
    if len(entries)>MAX_NODES: raise ValueError('Too many DAG nodes')
    root_sha=digest(content)
    archive.parent.mkdir(parents=True, exist_ok=True)
    temp=None
    try:
        with tempfile.NamedTemporaryFile(dir=archive.parent,prefix='.triadic-',delete=False) as out:
            temp=Path(out.name)
            out.write(HEADER.pack(MAGIC,1,depth,len(content),len(entries),root,root_sha))
            for node in entries:
                stop.check()
                out.write(NODE.pack(node.kind,node.size,node.sha))
                if node.kind==0:
                    out.write(LEAF.pack(node.trans,node.codec,len(node.payload)))
                    out.write(node.payload)
                else:
                    out.write(BRANCH.pack(*node.children))
        stop.check()
        os.replace(temp,archive)
        temp=None
    finally:
        if temp is not None:temp.unlink(missing_ok=True)
    return {'source_bytes':len(content),'archive_bytes':archive.stat().st_size,
            'saved_percent':round(100*(1-archive.stat().st_size/len(content)),4) if content else None,
            'depth_requested':depth,'node_count':len(entries),'root_node':root,
            'leaf_count':sum(v.kind==0 for v in entries),
            'branch_count':sum(v.kind==1 for v in entries),
            'selection_counts':dict(cache),'quality':quality,'sha256':root_sha.hex()}


def decode(archive,destination,*,stop=None):
    stop = stop or BreakController()
    stop.check()
    archive,destination=Path(archive),Path(destination)
    if archive.resolve()==destination.resolve():raise ValueError('Archive and destination paths must differ')
    entries=[]
    with archive.open('rb') as f:
        raw=f.read(HEADER.size)
        if len(raw)!=HEADER.size:raise ValueError('Truncated archive header')
        magic,version,depth,source_len,count,root,root_hash=HEADER.unpack(raw)
        if magic!=MAGIC or version!=1:raise ValueError('Invalid archive type/version')
        if source_len>MAX_SOURCE or count>MAX_NODES or depth>MAX_DEPTH or count==0 or root>=count:
            raise ValueError('Invalid archive size/node/depth bounds')
        for idx in range(count):
            stop.check()
            row=f.read(NODE.size)
            if len(row)!=NODE.size:raise ValueError('Truncated DAG node')
            kind,size,sha=NODE.unpack(row)
            if size>source_len:raise ValueError('Node size beyond source')
            if kind==0:
                hdr=f.read(LEAF.size)
                if len(hdr)!=LEAF.size:raise ValueError('Truncated leaf header')
                trans,codec,packed=LEAF.unpack(hdr)
                if trans not in R_METHODS or codec not in R_CODECS or packed>MAX_PAYLOAD:
                    raise ValueError('Invalid leaf metadata')
                payload=f.read(packed)
                if len(payload)!=packed:raise ValueError('Truncated leaf contents')
                entries.append(Entry(kind,size,sha,trans,codec,payload))
            elif kind==1:
                row=f.read(BRANCH.size)
                if len(row)!=BRANCH.size:raise ValueError('Truncated branch')
                children=BRANCH.unpack(row)
                if any(child>=idx for child in children):raise ValueError('Cyclic or forward reference')
                if sum(entries[c].size for c in children)!=size:
                    raise ValueError('Child sizes do not match parent')
                entries.append(Entry(kind,size,sha,children=children))
            else:
                raise ValueError('Invalid node kind')
        if f.read(1):raise ValueError('Trailing data after DAG')
    if entries[root].size!=source_len or entries[root].sha!=root_hash:
        raise ValueError('Root length/hash mismatch')
    # Enforce tree depth and references from the root; avoid processing unrelated nodes.
    stack=[(root,0)]
    reachable=set()
    while stack:
        stop.check()
        idx,level=stack.pop()
        if level>depth:raise ValueError('Tree deeper than declared depth')
        reachable.add(idx)
        node=entries[idx]
        if node.kind==1:
            stack.extend((i,level+1) for i in node.children)
    if len(reachable)!=len(entries):raise ValueError('Unreachable DAG nodes')
    leaf_cache={}
    def block_bytes(idx):
        stop.check()
        node=entries[idx]
        if node.kind!=0:raise ValueError('Nonleaf requested as leaf')
        if idx not in leaf_cache:
            limit=8*((node.size+7)//8)
            transformed=decompress(node.payload,R_CODECS[node.codec],limit)
            stop.check()
            recovered=TRANSFORMS[R_METHODS[node.trans]][1](transformed,node.size)
            if len(recovered)!=node.size or digest(recovered)!=node.sha:
                raise ValueError('Leaf reconstruction mismatch')
            leaf_cache[idx]=recovered
        return leaf_cache[idx]
    def traversal(idx):
        stop.check()
        node=entries[idx]
        if node.kind==0:
            yield block_bytes(idx)
            return
        local_hash=hashlib.sha256()
        local_size=0
        for child in node.children:
            for fragment in traversal(child):
                local_hash.update(fragment)
                local_size+=len(fragment)
                yield fragment
        if local_size != node.size or local_hash.digest() != node.sha:
            raise ValueError('Internal node reconstruction mismatch')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp=None
    hash_obj=hashlib.sha256(); seen=0
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent,prefix='.triadic-',delete=False) as out:
            temp=Path(out.name)
            for part in traversal(root):
                stop.check()
                out.write(part);hash_obj.update(part);seen+=len(part)
        if seen!=source_len or hash_obj.digest()!=root_hash:
            raise ValueError('Root reconstruction mismatch')
        stop.check()
        os.replace(temp,destination);temp=None
    finally:
        if temp is not None:temp.unlink(missing_ok=True)
    return {'recovered_bytes':seen,'sha256':hash_obj.hexdigest(),
            'node_count':len(entries),'leaf_count':len(leaf_cache),
            'byte_exact_verified_against_root_hash':True}


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    sub=cli.add_subparsers(dest='command',required=True)
    for cmd in ('encode','decode'):
        parser=sub.add_parser(cmd)
        parser.add_argument('input',type=Path)
        parser.add_argument('output',type=Path)
        if cmd=='encode':
            parser.add_argument('--depth',type=int,default=5)
            parser.add_argument('--quality',type=int,default=5)
    args=cli.parse_args()
    stop=BreakController()
    previous=install_break_signals(stop)
    try:
        with ClosedState([args.output]) as checkpoint:
            checkpoint.begin()
            try:
                result=(encode(args.input,args.output,depth=args.depth,
                               quality=args.quality,stop=stop)
                        if args.command=='encode' else
                        decode(args.input,args.output,stop=stop))
                stop.check()
            except BaseException:
                checkpoint.finish(False)
                raise
            else:
                checkpoint.finish(True)
        print(json.dumps(result,indent=2))
        return 0
    except StopRequested:
        print('BREAK: previous closed state restored; uncommitted output removed')
        return 130
    finally:
        restore_break_signals(previous)

if __name__=='__main__':
    import sys
    sys.exit(main())
