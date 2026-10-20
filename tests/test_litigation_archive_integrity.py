"""stdlib CI: verify complete 15-section SQLite, author stages, legacy continuity."""
from __future__ import annotations
import hashlib, importlib.util, json, sqlite3, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'archives/sqlite/WenguaApp_神奇之门_14章_71案例_完整研究库.sqlite3'
NEW=ROOT/'archives/sqlite/WenguaApp_神奇之门_15章_77案例_完整研究库.sqlite3'
D=ROOT/'data/knowledge/shenqi/litigation_prediction_ch11'
MAN=ROOT/'archives/sqlite/15chapters_77cases_manifest.json'

class LitigationArchiveRegression(unittest.TestCase):
 def test_binary_archive_and_source_integrity(self):
  if not (BASE.exists() and NEW.exists()):
   self.skipTest('Full public historical archives not present in this checkout')
  m=json.loads(MAN.read_text(encoding='utf8'))
  self.assertEqual(hashlib.sha256(NEW.read_bytes()).hexdigest(),m['sha256'])
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),m['baseline_sha256'])
  with sqlite3.connect(NEW) as db:
   self.assertEqual(db.execute('pragma integrity_check').fetchone()[0],'ok')
   self.assertEqual(db.execute('pragma foreign_key_check').fetchall(),[])
   for t,n in [('sections',15),('cases',77),('historical_chart_cells',693),
               ('historical_case_additional_cast_cells',45),('historical_case_reasoning',344),
               ('semantic_assertions',947),('historical_palace_standardization',738),
               ('historical_case_reasoning_trace',344),('historical_case_reasoning_corrections',2)]:
    self.assertEqual(db.execute('SELECT count(*) FROM '+t).fetchone()[0],n,t)
   full=db.execute("SELECT original_text FROM sections WHERE section_key='litigation_prediction_ch11'").fetchone()[0]
   self.assertEqual(hashlib.sha256(full.encode('utf8')).hexdigest(),'a0cf2a05700bfb832420d3318b2982d25f6150e7a5c5e8c5ecc1ae07f5c810d2')
   self.assertEqual(sum(len(z) for z in [full.splitlines()]),267)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_review_audit WHERE human_complete_step_chains>0").fetchone()[0],0)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_door IS NULL AND standard_star IS NULL AND standard_deity IS NULL").fetchone()[0],82)
   self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE case_id LIKE 'shenqi.litigation.%'").fetchone()[0],6)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning WHERE case_id LIKE 'shenqi.litigation.%'").fetchone()[0],25)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_phase_events WHERE case_id='shenqi.litigation.case06' AND phase='retrospective_author_explanation'").fetchone()[0],1)
   known=db.execute("SELECT known_before FROM cases WHERE case_id='shenqi.litigation.case06'").fetchone()[0]
   self.assertNotIn('结果事情的发展',known)
   self.assertNotIn('厂里经过咨询',known)
   self.assertNotIn('你是原告，你胜诉',known)
   self.assertNotIn('12月27号撤诉',known)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning_corrections WHERE case_id='shenqi.litigation.case05' AND original_analysis_is_positive_training=0").fetchone()[0],2)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE case_id LIKE 'shenqi.litigation.%' AND positive_training_eligible=1").fetchone()[0],0)
   self.assertEqual(db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id='shenqi.litigation.case05'").fetchone()[0],'author_book_success_default')
 def test_source_chapter_schema_and_case_index_complete(self):
  idx=json.loads((D/'case_index.json').read_text(encoding='utf8'))
  method=json.loads((D/'method_index.json').read_text(encoding='utf8'))
  self.assertEqual(len(idx['cases']),6)
  self.assertEqual(sum(len(c['analysis']) for c in idx['cases']),25)
  self.assertEqual(len(method['methods']),31)
  evid=json.loads((D/'author_reasoning_evidence_index.json').read_text(encoding='utf8'))
  self.assertEqual(sum(len(x['steps']) for x in evid['cases']),25)
  self.assertTrue(all(not z['positive_training_eligible'] for x in evid['cases'] for z in x['steps']))
  self.assertEqual([c['original_chart_start'] for c in idx['cases']],[30,67,104,145,188,245])
  self.assertEqual(idx['cases'][4]['explicit_wrong_yongshen']['editor_correction_lines'],[220,222])
  self.assertEqual(idx['cases'][5]['source_chronology_exception']['analysis_paragraphs_written_after_result'],[263,267])
 def test_14_legacy_sections_unchanged(self):
  if not (BASE.exists() and NEW.exists()):self.skipTest('Repo archive absent')
  with sqlite3.connect(BASE) as base,sqlite3.connect(NEW) as out:
   a=base.execute('SELECT section_key,sha256,original_text FROM sections ORDER BY section_id').fetchall()
   b=out.execute("SELECT section_key,sha256,original_text FROM sections WHERE section_key!='litigation_prediction_ch11' ORDER BY section_id").fetchall()
   self.assertEqual(a,b)
   for tab in ('cases','historical_chart_cells','historical_case_reasoning'):
    old=base.execute('SELECT * FROM '+tab).fetchall()
    new=set(out.execute('SELECT * FROM '+tab).fetchall())
    self.assertTrue(all(v in new for v in old),'changed '+tab)
if __name__=='__main__':unittest.main()
