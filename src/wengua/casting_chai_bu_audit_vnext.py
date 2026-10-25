"""Read-only verification of user's 时家拆补转盘 casting sequence.

Do not replace the existing two nine-palace original-book fixtures, or
pretend Meeus approximate solar longitude is an exact Swiss ephemeris.
At the 24 节气 transition the current online-independent calendar rejects
boundary-near timestamps rather than fabricate an exact solar-term side.
"""
from __future__ import annotations
from datetime import datetime,timezone,timedelta

from .casting_shenqi import (
    RING,DOORS,STARS,DEITIES,SIX_JIA,EARTH_ORDER,earth_plate,xun_shou,
    _rotate_to,_wrap)
from .astro_calendar import (
    solar_chart_clock,_jd,_at,_crossing,_sun_longitude,SOLAR_TERMS,
    JULIAN_UNIX_EPOCH)

def exact_within_offline_model_term_receipt(*,iso,timezone_name):
    """24×15° crossing times by model bisection; not independently exact astronomy.

    A protected core calendar may refuse near-boundary times due to model
    accuracy; never force assignment in the protected ±0.05° band.
    """
    clock=solar_chart_clock(iso,timezone_name)
    now=_at(iso,timezone_name)
    jd=_jd(now)
    longitude=_sun_longitude(jd)
    step=int(((longitude-270)%360)//15)
    active_angle=(270+step*15)%360
    next_angle=(active_angle+15)%360
    started=_crossing(jd-21,jd,active_angle)
    will=_crossing(jd,jd+21,next_angle)
    def utc(j):return datetime.fromtimestamp(
        (j-JULIAN_UNIX_EPOCH)*86400,timezone.utc).isoformat()
    return {
        "solar_term":SOLAR_TERMS[step],
        "model_crossing_utc":utc(started),
        "next_model_crossing_utc":utc(will),
        "observed_at_utc":now.astimezone(timezone.utc).isoformat(),
        "calendar_model":clock["method"],
        "near_term_guard_degrees":0.05,
        "astronomical_externally_verified":False,
        "rule":"solar_term_24_true_crossing_clock_is_gate_with_model_uncertainty",
        "clock_receipt_sha256":clock["sha256"],
    }

def verify_original_cast_steps(*,chart):
    """Validate original user sequence against already-cast factual chart.

    地盘阴阳顺逆→旬首→值符随时干→值使随时宫→神随大值符→
    天禽/中五天盘干寄坤二. Any mismatch raises rather than re-casts.
    """
    dun,ju,hour=chart["dun"],chart["ju"],chart["hour_ganzhi"]
    earth=earth_plate(dun,ju)
    for p in range(1,10):
        assert chart["palaces"][str(p)]["earth_stem"]==earth[p],("earth",p)
    head,steps,hidden=xun_shou(hour)
    source=next(p for p,stem in earth.items() if stem==hidden)
    source_host=2 if source==5 else source
    target_stem=hidden if hour[0]=="甲" else hour[0]
    destination=next(p for p,stem in earth.items() if stem==target_stem)
    target_host=2 if destination==5 else destination
    assert chart["xun_shou"]==head
    assert chart["value_star"]==STARS[source]
    assert chart["value_star_palace"]==target_host
    assert chart["value_door"]==DOORS[source_host]
    assert chart["palaces"][str(target_host)]["deity"]=="值符"
    star_rot=_rotate_to(source_host,target_host)
    for native in RING:
        target=star_rot[native]
        assert {"star":STARS[native],"carried_stem":earth[native]} in chart["palaces"][str(target)]["heaven_stars"],("star",native)
    central_star={"star":STARS[5],"carried_stem":earth[5]}
    assert central_star in chart["palaces"][str(star_rot[2])]["heaven_stars"]
    assert chart["palaces"]["5"]["heaven_stars"]==[]
    assert chart["palaces"]["5"]["door"] is None
    assert chart["palaces"]["5"]["deity"] is None
    expected_door=_wrap(source+steps*(1 if dun=="yang" else -1))
    if expected_door==5:
        if source==5 and steps==0 and destination==5:
            expected_door=source_host
        else:
            # Current unchanged source code does NOT invent a door in centre.
            raise ValueError("Unknown nonzero-step value door reaches centre 5")
    door_rot=_rotate_to(source_host,expected_door)
    for palace,name in DOORS.items():
        assert chart["palaces"][str(door_rot[palace])]["door"]==name,("door",palace)
    direction=1 if dun=="yang" else -1
    for index,deity in enumerate(DEITIES):
        palace=RING[(RING.index(target_host)+direction*index)%8]
        assert chart["palaces"][str(palace)]["deity"]==deity,("deity",palace)
    return {
        "verified":True,
        "earth_plate_luoshu_yang_forward_yin_reverse":True,
        "xun_shou":head,"xun_earth_palace":source,
        "chief_star_original":STARS[source],
        "chief_star_follows_hour_stem_to_palace":target_host,
        "chief_door_original":DOORS[source_host],
        "chief_door_follows_hour_palace":expected_door,
        "eight_deities_follows_value_star_yin_reverse_yang_forward":True,
        "centre_tianqin_and_heaven_stem_travel_with_kun_two":True,
        "existing_casting_method_not_replaced":True,
        "user_cast_rule_review_version":"chai_bu_user_process_audit_20261024_v1",
    }
