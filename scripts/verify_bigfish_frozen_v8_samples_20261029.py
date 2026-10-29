"""Actual BigFish TypeScript -> unchanged frozen Wengua V8/V10.2 composition.
No old board substitution is permitted: independent old layout is audit ONLY.
This is a two-real-clock smoke test, NOT 1080 verified V8 text parity.
"""
from __future__ import annotations
import json,subprocess,sys,hashlib
from pathlib import Path

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau,xun_shou
from src.wengua.health_severity_vnext_review import analyze_health_severity_review
from src.wengua.health_text_pipeline import DEFAULT_DB

ROOT=Path(__file__).resolve().parents[1]
RING={1,2,3,4,6,7,8,9}
GUA={1:"坎",2:"坤",3:"震",4:"巽",5:"中",6:"乾",7:"兑",8:"艮",9:"离"}
STARS={"天蓬","天芮","天冲","天辅","天心","天柱","天任","天英"}
DOORS={"休门","生门","伤门","杜门","景门","死门","惊门","开门"}
GODS={"值符","螣蛇","太阴","六合","白虎","玄武","九地","九天"}

def cast_bigfish(compiled,iso,zone):
    clock=solar_chart_clock(iso,zone)
    pillars=clock["four_pillars"]
    term=clock["active_solar_term"]
    process=subprocess.run(["node",str(ROOT/"scripts/bigfish_shijia_cast_bridge_20261029.cjs"),str(compiled)],
        input=json.dumps({"pillars":pillars,"term":term},ensure_ascii=False),
        text=True,capture_output=True,timeout=90)
    if process.returncode:raise AssertionError(process.stderr)
    original=json.loads(process.stdout)
    assert original["source"]=="perfhelf/bigfishmarquis-qimen"
    orig=original["chart"]
    by={p["palaceNumber"]:p for p in orig["palaces"]}
    assert set(by)==set(range(1,10))
    cells={}
    for i in range(1,10):
        p=by[i]
        assert p["palaceName"]==GUA[i]
        # The upstream TypeScript source explicitly reverses historic names:
        # skyStem contains actual EARTH stem; earthStem contains HEAVEN stem.
        earth=p["skyStem"]
        if i==5:
            assert p["star"]=="天禽" and not p["earthStem"] and not p["door"] and not p["god"]
            heavens=[]
            door=deity=None
        else:
            assert p["star"] in STARS and p["door"] in DOORS
            deity=p["god"].replace("腾蛇","螣蛇")
            assert deity in GODS
            heavens=[{"star":p["star"]+"星","carried_stem":p["earthStem"]}]
            if p["star"]=="天芮":
                assert p.get("jiGanStem")==by[5]["skyStem"],"真实中宫携干不能丢"
                heavens.append({"star":"天禽星","carried_stem":p["jiGanStem"]})
            door=p["door"]
        cells[str(i)]={"palace":i,"gua":GUA[i],"earth_stem":earth,
                       "heaven_stars":heavens,"door":door,"deity":deity}
    xun,elapsed,hidden=xun_shou(pillars["hour"])
    chart={"source_key":"bigfish_pinned","school_id":"shijia_zhuanpan",
           "status":"new_cast_needs_author_review","dun":orig["dun"],
           "ju":orig["juNumber"],"hour_ganzhi":pillars["hour"],
           "xun_shou":xun,"hidden_stem":hidden,
           "value_star":orig["zhiFuStar"]+"星",
           "value_star_palace":orig["zhiFuPalace"],
           "value_door":orig["zhiShiDoor"],
           "value_door_palace":orig["zhiShiPalace"],
           "palaces":cells}
    reference_bureau=bureau_for_term(pillars["day"],term)
    reference=layout_from_explicit_bureau(dun=reference_bureau["dun"],ju=reference_bureau["ju"],
                                          hour_ganzhi=pillars["hour"])
    differences=[]
    for i in range(1,10):
        a=cells[str(i)]; b=reference["palaces"][str(i)]
        for key in ("earth_stem","door","deity","heaven_stars"):
            if a[key]!=b[key]:differences.append("palace."+str(i)+"."+key)
    for field in ("value_star","value_door","value_star_palace","value_door_palace"):
        if chart[field]!=reference[field]:differences.append(field)
    calendar={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
              "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
              "month_branch":pillars["month"][1]}
    reading=analyze_health_severity_review(chart=chart,calendar=calendar,
                     inquiry={"intent":"severity","relationship":"father",
                              "consultation_context":"direct_proxy"},db_path=DEFAULT_DB)
    summary=reading["full_health_role_strength_network"]["candidate_five_grade_quantization"]["summary"]
    assert isinstance(summary["score"],int) and -5<=summary["score"]<=5
    assert reading["reading_text"] and reading["sections"]
    return {"iso":iso,"zone":zone,"four_pillars":pillars,"new_bureau":{"dun":orig["dun"],"ju":orig["juNumber"]},
            "original_source":"BigFish original compiled TS","new_chart_is_actual_input":True,
            "old_chart_is_comparison_only":True,"difference_paths":differences,
            "score":summary["score"],"customer_sha256":hashlib.sha256(reading["reading_text"].encode()).hexdigest(),
            "approved_for_app":False}

if __name__=="__main__":
    from argparse import ArgumentParser
    a=ArgumentParser()
    a.add_argument("--compiled",required=True)
    args=a.parse_args()
    tests=[("2026-10-28T06:00:00-04:00","America/New_York"),
           ("2026-10-28T10:00:00-04:00","America/New_York")]
    for iso,zone in tests:
        print(json.dumps(cast_bigfish(args.compiled,iso,zone),ensure_ascii=False),flush=True)
