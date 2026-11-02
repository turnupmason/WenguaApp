"""Preserve source, contextual exceptions and a fixed recovery-only template."""
import copy
import hashlib
import json
from pathlib import Path
import string
import tempfile
import unittest
from unittest.mock import patch
from src.wengua import user_timing_notes_20261102 as notes
from scripts.render_user_timing_material_20261102 import outputs,generated_part

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/knowledge/timing_methods/user_notes_20261102'
HEALTH=ROOT/'data/knowledge/health_recovery'

class TimingSourceRecords(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.bundle=notes.load_bundle()
  cls.rules={r['id']:r for r in cls.bundle['rules.json']['rules']}

 def test_entire_124_line_receipt_including_final_repeated_material(self):
  m=self.bundle['manifest'];units=self.bundle['source_units.json']['units']
  self.assertEqual(m['source_sha256'],'db098ffb881fb1665b05a712ca634974c1365e0e40462b899a986d0dfe546fb5')
  self.assertEqual((m['utf8_bytes'],m['unicode_characters'],m['source_lines']),(30306,10294,124))
  self.assertEqual((len(self.rules),m['illustrations'],m['domain_contracts']),(92,29,12))
  self.assertEqual({u['line'] for u in units},set(range(1,125)))
  self.assertEqual(units[-1]['line_end'],10294)
  self.assertTrue(all(u['rule_ids'] or u['kind']=='heading' for u in units))
  self.assertTrue(all(units[n-1]['rule_ids'] for n in range(119,125)))
  self.assertFalse(m['original_in_public_git'])
  self.assertEqual(m['new_book_chapters'],0)
  self.assertEqual(m['new_complete_historical_cases'],0)

 def test_17_existing_book_method_links_do_not_rewrite_original_book_text(self):
  source=json.loads((ROOT/'data/knowledge/kaiwu/analysis_judgment_ch04/timing_methods.json').read_text())['methods']
  by={r['method_key']:r for r in source}
  refs={r['existing_book_method_ref'] for r in self.rules.values() if r['existing_book_method_ref']}
  self.assertEqual(len(refs),17)
  self.assertTrue(refs<=set(by))
  self.assertTrue(all(r['runtime_enabled'] is False and r['review_status']=='draft' for r in self.rules.values()))
  self.assertEqual(self.bundle['rules.json']['provenance'],'user_supplied_notes_not_verified_original_book_quotation')

 def test_source_specific_differences_are_not_replaced_with_one_global_answer(self):
  c={x['id']:x for x in self.bundle['exceptions_and_duplicates.json']['conflicts']}
  self.assertEqual(len(c),9)
  self.assertTrue({'T064','T084','T085'}<=set(c['C02']['related_rule_ids']))
  self.assertTrue({'T066','T084'}<=set(c['C03']['related_rule_ids']))
  self.assertTrue({'T031','T039','T051','T055','T086'}<=set(c['C01']['related_rule_ids']))
  self.assertTrue(all(x['auto_resolved'] is False for x in c.values()))
  self.assertFalse(self.bundle['method_tracks.json']['total_order_verified_for_all_coexisting_symbols'])

 def test_duplicate_and_ocr_categories_keep_raw_text_separate(self):
  q=self.bundle['exceptions_and_duplicates.json']
  self.assertEqual(len(q['duplicate_groups']),5)
  self.assertEqual(len(q['normalization_candidates']),8)
  for row in q['normalization_candidates']:
   self.assertFalse(row['apply_globally'])
   self.assertEqual(row['review_status'],'candidate_not_applied_to_original')
  self.assertEqual({x['kind'] for x in q['duplicate_groups']},
   {'exact_duplicate','near_duplicate_with_wrap','repeated_fragment','later_expansion_of_truncated_sentence'})

 def test_examples_separate_context_forecast_and_report_without_invented_charts(self):
  examples=self.bundle['illustrations.json']['illustrations']
  self.assertEqual(sum(x['kind']=='reported_anecdote' for x in examples),2)
  for x in examples:
   self.assertTrue(x['known_context'])
   self.assertTrue(x['source_forecast_or_illustration'])
   self.assertFalse(x['complete_chart_available'])
   self.assertFalse(x['calendar_recomputed'])
   self.assertFalse(x['independent_accuracy_sample'])
   self.assertFalse(x['added_to_historical_case_database'])
  self.assertIsNotNone(next(x for x in examples if x['id']=='E04')['reported_result'])
  self.assertIsNone(next(x for x in examples if x['id']=='E08')['reported_result'])

 def test_hash_tampering_is_rejected_before_eligibility(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp)
   for p in BASE.glob('*.json'):(folder/p.name).write_bytes(p.read_bytes())
   p=folder/'rules.json';p.write_bytes(p.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'hash changed'):notes.load_bundle(folder)

class TimingConditionSemantics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rules={r['id']:r for r in notes.load_bundle()['rules.json']['rules']}
 def test_unknown_is_not_negative_and_booleans_do_not_equal_integers(self):
  eq={'field':'void','eq':False}
  self.assertIsNone(notes.evaluate_condition(eq,{}))
  self.assertIsNone(notes.evaluate_condition(eq,{'void':None}))
  self.assertTrue(notes.evaluate_condition(eq,{'void':False}))
  self.assertFalse(notes.evaluate_condition(eq,{'void':0}))
  self.assertIsNone(notes.evaluate_condition({'not':eq},{}))
  self.assertFalse(notes.evaluate_condition({'all':[eq,{'field':'horse','eq':True}]},{'void':True}))
  self.assertTrue(notes.evaluate_condition({'any':[eq,{'field':'horse','eq':True}]},{'horse':True}))
  with self.assertRaises(ValueError):notes.evaluate_condition({'all':[]},{})
  with self.assertRaises(ValueError):notes.evaluate_condition({'eval':'unsafe'},{})
 def test_empty_status_cannot_be_silently_bypassed_to_horse_or_tomb(self):
  horse=self.rules['T056']['conditions']
  self.assertIsNone(notes.evaluate_condition(horse,{'moving_horse':True}))
  self.assertTrue(notes.evaluate_condition(horse,{'void':False,'moving_horse':True}))
  self.assertFalse(notes.evaluate_condition(horse,{'void':True,'moving_horse':True}))
  tomb=self.rules['T057']['conditions']
  self.assertIsNone(notes.evaluate_condition(tomb,{'void':False,'tomb_or_store':True}))
  self.assertTrue(notes.evaluate_condition(tomb,{'void':False,'moving_horse':False,'tomb_or_store':True}))
 def test_ordinary_and_chief_role_scopes_remain_distinct(self):
  ordinary=self.rules['T064']['conditions'];chief=self.rules['T084']['conditions']
  facts={'jia_carrier':'戊','role_palace':3,'chief_required':False,'chief_clash':True}
  self.assertTrue(notes.evaluate_condition(ordinary,facts))
  self.assertFalse(notes.evaluate_condition(chief,facts))
  facts['chief_required']=True
  self.assertFalse(notes.evaluate_condition(ordinary,facts))
  self.assertTrue(notes.evaluate_condition(chief,facts))
 def test_coexisting_clash_and_join_are_not_auto_resolved(self):
  facts={'void':False,'moving_horse':False,'tomb_or_store':False,'punishment_or_clash':True,'combination':True}
  self.assertTrue(notes.evaluate_condition(self.rules['T060']['conditions'],facts))
  self.assertTrue(notes.evaluate_condition(self.rules['T074']['conditions'],facts))
  self.assertIn('C09',self.rules['T074']['exceptions'])
 def test_geng_track_and_success_failure_gates_do_not_cross_domains(self):
  f={'direct_geng_pattern':False,'timing_role':'day','day_polarity':'yin','geng_track_applicable':False}
  self.assertFalse(notes.evaluate_condition(self.rules['T045']['conditions'],f))
  f['geng_track_applicable']=True
  self.assertTrue(notes.evaluate_condition(self.rules['T045']['conditions'],f))
  f={'outcome_classified':True,'event_class':'failure','void':True}
  self.assertFalse(notes.evaluate_condition(self.rules['T031']['conditions'],f))
  self.assertTrue(notes.evaluate_condition(self.rules['T039']['conditions'],f))
  for key in notes.FORBIDDEN_FACTS:
   with self.assertRaises(ValueError):notes.evaluate_condition({'const':True},{key:'posterior'})

class PrivateTimingSourceArchive(unittest.TestCase):
 def fixture(self,raw):
  text=raw.decode('utf8');units=[];cursor=0
  for line in text.splitlines(keepends=True):
   plain=line.rstrip('\r\n');units.append({'char_start':cursor,'char_end':cursor+len(plain),'text_sha256':notes.sha256(plain.encode())});cursor+=len(line)
  return {'manifest':{'source_id':'synthetic_unit_test_only','source_sha256':notes.sha256(raw),'utf8_bytes':len(raw),'unicode_characters':len(text),'source_lines':len(units)},'source_units.json':{'units':units}}
 def test_private_copy_is_exact_reopened_and_idempotent(self):
  raw='合冲😀原字\r\n第二行末'.encode()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);src=root/'input.txt';src.write_bytes(raw);dest=root/'archive'
   with patch.object(notes,'load_bundle',return_value=self.fixture(raw)):
    a=notes.archive_original(src,dest);b=notes.archive_original(src,dest)
   self.assertEqual(a,b);self.assertEqual((dest/'original.txt').read_bytes(),raw)
   self.assertIn('001 合冲😀原字',(dest/'numbered_reading.txt').read_text())
   self.assertFalse(a['normalization_applied_to_original'])
 def test_bad_source_or_different_prior_backup_cannot_overwrite(self):
  raw='原始资料\n'.encode()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);src=root/'input.txt';src.write_bytes(raw+b'changed');dest=root/'archive'
   with patch.object(notes,'load_bundle',return_value=self.fixture(raw)):
    with self.assertRaises(ValueError):notes.archive_original(src,dest)
    self.assertFalse(dest.exists())
    src.write_bytes(raw);dest.mkdir();(dest/'original.txt').write_bytes(b'old source')
    with self.assertRaises(ValueError):notes.archive_original(src,dest)
    self.assertEqual((dest/'original.txt').read_bytes(),b'old source')
    self.assertFalse((dest/'numbered_reading.txt').exists())

class RecoveryV2Scope(unittest.TestCase):
 def test_fixed_recovery_goal_reuses_existing_severity_and_location(self):
  active=json.loads((HEALTH/'active_draft.json').read_text());p=HEALTH/active['active_draft']
  self.assertEqual(notes.sha256(p.read_bytes()),active['template_sha256'])
  t=json.loads(p.read_text())
  self.assertEqual(t['target'],{'id':'recovery','question':'病什么时候好','fixed':True,'requires_goal_picker':False})
  self.assertEqual([s['title'] for s in t['sections']],['病愈时间','应期缓急','取期依据','综合断语'])
  self.assertFalse(t['scope']['recalculate_severity']);self.assertFalse(t['scope']['recalculate_body_location'])
  self.assertFalse(t['release_contract']['app_enabled'])
  self.assertNotIn('needs_target',t['time_states'])
  self.assertNotIn('targets',t)
  self.assertTrue((HEALTH/'reading_template_v1_draft.json').exists())
 def test_fields_and_source_references_are_complete_without_fake_patient_dates(self):
  t=json.loads((HEALTH/'reading_template_v2_user_timing.json').read_text())
  rules={r['id'] for r in notes.load_bundle()['rules.json']['rules']}
  self.assertEqual(set(t['time_states']),set(t['summary_states']))
  for s in t['sections']:
   self.assertTrue(set(s.get('source_rule_ids',[]))<=rules)
   lists=t[s['branch']].values() if 'branch' in s else [[p['text'] for p in s['paragraphs']]]
   for rows in lists:
    for paragraph in rows:
     fields={x for _,x,_,_ in string.Formatter().parse(paragraph) if x}
     self.assertTrue(fields<=set(t['fields']))
  for state in set(t['time_states'])-{'dated_window','bounded_relative_window'}:
   self.assertNotIn('{window_label}',''.join(t['time_states'][state]+t['summary_states'][state]))
  self.assertEqual(t['window_contract']['current_calendar_producer'],['day','month'])
  project=(ROOT/'ios/WenguaAppUI/project.yml').read_text()
  self.assertNotIn('reading_template_v2_user_timing.json',project)
 def test_generated_reading_and_summary_match_canonical_records(self):
  for path,text in outputs().items():
   self.assertEqual(generated_part(path.read_text()),generated_part(text))
  manifest=json.loads((ROOT/'data/releases/health_frozen_20261102.json').read_text())
  for entry in manifest['files']:
   self.assertEqual(notes.sha256((ROOT/entry['path']).read_bytes()),entry['sha256'])
