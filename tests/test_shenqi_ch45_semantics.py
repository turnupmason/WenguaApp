"""Source-free synthetic end-to-end Ch4/5 parser and cross-chapter lookup tests.

Private book text is NOT shipped into public GitHub. The synthetic source
exercises complete 81+64+72 combination matrices and source-trace integrity.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from src.wengua import compile_shenqi_ch45 as compiler
from src.wengua.semantic_lookup import (
    door_palace_relation,nine_star_month_status,chart_concepts,
    lookup_concept,gather_chart_research_context
)
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.database import connect

def synthetic_source():
    lines=[""]*1261
    lines[0]="奇门预测符号的象数理含义"
    lines[500]="第五章 奇门预测的判断依据"
    for i,name in zip(range(223,242,2),"甲乙丙丁戊己庚辛壬癸"):
        lines[i-1]=f"{name}：合成语义说明"
    for i,name in zip(range(287,310,2),compiler.BRANCHES):
        lines[i-1]=f"{name}：合成地支说明"
    stem_pairs=[(a,b) for a in compiler.STEMS for b in compiler.STEMS]
    for n,(a,b) in enumerate(stem_pairs):
        lines[507+2*n-1]=f"样例天盘加地盘，即{a}加{b}，占位符。"
    door_pairs=[f"{a}加{b}" for a in compiler.DOORS for b in compiler.DOORS]
    door_stems=[f"{a}加{b}" for a in compiler.DOORS for b in compiler.STEMS
                if not (a=="休" and b=="癸")]
    door_stems.append("休加壬、癸")
    # Remove 休加壬 so its combined source line is unique.
    door_stems.remove("休加壬")
    self_all=door_pairs+door_stems
    assert len(self_all)==135
    for n,key in enumerate(self_all):
        lines[691+2*n-1]=f"{key}：模拟的组合说明。"
    for n in range(13):
        lines[987+7*n-1]=f"（{n+1}）吉格模拟条目{n+1}。"
    for n in range(27):
        lines[1093+6*n-1]=f"（{n+1}）凶格模拟条目{n+1}。"
    return "\n".join(lines)+"\n"

class ShenqiCh45Tests(unittest.TestCase):
    def test_reject_unsupported_chapter_format(self):
        with self.assertRaisesRegex(ValueError,"Unexpected edition"):
            compiler.parse_original("only a fragment")

    def test_exact_full_pair_coverage_in_synthetic_sample(self):
        rows=compiler.parse_original(synthetic_source())
        from collections import Counter
        c=Counter(x["kind"] for x in rows)
        self.assertEqual(c["stem_pair"],81)
        self.assertEqual(c["door_pair"],64)
        self.assertEqual(c["door_stem"],72)
        self.assertEqual(c["good_formation"],13)
        self.assertEqual(c["bad_formation"],27)
        self.assertEqual(c["symbol"],55)
        a=next(x for x in rows if x["concept_id"]=="door_over_stem:休:壬")
        b=next(x for x in rows if x["concept_id"]=="door_over_stem:休:癸")
        self.assertEqual(a["start"],b["start"])
        self.assertEqual(a["source_text"],b["source_text"])
        self.assertEqual(a["predicate"]["layer_binding"],"unresolved")

    def test_idempotent_private_sqlite_and_research_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            text=synthetic_source()
            input_file=root/"original.txt"
            input_file.write_text(text,encoding="utf-8")
            db=root/"local.sqlite3"
            digest=hashlib.sha256(input_file.read_bytes()).hexdigest()
            with patch.object(compiler,"SOURCE_SHA256",digest):
                first=compiler.ingest_local(db,input_file)
                second=compiler.ingest_local(db,input_file)
            self.assertEqual(first["total_entries"],second["total_entries"])
            self.assertEqual(first["approved"],0)
            self.assertEqual(first["historical_prediction_cases"],0)
            with connect(db) as c:
                self.assertEqual(c.execute("SELECT COUNT(*) FROM semantic_assertions").fetchone()[0],
                                 first["total_entries"])
                self.assertEqual(c.execute("SELECT COUNT(*) FROM sections").fetchone()[0],2)
                self.assertEqual(c.execute("SELECT COUNT(*) FROM cases").fetchone()[0],0)
                self.assertEqual(c.execute("SELECT COUNT(*) FROM rules WHERE status='approved'").fetchone()[0],0)
            look=lookup_concept(db,"heaven_over_earth:乙:丙")
            self.assertEqual(len(look),1)
            self.assertIsNone(look[0]["local_source_text"])
            self.assertEqual(look[0]["review_status"],"draft")
            self.assertEqual(len(lookup_concept(db,"door_over_stem:休:癸",include_original=True)),1)
            chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
            linked=gather_chart_research_context(db,chart)
            self.assertEqual(linked["status"],"draft_source_context_not_approved_divination")
            self.assertGreater(len(linked["matches"]),30)
            self.assertEqual(linked["school_id"],"shijia_zhuanpan")
            self.assertFalse(any("source_text" in str(i.get("evidence","")) for i in linked["matches"]))

    def test_refuse_wrong_source_hash_no_database_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"bad.txt"
            path.write_text(synthetic_source(),encoding="utf-8")
            db=Path(d)/"private.sqlite3"
            with self.assertRaisesRegex(ValueError,"Wrong chapter"):
                compiler.ingest_local(db,path)
            self.assertFalse(db.exists())

    def test_door_palance_element_categories_and_star_month(self):
        self.assertEqual(door_palace_relation("休门",9)["kind"],"迫")
        self.assertEqual(door_palace_relation("伤门",7)["kind"],"制")
        self.assertEqual(door_palace_relation("生门",2)["kind"],"比和")
        self.assertEqual(door_palace_relation("生门",9)["kind"],"义")
        self.assertEqual(door_palace_relation("景门",2)["kind"],"和")
        self.assertEqual(door_palace_relation("生门",5)["status"],"blocked_middle_palace")
        for element,expected in [("木","旺"),("水","相"),("金","废"),("火","休"),("土","囚")]:
            self.assertEqual(nine_star_month_status("天蓬星",element)["value"],expected)

    def test_chart_relation_uses_actual_carry_stems_for_two_stars(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        keys=[x["concept_id"] for x in chart_concepts(chart) if "concept_id" in x and x["palace"]==1]
        self.assertIn("heaven_over_earth:乙:丙",keys)
        self.assertIn("heaven_over_earth:庚:丙",keys)
        with self.assertRaises(ValueError):chart_concepts({"status":"invented"})

if __name__=="__main__":
    unittest.main()
