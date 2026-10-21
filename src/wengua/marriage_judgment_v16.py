"""Marriage V1.6: independent *initial* source-rule judgment, evidence and timing.

No case author answer or later feedback is read to choose outcome. An entire
held-out event family is excluded from SOURCE WITNESS RETRIEVAL and scoring.
The result is a traditional-interpretation decision trace, not evidence of
real-world events. The two book methods are only applied conditionally:
Shenqi marriage ch02 line 5,11 and Kaiwu marriage line 39/41/43.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json,sqlite3
from .marriage_runtime import (
 inspect_marriage_chart_json,element_relation,ELEMENTS,
 PALACE_BRANCHES,_fact)
from .symbol_relations import related,stem_stage,door_season
from .book_timing_runtime import load_source_timing_rules
from .astro_calendar import solar_chart_clock,branch_periods,EPHEMERIS_VERSION
from .timing_engine import derive_timing_candidates,finalize_traditional_decision

ROOT=Path(__file__).resolve().parents[2]
RELATIONS=ROOT/"data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json"
SHENQI_METHOD=ROOT/"data/knowledge/shenqi/marriage_prediction_ch02/method_index.json"
TRADITIONAL_BOUNDARY=("Original books document historical author judgments. "
 "No symbolic reading establishes a real person's conduct, health, legal rights or future certainty.")
POSITIVE=("比和","生","受生")
NEGATIVE=("克","受克")
MONTH_SEASON={"寅":"春","卯":"春","辰":"四季月",
              "巳":"夏","午":"夏","未":"四季月",
              "申":"秋","酉":"秋","戌":"四季月",
              "亥":"冬","子":"冬","丑":"四季月"}
RULES={"person_palace":"shenqi/marriage_prediction_ch02/v1:line11",
       "traditional_yi_geng":"shenqi/marriage_prediction_ch02/v1:line5",
       "liuhe":"shenqi/marriage_prediction_ch02/v1:line5",
       "book_exception":"shenqi/marriage_prediction_ch02/v1:line107",
       "kaiwu_marriage_case01":"kaiwu/marriage_prediction_ch02_section02/v1:lines39,41,43"}

def _load_rules_and_source(db):
 index=json.loads(SHENQI_METHOD.read_text(encoding="utf8"))
 if index.get("schema")!="wengua_marriage_domain_method_v1":
  raise ValueError("Original source marriage methods not found")
 book=db.execute("""SELECT original_text,sha256 FROM sections
   WHERE book_id='shenqi' AND section_key='marriage_prediction_ch02'""").fetchone()
 if not book or sha256(book[0].encode("utf8")).hexdigest()!=book[1]:
  raise ValueError("Canonical Shenqi marriage chapter hash mismatch")
 if book[1]!=index["source_sha256"]:
  raise ValueError("Method source not tied to unchanged original chapter")
 for line in (5,11,107):
  if line>len(book[0].splitlines()) or not book[0].splitlines()[line-1].strip():
   raise ValueError("No original book rule at claimed line")
 return {k:{"rule_ref":v,"original_source_sha256":book[1]} for k,v in RULES.items()}

def _evidence(phase,palaces,relation,rule_id,source_refs,comment,*,status="determinate"):
 return {"phase":phase,"palaces":palaces,"relation":relation,
         "rule_id":rule_id,"source_rule":source_refs[rule_id],
         "reason":comment,"source_status":status,
         "not_scientifically_validated":True}

def _year_actor(view,who):
 node=view.get("actual_year_stem_candidate_binding",{}).get(who,{})
 if node.get("status")!="year_stem_palace_candidate_only_not_selected_primary_yongshen":
  return None
 cells=node.get("candidate_palace_cells",[])
 if len(cells)!=1:return None
 cell=cells[0]
 if cell["palace"] not in ELEMENTS:return None
 return cell

def _source_witnesses(db,scene_id,*,held_out_family_id=None):
 """Retrieve only nonheldout, PRE-feedback witnesses; leave-out is by FAMILY.

 Two books can describe the same real incident in multiple ways. Holdout by
 event_family_id prevents duplicate descriptions slipping into learning.
 Any original author error is retained in NEGATIVE controls, not a success.
 """
 sql="""SELECT m.book_id,m.section_key,m.original_source_sha256,
      m.original_case_id,m.source_lines_json,m.source_snippets_json,
      m.source_phase,m.feedback_not_initial_reasoning,
      c.event_family_id, v.verdict
 FROM marriage22_original_case_links m
 JOIN cases c ON c.case_id=m.original_case_id
 LEFT JOIN historical_case_book_verdicts v ON v.event_family_id=c.event_family_id
 WHERE m.scene_id=? ORDER BY m.source_ordinal"""
 allrows=db.execute(sql,(scene_id,)).fetchall()
 if not allrows:raise ValueError("No historical authors cited for scene")
 kept=[];omitted=[]
 for bk,key,hashv,cid,lines,snips,phase,feedback,family,verdict in allrows:
  note={"case_id":cid,"event_family_id":family,"book_id":bk,
        "original_source_sha256":hashv,"source_section_key":key,
        "original_lines":json.loads(lines),"author_phase":phase}
  if family==held_out_family_id:
   omitted.append({**note,"reason":"entire_heldout_event_family"})
   continue
  if feedback or "feedback" in phase or "later" in phase or "post" in phase:
   omitted.append({**note,"reason":"post_event_information_never_initial_input"})
   continue
  if verdict=="author_book_error_explicit":
   omitted.append({**note,"reason":"original_author_explicit_failure_negative_test_only"})
   continue
  source=db.execute("""SELECT original_text FROM sections
       WHERE book_id=? AND section_key=? AND sha256=?""",(bk,key,hashv)).fetchone()
  if not source:raise ValueError("Original book witness missing from full database")
  raw=source[0].splitlines()
  for snippet in json.loads(snips):
   n=snippet["line"]
   if n<1 or n>len(raw) or raw[n-1]!=snippet["original"]:
    raise ValueError("Original pre-feedback author line no longer agrees")
   if sha256(snippet["original"].encode("utf8")).hexdigest()!=snippet["sha256"]:
    raise ValueError("Witness excerpt SHA mismatch")
  # Prohibit source-prose from passing into inference: only HASH and anchored
  # method topics are needed. Author's case specific outcome is not copied.
  kept.append(note)
 return {"pre_event_method_witnesses":kept,
         "excluded_heldout_feedback_or_explicit_errors":omitted,
         "heldout_family_id":held_out_family_id,
         "feedback_text_ever_visible_to_outcome_decider":False}

def grounded_factor_extensions(base,chart,calendar):
 """Populate only source-backed branch/month, tomb, and 8-door season fields."""
 rel=json.loads(RELATIONS.read_text("utf8"))
 if rel.get("schema")!="wengua_shenqi_symbol_relations_v1":
  raise ValueError("Original Shenqi symbol relation schema changed")
 md=calendar["four_pillars"]
 month=md["month"][1];day=md["day"][1]
 season=MONTH_SEASON[month]
 factors={k:dict(v) for k,v in base.items()}
 tested={"branch_opposition":[],"branch_harm":[],"branch_punishment":[],"month_day_break":[],
         "heaven_stem_tomb":[],"seasonal_prosperity":[]}
 for raw in chart["palaces"].values():
  p=raw["palace"]
  if p==5:continue
  bgroup=PALACE_BRANCHES[p]
  for outside_label,outside in (("month",month),("day",day)):
   for b in bgroup:
    for typ,name in (("branch_clash","branch_opposition"),
                     ("branch_harm","branch_harm"),
                     ("branch_punishment","branch_punishment")):
     relations=related(typ,(b,outside))
     if relations:
      entry={"palace":p,"palace_branch":b,"external_branch":outside,
             "external_dimension":outside_label,
             "source_relation_ids":[q["relation_id"] for q in relations],
             "source_lines":[q["source_lines"] for q in relations]}
      tested[name].append(entry)
      if typ=="branch_clash":
       tested["month_day_break"].append(entry)
  door=raw["door"]
  if door:
   state=door_season(door,season)
   if state["stage"] is not None:
    tested["seasonal_prosperity"].append({
     "palace":p,"door":door,"month_branch":month,"season":season,
     "state":state["stage"],"source_lines":state["source_lines"]})
  for st in raw["heaven_stars"]:
   carried=st["carried_stem"]
   try:tomb=stem_stage(carried,"墓")
   except ValueError:continue
   if tomb["branch"] in bgroup:
    tested["heaven_stem_tomb"].append({
     "palace":p,"heaven_stem":carried,"tomb_branch":tomb["branch"],
     "source_lines":tomb["source_lines"]})
 for fac,arr in tested.items():
  # seasonal state is reported for all 8 doors, therefore known even if
  # none is special. For others absence is a real rule-evaluated absence.
  factors[fac]=_fact("present" if arr else "absent",
    "shenqi/shijia_symbols_ch04/v1:source_relation_lines",
    {"matches":arr,"source_data_sha256":rel["source_chapter_sha256"],
     "month_branch":month,"day_branch":day,
     "scope":"original source-defined branch and gate season only"})
 return factors

def _traditional_decision(base,source_refs,*,intent):
 """Source-backed hierarchical rules; not invented probabilities or a vote."""
 mine=_year_actor(base,"subject")
 other=_year_actor(base,"partner")
 if mine is None or other is None:
  return {"outcome":"unresolved","support":[],"counter":[],
          "issues":["both_true_subject_partner_birth_year_pillars_required"],
          "priority":"actual_both_year_stems_first_no_gender_assumption"}
 pm,po=mine["palace"],other["palace"]
 if pm==5 or po==5:
  return {"outcome":"unresolved","support":[],"counter":[],
          "issues":["central_five_palace_requires_original_specific_hosting"],
          "priority":"source_center_five_not_fabricated"}
 relation=element_relation(ELEMENTS[pm],ELEMENTS[po])
 positive=[];negative=[]
 main=_evidence("primary_two_real_birth_years",[pm,po],relation,
   "person_palace",source_refs,
   "双方实际年命落宫相互关系为主证，乙庚性别模板不能覆盖真人年命")
 if relation in POSITIVE:positive.append(main)
 if relation in NEGATIVE:negative.append(main)
 liuhe=base["role_candidates_not_final_yongshen"]["liuhe"][0]["palace"]
 if liuhe!=5:
  lm=element_relation(ELEMENTS[liuhe],ELEMENTS[pm])
  lo=element_relation(ELEMENTS[liuhe],ELEMENTS[po])
  # Book '六合' is supportive marriage situation, not a proxy for any person.
  if lm in ("生","比和") and lo in ("生","比和"):
   positive.append(_evidence("secondary_liuhe",[liuhe,pm,po],lm+"/"+lo,
     "liuhe",source_refs,"六合宫同时扶助双方，为婚缘或关系纽带辅证"))
  elif lm=="克" or lo=="克":
   negative.append(_evidence("secondary_liuhe",[liuhe,pm,po],lm+"/"+lo,
     "liuhe",source_refs,"六合宫与一方相克，作为双方主证的反证"))
 # Determine traditional explicit outcome by PRIMARY, with a reversible
 # contradiction status. If secondary differs, outcome is 'mixed' not
 # majority rule. Negative evidence is never suppressed for a happy script.
 if relation in POSITIVE:
  outcome="mixed" if negative else "success"
 else:
  outcome="mixed" if positive else "failure"
 return {"outcome":outcome,"support":positive,"counter":negative,
         "issues":[],"priority":"primary_real_birth_year_relation_then_secondary_liuhe",
         "primary_relation":relation,"primary_palaces":[pm,po],
         "secondary_liuhe_palace":liuhe,
         "author_rule_not_mathematical_probabilities":True}

def analyze_marriage_unseen_chart(*,db_path,payload,held_out_family_id=None):
 """No book case outcome may be passed to, or read by, the verdict function."""
 if held_out_family_id is not None and (
    not isinstance(held_out_family_id,str) or not held_out_family_id):
  raise ValueError("Heldout must be an entire event family ID")
 base=inspect_marriage_chart_json(db_path=db_path,payload=payload)
 calendar=base.get("astronomical_local_calendar_receipt")
 chart=base["source_chart"]
 if not calendar:
  return {"status":"blocked_unverified_calendar",
          "source_chart_input":base,
          "initial_traditional_verdict":None,
          "final_timing_decision":None,
          "why":"An unverified supplied sexagenary timestamp cannot produce a forecast"}
 with sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro",uri=True) as db:
  refs=_load_rules_and_source(db)
  witness=_source_witnesses(db,payload["inquiry"]["scene_id"],
                           held_out_family_id=held_out_family_id)
 if not witness["pre_event_method_witnesses"]:
  return {"status":"blocked_no_nonheldout_author_method_witness",
          "heldout_family_id":held_out_family_id,
          "original_heldout_labels_not_loaded":True,
          "initial_traditional_verdict":None}
 factors=grounded_factor_extensions(base["factor_audit"],chart,calendar)
 # PRIMARY RULES learn methods from chapter, not specific case's verdict.
 verdict=_traditional_decision(base,refs,intent=base["parent_intent_id"])
 # If pivotal site has 月/日破、入墓 or 门迫, make it explicit
 # counterevidence; never secretly nullify a positive relation.
 primary=verdict.get("primary_palaces",[])
 if primary:
  for fac in ("month_day_break","heaven_stem_tomb"):
   for match in factors[fac]["evidence"]["matches"]:
    if match["palace"] in primary:
     verdict["counter"].append(_evidence(
      "source_obstruction",[match["palace"]],fac,"book_exception",
      refs,fac+"（详见已核符号出处）"))
  pressed=factors["door_press_palace"]["evidence"]["exact_mechanical_door_press_palaces"]
  for match in pressed:
   if match["palace"] in primary:
    verdict["counter"].append(_evidence(
     "source_obstruction",[match["palace"]],"门迫","book_exception",
     refs,"门五行克该用神落宫，不能只看年命相生"))
  if verdict["outcome"]=="success" and verdict["counter"]:
   verdict["outcome"]="mixed"
 relevant=base["traditional_void_timing_hypotheses"] if "traditional_void_timing_hypotheses" in base else {}
 observed_void=relevant.get("liuhe_palace_void_branches",[])
 methodname=("clash_empty" if verdict["outcome"]=="success" else
             "fill_empty" if verdict["outcome"]=="failure" else None)
 family_rules=load_source_timing_rules()
 timing=None
 if methodname and observed_void:
  # Only XunKong branches actually in 六合宫 are eligible. If 六合宫 has
  # 1 palace branch in void and 1 not, do not treat all 2 as active.
  periodic=branch_periods(payload["calendar_inputs"]["local_time_iso"],
     payload["calendar_inputs"]["iana_timezone"],granularity="month",days_ahead=370)
  sourcekey="successful_outcome:4" if methodname=="clash_empty" else "failed_outcome:3"
  ref="kaiwu/analysis_judgment_ch04/v1:line"+str(family_rules[sourcekey]["source_line"])
  choices=derive_timing_candidates(empty_branches=observed_void,periods=periodic,
     granularity="month",method=methodname,
     reference_iso=payload["calendar_inputs"]["local_time_iso"],
     calendar_method_version=EPHEMERIS_VERSION,
     calendar_receipt=calendar["sha256"],source_method_ref=ref)
  if choices:
   timing=finalize_traditional_decision(
    outcome=verdict["outcome"],reasoned_support=(
      verdict["support"] if verdict["outcome"]=="success" else verdict["counter"]),
    reasoned_counter=(
      verdict["counter"] if verdict["outcome"]=="success" else verdict["support"]),
    chosen_timing=choices[0],known_timing_candidates=choices,
    timing_choice_rule_ref=ref,
    confidence_boundary=TRADITIONAL_BOUNDARY)
    # Keep alternative dates for human-readable counterfactual audit.
   timing["other_computed_candidates"]=choices[1:]
 # Leave unresolved interpretation without invented dates.
 audit={
  "status":"source_rule_decision_and_conditioned_timing" if timing else
            "source_rule_decision_requires_more_event_timing_conditions",
  "scene_id":base["scene_id"],"question":base["actual_input_inquiry"]["question_text"],
  "traditional_initial_outcome":verdict["outcome"],
  "decisive_priority":verdict["priority"],
  "initial_judgment":verdict,
  "source_only_book_method_refs":refs,
  "book_witnesses_excluding_holdout":witness,
  "fact_audit_all_24":factors,
  "fact_calculated_count":sum(x["status"] in ("present","absent") for x in factors.values()),
  "full_book_source_non_feedback_rule_check":True,
  "complete_24_rule_coverage":all(x["status"]!="unknown" for x in factors.values()),
  "verified_civil_calendar":True,
  "astronomical_clock_receipt":calendar,
  "calculated_timing_if_source_condition_met":timing,
  "concrete_initial_aurthor_case_verdict_read":False,
  "unseen_family_post_event_information_was_read":False,
  "not_scientifically_verified_event_forecast":True,
  "publication_ready":False,
  "publication_blockers":[
   "global_24_factor_rule_interpreter_not_all_source_verified",
   "nine_scene_yongshen_priority_and_fuyin_tomb_horse_not_all_composed",
   "independent_event_family_blind_accuracy_not_yet_established"]
 }
 if verdict["outcome"]=="unresolved":
  audit["publication_blockers"].append("true_dual_birth_year_palaces_not_bound")
 if not timing:
  audit["publication_blockers"].append(
   "no_source_applicable_concrete_timing_or_conflicting_primary_evidence")
 return audit
