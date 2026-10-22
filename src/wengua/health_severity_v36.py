"""V3.6: source-attested 值使三奇得使/玉女守门 and correct 时支驿马.

Never mutate earlier 12-source V3.5 readouts. Only exact chart facts
trigger a formation. Source definitions: 开悟之门第四章, (2)(3) and the
preparation section on 驿马. Patient-first V3.5 survives unchanged.
"""
from __future__ import annotations
import re
from .health_severity_v35 import analyze_health_severity_v35
from .health_severity_v22 import _find_heaven_stem, _palace
from .health_dynamic_v21 import bind_patient
from .marriage_runtime import PALACE_BRANCHES
from .casting_shenqi import SIX_JIA
from .health_severity_v34 import HORSE, _cell_stems

def _rechecked_composites(chart,person,ill,observations):
    revised=[]
    value=chart["palaces"][str(chart["value_door_palace"])]
    if value["door"]!=chart["value_door"]:
        raise ValueError("Value door palace does not match actual source star/door casting")
    for row in observations:
        i=int(row["id"][-2:])
        if i==7:
            odd=tuple(k for k in ("乙","丙","丁") if k in _cell_stems(value))
            x={"id":row["id"],"name":row["name"],
               "state":"triggered" if odd else "not_triggered",
               "evidence":[{"value_door":chart["value_door"],"value_door_palace":value["palace"],
                          "same_palace_heaven_three_wonders":odd,
                          "source":"kaiwu_ch04_section_三奇得使"}] if odd else [],
               "reason":"","source":"kaiwu_ch04_section_三奇得使"}
            revised.append(x)
        elif i==8:
            ok=value["earth_stem"]=="丁"
            revised.append({"id":row["id"],"name":row["name"],
               "state":"triggered" if ok else "not_triggered",
               "evidence":[{"value_door":chart["value_door"],"value_door_palace":value["palace"],
                   "earth_stem":"丁","source":"kaiwu_ch04_section_玉女守门"}] if ok else [],
               "reason":"","source":"kaiwu_ch04_section_玉女守门"})
        elif i==12:
            hour=chart["hour_ganzhi"]
            # 源书明确时辰取驿马，NOT previous V3.4 accidental day branch.
            if not isinstance(hour,str) or len(hour)!=2:
                raise ValueError("Actual hour pillar must contain a real branch")
            branch=hour[1];horse=HORSE[branch]
            roles=[role for role,cell in (("患者宫",person),("病宫",ill))
                   if horse in PALACE_BRANCHES[cell["palace"]]]
            revised.append({"id":row["id"],"name":row["name"],
                "state":"triggered" if roles else "not_triggered",
                "evidence":[{"hour_branch":branch,"horse_branch":horse,
                    "roles_in_horse_palace":roles,
                    "horse_palace":next(p for p,bs in PALACE_BRANCHES.items() if horse in bs),
                    "source":"kaiwu_ch04_preparation_时辰驿马"}],
                "reason":"有马星方位≠应期已到，需真实冲合方可判断变化",
                "source":"kaiwu_ch04_preparation_时辰驿马"})
        else:revised.append(row)
    if len(revised)!=17 or len({r["id"] for r in revised})!=17:
        raise ValueError("Must audit every one of the same 17 composites")
    return revised

def _true_natal_cell(chart, birth, profile):
    if not birth:return None
    if birth[:1]=="甲":
        if birth not in SIX_JIA:raise ValueError("Invalid natal Jia xun")
        return _find_heaven_stem(chart,SIX_JIA[birth])
    return profile.get("birth_cell")

def analyze_health_severity_v36(*,chart,inquiry,calendar=None,db_path=None):
    base=analyze_health_severity_v35(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    profile=bind_patient(chart,inquiry,calendar)
    patient=profile["main_cell"]
    ill=next(c for c in chart["palaces"].values()
          if any(s["star"]=="天芮星" for s in c["heaven_stars"]))
    natal=inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
    natal_cell=_true_natal_cell(chart,natal,profile)
    old=base["audit"]["v34_17_composite_conditions"]
    revised=_rechecked_composites(chart,patient,ill,old)
    new_by={x["id"]:x for x in revised}
    is_same=lambda k:new_by["health_composite_"+str(k).zfill(2)]["state"]=="triggered"
    sections=[]
    for sec in base["sections"]:
        value=sec["text"]
        if sec["id"]=="01_role" and natal and inquiry["relationship"] not in ("spouse","wife","husband","son_in_law"):
            # Original V3.1 placed "落X宫" after the birth-year supplement
            # even though X was the MONTH or HOUR stem's primary palace.
            # Rebuild with two correctly named palaces.
            role=profile["role_name"].replace("（长辈候选）","").replace("（同辈候选）","").replace("（晚辈候选）","")
            role=role.replace("（动物/晚辈候选）","（晚辈用神）")
            value=("依据古籍，此次为"+profile["label"]+"测病情轻重。以"+role+
                    "落"+_palace(patient)+"为主用神；")
            value+=("出生年命"+natal+"另参"+_palace(natal_cell)+"，" if natal_cell
                    else "年命"+natal+"落宫未核定，")+"天芮主病。"
        elif sec["id"]=="01_role" and inquiry["relationship"] in ("nephew","son","daughter","child"):
            value=value.replace("（动物/晚辈候选）","（晚辈用神）")
        if sec["id"]=="09_hazards":
            elems=[]
            if is_same(7):
                z=new_by["health_composite_07"]["evidence"][0]
                elems.append("值使门"+chart["value_door"]+"在"+_palace(chart["palaces"][str(z["value_door_palace"])])+
                  "同宫有天盘"+("、".join(z["same_palace_heaven_three_wonders"]))+"，符合三奇得使")
            if is_same(8):
                elems.append("值使门落宫地盘丁奇，符合玉女守门")
            if elems:value=value.rstrip("。")+"；"+"；".join(elems)+"；吉利程度仍须看值使门与病人宫本身的实际吉凶。"
        if sec["id"]=="10_pace":
            # Retire only V3.4's *day-branch* horse statement plus other
            # grouped matches; rebuild the source-verified V3.6 composite list.
            value=re.sub(r"；已满足可实算复合条件：[^；。]*；需按不同条件确定性质与传统应期，不能自行推出具体日期","",value)
            activated=[z["name"] for z in revised if z["state"]=="triggered" and int(z["id"][-2:]) not in (12,17)]
            horse=new_by["health_composite_12"]["evidence"][0]
            sentence="依据占时"+horse["hour_branch"]+"支，驿马在"+horse["horse_branch"]+"，落"+str(horse["horse_palace"])+"宫"
            if horse["roles_in_horse_palace"]:
                sentence+="，涉及"+"/".join(horse["roles_in_horse_palace"])+"，为传统变化动象"
            else:sentence+="，未直接落患者与病宫"
            sentence+="；没有应期触发就不能指定日期"
            if activated:sentence+="；本盘另见实算条件："+("、".join(activated))
            value=value.rstrip("。")+"；"+sentence+"。"
        if sec["id"]=="11_final":
            if is_same(7) or is_same(8):
                value=value.rstrip("。")+"；三奇得使或玉女守门已通过实际值使宫条件核定，作为医治可能的辅助象，不直接代表实际疗效。"
        if "{" in value or "}" in value or "。。" in value:
            raise ValueError("Invalid fixed template text")
        sections.append({**sec,"text":value})
    audit={**base["audit"],"v36_17_source_rechecked_composites":revised,
       "v36_horse_branch_uses_actual_hour_not_day":True,
       "v36_source_attested_value_door_timing":True,
       "v36_natal_main_palace_not_confused":True,
       "v36_42_existing_pairs_preserved":True,
       "v36_parent_v35_immutable":True,"customer_approved":False}
    return {**base,"schema":"wengua_health_v36_source_value_door_three_wonders_and_hour_horse",
       "sections":sections,"reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in sections),
       "audit":audit,"user_accepted":False}
