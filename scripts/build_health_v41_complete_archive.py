"""V4.1 append-only full 194-event SQLite derived ONLY from exact V4.0 parent.

Persist all 81 user candidate weights, separate 81 author book source hashes,
42 distinct illness supplement entries left unchanged, 3 x 9 actual role
gates and full candidate-vs-source disagreement ledger. Past failures kept.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_health_v41_source_gated_3_cases import evaluate,PARENT_SHA
from src.wengua.health_symbolic_score_v41 import all81_proposed
from src.wengua.health_severity_v37 import load_81_book_pairs

ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/069_health_v41_original_book_81_user_weights_source_gated.sql"
WEIGHTS=ROOT/"data/knowledge/score_models/health_severity_v41/ordered81_user_weight_candidates.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def normalized_sha(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")).hexdigest()

def report(result):
    lines=["# V4.1｜81组有序天地盘组合与测病原书条件的候选评分实验","",
           "这是传统古籍数值象意研究，不代表真实生命体征、医疗诊断、复原概率、任何临床事件或死亡风险。",
           "用户新稿列出了9×9=81种有序天干对；项目旧病事专项目录另有42条。二者并行保存而不覆盖。",
           "书中明示的疾病例外优先于谋事通用吉格，不能对病宫凶格统一做符号翻转。",
           "仅原书明示病事且角色对应、用户分值方向一致、实际条件完整的组合可作为试验积分。","",
           "## 原文优先的具体反例","",
           "- 戊加丙、丙加戊：虽然是谋事两大吉格，但原书明示测病不吉，故用户候选+20与书中病事方向相冲突，此阶段不记+20。",
           "- 丙加辛：原书为月奇相合，写明测人疾病也不凶；新病+10是候选，久病-15与已知原句冲突，暂不采纳久病扣分。",
           "- 己加癸：原书称地刑玄武，明确有疾病不利象；属于患者宫时用户候选-20可作为独立负面象，不能在病宫倒置成+20。",
           "- 戊加庚：值符飞宫，原书测病也主凶，但在无关宫位不自动扣。",
           "- 丁加壬：原书奇仪相合、一般谋事有成，用户表给-12；缺疾病专项前不得将该扣分硬套给医药宫。",
           "",
           "## 同一三张已固定原时辰的原样差值","",
           "| 原问题 | V4.0原始分 | V4.1原始分 | V4.1显示(0–100) | 真正计分的原书病事配对 |",
           "|---|---:|---:|---:|---|"]
    for r in result["records"]:
        s=r["score"]
        active=s["book_pair_source_audit"]["eligible_book_explicit_ledger"]
        terms="；".join(x["source_pair_key"]+"("+str(x["points"])+")" for x in active) or "无，保留为待核条件"
        lines.append("| "+r["family_id"]+" | "+str(s["previous_v40_raw"])+" | "+
            str(s["revised_raw_score"])+" | "+str(s["revised_display_score"])+" | "+terms+" |")
    lines+=["","## 为什么未把81个格局全部直接加减分","",
            "每一张盘虽然实际计算九个天盘携干与地盘的有序关系，但不少原文只讲婚姻、官司、求财、主客或一般谋事，未经核实无法推出问病的独立分值。",
            "格局出现在患者宫、天芮病宫、天心/乙医药宫、时干宫或完全无关的宫位时不能套用同一条权重。",
            "同宫天禽的第二个携干保留为反证但不能把同一个病宫投票两次。",
            "已知原书结局不参与本轮预测前生成，旧案例只能作为机制回放而非新独立盲测。",
            "扣分和加分不构成统计验证，50/80/90等分段不对应任何真实病情、寿命或临床行动。",
            "完整81组和本盘所有九项已核证源文件/状态留在内部 JSON 与 SQLite，不在客户段落展示原书行号、数据库表名或SHA。"]
    return "\n".join(lines)+"\n"

def build(parent,output,seal,manifest,readout):
    parent,output,seal,manifest,readout=map(Path,(parent,output,seal,manifest,readout))
    compressed=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,readout,compressed)):
        raise ValueError("Never overwrite immutable prior artifact or half archive")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("Must be exact full V4.0 parent, not old source subset")
    payload=evaluate(parent)
    cfg,proposals=all81_proposed()
    originals=load_81_book_pairs()
    if len(payload["records"])!=3 or len(proposals)!=81:
        raise ValueError("Missing 3 exact samples or 81 ordered candidate names/weights")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        must={"cases":194,"sections":43,
              "kaiwu_ordered_stem_pair_occurrences":81,
              "health_v30_stem_pair_rules":42,"health_v30_composite_rule_index":17,
              "health_v33_all_historical_health_replay":12,
              "health_v34_role_and_condition_replay":12,
              "health_v35_patient_first_replay":12,
              "health_v36_source_horse_and_value_door":12,
              "health_v37_user_noon_test":1,
              "health_v38_case_readouts":3,
              "health_v39_concise_user_readings":3,
              "health_v40_three_symbolic_score_trials":3,
              "health_v40_symbolic_score_model":1}
        with db:
            for table,count in must.items():
                n=db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0]
                if n!=count:raise ValueError("Original source was altered: "+table)
            bad=db.execute("""SELECT count(*) FROM marriage_v16_post_inference_labels
                  WHERE matches_initial_book_retrospective_result=0""").fetchone()[0]
            if bad!=2:raise ValueError("Prior failures deleted")
            for name,row in sorted(proposals.items()):
                original=originals[name]
                db.execute("""INSERT INTO health_v41_candidate_ordered_pair_weights VALUES
                  (?,?,?,?,?,?,?,?,0)""",
                  (name,row["top"],row["bottom"],row["user_alias"],
                   row["proposed_points"],json.dumps(row.get("duration_points"),ensure_ascii=False),
                   original["excerpt_sha256"],original["source_line"],
                   "candidate_not_approved"))
            count=0
            for r in payload["records"]:
                s=r["score"]
                report=s["book_pair_source_audit"]
                for matched in report["matched_real_star_pairs"]:
                    db.execute("""INSERT INTO health_v41_real_chart_81_pair_checks
                      VALUES (?,?,?,?,?,?,?,?,?)""",
                      (r["family_id"],matched["matched_actual_star"],
                       matched["matched_actual_palace"],matched["ordered_pair"],
                       matched["actual_role"],matched["original_book_health_semantics"],
                       matched["match_status"],matched["applied_delta"],
                       matched["source_sha256_internal_only"]))
                    count+=1
                db.execute("""INSERT INTO health_v41_scoring_3_fixed_cases VALUES
                      (?,?,?,?,?,1,0,0)""",
                   (r["family_id"],s["previous_v40_raw"],
                    s["revised_raw_score"],s["revised_display_score"],
                    normalized_sha(s)))
            if count!=27:raise ValueError("Expected 3x9 actual source pairs")
            db.execute("""INSERT INTO health_v41_source_gate_archive_policy VALUES
              ('v4.1',?,194,43,81,42,17,2,81,27,1)""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite foreign key failure")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n","utf8")
    readout.parent.mkdir(parents=True,exist_ok=True)
    readout.write_text(report(payload),"utf8")
    compressed.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    receipt={"schema":"wengua_v41_81_user_candidacy_and_author_illness_gating_appendonly",
        "exact_v40_parent_sha256":PARENT_SHA,
        "complete_v41_sqlite_sha256":sha(output),
        "complete_v41_sqlite_bytes":output.stat().st_size,
        "complete_v41_xz_sha256":sha(compressed),
        "three_case_sealed_sha256":sha(seal),
        "readable_report_sha256":sha(readout),
        "user_candidate_matrix_sha256":sha(WEIGHTS),
        "source_cases_unchanged":194,"original_source_sections_unchanged":43,
        "book_all_ordered_stem_combos":81,"user_disease_supplement_combos":42,
        "composite_condition_rows_retained":17,"prior_dev_fails_retained":2,
        "original_v39_and_v40_user_predictions_untouched":True,
        "all81_user_weights_are_UNAPPROVED":True,
        "no_clinical_risk_claim":True,
        "book_outcome_not_used":True,
        "scores":[{"id":x["family_id"],"previous_v40_raw":x["score"]["previous_v40_raw"],
                   "new_v41_raw":x["score"]["revised_raw_score"],
                   "v41_display":x["score"]["revised_display_score"],
                   "applied_pair_count":len(x["score"]["book_pair_source_audit"]["eligible_book_explicit_ledger"])}
                   for x in payload["records"]]}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n","utf8")
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("parent","output","seal","manifest","readout"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest,a.readout),ensure_ascii=False,indent=2))
