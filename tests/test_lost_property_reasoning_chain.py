"""Source step evidence mapping must cover every one of the book's 36 analyses."""
import json
from pathlib import Path
from unittest import TestCase
ROOT=Path(__file__).resolve().parents[1]
class SourceReasoningEvidenceTest(TestCase):
    def test_source_line_coverage(self):
        d=ROOT/"data/knowledge/shenqi/lost_money_property_prediction_ch09"
        index=json.loads((d/"case_index.json").read_text(encoding="utf8"))["cases"]
        reason=json.loads((d/"author_reasoning_evidence_index.json").read_text(encoding="utf8"))
        self.assertEqual((len(reason["cases"]),sum(len(c["steps"]) for c in reason["cases"])),(8,36))
        for source,details in zip(index,reason["cases"]):
            self.assertEqual(source["case_id"],details["case_id"])
            self.assertEqual(source["numbered_or_unnumbered_analysis_lines"],[x["source_line"] for x in details["steps"]])
            for step in details["steps"]:
                self.assertTrue(step["author_evidence_sequence_paraphrase"])
                self.assertTrue(step["counterevidence_or_caveat"])
                self.assertFalse(step["positive_training_eligible"])
