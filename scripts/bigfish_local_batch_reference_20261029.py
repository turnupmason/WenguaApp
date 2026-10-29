#!/usr/bin/env python3
"""BigFish original shijia board -> frozen Wengua health V8 textual pipeline.

A new engine is genuinely used for all nine physical palaces. The old Wengua
casting path is for independent audit *only*; never injected as BigFish data.
Differences yield an UNAPPROVED candidate (never falsely label parity PASS).
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import traceback
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'vendor' / 'WenguaApp'
UPSTREAM = ROOT / 'vendor' / 'bigfish'
COMPILED = ROOT / 'vendor' / 'bigfish-compiled'
FROZEN = ROOT / 'frozen'
OUTPUT = ROOT / 'output'
BIGFISH_SHA = '6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c'
WENGUA_SHA = '0eae7d2b94742939e885938f8603e85c9452d1c3'
METHODS = ('chaibu', 'maoshan', 'zhirun')
ACTORS = frozenset(('self','father','mother','grandfather','grandmother',
                    'colleague','friend','older_sibling','younger_sibling','son','daughter'))
GUA = {1:'坎', 2:'坤', 3:'震', 4:'巽', 5:'中', 6:'乾', 7:'兑', 8:'艮', 9:'离'}
STARS = frozenset(('天蓬','天芮','天冲','天辅','天心','天柱','天任','天英'))
DOORS = frozenset(('休门','生门','伤门','杜门','景门','死门','惊门','开门'))
GODS = frozenset(('值符','螣蛇','太阴','六合','白虎','玄武','九地','九天'))
RING = frozenset((1,2,3,4,6,7,8,9))
GRADE = {-5:'极大凶',-4:'大凶',-3:'中凶',-2:'小凶',-1:'极小凶',
          0:'微恙',1:'极小吉',2:'小吉',3:'中吉',4:'大吉',5:'极大吉'}


def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def digest(x):
    return hashlib.sha256(x).hexdigest()


def _git_head(directory):
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=directory,text=True).strip()


def check_install():
    if not (UPSTREAM/'src/engines/shijia.ts').is_file():
        raise RuntimeError('首次先双击 install.command（联网安装 Git 固定版本）')
    if not (COMPILED/'engines/shijia.js').is_file():
        raise RuntimeError('BigFish TypeScript 未编译，请重跑 install.command')
    if not (SOURCE/'src/wengua/health_severity_vnext_review.py').is_file():
        raise RuntimeError('冻结 Wengua 原版 Python 缺失；请重跑 install.command')
    meta=json.loads((FROZEN/'FREEZE_MANIFEST.json').read_text(encoding='utf-8'))
    if meta['bigfish_sha']!=BIGFISH_SHA or meta['wengua_sha']!=WENGUA_SHA:
        raise RuntimeError('安装版本与固定源码版本不一致')
    if _git_head(UPSTREAM)!=BIGFISH_SHA or _git_head(SOURCE)!=WENGUA_SHA:
        raise RuntimeError('Git 工作树 HEAD 已改变；冻结验收中止')
    for name,entry in meta['files'].items():
        own=FROZEN/name
        original=SOURCE/entry['source']
        if not own.is_file() or not original.is_file():
            raise RuntimeError('原始冻结数据缺失：'+name)
        if digest(own.read_bytes())!=entry['sha256'] or digest(original.read_bytes())!=entry['sha256']:
            raise RuntimeError('冻结文件与源SHA256不一致：'+name)
    return meta


def parse_instant(iso, timezone_name):
    instant=dt.datetime.fromisoformat(iso)
    if instant.tzinfo is None:
        raise ValueError('必须提供含 UTC 偏移的真实 ISO 时刻')
    local=instant.astimezone(ZoneInfo(timezone_name))
    if local.hour==23:
        raise ValueError('晚子时23点换日规则仍存流派分歧，此版本拒绝')
    if local.astimezone(dt.timezone.utc).astimezone(ZoneInfo(timezone_name))!=local:
        raise ValueError('DST 本地时间不存在')
    return local


def iso_wall_clock(instant, timezone_name):
    """Prevent different offsets or ambiguous instant being silently cast."""
    x=parse_instant(instant,timezone_name)
    return x.isoformat()


def source_calendar(instant, timezone_name):
    sys.path.insert(0,str(SOURCE))
    from src.wengua.astro_calendar import solar_chart_clock
    from src.wengua.casting_shenqi import bureau_for_term
    clock=solar_chart_clock(instant.isoformat(),timezone_name)
    pillars=clock['four_pillars']
    bureau=bureau_for_term(pillars['day'],clock['active_solar_term'])
    return clock,pillars,bureau


def invoke_bigfish(pillars, term, method, *, elapsed_hours=None, day_gz_index=None,
                   days_since_term=None, next_term=None, days_to_next_term=None):
    payload={'compiled_root':str(COMPILED),'pillars':pillars,'solar_term':term,'method':method}
    if method=='maoshan':payload['elapsed_hours']=elapsed_hours
    if method=='zhirun':payload.update(day_gz_index=day_gz_index,days_since_term=days_since_term,
                                       next_term=next_term,days_to_next_term=days_to_next_term)
    completed=subprocess.run(['node',str(ROOT/'bigfish_cast.cjs')],input=canonical(payload),
                             capture_output=True,text=True,timeout=90)
    if completed.returncode:
        raise RuntimeError('BigFish original engine failed: '+completed.stderr[-2000:])
    raw=json.loads(completed.stdout)
    if raw.get('provenance')!='perfhelf/bigfishmarquis-qimen':
        raise ValueError('Unexpected source-of-chart')
    return raw


def normalize_bigfish(raw):
    """Preserve the original Wengua-compatible star/door/god identities.

    Upstream shijia.ts explicitly says `skyStem = eStem` and
    `earthStem = hStem`. Read by *meaning*, not misleading property names.
    Never infer TianQin carrier from the old Wengua chart.
    """
    chart=raw['chart']
    source=chart['palaces']
    by_id={int(p['palaceNumber']):p for p in source}
    if set(by_id)!=set(range(1,10)) or len(source)!=9:
        raise ValueError('BigFish must return exactly nine unique palaces')
    palaces={}
    heaven_seen=[]
    doors_seen=[]
    gods_seen=[]
    for i in range(1,10):
        p=by_id[i]
        if p.get('palaceName')!=GUA[i]:raise ValueError(f'宫号与宫名不对应:{i}')
        earth=p.get('skyStem') # intentionally the actual 地盘干 in upstream
        sky=p.get('earthStem') # intentionally the actual 天盘干 in upstream
        star=p.get('star') or ''
        door=p.get('door') or None
        deity=(p.get('god') or '').replace('腾蛇','螣蛇') or None
        if not isinstance(earth,str) or len(earth)!=1:
            raise ValueError('Invalid source physical earth stem at '+str(i))
        if i==5:
            if star not in ('天禽','') or sky or door or deity:
                raise ValueError('中五不能出现普通星/门/神/天盘干')
            heavens=[]
        else:
            if star not in STARS or door not in DOORS or deity not in GODS:
                raise ValueError(f'第{i}宫缺真实星/门/神: {star}/{door}/{deity}')
            if not isinstance(sky,str) or len(sky)!=1:
                raise ValueError('Missing real carried sky stem at '+str(i))
            heavens=[{'star':star+'星','carried_stem':sky}]
            if star=='天芮':
                resident=p.get('jiGanStem')
                if not resident or resident!=by_id[5]['skyStem']:
                    raise ValueError('天芮天禽寄宫必须保留中宫实际地干，不得借用天芮携干')
                heavens.append({'star':'天禽星','carried_stem':resident})
            heaven_seen.extend(x['star'] for x in heavens)
            doors_seen.append(door)
            gods_seen.append(deity)
        palaces[str(i)]={'palace':i,'gua':GUA[i],
                         'earth_stem':earth,'heaven_stars':heavens,
                         'door':door,'deity':deity}
    if (len(heaven_seen),len(set(heaven_seen)))!=(9,9):
        raise ValueError('Missing or repeated physical heavenly star (including TianQin)')
    if len(set(doors_seen))!=8 or len(set(gods_seen))!=8:
        raise ValueError('Eight doors / eight deities missing or repeated')
    if len(set(p['earth_stem'] for p in palaces.values()))!=9:
        raise ValueError('Earth nine actual six-yis must be unique')
    if not chart['fourPillars']:
        raise ValueError('Source lost calendar four pillars')
    year_month_day_hour={k:chart['fourPillars'][k]['gan']+chart['fourPillars'][k]['zhi']
                         for k in ('year','month','day','hour')}
    # Original fields never overwrite: preserve raw as separate immutable JSON.
    return {'source':'perfhelf/bigfishmarquis-qimen',
            'method':raw['method'],'dun':chart['dun'],'ju':chart['juNumber'],
            'palaces':palaces,'pillars':year_month_day_hour,
            'xun_void_branches':chart.get('kongWang'),
            'value_star':chart['zhiFuStar']+'星',
            'value_star_palace':chart['zhiFuPalace'],
            'value_door':chart['zhiShiDoor'],
            'value_door_palace':chart['zhiShiPalace'],
            'yuan':chart['yuan'],'bureau_raw':raw['bureau'],
            'source_marks':{str(i):by_id[i].get('marks') for i in range(1,10)},
            'extra_source_fields':{'ji_gan':{str(i):by_id[i].get('jiGanStem') for i in range(1,10)},
                                   'di_gods':{str(i):by_id[i].get('diGod') for i in range(1,10)}}}


def compare_old(q,pillars,bureau,reference):
    """Diagnostic only. A different school is allowed, never a forged PASS."""
    differences=[]
    def check(path,new,old):
        if new!=old:differences.append({'path':path,'bigfish':new,'shenqi_reference':old})
    check('calendar.four_pillars',q['pillars'],pillars)
    check('bureau.dun',q['dun'],bureau['dun'])
    check('bureau.ju',q['ju'],bureau['ju'])
    check('bureau.yuan',q['yuan'],{'upper':'上','middle':'中','lower':'下'}.get(bureau['yuan']))
    check('value_star',q['value_star'],reference['value_star'])
    check('value_star_palace',q['value_star_palace'],reference['value_star_palace'])
    check('value_door',q['value_door'],reference['value_door'])
    check('value_door_palace',q['value_door_palace'],reference['value_door_palace'])
    for i in range(1,10):
        a=q['palaces'][str(i)]
        b=reference['palaces'][str(i)]
        for field in ('earth_stem','door','deity'):
            check(f'palaces.{i}.{field}',a[field],b[field])
        check(f'palaces.{i}.heaven_stars',
              sorted((s['star'],s['carried_stem']) for s in a['heaven_stars']),
              sorted((s['star'],s['carried_stem']) for s in b['heaven_stars']))
    return differences


def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)


def database():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(OUTPUT/'progress.sqlite3')
    con.execute('''CREATE TABLE IF NOT EXISTS records
        (case_id TEXT PRIMARY KEY, instant TEXT NOT NULL, zone TEXT NOT NULL,
         actor TEXT NOT NULL, method TEXT NOT NULL, status TEXT NOT NULL,
         notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    con.commit()
    return con


def process(iso,zone,actor,method='chaibu',*,force=False,db=None):
    if actor not in ACTORS:raise ValueError('Unrecognized real relationship')
    if method not in METHODS:raise ValueError('Unsupported BigFish method')
    check_install()
    instant=parse_instant(iso,zone)
    iso=instant.isoformat()
    id_=digest(canonical([BIGFISH_SHA,WENGUA_SHA,iso,zone,actor,method]).encode())[:28]
    own=db is None
    con=db or database()
    old=con.execute('SELECT status FROM records WHERE case_id=?',(id_,)).fetchone()
    if old and not force:return {'case_id':id_,'status':'already_recorded','previous':old[0]}
    dir_=OUTPUT/'cases'/id_
    if force and dir_.exists():
        n=1
        while (dir_/f'attempt_{n:04d}').exists():n+=1
        dir_=dir_/f'attempt_{n:04d}'
    dir_.mkdir(parents=True,exist_ok=True)
    audit={'case_id':id_,'source':'perfhelf/bigfishmarquis-qimen','upstream_sha':BIGFISH_SHA,
           'wengua_frozen_sha':WENGUA_SHA,'instant':iso,'timezone':zone,
           'actor':actor,'method':method,'approved_for_app':False,
           'medical_validity_claimed':False,'status':'pending'}
    try:
        clock,pillars,old_bureau=source_calendar(instant,zone)
        term=clock['active_solar_term']
        kwargs={}
        if method=='maoshan':
            # No precise term instant is exposed by this wrapper. Never invent.
            raise ValueError('maoshan requires verified exact elapsed_hours; not wired in this release')
        if method=='zhirun':
            raise ValueError('zhirun requires original verified term-day counters; not wired in this release')
        raw=invoke_bigfish(pillars,term,method,**kwargs)
        write_json(dir_/'bigfish_original.json',raw)
        q=normalize_bigfish(raw)
        audit['source_board']=q
        if q['pillars']!=pillars:
            raise ValueError('Source four pillars do not match actual clock facts')
        if raw['chart'].get('solarTerm')!=term:
            raise ValueError('Source term changed unexpectedly')
        from src.wengua.casting_shenqi import layout_from_explicit_bureau,xun_shou
        old=layout_from_explicit_bureau(dun=old_bureau['dun'],ju=old_bureau['ju'],hour_ganzhi=pillars['hour'])
        audit['reference_differences']=compare_old(q,pillars,old_bureau,old)
        # New physical board is the ONLY physical input. Shared hour xun facts
        # are calculated independently from the true real hour ganzhi, not
        # copied from old board; old board remains comparison evidence only.
        xun,elapsed,hidden=xun_shou(pillars['hour'])
        physical={'source_key':'perfhelf/bigfishmarquis-qimen@'+BIGFISH_SHA,'school_id':'shijia_zhuanpan',
                  'casting_variant':'bigfish_shijia_chaibu_pilot',
                  'status':'bigfish_unapproved_candidate',
                  'dun':q['dun'],'ju':q['ju'],'hour_ganzhi':pillars['hour'],
                  'xun_shou':xun,'hidden_stem':hidden,
                  'value_star':q['value_star'],'value_star_palace':q['value_star_palace'],
                  'value_door':q['value_door'],'value_door_palace':q['value_door_palace'],
                  'palaces':q['palaces']}
        # Preserves V8 code exactly, routes the NEW physical board through it.
        from src.wengua.health_severity_vnext_review import analyze_health_severity_review
        from src.wengua.health_text_pipeline import DEFAULT_DB
        cal={'year_ganzhi':pillars['year'],'month_ganzhi':pillars['month'],
             'day_ganzhi':pillars['day'],'hour_ganzhi':pillars['hour'],
             'month_branch':pillars['month'][1]}
        inquiry={'intent':'severity','relationship':actor,'consultation_context':'direct_proxy'}
        from candidate_source_gate import bigfish_candidate_only
        with bigfish_candidate_only(physical):
            reading=analyze_health_severity_review(chart=physical,inquiry=inquiry,
                                                    calendar=cal,db_path=DEFAULT_DB)
        quant=reading['full_health_role_strength_network']['candidate_five_grade_quantization']
        score=quant['summary']['score']
        if score not in GRADE:
            raise ValueError('Frozen V8 grade is outside explicit -5..+5; reject')
        text=reading['reading_text']
        if not text or not reading['sections']:
            raise ValueError('Frozen customer template produced no text')
        # No old-engine reading or user outcome is allowed as input.
        (dir_/'reading_CANDIDATE.txt').write_text(text+'\n',encoding='utf-8')
        write_json(dir_/'candidate_result.json',{
            'stage':'new_engine_unapproved_candidate',
            'source_board_digest':digest(canonical(q).encode()),
            'grade':GRADE[score],'score_internal':score,
            'text':text,'sections':reading['sections'],
            'immutable_customer_template':'V10.2',
            'immutable_health_scoring':'V8.0',
            'approved_for_app':False})
        audit['status']='candidate_with_differences' if audit['reference_differences'] else 'candidate_matching_legacy_board'
        audit['score_internal']=score
        audit['text_sha256']=digest(text.encode('utf-8'))
        if not audit['reference_differences']:
            from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
            ref=auto_cast_health_review_text(iso=iso,timezone_name=zone,inquiry=inquiry)
            audit['frozen_customer_copy_exact_match']=text==ref['reading_text']
            if not audit['frozen_customer_copy_exact_match']:
                audit['status']='candidate_customer_copy_mismatch'
        # No automatic promotion: no independent original book/Native iOS check yet.
    except Exception as err:
        audit['status']='blocked'
        audit['error']=repr(err)
        audit['traceback']=traceback.format_exc(limit=8)
    write_json(dir_/'audit.json',audit)
    con.execute('INSERT OR REPLACE INTO records(case_id,instant,zone,actor,method,status,notes) VALUES(?,?,?,?,?,?,?)',
                (id_,iso,zone,actor,method,audit['status'],audit.get('error','') or str(len(audit.get('reference_differences',[])))+' reference differences'))
    con.commit()
    if own:con.close()
    return {k:audit.get(k) for k in ('case_id','status','instant','actor','method','error','score_internal','text_sha256')}


def batch(a):
    con=database()
    zone=ZoneInfo(a.timezone)
    actors=[x.strip() for x in a.actors.split(',') if x.strip()]
    if not actors or any(x not in ACTORS for x in actors):raise ValueError('Unknown actor')
    start=dt.date.fromisoformat(a.start_date)
    n=0;skipped=0;counts={}
    for day in range(a.days):
        date=start+dt.timedelta(days=day)
        for hour in range(0,23,2):
            local=dt.datetime(date.year,date.month,date.day,hour,30,tzinfo=zone)
            if local.astimezone(dt.timezone.utc).astimezone(zone).replace(fold=local.fold)!=local:
                skipped+=len(actors);continue
            for actor in actors:
                id_=digest(canonical([BIGFISH_SHA,WENGUA_SHA,local.isoformat(),a.timezone,actor,a.method]).encode())[:28]
                if not a.force and con.execute('SELECT 1 FROM records WHERE case_id=?',(id_,)).fetchone():
                    skipped+=1;continue
                if a.max_cases and n>=a.max_cases:
                    print('STOP max-cases reached; rerun identical command to resume');con.close();return
                row=process(local.isoformat(),a.timezone,actor,a.method,force=a.force,db=con)
                counts[row['status']]=counts.get(row['status'],0)+1
                n+=1
                if n % a.report_every==0:print('PROGRESS',n,canonical(counts),flush=True)
    print('DONE new=',n,'skipped=',skipped,canonical(counts))
    con.close()


def main(argv=None):
    p=argparse.ArgumentParser(description='BigFish real shijia TS chart -> frozen Wengua V8/V10.2 (Mac offline)')
    s=p.add_subparsers(dest='command',required=True)
    s.add_parser('verify');s.add_parser('status')
    one=s.add_parser('one')
    one.add_argument('--iso',required=True);one.add_argument('--timezone',default='America/New_York')
    one.add_argument('--relationship',default='father');one.add_argument('--method',choices=METHODS,default='chaibu')
    one.add_argument('--force',action='store_true')
    run=s.add_parser('run')
    run.add_argument('--start-date',required=True);run.add_argument('--days',type=int,default=1)
    run.add_argument('--timezone',default='America/New_York');run.add_argument('--actors',default='father,mother,grandfather,grandmother')
    run.add_argument('--method',choices=METHODS,default='chaibu');run.add_argument('--max-cases',type=int,default=24)
    run.add_argument('--report-every',type=int,default=12);run.add_argument('--force',action='store_true')
    a=p.parse_args(argv)
    if a.command=='verify':
        print('Verified:',canonical(check_install()));return 0
    if a.command=='status':
        con=database()
        print('Counts:',con.execute('SELECT status,COUNT(*) FROM records GROUP BY status').fetchall())
        print('Recent:',con.execute('SELECT instant,actor,method,status,notes FROM records ORDER BY rowid DESC LIMIT 10').fetchall())
        con.close();return 0
    if a.command=='one':
        result=process(a.iso,a.timezone,a.relationship,a.method,force=a.force)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status'].startswith('candidate_') or result['status']=='already_recorded' else 2
    if a.days<=0 or a.report_every<=0:raise ValueError('Days and report interval must be positive')
    batch(a);return 0


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as error:
        print('ERROR:',repr(error),file=sys.stderr)
        sys.exit(1)
