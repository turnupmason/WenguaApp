"""Reproduce the private two-book library from original WenguaApp sources."""
import argparse,gzip
from pathlib import Path
from src.wengua import book_rag as r
from src.wengua.book_rag_sources import build_two_book_library


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database',type=Path,required=True);p.add_argument('--course-pack',type=Path,required=True)
    p.add_argument('--fragments',type=Path,required=True);p.add_argument('--inventory',type=Path,required=True)
    p.add_argument('--coordinates',type=Path,default=Path('data/knowledge/qwen_book_only_v3/case_source_coordinates_20261104.json'))
    p.add_argument('--case-links',type=Path,required=True);p.add_argument('--step-reviews',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=r.private(a.output)
    if out.exists():raise ValueError('Choose a new source version output')
    from src.wengua.course_training_v51 import RELEASE
    if r.digest(a.course_pack.read_bytes())!=r.read(RELEASE)['files']['pack.json']:raise ValueError('Expected pinned reviewed V5.1 pack')
    inventory=r.read(a.inventory)
    if isinstance(inventory,dict):inventory=inventory['inventory']
    library,report=build_two_book_library(a.database,r.read(a.course_pack),r.read(a.coordinates),r.read(a.fragments),inventory,r.read(a.step_reviews),r.read(a.case_links))
    out.mkdir(parents=True);(out/'sources.json.gz').write_bytes(gzip.compress(r.dumps(library).encode('utf8'),mtime=0));r.write(out/'coverage.json',report)
    print(r.dumps(report))

if __name__=='__main__':main()
