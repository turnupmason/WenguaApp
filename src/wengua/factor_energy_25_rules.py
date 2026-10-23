"""Wengua V-next deterministic 25-cell strength heuristics; NOT a forecast.

Five symbol-palace relations x five monthly stages. The value labels are a
versioned engineering proposal, not derived book-author certainty.
"""
from __future__ import annotations

from .factor_energy_review import inspect_symbol_energy
from .semantic_lookup import GENERATES, CONTROLS

RELATIONS=("宫生符号","比和","符号生宫","符号克宫","宫克符号")
STAR_STAGES=("旺","相","休","囚","废")
EARTH_STAGES=("旺","相","休","囚","死")
TIERS=("极小","小","中等","大","极大")
RANK={s:i for i,s in enumerate(TIERS)}
# Every entry is explicitly fixed, ordered by RELATIONS.
STAR_25={
 "旺":("极大","极大","大","大","中等"),
 "相":("极大","大","中等","中等","小"),
 "休":("大","中等","小","小","极小"),
 "囚":("中等","小","极小","极小","极小"),
 "废":("小","极小","极小","极小","极小")}
ORDINARY_25={
 "旺":("极大","极大","大","大","中等"),
 "相":("极大","大","中等","中等","小"),
 "休":("大","中等","小","小","极小"),
 "囚":("中等","小","极小","极小","极小"),
 "死":("小","极小","极小","极小","极小")}
# Gods have no inherent monthly stage. Its matrix concerns the monthly
# strength of the LANDING PALACE, not the deity's own month.
DEITY_PALACE_25=dict(ORDINARY_25)
PALACE_TIERS={"旺":"极大","相":"大","休":"中等","囚":"小","死":"极小"}
METHOD="source_facts_plus_proposed_25_labels_v1"

def lookup_25(kind,stage,relation):
    kind={"九星":"star","八门":"door","天干":"stem","八神":"deity"}.get(kind,kind)
    if kind=="star": table,stages=STAR_25,STAR_STAGES
    elif kind in ("door","stem"):table,stages=ORDINARY_25,EARTH_STAGES
    elif kind=="deity":table,stages=DEITY_PALACE_25,EARTH_STAGES
    else:raise ValueError("Unknown kind")
    if stage not in stages or relation not in RELATIONS:
        raise ValueError("Unknown moon stage or directed relationship")
    index=RELATIONS.index(relation)
    return {"matrix_id":METHOD+":"+kind,"case_number":stages.index(stage)*5+index+1,
            "stage":stage,"relation":relation,"strength":table[stage][index],
            "status":"uncalibrated_review_heuristic"}

def inspect_strength_25(kind,symbol,month_branch,palace,*,plane="heaven",restrictions=()):
    if plane not in ("heaven","earth"):raise ValueError("Sky/earth plane required")
    facts=inspect_symbol_energy(kind,symbol,month_branch,palace)
    stage=(facts["palace_month_stage"] if facts["kind"]=="deity"
           else facts["symbol_month_stage"])
    rule=lookup_25(facts["kind"],stage,facts["nominal_relation_from_symbol"])
    landing=PALACE_TIERS[facts["palace_month_stage"]]
    blocked=list(dict.fromkeys(restrictions))
    return {**facts,**rule,"plane":plane,
      "fact_id":f"energy25:{facts['kind']}:{facts['symbol']}:{plane}:{palace}:{month_branch}",
      "strength_label":rule["strength"],"palace_strength_label":landing,
      "symbol_palace_conflict":abs(RANK[rule["strength"]]-RANK[landing])>=2,
      "restrictions":blocked,
      "strength_meaning":("落宫承载候选，八神自身无月令五态" if facts["kind"]=="deity"
                          else "月令和符号对宫关系的定性候选"),
      "effective_status":("conditions_unverified" if blocked else
                          "symbol_palace_conflict" if abs(RANK[rule["strength"]]-RANK[landing])>=2
                          else "review_conditional"),
      "one_compound_fact":True,"usable_as_final_verdict":False}

def _palace_relation(a,b):
    if a==b:return "比和"
    if CONTROLS[a]==b:return "克"
    if CONTROLS[b]==a:return "被克"
    if GENERATES[a]==b:return "生"
    if GENERATES[b]==a:return "被生"
    raise ValueError("Invalid five elements")

def compare_role_strength(actor,target,*,actor_name="施力方",target_name="受力方"):
    for item in (actor,target):
        if not item.get("matrix_id") or item.get("palace_strength_label") not in RANK:
            raise ValueError("Fully inspected factor required")
    relation=("同宫" if actor["palace"]==target["palace"]
              else _palace_relation(actor["palace_element"],target["palace_element"]))
    if relation!="克":
        outcome="不适用";reason="本方宫没有克对方宫，不能套用克制效果"
    elif actor["restrictions"] or target["restrictions"]:
        outcome="条件待核";reason="空墓刑迫候选需核定，名义相克不代表作用已经发生"
    elif (RANK[actor["strength_label"]]>=3 and RANK[actor["palace_strength_label"]]>=3
          and RANK[target["strength_label"]]<=1 and RANK[target["palace_strength_label"]]<=1):
        outcome="能";reason="施力方符号和宫均旺、受力方符号和宫均弱，传统作用条件较充分"
    elif (RANK[actor["strength_label"]]<=1 and RANK[actor["palace_strength_label"]]<=1
          and RANK[target["strength_label"]]>=3 and RANK[target["palace_strength_label"]]>=3):
        outcome="不能";reason="施力方符号和宫均弱、受力方均旺，名义相克难以落实"
    else:
        outcome="艰难";reason="符号与宫旺衰有冲突或强弱未明显悬殊，仍需其他原书证据"
    return {"actor":actor_name,"target":target_name,"relation":relation,
            "ability_to_control":outcome,"why":reason,
            "actor_strength":actor["strength_label"],
            "target_strength":target["strength_label"],
            "actor_palace_strength":actor["palace_strength_label"],
            "target_palace_strength":target["palace_strength_label"],
            "actor_fact_id":actor["fact_id"],"target_fact_id":target["fact_id"],
            "is_final_verdict":False,"additional_evidence_vote":False}

def format_strength_template(fact):
    if fact["kind"]=="deity":
        return (f"{fact['symbol']}不单算自身月令，落宫月令{fact['palace_month_stage']}，"
                f"神宫{fact['relation']}，第{fact['case_number']}格，"
                f"宫内承载{fact['strength_label']}。")
    return (f"{fact['symbol']}月令{fact['symbol_month_stage']}，对落宫{fact['relation']}，"
            f"第{fact['case_number']}格，符号力量{fact['strength_label']}；"
            f"宫月令{fact['palace_month_stage']}，宫力{fact['palace_strength_label']}。")

def format_duel_template(result):
    a=result["actor"];b=result["target"]
    return (f"{a}宫对{b}宫为{result['relation']}；"
            f"符号力量{result['actor_strength']}/{result['target_strength']}，"
            f"宫力{result['actor_palace_strength']}/{result['target_palace_strength']}。"
            f"制约判定{result['ability_to_control']}：{result['why']}。")
