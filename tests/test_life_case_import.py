"""Five indivisible authored stories; never leak retrospective or medical outcomes."""
from __future__ import annotations
import hashlib, importlib.util, json, sqlite3, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'sources/shenqi/神奇之门_人生机遇预测_精校完整版(1).txt'
BUILDER=ROOT/'scripts/build_shenqi_20_from_19.py'
BASE=ROOT/'archives/sqlite/WenguaApp_神奇之门_19章_93案例_完整研究库.sqlite3'
ARCHIVE=ROOT/'archives/sqlite/WenguaApp_神奇之门_20章_98案例_完整研究库.sqlite3'
MANIFEST=ROOT/'archives/sqlite/20chapters_98cases_manifest.json'
class LifeHistoryRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('life_original_source_builder',BUILDER)
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);cls.m=m
 def test_original_source_exact_all_real_charts(self):
  raw=SOURCE.read_bytes();m=self.m;lines=raw.decode('utf8').splitlines()
  self.assertEqual((len(raw),len(lines),hashlib.sha256(raw).hexdigest()),(37761,273,m.SOURCE_SHA))
  c=m.indices(lines)
  self.assertEqual([x['original_chart_start'] for x in c],[37,92,164,201,231])
  self.assertEqual([len(x['author_step_evidence']) for x in c],[11,15,7,5,13])
  self.assertEqual(len(m.METHODS),34)
  for case in c:
   cells=m.parse_chart(lines,case['original_chart_start'])
   self.assertEqual(len(cells),9)
   mid=[x for x in cells if x[0]==5][0]
   self.assertEqual((mid[3],mid[5]),('',''))
   self.assertTrue(all(not e['positive_training_eligible'] for e in case['author_step_evidence']))
 def test_case_stages_cannot_relabel_hindsight_as_first_prediction(self):
  c=self.m.indices(SOURCE.read_text('utf8').splitlines())
  self.assertEqual(c[0]['source_step_lines'][-1],78)
  self.assertEqual(c[1]['source_step_lines'][-1],155)
  self.assertTrue(c[1]['multiple_subquestions_same_event'])
  self.assertEqual(c[2]['author_step_evidence'][-1]['case_progress_phase'],'retrospective_after_result')
  self.assertTrue(c[3]['known_fatal_outcome_precedes_cast'])
  self.assertTrue(all(x['case_progress_phase']=='retrospective_after_result' for x in c[3]['author_step_evidence']))
  self.assertEqual(c[4]['explicit_year_mistake']['reported_year'],1996)
  self.assertEqual(c[4]['author_step_evidence'][5]['case_progress_phase'],'first_attempt_year_error')
  self.assertEqual(c[4]['author_step_evidence'][6]['case_progress_phase'],'after_disclosure')
 def test_previous_chapters_unchanged_and_new_source_is_integral(self):
  if not ARCHIVE.exists():self.skipTest('Separate archive workflow creates full binary after source commit')
  manifest=json.loads(MANIFEST.read_text('utf8'))
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),manifest['baseline_sha256'])
  self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),manifest['sha256'])
  with sqlite3.connect(ARCHIVE) as db,sqlite3.connect(BASE) as old:
   self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
   expected={'sections':20,'cases':98,'historical_chart_cells':882,'historical_case_additional_cast_cells':63,
     'historical_case_reasoning':468,'semantic_assertions':1207,'historical_palace_standardization':945,
     'historical_life_case_context':5,'historical_life_source_error_segments':1}
   for t,n in expected.items():self.assertEqual(db.execute('SELECT count(*) FROM '+t).fetchone()[0],n,t)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning WHERE case_id LIKE 'shenqi.life.%'").fetchone()[0],51)
   self.assertFalse(db.execute("SELECT 1 FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone())
   self.m.compare_legacy(old,db)
if __name__=='__main__':unittest.main()
