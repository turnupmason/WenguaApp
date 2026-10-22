"""Append only V3.9.1 ACTIVE TEXT to complete immutable V4.2 history.

Prior numeric experiments are preserved for audit but DEACTIVATED in the
source-to-reader production path. These 4 simulated self-questions are
not added to the 194 book cases or claims of personal health facts.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_health_v391_four_seeded_real_times import evaluate,PARENT_SHA
from src.wengua.health_lifecycle_v391 import source_full12
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/071_health_v391_active_source12_without_scores.sql"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v391/severity_text_full12_template.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_report(payload):
    text=["# V3.9.1｜疾病轻重：V3.9完整断词＋十二长生（无分数）","",
      "模板已从真实四柱自动起盘，11个固定段落中直接补充患者、天芮、天心、乙奇、时干的十二长生。",
      "全部时辰是**固定随机种子生成的四份模拟本人问身体**；真实问事者的生病历史、年命、病程未提供，不预设。",
      "所有原书的81组有序组合、42条疾病增补、17复合条件继续按原源规则推断；不输出任何数字打分或医学概率。",
      "**以下为待用户审查的完整断词，不是现实疾病诊断、治疗预后或医疗建议。**","",
      "## 四个固定随机时辰"]
    for i,item in enumerate(payload["samples"],1):
        p=item["four_pillars"]
        life=item["book_verifiable_chart_facts"]
        pt=life["patient"]
        il=life["illness_tianrui_heaven"]
        stage=lambda a:"、".join(y["branch"]+y["stage"] for y in a["actual_stage_facts"])
        text+=["","### "+str(i)+". "+item["local_datetime"]+"（"+item["timezone"]+"）","",
          "四柱：**"+"、".join(p[k] for k in ("year","month","day","hour"))+"**；节气："+item["solar_term"]+
          "；"+("阴遁" if item["bureau"]["dun"]=="yin" else "阳遁")+str(item["bureau"]["ju"])+"局。","",
          "患者用干"+pt["stem"]+"落"+str(pt["palace"])+"宫，十二长生："+stage(pt)+"；"+
          "病宫天芮所携"+il["stem"]+"落"+str(il["palace"])+"宫，十二长生："+stage(il)+"。","",
          item["v391_customer_reading_text"],"","---"]
    text+=["","## 交付与状态","",
      "V3.9 源模板和原三例封存完全不改；新V3.9.1只追加四段十二长生事实。",
      "不以这四份随机假设案例替代书籍真实问事案例，也不把它们当作四个医学实验。",
      "待用户逐条审阅合格后，才能生成USER_APPROVED正式模板封装；此文件当前是待审稿。"]
    return "\n".join(text)+"\n"

def build(parent,output,seal,manifest,readout):
    parent,output,seal,manifest,readout=map(Path,(parent,output,seal,manifest,readout))
    packed=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,readout,packed)):
        raise ValueError("Cannot overwrite prior version or incomplete snapshot")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact full V4.2 latest parent required")
    payload=evaluate(parent)
    book=source_full12()
    if len(book)!=10 or len(payload["samples"])!=4:
        raise ValueError("Missing entire verified source lifecycle or four real hour samples")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        unchanged={
          "cases":194,"sections":43,
          "kaiwu_ordered_stem_pair_occurrences":81,
          "health_v30_stem_pair_rules":42,
          "health_v30_composite_rule_index":17,
          "health_v37_user_noon_test":1,
          "health_v38_case_readouts":3,
          "health_v39_concise_user_readings":3,
          "health_v40_three_symbolic_score_trials":3,
          "health_v41_candidate_ordered_pair_weights":81,
          "health_v41_real_chart_81_pair_checks":27,
          "health_v42_book_anchored_twelve_stages":120,
          "health_v42_unified_five_qualitative_numeric":5}
        with db:
            for name,n in unchanged.items():
                v=db.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0]
                if v!=n:raise ValueError("Old complete source DB changed "+name)
            errors=db.execute("""SELECT count(*) FROM marriage_v16_post_inference_labels
                WHERE matches_initial_book_retrospective_result=0""").fetchone()[0]
            if errors!=2:raise ValueError("Old failed experiments must not be discarded")
            db.execute("""INSERT INTO health_v391_active_narrative_policy VALUES
              ('v3.9.1',?,1,1,1,194,43,81,42,17,2,120,4,0)""",(PARENT_SHA,))
            for x in payload["samples"]:
                p=x["four_pillars"];roles=x["book_verifiable_chart_facts"]
                db.execute("""INSERT INTO health_v391_random_hour_narratives VALUES
                  (?,?,?,?,?,?,?,?,?,?,?,0,0,'pending_user_review')""",
                  (x["case_id"],x["local_datetime"],p["year"],p["month"],p["day"],p["hour"],
                   x["solar_term"],"self",roles["patient"]["palace"],roles["illness_tianrui_heaven"]["palace"],
                   x["original_v39_reading_sha256"],x["v391_customer_reading_sha256"]))
                for label,a in [("patient",roles["patient"]),("illness",roles["illness_tianrui_heaven"]),
                      ("doctor",roles["doctor_tianxin_heaven"]),("yi",roles["medicine_yi"]),("hour",roles["hour_event"])]:
                    db.execute("""INSERT INTO health_v391_actual_role_lifecycle VALUES
                      (?,?,?,?,?,1)""",(x["case_id"],label,a["stem"],a["palace"],
                          json.dumps(a["actual_stage_facts"],ensure_ascii=False)))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("New score-free SQLite integrity failure")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("New SQLite foreign keys are invalid")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n","utf8")
    readout.parent.mkdir(parents=True,exist_ok=True)
    readout.write_text(write_report(payload),"utf8")
    packed.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    receipt={
       "schema":"wengua_v391_no_scores_true_solar_random_four_full194",
       "exact_full_parent_v42_sha256":PARENT_SHA,
       "new_complete_v391_sqlite_sha256":sha(output),
       "new_complete_v391_sqlite_bytes":output.stat().st_size,
       "new_complete_v391_sqlite_xz_sha256":sha(packed),
       "four_actual_cast_source_audit_sha256":sha(seal),
       "customer_four_full_v391_readings_sha256":sha(readout),
       "score_free_original_text_template_sha256":sha(TEMPLATE),
       "source_original_book_cases":194,"source_original_chapters":43,
       "original_author_ordered_stem_pairs":81,
       "old_illness_supplement_pairs":42,
       "old_composites":17,
       "retained_failed_historical_model_outputs":2,
       "retained_all_deactivated_score_model_history":True,
       "new_active_v391_has_no_score_or_probability":True,
       "stage_ten_stems_twelve_stages_verified":120,
       "four_synthetic_unanswered_real_hour_astro_casts":4,
       "random_seed_sha256":payload["frozen_seed_sha256"],
       "random_sample_hours":payload["four_selection_local_isos"],
       "user_has_approved_final_packaging":False}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n","utf8")
    return receipt

if __name__=="__main__":
    args=argparse.ArgumentParser()
    for k in ("parent","output","seal","manifest","readout"):args.add_argument("--"+k,required=True)
    p=args.parse_args()
    print(json.dumps(build(p.parent,p.output,p.seal,p.manifest,p.readout),ensure_ascii=False,indent=2))
