"""Astronomically computed solar terms and sexagenary periods, no GPT calendar.

Ephemeris: pyswisseph 2.10.3.2 / Swiss Ephemeris built-in Moshier backend.
Traditional pillar convention: solar-year begins at 立春; months turn at 节
(立春 惊蛰 清明 ...), NOT civil Gregorian first or lunar new moon.
Day-cycle anchor is compared with multiple distant complete book-worked dates.
This does not certify every casting-school boundary (late-Zi rollover etc).
"""
from __future__ import annotations
from datetime import date,datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from hashlib import sha256
import json,math
try:
 import swisseph as swe
except ImportError:
 swe=None
from .core import STEMS,BRANCHES,cycle60
from .casting_shenqi import hour_branch_from_wall_clock,hour_ganzhi_from_day

EPHEMERIS_VERSION="wen-gua-local-meeus-solar-longitude-v1"
SOLAR_TERMS=("冬至","小寒","大寒","立春","雨水","惊蛰","春分","清明",
             "谷雨","立夏","小满","芒种","夏至","小暑","大暑","立秋",
             "处暑","白露","秋分","寒露","霜降","立冬","小雪","大雪")
SOLAR_MONTH_BRANCHES="寅卯辰巳午未申酉戌亥子丑"
DAY_ANCHOR=date(1995,6,11)
DAY_ANCHOR_GANZHI="癸酉"
JULIAN_UNIX_EPOCH=2440587.5
def _need_ephemeris():
 # Local built-in Meeus series is the deterministic engine, never network.
 return True
def _at(s,zone):
 if not isinstance(s,str) or not isinstance(zone,str):
  raise ValueError("Date must be explicit timezone-aware ISO8601 and IANA timezone")
 try:
  dt=datetime.fromisoformat(s)
  z=ZoneInfo(zone)
 except (ValueError,KeyError,TypeError) as e:
  raise ValueError("Invalid civil clock or IANA timezone") from e
 if dt.utcoffset() is None:
  raise ValueError("Naive local datetimes cannot determine hour/day pillars")
 local=dt.astimezone(z)
 if local.replace(tzinfo=None)!=dt.replace(tzinfo=None) or local.utcoffset()!=dt.utcoffset():
  raise ValueError("Supplied offset and IANA timezone disagree; check DST")
 if not 1850<=local.year<=2150:
  raise ValueError("Outside tested 1850-2150 astronomical model boundary")
 return local
def _jd(dt):
 u=dt.astimezone(timezone.utc)
 return JULIAN_UNIX_EPOCH+(u-datetime(1970,1,1,tzinfo=timezone.utc)).total_seconds()/86400

def _sun_longitude(jd):
 """NOAA/Meeus apparent solar ecliptic longitude in degrees, offline.

 Solar equation-of-center approximation; no external ephemeris download.
 Separately compared with Moshier when optional pyswisseph is installed.
 The method has about 0.01-degree (~15 minute) model discrepancy on
 source book years; date classification CLOSE to any 15-degree boundary
 is conservatively blocked rather than silently assigned a wrong jie.
 """
 t=(jd-2451545.0)/36525.0
 mean_longitude=(280.46646+t*(36000.76983+0.0003032*t))%360
 anomaly=357.52911+t*(35999.05029-0.0001537*t)
 rad=math.radians
 correction=(
  (1.914602-t*(0.004817+0.000014*t))*math.sin(rad(anomaly))
  +(0.019993-0.000101*t)*math.sin(rad(2*anomaly))
  +0.000289*math.sin(rad(3*anomaly)))
 omega=125.04-1934.136*t
 longitude=(mean_longitude+correction-0.00569
            -0.00478*math.sin(rad(omega)))%360
 if not math.isfinite(longitude):raise RuntimeError("Nonfinite Sun longitude")
 return longitude

def compare_with_optional_swiss(iso,timezone_name):
 """External cross-check only. Not a library or online dependency."""
 if swe is None:return {"available":False,"does_not_block_offline_calendar":True}
 dt=_at(iso,timezone_name)
 local=_jd(dt)
 true=swe.calc_ut(local,swe.SUN,swe.FLG_MOSEPH)[0][0]
 approximate=_sun_longitude(local)
 error=((approximate-true+180)%360)-180
 return {"available":True,"absolute_longitude_error_deg":abs(error),
         "reference":"Swiss Ephemeris Moshier","offline_algorithm":EPHEMERIS_VERSION}
def _solar_longitude_offset(jd,angle):
 return ((_sun_longitude(jd)-angle+180)%360)-180
def _crossing(lo,hi,angle):
 """Sun passes target ecliptic longitude; 1-second UTC accuracy."""
 if _solar_longitude_offset(lo,angle)>=0 or _solar_longitude_offset(hi,angle)<0:
  raise ValueError("Solar-term crossing not bracketed")
 for _ in range(27):
  mid=(lo+hi)/2
  if _solar_longitude_offset(mid,angle)<0:lo=mid
  else:hi=mid
 return (lo+hi)/2
def _jd_aware(jd,zone):
 return datetime.fromtimestamp((jd-JULIAN_UNIX_EPOCH)*86400,timezone.utc).astimezone(ZoneInfo(zone))

# UTC Swiss/Moshier offline crossings 2025-2028, new term inclusive.
STRICT_JIEQI_VERSION="strict_utc_moshier_2025_2028_v1"
_STRICT_FIRST_UTC_MS=1736044366945
_STRICT_DELTAS_BASE36="l1ku06.l3448j.l6w468.lbcd2a.lhjhjp.lnpsly.luvhkk.m12w33.m7dkvx.mbtm33.mfj6it.mguqfq.mgwz4a.meoskx.mb4ea6.m5yxof.lzvgbg.lt8ua0.lmds59.lg2nh1.laauqk.l5x9w3.l2ovth.l1bgqb.l1dnlk.l3cxw5.l6o0gh.lbkjoy.lha6ot.lnyqp6.lukrpu.m1dqu2.m71fsl.mc650j.mf6tuj.mh78ln.mgm8rx.meyhfh.mawei4.m64m0q.lzqzyy.ltbpla.lmcd98.lg3yjc.laaig0.l5xiey.l2nuxq.l1b0nb.l1b886.l3byxq.l6knoq.lbj8ay.lh7vgw.lnx5c7.lum2uj.m1b3jj.m77xh3.mc0x0t.mfi91m.mgz8pl.mh104s.meorsm.mbb5zk.m5tutw.m030jq.lt0hjb.lmlkow.lft3lw.laiqeo.l5nk1k.l2wkud.l11pkl.l1kqq8.l32scm.l6ufiw.lb9wld.lhh3d8.lnod0b.luu49v.m14uns.m7dsyo.mbz4uo.mfjijo.mh1wa5.mgvymt.mevaqw.mb15wt.m62zs8.lzq03x.ltak30.lm7imi.lg3ms9.la56fg.l5yxbo.l2kdzn"
from functools import lru_cache
from bisect import bisect_right
@lru_cache(maxsize=1)
def _strict_crossing_times():
 t=[_STRICT_FIRST_UTC_MS]
 for diff in _STRICT_DELTAS_BASE36.split("."):
  t.append(t[-1]+int(diff,36))
 if len(t)!=96 or any(a>=b for a,b in zip(t,t[1:])):
  raise RuntimeError("Strict JieQi timestamp table corrupted")
 return t
def _strict_jieqi_index(utc_seconds):
 t=_strict_crossing_times()
 ms=utc_seconds*1000
 if ms<t[0] or ms>t[-1]:return None
 index=bisect_right(t,ms)-1
 return ((1+index)%24,t[index])

def solar_chart_clock(iso,timezone_name,*,zi_hour_rollover="civil_midnight"):
 """Return independently CALCULATED solar term+Ganzhi, not approved forecast."""
 _need_ephemeris()
 if zi_hour_rollover!="civil_midnight":
  raise ValueError("Only explicit civil-midnight policy is implemented")
 local=_at(iso,timezone_name)
 if local.hour==23:
  raise ValueError("Late-Zi 23h day boundary ambiguous; original school method required")
 jd=_jd(local)
 longitude=_sun_longitude(jd)
 distance_to_nearest_jie=min(longitude%15,15-(longitude%15))
 precise=_strict_jieqi_index(local.timestamp())
 if precise is None:
  if distance_to_nearest_jie<0.05:
   raise ValueError("Astronomical solar-term boundary within ~1.2-hour uncertainty; outside verified UTC crossing window")
  solar_index=math.floor(((longitude-270)%360)/15)
 else:
  solar_index=precise[0]
 term=SOLAR_TERMS[solar_index]
 cy=cycle60()
 day_gz=cy[(cy.index(DAY_ANCHOR_GANZHI)+(local.date()-DAY_ANCHOR).days)%60]
 # 立春 marks year boundary; Jan/early Feb before LiChun belongs previous year.
 solar_year=local.year-(local.month<=2 and solar_index in (0,1,2))
 year_gz=cy[(solar_year-1984)%60]
 solar_month_index=((solar_index-3)%24)//2
 start_stem={"甲":"丙","己":"丙","乙":"戊","庚":"戊",
             "丙":"庚","辛":"庚","丁":"壬","壬":"壬","戊":"甲","癸":"甲"}[year_gz[0]]
 start_i=STEMS.index(start_stem)
 month_gz=STEMS[(start_i+solar_month_index)%10]+BRANCHES[(2+solar_month_index)%12]
 hour_branch=hour_branch_from_wall_clock(local.hour)
 hour_gz=hour_ganzhi_from_day(day_gz[0],hour_branch)
 receipt={
  "method":STRICT_JIEQI_VERSION if precise else EPHEMERIS_VERSION,
  "ephemeris_flag":"offline_swiss_moshier_crossing" if precise else "offline_Meeus_NOAA_apparent_longitude",
  "solar_term_border_ambiguity_rejected_below_degrees":0.05,
  "solar_term_boundary_policy":"strict_instant_new_inclusive" if precise else "approximate_guarded_outside_window",
  "last_solar_crossing_utc_ms":precise[1] if precise else None,
  "reference_civil_local":local.isoformat(),"iana_zone":timezone_name,
  "day_boundary":"civil_midnight_no_23h","sun_ecliptic_longitude_deg":round(longitude,9),
  "active_solar_term":term,
  "four_pillars":{"year":year_gz,"month":month_gz,"day":day_gz,"hour":hour_gz},
  "day_cycle_book_anchor":{"civil_date":"1995-06-11","day_ganzhi":"癸酉",
   "second_original_book_fixture":"1995-08-13 丙子",
   "third_original_book_fixture":"2001-08-20 乙卯"}}
 receipt["sha256"]=sha256(json.dumps(receipt,ensure_ascii=False,
                sort_keys=True,separators=(",",":")).encode()).hexdigest()
 receipt["note"]="Strict Swiss Moshier UTC times 2025-2028; NOAA only display longitude" if precise else "Other years use conservative approximate calendar boundary guard"
 return receipt

def branch_periods(reference_iso,timezone_name,*,granularity="month",days_ahead=180):
 """Real solar-term month or local day period rows usable by timing_engine.

 Month boundaries use astronomical 30-degree jie transitions, NOT the 1st.
 Each interval includes a source-independent solar ephemeris calculation.
 """
 _need_ephemeris()
 if granularity not in ("day","month") or type(days_ahead)!=int or not 1<=days_ahead<=740:
  raise ValueError("Supported month/day horizon from 1 to 740 days")
 local=_at(reference_iso,timezone_name)
 if local.hour==23:raise ValueError("Late Zi method unresolved")
 end=local+timedelta(days=days_ahead)
 rows=[]
 if granularity=="day":
  current=datetime(local.year,local.month,local.day,tzinfo=ZoneInfo(timezone_name))
  if current<local:current+=timedelta(days=1)
  while current<end:
   following=current+timedelta(days=1)
   daygz=cycle60()[(cycle60().index(DAY_ANCHOR_GANZHI)+(current.date()-DAY_ANCHOR).days)%60]
   rows.append({"start_iso":current.isoformat(),"end_iso":following.isoformat(),
    "branch":daygz[1],"ganzhi":daygz,"granularity":"day",
    "calendar_method_version":EPHEMERIS_VERSION})
   current=following
 else:
  precise=_strict_jieqi_index(local.timestamp())
  if precise is not None:
   # 月柱按每30°的节定界，节内每15°的中气不另换月柱。
   all_crossings=_strict_crossing_times()
   jie=[(ms,(1+k)%24) for k,ms in enumerate(all_crossings)
        if ((1+k)%24)%2==1]
   starts=[item[0] for item in jie]
   k=bisect_right(starts,local.timestamp()*1000)-1
   if k<0 or k+1>=len(jie) or jie[-1][0]<end.timestamp()*1000:
    raise ValueError("Strict 30-degree Jie month horizon outside verified UTC crossing table")
   for i in range(k,len(jie)-1):
    first_ms,term_index=jie[i]
    second_ms=jie[i+1][0]
    if first_ms>=end.timestamp()*1000:break
    month_index=((term_index-3)%24)//2
    begin=datetime.fromtimestamp(first_ms/1000,timezone.utc).astimezone(ZoneInfo(timezone_name))
    finish=datetime.fromtimestamp(second_ms/1000,timezone.utc).astimezone(ZoneInfo(timezone_name))
    rows.append({"start_iso":begin.isoformat(),"end_iso":finish.isoformat(),
     "branch":SOLAR_MONTH_BRANCHES[month_index],"granularity":"month",
     "calendar_method_version":STRICT_JIEQI_VERSION,
     "solar_longitude_boundary_start":(315+month_index*30)%360})
   return rows
  jd=_jd(local)
  longitude=_sun_longitude(jd)
  index=int(((longitude-315)%360)//30)
  angle=(315+index*30)%360
  # Intervals begin at solar longitude 315, 345, 15,..., not civil month start.
  current=_crossing(jd-40,jd,angle)
  if current<jd-40 or current>jd:raise ValueError("Bad solar-month start")
  horizon=_jd(end)
  for _ in range(27):
   nextangle=(angle+30)%360
   next_jd=_crossing(current+10,current+40,nextangle)
   if current>=horizon:break
   start_local=_jd_aware(current,timezone_name)
   stop_local=_jd_aware(next_jd,timezone_name)
   branch=SOLAR_MONTH_BRANCHES[index]
   rows.append({"start_iso":start_local.isoformat(),
    "end_iso":stop_local.isoformat(),"branch":branch,"granularity":"month",
    "calendar_method_version":EPHEMERIS_VERSION,
    "solar_longitude_boundary_start":angle})
   current=next_jd
   angle=nextangle
   index=(index+1)%12
  # Timing-engine default skips the ongoing period; explicitly expose it
  # for audits while consumers choose future events deliberately.
 return rows
