"""Active integrated non-score front door, source chart and 11-slot reading.

Old numeric V4.0–V4.2 artifacts exist only as append-only historical experiments
and are never imported or called from this public route.
"""
from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
from src.wengua.health_text_pipeline import auto_cast_health_v39_text,DEFAULT_DB
ROOT=Path(__file__).resolve().parents[1]
class TextOnlyPublicEntry(unittest.TestCase):
 def test_actual_auto_clock_one_board_one_v39_template_no_score(self):
     source=json.loads((ROOT/"data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json").read_text("utf8"))
     self.assertEqual(len(source["samples"]),4)
     for row in source["samples"]:
         r=auto_cast_health_v39_text(
             iso=row["local_datetime"],timezone_name=row["timezone"],
             inquiry={"intent":"severity","relationship":"self","consultation_context":"direct_self"})
         self.assertEqual(r["four_pillars"],row["four_pillars"])
         self.assertEqual(r["actual_solar_term"],row["solar_term"])
         self.assertEqual(r["reading_text"],row["v391_customer_reading_text"])
         self.assertEqual(hashlib.sha256(r["reading_text"].encode()).hexdigest(),
                          row["v391_customer_reading_sha256"])
         self.assertEqual(len(r["text_sections"]),10)
         self.assertIsNone(r["score"])
         self.assertFalse(r["numeric_scoring_enabled"])
         self.assertEqual(len(r["source_internal_evidence"]["complete_eight_palaces_full12"]["outer_eight_palaces"]),8)
 def test_actual_full_archive_default_and_all_original_book_studies_preserved(self):
     self.assertTrue(DEFAULT_DB.is_file())
     manifest=json.loads((ROOT/"archives/sqlite/wengua_health_v391_active_numerics_disabled_manifest.json").read_text("utf8"))
     self.assertEqual(hashlib.sha256(DEFAULT_DB.read_bytes()).hexdigest(),
                      manifest["new_complete_v391_sqlite_sha256"])
     self.assertEqual(manifest["source_original_book_cases"],194)
     self.assertEqual(manifest["original_author_ordered_stem_pairs"],81)
     self.assertTrue(manifest["new_active_v391_has_no_score_or_probability"])
 def test_other_unimplemented_health_intent_is_not_falsely_reinterpreted(self):
     with self.assertRaises(ValueError):
        auto_cast_health_v39_text(iso="2026-11-04T05:00:00-05:00",
          timezone_name="America/New_York",
          inquiry={"intent":"medication","relationship":"self"})
if __name__=="__main__":unittest.main()
