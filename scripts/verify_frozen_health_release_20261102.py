"""Validate the two user-accepted releases and exact production bundle resources."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/releases/health_frozen_20261102.json'


def verify(bundle=None):
    release = json.loads(MANIFEST.read_text())
    assert release['status'] == 'user_accepted_frozen'
    assert set(release['topics']) == {'health.severity', 'health.discomfort'}
    for item in release['files']:
        source = ROOT / item['path']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256'], item['path']
        if bundle and item['kind'] == 'resource':
            assert (bundle / source.name).read_bytes() == source.read_bytes(), source.name
    archive = ROOT / 'archives/retired_health_templates_20261102/INDEX.json'
    for item in json.loads(archive.read_text())['entries']:
        assert not (ROOT / item['original']).exists(), item['original']
        assert hashlib.sha256((ROOT / item['archive']).read_bytes()).hexdigest() == item['sha256']
    if bundle:
        assert (bundle / MANIFEST.name).read_bytes() == MANIFEST.read_bytes()
        expected = {Path(x['path']).name for x in release['files'] if x['kind'] == 'resource'} | {MANIFEST.name}
        actual = {p.name for p in bundle.iterdir() if p.suffix in {'.json', '.tsv'}}
        assert actual == expected, (actual, expected)
    return release

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path)
    args = parser.parse_args()
    verify(args.bundle)
    print('PASS sealed health.severity V9.0 scoring + V11 template; health.discomfort V27; retired templates excluded')
