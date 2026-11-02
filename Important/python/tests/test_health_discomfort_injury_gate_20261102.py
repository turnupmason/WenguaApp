"""Execute real calendar boards through every explicit injury selection."""
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.wengua.health_discomfort_v19_parity import (
    compose, load_sources, _parts, _matched, ELEMENTS, CONTROLS,
)
from src.wengua.health_lifecycle_v391 import source_full12
from tests.test_ios_five_random_live_casts import generated_case


def live_board(iso):
    chart, palaces, extra = generated_case(iso, source_full12())
    chart.update(extra)
    chart["palaces"] = list(palaces.values())
    chart["hourHorsePalace"] = next(p["id"] for p in chart["palaces"] if p["horseBranch"])
    actor = {"mainStem": "庚", "mainPalace": next(
        p["id"] for p in chart["palaces"]
        if any(s["carriedStem"] == "庚" for s in p["heavenStars"]))}
    return chart, actor


class InjuryGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_sources()
        cls.boards = [live_board(iso) for iso in (
            "2026-11-18T09:00:00-05:00", "2026-12-02T21:00:00-05:00",
            "2026-12-29T09:00:00-05:00", "2027-02-07T11:00:00-05:00")]

    def test_missing_choice_rejects_before_board_lookup(self):
        for choice in (None, "", "unspecified", "unknown"):
            with self.subTest(choice=choice), self.assertRaises(ValueError):
                compose({}, {}, "丈夫", choice, self.sources)

    def test_all_six_selections_true_palace_and_priority(self):
        for chart, actor in self.boards:
            injury = next(p for p in chart["palaces"] if p.get("door") == "伤门")
            for choice in ("none", "accident", "bone", "bleeding", "severe_pain", "surgery"):
                with self.subTest(iso=chart["iso"], choice=choice):
                    got = compose(chart, actor, "丈夫", choice, self.sources)
                    sections = {x["id"]: x["text"] for x in got["sections"]}
                    self.assertEqual("02_injury" in sections, choice != "none")
                    self.assertEqual("injury" in got["rolePalaces"], choice != "none")
                    if choice == "none":
                        self.assertEqual(got["sections"][0]["id"], "01_location")
                        continue
                    self.assertEqual(got["sections"][0]["id"], "02_injury")
                    self.assertEqual(got["rolePalaces"]["injury"], injury["id"])
                    text = sections["02_injury"]
                    for token in ("伤门落", "伤门力量", injury["deity"], "地盘", "天盘"):
                        self.assertIn(token, text)
                    for star in injury["heavenStars"]:
                        self.assertIn(star["star"], text)
                        self.assertIn("天盘" + star["carriedStem"], text)
                    self.assertNotIn("待核", text)
                    if choice in {"accident", "bone", "bleeding", "severe_pain"}:
                        # The conclusion must name an anatomical candidate of
                        # the ACTUAL injury palace, even if the door is weak/void.
                        scope = "体表" if choice != "severe_pain" else (
                            "体内" if injury["id"] in (
                                {1,8,3,4} if chart["bureau"]["dun"] == "yang" else {9,2,7,6}) else "体表")
                        code = injury["gua"] + {1:"一",2:"二",3:"三",4:"四",6:"六",7:"七",8:"八",9:"九"}[injury["id"]]
                        rule = next(r for r in self.sources[0]["rules"]
                                    if r["子类"] == "神奇之门-" + scope and r["符号组合"] == code + "·" + scope)
                        candidates = _parts(rule["古籍象意或候选"])
                        head = sections["09_conclusion"].split("。",1)[0]
                        self.assertIn("先从伤门落宫看", head)
                        self.assertTrue(any(site in head for site in candidates), head)
                    if choice == "surgery":
                        self.assertIn("伤门所示手术部位另看", sections["09_conclusion"])

    def test_surgery_both_real_signals_and_negative_cases(self):
        observed = set()
        start = datetime(2026,11,15,9,tzinfo=ZoneInfo("America/New_York"))
        for offset in range(60):
            chart, actor = live_board((start+timedelta(days=offset)).isoformat())
            injury = next(p for p in chart["palaces"] if p.get("door") == "伤门")
            opening = next(p for p in chart["palaces"] if p.get("door") == "开门")
            tiger = injury["deity"] == "白虎"
            control = CONTROLS[ELEMENTS[opening["id"]]] == ELEMENTS[injury["id"]]
            text = compose(chart,actor,"丈夫","surgery",self.sources)["sections"][0]["text"]
            self.assertEqual("伤门同宫临白虎，传统有开刀" in text, tiger)
            self.assertEqual("五行克伤门宫，传统有外科处理" in text, control)
            observed.update({("tiger",tiger),("control",control)})
            if len(observed) == 4:
                break
        self.assertEqual(len(observed),4)


if __name__ == "__main__":
    unittest.main()
