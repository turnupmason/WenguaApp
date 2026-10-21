"""Leave-one-historical-event-family-out author-style marriage development evaluation.

The inference function receives ONLY actor birth years, chart, question and
heldout family ID. Book author's outcomes and later feedback remain solely
inside this separate AFTER-INFERENCE scorer. Case01 was used previously for
V1.5 timing and is not eligible as an untouched blind case.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.marriage_judgment_v16 import analyze_marriage_unseen_chart

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻原书应期天文推算V1_5_完整研究库.sqlite3"
BOOK=ROOT/"sources/kaiwu/开悟之门_恋爱婚姻预测.txt"
WIT=ROOT/"data/knowledge/kaiwu/marriage_prediction_ch02_section02/original_palace_witnesses.json"
D={"虎":"白虎","阴":"太阴","蛇":"螣蛇","合":"六合",
   "符":"值符","武":"玄武","天":"九天","地":"九地"}
DOORS="休生伤杜景死惊开"
# Heldout families 02 and 03 were not the previously fitted case01 timing.
# Outcome labels are used ONLY below AFTER all initial results are computed.
QUESTIONS=[
 ("kaiwu.marriage.case02","1997-02-23T14:00:00+08:00","丙申","乙未",
  "丁丑","壬寅","雨水","yang",9,"戊申","甲辰",
  "marriage.scene.09","婚姻接下来还能继续吗？","failure",[81,89],[93]),
 ("kaiwu.marriage.case03","1998-06-04T21:30:00+08:00","壬午","辛亥",
  "戊寅","丁巳","小满","yang",5,"戊申","丙午",
  "marriage.scene.02","女儿和第一位对象能不能谈成？","failure",[121,123],[135]),
 ("kaiwu.marriage.case03","1998-06-04T21:30:00+08:00","壬午","辛亥",
  "戊寅","丁巳","小满","yang",5,"戊申","乙巳",
  "marriage.scene.02","女儿和第二位对象能不能谈成？","failure",[121,125],[135])
]
def _compare_printed_chart(chart,case_id):
 data=json.loads(WIT.read_text(encoding="utf8"))
 if hashlib.sha256(BOOK.read_bytes()).hexdigest()!=data["source_sha256"]:
  raise ValueError("Kaiwu original source witness is not canonical")
 actual=next(x for x in data["charts"] if x["case_id"]==case_id)
 errors=[];tested=0
 for printed in actual["printed_palaces"]:
  p=printed["palace"]
  if p==5:continue
  computed=chart["palaces"][str(p)]
  deity=D.get(printed["deity"])
  door=next((d for d in DOORS if d in printed["door"]),None)
  if not deity or not door:
   errors.append({"p":p,"reason":"unparsed original book deity/door"})
   continue
  tested+=1
  if computed["deity"]!=deity:errors.append({"p":p,"kind":"deity","original":deity,"computed":computed["deity"]})
  if computed["door"]!=door+"门":errors.append({"p":p,"kind":"door","original":door,"computed":computed["door"]})
 return {"eight_printed_outer_palaces_checked":tested,"agrees_with_original_book":not errors,
         "disagreements":errors,"center_five_not_fabricated":chart["palaces"]["5"]["door"] is None}
def evaluate(*,db_path=DB):
 outputs=[]
 for (family,iso,day,hour,year,month,term,dun,ju,subject,partner,scene,question,
       expected,author_lines,feedback_lines) in QUESTIONS:
  chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
  aligned=_compare_printed_chart(chart,family)
  packet={"chart":chart,
   "calendar_inputs":{"day_ganzhi":day,"hour_ganzhi":hour,"year_ganzhi":year,
    "month_ganzhi":month,"solar_term":term,"local_time_iso":iso,
    "iana_timezone":"Asia/Shanghai"},
   "inquiry":{"domain":"marriage","scene_id":scene,"question_text":question,
    "relationship":"parent_of_subject","subject":{"year_ganzhi":subject},
    "partner":{"year_ganzhi":partner}}}
  result=None
  if aligned["agrees_with_original_book"]:
   judge=analyze_marriage_unseen_chart(db_path=db_path,payload=packet,held_out_family_id=family)
   w=judge["book_witnesses_excluding_holdout"]
   if any(item["event_family_id"]==family for item in w["pre_event_method_witnesses"]):
    raise ValueError("Heldout entire event-family method leak")
   if judge["unseen_family_post_event_information_was_read"]:
    raise ValueError("Post-hoc outcomes became inference inputs")
   result={"outcome":judge["traditional_initial_outcome"],
    "support":judge["initial_judgment"]["support"],
    "counter":judge["initial_judgment"]["counter"],
    "other_computed_timing":judge["calculated_timing_if_source_condition_met"],
    "computed_factors":judge["fact_calculated_count"],
    "book_witness_families_used":[x["event_family_id"] for x in w["pre_event_method_witnesses"]],
    "publication_ready":judge["publication_ready"]}
  # CRUCIAL: expected/author_lines/feedback_lines are never supplied to judge.
  outputs.append({"heldout_event_family_id":family,"actual_question":question,
    "original_book_chart_alignment":aligned,
    "initial_inference_without_author_label_or_feedback":result,
    "validation_only_later":{"original_author_forecast_lines":author_lines,
      "later_source_feedback_lines":feedback_lines,"book_reported_event_outcome":expected,
      "source_mentioned_result_is_not_independently_verified":True,
      "matched_initial_decision":None if result is None else result["outcome"]==expected}})
 scorable=[x for x in outputs if x["initial_inference_without_author_label_or_feedback"] is not None
           and x["initial_inference_without_author_label_or_feedback"]["outcome"] in ("success","failure")]
 return {"schema":"wengua_marriage_v16_book_family_dev_holdout",
  "historical_book_material_was_available_during_development":True,
  "not_claimed_to_be_untouched_blind_test":True,
  "heldout_by_complete_event_family":True,
  "author_judgment_and_feedback_never_initial_inference_inputs":True,
  "candidate_questions":len(QUESTIONS),"printed_original_chart_alignment_count":sum(
   x["original_book_chart_alignment"]["agrees_with_original_book"] for x in outputs),
  "scored_decisive_cases":len(scorable),
  "matched_book_reported_outcomes":sum(
   x["validation_only_later"]["matched_initial_decision"] for x in scorable),
  "number_of_distinct_heldout_book_families":len(set(x["heldout_event_family_id"] for x in outputs)),
  "original_source_outcomes_are_not_objective_ground_truth":True,
  "no_automatic_update_to_rule_weights_from_heldout_results":True,"results":outputs}
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--database",default=str(DB));p.add_argument("--output")
 a=p.parse_args()
 data=evaluate(db_path=Path(a.database))
 report=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
 if a.output:Path(a.output).write_text(report,encoding="utf8")
 else:print(report)
