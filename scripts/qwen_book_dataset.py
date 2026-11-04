"""Build only the new book dataset; does not start model training."""
import argparse,json
from pathlib import Path
from src.wengua.qwen_book_dataset_v3 import build,export


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-db',type=Path,required=True)
    parser.add_argument('--case-source-coordinates',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--pool-size',type=int,default=1000000)
    parser.add_argument('--materialize',action='store_true')
    args=parser.parse_args(argv)
    if args.pool_size<4:parser.error('pool size must cover four formats')
    pack=build(args.source_db,json.loads(args.case_source_coordinates.read_text(encoding='utf8')))
    manifest=export(pack,args.output,args.pool_size,args.materialize)
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('issues','file_sha256')},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
