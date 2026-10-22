"""Source-input V4 scoring regression: original user question and two fixed historical families."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from scripts.replay_all_historical_health_v31_v33 import CASES
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_symbolic_score_v40 import calculate_health_symbolic_score_v40
from scripts.replay_health_v39_fixed_cases import RANDOM_INDICES,PINNED_CASE_IDS

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"archives/sqlite/WenguaApp_双书194案例_三例精简自然断词V3_9_完整研究库.sqlite3"
PARENT_SHA="0e565ff5c4fea8d0510b155ab264b1af4c8ab9b63a173eb8cf96a00909c04ed1"

def evaluate(db_path=PARENT):
    p=Path(db_path)
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("Original complete V3.9 parent mismatch")
    samples=[None]+[CASES[i] for i in RANDOM_INDICES]
    if [r["id"] for r in samples[1:]]!=PINNED_CASE_IDS:
        raise ValueError("Original random selection changed")
    findings=[]
    for spec in samples:
        if spec is None:
            clock="2026-10-22T12:00:00-04:00";zone="America/New_York"
            rec=solar_chart_clock(clock,zone)
            pillars=rec["four_pillars"]
            if pillars!={"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"}:
                raise ValueError("User four pillars differ")
            bureau=bureau_for_term(pillars["day"],rec["active_solar_term"])
            q={"intent":"severity","relationship":"self","consultation_context":"direct_self"}
            name="user_20261022_1200_EDT"
        else:
            clock=spec["date"]+"T"+spec["clock"]+":00+08:00"
            rec=solar_chart_clock(clock,"Asia/Shanghai")
            pillars=rec["four_pillars"]
            if pillars["day"]!=spec["day"] or pillars["hour"]!=spec["hour"]:
                raise ValueError("Book first hour differs")
            bureau={"dun":spec["dun"],"ju":spec["ju"]}
            q={"intent":"severity","relationship":spec["relation"],
               "consultation_context":spec.get("context","direct_proxy")}
            for src,target in (("sex","patient_sex"),("relative_specific","relative_specific"),("birth_ganzhi","patient_birth_ganzhi")):
                if spec.get(src):q[target]=spec[src]
            name=spec["id"]
        cast=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
        if spec and (cast["value_star"],cast["value_door"])!=(spec["star"],spec["door"]):
            raise ValueError("Historical value symbol differs")
        calendar={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
                  "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
                  "month_branch":pillars["month"][1]}
        output=calculate_health_symbolic_score_v40(chart=cast,inquiry=q,calendar=calendar)
        findings.append({"family_id":name,"pillars":pillars,"datetime":clock,
                         "relationship":q["relationship"],"score":output,
                         "original_post_event_result_used":False})
    return {"schema":"wengua_health_v40_3_fixed_score_trials",
       "exact_complete_v39_source_sha256":PARENT_SHA,
       "unseen_blind_trial":False,"user_approved":False,"records":findings}

if __name__=="__main__":
    result=evaluate()
    print(json.dumps({"samples":[{"id":r["family_id"],"score":r["score"]["display_score_0_100"],
       "raw":r["score"]["raw_score"],"adjustment":r["score"]["signed_delta_sum"],
       "rows":[{"name":x["id"],"points":x["points"]} for x in r["score"]["ledger"]],
       "unknown":r["score"]["unscored_unknowns"]} for r in result["records"]]},ensure_ascii=False,indent=2))
