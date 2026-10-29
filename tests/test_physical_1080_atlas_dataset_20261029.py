"""Persistent 1080 full-plate atlas is not 1080 pre-approved health readings."""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau,cycle60

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/"data/atlas/shijia_zhuanpan_physical_1080_v1.jsonl"
AUDIT=ROOT/"data/atlas/shijia_zhuanpan_physical_1080_audit_v1.json"

class All1080PhysicalAtlasInvariant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert ATLAS.is_file()
        cls.rows=[json.loads(s) for s in ATLAS.read_text(encoding="utf8").splitlines() if s.strip()]
        cls.audit=json.loads(AUDIT.read_text(encoding="utf8"))
        cls.byid={x["base_id"]:x for x in cls.rows}
    def test_exact_index_and_complete_fingerprints(self):
        self.assertEqual(len(self.rows),1080)
        self.assertEqual(len(self.byid),1080)
        self.assertEqual(len({s["physical_fingerprint"] for s in self.rows}),1080)
        self.assertEqual(len({s["visible_layout_fingerprint"] for s in self.rows}),1032)
        self.assertEqual(self.audit["generated_rows"],1080)
        self.assertEqual(self.audit["distinct_physical_fingerprints"],1080)
        self.assertEqual(self.audit["distinct_visible_layout_fingerprints"],1032)
        self.assertEqual(self.audit["duplicate_visible_layout_hash_count"],42)
    def test_all_real_palace_and_month_condition_integrity(self):
        for item in self.rows:
            self.assertEqual(len(item["palaces"]),9)
            centre=next(p for p in item["palaces"] if p["palace"]==5)
            self.assertFalse(centre["ordinary_star_door_deity"])
            self.assertEqual(centre["earth_stem_host_palace"],2)
            per=[p for p in item["palaces"] if p["palace"]!=5]
            self.assertEqual(len(per),8)
            self.assertEqual(len({p["door"] for p in per}),8)
            self.assertEqual(len({p["deity"] for p in per}),8)
            self.assertEqual(sum(len(p["heaven_stars"]) for p in per),9)
            self.assertEqual(sum(len(p["directed_81_formations"]) for p in per),
                             item["real_81_formations_count"])
            self.assertIn(item["real_81_formations_count"],(9,10))
            for p in per:
                self.assertEqual(len(p["void_by_real_month_branch"]),12)
                self.assertEqual(len(p["heaven_residents"]),len(p["heaven_stars"]))
                self.assertIn(p["door_relation_200"],("门破","宫迫","被宫生","生宫","比和"))
            self.assertEqual(len(item["day_stem_variants"]),2)
            self.assertTrue(item["physical_only"])
            self.assertFalse(item["medical_diagnosis"])
    def test_independent_recast_target_sample(self):
        chosen=("yang-01-甲戌","yang-01-甲辰",
                "yin-02-己卯","yin-02-辛巳",
                "yang-09-癸亥","yin-09-甲子")
        for key in chosen:
            row=self.byid[key]
            board=layout_from_explicit_bureau(dun=row["dun"],ju=row["ju"],
                                               hour_ganzhi=row["hour_ganzhi"])
            for palace in row["palaces"]:
                actual=board["palaces"][str(palace["palace"])]
                self.assertEqual(actual["earth_stem"],palace["earth_stem"])
                if palace["palace"]!=5:
                    self.assertEqual(actual["heaven_stars"],palace["heaven_stars"])
                    self.assertEqual(actual["door"],palace["door"])
                    self.assertEqual(actual["deity"],palace["deity"])
    def test_visible_collision_is_not_removed(self):
        a=self.byid["yang-01-甲戌"]
        b=self.byid["yang-01-甲辰"]
        self.assertEqual(a["visible_layout_fingerprint"],b["visible_layout_fingerprint"])
        self.assertNotEqual(a["physical_fingerprint"],b["physical_fingerprint"])
        self.assertNotEqual(a["xun_shou"],b["xun_shou"])
        self.assertNotEqual(a["xun_void_branches"],b["xun_void_branches"])
if __name__=="__main__":
    unittest.main()
