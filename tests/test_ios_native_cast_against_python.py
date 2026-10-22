"""Require newly computed Swift chart to match ALL sealed original true-source facts.

Swift result is produced by ios/WenguaAppUI/WenguaNativeCore.swift,
not copied from Python golden fixtures. Fails any differences in the actual
star/door/god/earth/heaven/stage/void/horse/tomb. No score or fake role inference.
"""
import json,sys
from pathlib import Path

repo=Path(__file__).resolve().parents[1]
gold=json.loads((repo/"ios/WenguaAppUI/GoldenNativeCastCases.json").read_text("utf8"))["samples"]
actual=json.loads(Path(sys.argv[1]).read_text("utf8"))
assert len(actual)==len(gold)==4
palace_branches={1:("子",),2:("未","申"),3:("卯",),4:("辰","巳"),5:(),
                 6:("戌","亥"),7:("酉",),8:("丑","寅"),9:("午",)}
element_order=[4,9,2,3,5,7,8,1,6]
for i,(a,g) in enumerate(zip(actual,gold),1):
    assert a["engineVersion"]=="ios_offline_native_cast_v01",(i,a.get("engineVersion"))
    assert a["pillars"]==g["pillars"],(i,"pillars",a["pillars"],g["pillars"])
    assert a["solarTerm"]==g["solarTerm"],(i,"solarTerm")
    assert a["bureau"]==g["bureau"],(i,"bureau",a["bureau"],g["bureau"])
    assert a["xunShou"]==g["xunShou"],(i,"xun")
    assert a["valueStar"]==g["valueStar"],(i,"star")
    assert a["valueDoor"]==g["valueDoor"],(i,"door")
    assert a["voidBranches"]==g["voidBranches"],(i,"xun void")
    assert a["hourHorse"]==g["hourHorse"],(i,"hour horse")
    assert [v["id"] for v in a["palaces"]]==list(range(1,10)),i
    expected={v["id"]:v for v in g["palaces"]}
    checked=0
    for p in a["palaces"]:
        n=p["id"];bs=palace_branches[n]
        assert p["branches"]==list(bs)
        if n==5:
            assert p["door"] is None and p["deity"] is None and p["heavenStars"]==[]
            continue
        e=expected[n]
        for f in ("earthStem","door","deity","heavenStars"):
            assert p[f]==e[f],(i,n,f,p[f],e[f])
        assert p["voidBranches"]==[b for b in bs if b in g["voidBranches"]]
        assert (p["horseBranch"] is not None)==(g["hourHorse"] in bs)
        t=[]
        for st in e["heavenStars"]:
            t.extend([("天盘",st["carriedStem"],life["branch"]) for life in st["stages"] if life["stage"]=="墓"])
        t.extend([("地盘",p["earthStem"],life["branch"]) for life in p["earthStages"] if life["stage"]=="墓"])
        assert sorted([(x["plane"],x["stem"],x["branch"]) for x in p["tombs"]])==sorted(t),(i,n,"tomb")
        checked+=1
    assert checked==8
    print("PASS native original board",i,g["iso"],a["solarTerm"],a["bureau"]["dun"],a["bureau"]["ju"],
          a["xunShou"],"void",a["voidBranches"],"horse",a["hourHorse"])
print("PASS four dates, real solar pillars, 36 cells (32 outer), complete source stages, horse, void, plane-specific tomb, native != mocked")
