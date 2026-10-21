"""One strict six-layer gate for EVERY WenguaApp question/domain.

A complete immutable six-layer trace is required before any phrase instance
may be promoted as an approved completed reading. This validator enforces
evidence completeness; it DOES NOT claim an astrological method is empirically
predictive or that a self-reported engine receipt is genuinely authenticated.
"""
from __future__ import annotations
from .phrase_pipeline import FACTOR_IDS, inspect_marriage_input, canonical_sha

LAYERS=(
 "chart_facts",
 "all_palace_relations",
 "role_and_domain_yongshen",
 "author_methods_and_case_evidence",
 "decision_and_calendar_timing",
 "gpt_human_language",
)
STATUSES=("passed","blocked","unknown")
OUTCOMES=("success","failure","delayed","mixed")
def audit_all_domains(packet:dict)->dict:
 """Fail-closed. Nothing but completed + verifiably linked stages can publish.

 Every named mandatory factor must have checked/status/rule/source plus
 applicability. Layer-1 authenticating itself is not trusted here: a real
 engine-level receipt verification must supply receipt_verified=True.
 """
 failures={name:[] for name in LAYERS}
 if not isinstance(packet,dict):
  return {"status":"blocked_incomplete_pipeline","missing":["root_invalid"],"layers_checked":0}
 domain=packet.get("domain")
 if not isinstance(domain,str) or not domain.strip():
  failures[LAYERS[2]].append("domain_missing")
 stage_data=packet.get("layer_trace",{})
 if not isinstance(stage_data,dict):stage_data={}
 if set(stage_data)!=set(LAYERS):
  for name in LAYERS:
   if name not in stage_data:failures[name].append("layer_missing")
 for name in LAYERS:
  stage=stage_data.get(name,{})
  if not isinstance(stage,dict) or stage.get("status")!="passed":
   failures[name].append("not_passed_with_evidence")
   continue
  if not isinstance(stage.get("source_evidence"),(list,dict)) or not stage["source_evidence"]:
   failures[name].append("no_source_evidence")
  if not stage.get("rule_version"):failures[name].append("rule_version_missing")
 first=stage_data.get(LAYERS[0],{})
 if not isinstance(first,dict) or first.get("receipt_verified") is not True:
  failures[LAYERS[0]].append("casting_engine_receipt_not_independently_verified")
 if not isinstance(first,dict) or not isinstance(first.get("chart"),dict):
  failures[LAYERS[0]].append("full_cast_json_missing")
 second=stage_data.get(LAYERS[1],{})
 factors=second.get("factors",{}) if isinstance(second,dict) else {}
 if not isinstance(factors,dict):factors={}
 for fac in FACTOR_IDS:
  item=factors.get(fac)
  if not isinstance(item,dict) or item.get("checked") is not True:
   failures[LAYERS[1]].append("factor_unchecked:"+fac)
   continue
  if item.get("status") not in ("present","absent","not_applicable","unknown"):
   failures[LAYERS[1]].append("factor_bad_status:"+fac)
  if not item.get("rule_ref"):failures[LAYERS[1]].append("factor_rule_missing:"+fac)
  if item.get("evidence") is None:failures[LAYERS[1]].append("factor_evidence_missing:"+fac)
  if item.get("status")=="unknown" and not item.get("reason"):
   failures[LAYERS[1]].append("factor_unknown_without_reason:"+fac)
 third=stage_data.get(LAYERS[2],{})
 for k in ("intent_id","target_event","querent_subject_roles","primary_yongshen","secondary_yongshen"):
  if not isinstance(third,dict) or not third.get(k):
   failures[LAYERS[2]].append("missing_role_or_yongshen:"+k)
 fourth=stage_data.get(LAYERS[3],{})
 if not isinstance(fourth,dict) or not fourth.get("book_case_rule_refs"):
  failures[LAYERS[3]].append("no_real_author_book_refs")
 elif any(not isinstance(x,dict) or not all(x.get(k) for k in ("book_id","original_source_sha256","line_numbers","case_id"))
          for x in fourth["book_case_rule_refs"]):
  failures[LAYERS[3]].append("unverifiable_original_book_ref")
 if not isinstance(fourth,dict) or fourth.get("future_outcome_feedback_as_prediction_input") is not False:
  failures[LAYERS[3]].append("author_feedback_leakage_not_excluded")
 fifth=stage_data.get(LAYERS[4],{})
 if not isinstance(fifth,dict) or fifth.get("traditional_outcome") not in OUTCOMES:
  failures[LAYERS[4]].append("decisive_target_event_outcome_missing")
 if not isinstance(fifth,dict) or not isinstance(fifth.get("supporting_evidence"),list) or not fifth["supporting_evidence"]:
  failures[LAYERS[4]].append("no_supporting_reasoning")
 if not isinstance(fifth,dict) or not isinstance(fifth.get("counterevidence"),list):
  failures[LAYERS[4]].append("counterevidence_not_checked")
 if isinstance(fifth,dict) and fifth.get("timing_applicable") is True:
  for key in ("primary_window","calendar_method_version","verified_calendar_receipt",
              "timing_choice_method_ref","other_candidates_and_why_rejected"):
   if not fifth.get(key):
    failures[LAYERS[4]].append("missing_computed_timing:"+key)
 elif not isinstance(fifth,dict) or fifth.get("timing_applicable") is not False:
  failures[LAYERS[4]].append("missing_timing_applicability")
 elif not fifth.get("why_timing_not_applicable"):
  failures[LAYERS[4]].append("missing_reason_no_timing")
 sixth=stage_data.get(LAYERS[5],{})
 if not isinstance(sixth,dict) or not isinstance(sixth.get("user_text"),str):
  failures[LAYERS[5]].append("missing_chinese_user_text")
 elif not 90<=sum('\u4e00'<=x<='\u9fff' for x in sixth["user_text"])<=320:
  failures[LAYERS[5]].append("not_reasonable_natural_chinese_length")
 if not isinstance(sixth,dict) or sixth.get("new_facts_introduced") is not False:
  failures[LAYERS[5]].append("gpt_generated_unsourced_facts_not_checked")
 missing=[f"{name}:{problem}" for name in LAYERS for problem in failures[name]]
 return {"status":"blocked_incomplete_pipeline" if missing else "passed_six_layers_ready_for_external_review",
         "layers_checked":len(LAYERS),"checked_24_physical_factors":sum(
             isinstance(factors.get(k),dict) and factors[k].get("checked") is True for k in FACTOR_IDS),
         "missing":missing,"layer_results":{n:{"status":"blocked" if v else "passed","issues":v} for n,v in failures.items()},
         "real_world_predictive_accuracy_guaranteed":False,
         "contract_sha256":canonical_sha({"required_layers":LAYERS,"factor_ids":FACTOR_IDS})}
