"""V3.9 fixed customer output preserves fact role without generic absent stage warnings."""
from __future__ import annotations
import hashlib,unittest
from scripts.replay_health_v39_fixed_cases import evaluate,PARENT,PARENT_SHA,RANDOM_INDICES,PINNED_CASE_IDS
class V39Concise(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.batch=evaluate()
 def test_full_parent_and_fixed_two_cases(self):
    self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
    self.assertEqual(RANDOM_INDICES,[7,4])
    self.assertEqual(self.batch["randomly_selected_family_ids"],PINNED_CASE_IDS)
    self.assertEqual(len(self.batch["records"]),3)
 def test_user_illness_bing_tomb_extinction_void_once(self):
    r=self.batch["records"][0]
    f=r["illness_stem_tomb_absence"]
    self.assertTrue(f["compound_tomb_extinct_void_same_palace"])
    self.assertIn("在戌入墓",r["reading_text"])
    self.assertIn("在亥临绝",r["reading_text"])
    self.assertIn("戌/亥空",r["reading_text"])
    self.assertIn("乾六宫旬空",r["reading_text"])
    self.assertEqual(r["reading_text"].count("在戌入墓"),1)
    self.assertEqual(r["reading_text"].count("在亥临绝"),1)
    self.assertIn("地刑玄武",r["reading_text"])
    self.assertIn("月奇相合",r["reading_text"])
 def test_absent_stages_not_padded_into_other_cases(self):
    b,a=self.batch["records"][1:]
    self.assertFalse(b["illness_stem_tomb_absence"]["tomb_branch_in_illness_palace"])
    self.assertFalse(b["illness_stem_tomb_absence"]["extinct_branch_in_illness_palace"])
    self.assertTrue(b["illness_stem_tomb_absence"]["void_in_illness_palace"])
    self.assertNotIn("未同时出现相应入墓",b["reading_text"])
    self.assertNotIn("墓、绝与旬空是同宫的不同层次",b["reading_text"])
    self.assertIn("弟弟以月干",b["reading_text"])
    self.assertNotIn("弟弟或妹妹",b["reading_text"])
    self.assertFalse(a["illness_stem_tomb_absence"]["void_in_illness_palace"])
    self.assertNotIn("未同时出现相应入墓",a["reading_text"])
    self.assertNotIn("墓、绝与旬空是同宫的不同层次",a["reading_text"])
    self.assertIn("双重制病",a["reading_text"])
 def test_full_real_source_audit_and_no_line_numbers_in_reader_text(self):
    for r in self.batch["records"]:
        self.assertIn(len(r["sections"]),(10,11))
        self.assertEqual(hashlib.sha256(r["reading_text"].encode()).hexdigest(),r["readout_sha256"])
        for key,n in (("book_81_ordered_pairs_current_chart",9),
                      ("user_42_stem_pairs_audit",42),("composites_17_audit",17)):
           self.assertEqual(len(r[key]),n)
        self.assertNotRegex(r["reading_text"],r"原书第\s*\d+\s*行")
        self.assertNotIn("数据库",r["reading_text"])
        self.assertFalse(r["original_author_conclusion_used_as_input"])
if __name__=="__main__":unittest.main()
