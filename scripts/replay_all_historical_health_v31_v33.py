"""Reproduce V3.1 OFFLINE severity text on every indexed two-book illness event.

Uses only book PRE-disclosure date, hour, bureau, value symbol, and relationship.
No author outcome or retrospective explanation reaches analyze_health_severity_v31.
V3.1 is never modified; blocked relationships/uncertain source charts stay blocked.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_v31 import analyze_health_severity_v31

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "archives/sqlite/WenguaApp_双书194案例_两例新家族V31离线回测V3_2_完整研究库.sqlite3"
PARENT_SHA = "e4110828bbfb621e1bb7ed972284d4602d2ab361a12edc48d6f4750c965dddf9"
SHENQI = ROOT / "data/knowledge/shenqi/health_prediction_ch01/case_index.json"
KAIWU = ROOT / "data/knowledge/kaiwu/health_prediction_ch02_section01/case_index.json"
FINAL = ROOT / "data/knowledge/kaiwu/questions_answers_errors_and_methods_ch03/case_index.json"

# Clock anchors within the book's stated Chinese local double-hour. For an
# unknown exact minute, this is ONLY a canonical hour anchor, not an invented
# minute when the prediction was actually made.
# Manual source parameters below are transcriptions of the FIRST question's
# pillars, named source bureau, value star and door, never its answer.
CASES = [
 dict(id="shenqi.health.19960316.self_surgery",date="1996-03-16",clock="16:30",day="壬子",hour="戊申",dun="yang",ju=3,star="天柱星",door="惊门",relation="self",context="direct_self",source="shenqi",original_intent="health",minute_known=False),
 dict(id="shenqi.health.19960727.father_illness",date="1996-07-27",clock="16:00",day="乙丑",hour="甲申",dun="yin",ju=7,star="天禽星",door="死门",relation="father",context="direct_proxy",sex="male",source="shenqi",original_intent="health",minute_known=False),
 dict(id="shenqi.health.19960509.nephew_discharge",date="1996-05-09",clock="16:20",day="丙午",hour="丙申",dun="yang",ju=7,star="天蓬星",door="休门",relation="nephew",context="direct_proxy",sex="male",source="shenqi",original_intent="discharge",minute_known=True),
 dict(id="shenqi.health.19960523.aunt_illness",date="1996-05-23",clock="20:00",day="庚申",hour="丙戌",dun="yang",ju=8,star="天蓬星",door="休门",relation="older_relative",context="direct_proxy",sex="female",relative_specific="aunt",source="shenqi",original_intent="health",minute_known=False),
 dict(id="shenqi.health.19961102.on_site_health",date="1996-11-02",clock="16:00",day="癸卯",hour="庚申",dun="yin",ju=8,star="天冲星",door="伤门",relation="self",context="direct_self",source="shenqi",original_intent="health",minute_known=False),
 dict(id="shenqi.health.19971227.spouse_travel_for_treatment",date="1997-12-27",clock="21:30",day="癸卯",hour="癸亥",dun="yang",ju=7,star="天冲星",door="伤门",relation="spouse",context="direct_proxy",sex="female",source="shenqi",original_intent="travel_for_treatment",minute_known=False,pre_block="V3.1 spouse has no verified principal personal signifier; no silent self/day substitution"),
 dict(id="kaiwu.health.19960923.nasal_cancer",date="1996-09-23",clock="18:00",day="癸亥",hour="辛酉",dun="yin",ju=4,star="天任星",door="生门",relation="colleague",context="event_news",source="kaiwu",original_intent="health",minute_known=False),
 dict(id="kaiwu.health.19950219.brother_paralysis",date="1995-02-19",clock="09:30",day="辛巳",hour="癸巳",dun="yang",ju=9,star="天芮星",door="死门",relation="younger_sibling",context="direct_proxy",sex="male",birth_ganzhi="癸丑",source="kaiwu",original_intent="health",minute_known=False),
 dict(id="kaiwu.health.19980616.hen_illness",date="1998-06-16",clock="09:15",day="甲午",hour="己巳",dun="yang",ju=6,star="天心星",door="开门",relation="animal_hen",source="kaiwu",original_intent="animal_health",minute_known=True,pre_block="V3.1 actor_profiles does not define animals; cannot bind hen to patient palace"),
 dict(id="kaiwu.health.19980621.rooster_illness",date="1998-06-21",clock="07:45",day="己亥",hour="戊辰",dun="yang",ju=3,star="天冲星",door="伤门",relation="animal_rooster",source="kaiwu",original_intent="animal_health",minute_known=True,pre_block="V3.1 lacks animal role; original printed 巽4 palace also has two missing stems"),
 dict(id="kaiwu.health.19991020.wang_craniotomy",date="1999-10-20",clock="15:20",day="乙巳",hour="甲申",dun="yin",ju=3,star="天蓬星",door="休门",relation="self",context="direct_self",source="kaiwu",original_intent="surgery",minute_known=True),
 dict(id="kaiwu.final.recovery",date="2000-06-05",clock="21:30",day="甲午",hour="乙亥",dun="yang",ju=6,star="天柱星",door="惊门",relation="son_in_law",source="final",original_intent="recovery",minute_known=True,pre_block="V3.1 has no son-in-law route and original shared nine-palace print is spatially unverified OCR"),
]

def evaluate(*, db_path=PARENT):
    db = Path(db_path)
    if not db.is_file() or hashlib.sha256(db.read_bytes()).hexdigest() != PARENT_SHA:
        raise ValueError("Exact immutable latest V3.2 full 194-case parent required")
    s = {x["id"]: x for x in json.loads(SHENQI.read_text("utf8"))["cases"]}
    k = {x["id"]: x for x in json.loads(KAIWU.read_text("utf8"))["cases"]}
    f = {x["case_id"]: x for x in json.loads(FINAL.read_text("utf8"))["new_cases"]}
    if len(CASES) != 12 or len({x["id"] for x in CASES}) != 12:
        raise ValueError("Repeated or missing case family")
    if len(s) != 6 or len(k) != 6:
        raise ValueError("Dedicated health chapter corpus changed; re-audit scope")
    if sum(x["id"] == "shenqi.health.19960727.father_illness" for x in CASES) != 1:
        raise ValueError("Cross-book same father event duplicated")
    items = []
    for spec in CASES:
        row = {"family_id":spec["id"],"source":spec["source"],"source_date":spec["date"],
               "source_day":spec["day"],"source_hour":spec["hour"],
               "bureau":{"dun":spec["dun"],"ju":spec["ju"]},
               "value_symbols":{"star":spec["star"],"door":spec["door"]},
               "relationship":spec["relation"],"source_question_intent":spec["original_intent"],
               "template_intent":"severity","date_time_anchor":spec["date"]+"T"+spec["clock"]+":00+08:00",
               "minute_exactly_attested":bool(spec["minute_known"]),
               "author_judgment_loaded":False,"later_feedback_loaded":False,
               "status":"pending","user_approval":"pending"}
        if spec["source"] == "shenqi":
            orig = s[spec["id"]]["casting"]
            for x,y in (("date",spec["date"]),("day_ganzhi",spec["day"]),("hour_ganzhi",spec["hour"]),
                        ("dun",spec["dun"]),("ju",spec["ju"]),("value_star",spec["star"]),("value_door",spec["door"])):
                if orig[x] != y:
                    raise ValueError("Source first-question metadata discrepancy "+spec["id"]+" "+x)
        elif spec["source"] == "kaiwu":
            orig = k.get(spec["id"])
            if orig is None or orig["date"] != spec["date"] or orig["hour"] != spec["hour"]:
                raise ValueError("Kaiwu source case mismatch "+spec["id"])
        elif spec["source"] == "final" and spec["id"] not in f:
            raise ValueError("Final chapter health case missing")
        if spec.get("pre_block"):
            row.update(status="blocked_unverified_role_or_chart",reason=spec["pre_block"])
            items.append(row)
            continue
        try:
            cal = solar_chart_clock(row["date_time_anchor"],"Asia/Shanghai")["four_pillars"]
            row["calendar_pillars"] = cal
            if cal["day"] != spec["day"] or cal["hour"] != spec["hour"]:
                raise ValueError("Source day/hour differs from independent civil-calendar recast")
            board = layout_from_explicit_bureau(dun=spec["dun"],ju=spec["ju"],hour_ganzhi=spec["hour"])
            if board["value_star"] != spec["star"] or board["value_door"] != spec["door"]:
                raise ValueError("Source value star/door differs from real nine-palace casting")
            if spec["source"] == "shenqi":
                orig = s[spec["id"]]["casting"]
                for key in ("value_star_palace","value_door_palace"):
                    if key in orig and orig[key] != board[key]:
                        raise ValueError("Source "+key+" differs from real casting")
            question = {"intent":"severity","relationship":spec["relation"],"consultation_context":spec["context"]}
            if spec.get("sex"): question["patient_sex"] = spec["sex"]
            if spec.get("relative_specific"): question["relative_specific"] = spec["relative_specific"]
            if spec.get("birth_ganzhi"): question["patient_birth_ganzhi"] = spec["birth_ganzhi"]
            input_cal = {"year_ganzhi":cal["year"],"month_ganzhi":cal["month"],
                         "day_ganzhi":cal["day"],"hour_ganzhi":cal["hour"],"month_branch":cal["month"][1]}
            result = analyze_health_severity_v31(chart=board,inquiry=question,calendar=input_cal,db_path=db)
            content = result["reading_text"]
            if not content or "病凶" not in content and "病吉" not in content:
                raise ValueError("No full fixed-template reading")
            row.update(status="rendered_v31",readout=content,
                readout_sha256=hashlib.sha256(content.encode("utf8")).hexdigest(),
                sections=result["sections"],traditional_verdict=result["audit"]["traditional_verdict"]["verdict"],
                value_star_palace=board["value_star_palace"],value_door_palace=board["value_door_palace"],
                note=("V3.1 severity-only retrospective proxy; NOT a treatment/surgery/discharge prediction"
                      if spec["original_intent"] not in ("health","animal_health") else
                      "V3.1 book-method traditional severity-only retrospective replay"))
        except (ValueError,KeyError,IndexError,TypeError) as e:
            row.update(status="blocked_runtime_or_source_mismatch",reason=type(e).__name__+": "+str(e))
        items.append(row)
    return {"schema":"wengua_v33_all_indexed_health_events_v31_engine_unchanged",
            "exact_parent_v32_sha256":PARENT_SHA,
            "source_scope":{"shenqi_unique":6,"kaiwu_unique_new":5,"kaiwu_cross_book_duplicate":1,
                            "kaiwu_final_recovery_additional":1,"total_unique_events":12},
            "selected_cases_have_author_feedback_as_input":False,
            "readout_generator":"src.wengua.health_severity_v31.analyze_health_severity_v31",
            "model_or_network_rephrasing":False,
            "traditional_outcomes_not_accepted_as_medical_forecasts":True,
            "records":items,
            "counts":{"rendered_v31":sum(x["status"]=="rendered_v31" for x in items),
                      "blocked":sum(x["status"].startswith("blocked") for x in items)}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = evaluate()
    for row in out["records"]:
        print(row["family_id"],row["status"],row.get("traditional_verdict",""),
              row.get("reason",""),row.get("readout_sha256",""))
    print(json.dumps(out["counts"],ensure_ascii=False))
    if args.out:
        target=Path(args.out)
        if target.exists(): raise ValueError("Do not replace a previous sealed report")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

if __name__=="__main__":
    main()
