import unittest
from src.wengua.core import State,state_index,cycle60,compose_reading

class CoreTest(unittest.TestCase):
    def test_sixty_and_1080_indices_are_not_charts(self):
        cycle=cycle60()
        self.assertEqual(len(cycle),60)
        self.assertEqual(len(set(cycle)),60)
        self.assertEqual(cycle[0],"甲子")
        self.assertEqual(cycle[-1],"癸亥")
        rows=state_index()
        self.assertEqual(len(rows),1080)
        self.assertEqual(len({x["state_id"] for x in rows}),1080)
        self.assertEqual(set(x["status"] for x in rows),{"index_only_unverified_chart"})
    def test_invalid_index(self):
        for args in (("yin",0,0),("yang",10,0),("yin",1,60),("other",1,2)):
            with self.assertRaises(ValueError):State(*args)
    def test_unverified_chart_must_block(self):
        self.assertEqual(compose_reading({}, "work","self",[])["status"],
                         "blocked_unverified_chart")
    def test_only_reviewed_match_and_conflict_blocks(self):
        chart={"status":"engine_verified","school_id":"shijia_zhuanpan",
               "method_version":"validated-when-available","chart_id":"fixture",
               "verification_receipt":"fixture","palaces":{"1":{"door":"开门"}}}
        def rule(n, summary="审校断语"):
            return {"status":"approved","school_id":"shijia_zhuanpan",
                "domain_id":"work","relationship_id":"self","rule_id":n,
                "source_ref":"fixture:book:section","when":{"palaces.1.door":"开门"},
                "interpretation":"通过来源核对的文字","summary":summary}
        ok=compose_reading(chart,"work","self",[rule("a")])
        self.assertEqual(ok["status"],"rule_based_traditional_explanation")
        self.assertEqual(ok["summary"],"审校断语")
        self.assertEqual(compose_reading(chart,"work","other",[rule("a")])["status"],
            "blocked_no_applicable_reviewed_rule")
        self.assertEqual(compose_reading(chart,"work","self",
            [rule("a"),rule("b","冲突断语")])["status"],"blocked_conflicting_conclusions")
        unapproved={**rule("x"),"status":"draft"}
        self.assertEqual(compose_reading(chart,"work","self",[unapproved])["status"],
                         "blocked_no_applicable_reviewed_rule")

if __name__=="__main__":
    unittest.main()
