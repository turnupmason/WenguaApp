"""V1.7 sourced, executable marriage multi-evidence *candidate* rule combinator.

Implements executable facts separately from genre/author outcome judgment.
Source anchors are verified against canonical SHA of TWO Kaiwu chapters,
plus 81 directional ten-stem combinations. Scores are NOT arbitrary numbers,
no family labels are fed in and nobody can be identified from a chart.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import hashlib,json
from .casting_shenqi import DOORS,STARS,cycle60
from .marriage_runtime import ELEMENTS,PALACE_BRANCHES,CONTROLS,PRODUCES,element_relation
from .astro_calendar import solar_chart_clock,branch_periods
from .symbol_relations import door_season
ROOT=Path(__file__).resolve().parents[2]
RULES=ROOT/"data/knowledge/phrase_library/marriage_v1_7/original_combo_rules.json"
PAIRS=ROOT/"data/knowledge/kaiwu/analysis_judgment_ch04/ordered_stem_pairs.json"
FOURTH=ROOT/"sources/kaiwu/开悟之门_第四章.txt"
MARRIAGE=ROOT/"sources/kaiwu/开悟之门_恋爱婚姻预测.txt"
MONTH_ELEMENT={"寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土",
               "申":"金","酉":"金","戌":"土","亥":"水","子":"水","丑":"土"}
STEM_ELEMENT={"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
              "庚":"金","辛":"金","壬":"水","癸":"水"}
# Six examples are EXACT rules in Kaiwu chapter4 lines 510-520.
SIX_YI={"戊":3,"己":2,"庚":8,"辛":9,"壬":4,"癸":4}
TRI_TOMB={"乙":6,"丙":6,"丁":8}
OPPOSITE={1:9,9:1,2:8,8:2,3:7,7:3,4:6,6:4}
HORSE={
 "申":"寅","子":"寅","辰":"寅",
 "寅":"申","午":"申","戌":"申",
 "巳":"亥","酉":"亥","丑":"亥",
 "亥":"巳","卯":"巳","未":"巳"}
REFERENCE_BASIS="traditional_source_conditional_not_real_world_probability"

@lru_cache(maxsize=1)
def load_author_source_rules():
 j=json.loads(RULES.read_text("utf8"))
 if j["schema"]!="wengua_marriage_original_multi_book_conditional_rules_v17":
  raise ValueError("Unrecognized marriage rules schema")
 d={"fourth":FOURTH,"kaiwu_marriage":MARRIAGE}
 hash_expected={"fourth":"ce3203902f6fa2e129d13899e19ef4a3d02e8698f38eac3dbe7383ba550a2cf4",
 "kaiwu_marriage":"4df9dfe432daec759df4f0e01449bc4a2381eb4251e1290a0d99d199e467fa01"}
 books={}
 for k,file in d.items():
  b=file.read_bytes()
  if hashlib.sha256(b).hexdigest()!=hash_expected[k]:
   raise ValueError("Original full source book chapter SHA changed: "+k)
  books[k]=b.decode("utf8").splitlines()
 rules={}
 for r in j["rules"]:
  key="fourth" if r["source_section_key"]=="analysis_judgment_ch04" else "kaiwu_marriage"
  lines=books[key]
  n=r["source_line"]
  if not 1<=n<=len(lines) or lines[n-1]!=r["original_line"] or r["source_sha256"]!=hash_expected[key]:
   raise ValueError("Rule original Chinese source line drift: "+r["rule_id"])
  rr=dict(r)
  rr["excerpt_sha256"]=hashlib.sha256(rr["original_line"].encode("utf8")).hexdigest()
  if rr["rule_id"] in rules:raise ValueError("Duplicate author rule ID")
  rules[rr["rule_id"]]=rr
 if len(rules)!=j["rule_count"]:raise ValueError("Original rule count drift")
 pairs=json.loads(PAIRS.read_text("utf8"))
 pair_index={}
 for x in pairs["pairs"]:
  if (x["top"],x["bottom"]) in pair_index:raise ValueError("Direction of stem pair lost")
  if hashlib.sha256(x["source_original"].encode("utf8")).hexdigest()!=x["excerpt_sha256"]:
   raise ValueError("Original directional-stem text altered")
  n=x["source_line"]
  if books["fourth"][n-1]!=x["source_original"]:
   raise ValueError("Original Kaiwu 81-stem text source mismatch")
  pair_index[(x["top"],x["bottom"])]=x
 if len(pair_index)!=81:raise ValueError("Missing source 81 directional heaven/earth combinations")
 return rules,pair_index

def palace_map(chart):
 return {int(k):v for k,v in chart["palaces"].items()}

def _qi(month_element,element):
 if month_element==element:return "旺"
 if PRODUCES[month_element]==element:return "相"
 if PRODUCES[element]==month_element:return "休"
 if CONTROLS[element]==month_element:return "囚"
 if CONTROLS[month_element]==element:return "死"
 raise ValueError("Unknown month element interaction")
def _carrier_positions(chart):
 out={}
 for cell in chart["palaces"].values():
  for star in cell["heaven_stars"]:
   out.setdefault(star["carried_stem"],[]).append(cell["palace"])
 return out
def _source_match(book_rule,*,palace,trigger,qualifier=None):
 return {"rule_id":book_rule["rule_id"],"book_id":book_rule["book_id"],
  "section_key":book_rule["source_section_key"],"line":book_rule["source_line"],
  "book_source_sha256":book_rule["source_sha256"],
  "exact_original_line_sha256":book_rule["excerpt_sha256"],
  "palace":palace,"computed_symbol_condition":trigger,
  "qualifier":qualifier,"cannot_determine_real_world_personality_or_health":True}

def compute_author_combinations(chart,calendar):
 """Only compute source-defined symbol facts; unproven triggers stay marked."""
 rules,pairs=load_author_source_rules()
 if chart.get("status")!="source_text_consistency_only":
  raise ValueError("Chart label alone does not constitute verified source casting")
 if calendar.get("method") is None or not calendar.get("four_pillars"):
  raise ValueError("Independently calculated civil solar clock required")
 ppl=palace_map(chart)
 stems=_carrier_positions(chart)
 bz=calendar["four_pillars"]
 month_branch=bz["month"][1]
 year_branch=bz["year"][1]
 if month_branch not in MONTH_ELEMENT:raise ValueError("Unexpected lunar month branch")
 month_el=MONTH_ELEMENT[month_branch]
 twelve_season_states={p:{"palace":p,"month_branch":month_branch,
   "month_element":month_el,"palace_element":ELEMENTS[p],
   "season_state":_qi(month_el,ELEMENTS[p]),
   "standard_wang_xiang_xiu_qiu_si":True,
   "four_earth_transition_exact_solar_day_subperiod_unresolved":month_branch in "辰未戌丑"}
   for p in ppl}
 marks={"six_yi_striking_punishment":[],"sanqi_tomb":[],
        "time_stem_tomb":[],"time_horse":[],
        "tai_sui_linkage":[],"heaven_earth_stem_paired":[],
        "door_pressure_strength":[]}
 for stem,target in SIX_YI.items():
  if target in stems.get(stem,[]):
   marks["six_yi_striking_punishment"].append(_source_match(
    rules["six_yi_"+str(list(SIX_YI).index(stem)+1)],
    palace=target,trigger="天盘六仪"+stem+"落"+str(target)+"宫"))
 for stem,target in TRI_TOMB.items():
  if target in stems.get(stem,[]):
   marks["sanqi_tomb"].append(_source_match(
    rules["sanqi_tomb"],palace=target,
    trigger="天盘"+stem+"奇入墓（定义落宫）"))
 time_stem=bz["hour"][0]
 for place in stems.get(time_stem,[]):
  if (time_stem in TRI_TOMB and place==TRI_TOMB[time_stem]):
   marks["time_stem_tomb"].append(_source_match(
    rules["sanqi_tomb"],palace=place,
    trigger="时干本身三奇入墓，旺衰分入墓入库未独立下结论"))
 # Existing source 81 directional pairs, preserving天盘>地盘 asymmetry.
 for p,cell in ppl.items():
  for star in cell["heaven_stars"]:
   top=star["carried_stem"];bottom=cell["earth_stem"]
   if (top,bottom) in pairs:
    q=pairs[top,bottom]
    marks["heaven_earth_stem_paired"].append({
     "palace":p,"heaven":top,"earth":bottom,
     "pair_key":q["pair_key"],"source_line":q["source_line"],
     "source_excerpt_sha256":q["excerpt_sha256"],
     "book_source_sha256":rules["stem_pair_relative"]["source_sha256"],
     "directional_interpretation_not_symmetric":True,
     "rule_claim_not_automatically_fatal":True})
  if p!=5 and cell["door"] is not None:
   gate=cell["door"];door_el={"休门":"水","生门":"土","伤门":"木","杜门":"木",
                              "景门":"火","死门":"土","惊门":"金","开门":"金"}[gate]
   if CONTROLS[door_el]==ELEMENTS[p]:
    door_state=_qi(month_el,door_el)
    palace_state=twelve_season_states[p]["season_state"]
    # Kaiwu ch4 l550 expressly disallows "resting gate defeats 旺宫".
    force=("blocked_by_month_strength" if door_state in ("休","囚","死")
            and palace_state in ("旺","相") else
            "strong_gate_over_weak_palace" if door_state in ("旺","相")
            and palace_state in ("休","囚","死") else
            "requires_other_book_context")
    marks["door_pressure_strength"].append(_source_match(
      rules["door_strength"],palace=p,trigger="门克宫",
      qualifier={"door":gate,"door_state":door_state,
                 "palace_state":palace_state,"force":force}))
 for year_p,bb in ((p,b) for p,bs in PALACE_BRANCHES.items() for b in bs if b==year_branch):
  for sym in ("subject","partner","liuhe"):
   pass # Personnel are resolved by question, not automatically by year branch.
  marks["tai_sui_linkage"].append(_source_match(
    rules["tai_sui_case"],palace=year_p,trigger="年支太岁宫（仅定位，不含成败）",
    qualifier={"year_branch":year_branch,"year_ganzhi":bz["year"],
               "not_universal_verdict":True}))
 horse=HORSE[bz["hour"][1]]
 for p,br in PALACE_BRANCHES.items():
  if horse in br:
   marks["time_horse"].append(_source_match(
      rules["horse"],palace=p,trigger="时支三合定马星",
      qualifier={"hour_branch":bz["hour"][1],"horse_branch":horse,
                 "must_be_active_for_event_timing":True}))
 # Seven distinct original matching claims: 星伏吟/门伏吟 independently.
 star_home={name:p for p,name in STARS.items() if p!=5}
 gate_home={name:p for p,name in DOORS.items()}
 starpositions={star["star"]:p for p,cell in ppl.items()
                for star in cell["heaven_stars"] if star["star"] in star_home}
 doorpositions={cell["door"]:p for p,cell in ppl.items() if cell["door"] in gate_home}
 if len(starpositions)!=8 or len(doorpositions)!=8:
  raise ValueError("Cannot pretend complete star-door fuyin with missing raw cells")
 sf=sum(starpositions[s]==home for s,home in star_home.items())
 df=sum(doorpositions[s]==home for s,home in gate_home.items())
 sr=sum(starpositions[s]==OPPOSITE[home] for s,home in star_home.items())
 dr=sum(doorpositions[s]==OPPOSITE[home] for s,home in gate_home.items())
 assert max(sf,df,sr,dr)<=8
 pattern={"star_fuyin":sf==8,"door_fuyin":df==8,
          "star_fanyin":sr==8,"door_fanyin":dr==8,
          "star_original_palaces":sf,"door_original_palaces":df,
          "star_opposite_palaces":sr,"door_opposite_palaces":dr,
          "fuyin_rule":_source_match(rules["star_door_fuyin"],palace=None,
                                     trigger="八星八门分别原宫"),
          "fanyin_rule":_source_match(rules["fanyin"],palace=None,
                                      trigger="八星八门分别对宫"),
          "jia_hour_exception":bz["hour"].startswith("甲"),
          "fuyin_not_necessarily_fatal":True}
 # day/hour actual positions independent of assertion about individual.
 dn=stems.get(bz["day"][0],[])
 tn=stems.get(bz["hour"][0],[])
 dayhour={"day_stem":bz["day"][0],"hour_stem":bz["hour"][0],
   "day_palaces":dn,"time_palaces":tn,
   "relations":[{"day":d,"hour":t,"relation":element_relation(ELEMENTS[d],ELEMENTS[t])}
                for d in dn for t in tn if d!=5 and t!=5],
   "original_source_rule":_source_match(rules["person_day_hour"],palace=None,
                    trigger="日干与时干在对应九宫以求测者和事体作综合参考"),
   "cannot_singlehandedly_predict_marriage":True}
 return {"source_rule_catalog_count":len(rules),"directional_stem_pair_count":len(pairs),
  "month_palace_strength":twelve_season_states,
  "source_rule_matches":marks,"fu_yin_fan_yin":pattern,
  "day_hour_specialized_relationship":dayhour,
  "seasonal_model_limitations":["辰未戌丑土季的精确交界需书源核对，不能取四季月同于全月稳定土势"],
  "traditional_symbolic_conditions_only":True}

def conditional_hierarchy(base,combo,old):
 """Evaluate conflict by explicit predicates, NOT by calibrated dev labels.

 This hierarchy is source candidate research. When decisive evidence conflicts
 mark MIXED: only aligned source corroboration permits a qualified decision.
 Do not treat inferred abuse, sex, criminality or future legality as facts.
 """
 rules,_=load_author_source_rules()
 initial=old["initial_judgment"]
 outcome=initial["outcome"]
 positives=list(initial.get("support",[]))
 negatives=list(initial.get("counter",[]))
 scene=base["scene_id"]
 male=base["role_candidates_not_final_yongshen"].get("geng_traditional_candidate",[])
 female=base["role_candidates_not_final_yongshen"].get("yi_traditional_candidate",[])
 liuhe=base["role_candidates_not_final_yongshen"].get("liuhe",[])
 if len(male)!=1 or len(female)!=1 or len(liuhe)!=1:
  return {"traditional_initial_outcome":"unresolved","reason":"basic male female 六合 palace candidates must be unique",
    "author_method_evidence_positive":positives,"author_method_evidence_negative":negatives,
    "source_rule_decision":"no_case_specific_inference"}
 mp,fp,lp=male[0]["palace"],female[0]["palace"],liuhe[0]["palace"]
 geom=[]
 if 5 not in (mp,fp,lp):
  ef=element_relation(ELEMENTS[mp],ELEMENTS[fp])
  efl=element_relation(ELEMENTS[lp],ELEMENTS[fp])
  eml=element_relation(ELEMENTS[lp],ELEMENTS[mp])
  geom=[
   {"source_rule":rules["liuhe_case"]["source_sha256"],"line":rules["liuhe_case"]["source_line"],
     "relation":"传统乙庚", "male_palace":mp,"female_palace":fp,"male_to_female":ef},
   {"source_rule":rules["tai_sui_case"]["source_sha256"],"line":rules["tai_sui_case"]["source_line"],
     "relation":"六合与乙庚", "liuhe_palace":lp,"liuhe_to_female":efl,"liuhe_to_male":eml}]
 else:
  return {"traditional_initial_outcome":"unresolved","reason":"center 5 requires original hosting",
    "author_method_evidence_positive":positives,"author_method_evidence_negative":negatives,
    "source_rule_decision":"source_center_not_fabricated"}
 # Source book case02 §97 has 乙庚对冲克; §§123/125 explicitly use 六合
 # against multiple actors. 乙庚相克 ALONE is not a deterministic verdict.
 if ef in ("克","受克"):
  negatives.append({"rule":"kaiwu/marriage_prediction_ch02_section02:line79",
    "evidence":"传统乙庚二宫相克，需与真实对象年命、时干、六合同参",
    "male_palace":mp,"female_palace":fp,"not_alone_fatal":True})
 else:
  positives.append({"rule":"kaiwu/marriage_prediction_ch02_section02:line175",
    "evidence":"传统乙庚宫比和/相生，只是一项正向辅证，不保证结果"})
 if efl in ("克","受克") or eml in ("克","受克"):
  negatives.append({"rule":"kaiwu/marriage_prediction_ch02_section02:line125",
    "evidence":"六合与乙庚双方之一有生克冲突，需与其他直接阻隔复核",
    "liuhe_palace":lp,"male_palace":mp,"female_palace":fp})
 for record in combo["source_rule_matches"]["six_yi_striking_punishment"]:
  if record["palace"] in (mp,fp,lp):
   negatives.append({"rule":record["rule_id"],"evidence":"六仪击刑与婚恋相关用神同宫",
    "palace":record["palace"],"not_necessarily_final":True})
 for record in combo["source_rule_matches"]["sanqi_tomb"]:
  if record["palace"] in (mp,fp):
   negatives.append({"rule":"sanqi_tomb","evidence":"男女一方传统符号入墓",
      "palace":record["palace"],"not_necessarily_final":True})
 for record in combo["source_rule_matches"]["door_pressure_strength"]:
  if record["palace"] in (mp,fp,lp) and record["qualifier"]["force"]!="blocked_by_month_strength":
   negatives.append({"rule":"door_press_qualified","evidence":"用神宫门克宫且未证实月令可抑制",
       "palace":record["palace"],"actual_force":record["qualifier"]["force"]})
 if combo["fu_yin_fan_yin"]["star_fanyin"] or combo["fu_yin_fan_yin"]["door_fanyin"]:
  negatives.append({"rule":"kaiwu/analysis_judgment_ch04:line574",
       "evidence":"实际星/门八宫反吟，全局婚事传统不利，不能只凭年命比和",
       "not_absolute":True})
 # Distinguish a *composite* counterweight from one isolated negative sign.
 # An initial positive requires review if 乙庚 or 六合 conflicts AND at
 # least one separate direct obstruction from other original source rules.
 legacy_core=[n for n in negatives if n.get("rule") in (
   "kaiwu/marriage_prediction_ch02_section02:line79",
   "kaiwu/marriage_prediction_ch02_section02:line125")]
 extra=[n for n in negatives if n.get("rule") not in (
   "kaiwu/marriage_prediction_ch02_section02:line79",
   "kaiwu/marriage_prediction_ch02_section02:line125")]
 conditional=outcome
 if outcome=="success" and legacy_core and extra:conditional="mixed"
 if outcome=="success" and combo["fu_yin_fan_yin"]["star_fanyin"] and combo["fu_yin_fan_yin"]["door_fanyin"]:
  conditional="mixed"
 if outcome=="failure" and len(positives)>len(negatives):
  # A source-counterexample doesn't magically reverse a negative primary.
  conditional="mixed"
 return {"traditional_initial_outcome":conditional,
  "legacy_initial_outcome":outcome,
  "positive_source_evidence":positives,"negative_source_evidence":negatives,
  "source_cross_palace_comparison":geom,
  "rule_conflict_priority":"primary_real_actors > special_乙庚/六合 > independently sourced刑墓迫反吟; unresolved when primary/secondary major contradictions",
  "not_arbitrary_numeric_weighting":True,
  "not_trained_against_v16_dev_posthoc_answers":True,
  "published_accuracy_claim":False}

def analyze_marriage_v17(*,db_path,payload,held_out_family_id=None):
 """New chart -> independently recomputed calendar, sourced multi-evidence.

 Wrapper retains V1.6 fields for historical comparisons, but DOES NOT copy
 its conclusion as published or force previously computed timing after the
 new conflict hierarchy changes the decision.
 """
 from .marriage_judgment_v16 import analyze_marriage_unseen_chart
 from .marriage_runtime import inspect_marriage_chart_json
 prior=analyze_marriage_unseen_chart(db_path=db_path,payload=payload,
                                   held_out_family_id=held_out_family_id)
 if "initial_judgment" not in prior:
  return {"status":"blocked_before_v17_rule_decision","baseline":prior}
 base=inspect_marriage_chart_json(db_path=db_path,payload=payload)
 clock=base.get("astronomical_local_calendar_receipt")
 if not clock:return {"status":"blocked_without_independent_calendar"}
 combo=compute_author_combinations(base["source_chart"],clock)
 adjudication=conditional_hierarchy(base,combo,prior)
 # Exactly ONE predicate path can request new timing after verdict. Old
 # V1.6 timing generated from different outcome must NEVER be inherited.
 old_v=prior["traditional_initial_outcome"]
 new_v=adjudication["traditional_initial_outcome"]
 eligible_timing=(new_v==old_v and new_v in ("success","failure") and
                  prior.get("calculated_timing_if_source_condition_met") is not None)
 timing=prior.get("calculated_timing_if_source_condition_met") if eligible_timing else None
 return {"status":"v17_author_source_conditioned_development_interpretation",
  "scene_id":base["scene_id"],"question":base["actual_input_inquiry"]["question_text"],
  "source_backed_combo":combo,
  "judgment":adjudication,"traditional_initial_outcome":new_v,
  "conditionally_defensible_timing":timing,
  "book_first_outcome_after_hierarchy_not_calibrated_to_old_dev_labels":True,
  "heldout_event_family_id":held_out_family_id,
  "all_24_factor_keys_audited":len(prior["fact_audit_all_24"]),
  "all_24_implemented_and_proven":prior["complete_24_rule_coverage"],
  "prior_book_witness_holdout_audit":prior["book_witnesses_excluding_holdout"],
  "post_event_feedback_used_in_verdict":False,
  "normal_200_character_GPT_reading_enabled":False,
  "release_approved":False,
  "reason_if_no_timing":"V1.7 changed/composite contradiction, or no qualifying original source timing event rule" if timing is None else None,
  "traditional_only_never_scientific_proof":True}
