"""AutoDepth Triadic HEX: bounded, per-branch leaf/split calculator.

Reuses Triadic HEX v1 archive format, decoder, and leaf encodings. Each branch
compares a standalone leaf with a ternary subdivision, accounting for unique
node payloads and references in the constructed subgraph. The chosen depth
can differ across branches. This is not a global minimum-size guarantee:
child choices are greedy, candidate boundaries are bounded, and no global
reoptimization is performed across independent parent subtrees.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile

import triadic_hex as tri

# A local plan is a self-contained DAG whose keys identify exact leaf bytes or
# the ordered child keys of a branch. No data is discarded by these keys:
# payloads are included in the serialized archive. SHA-256 groups candidates,
# and the source bytes are compared on every prospective leaf deduplication.
@dataclass
class Plan:
    key: object
    records: dict
    size: int
    levels: int


@dataclass
class Record:
    kind: int
    start: int
    stop: int
    digest: bytes
    payload: bytes = b''
    transform: int = 0
    codec: int = 0
    children: tuple | None = None
    @property
    def bytes_on_disk(self):
        return tri.NODE.size + (tri.LEAF.size + len(self.payload) if self.kind == 0 else tri.BRANCH.size)


class Planner:
    def __init__(self, source: bytes, *, quality: int, max_depth: int,
                 min_leaf: int, boundary_mode: str, max_evaluations: int):
        self.source = source
        self.quality = quality
        self.max_depth = max_depth
        self.min_leaf = min_leaf
        self.boundary_mode = boundary_mode
        self.max_evaluations = max_evaluations
        self.evaluated = 0
        self.expanded = 0  # strict cap on nodes for which splitting is explored
        self.events = Counter()
        self.split_modes = Counter()
        self.memo = {}
        self.leaf_content = {}  # digest -> [(key,start,end)] used to check collisions
        self.leaf_serial = 0

    @staticmethod
    def balanced(left, right):
        n = right-left
        a = n//3 + bool(n%3)
        b = n//3 + bool(n%3>1)
        return (left+a,left+a+b)

    def boundaries(self,left,right):
        n=right-left
        first=self.balanced(left,right)
        yield first
        if self.boundary_mode=='aligned' and n>=3*self.min_leaf:
            # Optional chunk-aligned candidate: boundaries may differ from the
            # arithmetic thirds, enabling natural repeated-block alignment.
            for alignment in (4096,65536):
                x,y=first
                x=max(left+self.min_leaf,min(right-2*self.min_leaf,
                      round(x/alignment)*alignment))
                y=max(x+self.min_leaf,min(right-self.min_leaf,
                      round(y/alignment)*alignment))
                if (x,y)!=first and x>left and y>x and y<right:
                    yield x,y

    def leaf_key(self,left,right,h):
        candidates = self.leaf_content.get((right-left,h),[])
        for key,start,stop in candidates:
            if self.source[left:right] == self.source[start:stop]:
                self.events['matching_leaf_reused'] += 1
                return key
        key=('L',self.leaf_serial)
        self.leaf_serial+=1
        self.leaf_content.setdefault((right-left,h),[]).append((key,left,right))
        return key

    def leaf_plan(self,left,right):
        raw=self.source[left:right]
        h=tri.digest(raw)
        key=self.leaf_key(left,right,h)
        if key in self.memo_leaf:
            return self.memo_leaf[key]
        t,c,payload=tri.best_leaf(raw,self.quality)
        rec=Record(0,left,right,h,payload,tri.METHODS[t],tri.CODECS[c])
        out=Plan(key,{key:rec},rec.bytes_on_disk,0)
        self.memo_leaf[key]=out
        self.events[f'leaf_choice:{t}/{c}']+=1
        return out

    def visit(self,left,right,remaining):
        cache_key=(left,right,remaining)
        if cache_key in self.memo:
            return self.memo[cache_key]
        self.evaluated+=1
        leaf=self.leaf_plan(left,right)
        n=right-left
        # Refuse potentially explosive exploration; always emit a valid leaf.
        if (remaining<=0 or n<3*self.min_leaf or self.expanded>=self.max_evaluations):
            if remaining>0 and n>=3*self.min_leaf:
                self.events['budget_pruned']+=1
            self.memo[cache_key]=leaf
            return leaf
        self.expanded+=1
        best=leaf
        seen=set()
        for x,y in self.boundaries(left,right):
            if (x,y) in seen:continue
            seen.add((x,y))
            if not (x-left>=self.min_leaf and y-x>=self.min_leaf and right-y>=self.min_leaf):
                continue
            plans=[self.visit(a,b,remaining-1) for a,b in ((left,x),(x,y),(y,right))]
            # Merge by actual byte identity for leaves and ordered child
            # identity for branches; each unique record counted once.
            records={}
            for plan in plans:records.update(plan.records)
            child_keys=tuple(plan.key for plan in plans)
            bkey=('B',child_keys)
            if bkey not in records:
                records[bkey]=Record(1,left,right,tri.digest(self.source[left:right]),children=child_keys)
            size=sum(rec.bytes_on_disk for rec in records.values())
            if size<best.size:
                self.split_modes['aligned' if (x,y)!=self.balanced(left,right) else 'balanced']+=1
                best=Plan(bkey,records,size,1+max(p.levels for p in plans))
                self.events['branch_wins']+=1
        if best.key==leaf.key:self.events['leaf_wins']+=1
        self.memo[cache_key]=best
        return best

    def calculate(self):
        self.memo_leaf={}
        plan=self.visit(0,len(self.source),self.max_depth)
        return plan


def encode(source,archive,*,max_depth=5,min_leaf=65536,quality=5,
           boundary_mode='balanced',max_evaluations=500):
    source,archive=Path(source),Path(archive)
    if source.resolve()==archive.resolve():raise ValueError('Source and archive must differ')
    if not (0<=max_depth<=tri.MAX_DEPTH):raise ValueError('Invalid maximum depth')
    if not (1<=min_leaf<=tri.MAX_SOURCE):raise ValueError('Invalid minimum leaf size')
    if not (0<=quality<=11):raise ValueError('Invalid Brotli quality')
    if boundary_mode not in ('balanced','aligned'):raise ValueError('Invalid boundary mode')
    if not (1<=max_evaluations<=100000):raise ValueError('Invalid evaluation budget')
    if source.stat().st_size>tri.MAX_SOURCE:raise ValueError('Source exceeds prototype bound')
    original=source.read_bytes()
    planner=Planner(original,quality=quality,max_depth=max_depth,min_leaf=min_leaf,
                    boundary_mode=boundary_mode,max_evaluations=max_evaluations)
    best=planner.calculate()
    if len(best.records)>tri.MAX_NODES:raise ValueError('Too many nodes')
    # Topological ordering guarantees the existing v1 decoder accepts the DAG.
    ordered=[]
    indices={}
    def add(key):
        if key in indices:return indices[key]
        rec=best.records[key]
        if rec.kind==1:
            children=tuple(add(c) for c in rec.children)
        idx=len(ordered)
        indices[key]=idx
        ordered.append((rec,children if rec.kind else None))
        return idx
    root=add(best.key)
    assert len(ordered)==len(best.records)
    expected_bytes=tri.HEADER.size+best.size
    # Catch planner misuse before committing an archive: every parent must be
    # a concatenation of its children, and every leaf references actual bytes.
    for rec,children in ordered:
        if rec.kind==1:
            if sum(ordered[i][0].stop-ordered[i][0].start for i in children) != rec.stop-rec.start:
                raise ValueError('Planner size mismatch')
        else:
            if tri.digest(original[rec.start:rec.stop])!=rec.digest:
                raise ValueError('Planner leaf mismatch')
    leaf_depths=Counter()
    def count_logical_leaves(key,level):
        rec=best.records[key]
        if rec.kind==0:
            leaf_depths[level]+=1
        else:
            for child in rec.children:
                count_logical_leaves(child,level+1)
    count_logical_leaves(best.key,0)
    branch_trace=[]
    truncated=[False]
    def trace(key,offset,address,level):
        if len(branch_trace)>=128:
            truncated[0]=True
            return
        r=best.records[key]
        length=r.stop-r.start
        row={'address':address,'depth':level,'offset':offset,'bytes':length,
             'action':'store_leaf' if r.kind==0 else 'split_three'}
        if r.kind==0:
            row['transform']=tri.R_METHODS[r.transform]
            row['compressor']=tri.R_CODECS[r.codec]
        branch_trace.append(row)
        if r.kind==1:
            position=offset
            for i,child in enumerate(r.children):
                trace(child,position,address+'.'+str(i),level+1)
                c=best.records[child]
                position+=c.stop-c.start
    trace(best.key,0,'root',0)
    archive.parent.mkdir(parents=True,exist_ok=True)
    temp=None
    try:
        with tempfile.NamedTemporaryFile(dir=archive.parent,prefix='.autodepth-',delete=False) as f:
            temp=Path(f.name)
            f.write(tri.HEADER.pack(tri.MAGIC,1,max_depth,len(original),len(ordered),root,tri.digest(original)))
            for rec,children in ordered:
                f.write(tri.NODE.pack(rec.kind,rec.stop-rec.start,rec.digest))
                if rec.kind==0:
                    f.write(tri.LEAF.pack(rec.transform,rec.codec,len(rec.payload)))
                    f.write(rec.payload)
                else:
                    f.write(tri.BRANCH.pack(*children))
        os.replace(temp,archive)
        temp=None
    finally:
        if temp is not None:temp.unlink(missing_ok=True)
    if archive.stat().st_size != expected_bytes:
        raise ValueError('Archive size does not match plan accounting')
    return {'source_bytes':len(original),'archive_bytes':archive.stat().st_size,
            'saved_percent':round(100*(1-archive.stat().st_size/len(original)),4) if original else None,
            'max_depth':max_depth,'chosen_depth':best.levels,
            'min_leaf':min_leaf,'boundary_mode':boundary_mode,
            'evaluated_regions':planner.evaluated,'expanded_regions':planner.expanded,
            'max_split_explorations':max_evaluations,
            'logical_leaves_by_depth':{str(k):v for k,v in sorted(leaf_depths.items())},
            'branch_trace':branch_trace,'branch_trace_truncated':truncated[0],
            'node_count':len(ordered),'leaf_count':sum(r.kind==0 for r,_ in ordered),
            'branch_count':sum(r.kind==1 for r,_ in ordered),
            'planning_events':dict(planner.events),'successful_split_modes':dict(planner.split_modes),
            'sha256':tri.digest(original).hex(),
            'verified':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for action in ('encode','decode','plan'):
        p=sub.add_parser(action)
        p.add_argument('input',type=Path)
        if action != 'plan':
            p.add_argument('output',type=Path)
        if action in ('encode','plan'):
            p.add_argument('--max-depth',type=int,default=5)
            p.add_argument('--min-leaf',type=int,default=65536)
            p.add_argument('--quality',type=int,default=5)
            p.add_argument('--boundary-mode',choices=('balanced','aligned'),default='balanced')
            p.add_argument('--max-evaluations',type=int,default=500,
                           help='Maximum number of regions expanded into child candidates')
    args=parser.parse_args()
    if args.command=='decode':
        result=tri.decode(args.input,args.output)
    else:
        parameters=dict(max_depth=args.max_depth,min_leaf=args.min_leaf,
                        quality=args.quality,boundary_mode=args.boundary_mode,
                        max_evaluations=args.max_evaluations)
        if args.command=='encode':
            result=encode(args.input,args.output,**parameters)
        else:
            with tempfile.TemporaryDirectory(prefix='autodepth-plan-') as d:
                result=encode(args.input,Path(d)/'candidate.ut3',**parameters)
            result['mode']='plan_only; temporary archive discarded'
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
