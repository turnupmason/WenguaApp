"""First source-grounded shijia zhuanpan casting core, from Shenqi Zhimen.

ONLY fully determines a layout when the solar-term/bureau input and day/hour
ganzhi are already supplied. Calendar conversion and choice of casting variant
remain separate, UNVERIFIED prerequisites; this code must never silently cast
from the device's wall clock. Results are source-text consistency diagnostics,
not independent original scan or astronomical validation.
"""
from __future__ import annotations

from dataclasses import dataclass

from .core import BRANCHES, STEMS, cycle60

EARTH_ORDER = ("戊","己","庚","辛","壬","癸","丁","丙","乙")
RING = (1,8,3,4,9,2,7,6)  # 坎艮震巽离坤兑乾; clockwise
DOORS = {1:"休门",8:"生门",3:"伤门",4:"杜门",9:"景门",
         2:"死门",7:"惊门",6:"开门"}
STARS = {1:"天蓬星",2:"天芮星",3:"天冲星",4:"天辅星",5:"天禽星",
         6:"天心星",7:"天柱星",8:"天任星",9:"天英星"}
GUA = {1:"坎",8:"艮",3:"震",4:"巽",9:"离",2:"坤",7:"兑",6:"乾",5:"中"}
DEITIES = ("值符","螣蛇","太阴","六合","白虎","玄武","九地","九天")
SIX_JIA = {"甲子":"戊","甲戌":"己","甲申":"庚",
           "甲午":"辛","甲辰":"壬","甲寅":"癸"}
YANG_TERMS = {
    "冬至":(1,7,4),"惊蛰":(1,7,4),
    "小寒":(2,8,5),"大寒":(3,9,6),"春分":(3,9,6),
    "芒种":(6,3,9),"谷雨":(5,2,8),"小满":(5,2,8),
    "立春":(8,5,2),"立夏":(4,1,7),"清明":(4,1,7),
    "雨水":(9,6,3),
}
YIN_TERMS = {
    "夏至":(9,3,6),"白露":(9,3,6),"小暑":(8,2,5),
    "秋分":(7,1,4),"大暑":(7,1,4),"立秋":(2,5,8),
    "霜降":(5,8,2),"小雪":(5,8,2),"大雪":(4,7,1),
    "处暑":(1,4,7),"立冬":(6,9,3),"寒露":(6,9,3),
}
TERMS = {**{k:("yang",v) for k,v in YANG_TERMS.items()},
         **{k:("yin",v) for k,v in YIN_TERMS.items()}}
DAY_START_STEMS = {"甲":"甲","己":"甲","乙":"丙","庚":"丙",
                   "丙":"戊","辛":"戊","丁":"庚","壬":"庚",
                   "戊":"壬","癸":"壬"}

SOURCE_KEY = "shenqi/shijia-qiju/v1-20261019"

def _wrap(n:int)->int:
    return (n-1)%9+1

def yuan_from_day(day_ganzhi:str)->tuple[str,str]:
    """Find first Jia/Ji fu-tou backward inside the 60-day cycle, not just day's branch."""
    cycle=cycle60()
    if day_ganzhi not in cycle:
        raise ValueError("Unknown day ganzhi")
    index=cycle.index(day_ganzhi)
    fu_tou=next(cycle[(index-offset)%60] for offset in range(5)
                if cycle[(index-offset)%60][0] in ("甲","己"))
    branch=fu_tou[1]
    yuan= ("upper" if branch in "子午卯酉"
           else "middle" if branch in "寅申巳亥" else "lower")
    return yuan,fu_tou

def bureau_for_term(day_ganzhi:str, solar_term:str)->dict:
    """Treat supplied solar term as trusted external calendar fact only."""
    if solar_term not in TERMS:
        raise ValueError("Unsupported solar term")
    yuan,fu_tou=yuan_from_day(day_ganzhi)
    dun,values=TERMS[solar_term]
    ju=values[{"upper":0,"middle":1,"lower":2}[yuan]]
    return {"dun":dun,"ju":ju,"yuan":yuan,"futou":fu_tou,
            "solar_term":solar_term,
            "calendar_status":"supplied_solar_term_not_independently_checked"}

def hour_branch_from_wall_clock(hour:int)->str:
    """Branch of device local clock; no midnight day-rollover policy imposed."""
    if type(hour) is not int or not 0 <= hour <= 23:
        raise ValueError("Hour must be integer 0..23")
    return BRANCHES[((hour+1)//2)%12]

def hour_ganzhi_from_day(day_stem:str, hour_branch:str)->str:
    """五鼠遁元; relies on externally trusted day stem and local-hour branch."""
    if day_stem not in DAY_START_STEMS or hour_branch not in BRANCHES:
        raise ValueError("Invalid day stem/hour branch")
    offset=BRANCHES.index(hour_branch)
    stem_index=STEMS.index(DAY_START_STEMS[day_stem])
    return STEMS[(stem_index+offset)%10]+hour_branch

def xun_shou(hour_ganzhi:str)->tuple[str,int,str]:
    cycle=cycle60()
    if hour_ganzhi not in cycle:
        raise ValueError("Invalid hour ganzhi")
    offset=cycle.index(hour_ganzhi)%10
    head=cycle[cycle.index(hour_ganzhi)-offset]
    return head,offset,SIX_JIA[head]

def earth_plate(dun:str,ju:int)->dict[int,str]:
    if dun not in ("yin","yang") or type(ju) is not int or not 1 <= ju <= 9:
        raise ValueError("Requires explicitly established yin/yang ju 1..9")
    direction=1 if dun=="yang" else -1
    return {_wrap(ju+i*direction):stem for i,stem in enumerate(EARTH_ORDER)}

def _rotate_to(source:int,dest:int)->dict[int,int]:
    if source not in RING or dest not in RING:
        raise ValueError("Rotating a fixed perimeter requires perimeter palaces")
    shift=(RING.index(dest)-RING.index(source))%8
    return {p:RING[(i+shift)%8] for i,p in enumerate(RING)}

def layout_from_explicit_bureau(*,dun:str,ju:int,hour_ganzhi:str)->dict:
    """Produce source-step chart facts, not a calendar-validated or approved divination.

    星盘 rotates by clockwise palace order in both dun; 八神 travel by
    yin/yang direction. When the 5th palace/天禽 is selected, host 坤二宫
    and travel with 天芮 and their *separate* earth stems.
    """
    earth=earth_plate(dun,ju)
    head,steps,hidden=xun_shou(hour_ganzhi)
    source_palace=next(p for p,stem in earth.items() if stem==hidden)
    source_host=2 if source_palace==5 else source_palace
    value_star=STARS[source_palace]
    value_door=DOORS[source_host]
    if hour_ganzhi[0]=="甲":
        time_symbol=hidden
    else:
        time_symbol=hour_ganzhi[0]
    dest_earth=next(p for p,stem in earth.items() if stem==time_symbol)
    star_target=2 if dest_earth==5 else dest_earth
    star_map=_rotate_to(source_host,star_target)
    # Xun-start palace counts one step per hour over numerals 1..9.
    value_door_target=_wrap(source_palace+steps*(1 if dun=="yang" else -1))
    if value_door_target==5:
        # 时家转盘：旬首宫数九宫逐时行，阴逆阳顺。
        # When timed progress counts into 中五, place the door at Kun-2;
        # rotate the same eight outer doors from their real source host.
        # Never manufacture an ordinary centre door. Applies whether
        # elapsed == 0 or > 0, unlike the obsolete blocked fallback.
        value_door_target=2
    door_map=_rotate_to(source_host,value_door_target)
    heavens={p:[] for p in range(1,10)}
    for p in RING:
        heavens[star_map[p]].append({"star":STARS[p],"carried_stem":earth[p]})
    # The central star travels with the 2nd palace's star.
    heavens[star_map[2]].append({"star":STARS[5],"carried_stem":earth[5]})
    doors={door_map[p]:DOORS[p] for p in RING}
    deity_step=1 if dun=="yang" else -1
    deities={RING[(RING.index(star_target)+deity_step*i)%8]:deity
             for i,deity in enumerate(DEITIES)}
    return {
        "school_id":"shijia_zhuanpan",
        "casting_variant":"shenqi_book_explicit_bureau_v1",
        "status":"source_text_consistency_only",
        "source_key":SOURCE_KEY,
        "dun":dun,"ju":ju,"hour_ganzhi":hour_ganzhi,
        "xun_shou":head,"hidden_stem":hidden,"xun_elapsed_hours":steps,
        "xun_start_palace":source_palace,
        "value_star":value_star,"value_star_palace":star_target,
        "value_door":value_door,"value_door_palace":value_door_target,
        "palaces":{str(p):{
            "palace":p,"gua":GUA[p],"earth_stem":earth[p],
            "heaven_stars":heavens[p],
            "door":doors.get(p),"deity":deities.get(p)
        } for p in range(1,10)},
        "limitations":["Calendar/solar-term method not verified",
                       "Original printed source charts not independently inspected",
                       "Timed centre-door uses Kun-2 host in this Zhuanpan variant; other schools may differ"],
    }
