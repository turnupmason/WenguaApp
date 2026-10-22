"""Immutable V3.9 full-source 194 original events and 3 new audience-safe readings.

Parent exact V3.7; no rewrite/delete of original results, failed research
experiments or earlier V3.7 user's question. New user and two reproducibly
seeded old family samples are supplementary evaluations, not book cases.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_health_v39_fixed_cases import evaluate,PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/067_health_concise_three_user_readings_v39.sql"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _customer_doc(batch):
    intro=[
       "# 三份疾病轻重固定断词（V3.9 专业审核稿）","",
       "以下为奇门古籍象意研究，不属于实际疾病诊断、治疗指导或康复概率。"
       "所有时间均以原占时起盘；按问事人物选择用神。","",
       "三份断词是原样程序输出，来源行号及资料校验信息仅在内部封存中保留，不出现在客户断词。",""
    ]
    for idx,row in enumerate(batch["records"]):
        if idx==0:subject="丙午年 戊戌月 己巳日 庚午时，本人问健康"
        elif idx==1:subject="1995年2月19日 癸巳时，代问弟弟健康"
        else:subject="1996年11月2日 庚申时，本人问健康"
        intro.extend(["## "+str(idx+1)+". "+subject,"",
           row["reading_text"],""])
    return "\n".join(intro).rstrip()+"\n"

def build(parent,output,seal,manifest,readout):
    parent,output,seal,manifest,readout=map(Path,(parent,output,seal,manifest,readout))
    xz=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,readout,xz)):
        raise ValueError("Previous V3.9 immutable artifacts exist; cannot overwrite")
    if sha(parent)!=PARENT_SHA:raise ValueError("Full V3.8 exact parent required")
    results=evaluate(db_path=parent)
    if len(results["records"])!=3 or len(results["randomly_selected_family_ids"])!=2:
        raise ValueError("No 2 independently drawn original first-question cases")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        preserved={
           "cases":194,"sections":43,"kaiwu_ordered_stem_pair_occurrences":81,
           "health_v30_stem_pair_rules":42,"health_v30_composite_rule_index":17,
           "health_v33_all_historical_health_replay":12,"health_v34_role_and_condition_replay":12,
           "health_v35_patient_first_replay":12,"health_v36_source_horse_and_value_door":12,
           "health_v37_user_noon_test":1,"health_v37_ordered_81_pair_policy":1,
           "health_v38_case_readouts":3,"health_v38_latest_full_archive":1
        }
        with db:
            for table,n in preserved.items():
                actual=db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0]
                if actual!=n:raise ValueError("Original archived rows changed: "+table)
            bad=db.execute("""SELECT count(*) FROM marriage_v16_post_inference_labels
                              WHERE matches_initial_book_retrospective_result=0""").fetchone()[0]
            if bad!=2:raise ValueError("Prior development failures must remain, exact count 2")
            for i,row in enumerate(results["records"]):
                f=row["illness_stem_tomb_absence"]
                db.execute("""INSERT INTO health_v39_concise_user_readings VALUES
                   (?,?,?,?,?,?,?,1,0,0,?,'pending')""",
                   (row["case_id"],"user_noon" if i==0 else "pre_disclosure_book",
                    row["four_pillars"]["day"],row["four_pillars"]["hour"],
                    int(f["tomb_branch_in_illness_palace"]),
                    int(f["extinct_branch_in_illness_palace"]),
                    int(f["void_in_illness_palace"]),row["readout_sha256"]))
            db.execute("""INSERT INTO health_v39_appendonly_full_audit VALUES
              ('v3.9',?,194,43,81,42,17,2,2,3,1,0)""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite whole DB integrity failure")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite foreign keys invalid")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n","utf8")
    readout.parent.mkdir(parents=True,exist_ok=True)
    readout.write_text(_customer_doc(results),"utf8")
    xz.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    m={"schema":"wengua_v39_three_source_readings_and_internal_only_provenance",
       "full_sqlite_sha256":sha(output),"full_sqlite_size":output.stat().st_size,
       "full_sqlite_xz_sha256":sha(xz),
       "exact_parent_full_v38_sha256":PARENT_SHA,
       "full_three_predictions_sha256":sha(seal),
       "client_three_readings_sha256":sha(readout),
       "seed_input":results["rng_seed_input"],
       "random_selection_seed_sha256":results["rng_seed_sha256"],
       "random_original_source_family_ids":results["randomly_selected_family_ids"],
       "source_194_and_43_unchanged":True,
       "source_full81_user42_composites17_unchanged":True,
       "all_previous_sealed_outputs_and_failures_unchanged":True,
       "new_user_question_is_not_historical_case":True,
       "all_three_actual_temporal_charts_source_based":True,
       "client_does_not_see_book_line_ids":True,
       "actual_medical_predictiveness_claim":False,
       "further_professional_acceptance_before_ui_or_release":"pending",
       "template_file":"data/knowledge/phrase_library/health_v39/severity_customer_template.json"}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n","utf8")
    return m

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("parent","output","seal","manifest","readout"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest,a.readout),ensure_ascii=False,indent=2))
