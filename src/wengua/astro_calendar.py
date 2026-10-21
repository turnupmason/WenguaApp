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

EPHEMERIS_VERSION="pyswisseph-moshier-2.10.3.2-solar-term-v1"
SOLAR_TERMS=("冬至","小寒","大寒","立春","雨水","惊蛰","春分","清明",
             "谷雨","立夏","小满","芒种","夏至","小暑","大暑","立秋",
             "处暑","白露","秋分","寒露","霜降","立冬","小雪","大雪")
SOLAR_MONTH_BRANCHES="寅卯辰巳午未申酉戌亥子丑"
DAY_ANCHOR=date(1995,6,11)
DAY_ANCHOR_GANZHI="癸酉"
JULIAN_UNIX_EPOCH=2440587.5
def _need_ephemeris():
 if swe is None:
  raise RuntimeError("Install explicitly pinned pyswisseph==2.10.3.2; no guessed solar terms")
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
 return swe.julday(u.year,u.month,u.day,u.hour+u.minute/60+
                   u.second/3600+u.microsecond/3600000000)
def _sun_longitude(jd):
 _need_ephemeris()
 try:
  p,flags=swe.calc_ut(jd,swe.SUN,swe.FLG_MOSEPH|swe.FLG_SPEED)
 except Exception as e:
  raise RuntimeError("Cannot compute Sun longitude from Moshier ephemeris") from e
 if not math.isfinite(p[0]) or not 0<=p[0]<360:
  raise RuntimeError("Invalid solar ecliptic longitude")
 return p[0]
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
 solar_index=math.floor(((longitude-270)%360)/15)
 term=SOLAR_TERMS[solar_index]
 cy=cycle60()
 day_gz=cy[(cy.index(DAY_ANCHOR_GANZHI)+(local.date()-DAY_ANCHOR).days)%60]
 # 立春 marks year boundary; Jan/early Feb before LiChun belongs previous year.
 solar_year=local.year-(local.month<=2 and 270<=longitude<315)
 year_gz=cy[(solar_year-1984)%60]
 solar_month_index=int(((longitude-315)%360)//30)
 start_stem={"甲":"丙","己":"丙","乙":"戊","庚":"戊",
             "丙":"庚","辛":"庚","丁":"壬","壬":"壬","戊":"甲","癸":"甲"}[year_gz[0]]
 start_i=STEMS.index(start_stem)
 month_gz=STEMS[(start_i+solar_month_index)%10]+BRANCHES[(2+solar_month_index)%12]
 hour_branch=hour_branch_from_wall_clock(local.hour)
 hour_gz=hour_ganzhi_from_day(day_gz[0],hour_branch)
 receipt={
  "method":EPHEMERIS_VERSION,"ephemeris_flag":"FLG_MOSEPH",
  "reference_civil_local":local.isoformat(),"iana_zone":timezone_name,
  "day_boundary":"civil_midnight_no_23h","sun_ecliptic_longitude_deg":round(longitude,9),
  "active_solar_term":term,
  "four_pillars":{"year":year_gz,"month":month_gz,"day":day_gz,"hour":hour_gz},
  "day_cycle_book_anchor":{"civil_date":"1995-06-11","day_ganzhi":"癸酉",
   "second_original_book_fixture":"1995-08-13 丙子",
   "third_original_book_fixture":"2001-08-20 乙卯"}}
 receipt["sha256"]=sha256(json.dumps(receipt,ensure_ascii=False,
                sort_keys=True,separators=(",",":")).encode()).hexdigest()
 receipt["note"]="Astronomical conversion receipt; does not certify prediction or historical method variant"
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
