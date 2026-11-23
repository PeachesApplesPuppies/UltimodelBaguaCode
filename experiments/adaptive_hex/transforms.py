"""Exact reversible bit rearrangements for 8-bit source streams.

hex6+2 stores every source byte as a six-bit 'HEX state' and a 2-bit
high-side tag, with both bit fields packed independently. No loss occurs.
"""
import numpy as np


def pack62(data: bytes) -> bytes:
    n = len(data)
    x = np.frombuffer(data,dtype=np.uint8)
    pad = (-n) % 4
    if pad: x = np.pad(x,(0,pad))
    if not len(x): return b''
    q = x.reshape(-1,4)
    lo = q & 63
    hi = q >> 6
    out = np.empty((len(q),3),dtype=np.uint8)
    out[:,0] = (lo[:,0]<<2)|(lo[:,1]>>4)
    out[:,1] = (lo[:,1]<<4)|(lo[:,2]>>2)
    out[:,2] = (lo[:,2]<<6)|lo[:,3]
    hi_byte = (hi[:,0]<<6)|(hi[:,1]<<4)|(hi[:,2]<<2)|hi[:,3]
    return out.tobytes() + hi_byte.tobytes()


def unpack62(data: bytes, original_len:int) -> bytes:
    if not isinstance(original_len,int) or original_len<0: raise ValueError('invalid original length')
    groups=(original_len+3)//4
    if len(data)!=4*groups: raise ValueError('incorrect packed length')
    if not groups:return b''
    lo=np.frombuffer(data[:groups*3],dtype=np.uint8).reshape(-1,3)
    hi=np.frombuffer(data[groups*3:],dtype=np.uint8)
    x=np.empty((groups,4),dtype=np.uint8)
    x[:,0] = (lo[:,0]>>2)|((hi>>6)<<6)
    x[:,1] = ((lo[:,0]&3)<<4)|(lo[:,1]>>4)|(((hi>>4)&3)<<6)
    x[:,2] = ((lo[:,1]&15)<<2)|(lo[:,2]>>6)|(((hi>>2)&3)<<6)
    x[:,3] = (lo[:,2]&63)|((hi&3)<<6)
    return x.tobytes()[:original_len]


def xor_prev(data: bytes)->bytes:
    if not data:return data
    x=np.frombuffer(data,dtype=np.uint8)
    y=np.empty_like(x)
    y[0]=x[0]
    y[1:]=x[1:]^x[:-1]
    return y.tobytes()


def unxor_prev(data: bytes)->bytes:
    if not data:return data
    x=np.frombuffer(data,dtype=np.uint8)
    return np.bitwise_xor.accumulate(x).tobytes()


def shuffle_bits(data:bytes)->bytes:
    """Transpose 8x8 bits inside each 8-byte group; pad with zeros."""
    if not data:return data
    pad=(-len(data))%8
    x=np.frombuffer(data+b'\0'*pad,dtype=np.uint8).reshape(-1,8)
    bits=np.unpackbits(x,axis=1,bitorder='big')
    # unpackbits creates 64 bit columns, 8x8 group transpose.
    mapped=bits.reshape(-1,8,8).swapaxes(1,2).reshape(-1,64)
    return np.packbits(mapped,axis=1,bitorder='big').tobytes()


def unshuffle_bits(data:bytes,original_len:int)->bytes:
    if not data:return b''
    return shuffle_bits(data)[:original_len]

TRANSFORMS={
 'raw': (lambda data: data, lambda data,n: data if len(data)==n else (_ for _ in ()).throw(ValueError('size mismatch'))),
 'hex6+2':(pack62,unpack62),
 'xor':(xor_prev,lambda data,n:unxor_prev(data) if len(data)==n else (_ for _ in ()).throw(ValueError('size mismatch'))),
 'xor+hex6+2':(lambda data:pack62(xor_prev(data)),lambda data,n:unxor_prev(unpack62(data,n))),
 'bitshuffle':(shuffle_bits,unshuffle_bits),
}
