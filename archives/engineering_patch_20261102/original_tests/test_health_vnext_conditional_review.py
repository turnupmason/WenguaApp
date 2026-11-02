"""Independent V-next disease evidence logic acceptance; DO NOT tune to outcomes.

Pins old 4 V3.9.1 SHA facts, plus separately tests new conditional review
logic, no forced binary decision, source polarity gated, no evidence doubles.
"""
from __future__ import annotations
import hashlib
import json
import unittest
from pathlib import Path

from src.wengua.health_text_pipeline import auto_cast_health_v39_text
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_severity_vnext_review import (
    review_ordered_pairs,decide_review,dedup_lifecycle_facts,
)

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=ROOT/"data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json"
SELF={"intent":"severity","relationship":"self","consultation_context":"direct_self"}


class PureDecisionTests(unittest.TestCase):
    def base(self,**kwargs):
        options={
            "role_confidence":"source_case_specific",
            "patient_void":False,"patient_hazards":[],
            "patient_to_illness":"克","illness_to_star":"克",
            "medicine_controls":False,
            "eligible_bad_patient_pair":False,
            "unverified_bad_patient_pair":False,
        }
        options.update(kwargs)
        return decide_review(**options)

    def test_double_control_only_if_patient_is_unblocked(self):
        self.assertEqual(self.base()["state"],"favorable")
        self.assertEqual(self.base(patient_void=True)["state"],"conflicted")
        self.assertEqual(self.base(patient_hazards=["六仪击刑"])["state"],"conflicted")

    def test_true_double_adverse_and_medicine_conflict(self):
        a=self.base(patient_to_illness="受克",illness_to_star="比和")
        self.assertEqual(a["state"],"adverse")
        self.assertEqual(self.base(patient_to_illness="受克",
                     illness_to_star="比和",medicine_controls=True)["state"],"conflicted")

    def test_unproved_book_bad_cannot_force_original_binary(self):
        state=self.base(patient_to_illness="受克",illness_to_star="受生",
                        unverified_bad_patient_pair=True)
        self.assertEqual(state["state"],"unresolved")
        self.assertIsNone(state["decisive_chain"])

    def test_conditional_person_role_and_no_chain_must_abstain(self):
        self.assertEqual(self.base(role_confidence="research_candidate_only")["state"],"unresolved")
        self.assertEqual(self.base(patient_to_illness="比和",
                                   illness_to_star="比和")["state"],"unresolved")

    def test_source_phrase_not_a_verified_book_predicate(self):
        raw=[{"palace":6,"star":"天芮星","top":"丙","bottom":"戊",
              "roles":["病宫","值符宫"],"title":"飞鸟跌穴",
              "applicability":"book_health_adverse",
              "source_conditions":{"如果":False,"门迫":False,"但":False},
              "source_line":258,"source_sha256":"a"*64,
              "user_health_supplement":"health_supplement_pair_02"}]
        out=review_ordered_pairs(raw,{"illness_duration":"new"})
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["source_state"],"health_phrase_needs_full_gate")
        self.assertEqual(out[0]["roles"],["病宫","值符宫"])
        self.assertEqual(out[0]["supplement_id_internal"],"health_supplement_pair_02")

    def test_sky_earth_same_stem_same_branch_are_separate_facts(self):
        both={"stem":"丙","palace":6,"actual_stage_facts":[
            {"branch":"戌","stage":"墓"},{"branch":"亥","stage":"绝"}]}
        roles={x:both for x in ("patient","illness_tianrui_heaven",
                  "doctor_tianxin_heaven","medicine_yi","hour_event")}
        chart={"palaces":{str(i):{"earth_stem":"丙","heaven_stars":[],
                    "door":None,"deity":None} for i in range(1,10)}}
        facts=dedup_lifecycle_facts(roles,chart=chart)
        self.assertEqual(len(facts),14) # 12 real Earth branches + 2 sky branches
        sky=[x for x in facts if x["plane"]=="天盘" and x["palace"]==6]
        earth=[x for x in facts if x["plane"]=="地盘" and x["palace"]==6]
        self.assertEqual({x["stage"] for x in sky},{"墓","绝"})
        self.assertEqual({x["stage"] for x in earth},{"墓","绝"})
        self.assertTrue(set(x["fact_id"] for x in sky).isdisjoint(
                        x["fact_id"] for x in earth))

    def test_overlapping_roles_share_one_real_lifecycle_fact(self):
        common={"stem":"丙","palace":6,"actual_stage_facts":[
                {"branch":"戌","stage":"墓"},{"branch":"亥","stage":"绝"}]}
        evidence={k:common for k in ("patient","illness_tianrui_heaven",
                   "doctor_tianxin_heaven","medicine_yi","hour_event")}
        facts=dedup_lifecycle_facts(evidence)
        self.assertEqual(len(facts),2)
        self.assertEqual({z["stage"] for z in facts},{"墓","绝"})
        self.assertEqual(len(facts[0]["roles"]),5)


class MonthAndPalaceControlTests(unittest.TestCase):
    def compare(self,rel,**adjustments):
        from src.wengua.health_palace_sequence_vnext import compare_vigor_before_control
        opts=dict(relation=rel,actor_symbol_month="废",
                  target_symbol_month="旺",
                  actor_palace_month="囚",target_palace_month="旺")
        opts.update(adjustments)
        return compare_vigor_before_control(**opts)

    def test_weak_tianxin_versus_strong_tianrui_is_not_effective_control(self):
        # 天心星月废、医生落宫囚；天芮月旺、病星落宫旺。
        fact=self.compare("克")
        self.assertEqual(fact["nominal_relation"],"克")
        self.assertEqual(fact["power_class"],"反侮候选")
        self.assertEqual(fact["effect"],"limited")
        self.assertIn("弱者难克旺者",fact["why"])

    def test_strong_tianxin_resists_weak_disease_nominal_attack(self):
        fact=self.compare("受克",actor_symbol_month="旺",
                          actor_palace_month="旺",
                          target_symbol_month="废",target_palace_month="囚")
        self.assertEqual(fact["nominal_relation"],"受克")
        self.assertEqual(fact["power_class"],"反克候选")
        self.assertEqual(fact["effect"],"resists_weak_attack")
        self.assertIn("不能推断最终结果",fact["why"])

    def test_star_and_palace_mixed_strength_must_not_trigger_reverse(self):
        fact=self.compare("克",actor_symbol_month="废",
                          actor_palace_month="旺",
                          target_symbol_month="旺",target_palace_month="旺")
        self.assertEqual(fact["power_class"],"ordinary_conditional")
        self.assertEqual(fact["effect"],"conditional")

    def test_void_obstruction_and_unknown_stages_cannot_be_assumed(self):
        fact=self.compare("克",blocked=True)
        self.assertEqual(fact["effect"],"obstructed")
        self.assertNotEqual(fact["power_class"],"反侮候选")
        fact=self.compare("克",actor_symbol_month="未知")
        self.assertEqual(fact["effect"],"unknown")

    def test_shared_strength_engine_can_be_imported_without_health_domain(self):
        from src.wengua.qualitative_month_palace import compare_vigor_before_control
        f=compare_vigor_before_control(
            "克",actor_symbol_month="废",actor_palace_month="囚",
            target_symbol_month="旺",target_palace_month="旺")
        self.assertEqual(f["power_class"],"反侮候选")
        self.assertNotIn("痊愈",f["why"])
        self.assertNotIn("医生",f["why"])

    def test_same_element_must_still_compare_strength(self):
        fact=self.compare("比和")
        self.assertIn(fact["effect"],("same_element","limited"))
        self.assertIn("比和",fact["nominal_relation"])

class FullRealChartPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=json.loads(SAMPLE.read_text("utf8"))["samples"]
        cls.results=[]
        for row in cls.frozen:
            arguments={"iso":row["local_datetime"],"timezone_name":row["timezone"],
                       "inquiry":dict(SELF)}
            old=auto_cast_health_v39_text(**arguments)
            review=auto_cast_health_review_text(**arguments)
            cls.results.append((row,old,review))

    def test_old_frozen_v391_text_byte_identical_after_new_branch_added(self):
        self.assertEqual(len(self.results),4)
        for row,old,review in self.results:
            self.assertEqual(old["reading_text"],row["v391_customer_reading_text"])
            self.assertEqual(hashlib.sha256(old["reading_text"].encode()).hexdigest(),
                             row["v391_customer_reading_sha256"])
            self.assertEqual(old["score"],None)
            self.assertEqual(review["audit"]["legacy_v391_reading_text"],old["reading_text"])

    def test_new_readings_complete_and_no_scores_or_unverified_claims(self):
        for row,old,review in self.results:
            self.assertEqual(review["four_pillars"],row["four_pillars"])
            names=[part["title"] for part in review["sections"]]
            self.assertGreaterEqual(len(names),8)
            self.assertEqual(names[:5],["起盘总纲：五不遇时、伏吟、反吟","天芮病宫","天心医生","乙奇医药","患者用神"])
            self.assertIn("全部证据合断",names)
            self.assertEqual(names[-1],"时空及应期")
            self.assertEqual(review["evidence_counts"]["qualified_favorable"],
                             len(review["evidence_ledger"]["favorable"]))
            self.assertEqual(review["evidence_counts"]["qualified_adverse"],
                             len(review["evidence_ledger"]["adverse"]))
            self.assertTrue(review["verdict"]["state"] in
                            {"favorable","adverse","conflicted","unresolved"})
            self.assertEqual(review["audit"]["matched_real_star_pairs"],9)
            self.assertEqual(review["audit"]["book_81_catalog_size"],81)
            self.assertEqual(review["audit"]["supplement_rules_preserved"],42)
            self.assertEqual(review["audit"]["composites_preserved"],17)
            self.assertTrue(review["no_scoring"])
            self.assertFalse(review["medical_validity_claimed"])
            self.assertNotIn("健康指数",review["reading_text"])
            self.assertNotIn("吉凶概率",review["reading_text"])
            self.assertNotIn("原书第",review["reading_text"])
            self.assertNotIn("数据库",review["reading_text"])
            keys=[t["fact_id"] for t in review["audit"]["actual_stage_facts_unique"]]
            self.assertEqual(len(keys),len(set(keys)))

    def test_different_logic_is_preview_only_not_clinically_validated(self):
        for row,old,review in self.results:
            self.assertEqual(review["status"],"review_not_public")
            self.assertEqual(review["audit"]["actual_original_author_outcomes_not_used"],True)
        print("\n=== Four independent source-calculated review examples (not blind outcomes) ===")
        for n,(row,old,review) in enumerate(self.results,1):
            print("CASE",n,row["local_datetime"])
            print("BASELINE",old["reading_text"].split("最后断词：")[-1][:250].strip())
            print("MACRO",review["sections"][0]["text"])
            print("REVIEW",next(x["text"] for x in review["sections"]
                                if x["title"]=="全部证据合断"))
            print("GATES",review["audit"]["missing_source_predicates"],
                  "LIFECYCLE_UNIQUE",len(review["audit"]["actual_stage_facts_unique"]))


class OldBookQuestionOnlySmoke(unittest.TestCase):
    """Two preselected historical families: verify source-first inputs ONLY.

    These are known development cases. Never read author's outcome/feedback,
    never claim this is an untouched blind accuracy evaluation.
    """
    def test_two_source_historical_roles_are_not_forced_to_self(self):
        from scripts.replay_health_v39_fixed_cases import (
            CASES,RANDOM_INDICES,PARENT)
        from src.wengua.astro_calendar import solar_chart_clock
        from src.wengua.casting_shenqi import layout_from_explicit_bureau
        from src.wengua.health_severity_vnext_review import analyze_health_severity_review
        seen=[]
        for index in RANDOM_INDICES:
            spec=CASES[index]
            iso=spec["date"]+"T"+spec["clock"]+":00+08:00"
            clock=solar_chart_clock(iso,"Asia/Shanghai")
            p=clock["four_pillars"]
            self.assertEqual(p["day"],spec["day"])
            self.assertEqual(p["hour"],spec["hour"])
            chart=layout_from_explicit_bureau(
                 dun=spec["dun"],ju=spec["ju"],hour_ganzhi=p["hour"])
            self.assertEqual(chart["value_star"],spec["star"])
            self.assertEqual(chart["value_door"],spec["door"])
            q={"intent":"severity","relationship":spec["relation"],
               "consultation_context":spec.get("context","direct_proxy")}
            if spec.get("sex"):q["patient_sex"]=spec["sex"]
            if spec.get("relative_specific"):q["relative_specific"]=spec["relative_specific"]
            if spec.get("birth_ganzhi"):q["patient_birth_ganzhi"]=spec["birth_ganzhi"]
            calendar={"year_ganzhi":p["year"],"month_ganzhi":p["month"],
                      "day_ganzhi":p["day"],"hour_ganzhi":p["hour"],
                      "month_branch":p["month"][1]}
            answer=analyze_health_severity_review(
                chart=chart,inquiry=q,calendar=calendar,db_path=PARENT)
            self.assertEqual(answer["audit"]["matched_real_star_pairs"],9)
            self.assertEqual(answer["audit"]["book_81_catalog_size"],81)
            self.assertEqual(answer["audit"]["supplement_rules_preserved"],42)
            self.assertEqual(answer["audit"]["composites_preserved"],17)
            self.assertTrue(answer["audit"]["actual_original_author_outcomes_not_used"])
            self.assertGreaterEqual(len(answer["sections"]),8)
            self.assertEqual(answer["sections"][0]["title"],"起盘总纲：五不遇时、伏吟、反吟")
            self.assertTrue(answer["no_scores"])
            seen.append((spec["id"],answer["verdict"]["label"],
                         answer["audit"]["role_confidence"]))
        self.assertEqual(len({k for k,*_ in seen}),2)
        print("KNOWN HISTORICAL QUESTION-ONLY SMOKE; NOT SECRET BLIND:",seen)


if __name__=="__main__":
    unittest.main()
