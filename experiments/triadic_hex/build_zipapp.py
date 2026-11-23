"""Build AutoDepth Live .pyz from the source distribution, without external deps."""
import shutil
import tempfile
import zipapp
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULES = (
    '__main__.py', 'triadic_hex.py', 'autodepth_hex.py', 'transforms.py',
    'autodepth_live.py', 'emergency_break.py', 'live_player.py',
    'breakable_runner.py', 'closed_state.py'
)


def build(target=None):
    target = Path(target) if target else ROOT / 'AutoDepthLive_v0.4.pyz'
    with tempfile.TemporaryDirectory(prefix='ultimodel-zipapp-') as folder:
        staging = Path(folder)
        for name in MODULES:
            shutil.copy2(ROOT / name, staging / name)
        zipapp.create_archive(staging, target=target,
                              interpreter='/usr/bin/env python3', compressed=True)
    return target


if __name__ == '__main__':
    print('Wrote', build())
