"""Source-retrieval audits and private review exports; not prediction accuracy."""
from pathlib import Path
import html
from . import book_rag as r


def retrieval_checks(index,checks):
    rows=[]
    for check in checks:
        found=index.search(check['question'],mode=check.get('mode','knowledge'),domain=check.get('domain'),
            book=check.get('book'),case_id=check.get('case_id'),limit=check.get('limit',6))
        docs=found['documents'];parts=[p for d in docs for p in d['parts']]
        groups=[]
        for alternatives in check.get('source_groups',[]):
            groups.append(any(any(p['chapter']==chapter and p['lines'][0]<=line<=p['lines'][1] for p in parts) for chapter,line in alternatives))
        literal='\n'.join(d['content'] for d in docs)
        kept_conditions=all(s in literal for s in check.get('must_contain',[]))
        phase=check.get('required_phase');phase_found=not phase or any(d['phase']==phase for d in docs)
        no_leak=found['mode']=='study' or all(d['kind']=='rule' and not d['case_ids'] for d in docs)
        passed=bool(docs) and all(groups) and kept_conditions and phase_found and no_leak
        rows.append({'question':check['question'],'mode':found['mode'],'expected_source_groups':check.get('source_groups',[]),
            'source_groups_found':groups,'conditions_retained':kept_conditions,'phase_found':phase_found,
            'no_case_feedback_in_fresh_question':no_leak,'passed':passed,'retrieved_ids':[d['id'] for d in docs],
            'source_parts':parts})
    return {'checks':len(rows),'passed':sum(x['passed'] for x in rows),'failures':sum(not x['passed'] for x in rows),
        'meaning':'Targeted source-retrieval regression only, not model-answer or event-prediction accuracy',
        'rows':rows,'dense_embeddings_used':False,'actual_llm_inference_tested':False}


def review_html(index,output):
    target=r.private(output)
    if target.exists():raise ValueError('Review exports are immutable')
    e=html.escape;body=['<!doctype html><meta charset="utf-8"><title>WenguaApp 原书RAG索引审阅</title>',
        '<style>body{font:16px system-ui;max-width:1100px;margin:30px auto}pre{white-space:pre-wrap}details{padding:12px;border:1px solid #ddd;margin:10px}input{width:96%;padding:12px}</style>',
        '<h1>两书RAG来源索引</h1><p>所有正文来自原书定位片段；检索结果不是现实预测验证。case/reference仅用于来源复盘。这里只审阅来源，不加载模型。</p>',
        '<input id="q" placeholder="按书、章、案例编号或原文查找">']
    for raw, in index.db.execute('SELECT payload FROM documents ORDER BY id'):
        doc=index.expand(__import__('json').loads(raw));label=' | '.join([doc['id'],doc['kind'],doc['title'],','.join(doc['case_ids'])])
        sources='\n'.join('《'+s['book_title']+'》'+s['chapter']+' '+str(s['lines'])+' '+str(s['source_revision']) for s in doc['sources'])
        body+=['<details><summary>'+e(label)+'</summary><pre>'+e(sources+'\n阶段：'+doc['phase']+'\n\n'+doc['content'])+'</pre></details>']
    body+=['<script>document.getElementById("q").addEventListener("input",e=>{let q=e.target.value.toLowerCase();document.querySelectorAll("details").forEach(d=>d.hidden=!d.textContent.toLowerCase().includes(q));});</script>']
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(''.join(body),encoding='utf8');return target
