#!/usr/bin/env python3
"""Strict JieQi at the REAL crossing: compile & execute native Swift core.

Separate from historical V7 tests; does not alter V8 or old failure rows.
"""
from __future__ import annotations
import json
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"ios/WenguaAppUI/WenguaNativeCore.swift"

MOMENTS=(
    "2026-11-22T06:30:00.000Z", # pre 小雪: same 寅 branch
    "2026-11-22T07:23:21.138Z", # 1 ms before 小雪
    "2026-11-22T07:23:21.139Z", # crossing inclusive
    "2026-11-22T07:23:21.140Z", # 1 ms after
    "2026-11-22T08:30:00.000Z",
    "2026-12-07T02:30:00.000Z", # pre 大雪
    "2026-12-07T02:52:32.429Z", # crossing at 大雪
    "2026-12-21T20:30:00.000Z", # pre 冬至
    "2026-12-21T20:50:14.539Z", # crossing at 冬至
    "2027-03-14T07:30:00.000Z", # DST offset -4
    "2029-01-05T01:41:54.830Z", # before 2029 Xiaohan
    "2029-01-05T01:41:54.831Z", # new Xiaohan inclusive
    "2035-06-10T12:00:00.000Z", # future midyear
    "2040-02-04T05:39:52.575Z", # 1ms before 2040 Lichun
    "2040-02-04T05:39:52.576Z", # 2040 Lichun exact, year/month change
    "2040-12-21T06:32:50.769Z", # 1ms before Dongzhi
    "2040-12-21T06:32:50.770Z", # new Dongzhi inclusive
    "2040-12-31T23:59:59.000Z", # complete Dec 2040 must be covered
    "2041-01-04T23:48:07.975Z", # sentinel minus 1ms
    "2041-01-04T23:48:07.976Z", # last included endpoint Xiaohan
)

def verify_source_constants():
    table=json.loads((ROOT/"data/calendar/strict_jieqi_moshier_2025_2040.json").read_text("utf8"))
    packed=table["delta_base36"]
    for source in (ROOT/"src/wengua/astro_calendar.py",
                   ROOT/"scripts/wengua_bigfish_518400_offline_editorial_20261029.py",
                   SOURCE):
        text=source.read_text("utf8")
        if packed not in text or str(table["first_utc_ms"]) not in text:
            raise AssertionError("Strict UTC crossing table drift: "+str(source))
    times=[table["first_utc_ms"]]
    for delta in packed.split("."):
        times.append(times[-1]+int(delta,36))
    previous=json.loads((ROOT/"data/calendar/strict_jieqi_moshier_2025_2028.json").read_text("utf8"))
    if times[:96] != [previous["first_utc_ms"]] + [
        previous["first_utc_ms"] + sum(int(x,36) for x in previous["delta_base36"].split(".")[:i])
        for i in range(1,96)
    ]:
        raise AssertionError("Old 2025-2028 crossing timestamps must remain byte-exact")
    if (len(times)!=385 or times!=sorted(set(times)) or
        times[383]!=2239684370770 or times[-1]!=2240956087976):
        raise AssertionError("Strict table length/order invalid")
    return times

SWIFT_MAIN=r"""
import Foundation
@main struct StrictJieQiActualCast {
 static func main() throws {
   let parser=ISO8601DateFormatter()
   parser.formatOptions=[.withInternetDateTime,.withFractionalSeconds]
   let samples = [
REPLACE_MOMENTS
   ]
   for iso in samples {
     guard let date=parser.date(from:iso) else {
       fatalError("Cannot parse UTC "+iso)
     }
     let chart=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
     print([chart.solarTerm,chart.pillars.year,chart.pillars.month,
            chart.pillars.day,chart.pillars.hour,chart.bureau.dun,
            String(chart.bureau.ju)].joined(separator:"|"))
   }
 }
}
"""

def run():
    verify_source_constants()
    # Real native compiler, rather than inspecting Swift source and asserting success.
    values=",\n".join("      "+json.dumps(x) for x in MOMENTS)
    with tempfile.TemporaryDirectory(prefix="wengua_strict_native_") as folder:
        root=Path(folder)
        main=root/"StrictJieQiActualCast.swift"
        main.write_text(SWIFT_MAIN.replace("REPLACE_MOMENTS",values),encoding="utf8")
        exe=root/"strict_jieqi_native"
        subprocess.run(["swiftc","-O",str(SOURCE),str(main),"-o",str(exe)],
                       cwd=ROOT,check=True,timeout=180)
        output=subprocess.check_output([str(exe)],text=True,timeout=40)
    actual=[tuple(line.split("|")) for line in output.splitlines() if "|" in line]
    expected=[]
    for iso in MOMENTS:
        instant=datetime.fromisoformat(iso.replace("Z","+00:00"))
        local=instant.astimezone(ZoneInfo("America/New_York"))
        facts=solar_chart_clock(local.isoformat(),"America/New_York")
        term=facts["active_solar_term"]
        p=facts["four_pillars"]
        bureau=bureau_for_term(p["day"],term)
        expected.append((term,p["year"],p["month"],p["day"],p["hour"],
                         bureau["dun"],str(bureau["ju"])))
    if actual!=expected:
        pairs=[{"utc":t,"swift":a,"python":e} for t,a,e in
               zip(MOMENTS,actual,expected) if a!=e]
        raise AssertionError("Native/Python strict JieQi real board parity failed: "+
                             json.dumps(pairs,ensure_ascii=False))
    print("STRICT_JIEQI_NATIVE_PYTHON_REAL_CAST_PARITY_PASS",
          len(actual),"actual UTC clocks with verified 2025-2040 crossings")
    for iso,row in zip(MOMENTS,actual):
        print(iso,row[0],row[-2],row[-1])

if __name__=="__main__":
    run()
