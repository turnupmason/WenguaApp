"""Draft template/source contracts; no claim of an implemented recovery selector."""
import hashlib,json,string,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/knowledge/health_recovery'
class RecoveryTemplateDraft(unittest.TestCase):
 def test_target_and_placeholder_states_are_complete_and_fail_closed(self):
  t=json.loads((BASE/'reading_template_v1_draft.json').read_text())
  self.assertEqual(t['topic_id'],'health.recovery')
  self.assertFalse(t['release_contract']['app_enabled'])
  self.assertFalse(t['release_contract']['disease_rule_selection_implemented'])
  self.assertEqual(len(t['sections']),6)
  self.assertEqual({x['id'] for x in t['targets']},{'improvement','symptom_relief','discharge','clinical_recovery'})
  self.assertEqual(set(t['window_state']),set(t['summary_state']))
  formatter=string.Formatter()
  for section in t['sections']:
   branches=[section['paragraphs']] if 'paragraphs' in section else t[section['branch']].values()
   for paragraphs in branches:
    for paragraph in paragraphs:
     fields={field for _,field,_,_ in formatter.parse(paragraph) if field}
     self.assertTrue(fields<=set(t['placeholders']))
     self.assertNotIn('{',paragraph.format(**{k:'【'+k+'】' for k in fields}))
  for state in set(t['window_state'])-{'conditional_window'}:
   self.assertNotIn('{window_human}', ''.join(t['window_state'][state]+t['summary_state'][state]))
  self.assertIn('actual_discharge_date',t['input_contract']['forbidden_prediction_inputs'])
  self.assertFalse(t['assembly_policy']['book_feedback_used_for_selection'])
 def test_source_anchors_and_case_specific_duration_are_not_promoted(self):
  a=json.loads((BASE/'source_review_v1.json').read_text())
  for source in a['source_files']:
   self.assertEqual(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest(),source['sha256'])
  methods={x['method_key']:x for x in json.loads((ROOT/'data/knowledge/kaiwu/analysis_judgment_ch04/timing_methods.json').read_text())['methods']}
  self.assertEqual(len(a['generic_candidates']),8)
  for candidate in a['generic_candidates']:
   source=methods[candidate['source_method_key']]
   self.assertEqual(candidate['source_line'],source['source_line'])
   self.assertEqual(candidate['excerpt_sha256'],hashlib.sha256(source['original_text'].encode()).hexdigest())
   self.assertFalse(candidate['live_rule_enabled'])
   self.assertEqual(candidate['disease_applicability'],'unverified')
  case=a['historical_timing_checks'][0]
  lines=(ROOT/case['source_path']).read_text().splitlines()
  self.assertEqual(hashlib.sha256(lines[case['forecast_line']-1].encode()).hexdigest(),case['forecast_line_sha256'])
  self.assertIn('十天半月',lines[case['forecast_line']-1])
  self.assertNotIn('出院',lines[case['feedback_lines'][0]-1])
  self.assertFalse(case['actual_discharge_date_reported'])
  self.assertFalse(case['can_promote_10_to_15_days_to_default'])
  self.assertIsNone(a['historical_timing_checks'][1]['inferred_original_timing_method'])
 def test_cross_book_families_deduplicate_without_rewriting_originals(self):
  paths=['data/knowledge/shenqi/health_prediction_ch01/case_index.json','data/knowledge/kaiwu/health_prediction_ch02_section01/case_index.json']
  ids=[x['id'] for p in paths for x in json.loads((ROOT/p).read_text())['cases']]
  a=json.loads((BASE/'source_review_v1.json').read_text())['case_inventory']
  self.assertEqual((len(ids),len(set(ids))),(12,11))
  self.assertEqual(a['source_entries'],len(ids))
  self.assertEqual(a['unique_event_families'],len(set(ids)))
 def test_only_requested_guidance_spacing_changes_in_sealed_app_sources(self):
  before=json.loads((ROOT/'archives/engineering_patch_20261102/before_p9/health_frozen_20261102.json').read_text())
  current=json.loads((ROOT/'archives/engineering_patch_20261102/before_recovery_v3/data/releases/health_frozen_20261102.json').read_text())
  old={x['path']:x['sha256'] for x in before['files']}
  self.assertEqual(before['topics'],current['topics'])
  self.assertEqual({x['path'] for x in current['files'] if old[x['path']]!=x['sha256']},{'ios/WenguaAppUI/WenguaSetupPresentation.swift'})
  for entry in current['files']:
   self.assertEqual(hashlib.sha256((ROOT/'archives/engineering_patch_20261102/before_recovery_v3'/entry['path']).read_bytes()).hexdigest() if (ROOT/'archives/engineering_patch_20261102/before_recovery_v3'/entry['path']).is_file() else hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest(),entry['sha256'])
  app=(ROOT/'ios/WenguaAppUI/WenguaSetupPresentation.swift').read_text().split('struct WenguaCivilClockWheel:')[0]
  self.assertEqual(app.count('spacing:guidanceGap'),2)
  self.assertIn('private let guidanceGap:CGFloat=16',app)
 def test_recovery_draft_is_not_packaged_as_approved_resource(self):
  project=(ROOT/'ios/WenguaAppUI/project.yml').read_text()
  self.assertNotIn('reading_template_v1_draft.json',project)
  self.assertNotIn('reading_template_v2_user_timing.json',project)
  self.assertIn('runtime_v3_20261102.json',project)
  t=json.loads((BASE/'reading_template_v1_draft.json').read_text())
  self.assertEqual(t['input_contract']['calendar_producer_supported_resolutions'],['day','month'])
  self.assertEqual(t['input_contract']['optional_duration_default'],'unknown')
  self.assertTrue(t['input_contract']['no_score_to_days_mapping'])
