import unittest
from src.wengua.symbol_relations import related,stem_stage,door_season

class SymbolRelationTests(unittest.TestCase):
    def test_stem_harmony_clash_and_branch_relations(self):
        self.assertEqual(related("stem_combine",["甲","己"])[0]["attributes"]["result_element"],"土")
        self.assertEqual(len(related("stem_combine",["己","甲"])),1)
        self.assertEqual(len(related("stem_clash",["甲","庚"])),1)
        self.assertEqual(len(related("branch_clash",["子","午"])),1)
        self.assertEqual(len(related("branch_harm",["未","子"])),1)
        self.assertEqual(related("branch_harm",["子","丑"]),[])
        self.assertEqual(related("branch_three_harmony",["子","辰","申"])[0]["attributes"]["result_element"],"水")

    def test_punishment_preserves_cycle_direction(self):
        self.assertEqual(len(related("branch_punishment",["子","卯"])),1)
        self.assertEqual(len(related("branch_punishment",["卯","子"])),1)
        self.assertEqual(len(related("branch_punishment",["寅","巳","申"])),1)
        self.assertEqual(len(related("branch_punishment",["巳","申","寅"])),1)
        self.assertEqual(related("branch_punishment",["寅","申","巳"]),[])
        self.assertEqual(len(related("branch_self_punishment",["辰","辰"])),1)

    def test_ten_stem_growth_and_tomb_without_guess(self):
        self.assertEqual(stem_stage("甲","长生")["branch"],"亥")
        self.assertEqual(stem_stage("乙","墓")["branch"],"戌")
        self.assertEqual(stem_stage("癸","绝")["branch"],"午")
        self.assertEqual(stem_stage("丁","帝旺")["branch"],"巳")
        with self.assertRaises(ValueError):stem_stage("甲","未知")

    def test_door_specific_status_missing_in_original(self):
        self.assertEqual(door_season("开门","秋")["stage"],"旺")
        self.assertEqual(door_season("惊门","冬")["stage"],"休")
        self.assertEqual(door_season("景门","春")["stage"],"相")
        # 死门 original does not declare every stage; do not invent missing '休'
        self.assertEqual(door_season("死门","四季月")["status"],"unspecified_in_original")
        with self.assertRaises(ValueError):door_season("foo","秋")

if __name__=="__main__":
    unittest.main()
