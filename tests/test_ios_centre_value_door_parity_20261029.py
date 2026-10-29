"""Real independent Python source vs actual Swift WenguaNativeCore six center cases."""
import json,subprocess,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"tests"))
from test_ios_five_random_live_casts import generated_case
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,earth_plate,xun_shou
from src.wengua.health_lifecycle_v391 import source_full12

def run(binary,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    lookup=source_full12()
    picked=[]
    found={"yang":0,"yin":0}
    for month in range(1,13):
        if min(found.values())>=3:break
        for day in (6,9,12,15,18,21,24,27):
            if min(found.values())>=3:break
            for hour in (1,3,5,7,9,11,13,15,17,19,21):
                iso=datetime(2026,month,day,hour,0,tzinfo=ZoneInfo(
                    "America/New_York")).isoformat(timespec="seconds")
                try:
                    clock=solar_chart_clock(iso,"America/New_York")
                    bureau=bureau_for_term(clock["four_pillars"]["day"],
                                          clock["active_solar_term"])
                    earth=earth_plate(bureau["dun"],bureau["ju"])
                    _,steps,hidden=xun_shou(clock["four_pillars"]["hour"])
                    origin=next(p for p,v in earth.items() if v==hidden)
                    counted=(origin-1+steps*(1 if bureau["dun"]=="yang" else -1))%9+1
                    if counted!=5 or steps==0 or found[bureau["dun"]]>=3:continue
                    golden,palaces,extras=generated_case(iso,lookup)
                except ValueError:
                    continue
                assert extras["valueDoorPalace"]==2
                picked.append((golden,palaces,extras,origin,steps))
                found[bureau["dun"]]+=1
    assert found=={"yang":3,"yin":3},f"real center samples insufficient {found}"
    src=outdir/"six_real_center_kun2_python_reference.json"
    src.write_text(json.dumps({"samples":[x[0] for x in picked]},
                              ensure_ascii=False,indent=2)+"\n")
    proc=subprocess.run([str(binary.resolve()),str(src.resolve())],
                        capture_output=True,text=True)
    (outdir/"native_stderr.txt").write_text(proc.stderr)
    if proc.returncode:raise AssertionError("Swift center cast: "+proc.stderr[:1200])
    actual=json.loads(proc.stdout)
    (outdir/"six_real_center_kun2_swift_output.json").write_text(
        json.dumps(actual,ensure_ascii=False,indent=2)+"\n")
    assert len(actual)==6
    for i,(a,(gold,expected,extras,origin,elapsed)) in enumerate(zip(actual,picked),1):
        assert a["iso"]==gold["iso"] and a["pillars"]==gold["pillars"],(i,"clock")
        assert a["bureau"]==gold["bureau"] and a["solarTerm"]==gold["solarTerm"],(i,"bureau")
        for key in ("valueDoor","valueStar","voidBranches","hourHorse","xunShou"):
            assert a[key]==gold[key],(i,key)
        for key in ("valueDoorPalace","valueStarPalace","hiddenStem"):
            assert a[key]==extras[key],(i,key)
        assert a["valueDoorPalace"]==2
        for p in a["palaces"]:
            e=expected[p["id"]]
            for key in ("gua","earthStem","door","deity","heavenStars",
                        "earthStages","branches","voidBranches","horseBranch"):
                value=p.get(key) if key in ("door","deity","horseBranch") else p[key]
                assert value==e[key],(i,p["id"],key,value,e[key])
            norm=lambda arr:sorted((v["plane"],v["stem"],v["branch"],
                                    v.get("star") or "") for v in arr)
            assert norm(p["tombs"])==norm(e["tombs"]),(i,p["id"],"tombs")
        print(f"{i}: {a['iso']} {a['bureau']['dun']} {a['bureau']['ju']} "
              f"origin={origin} elapsed={elapsed}: {a['valueDoor']} at Kun2 "
              "Python==Swift all 9 palaces")
    print("PASS six unfiltered real center-door cases, Yin3 Yang3, complete native nine-palace parity")
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("native_binary evidence_dir")
    run(Path(sys.argv[1]),Path(sys.argv[2]))
