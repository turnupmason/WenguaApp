"""Deterministic *new* five-hour end-to-end template acceptance, no frozen four reuse.

Run against a freshly compiled Swift binary. Generate inputs and independent
Python expected facts at test time; do not copy Swift or frozen source data.
Strictly compare four pillars, yin/yang, bureau, seasonal term, xun, value
star/door, 9 palaces, 8+1 star host, stems, individual void, horse,
earth/heaven tombs and full twelve-life branch facts.
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Running a script as `python tests/file.py` does not add repository root
# to sys.path on GitHub Actions. This ensures the ORIGINAL local package wins.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term, layout_from_explicit_bureau
from src.wengua.marriage_runtime import PALACE_BRANCHES, hourly_void_branches
from src.wengua.health_lifecycle_v391 import source_full12, stage_for_stem_at_actual_palace
from src.wengua.health_severity_v34 import HORSE

ROOT=Path(__file__).resolve().parents[1]
TIMEZONE="America/New_York"
SEED=20261022
YEAR=2027
# Month stratification (random day and original Chinese shichen) guarantees
# winter/spring and summer/fall coverage, rather than cherry-picking one bureau.
MONTHS=(1,3,5,8,10)
HOURS=(1,3,5,7,9,11,13,15,17,19,21)  # full valid two-hour branches, avoid unproved 23h
ORIGINAL_FOUR={
    "2026-11-01T05:00:00-05:00",
    "2026-11-04T05:00:00-05:00",
    "2026-11-10T21:00:00-05:00",
    "2026-11-21T17:00:00-05:00",
}
ORDER=[4,9,2,3,5,7,8,1,6]
STAR_NAMES={"天蓬星","天芮星","天冲星","天辅星","天禽星",
            "天心星","天柱星","天任星","天英星"}

def generated_case(iso:str,lookup:dict):
    clock=solar_chart_clock(iso,TIMEZONE)
    pillars=clock["four_pillars"]
    bureau=bureau_for_term(pillars["day"],clock["active_solar_term"])
    chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],
                hour_ganzhi=pillars["hour"])
    emptiness=hourly_void_branches(pillars["hour"])
    assert emptiness["xun_head"]==chart["xun_shou"]
    hour_horse=HORSE[pillars["hour"][1]]
    golden_palaces=[]
    expected={}
    for idx in range(1,10):
        source=chart["palaces"][str(idx)]
        bs=PALACE_BRANCHES[idx]
        heavens=[]
        for star in source["heaven_stars"]:
            life=stage_for_stem_at_actual_palace(
                star["carried_stem"],idx,table=lookup)["actual_stage_facts"]
            heavens.append({"star":star["star"],
                            "carriedStem":star["carried_stem"],"stages":life})
        earth_life=(stage_for_stem_at_actual_palace(
            source["earth_stem"],idx,table=lookup)["actual_stage_facts"]
            if idx!=5 else [])
        tombs=[{"plane":"天盘","stem":h["carriedStem"],"branch":v["branch"],
                "star":h["star"]}
               for h in heavens for v in h["stages"] if v["stage"]=="墓"]
        tombs.extend({"plane":"地盘","stem":source["earth_stem"],
                      "branch":v["branch"],"star":None}
                     for v in earth_life if v["stage"]=="墓")
        # NativeParityMain intentionally expects only the eight OUTER
        # ordinary door/deity cells in GoldenPalace. Mid-five is checked
        # separately by the full output equality checks below.
        if idx != 5:
            golden_palaces.append({"id":idx,"earthStem":source["earth_stem"],
                            "door":source["door"],"deity":source["deity"],
                            "heavenStars":heavens})
        expected[idx]={"id":idx,"gua":source["gua"],
             "earthStem":source["earth_stem"],"door":source["door"],
             "deity":source["deity"],"heavenStars":heavens,
             "earthStages":earth_life,"branches":list(bs),
             "voidBranches":[z for z in bs if z in emptiness["xun_kong_branches"]],
             "horseBranch":hour_horse if hour_horse in bs else None,
             "tombs":tombs}
    return ({
        "iso":iso,"timezone":TIMEZONE,"pillars":pillars,
        "solarTerm":clock["active_solar_term"],
        "bureau":{"dun":bureau["dun"],"ju":bureau["ju"],
                  "yuan":bureau["yuan"],"futou":bureau["futou"],
                  "solarTerm":bureau["solar_term"]},
        "xunShou":chart["xun_shou"],
        "valueStar":chart["value_star"],"valueDoor":chart["value_door"],
        "voidBranches":emptiness["xun_kong_branches"],
        "hourHorse":hour_horse,"palaces":golden_palaces
    },expected,{
        "valueStarPalace":chart["value_star_palace"],
        "valueDoorPalace":chart["value_door_palace"],
        "hiddenStem":chart["hidden_stem"],
        "sunLongitude":clock["sun_ecliptic_longitude_deg"],
    })

def random_five():
    lookup=source_full12() # validates 10 stems × 12 values against book anchors
    rng=random.Random(SEED)
    chosen=[]
    rejected=[]
    for month in MONTHS:
        for attempt in range(60):
            day=rng.randrange(9,26)
            hour=rng.choice(HOURS)
            instant=datetime(YEAR,month,day,hour,0,0,tzinfo=ZoneInfo(TIMEZONE))
            iso=instant.isoformat(timespec="seconds")
            assert iso not in ORIGINAL_FOUR
            try:
                golden,expected,extras=generated_case(iso,lookup)
            except ValueError as exc:
                # A narrow unresolved casting method cannot become a fabricated
                # populated board. Log every original unmodified failure.
                rejected.append({"iso":iso,"month":month,"reason":str(exc)})
                continue
            chosen.append((golden,expected,extras))
            break
        else:
            raise AssertionError(f"No approved actual chart in month {month}; "
                                 f"rejected={rejected}")
    assert len(chosen)==5
    assert len({item[0]["iso"] for item in chosen})==5
    assert {item[0]["bureau"]["dun"] for item in chosen}=={"yin","yang"}, (
        "Random five lacked both yin and yang; don't mark template complete")
    return chosen,rejected

def same(name,actual,expected,where):
    if actual!=expected:
        raise AssertionError(f"{where} | {name}: actual={actual!r} original_Python={expected!r}")

def run(native_binary:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    chosen,rejected=random_five()
    gold={"schema":"five_new_seeded_hours_python_original_not_old_four",
          "seed":SEED,"year":YEAR,"timezone":TIMEZONE,
          "samples":[rec[0] for rec in chosen]}
    reference=outdir/"five_python_reference.json"
    reference.write_text(json.dumps(gold,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (outdir/"rejected_candidates.json").write_text(
        json.dumps(rejected,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    try:
        proc=subprocess.run([str(native_binary.resolve()),str(reference.resolve())],
                            capture_output=True,text=True,check=True)
    except subprocess.CalledProcessError as err:
        (outdir/"swift_stderr.txt").write_text(err.stderr,encoding="utf8")
        print("Swift CLI error from 5 genuinely new Python generated inputs:\n"+
              err.stderr, file=sys.stderr, flush=True)
        raise AssertionError("Swift rejected a Python-approved live chart; "
                             "see preserved swift_stderr.txt") from err
    actual=json.loads(proc.stdout)
    same("five chart count",len(actual),5,"all")
    stats=[]
    total_tombs=total_life=0
    for i,(got,(golden,expected,extras)) in enumerate(zip(actual,chosen),1):
        where=f"new_random_hour_{i}:{golden['iso']}"
        for key in ("pillars","solarTerm","bureau","xunShou","valueStar",
                    "valueDoor","voidBranches","hourHorse","timezone"):
            same(key,got[key],golden[key],where)
        for key in ("valueStarPalace","valueDoorPalace","hiddenStem"):
            same(key,got[key],extras[key],where)
        if abs(float(got["sunLongitude"])-extras["sunLongitude"])>0.0003:
            raise AssertionError(f"{where} sunLongitude diverges")
        same("time instant",datetime.fromisoformat(got["iso"]),
             datetime.fromisoformat(golden["iso"]),where)
        cells={p["id"]:p for p in got["palaces"]}
        same("9 unique palaces",set(cells),set(range(1,10)),where)
        assert all(p["id"]==j for p,j in zip(got["palaces"],range(1,10)))
        stars=[];deities=[];doors=[];hour_life=tombs=0
        for idx in ORDER:
            p=cells[idx];source=expected[idx]
            for key in ("gua","earthStem","door","deity","heavenStars",
                        "earthStages","branches","voidBranches","horseBranch"):
                value=p.get(key) if key in {"door","deity","horseBranch"} else p[key]
                same(key,value,source[key],where+f"/{idx}")
            def normalized_tombs(items):
                return sorted((v["plane"],v["stem"],v["branch"],v.get("star")) for v in items)
            same("heaven / earth tomb markers",
                 normalized_tombs(p["tombs"]),normalized_tombs(source["tombs"]),
                 where+f"/{idx}")
            tombs+=len(p["tombs"])
            hour_life+=len(p["earthStages"])
            hour_life+=sum(len(h["stages"]) for h in p["heavenStars"])
            if idx==5:
                same("center unassigned ordinary symbols",
                     [p.get("door"),p.get("deity"),p["heavenStars"],p["branches"],p["earthStages"]],
                     [None,None,[],[],[]],where)
            else:
                stars.extend(h["star"] for h in p["heavenStars"])
                deities.append(p["deity"]);doors.append(p["door"])
        same("8 unique deities",len(set(deities)),8,where)
        same("8 unique doors",len(set(doors)),8,where)
        same("all 9 stars including same-palace Tianrui/Tianqin",set(stars),STAR_NAMES,where)
        assert hour_life>=25
        assert sum(bool(p.get("horseBranch")) for p in cells.values())==1
        assert sum(len(p["voidBranches"]) for p in cells.values())==2
        total_tombs+=tombs;total_life+=hour_life
        summary={"n":i,"iso":golden["iso"],"pillars":golden["pillars"],
                 "dun":golden["bureau"]["dun"],"ju":golden["bureau"]["ju"],
                 "solarTerm":golden["solarTerm"],"xunShou":golden["xunShou"],
                 "valueStar":golden["valueStar"],"valueDoor":golden["valueDoor"],
                 "voidBranches":golden["voidBranches"],"horseBranch":golden["hourHorse"],
                 "tombs":tombs,"lifeFacts":hour_life,"ninePalaces":9,
                 "fullFieldParity":"PASS"}
        stats.append(summary)
        print("PASS new real hour",i,golden["iso"],
              "/".join(golden["pillars"].values()),golden["solarTerm"],
              golden["bureau"]["dun"],golden["bureau"]["ju"],
              "xun",golden["xunShou"],"value",golden["valueStar"],golden["valueDoor"],
              "void",golden["voidBranches"],"horse",golden["hourHorse"],
              "life",hour_life,"tombs",tombs,flush=True)
    assert total_life>=125
    report={"schema":"ios_five_new_hour_template_parity_v1",
            "seed":SEED,"year":YEAR,"timezone":TIMEZONE,
            "checks":{"new_hours":5,"total_nine_palace_cells":45,
                      "outer_palaces":40,"heaven_earth_life_slots":total_life,
                      "earth_heaven_tombs":total_tombs,"python_vs_swift":"PASS",
                      "complete_symbol_coverage_per_chart":True,
                      "no_old_four_used":True,"not_divination_outcome_or_score":True},
            "candidate_rejections":rejected,"samples":stats}
    (outdir/"five_cast_acceptance_report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (outdir/"five_swift_actual.json").write_text(
        json.dumps(actual,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(f"ACCEPTED 5/5 independent Python vs Swift parity; "
          f"45 palaces, {total_life} lifecycle slots, "
          f"{total_tombs} heaven/earth tomb tags, "
          f"{len(rejected)} explicitly recorded rejected candidate(s)",flush=True)

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python3 tests/test_ios_five_random_live_casts.py "
                         "/path/to/native-binary /path/to/output-folder")
    run(Path(sys.argv[1]),Path(sys.argv[2]))
