"""Audit the frozen book-only course; export full texts exclusively to local/."""
import argparse
import json
from pathlib import Path

from src.wengua import qwen_book_dataset_v3 as source
from src.wengua.qwen_book_course_audit_v1 import audit, candidate_repairs

ROOT = Path(__file__).resolve().parents[1]


def export(db, coordinate_path, output):
    output = output.resolve()
    if not output.is_relative_to((ROOT / 'local').resolve()):
        raise ValueError('Full source review must remain in ignored local/')
    if output.exists():
        raise ValueError('Preserve prior review; choose a new output directory')
    coordinates = json.loads(coordinate_path.read_text(encoding='utf8'))
    pack = source.build(db, coordinates)
    tables = source.load_tables(db)
    sections = {r['section_id']: r for r in tables['sections']}
    report = audit(pack, sections, coordinates)
    repairs = candidate_repairs(pack, report)
    output.mkdir(parents=True)
    def write(name, value):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    write('audit.json', report)
    write('summary.json', report['summary'])
    for name, rows in [('original_course.jsonl', pack['records']), ('question_repairs_DRAFT.jsonl', repairs)]:
        with (output / name).open('w', encoding='utf8') as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    # The role correction preserves the entire case and both voices. Nothing
    # here is automatically added to SFT or substituted into the old registry.
    weather = sections[43]['original_text'].splitlines()
    write('confirmed_weather_role_correction_DRAFT.json', {
        'case_id': 'kaiwu.final.weather', 'status': 'source_attribution_corrected_not_training_release',
        'student_report_lines': [416, 418], 'student_report': '\n'.join(weather[415:418]),
        'teacher_commentary_lines': [439, 445], 'teacher_commentary': '\n'.join(weather[438:445]),
        'student_wrong_inference_is_not_positive_teacher_answer': True,
        'training_eligible': False, 'old_registry_modified': False})
    workbook(pack, report, repairs, output)
    return report['summary']


def workbook(pack, report, repairs, output):
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Font
    book = Workbook(); book.remove(book.active)
    def sheet(name, headings, rows):
        ws = book.create_sheet(name); ws.append(headings)
        for row in rows:
            ws.append(row)
        ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]: cell.font = Font(bold=True)
        for cells in ws.iter_rows():
            for cell in cells:
                if isinstance(cell.value, str):
                    if len(cell.value) > 32767: raise ValueError('Excel cell would truncate text')
                    cell.data_type = 's'
                cell.alignment = Alignment(wrap_text=True, vertical='top')
        for column in ws.columns: ws.column_dimensions[column[0].column_letter].width = 36
        return ws
    sheet('审查结论', ['项目', '结果'], ((k, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
         for k, v in report['summary'].items()))
    originals = {r['id']: r for r in pack['records']}
    sheet('全部5250题目录', ['ID','格式','任务','分组','题目','问题标记','能力范围','状态'],
        ([r['id'],r['format'],r['task'],r['split'],originals[r['id']]['question'],
          '\n'.join(r['flags']),r['capability_bucket'],r['review_status']] for r in report['rows']))
    sheet('全部答案逐字分段', ['ID','段号','原参考答案（按28000字符分段，无删节）','出处'],
        ([r['id'],i//28000+1,r['answer'][i:i+28000],'\n'.join(r['source_ids'])]
         for r in pack['records'] for i in range(0,len(r['answer']),28000)))
    sheet('全部194案例', ['ID','领域','分组','原抄宫数','分析段数','老师按语坐标','已确认角色错误','语义时序审查完成'],
        ([r['case_id'],r['domain'],r['split'],r['printed_primary_cells'],r['registry_author_steps'],
          json.dumps(r['commentary_markers']),r['confirmed_role_defect'],False] for r in report['cases']))
    sheet('题目修订草稿', ['原ID','原题','修订题','答案保持原文','状态'],
        ([r['original_id'],originals[r['original_id']]['question'],r['question'],True,r['status']] for r in repairs))
    path = output / 'Wengua_全课题质量审查.xlsx'; book.save(path)
    with path.open('rb') as stream:
        check = load_workbook(stream, read_only=True)
        assert check['全部5250题目录'].max_row == len(pack['records']) + 1
        assert check['全部194案例'].max_row == len(pack['dossiers']) + 1
        from collections import defaultdict
        rebuilt = defaultdict(str)
        for rid, part, text, refs in check['全部答案逐字分段'].iter_rows(min_row=2, values_only=True):
            rebuilt[rid] += text or ''
        assert set(rebuilt) == set(originals)
        assert all(rebuilt[rid] == row['answer'] for rid, row in originals.items())
        check.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=ROOT/'archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3')
    parser.add_argument('--coordinates', type=Path, default=ROOT/'data/knowledge/qwen_book_only_v3/case_source_coordinates_20261104.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.db, args.coordinates, args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
