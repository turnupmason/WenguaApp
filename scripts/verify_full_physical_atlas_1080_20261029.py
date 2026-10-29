"""Build and audit all 1080 canonical physical Zhuanpan boards.

One physical board = (yin/yang, ju 1..9, hour 60). This dataset records
only truths determined by those inputs: earth/heaven stems, stars, doors,
deities, Xun/Shou, branch void candidates, horse, formations and static
tomb/punishment checks. Month/year/day/person are NOT invented.

The detailed "reading" must later bind actual year/month/day/role sources,
not create another physical board.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from src.wengua.casting_shenqi import (
    DEITIES,DOORS,EARTH_ORDER,RING,STARS,cycle60,
    hour_ganzhi_from_day,layout_from_explicit_bureau,
)
from src.wengua.health_81_excel_catalog_vnext import SOURCE as SOURCE81, catalog, for_real_palace
from src.wengua.health_severity_v25 import fuyin_fanyin_facts
from src.wengua.health_severity_v27 import five_not_encounter
from src.wengua.health_macro_facts_vnext import tianxian_hour
from src.wengua.health_severity_v34 import HORSE
from src.wengua.health_severity_v28 import STRIKING_PALACE
from src.wengua.marriage_runtime import (
    PALACE_BRANCHES,ELEMENTS,hourly_void_branches,
)
from src.wengua.health_palace_detailed_vnext import inspect_role_void
from src.wengua.selected_duel_table_vnext import table_one
from src.wengua.health_five_level_quant_vnext import door_break_penalty_policy
from src.wengua.health_lifecycle_v391 import (
    source_full12,stage_for_stem_at_actual_palace,
)

SCHEMA="wengua_shijia_zhuanpan_physical_1080_v1"
MONTH_BRANCHES="寅卯辰巳午未申酉戌亥子丑"
ALL_STARS=set(STARS.values())
ALL_DOORS=set(DOORS.values())
OUTER_STARS=ALL_STARS-{"天禽星"}
GODS=set(DEITIES)


def canonical(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"))

def sha(x):
    return hashlib.sha256(canonical(x).encode("utf8")).hexdigest()

def short_pair(x):
    return {k:x[k] for k in (
        "fact_id","star","key","heaven","earth","name",
        "polarity","source_excel_row")}


def build_one(dun,ju,hour,*,life):
    chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
    places=chart["palaces"]
    assert set(places)=={str(x) for x in range(1,10)}
    centre=places["5"]
    assert centre["heaven_stars"]==[] and centre["door"] is None and centre["deity"] is None
    allheaven=[s["star"] for p in places.values() for s in p["heaven_stars"]]
    assert len(allheaven)==9 and set(allheaven)==ALL_STARS
    assert sum(len(places[str(i)]["heaven_stars"])==2 for i in RING)==1
    assert {places[str(i)]["door"] for i in RING}==ALL_DOORS
    assert {places[str(i)]["deity"] for i in RING}==GODS
    assert {places[str(i)]["earth_stem"] for i in range(1,10)}==set(EARTH_ORDER)
    assert len({places[str(i)]["earth_stem"] for i in range(1,10)})==9
    xun=hourly_void_branches(hour)
    blanks=set(xun["xun_kong_branches"])
    horse=HORSE[hour[-1]]
    hp=[p for p in RING if horse in PALACE_BRANCHES[p]]
    assert len(hp)==1
    fuyin=fuyin_fanyin_facts(chart)
    day_options=[]
    for day in cycle60():
        if hour_ganzhi_from_day(day[0],hour[1])!=hour:
            continue
        flags={
          "day_stem":day[0],
          "five_not_encounter":five_not_encounter(day,hour)["triggered"],
          "tianxian_hour":tianxian_hour(day,hour),
        }
        if flags not in day_options:day_options.append(flags)
    assert len(day_options)==2,(dun,ju,hour,day_options)
    cells=[]
    pair_count=0
    for p in range(1,10):
        cell=places[str(p)]
        if p==5:
            cells.append({"palace":5,"gua":"中",
                          "earth_stem":cell["earth_stem"],
                          "ordinary_star_door_deity":False,
                          "earth_stem_host_palace":2})
            continue
        branches=PALACE_BRANCHES[p]
        void_hits=[b for b in branches if b in blanks]
        withhost=dict(cell,hosted_centre_earth_stem=centre["earth_stem"])
        pairs=[short_pair(item) for item in for_real_palace(withhost)]
        assert len(pairs)==(2 if p==2 or len(cell["heaven_stars"])==2 else 1)
        assert all(pair["key"] in catalog() for pair in pairs)
        pair_count+=len(pairs)
        residents=[]
        for s in cell["heaven_stars"]:
            details=stage_for_stem_at_actual_palace(
                s["carried_stem"],p,table=life)
            residents.append({
              "star":s["star"],"carried_stem":s["carried_stem"],
              "tombs":[v["branch"] for v in details["actual_stage_facts"]
                       if v["stage"]=="墓"],
              "striking":STRIKING_PALACE.get(s["carried_stem"])==p,
            })
        earth=stage_for_stem_at_actual_palace(
            cell["earth_stem"],p,table=life)
        door_relations={table_one("door",cell["door"],b,p)["user_cell_col"]
                        for b in MONTH_BRANCHES}
        assert len(door_relations)==1,("Door relation is NOT physical-only",p)
        door_relation=door_relations.pop()
        door_break=door_break_penalty_policy(
            door_name=cell["door"],palace=p,door_relation=door_relation)
        # Truth/falsity of empty palace depends on actual month branch.
        classified={m:inspect_role_void(
            palace=p,occupied_void_branches=void_hits,
            month_branch=m,hour_ganzhi=hour)["classification"]
            for m in MONTH_BRANCHES}
        # Expose variants explicitly; an unknown month's fake/true VOID
        # must never be silently selected as the physical board's void.
        cells.append({
          "palace":p,"gua":cell["gua"],"branches":list(branches),
          "earth_stem":cell["earth_stem"],
          "heaven_stars":cell["heaven_stars"],
          "door":cell["door"],"deity":cell["deity"],
          "xun_void_branches":void_hits,
          "hour_horse_branch":horse if horse in branches else None,
          "heaven_residents":residents,
          "earth_tombs":[v["branch"] for v in earth["actual_stage_facts"]
                         if v["stage"]=="墓"],
          "door_relation_200":door_relation,
          "door_break":door_break["has_door_break"],
          "door_break_extra_two_shift":door_break["two_level_shift"],
          "directed_81_formations":pairs,
          "void_by_real_month_branch":classified,
        })
    assert pair_count in (9,10)
    # Physical layer excludes month-variant void results, but keeps the
    # actual candidate Xun-void and complete month-variant evidence.
    physical={
        "schema":SCHEMA,"base_id":f"{dun}-{ju:02d}-{hour}",
        "dun":dun,"ju":ju,"hour_ganzhi":hour,
        "xun_shou":chart["xun_shou"],
        "hidden_stem":chart["hidden_stem"],
        "value_star":chart["value_star"],
        "value_star_palace":chart["value_star_palace"],
        "value_door":chart["value_door"],
        "value_door_palace":chart["value_door_palace"],
        "horse_branch":horse,"horse_palace":hp[0],
        "xun_void_branches":sorted(blanks),
        "star_fuyin_fanyin":fuyin["star"],
        "door_fuyin_fanyin":fuyin["door"],
        "source_81_sha256":hashlib.sha256(SOURCE81.read_bytes()).hexdigest(),
        "real_81_formations_count":pair_count,
        "palaces":cells,
        "day_stem_variants":day_options,
        "not_fixed_without_real_calendar":[
          "year_stem_selected_patient","month_branch_strength",
          "actual_12_lifecycle_month_effect","fake_true_void_month_condition",
          "selected_character_relationship","optional_verified_patient_natal"],
        "physical_only":True,"medical_diagnosis":False,
    }
    # Fingerprint only real physical star/door/god/stem placements; do
    # NOT let source line, month variants or actor identity create "new plates".
    physical["physical_fingerprint"]=sha({
        "dun":dun,
        "palaces":places,
        "xun_shou":chart["xun_shou"],
        "hidden_stem":chart["hidden_stem"],
        "value_star":chart["value_star"],
        "value_star_palace":chart["value_star_palace"],
        "value_door":chart["value_door"],
        "value_door_palace":chart["value_door_palace"],
    })
    return physical


def all1080():
    life=source_full12()
    rows=[build_one(d,j,h,life=life)
          for d in ("yang","yin")
          for j in range(1,10)
          for h in cycle60()]
    assert len(rows)==1080
    assert len({r["base_id"] for r in rows})==1080
    hashes=[r["physical_fingerprint"] for r in rows]
    duplicates=Counter(hashes)
    duplicated={k:v for k,v in duplicates.items() if v>1}
    return rows,duplicated


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--report",required=True)
    a=p.parse_args()
    rows,duplicates=all1080()
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text("".join(canonical(x)+"\n" for x in rows),encoding="utf8")
    report={
      "schema":SCHEMA,"generated_rows":len(rows),
      "distinct_identity_keys":len({x["base_id"] for x in rows}),
      "distinct_physical_fingerprints":len({x["physical_fingerprint"] for x in rows}),
      "duplicate_physical_hash_count":len(duplicates),
      "duplicate_hash_examples":list(duplicates.items())[:12],
      "all_81_formations_verified":True,
      "all_8_doors_8_gods_9_stars_unique_per_plate":True,
      "no_ordinary_centre_symbols":True,
      "all_1080_void_month_variants_recorded":True,
      "month_branch_variations_not_silently_frozen":True,
      "actual_calendar_and_actor_required_for_final_health_verdict":True,
      "cases_approved_for_app":0,
      "source_81_sha256":hashlib.sha256(SOURCE81.read_bytes()).hexdigest(),
    }
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("PHYSICAL_1080_REPORT "+canonical(report))
    if duplicates:
        raise RuntimeError("1080 IDs do not produce 1080 distinct physical placement fingerprints")


if __name__=="__main__":
    main()
