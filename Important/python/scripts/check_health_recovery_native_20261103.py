"""Compare independently executed native facts, methods, periods and all words."""
import argparse,json,subprocess,random,copy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from src.wengua.health_recovery_v3 import auto_cast_health_recovery_text,analyze_recovery

ROOT=Path(__file__).resolve().parents[1]

def normalize(x):
    if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if v is not None}
    if isinstance(x,list):return [normalize(v) for v in x]
    return x


def generate(folder):
    folder.mkdir(parents=True,exist_ok=True)
    seed=20261103;rng=random.Random(seed);cases=[];expected=[];rejected=[]
    clocks=[('2026-11-10T04:00:00-05:00','self','本人','America/New_York'),
            ('2026-11-10T04:00:00-05:00','father','父亲','America/New_York'),
            ('2026-03-08T01:00:00-05:00','self','本人','America/New_York'),
            ('2026-11-01T03:00:00-05:00','self','本人','America/New_York'),
            ('2026-11-10T17:00:00+08:00','friend','朋友','Asia/Shanghai'),
            ('2027-02-04T09:00:00+00:00','self','本人','Etc/UTC')]
    for i in range(24):
        d=datetime(2026,rng.randrange(1,13),rng.randrange(1,29),rng.choice([1,3,5,7,9,11,13,15,17,19,21]),tzinfo=ZoneInfo('America/New_York'))
        rel,label=[('self','本人'),('father','父亲'),('friend','朋友'),('wife','妻子')][i%4]
        clocks.append((d.isoformat(),rel,label,'America/New_York'))
    # Genuine role-specific Jia sources, not replacement of random draws.
    clocks.extend([('2024-05-28T13:00:00-04:00','father','父亲','America/New_York'),
                   ('2026-10-27T05:00:00-04:00','self','本人','America/New_York'),
                   ('2026-06-21T17:00:00-04:00','self','本人','America/New_York'),
                   ('2026-10-10T09:00:00-04:00','self','本人','America/New_York')])
    for draw,(iso,rel,label,zone) in enumerate(clocks):
        inquiry={'intent':'recovery','relationship':rel,'consultation_context':'direct_self' if rel=='self' else 'direct_proxy'}
        if rel=='wife':inquiry['patient_sex']='female'
        elif rel=='friend':inquiry['patient_sex']='male'
        try:result=auto_cast_health_recovery_text(iso=iso,timezone_name=zone,inquiry=inquiry)
        except (ValueError,LookupError,KeyError) as e:
            rejected.append({'draw':draw,'iso':iso,'relationship':rel,'reason':str(e)});continue
        case={'id':f'live_{draw:02d}','iso':iso,'timezone':zone,'relationship':label,'context':inquiry['consultation_context'],'patient_sex':inquiry.get('patient_sex')}
        cases.append(case);expected.append({'id':case['id'],'facts':result.pop('facts'),'result':result})
    # Explicit units test actual successful chart, not input guesses in App.
    for scale in ('hour','day','month','year'):
        iso='2026-10-10T09:00:00-04:00' if scale=='hour' else '2026-10-27T05:00:00-04:00'
        result=auto_cast_health_recovery_text(iso=iso,timezone_name='America/New_York',inquiry={'intent':'recovery','relationship':'self','consultation_context':'direct_self'},time_scale=scale)
        case={'id':'explicit_'+scale,'iso':iso,'timezone':'America/New_York','relationship':'本人','time_scale':scale}
        cases.append(case);expected.append({'id':case['id'],'facts':result.pop('facts'),'result':result})
    # Synthetic contracts exercise source branches, never counted as real
    # charts, historical cases, medical evidence or random date successes.
    from tests.test_health_recovery_runtime_v3_20261103 import synthetic_role
    base=copy.deepcopy(expected[0]['facts'])
    synthetic=[('void',synthetic_role(void='true_void',vb=['卯'])),
        ('horse',synthetic_role(horse='寅',tombs=['辰'])),
        ('tomb',synthetic_role(tombs=['辰'])),
        ('ordinary_punishment',synthetic_role(palace=3,carrier='戊',earth='乙')),
        ('chief_punishment',synthetic_role(id='chief',palace=3,carrier='戊',earth='乙')),
        ('ordinary_geng_gen',synthetic_role(palace=8,carrier='庚',earth='丙')),
        ('chief_geng_gen',synthetic_role(id='chief',palace=8,carrier='庚',earth='丙')),
        ('self_punishment',synthetic_role(palace=7,carrier='辛',earth='辛')),
        ('hidden_join',synthetic_role(palace=8,carrier='戊',earth='丙')),
        ('mixed_conflict',synthetic_role(palace=9,carrier='戊',earth='癸')),
        ('stem_branch',synthetic_role(palace=2,carrier='辛',earth='戊')),
        ('fuyin',synthetic_role()),('fanyin',synthetic_role()),('growth',synthetic_role())]
    for name,role in synthetic:
        f=copy.deepcopy(base)
        f['reference_iso']='2026-10-10T09:00:00-04:00'
        f['fuyin']=name=='fuyin';f['fanyin']=name=='fanyin'
        f['roles']=[synthetic_role(id='illness',palace=2),synthetic_role(id='hour',palace=4)]
        if role['id']!='patient':f['roles'].append(synthetic_role())
        f['roles'].append(role)
        f['controls']=[{'role':role['id'],'direction':'克','cell':'有效克制','eligible':True,'attacker':role['id']}]
        result=analyze_recovery(f,time_scale='day')
        case={'id':'synthetic_'+name,'kind':'synthetic_unit_only_not_real_chart','facts':f,'time_scale':'day'}
        cases.append(case);expected.append({'id':case['id'],'facts':f,'result':result})
    (folder/'input.json').write_text(json.dumps({'seed':seed,'selection':'all accepted fixed and sequential seeded clocks; no score/outcome filtering','rejected':rejected,'cases':cases},ensure_ascii=False,indent=2)+'\n')
    (folder/'expected.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2)+'\n')
    return cases,expected


def compare(folder,native):
    cases,expected=generate(folder)
    args=[str(native),str(ROOT/'data/knowledge/health_recovery/runtime_v3_20261102.json'),str(ROOT/'data/mobile/health_vnext/health_energy_200.json'),str(ROOT/'data/knowledge/phrase_library/health_v20/actor_profiles.json'),str(ROOT/'data/knowledge/health_81_excel_20261025/81_pairs.tsv'),str(folder/'input.json')]
    run=subprocess.run(args,text=True,capture_output=True)
    (folder/'native.jsonl').write_text(run.stdout);(folder/'native.stderr').write_text(run.stderr)
    if run.returncode:raise RuntimeError(f'Native recovery failed ({run.returncode}): {run.stderr[:2500]}')
    actual=[json.loads(line) for line in run.stdout.splitlines() if line.strip()]
    assert len(actual)==len(expected),(len(actual),len(expected))
    keys=['status','sections','windows','methods','alternative_windows','support','counterevidence','calendar_search']
    errors=[]
    def equal(a,b,label):
        if normalize(a)!=normalize(b):
            errors.append({'case_field':label,'actual':a,'expected':b})
    for a,e in zip(actual,expected):
        assert a['id']==e['id']
        # Role and control maps are unordered internally; their facts must be
        # independently identical before comparing the timing interpretation.
        for key in ['roles','controls']:
            aa=sorted(a['facts'][key],key=lambda v:v['id'] if key=='roles' else v['role'])
            ee=sorted(e['facts'][key],key=lambda v:v['id'] if key=='roles' else v['role'])
            equal(aa,ee,[a['id'],'facts',key])
        for key in ('reference_iso','timezone','pillars','dun','fuyin','fanyin'):
            equal(a['facts'][key],e['facts'][key],[a['id'],'facts',key])
        for key in keys:
            equal(a['result'][key],e['result'][key],[a['id'],key])
    (folder/'differences.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2)+'\n')
    for err in errors:print('RECOVERY_MISMATCH',json.dumps(err,ensure_ascii=False)[:4500])
    assert not errors, f'{len(errors)} recovery native differences; all cases compared, see differences.json'
    statuses={e['result']['status'] for e in expected}
    assert any(e['result']['windows'] for e in expected), 'No dated execution exercised'
    assert 'recovery_premise_unresolved' in statuses
    receipt={'cases':len(actual),'status':'passed','actual_native_executed':True,'real_chart_cases':sum(not c['id'].startswith('synthetic_') for c in cases),'synthetic_contract_cases':sum(c['id'].startswith('synthetic_') for c in cases),'comparison':keys,'same_clock_and_patient_facts_independently_compared':True,'statuses':sorted(statuses),'medical_validation':False}
    (folder/'parity_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('RECOVERY_PYTHON_SWIFT_PARITY_PASS',len(actual),'cases; complete facts, windows and all four sections')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.native:compare(args.output.resolve(),args.native.resolve())
    else:generate(args.output.resolve());print('Recovery fixtures generated')
