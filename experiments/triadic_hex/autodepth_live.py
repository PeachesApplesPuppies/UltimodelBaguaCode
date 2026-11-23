"""Ultimodel AutoDepth Live v0.3 — seekable, checksum-checked .ut3 reader.

Compatible with Triadic HEX v0.1 and AutoDepth v0.2 archives. No full
extraction required for byte-range reads. Optional loopback HTTP server sends
206 Partial Content so an ordinary MP4 player can seek within the archive.

The archive stays compressed on disk. Unmodified decoded buffers are simply
released; we do not recompress them. Requires brotli+numpy installed externally.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import re
import tempfile
import hmac
import secrets
import urllib.request
import urllib.error
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

import triadic_hex as tri
from transforms import TRANSFORMS
from emergency_break import BreakController, StopRequested, install_break_signals, restore_break_signals
from live_player import run_stream_session

DEFAULT_CACHE = 8 * 1024 * 1024
DEFAULT_LEAF_LIMIT = 64 * 1024 * 1024
READ_CHUNK = 64 * 1024


@dataclass(frozen=True)
class NodeInfo:
    kind: int
    size: int
    digest: bytes
    transform: int = 0
    codec: int = 0
    payload_start: int = 0
    payload_len: int = 0
    children: tuple[int, int, int] | None = None


class IndexedArchive:
    """Index a .ut3 file without loading its compressed leaf payloads.

    read_range checks the SHA256 of every touched leaf. verify_full checks all
    reachable internal node digests and the root digest. On-demand reads alone
    do not authenticate untouched regions or the complete root hash.

    max_leaf_bytes is a per-leaf bound: decoding any larger leaf fails. The
    cache has its own hard cap, but transient decoding/output buffers add RAM.
    """

    def __init__(self, archive, *, cache_bytes=DEFAULT_CACHE,
                 max_leaf_bytes=DEFAULT_LEAF_LIMIT, stop=None):
        self.path = Path(archive)
        self.stop = stop or BreakController()
        if type(cache_bytes) is not int or cache_bytes < 0:
            raise ValueError('cache_bytes must be a nonnegative integer')
        if type(max_leaf_bytes) is not int or not 1 <= max_leaf_bytes <= tri.MAX_SOURCE:
            raise ValueError('max_leaf_bytes outside supported range')
        self.cache_limit = cache_bytes
        self.max_leaf_bytes = max_leaf_bytes
        self._cache = collections.OrderedDict()
        self._cache_used = 0
        self._lock = threading.RLock()
        self._stats = collections.Counter()
        self.nodes: list[NodeInfo] = []
        self._load_index()

    def _load_index(self):
        self.stop.check()
        filesize = self.path.stat().st_size
        with self.path.open('rb') as f:
            header = f.read(tri.HEADER.size)
            if len(header) != tri.HEADER.size:
                raise ValueError('Truncated .ut3 header')
            magic, version, depth, length, node_count, root, root_digest = tri.HEADER.unpack(header)
            if magic != tri.MAGIC or version != 1:
                raise ValueError('Unrecognized Triadic HEX archive')
            if (depth > tri.MAX_DEPTH or length > tri.MAX_SOURCE or
                    not (1 <= node_count <= tri.MAX_NODES) or root >= node_count):
                raise ValueError('Archive metadata outside supported bounds')
            for i in range(node_count):
                self.stop.check()
                meta = f.read(tri.NODE.size)
                if len(meta) != tri.NODE.size:
                    raise ValueError('Truncated node metadata')
                kind, size, digest = tri.NODE.unpack(meta)
                if size > length:
                    raise ValueError('Node is larger than archive source')
                if kind == 0:
                    lh = f.read(tri.LEAF.size)
                    if len(lh) != tri.LEAF.size:
                        raise ValueError('Truncated leaf metadata')
                    transform, codec, packed = tri.LEAF.unpack(lh)
                    if (transform not in tri.R_METHODS or codec not in tri.R_CODECS or
                            packed > tri.MAX_PAYLOAD):
                        raise ValueError('Unknown codec/transform or excessive compressed length')
                    payload_start = f.tell()
                    if payload_start + packed > filesize:
                        raise ValueError('Truncated compressed payload')
                    f.seek(packed, 1)
                    self.nodes.append(NodeInfo(kind, size, digest, transform, codec,
                                               payload_start, packed))
                elif kind == 1:
                    data = f.read(tri.BRANCH.size)
                    if len(data) != tri.BRANCH.size:
                        raise ValueError('Truncated parent references')
                    children = tri.BRANCH.unpack(data)
                    if any(child >= i for child in children):
                        raise ValueError('Cyclic or forward DAG reference')
                    if sum(self.nodes[c].size for c in children) != size:
                        raise ValueError('Parent length does not match children')
                    self.nodes.append(NodeInfo(kind, size, digest, children=children))
                else:
                    raise ValueError('Invalid node kind')
            if f.tell() != filesize:
                raise ValueError('Trailing bytes after archive index')
        if self.nodes[root].size != length or self.nodes[root].digest != root_digest:
            raise ValueError('Root length/hash metadata mismatch')
        reachable = set()
        seen_pairs = set()
        stack = [(root, 0)]
        while stack:
            self.stop.check()
            idx, level = stack.pop()
            if level > depth:
                raise ValueError('Tree exceeds declared depth')
            if (idx, level) in seen_pairs:
                continue
            seen_pairs.add((idx, level))
            reachable.add(idx)
            node = self.nodes[idx]
            if node.children:
                stack.extend((child, level + 1) for child in node.children)
        if len(reachable) != node_count:
            raise ValueError('Unreachable DAG nodes in archive')
        self.length = length
        self.root = root
        self.root_digest = root_digest
        self.max_depth = depth
        self.compressed_bytes = filesize
        self._stats['index_nodes'] = node_count
        self._stats['unique_leaves'] = sum(n.kind == 0 for n in self.nodes)

    @staticmethod
    def _transformed_limit(node):
        name = tri.R_METHODS[node.transform]
        if name in ('hex6+2', 'xor+hex6+2'):
            return 4 * ((node.size + 3) // 4)
        if name == 'bitshuffle':
            return 8 * ((node.size + 7) // 8)
        return node.size

    def _decode_leaf(self, idx):
        self.stop.check()
        node = self.nodes[idx]
        if node.kind != 0:
            raise ValueError('Not a leaf')
        if node.size > self.max_leaf_bytes:
            raise ValueError(f'Leaf {idx} exceeds max_leaf_bytes; re-encode with smaller leaves')
        with self._lock:
            if idx in self._cache:
                self._cache.move_to_end(idx)
                self._stats['cache_hits'] += 1
                return self._cache[idx]
            self._stats['cache_misses'] += 1
            with self.path.open('rb') as f:
                f.seek(node.payload_start)
                packed = f.read(node.payload_len)
            self.stop.check()
            if len(packed) != node.payload_len:
                raise ValueError('Archive modified during read')
            limit = self._transformed_limit(node)
            try:
                transformed = tri.decompress(packed, tri.R_CODECS[node.codec], limit)
                data = TRANSFORMS[tri.R_METHODS[node.transform]][1](transformed, node.size)
            except StopRequested:
                raise
            except Exception as exc:
                raise ValueError(f'Failed to reconstruct leaf {idx}') from exc
            self.stop.check()
            if len(data) != node.size or tri.digest(data) != node.digest:
                raise ValueError(f'Leaf {idx} SHA-256 verification failed')
            self._stats['leaf_bytes_decoded'] += len(data)
            self._stats['largest_decoded_leaf'] = max(
                self._stats['largest_decoded_leaf'], len(data))
            if len(data) <= self.cache_limit:
                while self._cache and self._cache_used + len(data) > self.cache_limit:
                    _, discarded = self._cache.popitem(last=False)
                    self._cache_used -= len(discarded)
                    self._stats['cache_evictions'] += 1
                self._cache[idx] = data
                self._cache_used += len(data)
                self._stats['max_cache_bytes_used'] = max(
                    self._stats['max_cache_bytes_used'], self._cache_used)
            return data

    def _visit_range(self, idx, base, start, stop) -> Iterator[bytes]:
        self.stop.check()
        node = self.nodes[idx]
        node_end = base + node.size
        if stop <= base or start >= node_end:
            return
        if node.kind == 0:
            data = self._decode_leaf(idx)
            yield data[max(start - base, 0): min(stop - base, node.size)]
            return
        cursor = base
        for child in node.children:
            child_size = self.nodes[child].size
            if start < cursor + child_size and stop > cursor:
                yield from self._visit_range(child, cursor, start, stop)
            cursor += child_size

    def read_range(self, offset, size):
        self.stop.check()
        if type(offset) is not int or type(size) is not int:
            raise TypeError('Read offset and size must be integers')
        if offset < 0 or size < 0:
            raise ValueError('Read offset and size cannot be negative')
        if size == 0 or offset >= self.length:
            return b''
        end = min(self.length, offset + size)
        result = b''.join(self._visit_range(self.root, 0, offset, end))
        if len(result) != end - offset:
            raise ValueError('Unexpected partial byte-range reconstruction')
        with self._lock:
            self._stats['range_reads'] += 1
            self._stats['bytes_returned'] += len(result)
        return result

    def verify_full(self):
        self.stop.check()
        """Stream the entire DAG, check every leaf and every internal digest."""
        def checked(idx):
            self.stop.check()
            node = self.nodes[idx]
            if node.kind == 0:
                yield self._decode_leaf(idx)
                return
            sha = hashlib.sha256()
            length = 0
            for child in node.children:
                for chunk in checked(child):
                    sha.update(chunk)
                    length += len(chunk)
                    yield chunk
            if length != node.size or sha.digest() != node.digest:
                raise ValueError(f'Internal node {idx} SHA-256 verification failed')
        all_hash = hashlib.sha256()
        total = 0
        for piece in checked(self.root):
            self.stop.check()
            all_hash.update(piece)
            total += len(piece)
        if total != self.length or all_hash.digest() != self.root_digest:
            raise ValueError('Full archive hash verification failed')
        return {'verified': True, 'bytes': total, 'sha256': all_hash.hexdigest(),
                'stats': self.stats()}

    def clear_cache(self):
        with self._lock:
            self._cache.clear()
            self._cache_used = 0

    def stats(self):
        with self._lock:
            return {**self._stats, 'cache_bytes': self._cache_used,
                    'cache_limit': self.cache_limit,
                    'source_bytes': self.length, 'archive_bytes': self.compressed_bytes}

    def file(self):
        return SeekableHEXFile(self)


class SeekableHEXFile(io.RawIOBase):
    """Read-only seekable virtual file backed by an IndexedArchive."""
    def __init__(self, archive: IndexedArchive):
        super().__init__()
        self.archive = archive
        self.position = 0

    def readable(self): return True
    def seekable(self): return True
    def writable(self): return False
    def tell(self): return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        self._checkClosed()
        if type(offset) is not int:
            raise TypeError('Seek offset must be integer')
        if whence == io.SEEK_SET:
            pos = offset
        elif whence == io.SEEK_CUR:
            pos = self.position + offset
        elif whence == io.SEEK_END:
            pos = self.archive.length + offset
        else:
            raise ValueError('Unsupported whence')
        if pos < 0:
            raise ValueError('Seek cannot precede source beginning')
        self.position = pos
        return pos

    def read(self, size=-1):
        self._checkClosed()
        if size is None or size < 0:
            size = max(0, self.archive.length - self.position)
        out = self.archive.read_range(self.position, size)
        self.position += len(out)
        return out

    def readinto(self, b):
        value = self.read(len(b))
        memoryview(b)[:len(value)] = value
        return len(value)


_RANGE = re.compile(r'^bytes=(\d*)-(\d*)$')


def parse_range(value, total):
    """Return inclusive [first,last], or raise ValueError if invalid."""
    if total <= 0:
        raise ValueError('No satisfiable range for empty file')
    m = _RANGE.fullmatch(value.strip())
    if not m:
        raise ValueError('Only a single bytes=start-end range is supported')
    left, right = m.groups()
    if not left and not right:
        raise ValueError('Empty byte range')
    if not left:
        count = int(right)
        if count <= 0:
            raise ValueError('Zero-byte suffix range')
        first = max(0, total - count)
        return first, total - 1
    first = int(left)
    last = min(total - 1, int(right)) if right else total - 1
    if first >= total or last < first:
        raise ValueError('Unsatisfiable byte range')
    return first, last


def make_http_server(archive: IndexedArchive, host='127.0.0.1', port=0,
                     path='/video.mp4', stop_secret=None):
    if not path.startswith('/'):
        raise ValueError('HTTP route must start with /')
    if path == '/__break':
        raise ValueError('Reserved BREAK endpoint')
    token = stop_secret or secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        server_version = 'UltimodelAutoDepthLive/0.3'
        def do_HEAD(self): self._serve(head=True)
        def do_GET(self): self._serve(head=False)
        def do_POST(self):
            if self.path != '/__break':
                self.send_error(404)
                return
            # A localhost endpoint is necessary but not sufficient: require a
            # high-entropy per-server token to prevent cross-site stop requests.
            supplied = self.headers.get('X-Ultimodel-Break', '')
            remote = self.client_address[0]
            if remote not in ('127.0.0.1', '::1') or not hmac.compare_digest(supplied, token):
                self.send_error(403, 'BREAK requires the local control token')
                return
            # Do not acquire the reader lock before acknowledging BREAK:
            # a decompression thread might currently hold it for a while.
            archive.stop.request()
            self.send_response(202)
            self.send_header('Content-Length', '0')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            threading.Thread(target=archive.clear_cache, daemon=True).start()

        def _serve(self, head):
            if archive.stop.requested:
                self.send_error(503, 'Stopped by BREAK')
                return

            if self.path.split('?', 1)[0] != path:
                self.send_error(404, 'Not found')
                return
            total = archive.length
            given = self.headers.get('Range')
            try:
                if given:
                    first, last = parse_range(given, total)
                    status = 206
                else:
                    first, last = 0, total - 1
                    status = 200
            except ValueError:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{total}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            length = max(0, last - first + 1)
            self.send_response(status)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Cache-Control', 'no-store, no-transform')
            self.send_header('Content-Length', str(length))
            if status == 206:
                self.send_header('Content-Range', f'bytes {first}-{last}/{total}')
            self.end_headers()
            if head:
                return
            pos = first
            while pos <= last:
                if archive.stop.requested:
                    self.close_connection = True
                    break
                amount = min(READ_CHUNK, last - pos + 1)
                try:
                    fragment = archive.read_range(pos, amount)
                    if len(fragment) != amount:
                        raise ValueError('Incomplete archive read')
                    self.wfile.write(fragment)
                    pos += amount
                except (BrokenPipeError, ConnectionResetError, StopRequested):
                    break
                except Exception as exc:
                    # Headers may already have been sent; terminate rather
                    # than accidentally sending corrupted content as valid data.
                    self.log_error('Archive read failed at %d: %s', pos, exc)
                    self.close_connection = True
                    break
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.break_token = token
    return server


def send_break(port, token, host='127.0.0.1'):
    """Stop this project's local stream via an authenticated HTTP control POST."""
    if host not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('BREAK CLI supports loopback only')
    req = urllib.request.Request(
        f'http://{host}:{port}/__break', data=b'', method='POST',
        headers={'X-Ultimodel-Break': token})
    with urllib.request.urlopen(req, timeout=3) as response:
        if response.status != 202:
            raise RuntimeError(f'BREAK was not accepted: {response.status}')
    return True


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('inspect', 'verify', 'read', 'serve', 'play'):
        p = sub.add_parser(action)
        p.add_argument('archive', type=Path)
        p.add_argument('--cache-mib', type=int, default=8)
        p.add_argument('--max-leaf-mib', type=int, default=64)
        if action == 'read':
            p.add_argument('--offset', type=int, required=True)
            p.add_argument('--length', type=int, required=True)
            p.add_argument('--output', type=Path, help='Optional raw output file')
        if action in ('serve', 'play'):
            p.add_argument('--port', type=int, default=8766)
            p.add_argument('--host', default='127.0.0.1')
    stop_cmd = sub.add_parser('break', help='EMERGENCY STOP an active stream')
    stop_cmd.add_argument('--port', type=int, default=8766)
    stop_cmd.add_argument('--token', required=True)
    args = parser.parse_args()
    if args.action == 'break':
        send_break(args.port, args.token)
        print('BREAK acknowledged: streaming stop requested', flush=True)
        return
    controller = BreakController()
    previous = install_break_signals(controller)
    try:
        archive = IndexedArchive(args.archive, cache_bytes=args.cache_mib * 2**20,
                                 max_leaf_bytes=args.max_leaf_mib * 2**20,
                                 stop=controller)
        if args.action == 'inspect':
            print(json.dumps({'length': archive.length, 'nodes': len(archive.nodes),
                              'root': archive.root, 'stats': archive.stats()}, indent=2))
        elif args.action == 'verify':
            print(json.dumps(archive.verify_full(), indent=2))
        elif args.action == 'read':
            content = archive.read_range(args.offset, args.length)
            controller.check()
            if args.output:
                import os
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(dir=args.output.parent, prefix='.hex-read-', delete=False) as f:
                        tmp_path = Path(f.name)
                        f.write(content)
                    controller.check()
                    os.replace(tmp_path,args.output)
                    tmp_path = None
                finally:
                    if tmp_path is not None:
                        tmp_path.unlink(missing_ok=True)
                print(json.dumps({'wrote': str(args.output), 'bytes': len(content),
                                  'stats': archive.stats()}, indent=2))
            else:
                import sys
                sys.stdout.buffer.write(content)
        elif args.action in ('serve', 'play'):
            server = make_http_server(archive, host=args.host, port=args.port)
            print(f'Range-capable MP4 stream: http://{args.host}:{server.server_port}/video.mp4', flush=True)
            print(f'BREAK command: python autodepth_live.py break --port {server.server_port} --token {server.break_token}', flush=True)
            print('CTRL-C or SIGTERM also requests cancellation. A second signal forces interruption.', flush=True)
            try:
                if args.action == 'play':
                    # ffplay is a separate supervised child process. No shell.
                    url=f'http://127.0.0.1:{server.server_port}/video.mp4'
                    print('Playing through ffplay; BREAK stops playback and server.', flush=True)
                    cmd=['ffplay','-loglevel','error','-autoexit',url]
                else:
                    cmd=None
                run_stream_session(server,controller,player_argv=cmd)
            finally:
                archive.clear_cache()
    except StopRequested:
        print('BREAK: operation cancelled, no new archive/output committed', flush=True)
    finally:
        restore_break_signals(previous)


if __name__ == '__main__':
    cli()
