"""V4.2 exact FULL parent 194 event source DB + 3 immutable user-readouts + 2 extra.

The new snapshot adds verified 120 stem-stage facts, exact unchanged V3.9
customer texts, V4.2 six-budget score/conditional scenarios & 5 actual charts.
No update to original source or prior V4.1 numeric failure records.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_health_v42_unified_five_actual_casts import evaluate,PARENT_SHA
from src.wengua.health_severity_v42_integrated import source_full12,MODULES,STAGE,POLICY
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/070_health_v42_unified_v39_full12_sixmodule.sql"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(item):return hashlib.sha256(json.dumps(item,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")).hexdigest()

def customer_report(data):
    lines=["# V4.2｜同一张原始盘，保留完整V3.9断词并追加六模块象意评分","",
      "本版使用古籍方法与规则的**实验分数**，绝非真实生命体征指数、诊断、病情概率、住院或用药建议。",
      "所有宫位、干支、八门、九星、八神、月令、十二长生、旬空、刑冲墓马由程序按真实盘核算。",
      "如果问题未告知新病久病，系统分别给出这两种假设的分数；**不伪造病史**。没有出生年命也不臆造。",
      "所列旧古籍样本不使用作者结局作为输入，不能当独立现实医学盲测。","",
      "## 五张盘数值总览","",
      "| 问题 | 已知条件分 | 假设新病 | 假设久病 | V3.9文本是否原样 |",
      "|---|---:|---:|---:|---|"]
    for x in data["records"]:
        s=x["symbolic_scoring"]
        c=s["conditional_scenarios"]
        lines.append("| "+x["family_id"]+" | "+
            str(s["observed_or_unspecified_nominal"]["score"])+" | "+
            str(c.get("new",c.get("unprovided")))+" | "+
            str(c.get("chronic",c.get("unprovided")))+" | "+
            ("是" if x["old_v39_reading_byte_identical"] else "否")+" |")
    for x in data["records"]:
        sections=x["symbolic_scoring"]["observed_or_unspecified_nominal"]["six_modules"]
        p=x["stage_actor_audit"]["patient"]["all_actual_branch_stages"]
        d=x["stage_actor_audit"]["tianrui_heaven"]["all_actual_branch_stages"]
        lines+=["","## "+x["family_id"],"",
          "实际起局四柱："+"/".join(x["four_pillars"][k] for k in ("year","month","day","hour"))+"。",
          "患者实际十二长生："+ "、".join(v["branch"]+v["stage"] for v in p)+"；"+
          "病宫天芮携干实际十二长生："+ "、".join(v["branch"]+v["stage"] for v in d)+"。","",
          "| 共享规则模块 | 模块正负预算 | 本盘已用分 |",
          "|---|---:|---:|"]
        for z in sections:
            lines.append("| "+z["name"]+" | ±"+str(z["budget"])+" | "+
                         ("+" if z["applied_signed_score"]>=0 else "")+
                         str(z["applied_signed_score"])+" |")
        lines+=["","### V3.9 原样断词与新增V4.2分数","",x["V42_integrated_customer_text"],""]
    lines+=["## 严格限定","",
       "完整历史库194原书事件、43章节、81原书有序组合、旧42条疾病专题、17复合条目和老失败均不可被覆盖。",
       "V4.0、V4.1的高分饱和/已知不利判断得90分失误原样保留。本版重设中性基准50与六模块预算，不保证古籍判断一致率，更不保证实际医学准确。",
       "所有内部来源行号/哈希留在数据库、源账本和加减分 JSON；用户断词不含技术审计来源。",
       "候选权重和这个总分仍须用户单独审核，未经批准不加入iOS客户界面。"]
    return "\n".join(lines)+"\n"

def build(parent,output,seal,manifest,report_path):
    parent,output,seal,manifest,report_path=map(Path,(parent,output,seal,manifest,report_path))
    compressed=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,report_path,compressed)):
        raise ValueError("Existing V4.2 immutable file; never overwrite")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact V4.1 FULL parent required")
    scores=evaluate(parent)
    if len(scores["records"])!=5 or len({r["family_id"] for r in scores["records"]})!=5:
        raise ValueError("Source 5-case identity changed")
    stems=source_full12()
    if len(stems)!=10:raise ValueError("No full ten stems")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        must={
          "cases":194,"sections":43,"kaiwu_ordered_stem_pair_occurrences":81,
          "health_v30_stem_pair_rules":42,"health_v30_composite_rule_index":17,
          "health_v33_all_historical_health_replay":12,
          "health_v34_role_and_condition_replay":12,
          "health_v35_patient_first_replay":12,
          "health_v36_source_horse_and_value_door":12,
          "health_v37_user_noon_test":1,
          "health_v38_case_readouts":3,
          "health_v39_concise_user_readings":3,
          "health_v40_three_symbolic_score_trials":3,
          "health_v41_candidate_ordered_pair_weights":81,
          "health_v41_real_chart_81_pair_checks":27,
          "health_v41_scoring_3_fixed_cases":3}
        with db:
            for name,number in must.items():
                if db.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0]!=number:
                    raise ValueError("Old original source count changed "+name)
            failed=db.execute("""SELECT count(*) FROM marriage_v16_post_inference_labels
               WHERE matches_initial_book_retrospective_result=0""").fetchone()[0]
            if failed!=2:raise ValueError("Original two failed developer predictions lost")
            n=0
            for stem,ref in stems.items():
                for stage,branch in ref["stage_to_branch"].items():
                    db.execute("""INSERT INTO health_v42_book_anchored_twelve_stages VALUES
                      (?,?,?,?,?,?)""",
                      (stem,stage,branch,int(stage in ref["source_existing_5_anchor_branches"]),
                       ref["polarity"],ref["source_line_start"]))
                    n+=1
            if n!=120:raise ValueError("Expected ten-times-twelve stage table")
            ledgers=0
            for row in scores["records"]:
                z=row["symbolic_scoring"]
                nominal=z["observed_or_unspecified_nominal"]
                db.execute("""INSERT INTO health_v42_unified_five_qualitative_numeric VALUES
                  (?,?,?,?,?,?,?,?,?,?,1,0,0)""",
                  (row["family_id"],row["four_pillars"]["day"],row["four_pillars"]["hour"],
                   row["original_question"]["relationship"],row["original_v39_reading_sha256"],
                   row["new_integrated_reading_sha256"],1,
                   nominal["score"],z["scenario_range"][0],z["scenario_range"][1]))
                for module in nominal["six_modules"]:
                    db.execute("""INSERT INTO health_v42_six_module_ledger VALUES
                      (?,?,?,?,?,?,?)""",
                      (row["family_id"],module["name"],module["budget"],
                       module["raw_rule_sum"],module["applied_signed_score"],
                       len(module["all_scored_facts"]),digest(module)))
                    ledgers+=1
            if ledgers!=30:raise ValueError("Expected 5*6 module ledgers")
            db.execute("""INSERT INTO health_v42_appendonly_full_original_retention VALUES
              ('v4.2',?,194,43,81,42,17,2,3,2,120,30,0)""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite orphaned reference")
        db.execute("VACUUM")
        db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(scores,ensure_ascii=False,indent=2)+"\n","utf8")
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(customer_report(scores),"utf8")
    compressed.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    receipt={
      "schema":"wengua_v42_unified_v39_express_reading_and_book_anchor_120_score_full",
      "full_parent_v41_sha256":PARENT_SHA,
      "complete_v42_sqlite_sha256":sha(output),
      "complete_v42_sqlite_bytes":output.stat().st_size,
      "compressed_complete_v42_sqlite_sha256":sha(compressed),
      "sealed_five_real_question_sha256":sha(seal),
      "five_integrated_human_readings_sha256":sha(report_path),
      "full12_10stems5sourceanchors_sha256":sha(STAGE),
      "six_budget_policy_sha256":sha(POLICY),
      "all_old_194_and_43_and_81_42_17_preserved":True,
      "old_developer_failure_count":2,
      "extra_health_first_question_families":2,
      "stage_count_computed_from_verified_anchors":120,
      "actual_six_budget_snapshots":30,
      "all_first_3_v39_user_readings_unchanged":True,
      "user_current_score_approval":False,
      "medical_risk_or_probability":False,
      "results":[{"id":r["family_id"],
        "score":r["symbolic_scoring"]["observed_or_unspecified_nominal"]["score"],
        "scenario_low_high":r["symbolic_scoring"]["scenario_range"],
        "v39_sha256":r["original_v39_reading_sha256"],
        "v39_verbatim_preserved":r["old_v39_reading_byte_identical"]}
        for r in scores["records"]]}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n","utf8")
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("parent","output","seal","manifest","report"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest,a.report),ensure_ascii=False,indent=2))
