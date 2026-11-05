"""WenguaApp two-book RAG: CPU index/search; existing program cast; sealed 8B inference."""
import argparse,gzip,json,time
from pathlib import Path
from src.wengua import book_rag as r

RELEASE=r.ROOT/'data/knowledge/book_rag_v1/release.json'
DEFAULT_DATA=r.ROOT/'local/wengua_rag/sources_v1'
DEFAULT_INDEX=r.ROOT/'local/wengua_rag/index_v1.sqlite3'


def load_library(path):
    path=r.private(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw.decode('utf-8-sig'))


def install(archive,destination=DEFAULT_DATA):
    import zipfile,shutil
    release=r.read(RELEASE);archive=Path(archive);destination=r.private(destination)
    if r.digest(archive.read_bytes())!=release['archive_sha256']:raise ValueError('Wrong private RAG source package')
    if destination.exists():verify_sources(destination);return destination
    pending=destination.with_name(destination.name+'.pending')
    if pending.exists():raise ValueError('Incomplete source installation preserved')
    with zipfile.ZipFile(archive) as z:
        if len(set(z.namelist()))!=len(z.namelist()) or set(z.namelist())!=set(release['files']):raise ValueError('Wrong source ZIP members')
        if any(Path(n).is_absolute() or '..' in Path(n).parts or '\\' in n for n in z.namelist()):raise ValueError('Unsafe source ZIP member')
        pending.mkdir(parents=True)
        for name,digest in release['files'].items():
            data=z.read(name)
            if r.digest(data)!=digest:raise ValueError('Source ZIP member changed')
            target=pending/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    verify_sources(pending);pending.rename(destination);return destination


def verify_sources(root):
    root=r.private(root);release=r.read(RELEASE)
    for name,digest in release['files'].items():
        if r.digest((root/name).read_bytes())!=digest:raise ValueError('Source library file changed: '+name)
    return load_library(root/'sources.json.gz')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    build=sub.add_parser('build',help='CPU only; immutable new index')
    build.add_argument('--archive',type=Path);build.add_argument('--library',type=Path,action='append')
    build.add_argument('--output',type=Path,default=DEFAULT_INDEX);build.add_argument('--activate',action='store_true')
    stage=sub.add_parser('stage-chapter',help='Archive incoming source as draft; no automatic approval/indexing')
    stage.add_argument('--input',required=True,type=Path);stage.add_argument('--book-id',required=True);stage.add_argument('--book-title',required=True)
    stage.add_argument('--chapter-id',required=True);stage.add_argument('--title',required=True);stage.add_argument('--method-id',required=True)
    stage.add_argument('--revision',required=True);stage.add_argument('--output',required=True,type=Path)
    reviewed=sub.add_parser('reviewed-chapter',help='Build source library from an explicitly completed source review')
    reviewed.add_argument('--draft',required=True,type=Path);reviewed.add_argument('--review',required=True,type=Path);reviewed.add_argument('--output',required=True,type=Path)
    audit=sub.add_parser('audit');audit.add_argument('--index',type=Path,default=None);audit.add_argument('--checks',required=True,type=Path);audit.add_argument('--output',required=True,type=Path)
    review=sub.add_parser('review');review.add_argument('--index',type=Path,default=None);review.add_argument('--output',required=True,type=Path)
    active=sub.add_parser('activate');active.add_argument('--index',type=Path,required=True)
    inspect=sub.add_parser('inspect');inspect.add_argument('--index',type=Path,default=None)
    cast=sub.add_parser('cast');cast.add_argument('--time',required=True);cast.add_argument('--zone',required=True);cast.add_argument('--output',required=True,type=Path)
    chapter=sub.add_parser('chapter');chapter.add_argument('--index',type=Path,default=None);chapter.add_argument('--id',required=True);chapter.add_argument('--output',type=Path)
    event=sub.add_parser('case');event.add_argument('--index',type=Path,default=None);event.add_argument('--id',required=True);event.add_argument('--output',required=True,type=Path)
    for name in ('search','prompt','ask'):
        q=sub.add_parser(name);q.add_argument('--question',required=True);q.add_argument('--index',type=Path,default=None)
        q.add_argument('--mode',choices=['knowledge','reading','study'],default='knowledge');q.add_argument('--domain');q.add_argument('--book');q.add_argument('--case-id');q.add_argument('--limit',type=int,default=8)
        if name=='search':q.add_argument('--json',action='store_true');q.add_argument('--output',type=Path)
        if name!='search':
            q.add_argument('--time');q.add_argument('--zone');q.add_argument('--chart',type=Path);q.add_argument('--facts',type=Path)
            q.add_argument('--max-new-tokens',type=int,default=768);q.add_argument('--output',type=Path)
        if name=='ask':
            q.add_argument('--adapter',type=Path);q.add_argument('--run',type=Path,default=r.ROOT/'local/course_v51/run1');q.add_argument('--base-only',action='store_true')
    a=p.parse_args(argv)
    if a.command in ('stage-chapter','reviewed-chapter'):
        from src.wengua.book_rag_sources import stage_chapter,reviewed_chapter_library
        target=r.private(a.output)
        if target.exists():raise ValueError('Source versions/reviews are immutable; choose a new path')
        if a.command=='stage-chapter':value=stage_chapter(a.input,book_id=a.book_id,book_title=a.book_title,chapter_id=a.chapter_id,title=a.title,method_id=a.method_id,revision=a.revision)
        else:value=reviewed_chapter_library(r.read(a.draft),r.read(a.review))
        r.write(target,value);print('Source version written: '+str(target));return 0
    if a.command=='activate':print(r.dumps(r.activate_index(a.index)));return 0
    if a.command=='build':
        if a.library:libraries=[load_library(x) for x in a.library]
        else:
            if a.archive:install(a.archive)
            if not DEFAULT_DATA.exists():
                name=r.read(RELEASE)['archive_name'];path=Path.home()/'Downloads'/name
                if not path.is_file():raise FileNotFoundError('First restore the private source package with unlock_wengua_rag.py')
                install(path)
            libraries=[verify_sources(DEFAULT_DATA)]
        result=r.build_index(libraries,a.output)
        if a.activate or not (r.ROOT/'local/wengua_rag/active_index.json').exists():r.activate_index(a.output)
        print(r.dumps(result));return 0
    if a.command=='cast':
        from src.wengua.book_rag_query import cast_time
        target=r.private(a.output)
        if target.exists():raise ValueError('Program chart receipts are immutable')
        result=cast_time(a.time,a.zone);r.write(target,result);print('Program chart written: '+str(target));return 0
    with r.Index(a.index or r.active_index()) as index:
        if a.command=='inspect':print(r.dumps(index.coverage));return 0
        if a.command=='review':
            from src.wengua.book_rag_audit import review_html
            print('Source review written: '+str(review_html(index,a.output)));return 0
        if a.command=='audit':
            from src.wengua.book_rag_audit import retrieval_checks
            target=r.private(a.output)
            if target.exists():raise ValueError('Preserve previous audit')
            result=retrieval_checks(index,r.read(a.checks));r.write(target,result)
            print(r.dumps({k:v for k,v in result.items() if k!='rows'}));return 0 if result['failures']==0 else 2

        if a.command=='chapter':
            value=index.chapters[a.id]
            if a.output:r.write(r.private(a.output),value)
            else:print(value['original_text'])
            return 0
        if a.command=='case':r.write(r.private(a.output),index.case(a.id));print('Historical case sources written: '+str(a.output));return 0
        packet=None
        if a.command!='search':
            from src.wengua.book_rag_query import cast_time,checked_chart,make_prompt
            if a.chart and a.time:raise ValueError('Choose a program chart receipt or time, not both')
            if a.chart:packet=checked_chart(r.read(a.chart))
            elif a.time:
                if not a.zone:raise ValueError('Time casting uses the existing App calendar and requires its explicit timezone')
                packet=cast_time(a.time,a.zone)
        result=index.search(a.question,mode=a.mode,domain=a.domain,book=a.book,case_id=a.case_id,
            limit=a.limit if a.command=='search' else 20,method_id=packet['method_id'] if packet else None)
        if a.command=='search':
            if a.output:
                target=r.private(a.output)
                if target.exists():raise ValueError('Preserve previous retrieval trace')
                r.write(target,result)
            if a.json:print(json.dumps(result,ensure_ascii=False,indent=2))
            else:
                print('原书检索结果（CPU，不加载模型）：')
                for number,doc in enumerate(result['documents'],1):
                    print('[S'+str(number)+'] '+'；'.join('《'+s['book_title']+'》'+s['chapter']+' 原文第'+str(s['lines'][0])+'—'+str(s['lines'][1])+'行' for s in doc['sources']))
                    if doc.get('editorial_notice'):print(doc['editorial_notice'])
                    if doc.get('source_uncertainties'):print('待校勘：'+r.dumps(doc['source_uncertainties']))
                    if doc.get('interpretation_limits'):print('整理范围：'+r.dumps(doc['interpretation_limits']))
                    print(doc.get('reading_content',doc['content']))
                if not result['documents']:print('未检到符合当前来源范围的片段；请明确领域、书目或案例编号。')
            return 0
        from transformers import AutoTokenizer
        tok=AutoTokenizer.from_pretrained('Qwen/Qwen3-8B',revision='b968826d9c46dd6066d109eabc6255188de91218',local_files_only=True,trust_remote_code=False)
        prompt=make_prompt(result,a.question,tok,packet=packet,facts=r.read(a.facts) if a.facts else None,max_new_tokens=a.max_new_tokens)
        output=r.private(a.output or r.ROOT/'local/wengua_rag/traces'/(str(time.time_ns())+'_'+a.command+'.json'))
        if output.exists():raise ValueError('Choose a new trace output')
        if a.command=='prompt':r.write(output,prompt);print(r.dumps({'state':prompt['state'],'prompt_budget':prompt['prompt_budget'],'path':str(output),'GPU_loaded':False}));return 0
        from src.wengua.book_rag_inference import answer
        adapter=a.adapter
        if adapter is None:
            status=r.read(r.private(a.run)/'phase_status.json')
            if status.get('state')!='complete':raise ValueError('V5.1 is not complete yet; CPU search/prompt can be used while it trains')
            adapter=Path(status['adapter'])
        value=answer(prompt,adapter,output,base_only=a.base_only);print(value['answer'])
        if value['checks']['status']!='citations_checked_semantics_unverified':print('引用或盘面核对未通过；原答及原因已保留：'+str(output));return 2
        used=set(value['checks']['used_citations'])
        for doc in value['references']:
            if doc['citation'] in used:
                print('['+doc['citation']+'] '+'；'.join('《'+s['book_title']+'》'+s['chapter']+'，原文第'+str(s['lines'][0])+'—'+str(s['lines'][1])+'行' for s in doc['sources']))
        return 0

if __name__=='__main__':raise SystemExit(main())
