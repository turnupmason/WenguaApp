"""Marriage phrase input contract: check factors without inventing original charts.

This is *not* a casting algorithm. 1080 distinct state indices are known, but
real fully verified nine-palace computations + audit signatures must come
from the audited casting engine, not claimed by GPT or a caller-controlled
status field. Returns data-readiness gates only; never makes marriage predictions.
"""
from __future__ import annotations
from hashlib import sha256
import json,re
from .core import SCHOOL,cycle60
AGE_BANDS=("young","adult","older")
SEXES=("male","female")
DOMAINS=("marriage",)
STEMS=tuple(cycle60())
FACTOR_IDS=(
 "six_yi_striking_punishment","branch_opposition","branch_punishment",
 "branch_harm","month_day_break","door_press_palace","heaven_stem_tomb",
 "stem_storage","travel_horse","xun_kong","kong_near_far",
 "kong_fill","kong_clash","hidden_stems","seasonal_prosperity",
 "palace_five_elements","heaven_earth_stem_structure",
 "star_door_deity_structure","fuyin_fanyin","palace_interactions",
 "auspicious_inauspicious_formations","primary_secondary_yongshen",
 "conflicting_evidence","timing_qualification",
)
STATUSES=("present","absent","not_applicable","unknown")
CAST_STATUS="engine_verified"
def state_key(state):
 if not isinstance(state,str) or re.fullmatch(r"(yang|yin)-(0[1-9])-(0[0-9]|[1-5][0-9])",state) is None:
  return None
 return state
def matrix_base_key(state,year_ganzhi,age_band,sex):
 """One of 388,800 context coordinates; not a verified cast or reading."""
 if state_key(state) is None or year_ganzhi not in STEMS or age_band not in AGE_BANDS or sex not in SEXES:
  raise ValueError("Unknown 1080-state / year_ganzhi / three ages / sex coordinate")
 return (state,year_ganzhi,age_band,sex)
def matrix_cardinality():
 return 2*9*60*len(STEMS)*len(AGE_BANDS)*len(SEXES)
def inspect_marriage_input(document):
 """Return structured blockers; even 'ready_for_draft_review' is NOT proof of chart correctness."""
 blocked=[]
 if not isinstance(document,dict):
  return {"status":"blocked_invalid_input","blockers":["root_must_be_dict"],"coverage_key":None}
 chart=document.get("chart",{})
 if not isinstance(chart,dict):
  return {"status":"blocked_invalid_input","blockers":["chart_must_be_dict"],"coverage_key":None}
 if chart.get("school_id")!=SCHOOL: blocked.append("unsupported_casting_school")
 state=state_key(chart.get("state_id"))
 if state is None:blocked.append("missing_or_invalid_1080_state_id")
 if chart.get("status")!=CAST_STATUS:blocked.append("unverified_nine_palace_cast")
 if not isinstance(chart.get("method_version"),str) or not chart.get("method_version"):blocked.append("missing_casting_method_version")
 if not isinstance(chart.get("verification_receipt"),str) or not chart.get("verification_receipt"):blocked.append("missing_casting_verification_receipt")
 if not isinstance(chart.get("calendar_inputs"),dict) or not all(chart["calendar_inputs"].get(k) for k in ("time_iso","timezone","solar_term_basis")):
  blocked.append("missing_time_timezone_solar_term_input")
 cells=chart.get("palaces")
 if not isinstance(cells,list) or len(cells)!=9 or any(not isinstance(c,dict) for c in cells):
  blocked.append("nine_palace_cells_not_available")
 else:
  vals=[v.get("palace_id") for v in cells]
  if set(vals)!={1,2,3,4,5,6,7,8,9} or len(set(vals))!=9:
   blocked.append("invalid_nine_palace_coordinates")
  if any(not c.get("earth_stem") or not c.get("heaven_stem") for c in cells):
   blocked.append("missing_original_heaven_earth_stems")
  if any(v["palace_id"]!=5 and not all(v.get(k) for k in ("door","star","deity")) for v in cells):
   blocked.append("missing_noncentral_door_star_deity")
 # Center-5 cannot be forced to have a conventional gate/star/deity.
 inquiry=document.get("inquiry",{})
 if not isinstance(inquiry,dict):
  inquiry={}
  blocked.append("inquiry_missing")
 if inquiry.get("domain")!="marriage":blocked.append("non_marriage_domain")
 for k in ("question_type","relationship","querent","subject"):
  if not inquiry.get(k):blocked.append("missing_inquiry_"+k)
 person=inquiry.get("subject",{})
 if not isinstance(person,dict):
  person={}
  blocked.append("missing_subject_record")
 if person.get("age_band") not in AGE_BANDS:blocked.append("missing_or_unsupported_subject_age_band")
 if person.get("sex") not in SEXES:blocked.append("missing_or_unsupported_subject_sex")
 if person.get("year_ganzhi") not in STEMS:blocked.append("missing_or_unsupported_subject_year_ganzhi")
 if inquiry.get("relationship") not in ("self","parent_of_subject","child_of_subject",
                                       "spouse_of_subject","friend","colleague","leader","other"):
  blocked.append("unbound_person_relationship")
 factors=document.get("calculated_factors",{})
 if not isinstance(factors,dict):
  blocked.append("no_full_physical_factor_audit")
  factors={}
 for name in FACTOR_IDS:
  item=factors.get(name)
  if not isinstance(item,dict) or item.get("checked") is not True or item.get("status") not in STATUSES:
   blocked.append("missing_or_unchecked_factor:"+name)
  elif not item.get("rule_ref") or item.get("evidence") is None:
   blocked.append("missing_factor_rule_or_evidence:"+name)
  elif item["status"] in ("unknown","not_applicable") and not item.get("reason"):
   blocked.append("unknown_or_na_without_reason:"+name)
  elif item["status"]=="unknown" and name in (
   "primary_secondary_yongshen","conflicting_evidence","palace_interactions"):
   blocked.append("decisive_unknown_factor:"+name)
 # A user-provided receipt is metadata, never cryptographic proof.
 # This inspector cannot confer release approval on any result.
 key=None
 if state is not None:
  try:key=matrix_base_key(state,person.get("year_ganzhi"),person.get("age_band"),person.get("sex"))
  except ValueError:pass
 return {"status":"blocked_requires_review" if blocked else "ready_for_draft_review",
         "blockers":sorted(set(blocked)),
         "coverage_key":list(key) if key else None,
         "factors_checked":sum(isinstance(factors.get(n),dict) and factors[n].get("checked") is True for n in FACTOR_IDS),
         "total_required_factors":len(FACTOR_IDS),
         "cast_receipt_cryptographically_verified":False,
         "eligible_to_publish_predictive_reading":False}
def canonical_sha(record):
 return sha256(json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
