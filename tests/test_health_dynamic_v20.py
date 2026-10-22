"""V2 health full 21 detailed lines; role-conditioned routes; distinct intent flows."""
from __future__ import annotations
import copy
import unittest

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v20 import analyze_health_v20, bind_patient, INTENTS
from src.wengua.phrase_pipeline import FACTOR_IDS


class HealthV20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        cls.cal={"day_ganzhi":"癸酉","year_ganzhi":"丙子",
                 "month_ganzhi":"丙午","month_branch":"午"}
    def inquire(self,who="self",intent="severity",context=None,**options):
        context=context or ("direct_self" if who=="self" else "direct_proxy")
        return {"relationship":who,"intent":intent,"consultation_context":context,**options}
    def run_case(self,who="self",intent="severity",context=None,cal=None,**options):
        return analyze_health_v20(
          chart=self.chart,inquiry=self.inquire(who,intent,context,**options),
          calendar=self.cal if cal is None else cal)
    def test_severity_all_21_full_paragraphs_no_short_generic_example(self):
        o=self.run_case()
        self.assertEqual(len(o["sections"]),21)
        self.assertGreater(len(o["reading_text"]),2400)
        self.assertIn("天芮星",o["reading_text"])
        self.assertIn("体表部位",o["reading_text"])
        self.assertIn("体内对应",o["reading_text"])
        self.assertIn("本宫五行",o["reading_text"])
        self.assertIn("天盘",o["reading_text"])
        self.assertIn("地盘",o["reading_text"])
        self.assertIn("天心星",o["reading_text"])
        self.assertIn("乙奇",o["reading_text"])
        self.assertIn("病宫",o["reading_text"])
        self.assertNotIn("《开悟之门》",o["reading_text"])
        self.assertNotIn("《神奇之门》",o["reading_text"])
        self.assertNotIn("例如",o["reading_text"])
        self.assertNotIn("{patient_",o["reading_text"])
        self.assertIsNone(o["audit"]["medical_severity_grade"])
        self.assertEqual(set(o["audit"]["twenty_four_factors"]),set(FACTOR_IDS))
    def test_same_chart_self_father_mother_friend_child_not_same_person(self):
        cases=[self.run_case("self"),
               self.run_case("father"),
               self.run_case("mother"),
               self.run_case("friend"),
               self.run_case("son",patient_sex="male",birth_order="eldest")]
        routes=[c["role_binding"]["role_name"] for c in cases]
        self.assertEqual(len(set(routes)),4) # mother/father both may be year stem
        self.assertEqual(cases[0]["role_binding"]["role_via"],"day_stem")
        self.assertEqual(cases[1]["role_binding"]["role_via"],"casting_year_stem")
        self.assertEqual(cases[2]["role_binding"]["role_via"],"casting_year_stem")
        self.assertEqual(cases[3]["role_binding"]["role_via"],"casting_month_stem")
        self.assertEqual(cases[4]["role_binding"]["role_via"],"casting_hour_stem")
        self.assertIn("乾",cases[1]["role_binding"]["extra_meaning"])
        self.assertIn("坤",cases[2]["role_binding"]["extra_meaning"])
        self.assertIn("震",cases[4]["role_binding"]["extra_meaning"])
        self.assertNotEqual(cases[0]["reading_text"],cases[3]["reading_text"])
        self.assertNotEqual(cases[1]["reading_text"],cases[2]["reading_text"])
    def test_friend_news_event_day_vs_direct_proxy_month(self):
        direct=self.run_case("friend",context="direct_proxy")
        heard=self.run_case("friend",context="event_news")
        self.assertEqual(direct["role_binding"]["role_via"],"casting_month_stem")
        self.assertEqual(heard["role_binding"]["role_via"],"day_stem")
        self.assertNotEqual(direct["role_binding"]["source_rule"],
                            heard["role_binding"]["source_rule"])
        self.assertIn("闻讯事件日干",heard["reading_text"])
        self.assertNotEqual(direct["reading_text"],heard["reading_text"])
    def test_explicit_context_required_not_silently_assumed(self):
        with self.assertRaises(ValueError):
            analyze_health_v20(chart=self.chart,
                inquiry={"intent":"severity","relationship":"friend"},calendar=self.cal)
        with self.assertRaises(ValueError):
            self.run_case("father",context="direct_self")
        with self.assertRaises(ValueError):
            self.run_case("self",context="event_news")
    def test_unknown_personal_ganzhi_not_fabricated_when_missing(self):
        for relation in ("self","father","mother","friend","son","daughter"):
            with self.subTest(who=relation):
                o=self.run_case(relation,cal={"month_branch":"午"})
                # son/daughter still know the casting hour Ganzhi
                if relation not in ("son","daughter"):
                    self.assertIsNone(o["role_binding"]["stem"])
                self.assertIn("年命未提供",o["reading_text"])
        friend=self.run_case("friend",cal={"month_branch":"午"})
        self.assertIn("尚未绑定",friend["role_binding"]["role_name"])
    def test_optional_year_is_truly_optional_and_never_becomes_cast_year(self):
        no=self.run_case("father")
        supplied=self.run_case("father",patient_birth_ganzhi="庚申")
        self.assertEqual(no["role_binding"]["stem"],supplied["role_binding"]["stem"])
        self.assertIn("年命未提供",no["role_binding"]["birth_note"])
        self.assertIn("庚申",supplied["reading_text"])
        self.assertIn("患者年命未提供",no["reading_text"])
        with self.assertRaises(ValueError):
            self.run_case("father",patient_birth_ganzhi="随便")
    def test_children_age_order_candidates_not_fixed_birth_order(self):
        b=self.run_case("son",patient_sex="male",birth_order="eldest")
        g=self.run_case("daughter",patient_sex="female",birth_order="youngest")
        self.assertIn("震",b["role_binding"]["extra_meaning"])
        self.assertIn("兑",g["role_binding"]["extra_meaning"])
        unknown=self.run_case("child")
        self.assertIn("无额外固定人物宫",unknown["role_binding"]["extra_meaning"])
    def test_each_intent_has_different_methods_and_length(self):
        expected={"severity":21,"treatment":12,"discharge":12,
                  "surgery":10,"travel_for_treatment":11}
        first=[]
        for intent,length in expected.items():
            with self.subTest(intent=intent):
                o=self.run_case("father",intent=intent)
                self.assertEqual(len(o["sections"]),length)
                self.assertIn("依据古籍",o["reading_text"])
                self.assertEqual(o["intent"],intent)
                self.assertIsNone(o["audit"]["specific_disease_diagnosis"])
                self.assertIsNone(o["audit"]["recovery_date_as_clinical_claim"])
                self.assertNotIn("《神奇之门》",o["reading_text"])
                first.append(o["sections"][0]["text"])
        self.assertGreater(len(set(first)),2)
        self.assertIn("开门",self.run_case("father",intent="surgery")["reading_text"])
        self.assertIn("旬空",self.run_case("nephew",intent="discharge")["reading_text"])
        self.assertIn("异地求医",self.run_case("spouse",intent="travel_for_treatment")["reading_text"])
    def test_source_only_status_not_clinical_and_no_v19_mutation(self):
        before=copy.deepcopy(self.chart)
        o=self.run_case()
        self.assertEqual(self.chart,before)
        self.assertEqual(o["status"],"traditional_source_research_not_clinical")
        self.assertFalse(o["audit"]["historical_feedback_used_as_input"])
    def test_cross_dun_multiple_roles_and_intents_fully_expand(self):
        """Several genuinely recalculated layouts across both Yin and Yang."""
        for dun,ju,hour in (("yang",3,"丁巳"),("yin",8,"戊戌")):
            actual=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
            for who in ("self","father","mother","friend","daughter"):
                for intent in INTENTS:
                    with self.subTest(dun=dun,who=who,intent=intent):
                        q=self.inquire(who,intent,patient_sex="female" if who=="daughter" else None,
                                       birth_order="youngest" if who=="daughter" else None)
                        o=analyze_health_v20(chart=actual,inquiry=q,calendar=self.cal)
                        self.assertEqual(len(o["sections"]),
                                         {"severity":21,"treatment":12,"discharge":12,
                                          "surgery":10,"travel_for_treatment":11}[intent])
                        self.assertEqual(len(o["audit"]["twenty_four_factors"]),24)
                        self.assertFalse(any("{" in x["text"] for x in o["sections"]))
                        self.assertFalse(any("《" in x["text"] for x in o["sections"]))
                        self.assertEqual(len({x["id"] for x in o["sections"]}),
                                         len(o["sections"]))

    def test_traditional_symbol_glossary_covers_actual_casting_symbols(self):
        from src.wengua.casting_shenqi import STARS, DOORS, DEITIES, STEMS
        from src.wengua.health_dynamic_v20 import (
            STAR_MEANINGS,DOOR_MEANINGS,DEITY_MEANINGS,STEM_MEANINGS)
        self.assertEqual(set(STARS.values()),set(STAR_MEANINGS))
        self.assertEqual(set(DOORS.values()),set(DOOR_MEANINGS))
        self.assertEqual(set(DEITIES),set(DEITY_MEANINGS))
        self.assertEqual(set(STEMS),set(STEM_MEANINGS))

    def test_invalid_chart_or_intent_rejected(self):
        wrong=copy.deepcopy(self.chart)
        wrong["palaces"]["1"]["earth_stem"]="乙"
        with self.assertRaises(ValueError):
            analyze_health_v20(chart=wrong,
              inquiry=self.inquire(),calendar=self.cal)
        with self.assertRaises(ValueError):
            self.run_case("father",intent="criminal_verdict")

if __name__=="__main__":
    unittest.main()
