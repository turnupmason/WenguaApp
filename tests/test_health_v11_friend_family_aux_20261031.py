"""V11 real-clock friend-only month stem vs four family sibling auxiliary gates.

Runs the SAME real instant and unchanged 200/81 source arithmetic.
Previously approved V8 sealed feedback is not treated as an unseen test.
"""
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

INSTANT="2026-12-03T17:30:00-05:00"
TZ="America/New_York"

def cast(relation, **extra):
    return auto_cast_health_review_text(
        iso=INSTANT,timezone_name=TZ,
        inquiry={"intent":"severity","relationship":relation,
                 "consultation_context":"direct_proxy",**extra})

class V11FriendAndSiblings(unittest.TestCase):
    def test_friend_no_demographics_no_family_aux_and_same_verdict(self):
        base=cast("friend")
        supplied=cast("friend",patient_sex="female",relative_age="older")
        a,b=(x["full_health_role_strength_network"]["nodes"]
             for x in (base,supplied))
        self.assertEqual(base["four_pillars"],supplied["four_pillars"])
        self.assertEqual(base["four_pillars"]["month"],"己亥")
        self.assertEqual(a["patient"]["symbol"],"己")
        self.assertEqual(a["patient"]["palace"],b["patient"]["palace"])
        for nodes in (a,b):
            self.assertNotIn("sibling",nodes)
            self.assertNotIn("gender",nodes)
        self.assertEqual(base["scored_relevant_palaces"],
                         supplied["scored_relevant_palaces"])
        self.assertEqual(base["verdict"],supplied["verdict"])
        self.assertEqual(base["reading_text"],supplied["reading_text"])
        self.assertNotIn("兄弟姐妹排行辅助宫",
                         "".join(x["title"] for x in base["sections"]))
    def test_four_family_siblings_true_extra_palace_one_physical_base(self):
        for relation,expected in (("older_brother",3),("older_sister",4),
                                  ("younger_brother",8),("younger_sister",7)):
            with self.subTest(relation=relation):
                r=cast(relation)
                nodes=r["full_health_role_strength_network"]["nodes"]
                self.assertEqual(nodes["patient"]["symbol"],"己")
                self.assertEqual(nodes["sibling"]["palace"],expected)
                self.assertIn(expected,r["scored_relevant_palaces"])
                self.assertIn("09a",{x["id"] for x in r["sections"]})
                self.assertEqual(len(r["scored_relevant_palaces"]),
                                 len(set(r["scored_relevant_palaces"])))
                summary=next(s["text"] for s in r["sections"]
                             if s["id"]=="90_review")
                # The auxiliary and illness may be the SAME real star/palace:
                # one role section remains, but no second independent vote.
                sibling_identity=(nodes["sibling"]["palace"],nodes["sibling"]["symbol"])
                illness_identity=(nodes["illness"]["palace"],nodes["illness"]["symbol"])
                if sibling_identity!=illness_identity:
                    self.assertIn("兄弟姐妹辅助",summary)

if __name__=="__main__":unittest.main()
