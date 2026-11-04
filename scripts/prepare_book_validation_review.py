"""Read-only validation review pack. Never generates training data or runs a GPU."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import html
import json
from pathlib import Path

from src.wengua.qwen_book_loop_v3 import SOURCE_SHA256,atomic_json,file_sha,private_output,read_json,read_rows

CHECKS=('盘面事实','人物与取用','条件与例外','证据与综合','出处支持','信息不足处理','直接回答与表达')
OPTIONS=('符合','部分符合','不符合','不适用','待核')
NOTES=(
    '本表只导出固定validation划分；不展示最终test题，不修改任何训练文件或检查点。',
    '教材复核检查问答表达、来源对应与条件保真；不改原文列，意见写在复核意见列。',
    '模型验收表的模型回答和结论初始为空；只填实际模型输出，不预填或编造结果。',
    '原书辅助复盘、原盘字面读取和明确初问阶段分别保留source_mode，不冒充新盘盲测。',
    '七项只是人工复核维度，不是奇门吉凶算分、概率或自动专业正确率。',
    '这些记录不自动用于训练或选模型；当前loop的选择依据与最终测试冻结策略保持不变。',
    '共同验证16题对应当前固定生成验证；长题是另行诊断，2048实验未生成长题不能直接判作失败。',
    'book_knowledge=原书知识；literal_chart_reading=原抄盘事实读取。',
    'source_assisted_case_application、author_written_premise_application=提供作者资料或作者依据的应用题。',
    'complete_source_assisted_author_lesson=提供作者材料的完整复盘；explicit_initial_phase_reconstruction=明确初问阶段复原。',
)


def checked(path,receipt,key):
    path=Path(path)
    if file_sha(path)!=receipt['file_sha256'][key]:raise ValueError('Input hash mismatch: '+key)
    return read_rows(path)


def csv_file(path,headers,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(headers);writer.writerows(rows)


def prepare(dataset,prepared,output,*,long_prepared=None,xlsx=False):
    dataset=Path(dataset);prepared=Path(prepared);output=private_output(output)
    manifest=read_json(dataset/'manifest.json');receipt=read_json(prepared/'receipt.json')
    if any(r['source_database_sha256']!=SOURCE_SHA256 for r in (manifest,receipt)):
        raise ValueError('Only the pinned book-only source is allowed')
    if manifest.get('legacy_score_teachers_used') or manifest.get('non_book_supplements_used'):
        raise ValueError('Non-book teachers forbidden')
    cores=checked(dataset/'core_tasks.jsonl.gz',manifest,'core_tasks.jsonl.gz')
    units=checked(dataset/'source_units.jsonl.gz',manifest,'source_units.jsonl.gz')
    prepared_units=checked(prepared/'source_units.jsonl.gz',receipt,'source_units.jsonl.gz')
    validation=[r for r in cores if r['split']=='validation']
    common=checked(prepared/'validation_prompts.jsonl.gz',receipt,'validation_prompts.jsonl.gz')
    long=[]
    if long_prepared is not None:
        long_prepared=Path(long_prepared);proof=read_json(long_prepared/'receipt.json')
        if proof['source_database_sha256']!=SOURCE_SHA256:raise ValueError('Long source changed')
        long=checked(long_prepared/'extended_validation_prompts.jsonl.gz',proof,'extended_validation_prompts.jsonl.gz')
    if not validation or not common:raise ValueError('Validation pool and common questions must be nonempty')
    core_by_id={r['id']:r for r in validation};unit_by_id={r['id']:r for r in units};prepared_by_id={r['id']:r for r in prepared_units}
    if len(core_by_id)!=len(validation):raise ValueError('Duplicate validation task IDs')
    for row in [*validation,*common,*long]:
        if row.get('split')!='validation' or row['id'] not in core_by_id:raise ValueError('Non-validation row rejected')
        original=core_by_id[row['id']]
        for key in ('messages','answer','source_ids','group','source_mode'):
            if row[key]!=original[key]:raise ValueError('Reference changed: '+row['id'])
        if row['answer']!=row['messages'][-1]['content']:raise ValueError('Answer/turn mismatch')
        if not row['source_ids'] or any(uid not in unit_by_id for uid in row['source_ids']):raise ValueError('Missing source')
        for uid in row['source_ids']:
            if uid not in prepared_by_id or any(unit_by_id[uid][key]!=prepared_by_id[uid][key] for key in ('original_quote','source_sha256','book_id','chapter','lines')):
                raise ValueError('Prepared source differs from dataset source: '+uid)
    if output.exists():raise FileExistsError('Preserve existing human review; choose a new output')
    workbook=None
    if xlsx:
        from openpyxl import Workbook
        workbook=Workbook();workbook.remove(workbook.active)
    output.mkdir(parents=True)
    common_ids={r['id'] for r in common};long_ids={r['id'] for r in long}
    def priority(row):return '共同验证' if row['id'] in common_ids else '长题诊断' if row['id'] in long_ids else '验证池'
    def prompt(row):return '输入：\n'+'\n\n'.join(m['role']+'：'+m['content'] for m in row['messages'][:-1])
    def reference(row):return '书源参考：\n'+row['answer']
    validation.sort(key=lambda r:(r['id'] not in common_ids,r['id'] not in long_ids,r['format'],r['id']))
    source_ids={uid for row in validation for uid in row['source_ids']}
    links=[];source_rows=[]
    for uid in sorted(source_ids):
        unit=unit_by_id[uid];quote=unit['original_quote']
        # Excel cells have a hard 32767-character limit; split, never truncate.
        parts=[quote[i:i+30000] for i in range(0,len(quote),30000)] or ['']
        for n,part in enumerate(parts,1):source_rows.append([uid,unit['book_id'],unit['chapter'],str(unit['lines']),unit['source_sha256'],n,len(parts),'原文：\n'+part])
    headers=['任务ID','优先级','格式','任务类型','原案ID','来源分组','资料方式','完整输入','原样参考答案','来源ID','教材表达复核','复核意见与出处']
    review_rows=[]
    for row in validation:
        review_rows.append([row['id'],priority(row),row['format'],row['task'],row.get('case_id') or '',row['group'],row['source_mode'],prompt(row),reference(row),'; '.join(row['source_ids']),'',''])
        links.extend([row['id'],uid] for uid in row['source_ids'])
    selected=[r for r in validation if r['id'] in common_ids|long_ids]
    answer_headers=headers[:10]+['模型或配置ID','实际模型回答',*CHECKS,'错误类型','人工结论','修改建议与出处']
    answer_rows=[r[:10]+['']*(len(answer_headers)-10) for r in review_rows if r[0] in common_ids|long_ids]
    sheets=[('开始这里',['说明'],[[s] for s in NOTES]),('教材复核',headers,review_rows),('模型验收',answer_headers,answer_rows),
        ('出处',['来源ID','书ID','章节','原文行','原章SHA256','分段','总段数','完整原文'],source_rows),('来源关联',['任务ID','来源ID'],links)]
    for name,columns,rows in sheets:
        csv_file(output/(name+'.csv'),columns,rows)
        if workbook is not None:
            from openpyxl.styles import Alignment,Font,PatternFill
            sheet=workbook.create_sheet(name);sheet.append(columns)
            for values in rows:
                if any(isinstance(value,str) and len(value)>32767 for value in values):
                    raise ValueError('Excel cell limit exceeded; use CSV/HTML instead of truncating source text')
                sheet.append(values)
                for cell in sheet[sheet.max_row]:
                    if isinstance(cell.value,str):cell.data_type='s'
                    cell.alignment=Alignment(vertical='top',wrap_text=True)
                sheet.row_dimensions[sheet.max_row].height=85
            for cell in sheet[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='173A47')
            sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
            for column in sheet.columns:sheet.column_dimensions[column[0].column_letter].width=24
            for field in ('完整输入','原样参考答案','实际模型回答','完整原文','复核意见与出处'):
                if field in columns:sheet.column_dimensions[sheet.cell(1,columns.index(field)+1).column_letter].width=70
    if workbook is not None:
        from openpyxl.worksheet.datavalidation import DataValidation
        sheet=workbook['模型验收'];rule=DataValidation(type='list',formula1='"'+','.join(OPTIONS)+'"',allow_blank=True)
        sheet.add_data_validation(rule)
        for check in CHECKS:
            col=answer_headers.index(check)+1;rule.add(f'{sheet.cell(1,col).column_letter}2:{sheet.cell(1,col).column_letter}{len(answer_rows)+1}')
        workbook.save(output/'Wengua_Validation_Review.xlsx')
    # Browser reading copy; all source text is escaped and model answers stay blank.
    body=['<!doctype html><meta charset="utf-8"><title>问卦验证资料复核</title><style>body{max-width:1100px;margin:35px auto;font:16px sans-serif}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{padding:12px;border:1px solid #ccc;margin:8px}</style><h1>验证资料复核</h1>']
    body.extend('<p>'+html.escape(s)+'</p>' for s in NOTES)
    for row in validation:
        quotes='\n\n'.join(uid+'\n'+unit_by_id[uid]['original_quote'] for uid in row['source_ids'])
        body.append('<details><summary>'+html.escape(priority(row)+' | '+row['format']+' | '+row['id'])+'</summary><pre>'+html.escape(prompt(row)+'\n\n'+reference(row)+'\n\n资料方式：'+row['source_mode']+'\n\n'+quotes)+'</pre></details>')
    (output/'review.html').write_text('\n'.join(body),encoding='utf8')
    summary={'validation_tasks':len(validation),'formats':dict(Counter(r['format'] for r in validation)),
        'common_validation_questions':len(common),'long_diagnostic_questions':len(long),'answer_review_rows':len(selected),
        'source_units':len(source_ids),'source_database_sha256':SOURCE_SHA256,'training_files_changed':False,
        'test_questions_exported':False,'human_ratings_prefilled':False,'model_answers_prefilled':False,
        'training_eligible':False,'independent_new_case_evaluation':False,
        'exporter_text_sha256':hashlib.sha256(Path(__file__).read_text(encoding='utf8').encode()).hexdigest(),
        'input_sha256':{'core_tasks':file_sha(dataset/'core_tasks.jsonl.gz'),'common_validation':file_sha(prepared/'validation_prompts.jsonl.gz')},
        'files':{p.name:file_sha(p) for p in output.iterdir() if p.is_file()}}
    atomic_json(output/'review_manifest.json',summary);return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,required=True);parser.add_argument('--prepared',type=Path,required=True)
    parser.add_argument('--long-prepared',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--xlsx',action='store_true')
    args=parser.parse_args();print(json.dumps(prepare(args.dataset,args.prepared,args.output,long_prepared=args.long_prepared,xlsx=args.xlsx),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
