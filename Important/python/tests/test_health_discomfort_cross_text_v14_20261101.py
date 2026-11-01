"""V14 cross-source workbook staging: match only actual directed evidence.

All examples are previously revealed book cases, not blind outcomes.
Never edit frozen V8 or decide a medical diagnosis from a glyph match.
"""
import json
import unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.core import cycle60
from src.wengua.health_discomfort_cross_text_v14_draft import (
    rules, inspect_cross_text_candidates, stem_source_variants)
from src.wengua.health_discomfort_template_v11_draft import compose_draft

ROOT=Path(__file__).resolve().parents[1]
CAL={"year_ganzhi":"庚午","month_ganzhi":"己丑","day_ganzhi":"辛卯"}
ASK={"intent":"discomfort","relationship":"friend",
     "consultation_context":"direct_proxy"}
DOC=ROOT/"data/knowledge/health_discomfort/book_cases_12_conflicts_20_v14_20261101.json"
MAN=ROOT/"data/knowledge/health_discomfort/workbook_255_v14_ingest_manifest_20261101.json"


class CrossSourceV14(unittest.TestCase):
    def test_spreadsheet_manifest_is_precise_not_false_import_claim(self):
        m=json.loads(MAN.read_text(encoding="utf8"))
        self.assertEqual(m["sheets"]["古籍规则总库"],255)
        self.assertEqual(m["sheets"]["组合精选"],62)
        self.assertEqual(m["sheets"]["实战与反例"],12)
        self.assertEqual(m["sheets"]["异文与冲突"],20)
        self.assertEqual(sum(m["evidence_counts"].values()),255)
        self.assertEqual(m["explicit_direction_cells"],0)
        self.assertEqual(m["missing_urls"],43)
        self.assertFalse(m["release"])
        self.assertEqual(m["sha256"],
                         "19d199a42f306d2855709a8f19979bea22e24443053e2d79e75fe89fddb6d00c")

    def test_16_cross_system_candidates_are_not_approved(self):
        p=rules()
        self.assertEqual(len(p["rows"]),16)
        self.assertTrue(all(x["status"]=="candidate_not_authorized"
                            for x in p["rows"]))
        for x in p["rows"]:
            if len(x["stem_tokens"])>1:
                self.assertFalse(x["executable_research_only"])
        self.assertEqual(len([x for x in p["rows"]
                              if x["executable_research_only"]]),6)

    def test_three_school_stem_mappings_never_self_confirm(self):
        variants=stem_source_variants()
        self.assertEqual(len(variants["mapping"]),10)
        geng=variants["mapping"]["庚"]
        self.assertIn("肺",geng["qimen_secret_vol13"])
        self.assertIn("大肠",geng["sanming_viscera"])
        self.assertIn("脐",geng["sanming_body_surface"])
        self.assertTrue(all(variants["guard"].values()))
        self.assertNotEqual(variants["provenance"][0]["verified"],
                            variants["provenance"][1]["verified"])

    def test_12_old_examples_20_conflicts_and_duplicate_family(self):
        f=json.loads(DOC.read_text(encoding="utf8"))
        self.assertEqual(len(f["cases"]),12)
        self.assertEqual(len(f["source_conflict_ids"]),20)
        groups=[c["event_family"] for c in f["cases"]]
        self.assertEqual(len(set(groups)),11)
        self.assertEqual(f["duplicate_same_event_workbook_ids"],["S02","K02B"])
        a,b=f["comparisons"]
        self.assertEqual((a["dun"],a["illness_palace"]),("yang",2))
        self.assertEqual((b["dun"],b["illness_palace"]),("yin",2))
        self.assertNotEqual(a["ordered_heaven_earth"],b["ordered_heaven_earth"])
        self.assertEqual(a["tianrui_carried_stem"],"庚")
        self.assertEqual(b["tianrui_carried_stem"],"癸")
        self.assertTrue(all(x["source_book_feedback_is_retrospective"]
                            for x in f["comparisons"]))

    def test_actual_1080_source_matching_and_preserved_alternatives(self):
        matched=0
        blocked=0
        for dun in ("yang","yin"):
            for ju in range(1,10):
                for hour in cycle60():
                    c=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                    result=compose_draft(chart=c,inquiry=ASK,calendar=CAL)
                    x=result["audit"]["v14_cross_text_research"]
                    self.assertEqual(x["schema"],
                                     "wengua_health_discomfort_v14_16_combinations_20261101")
                    self.assertEqual(x["distinct_independent_confirmations"],0)
                    self.assertEqual(x["directly_deduced_medical_organ"],None)
                    self.assertEqual(len(x["source_scheme_variants_for_actual_sky_stem"]),3)
                    self.assertEqual(sum(x["source_scheme_independent_counts"].values()),0)
                    self.assertFalse(x["released"])
                    self.assertFalse(result["ios_enabled"])
                    self.assertIsNone(result["audit"]["v80_severity_score"])
                    self.assertEqual(x["primary_original_book_candidates"],
                                     result["audit"]["selected_body_candidates"])
                    matched+=len(x["research_matches"])
                    blocked+=len(x["unresolved_multi_stem_rules"])
                    for y in x["research_matches"]:
                        self.assertEqual(y["independent_confirmations"],0)
                        self.assertFalse(y["may_narrow_for_customer"])
        self.assertGreater(matched,0)
        self.assertGreater(blocked,0)

    def test_no_postcast_feedback_in_initial_evidence(self):
        c=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        r=compose_draft(chart=c,inquiry=ASK,calendar=CAL)
        location=r["audit"]["location_priority"]
        with self.assertRaises(ValueError):
            inspect_cross_text_candidates(chart=c,location=location,
                            source_case_context={"known_after_cast":True})
        with self.assertRaises(ValueError):
            inspect_cross_text_candidates(chart={**c,"school_id":"other"},
                                          location=location)
        bad={**location,"actual_sky_stem":"错"}
        with self.assertRaises(ValueError):
            inspect_cross_text_candidates(chart=c,location=bad)


if __name__=="__main__":
    unittest.main()
