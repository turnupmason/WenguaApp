"""Fixed user-selected 2026-10-28 06:00/10:00 EDT: six relatives each.

Produces exactly twelve SOURCE-VERBATIM V8/V10.2 reports, without any LLM
rewrite or feedback-tuned score. Sibling month-stem remains research-candidate
under actual actor_profiles.json. No patient birth year was provided.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ZONE = "America/New_York"
CLOCKS = ("2026-10-28T06:00:00-04:00","2026-10-28T10:00:00-04:00")
RELATIONS = (
    ("father","父亲","source_conditional"),
    ("mother","母亲","analogy"),
    ("grandfather","爷爷","conditional_elder_analogy"),
    ("grandmother","奶奶","conditional_elder_analogy"),
    ("older_sibling","姐姐","research_candidate"),
    ("younger_sibling","弟弟","research_candidate"),
)
SOURCE_SCHEMA = "wengua_v80_twelve_two_clocks_source_draft_v1"


def collect():
    readings=[]
    for instant in CLOCKS:
        for relation,label,known_scope in RELATIONS:
            result=auto_cast_health_review_text(
                iso=instant,timezone_name=ZONE,inquiry={
                    "intent":"severity","relationship":relation,
                    "consultation_context":"direct_proxy"
                })
            quant=result["full_health_role_strength_network"]["candidate_five_grade_quantization"]
            summary=quant["summary"]
            confidence=result["audit"]["role_confidence"]
            roles=quant["roles"]
            selected={k:{"primary_strength_25":{"strength_label":v["strength"],"symbol":v["symbol"],"kind":v["kind"],"fact_id":v["fact_id"],"symbol_month_stage":v["month_stage"]}} for k,v in result["full_health_role_strength_network"]["nodes"].items()}
            patient=roles["patient"]
            illness=roles["illness"]
            four=result["four_pillars"]
            assert four["year"]=="丙午" and four["month"]=="戊戌" and four["day"]=="乙亥"
            assert four["hour"]==("己卯" if "T06:" in instant else "辛巳")
            assert not any(k in roles for k in ("natal","birth"))
            assert summary["score"] in (-5,-4,-3,-2,-1,0,1,2,3,4,5)
            assert patient["palace"] in (1,2,3,4,6,7,8,9)
            expected_aux=6 if relation in ("father","grandfather") else 2 if relation in ("mother","grandmother") else None
            got_aux=roles.get("gender",{}).get("palace")
            assert got_aux==expected_aux, (relation,got_aux,expected_aux)
            if relation in ("older_sibling","younger_sibling"):
                assert confidence=="research_candidate_only"
            report={
                "instant":instant,"relationship_id":relation,"label":label,
                "person_scope":known_scope,"source_confidence":confidence,
                "pillars":four,"solar_term":result["solar_term"],
                "bureau":result["bureau"],
                "selected_palaces":result["scored_relevant_palaces"],
                "patient": {
                    "palace":patient["palace"],
                    "source_strength":selected["patient"]["primary_strength_25"],
                    "palace_net":patient["palace_score"]["score"],
                    "void":patient["palace_score"]["void_state"],
                },
                "illness": {
                    "palace":illness["palace"],
                    "source_strength":selected["illness"]["primary_strength_25"],
                    "palace_net":illness["palace_score"]["score"],
                    "void":illness["palace_score"]["void_state"],
                },
                "score":summary["score"],
                "raw_before_saturation":summary["raw_final_before_saturation"],
                "summary":summary,
                "verdict":result["verdict"],
                "sections":result["sections"],
                "template_verbatim":result["reading_text"],
                "no_birth_ganzhi_fabricated":True,
                "is_medical_diagnosis":False,
                "is_literary_revision":False,
                "not_a_blind_test":True
            }
            readings.append(report)
    assert len(readings)==12
    assert {r["label"] for r in readings}=={x[1] for x in RELATIONS}
    assert {r["instant"] for r in readings}==set(CLOCKS)
    return {"schema":SOURCE_SCHEMA,"timezone":ZONE,"frozen_logic":"V8.0",
            "live_copy":"V10.2","source":"auto_cast_health_review_text",
            "not_final_app_readings":True,"readings":readings}


def compact_report(payload):
    lines=[
        "# 2026-10-28 上午06:00与10:00 · 六位亲属12份V8源断词（预生成文学实验底稿）",
        "",
        "两真实时辰 × 父亲/母亲/爷爷/奶奶/姐姐/弟弟。美国东部时区EDT。未提供出生年命，绝不补造。",
        "以下为冻结引擎原始中文，非GPT润色、未人工批准、亦非医学判断；姐姐与弟弟的月干人物规则仅为待核同辈候选。",
        "",
    ]
    for i,item in enumerate(payload["readings"],1):
        lines.extend([
            f'## {i:02d} {item["instant"]} · {item["label"]}',
            "",
            "四柱："+"/".join(item["pillars"][x] for x in ("year","month","day","hour"))+
            f'；{item["bureau"]["dun"]}遁{item["bureau"]["ju"]}局；'+
            f'V8={item["score"]}（仅内部研发）',
            f'人物落宫：{item["patient"]["palace"]}；天芮病宫：{item["illness"]["palace"]}；'+
            f'人物取用来源状态：{item["source_confidence"]}',
            "",
            "### 原模板全文（未润色）",
            "",
            item["template_verbatim"],
            "",
            "### 人工润色保留栏",
            "",
            "尚未润色／尚未审定。不得把修辞改动误当作原规则修改。",
            "",
        ])
    return "\n".join(lines)+"\n"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",required=True)
    ap.add_argument("--markdown",required=True)
    args=ap.parse_args()
    batch=collect()
    jp=Path(args.json);mp=Path(args.markdown)
    jp.parent.mkdir(parents=True,exist_ok=True)
    mp.parent.mkdir(parents=True,exist_ok=True)
    jp.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    mp.write_text(compact_report(batch),encoding="utf8")
    print("WENGUA_TWELVE_PILLARS "+json.dumps({
        "count":len(batch["readings"]),
        "at6":batch["readings"][0]["pillars"],
        "at10":batch["readings"][6]["pillars"],
        "zone":ZONE},ensure_ascii=False))
    for r in batch["readings"]:
        last=next((s["text"] for s in r["sections"] if s["id"]=="90_review"),"")
        snippet={
            "hour":r["instant"][11:16],"label":r["label"],"score":r["score"],
            "raw":r["raw_before_saturation"],"patient_palace":r["patient"]["palace"],
            "illness_palace":r["illness"]["palace"],
            "person_strength":r["patient"]["source_strength"]["strength_label"],
            "illness_strength":r["illness"]["source_strength"]["strength_label"],
            "confidence":r["source_confidence"],
            "macro":next((s["text"] for s in r["sections"] if s["id"]=="01_macro"),"")[:240],
            "final":last[:1550],
            "selected_palaces":r["selected_palaces"],
            "verdict":r["verdict"]
        }
        print("WENGUA_TWELVE_CASE "+json.dumps(snippet,ensure_ascii=False,sort_keys=True))
    print("WENGUA_TWELVE_ALL_SOURCE_TEMPLATE_VERBATIM_FILE "+str(mp))


if __name__=="__main__":
    main()
