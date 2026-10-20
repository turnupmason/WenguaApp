"""Hot topics unified-domain, 20 genuine boards, 13 events, author error retention."""
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_hot_topics_from_health import (
 BASE_NAME,BASE_SHA,SOURCE_SHA,ROOT,CHAPTER,EVENTS,NEW_NAME,STARTS,
 validate_source,parsed,build,chart
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_热门话题预测评析.txt"

class HotTopicsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=validate_source(cls.raw)
  cls.events=parsed(cls.lines)
 def test_original_complete_and_exact_all_20_source_prints(self):
  self.assertEqual(len(self.raw),106044)
  self.assertEqual(len(self.lines),913)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.events),13)
  self.assertEqual(sum(len(e["casts"]) for e in self.events),20)
  self.assertEqual(sorted([c["source_line"] for e in self.events for c in e["casts"]]),STARTS)
  self.assertEqual(sum(len(e["steps"]) for e in self.events),97)
  for e in self.events:
   for c in e["casts"]:
    self.assertEqual(len(c["cells"]),9)
    self.assertEqual(sorted(x["palace"] for x in c["cells"]),list(range(1,10)))
    middle=next(x for x in c["cells"] if x["palace"]==5)
    self.assertEqual(middle["god"],"")
    self.assertEqual(middle["star"],"")
 def test_one_event_many_boards_and_common_domain(self):
  e={x["key"]:x for x in self.events}
  self.assertEqual(len(e["us_election_2000"]["casts"]),3)
  self.assertEqual(len(e["beijing_2008"]["casts"]),2)
  self.assertEqual(e["beijing_2008"]["n"],["九","十三"])
  self.assertEqual(len(e["shijiazhuang_2001"]["casts"]),2)
  self.assertEqual(e["world_outlook_2000"]["casts"],[])
  self.assertEqual(len(e["rail_xinle_1998"]["casts"]),1)
  self.assertEqual(len(e["rail_xingtai_1999"]["casts"]),1)
  for key in ("river_jump","women_world_cup","beijing_2008"):
   self.assertEqual(e[key]["domain"],"sports_competition")
  for key in ("rail_xinle_1998","rail_xingtai_1999","shijiazhuang_2001"):
   self.assertEqual(e[key]["domain"],"criminal_case")
  self.assertEqual(e["nato"]["domain"],"military_history_source")
 def test_documented_prediction_error_and_hindsight_kept(self):
  by_key={e["key"]:e for e in self.events}
  self.assertTrue(by_key["taiwan_2000"]["explicit_error"])
  self.assertIn("宋楚瑜可能会获胜",self.lines[532])
  self.assertIn("陈水扁当选",self.lines[540])
  self.assertIn("看来我测错了",self.lines[542])
  self.assertIn("1951年辛卯",self.lines[544])
  self.assertIn("谁是主谁是客，却存在分歧",self.lines[370])
  self.assertIn("美国队作为东道主队",self.lines[374])
  self.assertIn("反复三次左右",self.lines[200])
  self.assertIn("人有惊无险",self.lines[200])
  self.assertEqual(by_key["world_outlook_2000"]["feedback"],[])
 def test_real_full_db_immutable_and_accepted_case_status(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/NEW_NAME;idx=Path(temp)/"knowledge"
   doc=build(BASE,SOURCE,path,idx)
   self.assertEqual(doc["new_distinct_historical_event_families"],13)
   self.assertEqual(doc["new_historical_event_families_with_casts"],12)
   self.assertEqual(doc["source_original_printed_casts"],20)
   with sqlite3.connect(path) as db:
    for table,count in doc["cumulative_counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],121)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],7)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historic_book_case_acceptance WHERE requires_manual_user_approval=0").fetchone()[0],13)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM hot_topic_witness_palaces").fetchone()[0],180)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_palace_standardization").fetchone()[0],1233)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM hot_topic_annual_forecast_parts").fetchone()[0],7)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM hot_topic_correction_audits").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM accepted_book_cases_across_books").fetchone()[0],121)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE book_id='kaiwu' AND section_key='hot_topics_prediction_ch01'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"source_audit.json").read_text("utf8"))
   self.assertTrue(audit["source_case_acceptance_is_not_independent_scientific_validation"])
if __name__=="__main__":unittest.main()
