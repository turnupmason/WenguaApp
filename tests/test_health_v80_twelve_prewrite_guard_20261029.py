"""Twelve literary drafts may NEVER silently alter frozen V8 grades."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/knowledge/phrase_library/health_v80_prewrite/twelve_two_clocks_20261028_literary_draft.json"

class TwelvePrewriteDraftGuard(unittest.TestCase):
    def test_twelve_have_correct_frozen_grade_and_pending_release(self):
        j=json.loads(SOURCE.read_text(encoding="utf8"))
        self.assertFalse(j["app_enabled"])
        self.assertEqual(j["status"],"human_review_pending_not_shipped")
        self.assertEqual(len(j["readings"]),12)
        self.assertEqual({x["hour"] for x in j["readings"]},{"06:00","10:00"})
        self.assertEqual({x["label"] for x in j["readings"]},{"父亲","母亲","爷爷","奶奶","姐姐","弟弟"})
        for x in j["readings"]:
            expected=0 if x["hour"]=="10:00" and x["id"] in ("older_sibling","younger_sibling") else -5
            self.assertEqual(x["score"],expected)
            self.assertEqual(x["grade"],"不凶不吉" if expected==0 else "极大凶")
            self.assertEqual(x["review_status"],"literary_candidate_only")
            self.assertIn("app_enabled",j)
            self.assertNotIn("人工已批准",x["text"])
            self.assertNotIn("痊愈日期",x["text"])

if __name__=="__main__":
    unittest.main()
