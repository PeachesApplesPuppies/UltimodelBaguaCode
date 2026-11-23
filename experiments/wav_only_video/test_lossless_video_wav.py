"""Deterministic regressions for the lossless-video-to-data-WAV codec.

Run: python -m unittest -v test_lossless_video_wav.py
No third-party video required. The test suite includes original-deleted recovery.
"""
import hashlib
import os
import random
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from lossless_video_wav import HEADER, MAGIC, VERSION, SAMPLE_RATE, encode, decode, from_pcm16, to_pcm16


class LosslessVideoWavTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def roundtrip(self, payload, remove_source=False):
        src = self.root / 'source.mp4'
        wav = self.root / 'data.wav'
        recovered = self.root / 'recovered.mp4'
        src.write_bytes(payload)
        info = encode(src, wav)
        self.assertEqual(info['source_bytes'], len(payload))
        self.assertEqual(info['source_sha256'], hashlib.sha256(payload).hexdigest())
        with wave.open(str(wav), 'rb') as wf:
            self.assertEqual(wf.getnframes(), len(payload) + HEADER.size)
        if remove_source:
            src.unlink()
            self.assertFalse(src.exists())
        result = decode(wav, recovered)
        self.assertTrue(result['hash_verified'])
        self.assertEqual(recovered.read_bytes(), payload)
        self.assertEqual(result['recovered_sha256'], hashlib.sha256(payload).hexdigest())

    def test_empty(self): self.roundtrip(b'')
    def test_single_byte(self):
        for b in range(256): self.roundtrip(bytes([b]))
    def test_all_possible_two_byte_codes(self):
        data = b''.join(bytes((i, j)) for i in range(256) for j in range(256))
        self.roundtrip(data, remove_source=True)
    def test_original_is_absent_for_decode(self):
        self.roundtrip(b'MP4\x00\xffDATA\xf0\x9f\x8e\xb5' * 100, remove_source=True)
    def test_random_sizes(self):
        rng = random.Random(20261123)
        for length in [0, 1, 2, 3, 5, 7, 14, 15, 16, 17, 254, 255, 256, 257,
                       4095, 4096, 4097, 65535, 65536, 65537, 1048575, 1048576, 1048577]:
            with self.subTest(length=length):
                data = rng.randbytes(length)
                self.roundtrip(data,remove_source=True)
    def test_unicode_paths(self):
        source = self.root / '🎼 原件.mp4'
        wav = self.root / '音楽データ.wav'
        destination = self.root / '重建🎵.mp4'
        source.write_bytes(bytes(range(256))*33)
        encode(source,wav)
        source.unlink()
        decode(wav,destination)
        self.assertEqual(destination.read_bytes(),bytes(range(256))*33)
    def test_header_version_magic(self):
        p = self.root/'src.bin'; w=self.root/'x.wav';out=self.root/'out.bin'
        p.write_bytes(b'abc123'); encode(p,w)
        with wave.open(str(w),'rb') as wf:
            data=from_pcm16(wf.readframes(HEADER.size))
        self.assertEqual(data[:8],MAGIC)
        self.assertEqual(data[8],VERSION)
        self.assertEqual(HEADER.unpack(data)[2],len(p.read_bytes()))
    def test_invalid_input_is_not_a_data_wav(self):
        w=self.root/'x.wav'; out=self.root/'out'
        with wave.open(str(w),'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b'\x00\x00'*200)
        with self.assertRaises(ValueError): decode(w,out)
        self.assertFalse(out.exists())
    def test_modified_data_checksum(self):
        p=self.root/'src';w=self.root/'x.wav';out=self.root/'out'
        p.write_bytes(os.urandom(1000));encode(p,w)
        with wave.open(str(w),'rb') as wf:
            raw=bytearray(wf.readframes(wf.getnframes()))
        # Change a payload byte while retaining a valid 8->16 PCM sample.
        offset=HEADER.size*2 + 2*200
        raw[offset+1] ^= 1
        with wave.open(str(w),'wb') as wf:
            wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SAMPLE_RATE)
            wf.writeframes(raw)
        with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'): decode(w,out)
        self.assertFalse(out.exists())
    def test_noncanonical_audio_sample_is_rejected(self):
        p=self.root/'src';w=self.root/'x.wav';out=self.root/'out'
        p.write_bytes(b'hello world');encode(p,w)
        with wave.open(str(w),'rb') as wf:
            raw=bytearray(wf.readframes(wf.getnframes()))
        raw[HEADER.size*2] ^= 1
        with wave.open(str(w),'wb') as wf:
            wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SAMPLE_RATE)
            wf.writeframes(raw)
        with self.assertRaisesRegex(ValueError,'canonical'):decode(w,out)
        self.assertFalse(out.exists())
    def test_truncated_frame_count_is_rejected(self):
        p=self.root/'src';w=self.root/'x.wav';out=self.root/'out'
        p.write_bytes(b'1234567890');encode(p,w)
        with wave.open(str(w),'rb') as wf:
            raw=wf.readframes(wf.getnframes())
        with wave.open(str(w),'wb') as wf:
            wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SAMPLE_RATE)
            wf.writeframes(raw[:-2])
        with self.assertRaisesRegex(ValueError,'Frame count'):decode(w,out)
        self.assertFalse(out.exists())
    def test_non_pcm_mono_is_rejected(self):
        w=self.root/'stereo.wav';out=self.root/'out'
        with wave.open(str(w),'wb') as wf:
            wf.setnchannels(2);wf.setsampwidth(2);wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b'\x00\x00'*100)
        with self.assertRaisesRegex(ValueError,'Not a supported'):decode(w,out)
    def test_refuse_to_overwrite_own_source(self):
        p=self.root/'one.mp4'
        p.write_bytes(b'original')
        with self.assertRaisesRegex(ValueError, 'must differ'): encode(p,p)
        self.assertEqual(p.read_bytes(),b'original')
        w=self.root/'data.wav'
        encode(p,w)
        before=w.read_bytes()
        with self.assertRaisesRegex(ValueError, 'must differ'): decode(w,w)
        self.assertEqual(w.read_bytes(),before)

    def test_byte_pcm_mapping_exhaustive(self):
        binary=bytes(range(256))
        self.assertEqual(from_pcm16(to_pcm16(binary)),binary)
        self.assertEqual(len(to_pcm16(binary)),len(binary)*2)
    def test_fuzzed_roundtrips(self):
        rng=random.Random(0xB16A)
        for trial in range(100):
            payload=rng.randbytes(rng.randint(0,30000))
            with self.subTest(trial=trial):
                self.roundtrip(payload,remove_source=True)


if __name__ == '__main__': unittest.main()
