"""Build revised private material from pinned V5 pack and reviewed decisions."""
import argparse
from pathlib import Path
from src.wengua.course_repair_v51 import repair,load,dump,sha
from src.wengua.qwen_book_loop_v3 import private_output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v5-pack',required=True,type=Path);p.add_argument('--decisions',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    from src.wengua import course_training_v5 as old
    if sha(a.v5_pack.read_bytes())!=load(old.RELEASE)['files']['pack.json']:raise ValueError('Not the pinned parent V5 pack')
    from transformers import AutoTokenizer
    t=AutoTokenizer.from_pretrained('Qwen/Qwen3-8B',revision='b968826d9c46dd6066d109eabc6255188de91218',local_files_only=True)
    root=private_output(a.output)
    if root.exists():raise ValueError('Use a new build directory; previous audit output is preserved')
    pack,audit=repair(load(a.v5_pack),load(a.decisions),t);root.mkdir(parents=True)
    dump(root/'pack.json',pack);dump(root/'task_dispositions.json',audit);dump(root/'summary.json',pack['summary'])
    from scripts.build_course_complete_v5 import token_audit
    print(token_audit(root,t))

if __name__=='__main__':main()
