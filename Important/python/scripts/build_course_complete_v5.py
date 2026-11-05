"""Build/audit the private two-book course; never writes plaintext into public data/."""
import argparse
from pathlib import Path
from src.wengua import course_complete_v5 as course
from src.wengua.qwen_book_loop_v3 import private_output,encode,target_views,generation_rows


def token_audit(root,tokenizer):
    pack=course.load(root/'pack.json');lengths=[];failed=[]
    for r in pack['records']:
        for view in target_views(r,0):
            encoded,n=encode(view,tokenizer,4096)
            lengths.append({'id':view['id'],'split':view['split'],'tokens':n,
                'assistant_tokens':sum(x!=-100 for x in encoded['labels']) if encoded else None})
            if encoded is None:failed.append({'id':view['id'],'tokens':n})
    fit,skips=generation_rows(pack['records'],tokenizer,{'eval_max_new_tokens':1024,'inference_max_context':4096})
    audit={'core_tasks':len(pack['records']),'assistant_views':len(lengths),'exclusions':failed,
        'max_tokens':max(x['tokens'] for x in lengths),'max_assistant_tokens':max(x['assistant_tokens'] or 0 for x in lengths),
        'generation_skips':skips,'generation_fits':len(fit),'tokenizer':'Qwen/Qwen3-8B',
        'revision':'b968826d9c46dd6066d109eabc6255188de91218','truncation':False}
    course.dump(root/'token_audit.json',audit);course.dump(root/'token_lengths.json',lengths)
    if failed or skips:raise ValueError('Course does not fit intact; revise sources/targets before training')
    return audit


def workbook(root,inputs_path):
    """Read back every cell; fail instead of silently clipping long source text."""
    import json
    from openpyxl import Workbook,load_workbook
    from openpyxl.cell import WriteOnlyCell
    p=course.load(root/'pack.json');inputs=course.load(inputs_path)
    book=Workbook(write_only=True);expected={}
    def sheet(name,header,rows):
        ws=book.create_sheet(name);values=[header,*rows];expected[name]=values
        for row in values:
            cells=[]
            for value in row:
                if value is None:value=''
                if not isinstance(value,(str,int,float,bool)):value=json.dumps(value,ensure_ascii=False)
                if isinstance(value,str) and len(value)>32767:raise ValueError('Excel cell needs explicit split')
                cell=WriteOnlyCell(ws,value=value)
                if isinstance(value,str):cell.data_type='s'
                cells.append(cell)
            ws.append(cells)
        ws.freeze_panes='A2'
    bykey={u['review_key']:u for u in inputs['inventory']}
    sheet('说明',['项目','内容'],[
        ['来源覆盖','仅指已提供并入库的两本书43个章节；不声称核对了未提供的纸本页。'],
        ['课程性质','基础、条件、原表读取、原案复盘；案例错断、后续反馈和更正分别保留。'],
        ['评测限制','来源复盘不等于未见盘预测；分数不等于现实命中率或临床概率。'],
        ['分组政策','通用知识进入训练，原案固定留出家族不回灌训练；最终测试不参与调参。'],
        ['不确定项','日奇人/入天罗等字形、作者假说、跨书异说保留，详见不确定项表。'],
        ['源数据库SHA256',p['source_sha256']],['课程统计',p['summary']]])
    sheet('全部课程',['ID','格式','分组','任务','问题','答案','完整对话','证据ID','案例ID','来源模式'],[
        [r['id'],r['format'],r['split'],r['task'],r['question'],r['answer'],r['messages'],r['source_ids'],r['case_ids'],r['source_mode']] for r in p['records']])
    sheet('1451知识覆盖',['审阅键','书','章','行','原文','处置','说明','对应课程'],[
        [x['key'],bykey[x['key']]['book_id'],bykey[x['key']]['chapter'],bykey[x['key']]['lines'],bykey[x['key']]['original_quote'],x['state'],x['reason'],x['task_ids']] for x in course.load(root/'general_coverage.json')])
    sheet('194全部原案',['案例','领域','背景及披露','主要判断','证据及原因','反馈与时序','核对','原断语','后续反馈原栏'],[
        [d['case_id'],d['domain'],n['context'],n['result'],n['reason'],n['timing_and_feedback'],n['review_note'],d['author_original_judgment'],d['later_feedback_separate']] for d,n in zip(p['dossiers'],p['review_notes'])])
    sheet('1008索引分析',['案例','步骤','证据ID','说话者身份','需更正','对应课程'],[
        [s['case_id'],s['step'],s['source_id'],s['speaker_status'],s['correction_required'],s['task_ids']] for s in course.load(root/'author_step_coverage.json')])
    sheet('案例正文补课',['章ID','行','案例','处置','说话者','对应课程'],[
        [s['section_id'],s['lines'],s['case_id'],s['state'],s.get('speaker',''),s['task_ids']] for s in course.load(root/'case_paragraph_coverage.json')])
    sheet('原盘逐宫读取',['案例','盘','宫','证据ID','对应课程'],[
        [s['case_id'],s['cast'],s['palace'],s['source_ids'],s['task_id']] for s in course.load(root/'chart_cell_coverage.json')])
    sheet('全部来源',['ID','书','章','行','匹配方式','原文'],[
        [u['id'],u['book_id'],u.get('chapter',''),u.get('lines',''),u.get('match_status',''),u['original_quote']] for u in p['units'].values()])
    sheet('不确定项',['原始记录'],[[x] for x in course.load(root/'source_uncertainties.json')])
    path=root/'Wengua_两书完整课程_v5.xlsx';book.save(path)
    actual=load_workbook(path,read_only=True,data_only=False)
    checked=0
    for name,rows in expected.items():
        got=list(actual[name].values)
        wanted=[tuple('' if v is None else v if isinstance(v,(str,int,float,bool)) else json.dumps(v,ensure_ascii=False) for v in row) for row in rows]
        normalized=[tuple('' if v is None else v for v in row) for row in got]
        if normalized!=wanted:raise ValueError('Excel round trip mismatch: '+name)
        checked+=sum(len(row) for row in rows)
    actual.close();course.dump(root/'excel_audit.json',{'all_cells_read_back':True,'checked_cells':checked,'sha256':course.sha(path.read_bytes())})
    return path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reviews',type=Path,required=True);p.add_argument('--v4-pack',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--coordinates',type=Path,default=Path('data/knowledge/qwen_book_only_v3/case_source_coordinates_20261104.json'))
    p.add_argument('--database',type=Path,default=Path('archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3'))
    a=p.parse_args();root=private_output(a.output)
    print(course.build(a.reviews,a.v4_pack,a.database,a.coordinates,root))
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained('Qwen/Qwen3-8B',revision='b968826d9c46dd6066d109eabc6255188de91218',local_files_only=True)
    print(token_audit(root,tok));print(workbook(root,a.reviews))

if __name__=='__main__':main()
