"""Ensure the original new weather chapter is studied as five COMPLETE source events."""
from __future__ import annotations
import importlib.util,hashlib,json,sqlite3,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'sources/shenqi/神奇之门_天时气象预测_精校完整版(1).txt'
BUILDER=ROOT/'scripts/build_shenqi_18_from_17.py'
BASE=ROOT/'archives/sqlite/WenguaApp_神奇之门_17章_86案例_完整研究库.sqlite3'
ARCHIVE=ROOT/'archives/sqlite/WenguaApp_神奇之门_18章_91案例_完整研究库.sqlite3'
MANIFEST=ROOT/'archives/sqlite/18chapters_91cases_manifest.json'
class WeatherWholeCaseRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('weather_source_builder',BUILDER)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  cls.builder=module
 def test_full_original_txt_and_palaces(self):
  raw=SOURCE.read_bytes();m=self.builder
  self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(19857,m.SOURCE_SHA))
  lines=raw.decode('utf8').splitlines();self.assertEqual(len(lines),156)
  c=m.cases_index(lines)
  self.assertEqual(len(c),5)
  self.assertEqual([x['printed_original_cast_line'] for x in c],[24,51,79,109,137])
  self.assertEqual([len(x['author_step_index']) for x in c],[2,3,4,2,2])
  self.assertEqual(len(m.METHODS),36)
  for x in c:
   nine=m.parse_chart(lines,x['printed_original_cast_line'])
   self.assertEqual(len(nine),9)
   middle=[row for row in nine if row[0]==5]
   self.assertEqual(len(middle),1)
   self.assertFalse(middle[0][3]);self.assertFalse(middle[0][5])
   self.assertTrue(all(not step['positive_training_eligible'] for step in x['author_step_index']))
 def test_chronology_and_other_divinations_isolation(self):
  m=self.builder;lines=SOURCE.read_text('utf8').splitlines();items=m.cases_index(lines)
  initial=m.known_text(lines,2,items[1]['initial_question_lines'])
  self.assertNotIn('三个卦都表明',initial)
  self.assertNotIn('5月11日是晴天',initial)
  self.assertEqual(items[1]['other_divination_not_qimen']['extra_qimen_charts_printed'],0)
  self.assertEqual(items[2]['same_event_subhour_phase']['additional_printed_chart'],False)
  self.assertTrue(items[3]['reused_cast_for_different_question']['separate_weather_question'])
  self.assertIn('结果，',lines[41])
  self.assertNotIn('结果，',m.expected_outcome(lines,1,42))
  self.assertTrue(m.feedback_text(lines,1,42).startswith('结果，'))
 def test_published_archive_and_legacy_equality(self):
  if not ARCHIVE.exists():self.skipTest('GitHub archive workflow creates versioned binary after source commit')
  m=json.loads(MANIFEST.read_text('utf8'))
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),m['baseline_sha256'])
  self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),m['sha256'])
  with sqlite3.connect(ARCHIVE) as new,sqlite3.connect(BASE) as old:
   self.assertEqual(new.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(new.execute('PRAGMA foreign_key_check').fetchall(),[])
   expected={'sections':18,'cases':91,'historical_chart_cells':819,'historical_case_additional_cast_cells':63,
       'historical_case_reasoning':411,'semantic_assertions':1093,'historical_palace_standardization':882,
       'historical_weather_cast_context':5}
   for table,n in expected.items():self.assertEqual(new.execute('SELECT count(*) FROM '+table).fetchone()[0],n,table)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL").fetchone()[0],98)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],5)
   self.assertEqual(new.execute("SELECT count(*) FROM cases WHERE case_id LIKE 'shenqi.weather.%'").fetchone()[0],5)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_case_reasoning WHERE case_id LIKE 'shenqi.weather.%'").fetchone()[0],13)
   self.assertEqual(new.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE case_id LIKE 'shenqi.weather.%' AND positive_training_eligible=1").fetchone()[0],0)
   m_builder=self.builder
   m_builder.compare_legacy(old,new)
if __name__=='__main__':unittest.main()
