"""Reproducible random 2021 SELF-health example using production real chart.

No chart cells, auspices, scores, or verbal readings are hand-authored.
Runs offline in GitHub WenguaApp CI with the current checked-in 81 Excel
TSV and current live/editable Chinese template JSON. Sampling is blind
to final auspice; only engine inability to bind the self day-stem may
skip a timestamp. No clinical diagnostic/forecast use.
"""
from __future__ import annotations

import datetime as dt
import json
import random
import unittest
from zoneinfo import ZoneInfo

from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

SEED=20211025
ZONE="America/New_York"
INQUIRY={"intent":"severity","relationship":"self",
         "consultation_context":"direct_self"}


def selected_2021_example():
    rng=random.Random(SEED)
    sampled=[]
    for draw in range(1,101):
        naive=dt.datetime(2021,rng.randint(1,12),rng.randint(1,28),
                          rng.randrange(1,24,2))
        instant=naive.replace(tzinfo=ZoneInfo(ZONE)).isoformat()
        try:
            report=auto_cast_health_review_text(
                iso=instant,timezone_name=ZONE,inquiry=INQUIRY)
        except ValueError as exc:
            # Chart has been attempted through the REAL engine; only an
            # unresolved SELF day-stem is a legitimate skip, never auspice.
            why=str(exc)
            if ("Patient signifier unresolved" not in why and
                "No confirmed actual chart palace for this person" not in why):
                raise
            sampled.append({"draw":draw,"instant":instant,
                            "reason":"unresolved_actual_self_stem"})
            continue
        return {"seed":SEED,"draw":draw,"skipped":sampled,
                "report":report}
    raise AssertionError("100 unbiased 2021 instants all failed real self binding")


def example_payload(case):
    out=case["report"]
    net=out["full_health_role_strength_network"]
    roles={}
    for key, detail in net["complete_selected_palace_audits"].items():
        role=out["full_health_role_strength_network"]["nodes"][key]
        roles[key]={
            "role":role["role"],"palace":role["palace"],
            "symbol":role["symbol"],"strength":role["strength"],
            "star_factors":[{
                "name":x["name"],
                "strength":x["strength"]["strength_label"],
                "row":x["strength"].get("user_cell_row"),
                "column":x["strength"].get("user_cell_col"),
            } for x in detail["stars"]],
            "god":{k:detail["deity"].get(k) for k in
                   ("name","relation","polarity","strength_effect")},
            "door":{
                "name":(detail["door"]["symbol"] if detail["door"] else None),
                "strength":(detail["door"]["strength_label"]
                            if detail["door"] else None),
                "column":(detail["door"].get("user_cell_col")
                          if detail["door"] else None)},
            "heaven_stems":[{
                "symbol":x["symbol"],"strength":x["strength_label"],
                "stage_rows":x.get("stem_life_rows_at_real_palace"),
                "stage_pending":x.get("stem_life_strength_pending")
            } for x in detail["heaven_stems"]],
            "earth_stem":{
                "symbol":detail["earth_stem"]["symbol"],
                "strength":detail["earth_stem"]["strength_label"]},
            "ordered_book_81_pairs":[{
                "name":pair["name"],"heaven":pair["heaven"],
                "earth":pair["earth"],"polarity":pair.get("polarity"),
                "classical_text":pair.get("classical_text"),
                "classical_meaning":pair.get("classical_meaning"),
                "imagery":pair.get("imagery")}
                for pair in detail["ordered_book_81_pairs"]],
            "void":detail["void"],
            "door_pressure":detail["door_pressure"],
            "striking_stems":detail["striking_stems"],
            "sky_tombs":detail["sky_tombs"],
            "earth_tombs":detail["earth_tombs"]}
    chart={}
    for p,c in out["nine_palaces"].items():
        chart[p]={"deity":c["deity"],"door":c["door"],
                  "earth_stem":c["earth_stem"],
                  "heaven_stars":c["heaven_stars"]}
    return {
        "seed":case["seed"],"draw":case["draw"],
        "skipped":case["skipped"],
        "instant":out["instant"],"zone":out["timezone"],
        "four_pillars":out["four_pillars"],
        "solar_term":out["solar_term"],
        "bureau":out["bureau"],
        "chart_facts":out["chart_facts"],
        "nine_palaces":chart,
        "first_stage_macro":out["first_stage_macro"],
        "role_details":roles,
        "role_relationships":net.get("role_group_reviews",{}),
        "qian_kun":net.get("qian_kun_auxiliary_observations"),
        "evidence_counts":out["evidence_counts"],
        "verdict":out["verdict"],
        "sections":out["sections"],
        "no_scoring_flag":out["no_scoring"],
        "clinical_validity_claimed":out["medical_validity_claimed"],
    }


class Blind2021RealSelfExample(unittest.TestCase):
    def test_random_2021_self_chart_and_live_template(self):
        case=selected_2021_example()
        out=case["report"]
        assert out["instant"][:4]=="2021"
        self.assertEqual(len(out["nine_palaces"]),9)
        self.assertEqual(out["four_pillars"]["hour"],out["first_stage_macro"]["five_not_encounter"]["hour_stem"]+
                         out["four_pillars"]["hour"][1])
        self.assertTrue(out["full_health_role_strength_network"]["complete_selected_palace_audits"])
        self.assertIn("天芮",out["reading_text"])
        self.assertIn("天心",out["reading_text"])
        self.assertIn("乙奇",out["reading_text"])
        self.assertTrue(out["sections"])
        self.assertFalse(out["medical_validity_claimed"])
        print("WENGUA_2021_REAL_SELF_JSON="+json.dumps(
            example_payload(case),ensure_ascii=False,separators=(",",":"),
            default=str))


if __name__=="__main__":
    unittest.main()
