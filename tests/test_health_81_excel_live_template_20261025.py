"""User's 81 Excel rows are authoritative; no phantom unmet-predicate labels.

Tests look up all ordered 9x9 pairs, real-cast selected palace descriptions,
active user text template, scores and immutable frozen baseline.
"""
from __future__ import annotations
import unittest
from unittest.mock import patch

from src.wengua.health_81_excel_catalog_vnext import (
    catalog,lookup_pair,for_real_palace,authoritative_score_source)
from src.wengua.health_reading_template_vnext import (
    template,formation_sentence,title,render)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

REQ={"intent":"severity","relationship":"father",
     "consultation_context":"direct_proxy"}


class Excel81(unittest.TestCase):
    def test_all_81_named_historical_pairs_have_full_authority(self):
        rec=catalog()
        self.assertEqual(len(rec),81)
        self.assertEqual(sum(v["polarity"]=="吉" for v in rec.values()),25)
        self.assertEqual(sum(v["polarity"]=="凶" for v in rec.values()),56)
        self.assertEqual(len({(x["heaven"],x["earth"]) for x in rec.values()}),81)
        for x in rec.values():
            for key in ("name","classical_text","classical_meaning","imagery"):
                self.assertTrue(x[key].strip(),(x["key"],key))
            y=lookup_pair(x["heaven"],x["earth"])
            self.assertEqual(y,x)
            resolved=authoritative_score_source(x["heaven"],x["earth"])
            self.assertEqual(resolved["polarity"],x["polarity"])
            self.assertEqual(resolved["status"],"user_excel_exact_81")
            self.assertFalse(resolved["conditional"])
            line=formation_sentence(x)
            self.assertIn(x["name"],line)
            self.assertIn(x["classical_text"],line)
            self.assertIn(x["classical_meaning"],line)
            self.assertIn(x["imagery"],line)
            self.assertNotIn("条件待核",line)

    def test_golden_exact_user_excel_rows_including_old_name_conflicts(self):
        for h,e,name,polarity,ancient in (
            ("戊","戊","伏吟","凶","凡事闭塞，静守为吉。"),
            ("乙","乙","日奇伏吟","凶","只可安分守身。"),
            ("庚","己","刑格","凶","官司被重刑。"),
            ("壬","壬","蛇入地罗","凶","星门俱吉，庶免蹉跎。"),
            ("癸","癸","天网四张","凶","行人失伴，病讼皆伤。")):
            x=lookup_pair(h,e)
            self.assertEqual((x["name"],x["polarity"],x["classical_text"]),
                             (name,polarity,ancient))
        self.assertEqual(lookup_pair("丁","乙")["imagery"],
                         "乙木生丁阴火，日奇扶星奇，有三奇相助、人在其中得庇护之象。")

    def test_source_tsv_is_user_editable_and_template_loader_is_single_location(self):
        obj=template()
        self.assertIn("{name}",obj["formation"])
        self.assertIn("{classical_text}",obj["formation"])
        self.assertIn("{classical_meaning}",obj["formation"])
        self.assertIn("{imagery}",obj["formation"])
        self.assertIn("role",obj["macros"])
        self.assertEqual(title("doctor"),"天心医生")
        edited={**obj,"formation":"【{name}】{polarity}｜{classical_text}"}
        with patch("src.wengua.health_reading_template_vnext.template",
                   return_value=edited):
            self.assertEqual(
                formation_sentence(lookup_pair("戊","丙")),
                "【青龙返首】吉｜动作大利。")
        self.assertTrue(render("no_natal").startswith("患者未提供"))

    def test_real_chart_displays_all_four_excel_fields_every_selected_palace(self):
        out=auto_cast_health_review_text(
            iso="2024-05-28T13:00:00-04:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"self",
                     "consultation_context":"direct_self"})
        net=out["full_health_role_strength_network"]
        details=net["complete_selected_palace_audits"]
        sections=out["sections"]
        self.assertTrue(details)
        by_title={s["title"]:s["text"] for s in sections}
        for role,detail in details.items():
            self.assertTrue(detail["user_excel_81_is_authoritative"])
            self.assertTrue(detail["ordered_book_81_pairs"])
            for pair in detail["ordered_book_81_pairs"]:
                expected=lookup_pair(pair["heaven"],pair["earth"])
                self.assertEqual(pair["name"],expected["name"])
                self.assertEqual(pair["polarity"],expected["polarity"])
                self.assertTrue(pair["can_vote"])
                self.assertEqual(pair["source_state"],"user_excel_explicit_81")
                text=out["reading_text"]
                self.assertIn("古文："+expected["classical_text"].rstrip("。；"),text)
                self.assertIn("古诀大意："+expected["classical_meaning"].rstrip("。；"),text)
                self.assertIn("天地盘取象："+expected["imagery"].rstrip("。；"),text)
        self.assertNotIn("（条件待核）",out["reading_text"])
        # One true heaven + earth pair counts once; no invented missing 82nd.
        source_polarities=[]
        for score in net["complete_selected_palace_audits"].values():
            source_polarities += [x["polarity"] for x in
                                  score["ordered_book_81_pairs"]]
        self.assertTrue(set(source_polarities).issubset({"吉","凶"}))


if __name__=="__main__":
    unittest.main()
