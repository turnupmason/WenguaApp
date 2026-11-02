"""Preserve the exact user timing notes privately, then validate public receipts."""
import argparse
import json
from pathlib import Path
from src.wengua.user_timing_notes_20261102 import archive_original, load_bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', type=Path)
    parser.add_argument('--private-dir', type=Path, default=Path('local/user_timing_notes/20261102'))
    args = parser.parse_args()
    if args.source_file:
        result = archive_original(args.source_file, args.private_dir)
    else:
        result = {'status': 'public_derivative_receipts_validated',
                  'source_id': load_bundle()['manifest']['source_id'],
                  'original_re_read_in_this_call': False}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
