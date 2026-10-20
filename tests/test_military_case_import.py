"""Original-source military HISTORICAL study; offline complete archive regression."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILDER=ROOT/'scripts/build_shenqi_17_from_16.py'
SRC=ROOT/'sources/shenqi/神奇之门_军事事件预测_精校完整版(1).txt'
BASE=ROOT/'archives/sqlite/WenguaApp_神奇之门_16章_84案例_完整研究库.sqlite3'
ARCHIVE=ROOT/'archives/sqlite/WenguaApp_神奇之门_17章_86案例_完整研究库.sqlite3'
MANIFEST=ROOT/'archives/sqlite/17chapters_86cases_manifest.json'

class MilitaryStudyRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import sys
  spec=importlib.util.spec_from_file_location('military_builder',BUILDER)
  mod=importlib.util.module_from_spec(spec)
  sys.modules[spec.name]=mod
  spec.loader.exec_module(mod)
  cls.m=mod

 def test_exact_source_and_all_casts(self):
  m=self.m;raw=SRC.read_bytes()
  self.assertEqual(len(raw),22467)
  self.assertEqual(hashlib.sha256(raw).hexdigest(),m.SOURCE_SHA)
  lines=raw.decode('utf8').splitlines()
  self.assertEqual(len(lines),183)
  cases=m.prepare(lines)
  self.assertEqual([c['event_family_id'] for c in cases],['shenqi.military.case01','shenqi.military.case02'])
  self.assertEqual([len(c['actual_printed_casts']) for c in cases],[1,3])
  self.assertEqual([len(c['original_author_steps']) for c in cases],[9,13])
  self.assertEqual([x['border'] for s in m.CASE_SPECS for x in s['source_casts']],[38,89,126,161])
  self.assertEqual(len(m.METHODS),32)
  for c in cases:
   self.assertFalse(c['positive_training_eligible'])
   for cast in c['actual_printed_casts']:
    self.assertEqual(len(m.parse_chart(lines,cast['border'])),9)
   for step in c['original_author_steps']:
    self.assertFalse(step['positive_training_eligible'])
  self.assertEqual(cases[1]['original_author_steps'][11]['source_cast'],'cast03')
  self.assertEqual(cases[1]['original_author_steps'][2]['source_end_line'],111)
  self.assertEqual(cases[0]['source_type'],'retrospective_after_actual_war')
  self.assertEqual(cases[0]['source_historical_inaccuracy_caution']['line'],31)

 def test_versioned_archive(self):
  if not ARCHIVE.exists():self.skipTest('New archival binary is written only by independent archive workflow')
  record=json.loads(MANIFEST.read_text('utf8'))
  self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),record['sha256'])
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),record['baseline_sha256'])
  with sqlite3.connect(ARCHIVE) as db,sqlite3.connect(BASE) as old:
   self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
   for table,cnt in [('sections',17),('cases',86),('historical_chart_cells',774),
       ('historical_case_additional_cast_cells',63),('historical_case_reasoning',398),
       ('semantic_assertions',1044),('historical_palace_standardization',837),
       ('historical_case_additional_casts',7),('historical_military_cast_protocol',4)]:
    self.assertEqual(db.execute('SELECT count(*) FROM '+table).fetchone()[0],cnt,table)
   self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL").fetchone()[0],93)
   self.assertEqual(db.execute('SELECT count(*) FROM historical_military_source_caveat').fetchone()[0],1)
   self.assertEqual(db.execute('SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1 AND case_id LIKE \'shenqi.military.%\'').fetchone()[0],0)
   rows=db.execute("SELECT cast_key,source_chart_line FROM historical_military_cast_protocol WHERE case_id='shenqi.military.case02' ORDER BY cast_key").fetchall()
   self.assertEqual(rows,[('cast02',126),('cast03',161),('primary',89)])
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_phase_events WHERE case_id='shenqi.military.case02'").fetchone()[0],7)
   self.assertEqual(db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id='shenqi.military.case01'").fetchone()[0],'author_book_success_default')
   self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],5)
   self.assertEqual(db.execute("SELECT sha256 FROM sections WHERE section_key='military_events_prediction_ch13'").fetchone()[0],self.m.SOURCE_SHA)
   self.assertEqual(old.execute('SELECT section_key,sha256,original_text FROM sections ORDER BY section_id').fetchall(),
     db.execute("SELECT section_key,sha256,original_text FROM sections WHERE section_key!='military_events_prediction_ch13' ORDER BY section_id").fetchall())
   for table in ('cases','historical_chart_cells','historical_case_reasoning','historical_palace_standardization'):
    self.assertTrue(all(row in set(db.execute('SELECT * FROM '+table)) for row in old.execute('SELECT * FROM '+table)),table)

if __name__=='__main__':unittest.main()
