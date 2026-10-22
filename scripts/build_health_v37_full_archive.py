"""V3.7 append-only archive from verified V3.6 full 194 original case SQLite."""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_health_v37_user_20261022_noon import test_case,PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/065_health_full_81_pair_double_adverse_v37.sql"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def report(t):
    p=t["chart"]["palaces"]
    def cell(idx):
        q=p[str(idx)]
        names="、".join(z["star"]+"携"+z["carried_stem"] for z in q["heaven_stars"]) or "不设普通九星"
        return (q["gua"]+str(idx)+"宫 "+names+" 地"+q["earth_stem"]+" "+
                str(q["door"] or "不设普通八门")+" "+str(q["deity"] or "不设普通八神"))
    lines=["# V3.7 原样断案：丙午年 戊戌月 己巳日 庚午时",
        "","2026-10-22 12:00 EDT，寒露阴遁九局。按本人疾病轻重测试，日干己；出生年命未给，不虚构。",
        "","## 真实九宫", "",
        "| 巽四 | 离九 | 坤二 |","|---|---|---|",
        "| "+" | ".join(cell(i) for i in (4,9,2))+" |",
        "| "+" | ".join(cell(i) for i in (3,5,7))+" |",
        "| "+" | ".join(cell(i) for i in (8,1,6))+" |",
        "","## 原书81条有序组合中本盘实际9星携干的原始名称","",
        "| 所落宫及用神角色 | 有序组合 | 原书名称 | 传统条件 | 原文行 |",
        "|---|---|---|---|---|"]
    for q in t["actual_all_nine_source_pairs"]:
        lines.append("| "+"/".join(q["roles"])+" "+str(q["palace"])+" | "+q["pair_key"]+
           " | "+q["title"]+" | "+q["applicability"]+" | "+str(q["source_line"])+" |")
    lines.extend(["","## 双重制病、双重凶象的独立真实依据","",
       json.dumps(t["double_evidence"],ensure_ascii=False,indent=2),
       "","## V3.7 本时辰完整断词（原样）","",t["reading_text"],"",
       "原文sha256："+t["reading_sha256"],"",
       "古籍术数文化研究；不构成现代医学诊断、医药效果或生命危险的预测。"])
    return "\n".join(lines)+"\n"

def build(parent,output,seal,manifest,readout):
    parent,output,seal,manifest,readout=map(Path,(parent,output,seal,manifest,readout))
    packed=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,readout,packed)):
        raise ValueError("No immutable V3.7 artifact can be overwritten")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact parent V3.6 SHA mismatch")
    case=test_case(db_path=parent)
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as new:
        old.backup(new)
        new.executescript(MIG.read_text("utf8"))
        new.execute("PRAGMA foreign_keys=ON")
        with new:
            for name,count in [("cases",194),("sections",43),
              ("kaiwu_ordered_stem_pair_occurrences",81),
              ("health_v30_stem_pair_rules",42),("health_v30_composite_rule_index",17),
              ("health_v33_all_historical_health_replay",12),
              ("health_v34_role_and_condition_replay",12),
              ("health_v35_patient_first_replay",12),
              ("health_v36_source_horse_and_value_door",12)]:
                actual=new.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0]
                if actual!=count:raise ValueError("Lost original prior table "+name+" "+str(actual))
            if new.execute("SELECT count(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]!=2:
                raise ValueError("Original prior errors removed")
            new.execute("""INSERT INTO health_v37_ordered_81_pair_policy VALUES
              ('health_v37_full_81_original',
               'data/knowledge/kaiwu/analysis_judgment_ch04/ordered_stem_pairs.json',
               81,1,42,17,81,1,1,0)""")
            d=case["double_evidence"]
            new.execute("""INSERT INTO health_v37_user_noon_test VALUES
                ('user_2026_10_22_1200_EDT','2026-10-22T12:00:00-04:00',
                 'America/New_York','丙午','戊戌','己巳','庚午','寒露','yin',9,
                 'self',?,?,?,?,?,9,?,0,0,'pending')""",
                 (PARENT_SHA,int(d["double_control"]),
                  int(d["double_adverse_disease_growth"] or d["double_adverse_patient_nourishes"]),
                  int(d["double_adverse_patient_formation"]),
                  case["traditional_v37_verdict"],case["reading_sha256"]))
            new.execute("""INSERT INTO health_v37_full_archive_audit VALUES
                ('v3.7',?,194,43,2,12,1,1,1,0)""",(PARENT_SHA,))
        preserve(old,new)
        if new.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("Bad SQLite")
        if new.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("Foreign key error")
        new.execute("VACUUM");new.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(case,ensure_ascii=False,indent=2)+"\n","utf8")
    readout.parent.mkdir(parents=True,exist_ok=True)
    readout.write_text(report(case),"utf8")
    packed.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    m={"schema":"wengua_health_v37_user_noon_all81_two_sided_full_archive",
       "exact_v36_parent_sha256":PARENT_SHA,
       "sqlite_sha256":sha(output),"sqlite_size":output.stat().st_size,
       "xz_sha256":sha(packed),"test_case_sha256":sha(seal),
       "readable_report_sha256":sha(readout),
       "test_reading_sha256":case["reading_sha256"],
       "original_books_events":194,"original_source_sections":43,
       "source_book_ordered_pair_rows":81,"health_supplement_pair_rows":42,
       "health_composite_rows":17,"prior_error_records":2,
       "prior_12_source_case_histories_unchanged":True,
       "unique_new_user_question_not_an_ancient_book_event":True,
       "tested_pillars":"丙午年戊戌月己巳日庚午时",
       "source_bureau":"寒露阴遁九局",
       "traditional_illness_symbolic_verdict":case["traditional_v37_verdict"],
       "actual_compound_adverse":case["double_evidence"]["double_adverse_patient_formation"],
       "historical_outcomes_not_used":True,
       "not_medically_validated":True,
       "user_approval":"pending"}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n","utf8")
    return m

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for v in ("parent","output","seal","manifest","readout"):p.add_argument("--"+v,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest,a.readout),ensure_ascii=False,indent=2))
