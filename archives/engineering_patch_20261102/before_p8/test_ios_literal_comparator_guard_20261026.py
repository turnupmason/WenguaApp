"""Refuse false-positive GPT Python versus iOS literal parity."""
import json
import tempfile
import unittest
from pathlib import Path
from compare_gpt_ios_exact_wording_20261026 import compare

class ExactParityGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.section={"id":"02","title":"病宫","text":"逐字相同，才是成功。"}
        self.source={"cases":[{
            "instant":"2024-08-02T05:00:00-04:00",
            "relationship":"本人",
            "source_sections":[self.section],
            "python_reading_text":"病宫：\n逐字相同，才是成功。"
        }]}
        self.native={"ordinal":1,
            "instant":"2024-08-02T05:00:00-04:00",
            "relationship":"本人",
            "section_count":1,
            "sections":[self.section]}
    def run_compare(self):
        a,b,c=[self.root/name for name in ("source.json","native.log","diff.md")]
        a.write_text(json.dumps(self.source,ensure_ascii=False),encoding="utf8")
        b.write_text("VNEXT_IOS_PYEXACT="+json.dumps(self.native,ensure_ascii=False)+"\n",encoding="utf8")
        return compare(a,b,c),c.read_text(encoding="utf8")
    def test_exact_match(self):
        result,report=self.run_compare()
        self.assertTrue(result)
        self.assertIn("VERDICT: PASS",report)
    def test_mismatched_clock_cannot_pass_same_wording(self):
        self.native["instant"]="2024-08-03T05:00:00-04:00"
        result,report=self.run_compare()
        self.assertFalse(result)
        self.assertIn("clock mismatch",report)
    def test_mismatched_role_cannot_pass_same_wording(self):
        self.native["relationship"]="父亲"
        result,report=self.run_compare()
        self.assertFalse(result)
        self.assertIn("role mismatch",report)
    def test_one_punctuation_change_fails(self):
        self.native["sections"]=[dict(self.section,text="逐字相同,才是成功。")]
        result,report=self.run_compare()
        self.assertFalse(result)
        self.assertIn("FULL_TEXT_MISMATCH",report)
    def test_missing_native_cast_fails(self):
        self.native["sections"]=[self.section]
        self.source["cases"].append(dict(self.source["cases"][0],
            instant="2024-08-05T05:00:00-04:00"))
        result,report=self.run_compare()
        self.assertFalse(result)
        self.assertIn("COUNT python=2 swift=1",report)
    def test_section_id_mismatch_fails_even_if_wording_matches(self):
        self.native["sections"]=[dict(self.section,id="wrong")]
        result,report=self.run_compare()
        self.assertFalse(result)
        self.assertIn("SECTION_STRUCTURE_MISMATCH",report)

if __name__=="__main__":
    unittest.main()
