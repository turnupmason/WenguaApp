"""V3.8 deterministic reader and original-book source regressions."""
from __future__ import annotations
import hashlib,unittest
from scripts.replay_health_v38_user_and_two_seeded_cases import evaluate,PARENT,PARENT_SHA,RANDOM_INDICES,PINNED_CASE_IDS,SEED_SHA,SEED_INPUT
from src.wengua.health_severity_v38 import _customer_clean
from src.wengua.symbol_relations import stem_stage

class UserAndAncientHealthV38(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=evaluate()
    def test_immutable_source_and_random_selection(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
        self.assertEqual(RANDOM_INDICES,[7,4])
        self.assertEqual(self.data["randomly_selected_family_ids"],PINNED_CASE_IDS)
        self.assertEqual(self.data["rng_seed_sha256"],hashlib.sha256(SEED_INPUT.encode()).hexdigest())
    def test_noon_bing_stage_and_illness_void(self):
        self.assertEqual(stem_stage("丙","墓")["branch"],"戌")
        self.assertEqual(stem_stage("丙","绝")["branch"],"亥")
        row=self.data["records"][0]
        self.assertEqual(row["four_pillars"],{"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"})
        self.assertEqual(row["patient_palace"],4)
        self.assertEqual(row["illness_palace"],6)
        facts=row["illness_stem_tomb_absence"]
        self.assertEqual(facts["actual_heaven_carried_stem"],"丙")
        self.assertEqual(facts["illness_palace_branches"],("戌","亥"))
        self.assertEqual(facts["hour_xun_head"],"甲子")
        self.assertEqual(set(facts["void_branches"]),{"戌","亥"})
        for key in ("tomb_branch_in_illness_palace","extinct_branch_in_illness_palace","void_in_illness_palace","compound_tomb_extinct_void_same_palace"):
            self.assertTrue(facts[key])
        for word in ("丙火在戌为墓","丙在亥为绝","戌、亥空","病星宫乾六宫逢旬空","地刑玄武","月奇相合"):
            self.assertIn(word,row["reading_text"])
        self.assertFalse(row["two_sided_evidence"]["patient_void"])
    def test_three_complete_clean_customer_readings(self):
        self.assertEqual(len(self.data["records"]),3)
        self.assertEqual(len({x["case_id"] for x in self.data["records"]}),3)
        for row in self.data["records"]:
            self.assertEqual(hashlib.sha256(row["reading_text"].encode()).hexdigest(),row["readout_sha256"])
            self.assertIn(len(row["sections"]),(10,11))
            self.assertEqual(len(row["book_81_ordered_pairs_current_chart"]),9)
            self.assertEqual(len(row["user_42_stem_pairs_audit"]),42)
            self.assertEqual(len(row["composites_17_audit"]),17)
            self.assertNotRegex(row["reading_text"],r"原书第\s*\d+\s*行")
            self.assertNotRegex(row["reading_text"],r"数据库|程序|测试|GPT|SHA|SQLite")
            self.assertFalse(row["original_author_conclusion_used_as_input"])
    def test_source_lines_only_internal(self):
        self.assertEqual(_customer_clean("丙加辛月奇相合（原书第332行）。"),"丙加辛月奇相合。")
        for row in self.data["records"]:
            self.assertTrue(all(z["source_line"]>0 and len(z["source_sha256"])==64 for z in row["book_81_ordered_pairs_current_chart"]))
    def test_actual_random_two_person_and_self(self):
        one,two=self.data["records"][1:]
        self.assertEqual(one["case_id"],"kaiwu.health.19950219.brother_paralysis")
        self.assertEqual(one["relationship"],"younger_sibling")
        self.assertEqual(two["case_id"],"shenqi.health.19961102.on_site_health")
        self.assertEqual(two["relationship"],"self")
        self.assertEqual(one["four_pillars"]["hour"],"癸巳")
        self.assertEqual(two["four_pillars"]["hour"],"庚申")
if __name__=="__main__":unittest.main()
