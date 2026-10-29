"""Use real civil instants to check existing production Swift core against 1080 atlas.

Does not add an alternate Swift casting engine. Each unique base board is
encountered in real 2026+ local calendars and checked against full Python facts.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/"data/atlas/shijia_zhuanpan_physical_1080_v1.jsonl"
ZONE="Asia/Shanghai"
UTC8=timezone(timedelta(hours=8))


def atlas():
    return {j["base_id"]:j for j in (json.loads(s) for s in ATLAS.read_text().splitlines())}


def select_real_times():
    source=atlas()
    found={}
    rejected=0
    for year in range(2026,2035):
        date=datetime(year,1,1,tzinfo=UTC8)
        end=datetime(year+1,1,1,tzinfo=UTC8)
        while date<end:
            for hour in range(0,23,2):
                stamp=date.replace(hour=hour,minute=30).isoformat()
                try:
                    calc=solar_chart_clock(stamp,ZONE)
                    pillars=calc["four_pillars"]
                    b=bureau_for_term(pillars["day"],calc["active_solar_term"])
                except ValueError:
                    rejected+=1
                    continue
                key=f'{b["dun"]}-{b["ju"]:02d}-{pillars["hour"]}'
                if key in source and key not in found:
                    found[key]={
                      "base_id":key,"iso":stamp,"timezone":ZONE,
                      "pillars":pillars,"solar_term":calc["active_solar_term"],
                      "expected_bureau":{"dun":b["dun"],"ju":b["ju"]},
                    }
                if len(found)==1080:
                    return [found[k] for k in sorted(found)],{
                        "covered":1080,"year":year,"rejected_technical":rejected,
                        "source":"actual_mapped_year_solar_term_no_fabricated_bureau"}
            date+=timedelta(days=1)
    return [found[k] for k in sorted(found)],{
        "covered":len(found),"rejected_technical":rejected,
        "missing":sorted(set(source)-set(found))[:100],
        "source":"actual_mapped_year_solar_term_no_fabricated_bureau"}


def verify(fixtures,swiftout):
    expected=atlas()
    got={}
    for line in Path(swiftout).read_text().splitlines():
        if not line.strip():continue
        j=json.loads(line)
        if j["base_id"] in got:raise ValueError("Repeated native case")
        got[j["base_id"]]=j["chart"]
    assert len(fixtures)==1080 and len(got)==1080,(len(fixtures),len(got))
    mismatches=[]
    for f in fixtures:
        key=f["base_id"]
        src=expected[key]
        swift=got[key]
        facts={
          "xun_shou":swift["xunShou"],
          "hidden_stem":swift["hiddenStem"],
          "value_star":swift["valueStar"],
          "value_star_palace":swift["valueStarPalace"],
          "value_door":swift["valueDoor"],
          "value_door_palace":swift["valueDoorPalace"],
          "horse_branch":swift["hourHorse"],
          "horse_palace":swift["hourHorsePalace"],
        }
        for a,b in facts.items():
            if b!=src[a]:mismatches.append({"base_id":key,"fact":a,"python":src[a],"swift":b})
        if swift["pillars"]!=f["pillars"]:
            mismatches.append({"base_id":key,"fact":"four_pillars","python":f["pillars"],
                               "swift":swift["pillars"]})
        if swift["solarTerm"]!=f["solar_term"] or swift["bureau"]["dun"]!=src["dun"] or swift["bureau"]["ju"]!=src["ju"]:
            mismatches.append({"base_id":key,"fact":"solar_term_or_bureau","python":(f["solar_term"],src["dun"],src["ju"]),"swift":(swift["solarTerm"],swift["bureau"]["dun"],swift["bureau"]["ju"])})
        if sorted(swift["voidBranches"])!=sorted(src["xun_void_branches"]):
            mismatches.append({"base_id":key,"fact":"xun_void",
                               "python":src["xun_void_branches"],"swift":swift["voidBranches"]})
        for sp in swift["palaces"]:
            n=sp["id"]
            pc=next(x for x in src["palaces"] if x["palace"]==n)
            for prop,other in (("gua","gua"),("earthStem","earth_stem"),("door","door"),("deity","deity")):
                want=pc.get(other)
                # Middle has no ordinary door/deity and no fake heavenly star.
                if sp[prop]!=want:
                    mismatches.append({"base_id":key,"palace":n,"fact":prop,
                                       "python":want,"swift":sp[prop]})
            starlist=[{"star":x["star"],"carried_stem":x["carriedStem"]} for x in sp["heavenStars"]]
            want=[] if n==5 else pc["heaven_stars"]
            if starlist!=want:
                mismatches.append({"base_id":key,"palace":n,"fact":"heaven_stars",
                                   "python":want,"swift":starlist})
            if n!=5:
                if sorted(sp["voidBranches"])!=sorted(pc["xun_void_branches"]):
                    mismatches.append({"base_id":key,"palace":n,"fact":"voidBranches",
                                       "python":pc["xun_void_branches"],"swift":sp["voidBranches"]})
                horse=src["horse_branch"] if n==src["horse_palace"] else None
                if sp["horseBranch"]!=horse:
                    mismatches.append({"base_id":key,"palace":n,"fact":"horseBranch",
                                       "python":horse,"swift":sp["horseBranch"]})
    return {"checked":len(fixtures),"field_differences":len(mismatches),
            "first_differences":mismatches[:30],
            "source":"actual Swift WenguaNativeCore.compute and Python full 1080 atlas",
            "all_agree":not mismatches}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("select","verify"))
    p.add_argument("--input")
    p.add_argument("--swift")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    if args.mode=="select":
        rows,report=select_real_times()
        dest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n")
        print("REAL_NATIVE_1080_CLOCK_COVERAGE "+json.dumps(report,ensure_ascii=False))
        if len(rows)!=1080:raise RuntimeError("Not all 1080 base boards located in actual real-year windows")
    else:
        if not args.input or not args.swift:raise ValueError("Need fixtures and native output")
        rows=json.loads(Path(args.input).read_text())
        report=verify(rows,args.swift)
        dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
        print("ACTUAL_SWIFT_PYTHON_1080_RESULT "+json.dumps(report,ensure_ascii=False))
        if not report["all_agree"]:raise RuntimeError("Native full-board parity mismatches found")


if __name__=="__main__":
    main()
