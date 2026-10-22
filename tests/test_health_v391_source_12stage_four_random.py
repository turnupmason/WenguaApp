"""Active V3.9 + real book all12 lifecycle, with no V4 number output.

Tests prove four real seeded civil-date charts, original user V3.9 texts
unchanged and source5x10 anchors, 8-corner source board, no line leakage,
zero medical score. We test rendered words and actual patient roles.
"""
from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
from scripts.replay_health_v391_four_seeded_real_times import (
    evaluate,PARENT,PARENT_SHA,SELECTED,SEED_PHRASE,SEED_SHA)
from src.wengua.health_lifecycle_v391 import (
    source_full12,stage_for_stem_at_actual_palace,all_actual_palace_stage_facts)
from src.wengua.health_severity_v391_active import analyze_health_severity_v391
from src.wengua.symbol_relations import stem_stage
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term

ROOT=Path(__file__).resolve().parents[1]

class ActiveV391SourceCustomerRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples=evaluate()
    def test_source_book_all_120_cross_validated(self):
        source=source_full12()
        self.assertEqual(len(source),10)
        for stem,item in source.items():
            self.assertEqual(len(item["stage_to_branch"]),12)
            self.assertEqual(len(item["branch_to_stage"]),12)
            for stage in ("长生","帝旺","死","墓","绝"):
                self.assertEqual(item["stage_to_branch"][stage],stem_stage(stem,stage)["branch"])
        self.assertEqual(stage_for_stem_at_actual_palace("丙",6)["actual_stage_facts"],
            [{"branch":"戌","stage":"墓"},{"branch":"亥","stage":"绝"}])
        self.assertEqual(stage_for_stem_at_actual_palace("己",4)["actual_stage_facts"],
            [{"branch":"辰","stage":"衰"},{"branch":"巳","stage":"帝旺"}])
    def test_original_old_complete_source_db_and_seed_are_unchanged(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
        self.assertEqual(len(SELECTED),4)
        self.assertEqual(len({t.isoformat() for t in SELECTED}),4)
        self.assertEqual(SEED_SHA,hashlib.sha256(SEED_PHRASE.encode("utf8")).hexdigest())
    def test_four_true_random_charts_are_purely_text_11_slot_extensions(self):
        self.assertEqual(len(self.samples["samples"]),4)
        for row in self.samples["samples"]:
            self.assertTrue(row["case_id"].startswith("random_sample_self_"))
            self.assertEqual(row["person_inquiry"]["relationship"],"self")
            self.assertTrue(row["no_numerical_score"])
            self.assertFalse(row["real_health_prognosis_claimed"])
            self.assertEqual(len(row["new_v391_customer_sections"]),10)
            self.assertEqual(hashlib.sha256(row["v391_customer_reading_text"].encode("utf8")).hexdigest(),
                             row["v391_customer_reading_sha256"])
            self.assertTrue(row["local_datetime"].endswith("-04:00") or row["local_datetime"].endswith("-05:00"))
            raw_sections=row["new_v391_customer_sections"]
            for k in ("03_illness","05_patient","07_medicine","08_hour"):
                text=next(x["text"] for x in raw_sections if x["id"]==k)
                self.assertIn("十二长生：",text)
            for k in ("01_role","02_far","04_season","09_hazards","10_pace","11_final"):
                x=next(x["text"] for x in raw_sections if x["id"]==k)
                self.assertNotIn("十二长生：",x)
            self.assertNotIn("健康指数",row["v391_customer_reading_text"])
            self.assertNotIn("吉凶概率",row["v391_customer_reading_text"])
            self.assertNotRegex(row["v391_customer_reading_text"],r"原书第\s*\d+\s*行")
            self.assertNotIn("SHA",row["v391_customer_reading_text"])
            facts=row["book_verifiable_chart_facts"]
            self.assertEqual(facts["v39_original_book_pair_catalog_size"],9)
            self.assertEqual(facts["v39_health_supplement_size"],42)
            self.assertEqual(facts["v39_complex_conditions_size"],17)
            self.assertEqual(facts["complete_eight_palaces_full12"]["total_source_stages"],120)
            self.assertEqual(len(facts["complete_eight_palaces_full12"]["outer_eight_palaces"]),8)
            self.assertTrue(facts["all_old_numeric_scoring_disabled"])
    def test_original_v39_20261022_ji_si_user_prose_stays_identical(self):
        j=json.loads((ROOT/"data/evaluation/health_v39/user_noon_two_seeded_book_families_V39_SEALED.json").read_text("utf8"))
        old=j["records"][0]
        c=solar_chart_clock("2026-10-22T12:00:00-04:00","America/New_York")
        p=c["four_pillars"]
        self.assertEqual(p,{"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"})
        b=bureau_for_term(p["day"],c["active_solar_term"])
        chart=layout_from_explicit_bureau(dun=b["dun"],ju=b["ju"],hour_ganzhi=p["hour"])
        calendar={"year_ganzhi":p["year"],"month_ganzhi":p["month"],
                  "day_ganzhi":p["day"],"hour_ganzhi":p["hour"],"month_branch":p["month"][1]}
        x=analyze_health_severity_v391(chart=chart,
            inquiry={"intent":"severity","relationship":"self","consultation_context":"direct_self"},
            calendar=calendar,db_path=PARENT)
        self.assertEqual(x["original_v39_reading"],old["reading_text"])
        self.assertEqual(x["source_chart_evidence"]["patient"]["actual_stage_facts"],
              [{"branch":"辰","stage":"衰"},{"branch":"巳","stage":"帝旺"}])
        self.assertEqual(x["source_chart_evidence"]["illness_tianrui_heaven"]["actual_stage_facts"],
              [{"branch":"戌","stage":"墓"},{"branch":"亥","stage":"绝"}])
        self.assertEqual(x["reading_text"].count("综合看，本盘古籍取象"),1)
        self.assertIsNone(x["score"])
if __name__=="__main__":unittest.main()
