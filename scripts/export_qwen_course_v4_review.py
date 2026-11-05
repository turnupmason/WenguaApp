"""Private Excel review, with all original cases and registered author paragraphs."""
import argparse
import json
from pathlib import Path


def export(pack_path,output):
    from openpyxl import Workbook,load_workbook
    from openpyxl.styles import Alignment,Font,PatternFill
    p=json.loads(Path(pack_path).read_text(encoding='utf8'));w=Workbook();w.remove(w.active)
    def sheet(name,headers,rows):
        s=w.create_sheet(name);s.append(headers)
        for row in rows:
            if any(isinstance(x,str) and len(x)>32767 for x in row):raise ValueError('Excel cell limit; split source explicitly')
            s.append(row)
        s.freeze_panes='A2';s.auto_filter.ref=s.dimensions
        for c in s[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='325779')
        for col in s.columns:s.column_dimensions[col[0].column_letter].width=55 if col[0].column>2 else 24
        for row in s.iter_rows(min_row=2):
            for c in row:c.alignment=Alignment(wrap_text=True,vertical='top')
    sheet('全部3129教学任务',['任务ID','拆分','格式','问题及上下文','回答','来源ID','任务性质','案例ID','事件及盘面组'],
          [[r['id'],r['split'],r['format'],json.dumps(r['messages'][:-1],ensure_ascii=False),r['answer'],'\n'.join(r['source_ids']),r['source_mode'],r['case_id'],r['group']] for r in p['records']])
    notes={n['n']:n for n in p['review_notes']}
    sheet('全部194原书案例',['序号','案例ID','领域','原书断语','书中反馈','本次结果核对','原因证据','应期及反馈核对','防止误读'],
          [[i,d['case_id'],d['domain'],d['author_original_judgment'],d['later_feedback_separate'],notes[i]['result'],notes[i]['reason'],notes[i]['timing_and_feedback'],notes[i]['review_note']] for i,d in enumerate(p['dossiers'],1)])
    sheet('全部1008作者分析',['案例ID','步骤','原文','来源ID'],[[d['case_id'],s['step'],s['original'],s['source_id']] for d in p['dossiers'] for s in d['author_steps']])
    sheet('全部出处',['来源ID','原书','章节','行号','原文','来源标记'],[[u['id'],u['book_id'],u.get('section_id'),str(u.get('lines')),u['original_quote'],u.get('match_status')] for u in p['units'].values()])
    sheet('使用说明',['项目','内容'],[['训练用途','知识短答、条件追问、字面读盘、作者复盘与纠错；不把回顾性复盘称为未见盘预测。'],['人工评分','不使用旧人工吉凶分数或旧适配器。'],['完整性','194案例和1008登记分析全部保留；原书错误保留在原文层，纠错题另列。'],['限制','来源核对及逐条批注不等于不存在任何疏漏；效果看真实留出回答。']])
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);w.save(output)
    check=load_workbook(output,read_only=True,data_only=True)
    assert check['全部194原书案例'].max_row==195
    assert check['全部1008作者分析'].max_row==1009
    actual=list(check['全部3129教学任务'].values)[1:]
    assert len(actual)==len(p['records'])
    for r,x in zip(p['records'],actual):assert x[0]==r['id'] and x[4]==r['answer']
    cases=list(check['全部194原书案例'].values)[1:]
    for d,x in zip(p['dossiers'],cases):
        assert (x[1],x[3] or '',x[4] or '')==(d['case_id'],d['author_original_judgment'],d['later_feedback_separate'])
    steps=list(check['全部1008作者分析'].values)[1:]
    expected=[(d['case_id'],s['step'],s['original'],s['source_id']) for d in p['dossiers'] for s in d['author_steps']]
    assert steps==expected
    source_rows=list(check['全部出处'].values)[1:]
    for u,x in zip(p['units'].values(),source_rows):assert x[0]==u['id'] and x[4]==u['original_quote']
    check.close();return output

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('pack',type=Path);a.add_argument('output',type=Path);v=a.parse_args();print(export(v.pack,v.output))
