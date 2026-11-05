"""Run the unchanged 8B CLI with native-error sidecars and live stderr."""
import argparse
import faulthandler
import sys

from src.wengua.qwen8b_diagnostics_v1 import diagnostic_processes


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    # Recognize options before the command too, without importing training code.
    check = argparse.ArgumentParser(add_help=False)
    for option in ('--spec', '--output', '--hours', '--resume-from-checkpoint'):
        check.add_argument(option)
    for option in ('--resume', '--offline'):
        check.add_argument(option, action='store_true')
    check.add_argument('command', nargs='?')
    request, _ = check.parse_known_args(arguments)
    if request.command == 'run' and not {'-h', '--help'}.intersection(arguments):
        print('旧版 bookv3 课程已暂停：已确认题目范围含糊及说话人标注错误。'
              '保留现有模型和检查点；完成新课程审查后使用独立训练目录。'
              '见 docs/QWEN_BOOK_COURSE_REVIEW_20261105.md。', file=sys.stderr)
        return 3
    from scripts.qwen8b_research import main as training_main
    faulthandler.enable(all_threads=True)
    with diagnostic_processes():return training_main(arguments)


if __name__=='__main__':raise SystemExit(main())
