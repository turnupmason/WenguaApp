"""Independent supplied-case witnesses, chronology, convergence and daily copy."""
import copy,hashlib,json,unittest
from pathlib import Path
from src.wengua.health_recovery_v4 import *
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from tests.test_health_recovery_runtime_v3_20261103 import synthetic_role
ROOT=Path(__file__).resolve().parents[1]

class FivePathSourceWitness(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.q={'intent':'severity','relationship':'father','consultation_context':'direct_proxy','patient_birth_ganzhi':'癸酉'}
  cls.a=auto_cast_health_review_text(iso='2009-07-18T09:45:00+08:00',timezone_name='Asia/Shanghai',inquiry=cls.q)
  cls.f=facts_from_assessment(cls.a,cls.q);cls.c=context_from_assessment(cls.a,cls.f)
  cls.result=source_five_path_replay(cls.f,cls.c)
 def test_real_chart_matches_all_independent_source_roles_and_hosted_stem(self):
  self.assertEqual(self.a['four_pillars'],{'year':'己丑','month':'辛未','day':'甲子','hour':'己巳'})
  self.assertEqual(self.a['bureau']['ju'],8);self.assertEqual(self.a['bureau']['dun'],'yin')
  self.assertEqual(self.c['illness_palace'],3)
  self.assertEqual((self.c['executor']['name'],self.c['executor']['palace']),('生门',3))
  self.assertEqual(self.c['executor']['sky_stems'],['丁','辛'])
  self.assertEqual(self.c['executor']['sky_sources'],['天芮星','天禽星'])
  self.assertEqual((self.c['natal']['palace'],self.c['natal']['earth_stem']),(6,'庚'))
  self.assertEqual(self.c['year']['palace'],4)
 def test_five_routes_converge_without_reported_date_as_input(self):
  x=self.result
  self.assertEqual(x['month_branch'],'申');self.assertEqual(x['month_evidence']['palace_stage'],'死')
  self.assertEqual(x['month_evidence']['illness_star_stage'],'旺')
  self.assertEqual(x['duration_days'],[30,38]);self.assertTrue(x['duration_is_case_specific'])
  self.assertEqual(x['executor_month_stage'],'旺');self.assertEqual(x['case_numbers'],[3,8])
  self.assertEqual(x['natal_hidden_branch'],'寅');self.assertEqual(x['natal_palace_join'],['亥'])
  self.assertEqual(x['year_clash_palace_branches'],['辰']);self.assertTrue(x['year_half_join'])
  self.assertEqual(x['natal_tomb_branch'],'未');self.assertEqual(x['day_branch'],'丑')
  self.assertEqual(x['computed_dates'],[{'date':'2009-08-24','ganzhi':'辛丑','elapsed_days':37}])
  self.assertFalse(x['original_exact_date_prediction_made'])
 def test_half_join_is_not_full_join_and_wrong_branch_does_not_match(self):
  self.assertTrue(half_join('申','辰'));self.assertFalse(half_join('申','午'));self.assertFalse(half_join('辰','辰'))
  bad=copy.deepcopy(self.c);bad['year']['palace']=1
  with self.assertRaises(ValueError):source_five_path_replay(self.f,bad)
 def test_external_palace_join_is_not_cancelled_by_sky_earth_clash(self):
  role=synthetic_role(id='natal',palace=6,carrier='癸',earth='庚')
  m=scoped_method(role,self.f)
  self.assertEqual(m['branches'],['申']);self.assertEqual(m['status'],'selected');self.assertIn('U003',m['rule_ids'])
 def test_corrected_birth_cannot_be_retroactively_claimed_as_initial_input(self):
  q={**self.q,'patient_birth_ganzhi':'甲戌'}
  a=auto_cast_health_review_text(iso=self.f['reference_iso'],timezone_name=self.f['timezone'],inquiry=q)
  f=facts_from_assessment(a,q);ctx=context_from_assessment(a,f)
  self.assertEqual(ctx['natal']['carrier'],'己');self.assertEqual(ctx['natal']['palace'],4)
  self.assertNotEqual(ctx['natal'],self.c['natal'])
  with self.assertRaises(ValueError):source_five_path_replay(f,ctx)
 def test_source_death_date_never_appears_as_recovery_forecast(self):
  x=analyze_recovery_v4(self.f,self.c)
  self.assertEqual(x['status'],'recovery_not_established');self.assertIsNone(x['selected_day'])
  text='\n'.join(s['text'] for s in x['sections'])
  self.assertNotIn('8月24日',text);self.assertIn('不利变化',text)
 def test_outcome_cannot_be_passed_into_replay_or_live_selector(self):
  f=copy.deepcopy(self.f);f['actual_recovery_date']='2009-08-24'
  for fn in (source_five_path_replay,analyze_recovery_v4):
   with self.assertRaises(ValueError):fn(f,self.c)

class RecoveryDayPresentation(unittest.TestCase):
 def run_clock(self,iso):return auto_cast_health_recovery_v4(iso=iso,timezone_name='America/New_York',inquiry={'intent':'recovery','relationship':'self','consultation_context':'direct_self'})
 def test_actual_original_random_cast_yields_sourced_release_day(self):
  r=self.run_clock('2026-11-10T04:00:00-05:00')
  self.assertEqual(r['status'],'release_day');self.assertEqual(r['selected_day']['ganzhi'],'癸亥')
  self.assertEqual(r['selected_day']['start_iso'][:10],'2026-12-15')
  self.assertIn('2026年12月15日',r['sections'][0]['text']);self.assertIn('亥日',r['sections'][2]['text'])
  self.assertIn('未见墓',r['sections'][2]['text']);self.assertEqual(r['methods'][0]['method'],'punishment')
  table=source_full12()
  self.assertEqual([table['甲']['branch_to_stage'][b] for b in ('辰','巳')],['衰','病'])
  self.assertEqual([table['癸']['branch_to_stage'][b] for b in ('辰','巳')],['养','胎'])
 def test_executor_stem_refines_branch_to_a_single_real_day(self):
  r=self.run_clock('2026-10-27T05:00:00-04:00')
  self.assertEqual(r['selected_day']['ganzhi'],'辛卯');self.assertTrue(r['selected_day']['executor_stem_matched'])
  text=r['reading_text']
  for unwanted in ['America','timezone','按日看','按月看','时间单位尚未明确','T00:00']:
   self.assertNotIn(unwanted,text)
  self.assertIn('2026年11月13日',text)
 def test_no_automatic_30_38_days_on_other_palaces_or_events(self):
  r=self.run_clock('2026-10-27T05:00:00-04:00')
  self.assertNotIn('30～38',r['reading_text']);self.assertNotIn('30~38',r['reading_text'])
 def test_opposing_patient_control_does_not_become_an_unconditional_cure(self):
  r=self.run_clock('2026-10-27T05:00:00-04:00');f=copy.deepcopy(r['facts'])
  f['controls'].append({'role':'patient','direction':'被克','attacker':'illness','eligible':True,'cell':'绝对主克'})
  x=analyze_recovery_v4(f,r['context'])
  self.assertEqual(x['status'],'release_day');self.assertIn('病宫仍对患者',x['sections'][2]['text'])
 def test_all_existing_frozen_mathematics_and_seven_resources_stay_exact(self):
  manifest=json.loads((ROOT/'archives/engineering_patch_20261103/before_recovery_v4/data/releases/health_frozen_20261102.json').read_text())
  changed={'ios/WenguaAppUI/WenguaNativeReadingRouter.swift','ios/WenguaAppUI/WenguaPremiumReadingView.swift','ios/WenguaAppUI/project.yml'}
  for row in manifest['files']:
   if row['path'] not in changed:self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'],row['path'])

if __name__=='__main__':unittest.main()
