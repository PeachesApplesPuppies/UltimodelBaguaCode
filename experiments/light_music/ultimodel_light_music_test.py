"""Ultimodel Light Music test: optical-symbol encoding of real soundtrack audio.

Reproducibility: requires ffmpeg and numpy. This is a DIGITAL CHANNEL
simulation, not an experiment with actual photons or a proof of string theory.
Run: python ultimodel_light_music_test.py /path/to/ALittleLightMusic.mp4
"""
import hashlib
import json
import random
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

VIDEO = Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/ALittleLightMusic.mp4')


def pcm_from_video(video):
    return subprocess.check_output([
        'ffmpeg', '-hide_banner','-loglevel','error', '-ss','240', '-t','2',
        '-i',str(video), '-vn','-ac','1','-ar','8000',
        '-c:a','pcm_s16le','-f','s16le','pipe:1'
    ])


def split_hex_byte(b):
    return (b & 0x3f, b >> 6)


def join_hex_byte(state6, high2):
    if not (0 <= state6 < 64 and 0 <= high2 < 4):
        raise ValueError('invalid 6+2 code')
    return (high2 << 6) | state6


def invert_six(v):
    return v ^ 0x3f


def reverse_six(v):
    return int(f'{v:06b}'[::-1],2)


class LightMusicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pcm = pcm_from_video(VIDEO)
        cls.samples = np.frombuffer(cls.pcm,dtype='<i2').astype(np.float64)

    def test_01_all_256_possible_brightness_symbols_reconstruct(self):
        for byte in range(256):
            self.assertEqual(join_hex_byte(*split_hex_byte(byte)),byte)

    def test_02_all_64_six_bit_states_invert_and_reverse(self):
        for state in range(64):
            self.assertEqual(invert_six(invert_six(state)),state)
            self.assertEqual(reverse_six(reverse_six(state)),state)
            self.assertEqual(reverse_six(invert_six(state)),invert_six(reverse_six(state)))

    def test_03_actual_soundtrack_bytes_survive_brightness_mapping(self):
        # Model each PCM byte as an idealized normalized intensity between 0 and 1.
        # This is a numerical channel model, not a physical optical experiment.
        intensities = [byte / 255 for byte in self.pcm]
        decoded = bytes(round(intensity * 255) for intensity in intensities)
        self.assertEqual(decoded, self.pcm)
        self.assertEqual(len(self.pcm), 32000)

    def test_04_sixbit_view_requires_two_bit_provenance(self):
        states_and_history = [split_hex_byte(v) for v in self.pcm]
        self.assertEqual(bytes(join_hex_byte(*p) for p in states_and_history),self.pcm)
        only_six_bits = bytes(v & 63 for v in self.pcm)
        self.assertNotEqual(only_six_bits,self.pcm)

    def test_05_spectrum_magnitude_alone_does_not_restore_phase(self):
        spectrum=np.fft.rfft(self.samples)
        inverted=np.fft.rfft(-self.samples)
        self.assertTrue(np.allclose(np.abs(spectrum),np.abs(inverted)))
        self.assertFalse(np.array_equal(self.samples,-self.samples))

    def test_06_full_complex_spectrum_recovers_pcm_in_this_clip(self):
        spectrum=np.fft.rfft(self.samples)
        recovered=np.rint(np.fft.irfft(spectrum,n=len(self.samples))).astype('<i2')
        self.assertEqual(recovered.tobytes(),self.pcm)

    def test_07_single_bit_corruption_detectable_in_2500_trials(self):
        rng=random.Random(20261123)
        expected=hashlib.sha256(self.pcm).digest()
        for _ in range(2500):
            corrupted=bytearray(self.pcm)
            corrupted[rng.randrange(len(corrupted))]^=(1<<rng.randrange(8))
            self.assertNotEqual(hashlib.sha256(corrupted).digest(),expected)


if __name__=='__main__':
    if not VIDEO.exists():
        raise SystemExit('Video file not found')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(LightMusicTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    pcm=pcm_from_video(VIDEO)
    losses=sum((v & 63)!=v for v in pcm)
    data={'input_video':VIDEO.name,'excerpt_start_seconds':240,'excerpt_seconds':2,
          'pcm_sampling_hz':8000,'pcm_bits_per_sample':16,'pcm_bytes':len(pcm),
          'sha256':hashlib.sha256(pcm).hexdigest(),
          'tests_run':result.testsRun,'tests_passed':result.testsRun-len(result.failures)-len(result.errors),
          'six_bit_only_differing_bytes':losses,
          'full_six_plus_two_encoding_restores_all_bytes':True,
          'sampled_corruption_trials':2500,
          'conclusion':'Digital sound can be represented by ideal 8-bit light-intensity symbols, and decoded; not physical transmission or proof of a vibrating-string ontology.'}
    out=Path(__file__).with_name('run_results.json')
    out.write_text(json.dumps(data,indent=2)+'\n')
    print('Wrote:',out)
