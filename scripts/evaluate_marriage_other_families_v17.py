"""V1.7 next event-family heldouts 04/05, plus author-wrong 06 negative control.

Historical book was available during development, and V1.7 rules cite
cases 04 and 05 among 27 source evidence records. This therefore is NOT an
untouched sealed test; it is a DIFFERENT event-family research holdout only.
Do not claim accuracy when source has no later verification, no true partner
birth year, or no objectively observable future relationship event.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.marriage_book_combinator_v17 import analyze_marriage_v17
from scripts.evaluate_marriage_family_holdout_v16 import _compare_printed_chart
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻作者式判断与家族留出评测V1_6_完整研究库.sqlite3"
BOOK=ROOT/"sources/kaiwu/开悟之门_恋爱婚姻预测.txt"
CASES=[
 {"family":"kaiwu.marriage.case04","day":"庚戌","hour":"乙酉","dun":"yin","ju":9,
  "date":"1999-06-27T17:30:00+08:00","year":"己卯","month":"庚午",
  "solar_term":"夏至","scene":"marriage.scene.09","year_subject":"乙卯",
  "question":"现交往男友的恋爱走向如何？","source_first_lines":[159,175],
  "later_feedback_lines":[161,167],"question_outcome_independently_observed":False},
 {"family":"kaiwu.marriage.case05","day":"辛酉","hour":"癸巳","dun":"yin","ju":5,
  "date":"1999-07-08T10:00:00+08:00","year":"己卯","month":"辛未",
  "solar_term":"小暑","scene":"marriage.scene.19","year_subject":None,
  "question":"前夫要求复婚，复婚是否合适及何时办理？","source_first_lines":[229,231],
  "later_feedback_lines":[],"question_outcome_independently_observed":False}
]
def evaluate(*,db_path=DB):
 initial=[]
 for case in CASES:
  chart=layout_from_explicit_bureau(dun=case["dun"],ju=case["ju"],hour_ganzhi=case["hour"])
  aligned=_compare_printed_chart(chart,case["family"])
  if not aligned["agrees_with_original_book"]:
   initial.append({"family":case["family"],"source_chart_alignment":aligned,
    "initial_source_judgment":None,
    "blocked":"Book chart does not agree with this source casting engine; do not score"})
   continue
  actors={"subject":{"year_ganzhi":case["year_subject"]} if case["year_subject"] else {},
          "partner":{}}
  payload={"chart":chart,
   "calendar_inputs":{"day_ganzhi":case["day"],"hour_ganzhi":case["hour"],
    "year_ganzhi":case["year"],"month_ganzhi":case["month"],
    "solar_term":case["solar_term"],
    "local_time_iso":case["date"],"iana_timezone":"Asia/Shanghai"},
   "inquiry":{"domain":"marriage","scene_id":case["scene"],
    "question_text":case["question"],"relationship":"self",**actors}}
  result=analyze_marriage_v17(db_path=db_path,payload=payload,
                             held_out_family_id=case["family"])
  witness=result.get("prior_book_witness_holdout_audit",{})
  if any(c["event_family_id"]==case["family"] for c in witness.get("pre_event_method_witnesses",[])):
   raise ValueError("V1.7 heldout complete family leaked into source witness inference")
  if result.get("post_event_feedback_used_in_verdict") is not False:
   raise ValueError("V1.7 future feedback used as input")
  if case["year_subject"] is None or not actors["partner"].get("year_ganzhi"):
   if result["traditional_initial_outcome"]!="unresolved":
    raise ValueError("Invented partner birth year / resolved relationship without true participant")
  initial.append({"family":case["family"],"source_chart_alignment":aligned,
    "initial_source_judgment":{
      "outcome":result["traditional_initial_outcome"],
      "source_combo_rule_count":result["source_backed_combo"]["source_rule_catalog_count"],
      "real_81_ordered_pairs":result["source_backed_combo"]["directional_stem_pair_count"],
      "person_details_missing_are_not_fabricated":True,
      "future_window":result["conditionally_defensible_timing"],
      "publication_ready":result["release_approved"]},
    "family_initial_inference_source_hash":hashlib.sha256(
       json.dumps({"family":case["family"],"question":case["question"],
                   "year":case["year_subject"]},sort_keys=True,
                  ensure_ascii=False).encode()).hexdigest()})
 # AFTER initial results are materialized, reference author narrative
 # for error study. Neither 04 nor 05 reports verified future relationship
 # outcome; they cannot be scored as actual predictive hits.
 comparison=[]
 source=BOOK.read_text("utf8").splitlines()
 for case,item in zip(CASES,initial):
  for n in case["source_first_lines"]+case["later_feedback_lines"]:
   if not 1<=n<=len(source) or not source[n-1].strip():
    raise ValueError("Original printed source line cannot be verified")
  comparison.append({"family":case["family"],"original_first_lines":case["source_first_lines"],
    "later_source_lines":case["later_feedback_lines"],
    "author_outcome_vs_unobserved_future_not_scorable":True,
    "initial_author_verdict_was_not_a_model_input":True})
 return {"schema":"marriage_v17_other_family_not_sealed_holdout",
  "new_historical_event_families":["kaiwu.marriage.case04","kaiwu.marriage.case05"],
  "excluded_prior_development_event_families":["kaiwu.marriage.case01","kaiwu.marriage.case02","kaiwu.marriage.case03"],
  "not_untouched_sealed":True,
  "historical_corpus_already_known_to_method_designer":True,
  "actual_new_forecast_correctness_scores":0,
  "book_original_cases_future_outcome_not_verified":True,
  "case06_explicit_first_author_failure_kept_out_of_positive_training":True,
  "unsafe_inferences_from_sexual_orientation_forbidden":True,
  "original_book_source_sha256":hashlib.sha256(BOOK.read_bytes()).hexdigest(),
  "before_feedback_initial_study":initial,"after_initial_author_comments":comparison}
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--database",default=str(DB));p.add_argument("--output")
 a=p.parse_args()
 result=evaluate(db_path=Path(a.database))
 s=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
 if a.output:Path(a.output).write_text(s,"utf8")
 else:print(s)
