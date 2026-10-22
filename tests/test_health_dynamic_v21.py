"""V2.1 strict directional Wu Xing and calendar consistency for health rendering."""
import unittest

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import (
    analyze_health_v21,_edge,_checked_calendar)
from src.wengua.marriage_runtime import element_relation, ELEMENTS


class HealthDirectedRelationsV21(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart=layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="戊戌")
        cls.calendar={"year_ganzhi":"乙亥","month_ganzhi":"甲申",
                      "day_ganzhi":"丙子","hour_ganzhi":"戊戌"}
    def args(self,intent="severity",who="self"):
        return dict(chart=self.chart,
            inquiry={"intent":intent,"relationship":who,
                     "consultation_context":"direct_self" if who=="self" else "direct_proxy"},
            calendar=self.calendar)
    def test_directed_five_element_all_five_disjoint(self):
        cases={
         "此宫对病宫克":"本宫克制病宫",
         "此宫对病宫受克":"本宫被病宫所克",
         "此宫对病宫生":"本宫生扶病宫",
         "此宫对病宫受生":"病宫生本宫",
         "此宫对病宫比和":"与病宫比和",
        }
        for relation,answer in cases.items():
            with self.subTest(relation=relation):
                self.assertIn(answer,_edge(relation))
        self.assertNotEqual(_edge("此宫对病宫克"),_edge("此宫对病宫受克"))
        self.assertNotEqual(_edge("此宫对病宫生"),_edge("此宫对病宫受生"))
    def test_actual_relation_orientations_use_existing_five_element_engine(self):
        self.assertEqual(element_relation("水","火"),"克")
        self.assertEqual(element_relation("火","水"),"受克")
        self.assertEqual(element_relation("木","火"),"生")
        self.assertEqual(element_relation("火","木"),"受生")
        self.assertEqual(element_relation("金","金"),"比和")
        for p,e in ELEMENTS.items():
            self.assertIsInstance(p,int)
            self.assertIn(e,("金","木","水","火","土"))
    def test_calendar_month_ganzhi_branch_must_match(self):
        a=self.args()
        a["calendar"]=dict(a["calendar"],month_branch="酉")
        with self.assertRaisesRegex(ValueError,"month_branch conflicts"):
            analyze_health_v21(**a)
    def test_calendar_hour_matches_cast(self):
        a=self.args()
        a["calendar"]=dict(a["calendar"],hour_ganzhi="己亥")
        with self.assertRaisesRegex(ValueError,"hour Ganzhi conflicts"):
            analyze_health_v21(**a)
    def test_bad_pillars_rejected(self):
        a=self.args()
        a["calendar"]=dict(a["calendar"],year_ganzhi="假的")
        with self.assertRaises(ValueError):
            analyze_health_v21(**a)
    def test_valid_month_stem_infers_month_branch(self):
        clean=_checked_calendar(self.calendar,self.chart)
        self.assertEqual(clean["month_branch"],"申")
        o=analyze_health_v21(**self.args())
        self.assertEqual(o["schema"],"wengua_health_intent_dynamic_v21")
        self.assertIn("申",o["sections"][6]["text"])
        self.assertTrue(o["audit"]["calendar_pillar_consistency_checked"])
        self.assertTrue(o["audit"]["directional_five_element_relation_fixed"])
    def test_five_distinct_intents_and_role_charts_with_calendar(self):
        length={"severity":21,"treatment":12,"discharge":12,
                "surgery":10,"travel_for_treatment":11}
        texts=[]
        for intent,n in length.items():
            with self.subTest(intent=intent):
                o=analyze_health_v21(**self.args(intent=intent,who="father"))
                self.assertEqual(len(o["sections"]),n)
                self.assertIn("父亲",o["reading_text"])
                self.assertNotIn("《开悟之门》",o["reading_text"])
                self.assertNotIn("《神奇之门》",o["reading_text"])
                self.assertIsNone(o["audit"]["medical_severity_grade"])
                texts.append(o["reading_text"])
        self.assertEqual(len(set(texts)),5)

if __name__=="__main__":
    unittest.main()
