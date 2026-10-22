"""Deterministic seed-drawn 2 DISTINCT historical health-hour test cases.

The predictor reads ONLY source case metadata: time, explicit bureau, role.
It never reads original author conclusions or feedback. Each prediction is
serialized verbatim + sha256 for subsequent human comparison.
"""
from __future__ import annotations
import argparse, hashlib,json
from pathlib import Path

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_v27 import analyze_health_severity_v27

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/knowledge/shenqi/health_prediction_ch01/case_index.json"
PARENT_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_庚申时本人病情精简模板纠错V2_6_完整研究库.sqlite3"
SEED="e6dff53d3c1f403650581877b8563db00b49958d75b0a3e8a459d6c7bb4cfa17"
CANDIDATES=(
 "shenqi.health.19960727.father_illness",
 "shenqi.health.19960523.aunt_illness",
 "shenqi.health.19961102.on_site_health",
 "kaiwu.health.19960923.nasal_cancer",
 "kaiwu.health.19950219.brother_paralysis",
 "kaiwu.health.19991020.wang_craniotomy",
)
CHOSEN_EXPECTED=(
 "shenqi.health.19961102.on_site_health",
 "shenqi.health.19960523.aunt_illness"
)
CASE_METADATA={
 "shenqi.health.19961102.on_site_health":{
    "local":"1996-11-02T16:00:00+08:00",
    "relationship":"self","context":"direct_self",
    "sex":None,"role_specific":None,
    "user_question":"本人当面问身体情况（书中问事已知）"},
 "shenqi.health.19960523.aunt_illness":{
    "local":"1996-05-23T19:30:00+08:00",
    "relationship":"older_relative","context":"direct_proxy",
    "sex":"female","role_specific":"aunt",
    "user_question":"亲属代问姨母病情（女性关系已知）"},
}


def fnv32(s:str,h=2166136261):
    for ch in s:
        h=((h^ord(ch))*16777619)&0xffffffff
    return h


def draw():
    seed=fnv32(SEED)
    ranked=sorted(CANDIDATES,key=lambda case:fnv32(case,seed))
    choices=tuple(ranked[:2])
    if choices!=CHOSEN_EXPECTED:
        raise ValueError("Random draw changed; historical family audit invalid")
    return choices, {k:fnv32(k,seed) for k in CANDIDATES}


def evaluate(*,db_path=PARENT_DB):
    chosen,scores=draw()
    source=json.loads(SOURCE.read_text("utf8"))
    originals={x["id"]:x for x in source["cases"]}
    predictions=[]
    for id in chosen:
        original=originals[id]
        meta=CASE_METADATA[id]
        c=original["casting"]
        calendar=solar_chart_clock(meta["local"],"Asia/Shanghai")
        if calendar["four_pillars"]["day"]!=c["day_ganzhi"] or calendar["four_pillars"]["hour"]!=c["hour_ganzhi"]:
            raise ValueError("Source-day or source-hour differs from independent calendar: "+id+" "+str(calendar["four_pillars"]))
        chart=layout_from_explicit_bureau(dun=c["dun"],ju=c["ju"],hour_ganzhi=c["hour_ganzhi"])
        # Check source chart metadata where a field is explicitly asserted.
        for fld in ("value_star","value_door"):
            if fld in c and chart[fld]!=c[fld]:
                raise ValueError("Source chart mismatch "+id+" "+fld+
                                 " original:"+c[fld]+" cast:"+chart[fld])
        inquiry={"intent":"severity","relationship":meta["relationship"],
                 "consultation_context":meta["context"]}
        if meta["sex"]: inquiry["patient_sex"]=meta["sex"]
        if meta["role_specific"]: inquiry["relative_specific"]=meta["role_specific"]
        cal={"year_ganzhi":calendar["four_pillars"]["year"],
             "month_ganzhi":calendar["four_pillars"]["month"],
             "day_ganzhi":c["day_ganzhi"],
             "hour_ganzhi":c["hour_ganzhi"],
             "month_branch":calendar["four_pillars"]["month"][1]}
        reading=analyze_health_severity_v27(chart=chart,inquiry=inquiry,
                                            calendar=cal,db_path=db_path)
        txt=reading["reading_text"]
        predictions.append({
            "case_id":id,"case_title":original["title"],
            "question_known_before_outcome":meta["user_question"],
            "civil_clock_anchor":meta["local"],
            "year_ganzhi":cal["year_ganzhi"],"month_ganzhi":cal["month_ganzhi"],
            "day_ganzhi":cal["day_ganzhi"],"hour_ganzhi":cal["hour_ganzhi"],
            "book_source_bureau":{"dun":c["dun"],"ju":c["ju"]},
            "patient_sex":meta["sex"],
            "book_metadata_only_used":True,"original_pred_and_feedback_read":False,
            "role":reading["audit"]["role_binding"],
            "five_not_encounter":reading["audit"]["five_not_encounter"],
            "gender_auxiliary_palace":reading["audit"]["gender_auxiliary_palace"],
            "traditional_verdict":reading["audit"]["traditional_verdict"]["verdict"],
            "readout_sections":reading["sections"],
            "readout_text":txt,
            "readout_sha256":hashlib.sha256(txt.encode("utf8")).hexdigest(),
            "full_chart":chart,
            "source_case_index_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "source_database_sha256":hashlib.sha256(Path(db_path).read_bytes()).hexdigest(),
            "end_user_review_status":"pending",
            "historical_case_is_not_truly_unseen":True,
            "modern_medical_validation":False
        })
    return {
        "schema":"wengua_v27_two_historical_case_sealed_readouts",
        "selection_seed":SEED,"selection_algorithm":"FNV1a32_from_exact_parent_full_sqlite_sha",
        "candidate_pool":list(CANDIDATES),
        "selection_ranks":scores,"selected_ids":list(chosen),
        "training_and_review_note":"These historical families are in the source library; this run did not retrieve their endings; retrospective review only, not untouched secret blind testing.",
        "predictions":predictions,
        "original_book_outcomes_appended":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--database",default=str(PARENT_DB))
    p.add_argument("--output",required=True)
    x=p.parse_args()
    out=Path(x.output)
    if out.exists():raise ValueError("Do not overwrite an earlier sealed trial")
    report=evaluate(db_path=Path(x.database))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    print("V27_TWO_PREDICTIONS_BEGIN")
    for i,pred in enumerate(report["predictions"],1):
        print("CASE_%d_ID="%i+pred["case_id"])
        print("CASE_%d_SOURCE_TIME="%i+pred["day_ganzhi"]+"日"+pred["hour_ganzhi"]+"时")
        print("CASE_%d_FIVE_NOT_ENCOUNTER="%i+str(pred["five_not_encounter"]["triggered"]))
        print("CASE_%d_READOUT_SHA256="%i+pred["readout_sha256"])
        print("CASE_%d_READOUT_START"%i)
        print(pred["readout_text"])
        print("CASE_%d_READOUT_END"%i)
    print("V27_TWO_PREDICTIONS_END")


if __name__=="__main__":
    main()
