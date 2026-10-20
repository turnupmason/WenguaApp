"""Full-copyright chapter remains source-file; tests never fill undocumented author logic."""
from __future__ import annotations
import hashlib,importlib.util,json,sqlite3,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'sources/shenqi/神奇之门_地理环境预测_精校完整版(1).txt'
BUILDER=ROOT/'scripts/build_shenqi_19_from_18.py'
BASE=ROOT/'archives/sqlite/WenguaApp_神奇之门_18章_91案例_完整研究库.sqlite3'
ARCHIVE=ROOT/'archives/sqlite/WenguaApp_神奇之门_19章_93案例_完整研究库.sqlite3'
MANIFEST=ROOT/'archives/sqlite/19chapters_93cases_manifest.json'
class GeographicHistoricalSourceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('geography_builder',BUILDER)
  cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
 def test_source_hash_whole_events_and_literal_nine_palaces(self):
  data=SOURCE.read_bytes();m=self.m
  self.assertEqual((len(data),hashlib.sha256(data).hexdigest()),(10912,m.SOURCE_SHA))
  lines=data.decode('utf8').splitlines();self.assertEqual(len(lines),81)
  cases=m.cases_index(lines)
  self.assertEqual(len(cases),2)
  self.assertEqual([case['printed_chart_line'] for case in cases],[26,61])
  self.assertEqual([len(case['author_analysis_steps']) for case in cases],[4,2])
  self.assertEqual(len(m.METHODS),23)
  for c in cases:
   rows=m.parse_chart(lines,c['printed_chart_line'])
   self.assertEqual(len(rows),9)
   middle=[z for z in rows if z[0]==5]
   self.assertEqual(len(middle),1)
   self.assertEqual(middle[0][3],'')
   self.assertEqual(middle[0][5],'')
   self.assertTrue(all(not x['positive_training_eligible'] for x in c['author_analysis_steps']))
 def test_avoid_unprinted_board_and_unstated_reasoning(self):
  lines=SOURCE.read_text('utf8').splitlines();c=self.m.cases_index(lines)
  self.assertEqual(c[1]['printed_chart_line'],61)
  self.assertIn('第54—55行',c[1]['limitations'][0])
  self.assertTrue(any('没有逐宫方法说明' in x['source_grounded_argument_or_explicit_gap'] for x in c[1]['author_analysis_steps']))
  self.assertTrue(c[0]['first_case_previous_expert_conclusion_known'])
  self.assertTrue(any('无事后核实' in x for x in c[0]['limitations']))
  self.assertNotIn('作者确定土地权属',str(c[1]['author_analysis_steps']))
 def test_archive_full_counts_and_legacy_rows(self):
  if not ARCHIVE.exists():self.skipTest('Full 19-section archive generated only by GitHub Actions')
  m=json.loads(MANIFEST.read_text('utf8'))
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),m['baseline_sha256'])
  self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),m['sha256'])
  with sqlite3.connect(ARCHIVE) as new,sqlite3.connect(BASE) as old:
   self.assertEqual(new.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(new.execute('PRAGMA foreign_key_check').fetchall(),[])
   for table,num in [('sections',19),('cases',93),('historical_chart_cells',837),
     ('historical_case_additional_cast_cells',63),('historical_case_reasoning',417),
     ('semantic_assertions',1122),('historical_palace_standardization',900),
     ('historical_geography_source_context',2),('historical_case_reasoning_trace',417)]:
    self.assertEqual(new.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0],num,table)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL").fetchone()[0],100)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],5)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_geography_source_context WHERE other_subquestion_without_chart=1").fetchone()[0],1)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE case_id LIKE 'shenqi.geography.%' AND positive_training_eligible=1").fetchone()[0],0)
   self.m.compare_legacy(old,new)
if __name__=='__main__':unittest.main()
