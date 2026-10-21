"""Source-tested chart facts -> marriage 22-scene case evidence preview.

The two original Shenqi printed-example layouts are useful for regression;
neither is an original marriage inquiry.  This research adapter MUST NOT
turn them into a real romantic prediction or claim an independently verified
calendar/casting receipt. It resolves actual sun/earth palaces and mechanical
door-pressure, void branches, palace elements, and source witnesses instead
of hallucinating a complete six-layer reading.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from .casting_shenqi import (
    BRANCHES,STEMS,cycle60,bureau_for_term,layout_from_explicit_bureau,
    xun_shou)
from .phrase_pipeline import FACTOR_IDS
from .six_layer_contract import LAYERS

ELEMENTS={1:"水",2:"土",3:"木",4:"木",5:"土",6:"金",7:"金",8:"土",9:"火"}
DOOR_ELEMENTS={"休门":"水","生门":"土","伤门":"木","杜门":"木",
               "景门":"火","死门":"土","惊门":"金","开门":"金"}
PRODUCES={"木":"火","火":"土","土":"金","金":"水","水":"木"}
CONTROLS={"木":"土","土":"水","水":"火","火":"金","金":"木"}
# Two source-chapter original worked diagrams, ALL nine cells compared in tests.
SOURCE_EXAMPLES={
 "shenqi_casting_example_1995_06_11":{
  "day_ganzhi":"癸酉","solar_term":"芒种","dun":"yang","ju":3,
  "hour_ganzhi":"丁巳","xun_shou":"甲寅",
  "school_source":"shenqi/shijia-qiju/v1-20261019",
  "original_text_status":"chapter01_two_completed_original_examples_source_only"},
 "shenqi_casting_example_1995_08_13":{
  "day_ganzhi":"丙子","solar_term":"立秋","dun":"yin","ju":8,
  "hour_ganzhi":"戊戌","xun_shou":"甲午",
  "school_source":"shenqi/shijia-qiju/v1-20261019",
  "original_text_status":"chapter01_two_completed_original_examples_source_only"}
}
PALACE_BRANCHES={1:("子",),2:("未","申"),3:("卯",),4:("辰","巳"),
                 5:(),6:("戌","亥"),7:("酉",),8:("丑","寅"),9:("午",)}

def element_relation(left,right):
 if left==right:return "比和"
 if PRODUCES[left]==right:return "生"
 if CONTROLS[left]==right:return "克"
 if PRODUCES[right]==left:return "受生"
 if CONTROLS[right]==left:return "受克"
 raise ValueError("Invalid five-element chart cells")

def hourly_void_branches(hour_ganzhi):
 head,_,_=xun_shou(hour_ganzhi)
 cycle=cycle60()
 i=cycle.index(head)
 non_void={cycle[(i+k)%60][1] for k in range(10)}
 missing=[b for b in BRANCHES if b not in non_void]
 if len(missing)!=2:raise ValueError("Invalid Jia-Xun or empty branches")
 return {"xun_head":head,"xun_kong_branches":missing}

def _palace_mapping(chart):
 mp={}
 for raw in chart["palaces"].values():
  p=raw["palace"]
  if p not in ELEMENTS:raise ValueError("Unexpected original palace")
  for item in raw["heaven_stars"]:
   mp.setdefault(item["carried_stem"],[]).append({
    "palace":p,"star":item["star"],
    "carried_stem":item["carried_stem"],
    "earth_stem":raw["earth_stem"],"door":raw["door"],"deity":raw["deity"]})
 return mp

def _fact(status,rule,evidence,reason=None):
 return {"checked":True,"status":status,"rule_ref":rule,"evidence":evidence,
         **({"reason":reason} if reason else {})}

def compute_source_chart_factors(chart):
 """Only compute elements justified by actual chart cells, do not invent 暗干."""
 cells=chart["palaces"]
 stems=_palace_mapping(chart)
 press=[]
 for key,cell in cells.items():
  p=int(key); door=cell["door"]
  if door is None:
   if p!=5:raise ValueError("Noncentral palace without original door")
   continue
  if door not in DOOR_ELEMENTS:raise ValueError("Unexpected eight door symbol")
  e=DOOR_ELEMENTS[door]
  if CONTROLS[e]==ELEMENTS[p]:
   press.append({"palace":p,"door":door,"door_element":e,
                 "palace_element":ELEMENTS[p],
                 "rule":"door_element_controls_palace_element"})
 empty=hourly_void_branches(chart["hour_ganzhi"])
 potential_void=[{"palace":p,"branches":list(set(PALACE_BRANCHES[p])&
                      set(empty["xun_kong_branches"]))}
                for p in ELEMENTS
                if set(PALACE_BRANCHES[p])&set(empty["xun_kong_branches"])]
 door_rows=[{"palace":int(k),"door":v["door"],"deity":v["deity"],
             "heaven_stars":v["heaven_stars"],"earth_stem":v["earth_stem"]}
            for k,v in cells.items()]
 facts={fac:_fact("unknown","not_yet_verified_from_two_book_originals",
             {"source_chart":chart["source_key"],"factor":fac},
             "Requires original-book-specific applicable condition / full source data")
        for fac in FACTOR_IDS}
 facts["door_press_palace"]=_fact("present" if press else "absent",
   "basic_five_elements:door_over_palace;source_review_pending",
   {"exact_mechanical_door_press_palaces":press,
    "rule_warning":"杜门木落震木 NOT 门迫; percentages never invented"})
 facts["xun_kong"]=_fact("present","six_jia_xun_ten_hour_complement",
  {"hour_ganzhi":chart["hour_ganzhi"],**empty,
   "possible_palaces_based_on_conventional_branches_not_original_cast_verified":potential_void})
 facts["palace_five_elements"]=_fact("present","fixed_eight_trigram_palace_elements",
   [{"palace":p,"element":ELEMENTS[p]} for p in range(1,10)])
 facts["heaven_earth_stem_structure"]=_fact("present",
  "shenqi_original_casting_chapter01_heavenly_stem_carried_by_star",
  {"heaven_stem_carrier_matches":stems,
   "warning":"甲六仪隐遁不可直接当作天盘甲；中心寄宫需原书分辨"})
 facts["star_door_deity_structure"]=_fact("present",
  "shenqi_original_casting_chapter01_nine_cell_regression",door_rows)
 facts["palace_interactions"]=_fact("unknown","cross_actor_pillars_required",
  {"palace_elements":ELEMENTS},
  "Cannot choose which two palaces to compare before actual asker/subject/partner binding")
 return facts

def inspect_marriage_study_cast(*,db_path,scene_id,day_ganzhi,solar_term,
                                 hour_ganzhi,example_key=None,people=None):
 """Read full versioned SQLite source links; calculate no imaginary final forecast."""
 if not isinstance(scene_id,str) or not scene_id.startswith("marriage.scene."):
  raise ValueError("Choose one persisted 22-marriage scenario ID")
 if day_ganzhi not in cycle60() or hour_ganzhi not in cycle60():
  raise ValueError("Supplied day and hour MUST be valid sexagenary")
 if not isinstance(solar_term,str):
  raise ValueError("Explicit solar term required")
 bureau=bureau_for_term(day_ganzhi,solar_term)
 chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],
                                  hour_ganzhi=hour_ganzhi)
 sample=SOURCE_EXAMPLES.get(example_key)
 if example_key is not None:
  if sample is None:raise ValueError("Unknown actual historical casting example")
  for k in ("day_ganzhi","solar_term","hour_ganzhi","dun","ju"):
   supplied={"day_ganzhi":day_ganzhi,"solar_term":solar_term,
             "hour_ganzhi":hour_ganzhi,"dun":bureau["dun"],"ju":bureau["ju"]}[k]
   if supplied!=sample[k]:
    raise ValueError("The named source-example input was changed: "+k)
  if xun_shou(hour_ganzhi)[0]!=sample["xun_shou"]:
   raise ValueError("Xun-head disagreement with original worked chart")
 stems=_palace_mapping(chart)
 facts=compute_source_chart_factors(chart)
 if people is None:people={}
 if not isinstance(people,dict):raise ValueError("People roles require a JSON object")
 day=day_ganzhi[0]
 day_stem_palaces=stems.get(day,[])
 hour_stem_palaces=stems.get(hour_ganzhi[0],[])
 yi=stems.get("乙",[])
 geng=stems.get("庚",[])
 liuhe=[{"palace":v["palace"],"door":v["door"],"earth_stem":v["earth_stem"]}
        for v in chart["palaces"].values() if v["deity"]=="六合"]
 if len(liuhe)!=1:raise ValueError("Original casting must locate exactly one 六合")
 if not day_stem_palaces or not hour_stem_palaces:
  raise ValueError("Day/hour carried-stem location incomplete")
 # Same input state may refer to different people, so role binding is explicit.
 roles={"day_stem":day,"day_stem_palaces":day_stem_palaces,
        "hour_stem":hour_ganzhi[0],"hour_stem_palaces":hour_stem_palaces,
        "yi_traditional_candidate":yi,"geng_traditional_candidate":geng,
        "liuhe":liuhe,"external_people_bound":bool(people),
        "people_user_supplied_only":people}
 with sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro",uri=True) as db:
  row=db.execute("""SELECT title,parent_intent_id,target_event,evidence_grade,
    protocol_json FROM marriage22_scenario_protocol WHERE scene_id=?""",(scene_id,)).fetchone()
  if row is None:raise ValueError("Unknown approved-source-backed marriage scenario")
  sources=db.execute("""SELECT book_id,section_key,original_source_sha256,
    original_case_id,source_lines_json,source_snippets_json,
    source_phase,feedback_not_initial_reasoning
    FROM marriage22_original_case_links WHERE scene_id=?
    ORDER BY source_ordinal""",(scene_id,)).fetchall()
  if not sources:raise ValueError("Scene has no historical book evidence source")
  originals=[];validation_only=[]
  for bk,key,digest,case,line_json,snippet_json,phase,feedback in sources:
   item={"book_id":bk,"source_section_key":key,"original_source_sha256":digest,
    "case_id":case,"source_line_numbers":json.loads(line_json),
    "original_excerpt":json.loads(snippet_json),"original_phase_role":phase}
   if feedback:validation_only.append(item)
   else:originals.append(item)
 ref_2=elements=ELEMENTS
 example_fidelity="two_source_chapter_example_input_cross_checked" if sample else "explicit_bureau_not_original_example_proven"
 blockers=["calendar_solar_term_provided_not_independently_verified",
           "casting_variant_matches_two_examples_only",
           "24_original_factors_not_fully_computed",
           "no_source_approved_combined_marriage_outcome_rule",
           "no_independently_verified_event_timing_calendar"]
 if not people:blockers.append("specific_marriage_people_and_birth_year_ganzhi_not_provided")
 return {
  "status":"research_partial_chart_pipeline_not_final_forecast",
  "scene_id":scene_id,"target_event":row[2],"parent_intent_id":row[1],
  "evidence_strength":row[3],
  "source_example_attestation":example_fidelity,
  "source_chart":chart,"bureau_from_explicit_term":bureau,
  "role_candidates_not_final_yongshen":roles,
  "factor_audit":facts,"factor_checked_count":len(facts),
  "factor_mechanically_resolved_count":sum(x["status"] in ("present","absent") for x in facts.values()),
  "author_first_and_method_source_links":originals,
  "source_later_feedback_validation_only":validation_only,
  "six_layer_execution_status":{
   LAYERS[0]:"source_example_consistency" if sample else "unverified_explicit_bureau",
   LAYERS[1]:"partial_mechanical_known_and_unknown",
   LAYERS[2]:"candidate_roles_not_confirmed",
   LAYERS[3]:"book_sources_retrieved_without_feedback_leakage",
   LAYERS[4]:"blocked_no_source_approved_forecast_timing",
   LAYERS[5]:"not_called_missing_structured_outcome"},
  "missing_to_publish":blockers,
  "traditional_forecast_result":None,
  "calculated_primary_timing":None,
  "human_natural_phrase":None,
  "book_accuracy_independently_verified":False}
