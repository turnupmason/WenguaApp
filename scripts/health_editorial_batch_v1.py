"""Prepare immutable health V8 facts and OpenAI Batch API editorial requests.

NO model calls occur here; no grading, chapter sources or Swift are changed.
First 1080 layouts are ONLY topological index, not 1080 complete forecasts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from src.wengua.casting_shenqi import cycle60,layout_from_explicit_bureau
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ROOT=Path(__file__).resolve().parents[1]
PROMPT=ROOT/"prompts/health_severity_gpt_editorial_v1_20261029.md"
ZONE="America/New_York"
CLOCKS=("2026-10-28T06:00:00-04:00","2026-10-28T10:00:00-04:00")
ACTORS=(("father","父亲"),("mother","母亲"),("grandfather","爷爷"),
        ("grandmother","奶奶"),("older_sibling","姐姐"),("younger_sibling","弟弟"))
GRADE={-5:"极大凶",-4:"大凶",-3:"中凶",-2:"小凶",-1:"极小凶",
        0:"不凶不吉",1:"极小吉",2:"小吉",3:"中吉",4:"大吉",5:"极大吉"}
SCHEMA="wengua_health_editorial_casefacts_v1"
STATUS="queued_needs_gpt_and_manual_review"


def canonical(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def digest(data):
    return hashlib.sha256(canonical(data).encode("utf8")).hexdigest()

def write_jsonl(path,rows):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf8") as out:
        for r in rows:
            out.write(canonical(r)+"\n")
    return len(rows)

def read_jsonl(path):
    with Path(path).open(encoding="utf8") as f:
        return [json.loads(line) for line in f if line.strip()]


def topology1080():
    """A base casting catalog. Real month/year/day/context still required."""
    states=[]
    for dun in ("yang","yin"):
        for ju in range(1,10):
            for hour in cycle60():
                chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                palace=chart["palaces"]
                assert palace["5"]["heaven_stars"]==[] and palace["5"]["door"] is None
                state={
                    "base_id":f"{dun}-{ju:02d}-{hour}",
                    "dun":dun,"ju":ju,"hour_ganzhi":hour,
                    "real_nine_palaces_fingerprint":digest(palace),
                    "value_star":chart["value_star"],
                    "value_door":chart["value_door"],
                    "xun_shou":chart["xun_shou"],
                    "complete_severity_reading":False,
                    "not_supplied":["actual_year","actual_month","actual_day",
                                    "solar_term","month_season_strength",
                                    "relationship","patient_natal","source_rule_conditions"],
                    "not_a_medical_case":True,
                }
                states.append(state)
    assert len(states)==1080
    assert len({s["base_id"] for s in states})==1080
    return states


def first_complete_batch():
    """Twelve user-requested true clock/person cases; no artificial pillars."""
    rows=[]
    psha=hashlib.sha256(PROMPT.read_bytes()).hexdigest()
    for iso in CLOCKS:
        for relation,label in ACTORS:
            result=auto_cast_health_review_text(
                iso=iso,timezone_name=ZONE,
                inquiry={"intent":"severity","relationship":relation,
                         "consultation_context":"direct_proxy"})
            net=result["full_health_role_strength_network"]
            quant=net["candidate_five_grade_quantization"]
            summary=quant["summary"]
            score=summary["score"]
            if score not in GRADE:
                raise ValueError("No sealed resolved grade, do not forge a reading")
            nine=result["nine_palaces"]
            assert len(nine)==9
            assert not nine["5"]["heaven_stars"] and nine["5"]["door"] is None
            sections=result["sections"]
            assert sections and sections[-1]["id"]=="91_timing"
            # Text construction happens later. No unreviewed prose is published.
            facts={
                "instant":iso,"timezone":ZONE,"topic_id":"health.severity",
                "relationship_id":relation,"relationship_label":label,
                "source_confidence":result["audit"]["role_confidence"],
                "four_pillars":result["four_pillars"],"solar_term":result["solar_term"],
                "bureau":result["bureau"],"nine_palaces":nine,
                "selected_palaces":result["scored_relevant_palaces"],
                "nine_palace_condition_facts":result["nine_palace_condition_facts"],
                "first_stage_macro":result["first_stage_macro"],
                "role_nodes":net["nodes"],
                "directed_edges":net["directed_edges"],
                "role_effectiveness_gates":quant["role_effectiveness_gates"],
                "evidence_counts":result["evidence_counts"],
                "no_supplied_birth_ganzhi":True,
            }
            root_id=digest({"case_facts":facts,"source_sections":sections,
                            "freeze_score":score,"source_template":"V10.2"})
            row={
                "schema":SCHEMA,"case_id":"health-severity-"+root_id[:24],
                "case_fingerprint":root_id,
                "prompt_path":PROMPT.relative_to(ROOT).as_posix(),
                "prompt_sha256":psha,
                "status":STATUS,
                "freeze":{"engine":"V8.0","customer_copy":"V10.2",
                          "score":score,"grade":GRADE[score],
                          "final_grade_immutable":True},
                "case_facts":facts,
                "source_sections":sections,
                "evidence_ids":["section:"+s["id"] for s in sections],
                "approved_for_app":False,
                "not_a_hidden_blind_test":True,
                "not_a_clinical_diagnosis":True,
            }
            rows.append(row)
    assert len(rows)==12
    assert len({x["case_id"] for x in rows})==12
    return rows


def result_schema():
    """Supported structured outputs, then explicit source-fact validation."""
    text={"type":"string"}
    issue={
      "type":"object","additionalProperties":False,
      "properties":{k:text for k in ("claim","case_evidence_id","source_reference",
                    "expected","actual","suggested_test","priority")},
      "required":["claim","case_evidence_id","source_reference","expected","actual",
                  "suggested_test","priority"]
    }
    section={
      "type":"object","additionalProperties":False,
      "properties":{"id":text,"title":text,"text":text,
                    "evidence_ids":{"type":"array","items":text}},
      "required":["id","title","text","evidence_ids"]
    }
    return {
      "type":"object","additionalProperties":False,
      "properties":{
        "case_id":text,"case_fingerprint":text,"grade_anchor":text,
        "summary":text,
        "detailed_sections":{"type":"array","items":section},
        "audit_flags":{"type":"array","items":issue},
      },
      "required":["case_id","case_fingerprint","grade_anchor","summary",
                  "detailed_sections","audit_flags"]
    }


def requests_for_batch(cases,model):
    if not model or not model.strip() or any(x in model.lower() for x in ("example","replace","placeholder")):
        raise ValueError("A REAL confirmed API model ID must be supplied for request generation")
    p=PROMPT.read_text(encoding="utf8")
    entries=[]
    for row in cases:
        if row["schema"]!=SCHEMA or row["status"]!=STATUS:
            raise ValueError("Only unapproved immutable case facts are eligible")
        if row["prompt_sha256"]!=hashlib.sha256(PROMPT.read_bytes()).hexdigest():
            raise ValueError("Prompt version drift: re-prepare the source facts")
        body={
            "model":model,
            "instructions":p,
            "input":("仅根据如下不可变JSON事实，输出专业润色和独立审计的严格JSON对象：\n"
                     +canonical({k:v for k,v in row.items() if k!="schema"})),
            "text":{"format":{"type":"json_schema",
                              "name":"wengua_health_editorial_v1",
                              "strict":True,"schema":result_schema()}}
        }
        entries.append({"custom_id":row["case_id"],
                        "method":"POST","url":"/v1/responses","body":body})
    if len({e["custom_id"] for e in entries})!=len(entries):
        raise ValueError("Duplicate batch custom_id")
    return entries


def validate_candidate(source,answer):
    """Programmatic coarse guard; NOT a substitute for semantic human review."""
    if not isinstance(answer,dict):raise ValueError("Expected JSON object")
    for k,expected in (("case_id",source["case_id"]),
                       ("case_fingerprint",source["case_fingerprint"]),
                       ("grade_anchor",source["freeze"]["grade"])):
        if answer.get(k)!=expected:raise ValueError("Source identity or grade drift: "+k)
    summary=answer.get("summary","")
    if not isinstance(summary,str) or not 160<=len(summary)<=280:
        raise ValueError("First page must contain approximately 200 Chinese characters")
    bad_summary=("极大凶","大凶","中凶","极小凶","极大吉","-5分",
                 "无法给出","无法判断","尚不足以下结论","尚未定局","结果待定",
                 "GPT","模型","规则库","矩阵","数据库","死亡","保证痊愈")
    if any(w in summary for w in bad_summary):
        raise ValueError("Public summary leaked internal grade or unverified prognosis")
    source_sections=source["source_sections"]
    details=answer.get("detailed_sections")
    if not isinstance(details,list) or len(details)!=len(source_sections):
        raise ValueError("Any missing long-form section is a rejection")
    for expected,given in zip(source_sections,details):
        if given.get("id")!=expected["id"] or given.get("title")!=expected["title"]:
            raise ValueError("Cannot remove, reorder or relabel frozen source sections")
        if not isinstance(given.get("text"),str) or len(given["text"].strip())<15:
            raise ValueError("Detailed evidence cannot become an empty summary")
        if ("section:"+expected["id"]) not in given.get("evidence_ids",[]):
            raise ValueError("Section missing source trace")
        if any(a not in source["evidence_ids"] for a in given.get("evidence_ids",[])):
            raise ValueError("Fabricated source section reference")
    if not isinstance(answer.get("audit_flags"),list):
        raise ValueError("Audit issues must remain an explicit list")
    return {
        "case_id":source["case_id"],
        "case_fingerprint":source["case_fingerprint"],
        "grade_anchor":source["freeze"]["grade"],
        "summary":summary,
        "detailed_sections":details,
        "audit_flags":answer["audit_flags"],
        "status":"draft_needs_source_semantic_and_human_review",
        "approved_for_app":False,
        "prompt_sha256":source["prompt_sha256"],
        "human_approval":None,
    }


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--mode",choices=("topology1080","seed12","requests","validate"),required=True)
    cli.add_argument("--output",required=True)
    cli.add_argument("--input")
    cli.add_argument("--candidate")
    cli.add_argument("--model")
    opt=cli.parse_args()
    if opt.mode=="topology1080":rows=topology1080()
    elif opt.mode=="seed12":rows=first_complete_batch()
    elif opt.mode=="requests":
        if not opt.input:raise ValueError("--input needed")
        rows=requests_for_batch(read_jsonl(opt.input),opt.model)
    else:
        if not opt.input or not opt.candidate:raise ValueError("--input and --candidate needed")
        sources=read_jsonl(opt.input)
        answer=json.loads(Path(opt.candidate).read_text(encoding="utf8"))
        matches=[x for x in sources if x["case_id"]==answer.get("case_id")]
        if len(matches)!=1:raise ValueError("No unique source matching this candidate")
        rows=[validate_candidate(matches[0],answer)]
    n=write_jsonl(opt.output,rows)
    print("HEALTH_EDITORIAL_STAGE",opt.mode,"CASES",n,
          "NO_GPT_API_CALLED","NO_V8_CHANGES","NO_PUBLIC_RELEASE")
    if opt.mode=="seed12":
        print("HEALTH_SOURCE_GRADES",json.dumps([
            {"hour":x["case_facts"]["instant"][11:16],
             "who":x["case_facts"]["relationship_label"],
             "grade":x["freeze"]["grade"],
             "status":x["status"]} for x in rows],ensure_ascii=False))

if __name__=="__main__":
    main()
