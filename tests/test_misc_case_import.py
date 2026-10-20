"""Original book cases: one event may have many charts; no leaked retrospective result."""
import hashlib,importlib.util,json,sqlite3,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'sources/shenqi/神奇之门_第十七章_其他杂项预测_精校完整版(1).txt'
MOD=ROOT/'scripts/build_shenqi_21_from_20.py'
BASE=ROOT/'archives/sqlite/WenguaApp_神奇之门_20章_98案例_完整研究库.sqlite3'
ARCHIVE=ROOT/'archives/sqlite/WenguaApp_神奇之门_21章_103案例_完整研究库.sqlite3'
MANIFEST=ROOT/'archives/sqlite/21chapters_103cases_manifest.json'
class MiscHistoryRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('misc_archive_source',MOD)
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);cls.m=m
 def test_exact_original_charts_and_step_coverage(self):
  raw=FILE.read_bytes();lines=raw.decode('utf8').splitlines();m=self.m
  self.assertEqual((len(raw),len(lines),hashlib.sha256(raw).hexdigest()),(27639,280,m.SOURCE_SHA))
  cases=m.case_index(lines)
  self.assertEqual([len(x['source_casts']) for x in cases],[3,1,1,1,1])
  self.assertEqual([len(x['source_analysis_steps']) for x in cases],[12,3,4,6,2])
  self.assertEqual([z['source_chart_line'] for x in cases for z in x['source_casts']],[25,56,83,116,151,218,255])
  self.assertEqual(len(m.METHODS),23)
  self.assertEqual(len({x['event_family_id'] for x in cases}),5)
  for case in cases:
   for cast in case['source_casts']:
    cells=m.parse_chart(lines,cast['source_chart_line'])
    self.assertEqual(len(cells),9)
    middle=[x for x in cells if x[0]==5]
    self.assertEqual(len(middle),1)
    self.assertEqual((middle[0][3],middle[0][5]),('',''))
    self.assertTrue(middle[0][4] in '乙丙丁戊己庚辛壬癸')
   self.assertTrue(all(not s['positive_training_eligible'] for s in case['source_analysis_steps']))
 def test_multiple_method_provenance_and_feedback_gates(self):
  c=self.m.case_index(FILE.read_text('utf8').splitlines())
  self.assertTrue(c[0]['six_yao_claim_not_qimen_cast']['no_proof_contemporaneous_qimen_prediction'])
  self.assertEqual([x['key'] for x in c[0]['source_casts']],['primary','bid_1993_09_23','vote_1993_09_24'])
  self.assertTrue(c[1]['three_questions_one_event'])
  self.assertTrue(c[2]['interim_known_participants_at_line178'])
  self.assertEqual(c[3]['live_predictions_before_written_reconstruction']['initial_lines'],[196,200,204])
  self.assertEqual(c[3]['live_predictions_before_written_reconstruction']['explanation_after_revealed_feedback'],[237,241,245])
  self.assertEqual([s['phase'] for s in c[3]['source_analysis_steps'][:3]],['initial_live_prediction']*3)
  self.assertEqual([s['phase'] for s in c[3]['source_analysis_steps'][3:]],['post_feedback_explanatory_analysis']*3)
  self.assertEqual(c[4]['teacher_retrospective_commentary_line'],280)
 def test_archive_real_binary_preserves_all_previous_source(self):
  if not ARCHIVE.exists():self.skipTest('New immutable GitHub Action archive not created yet')
  manifest=json.loads(MANIFEST.read_text('utf8'))
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),manifest['baseline_sha256'])
  self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),manifest['sha256'])
  with sqlite3.connect(BASE) as old,sqlite3.connect(ARCHIVE) as db:
   self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
   counts={'sections':21,'cases':103,'historical_chart_cells':927,
     'historical_case_additional_cast_cells':81,'historical_case_additional_casts':9,
     'historical_case_reasoning':495,'historical_case_reasoning_trace':495,
     'historical_palace_standardization':1008,'semantic_assertions':1257,
     'historical_misc_cast_context':7}
   for tab,n in counts.items():self.assertEqual(db.execute('SELECT count(*) FROM '+tab).fetchone()[0],n,tab)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0],0)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL").fetchone()[0],112)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_additional_casts WHERE case_id='shenqi.misc.case01'").fetchone()[0],2)
   self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE case_id LIKE 'shenqi.misc.case%'").fetchone()[0],5)
   self.m.compare_legacy(old,db)
if __name__=='__main__':unittest.main()
