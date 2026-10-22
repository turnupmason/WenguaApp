"""V3.1 *new historical families* book-metadata-only severity replay.

Source-case originals and feedback are deliberately not used to produce the
reading. CASE_METADATA is pre-disclosure-only: no patient birth year, answer,
illness label, surgery confirmation, predicted year or feedback. One event
family stays one event family. Full predictions sealed before source comparison.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_v31 import analyze_health_severity_v31

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/knowledge/shenqi/health_prediction_ch01/case_index.json"
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_患者时干病事有向修正V3_1_完整研究库.sqlite3"
PARENT_SHA="3a72dbb798d73413c2ebb994e232b83039a483d91cfa8a8f60f246d4ad84b529"
CASES=(
 ("shenqi.health.19960316.self_surgery","1996-03-16T16:30:00+08:00",
  "self","direct_self",None,"本人最初仅问身体是否健康，不引入后来确认的手术或年命"),
 ("shenqi.health.19960727.father_illness","1996-07-27T16:00:00+08:00",
  "father","direct_proxy","male","女儿最初代问父亲病情；父亲年命未给"),
)

def evaluate(*,db_path=DB):
    db=Path(db_path)
    if hashlib.sha256(db.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("Historical replay requires exact immutable V3.1 full 194-case source")
    idx=json.loads(SOURCE.read_text("utf8"))
    # Never materialize or inspect 'author_predictions', 'feedback_lines',
    # later disclosures, outcome labels, or source-ending text in forecasting.
    basic={}
    for x in idx["cases"]:
        if x["id"] in {k[0] for k in CASES}:
            basic[x["id"]]={"id":x["id"],
              "title":x["title"],"casting":dict(x["casting"]),
              "patient_relation":x["patient_relation"]}
    if len(basic)!=2:raise ValueError("Two specified original historical families required")
    out=[]
    for id,clock,relation,context,sex,prompt in CASES:
        row=basic[id];casting=row["casting"]
        computed=solar_chart_clock(clock,"Asia/Shanghai")
        pillars=computed["four_pillars"]
        if pillars["day"]!=casting["day_ganzhi"] or pillars["hour"]!=casting["hour_ganzhi"]:
            raise ValueError("Independent calendar and original input differ: "+id+
                             " "+json.dumps(pillars,ensure_ascii=False))
        board=layout_from_explicit_bureau(dun=casting["dun"],ju=casting["ju"],
                                          hour_ganzhi=casting["hour_ganzhi"])
        for attr in ("value_star","value_door","value_star_palace","value_door_palace"):
            if attr in casting and board[attr]!=casting[attr]:
                raise ValueError("Original book vs real casting engine "+id+" "+
                                 attr+": "+str(casting[attr])+" vs "+str(board[attr]))
        # no book feedback, later-born birth year, or human outcome labels!
        inquiry={"intent":"severity","relationship":relation,"consultation_context":context}
        if sex:inquiry["patient_sex"]=sex
        calendar={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
                  "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
                  "month_branch":pillars["month"][1]}
        rendered=analyze_health_severity_v31(chart=board,inquiry=inquiry,
                                             calendar=calendar,db_path=db)
        if "病吉" not in rendered["reading_text"] and "病凶" not in rendered["reading_text"]:
            raise ValueError("No traditional illness verdict in fixed local template")
        originaltext=rendered["reading_text"]
        out.append({
         "family_id":id,"original_title":row["title"],"original_question_opening":prompt,
         "civil_time_anchor":clock,"four_pillars":pillars,
         "original_given_bureau":{"dun":casting["dun"],"ju":casting["ju"]},
         "sex":sex,"relation":relation,
         "birth_year_supplied_pre_question":False,
         "value_star":board["value_star"],"value_door":board["value_door"],
         "live_engine":"analyze_health_severity_v31",
         "full_chart":board,
         "sections":rendered["sections"],
         "verdict":rendered["audit"]["traditional_verdict"]["verdict"],
         "fuyin_fanyin":rendered["audit"]["fuyin_fanyin"],
         "actual_tomb_and_punishment":rendered["audit"].get("actual_tomb_punishment_v28",[]),
         "medical_opportunity":rendered["audit"].get("medical_timing_v28",{}),
         "patient_hour_direction":rendered["audit"]["v31_patient_hour_direction"],
         "text":originaltext,
         "text_sha256":hashlib.sha256(originaltext.encode("utf8")).hexdigest(),
         "original_author_outcome_used":False,
         "old_historical_event_family_not_secret_blind":True,
         "patient_review":"pending",
         "not_a_clinical_diagnosis":True
        })
    return {
      "schema":"wengua_v32_two_other_historical_families_v31_engine",
      "full_parent_v31_sha256":PARENT_SHA,
      "case_selection":"two source-index families excluding all V2.7-V3.1 evaluation families",
      "original_book_conclusions_loaded":False,
      "old_evaluation_families_reused":False,
      "pure_python_no_gpt":True,
      "samples":out
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--database",default=str(DB))
    p.add_argument("--out")
    args=p.parse_args()
    result=evaluate(db_path=args.database)
    if args.out:
        outfile=Path(args.out)
        if outfile.exists():raise ValueError("Original sealed predictions must never be overwritten")
        outfile.parent.mkdir(parents=True,exist_ok=True)
        outfile.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
    print("V32_PRE_DISCLOSURE_TWO_CASES_BEGIN")
    for i,r in enumerate(result["samples"],1):
        print("CASE_"+str(i)+" "+r["family_id"]+" "+r["four_pillars"]["day"]+"日"+
              r["four_pillars"]["hour"]+"时")
        print("CASE_SHA256="+r["text_sha256"])
        print(r["text"])
        print("CASE_"+str(i)+"_END")
    print("V32_PRE_DISCLOSURE_TWO_CASES_END")

if __name__=="__main__":main()
