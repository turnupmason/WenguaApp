"""Append research-only V4 symbolic scores to exact full V3.9 case database.

Seals THREE score ledgers, without touching immutable V3.9 audience template,
its source, 194 book cases, 43 chapters or prior failed evaluation records.
Scores are NOT probabilities or validated health assessments.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_health_v40_score_three_cases import evaluate,PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/068_health_v40_symbolic_score_prototype.sql"
CONFIG=ROOT/"data/knowledge/score_models/health_severity_v40/weights_draft.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row_sha(row):
    content=json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(content.encode("utf8")).hexdigest()

def report(data):
    rows=["# V4.0 实验性奇门病势象意评分（非健康指数/概率）","",
    "来源是用户提出的100分起始加减分方案和另列的病人、病宫、乾坤、旬空、刑墓、驿马冲墓研究候选。",
    "**不能把分值解释成真实病情严重程度、病愈概率、死亡风险或医药疗效。**",
    "既有 V3.9 文字未修改。这三份是固定旧问题的新模型回放，绝非新独立盲测。","",
    "每个总分保留未截断分和0—100显示分。分数超过100也不会让健康优于100%，它只暴露算分模型尚未校准的缺陷。",""]
    for index,r in enumerate(data["records"]):
        x=r["score"]
        rows.extend(["## "+str(index+1)+". "+r["family_id"],"",
          "四柱："+"/".join(r["pillars"][k] for k in ("year","month","day","hour")),
          "；患者"+str(x["patient_palace"])+"宫，天芮病宫"+str(x["illness_palace"])+"宫。",
          "原始100＋调整"+str(x["signed_delta_sum"])+"＝"+str(x["raw_score"])+
          "；区间显示："+str(x["display_score_0_100"])+"（仅象意分，非百分比）。","",
          "| 项目 | 分值 | 真实宫位及规则 |",
          "|---|---:|---|"])
        for z in x["ledger"]:
            rows.append("| "+z["id"]+" | "+("+" if z["points"]>0 else "")+str(z["points"])+" | "+z["why"]+" |")
        rows+=["","缺失或不能自动加减分的条件："]
        for z in x["unscored_unknowns"]:
            rows.append("- "+z["id"]+"："+z["reason"])
        t=x["tomb_and_horse"]
        rows+=["","墓库与马星：患者宫"+str(t["patient_palace"])+"，"+t["stem"]+
             "墓支"+t["tomb_branch"]+"；"+t["name"]+
             "宫位匹配="+str(t["in_tomb_palace"])+"，时支驿马在"+t["horse_branch"]+
             "（"+str(t["horse_palace"])+"宫），是否正对="+str(t["horse_spatial_opposite"])+
             "，真正四柱地支冲墓候选="+str(t["direct_clash_in_pillars"])+
             "。开墓判别="+t["opening_mode"]+"。",""]
    rows+=["## 研究限制","",
     "用户所提分值、交互加减权重和马星对宫开墓的退款比例都未用独立盲测校准。",
     "大部分古籍案例有已知结局，不能直接用结局调参后当验证。",
     "确定新旧病、病人性别、实际人物年命等之前，对应项目保持未评分。",
     "原书组合全量81条、疾病补充42条、复合17条仍必须保留出处并逐条判断条件；"+
     "这里不是声称所有项目可完全数值化。"]
    return "\n".join(rows)+"\n"

def build(parent,output,seal,manifest,readout):
    parent,output,seal,manifest,readout=map(Path,(parent,output,seal,manifest,readout))
    packed=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,readout,packed)):
        raise ValueError("Immutable V4 output already exists, don't overwrite")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("Input MUST be exact complete source V3.9")
    data=evaluate(parent)
    if len(data["records"])!=3 or len({z["family_id"] for z in data["records"]})!=3:
        raise ValueError("Must retain exact three existing source question inputs")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        preserved={"cases":194,"sections":43,"kaiwu_ordered_stem_pair_occurrences":81,
          "health_v30_stem_pair_rules":42,"health_v30_composite_rule_index":17,
          "health_v33_all_historical_health_replay":12,
          "health_v34_role_and_condition_replay":12,
          "health_v35_patient_first_replay":12,
          "health_v36_source_horse_and_value_door":12,
          "health_v37_user_noon_test":1,
          "health_v38_case_readouts":3,
          "health_v39_concise_user_readings":3}
        with db:
            for name,expected in preserved.items():
                number=db.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0]
                if number!=expected:raise ValueError("Preserved source count changed "+name)
            bad=db.execute("""SELECT count(*) FROM marriage_v16_post_inference_labels
                WHERE matches_initial_book_retrospective_result=0""").fetchone()[0]
            if bad!=2:raise ValueError("Two old failed forecasts must remain")
            db.execute("""INSERT INTO health_v40_symbolic_score_model VALUES
              ('v4.0-experimental-1',?,'research_draft_unapproved',100,0,0,194,43,81,42,17,1)""",
              (PARENT_SHA,))
            for i,r in enumerate(data["records"]):
                sc=r["score"]
                db.execute("""INSERT INTO health_v40_three_symbolic_score_trials VALUES
                     (?,?,?,?,?,?,?,0,0)""",
                   (r["family_id"],"user_new" if i==0 else "older_book_first_question",
                    sc["signed_delta_sum"],sc["raw_score"],sc["display_score_0_100"],
                    row_sha(sc),len(sc["unscored_unknowns"])))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("Bad V4 SQLite integrity")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign key integrity fail")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n","utf8")
    readout.parent.mkdir(parents=True,exist_ok=True)
    readout.write_text(report(data),"utf8")
    packed.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    receipt={"schema":"wengua_health_v40_nonclinical_symbolic_score_archive",
      "parent_complete_v39_sha256":PARENT_SHA,
      "new_complete_v40_sha256":sha(output),"new_complete_v40_bytes":output.stat().st_size,
      "new_complete_v40_xz_sha256":sha(packed),
      "sealed_three_score_ledgers_sha256":sha(seal),
      "score_report_sha256":sha(readout),
      "weight_config_sha256":sha(CONFIG),
      "book_cases_original":194,"source_chapters_original":43,
      "book_ordered_pairs_original":81,"supplement_pairs_original":42,
      "composite_catalog_original":17,"old_known_errors_preserved":2,
      "latest_user_acceptance_of_score_weights":False,
      "medical_probability_or_actual_health_prediction":False,
      "v39_staged_baseline_unchanged":True,
      "score_model_is_unvalidated_prototype":True,
      "raw_scores_not_same_as_probabilities":True,
      "three_scores":[{"case":x["family_id"],
          "raw":x["score"]["raw_score"],"display":x["score"]["display_score_0_100"]}
          for x in data["records"]]}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n","utf8")
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("parent","output","seal","manifest","readout"):p.add_argument("--"+x,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest,a.readout),ensure_ascii=False,indent=2))
