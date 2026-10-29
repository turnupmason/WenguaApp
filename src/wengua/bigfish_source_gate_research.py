"""Mac research-only source adapter for BigFish physical nine-palace facts.

Not part of frozen V8 scoring and not approved as iPhone production.
The legacy renderer deliberately verifies its *Shenqi* casting by recasting
inside _validate_chart. For a different real casting source, that would force
the old board over the user's chosen BigFish board. This context manager
changes only the old source-identity gate while the original V8 math runs.
Never use this for app publishing; two-source independent parity is pending.
"""
from __future__ import annotations
from contextlib import contextmanager
from .casting_shenqi import xun_shou, SIX_JIA

_GUAS={1:"坎",2:"坤",3:"震",4:"巽",5:"中",6:"乾",7:"兑",8:"艮",9:"离"}
_STARS={"天蓬星","天芮星","天冲星","天辅星","天心星","天柱星","天任星","天英星","天禽星"}
_DOORS={"休门","生门","伤门","杜门","景门","死门","惊门","开门"}
_GODS={"值符","螣蛇","太阴","六合","白虎","玄武","九地","九天"}

def validate_bigfish_candidate(chart):
    if chart.get("school_id")!="shijia_zhuanpan" or chart.get("casting_variant")!="bigfish_shijia_chaibu_pilot":
        raise ValueError("BigFish research adapter only accepts explicit BigFish shijia chaibu candidates")
    if chart.get("status")!="bigfish_unapproved_candidate":
        raise ValueError("Do not bypass source gates without audit-only provenance")
    if chart.get("source_key")!="perfhelf/bigfishmarquis-qimen@6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c":
        raise ValueError("Wrong upstream source commit")
    if chart.get("dun") not in ("yang","yin") or type(chart.get("ju")) is not int or not 1<=chart["ju"]<=9:
        raise ValueError("Invalid original BigFish bureau")
    xun,_,hidden=xun_shou(chart.get("hour_ganzhi",""))
    if chart.get("xun_shou")!=xun or chart.get("hidden_stem")!=hidden or SIX_JIA[xun]!=hidden:
        raise ValueError("Hidden Jia/xun integrity failed")
    pals=chart.get("palaces")
    if not isinstance(pals,dict) or set(pals)!={str(i) for i in range(1,10)}:
        raise ValueError("Exactly nine genuine palaces are required")
    stars=[];doors=[];deities=[];earth=[]
    for i in range(1,10):
        p=pals[str(i)]
        if p.get("palace")!=i or p.get("gua")!=_GUAS[i]:
            raise ValueError("Wrong palace number / gua")
        e=p.get("earth_stem")
        if not isinstance(e,str) or len(e)!=1 or e not in "戊己庚辛壬癸丁丙乙":
            raise ValueError("Missing physical earth-stem")
        earth.append(e)
        entries=p.get("heaven_stars")
        if not isinstance(entries,list):raise ValueError("Missing physical star list")
        if i==5:
            if entries or p.get("door") is not None or p.get("deity") is not None:
                raise ValueError("No invented middle-five ordinary star/door/god")
            continue
        for s in entries:
            if s.get("star") not in _STARS or s.get("carried_stem") not in "戊己庚辛壬癸丁丙乙":
                raise ValueError("Invalid independent physical heavenly carrier")
            stars.append(s["star"])
        if p.get("door") not in _DOORS or p.get("deity") not in _GODS:
            raise ValueError("Missing eight doors/deities")
        doors.append(p["door"]);deities.append(p["deity"])
    if len(set(earth))!=9 or len(stars)!=9 or set(stars)!=_STARS:
        raise ValueError("Physical 9 earth, 9 sky/star identities not complete")
    if len(doors)!=8 or len(set(doors))!=8 or len(deities)!=8 or len(set(deities))!=8:
        raise ValueError("Physical eight doors / gods not complete")
    if chart.get("value_door") not in _DOORS or chart.get("value_star") not in _STARS:
        raise ValueError("Missing real value star/door")
    if chart.get("value_door_palace") not in range(1,10) or chart.get("value_star_palace") not in range(1,10):
        raise ValueError("Missing real value star/door palace")
    return chart


@contextmanager
def bigfish_candidate_only(chart):
    """Temporarily replace only the V22 Shenqi-identity check, not any score.

    This is process-global monkeypatching, unsafe for concurrent production.
    Standalone single-thread Mac worker only. The old source is restored even
    after failure. No pretense that the original V8 source validation passed.
    """
    validate_bigfish_candidate(chart)
    from . import health_severity_v22
    original=health_severity_v22._validate_chart
    def accept(incoming):
        if incoming is not chart:
            raise ValueError("Rejected accidental unrelated chart input")
        return validate_bigfish_candidate(incoming)
    health_severity_v22._validate_chart=accept
    try:
        yield
    finally:
        health_severity_v22._validate_chart=original
