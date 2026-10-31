"""Every strict 2025-2040 JieQi UTC instant; preserve legacy and 23h guard.

No network or Swiss runtime dependency. Physics source generated offline earlier;
these tests verify source-table continuity and fail-closed casting integration.
"""
import json
import unittest
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

from src.wengua.astro_calendar import (
    _strict_crossing_times,_strict_jieqi_index,solar_chart_clock,
    SOLAR_TERMS,STRICT_JIEQI_VERSION,
)

ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/"data/calendar/strict_jieqi_moshier_2025_2040.json"
OLD=ROOT/"data/calendar/strict_jieqi_moshier_2025_2028.json"


def expand(payload):
    values=[payload["first_utc_ms"]]
    for delta in payload["delta_base36"].split("."):
        values.append(values[-1]+int(delta,36))
    return values


class CompleteStrictSolarTermTimeline(unittest.TestCase):
    def test_all_table_entries_and_legacy_96_are_exact(self):
        new=json.loads(NEW.read_text("utf8"))
        old=json.loads(OLD.read_text("utf8"))
        values=expand(new)
        self.assertEqual(new["count"],385)
        self.assertEqual(len(values),385)
        self.assertEqual(values,_strict_crossing_times())
        self.assertEqual(values[:96],expand(old))
        self.assertEqual(values,sorted(set(values)))
        self.assertEqual(values[95],1860999580462)
        self.assertEqual(values[96],1862271714831)
        self.assertEqual(values[383],2239684370770)
        self.assertEqual(values[384],2240956087976)
        self.assertEqual(new["terminal_sentinel_year"],2041)
        self.assertEqual(new["terminal_sentinel_term"],"小寒")

    def test_exact_new_term_inclusive_for_all_385_crossing_instants(self):
        values=_strict_crossing_times()
        zone=ZoneInfo("America/New_York")
        real_casts=0
        for i,at in enumerate(values):
            old_term=SOLAR_TERMS[i%24]
            new_term=SOLAR_TERMS[(i+1)%24]
            utc=datetime.fromtimestamp(at/1000,timezone.utc)
            pre=utc-timedelta(milliseconds=1)
            post=utc+timedelta(milliseconds=1)
            # First boundary precedes coverage; do not invent previous term.
            if i:
                self.assertEqual(_strict_jieqi_index(pre.timestamp())[0],i%24)
            self.assertEqual(_strict_jieqi_index(utc.timestamp()),((i+1)%24,at))
            if i<384:
                self.assertEqual(_strict_jieqi_index(post.timestamp()),((i+1)%24,at))
            # Keep strict 23-hour rollover refusal intact. A crossing instant
            # can itself happen at 23:xx in a particular timezone; select the
            # separately verified UTC instant but do not fabricate a day pillar.
            # The 2041 Xiaohan crossing is an UPPER sentinel: the instant
            # itself is included, but +1ms is deliberately outside coverage.
            moments=(pre,utc) if i==384 else (pre,utc,post)
            civil=[q.astimezone(zone) for q in moments]
            if i==0 or 23 in [q.hour for q in civil]:
                continue
            results=[solar_chart_clock(q.isoformat(),"America/New_York")
                     for q in civil]
            self.assertEqual(
                [r["active_solar_term"] for r in results],
                [old_term,new_term] if i==384 else [old_term,new_term,new_term],
                "UTC crossing "+utc.isoformat())
            self.assertTrue(all(r["method"]==STRICT_JIEQI_VERSION
                                for r in results))
            self.assertEqual(len({r["four_pillars"]["hour"] for r in results}),1)
            real_casts+=1
        self.assertGreaterEqual(real_casts,280)

    def test_all_calendar_years_2029_through_2040_retain_utc_source(self):
        for year in range(2029,2041):
            for month,day in ((2,10),(6,10),(12,30)):
                utc=datetime(year,month,day,17,tzinfo=timezone.utc)
                local=utc.astimezone(ZoneInfo("America/New_York"))
                cal=solar_chart_clock(local.isoformat(),"America/New_York")
                self.assertEqual(cal["solar_term_boundary_policy"],
                                 "strict_instant_new_inclusive")
                self.assertEqual(cal["method"],STRICT_JIEQI_VERSION)
        last=datetime.fromisoformat("2040-12-31T22:59:59+00:00")
        local=last.astimezone(ZoneInfo("America/New_York"))
        self.assertEqual(
            solar_chart_clock(local.isoformat(),"America/New_York")["active_solar_term"],
            "冬至")

if __name__=="__main__":
    unittest.main()
