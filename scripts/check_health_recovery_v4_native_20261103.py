"""Source-witness replay plus current recovery route: independent native execution."""
import json,argparse,subprocess
from pathlib import Path
from scripts.check_health_recovery_native_20261103 import generate as v3_inputs,normalize
from src.wengua.health_recovery_v4 import *
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
ROOT=Path(__file__).resolve().parents[1]

def generate(folder):
 folder.mkdir(parents=True,exist_ok=True);old,_=v3_inputs(folder/'legacy_inputs')
 cases=[{k:v for k,v in c.items() if k in ('id','iso','timezone','relationship','context','patient_sex')} for c in old if c.get('iso')]
 cases.extend([{'id':'user_source_corrected_birth','iso':'2009-07-18T09:45:00+08:00','timezone':'Asia/Shanghai','relationship':'父亲','context':'direct_proxy','patient_birth_ganzhi':'癸酉','source_replay':True},
 {'id':'user_source_original_birth','iso':'2009-07-18T09:45:00+08:00','timezone':'Asia/Shanghai','relationship':'父亲','context':'direct_proxy','patient_birth_ganzhi':'甲戌'}])
 for c in cases:c.setdefault('context','direct_self' if c['relationship']=='本人' else 'direct_proxy')
 expected=[];labels={'本人':'self','父亲':'father','朋友':'friend','妻子':'wife'}
 for c in cases:
  q={'intent':'severity','relationship':labels[c['relationship']],'consultation_context':c.get('context','direct_self')}
  for k in ('patient_sex','patient_birth_ganzhi'):
   if c.get(k):q[k]=c[k]
  a=auto_cast_health_review_text(iso=c['iso'],timezone_name=c['timezone'],inquiry=q)
  f=facts_from_assessment(a,q);ctx=context_from_assessment(a,f);r=analyze_recovery_v4(f,ctx)
  e={'id':c['id'],'result':r}
  if c.get('source_replay'):e['replay']=source_five_path_replay(f,ctx)
  expected.append(e)
 (folder/'input.json').write_text(json.dumps({'cases':cases,'random_software_clocks_not_filtered_by_verdict':True,'source_case_selection':'user_supplied_known_adverse_case','source_replay_is_retrospective_not_blind_prediction':True},ensure_ascii=False,indent=2)+'\n')
 (folder/'expected.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2)+'\n')
 return cases,expected

def compare(folder,native,bundle=None):
 cases,expected=generate(folder)
 args=[str(native),str(DATA),str(ROOT/'data/knowledge/health_recovery/runtime_v3_20261102.json'),str(ROOT/'data/mobile/health_vnext/health_energy_200.json'),str(ROOT/'data/knowledge/phrase_library/health_v20/actor_profiles.json'),str(ROOT/'data/knowledge/health_81_excel_20261025/81_pairs.tsv'),str(folder/'input.json')]
 p=subprocess.run(args,text=True,capture_output=True);(folder/'native.jsonl').write_text(p.stdout);(folder/'native.stderr').write_text(p.stderr)
 if p.returncode:raise RuntimeError(p.stderr[-5000:])
 actual=[json.loads(x) for x in p.stdout.splitlines() if x.strip()]
 assert len(actual)==len(expected),(len(actual),len(expected))
 errors=[]
 for a,e in zip(actual,expected):
  if normalize(a)!=normalize(e):errors.append({'id':e['id'],'actual':a,'expected':e})
 (folder/'differences.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2)+'\n')
 for x in errors:print('V4_DIFFERENCE',json.dumps(x,ensure_ascii=False)[:11000])
 assert not errors,f'{len(errors)} V4 native differences'
 source=next(x['replay'] for x in actual if x['id']=='user_source_corrected_birth')
 assert source['computed_dates']==[{'date':'2009-08-24','ganzhi':'辛丑','elapsed_days':37}]
 if bundle:
  q=subprocess.run([str(native),'--bundle',str(bundle)],capture_output=True,text=True)
  (folder/'bundle.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr;print(q.stdout,end='')
 receipt={'status':'passed','cases':len(actual),'source_five_path_reconstruction':source,'new_cases_are_software_checks_not_clinical_validation':True}
 (folder/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
 print('RECOVERY_V4_PYTHON_SWIFT_PASS',len(actual),'cases; supplied five-path source independently converges to 37th day XinChou; recovery date-only copy matches')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--native',type=Path);p.add_argument('--bundle',type=Path);a=p.parse_args()
 if a.native:compare(a.output.resolve(),a.native.resolve(),a.bundle)
 else:generate(a.output.resolve())
