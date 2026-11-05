"""Reviewed, private two-book course. No legacy score engine or teacher input."""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .qwen_book_dataset_v3 import SOURCE_SHA256, Groups as BaseGroups, BOOKS

SCHEMA = "wengua_reviewed_course_v4"
SYSTEM = ("直接回答问题。简题只答所问；案例先说结果，再说原因和证据，结论不重复。"
          "保留来源的适用条件与异说。区分初断、补充信息、事后反馈和作者改错；"
          "不补造出生年、宫位、应期或百分比。")
FORBIDDEN = ("HEALTH_V9_V11", "STRENGTH_200", "candidate_five_grade_quantization", "pre_relationship_bonus_score")

class Groups(BaseGroups):
    def union(self, a, b):
        return self.join([a,b])

def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf8")).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding="utf8"))

def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf8")

def compact(text):
    return re.sub(r"\s+", "", text)

def printed_board_key(cells):
    """Normalize written aliases only; never repair unknown or missing cells."""
    aliases={"值符":"符","螣蛇":"蛇","腾蛇":"蛇","太阴":"阴","六合":"合","白虎":"虎","玄武":"武","九地":"地","九天":"天"}
    aliases.update({"天"+x:x for x in "蓬芮冲辅禽心柱任英"})
    aliases.update({x+"门":x for x in "开休生伤杜景死惊"})
    def normal(value):
        value=compact(str(value))
        for a,b in aliases.items():value=value.replace(a,b)
        return value
    return tuple(sorted((int(c["palace"]),*(normal(c.get(k,"")) for k in ("deity_raw","door_position_raw","star_position_raw"))) for c in cells))


def validate_rows(rows, units):
    """Mechanical gates, not a claim of infallible semantic verification."""
    ids=set(); prompts={}; groups={}; owners={}
    for r in rows:
        if r["id"] in ids: raise ValueError("Duplicate row id")
        ids.add(r["id"])
        if r["split"] not in ("train", "validation", "test"): raise ValueError("Invalid split")
        if groups.setdefault(r["group"],r["split"])!=r["split"]: raise ValueError("Family split leakage")
        if not r["source_ids"] or any(x not in units for x in r["source_ids"]): raise ValueError("Missing source")
        for uid in r["source_ids"]:
            if units[uid]["book_id"] not in BOOKS: raise ValueError("Non-book source")
            if not all(k in units[uid] for k in ("id","chapter","lines","original_quote")):raise ValueError("Incomplete source rendering fields")
            if owners.setdefault(uid,r["split"])!=r["split"]: raise ValueError("Source split leakage")
        if not isinstance(r["answer"],str) or not r["answer"].strip(): raise ValueError("Empty answer")
        if any(x in r["answer"] for x in FORBIDDEN): raise ValueError("Legacy teacher marker")
        if r["messages"][-1]!={"role":"assistant","content":r["answer"]}: raise ValueError("Target mismatch")
        key=json.dumps(r["messages"][:-1],ensure_ascii=False,sort_keys=True)
        if key in prompts and prompts[key]!=r["answer"]: raise ValueError("Same prompt has conflicting targets")
        prompts[key]=r["answer"]
        if any(x in r["answer"] for x in ("以下是来源资料，尚非现实预测验证", "未提供程序排盘；只能讲来源规则")):
            raise ValueError("Retired boilerplate")
        sentences=[compact(x) for x in re.split("[。！？\n]",r["answer"]) if len(compact(x))>14]
        if len(sentences)!=len(set(sentences)): raise ValueError("Repeated answer sentence: "+r["id"])
    return {"rows":len(rows),"groups":len(groups),"formats":dict(Counter(r["format"] for r in rows)),
            "splits":dict(Counter(r["split"] for r in rows)),"conflicting_prompts":0,
            "family_and_source_leakage":0,"production_enabled":False}


def compile_course(review_dir, pack_path, database, output):
    """Compile explicit review decisions; rejected and unused material stays in audit."""
    review_dir=Path(review_dir); output=Path(output)
    if sha(Path(database).read_bytes())!=SOURCE_SHA256: raise ValueError("Source database hash changed")
    inv=load(review_dir/"general_inventory.json"); lookup={x["review_key"]:x for x in inv}
    pack=load(pack_path); dossiers=pack["dossiers"]
    notes=[json.loads(x) for x in (review_dir/"case_notes.jsonl").read_text(encoding="utf8").splitlines() if x.strip()]
    if len(dossiers)!=194 or sorted(x["n"] for x in notes)!=list(range(1,195)): raise ValueError("Incomplete 194-case review")
    manifests=[load(x) for x in sorted(review_dir.glob("review_G*.json"))]
    if sorted(n for m in manifests for n in range(m["range"][0],m["range"][1]+1))!=list(range(1,1452)):
        raise ValueError("General review coverage missing or overlapping")
    units={x["id"]:dict(x) for x in inv}; units.update(pack["units"])
    for d in dossiers:
        for step in d["author_steps"]:
            if step["source_id"] not in units: raise ValueError("Missing author original")
    sections={}
    with sqlite3.connect("file:"+str(Path(database).resolve())+"?mode=ro",uri=True) as db:
        db.row_factory=sqlite3.Row
        sections={int(x["section_id"]):dict(x) for x in db.execute("SELECT * FROM sections")}
    def raw_ref(section, lines):
        s=sections[int(section)]; quote="\n".join(s["original_text"].splitlines()[lines[0]-1:lines[1]])
        if not quote.strip(): raise ValueError("Empty raw coordinates")
        uid=f"review:{section}:L{lines[0]}-{lines[1]}:"+sha(quote)[:12]
        units[uid]={"id":uid,"book_id":s["book_id"],
                    "chapter":s["title"],"source_sha256":s["sha256"],"section_id":int(section),"lines":lines,"original_quote":quote,"match_status":"literal_line_slice"}
        return uid
    g=Groups(); rows=[]; seen={}; covered=set()
    def add(q,a,refs,*,fmt="foundation_qa",task="reviewed_rule",case_id=None,source_mode="book_knowledge",context="",group_keys=(),turns=None):
        q=q.strip();a=a.strip()
        if not a: raise ValueError("No manual answer: "+q)
        uids=[lookup[x]["id"] if x in lookup else x for x in refs]
        uids=list(dict.fromkeys(uids));covered.update(x for x in refs if x in lookup)
        for uid in uids:
            if uid not in units: raise ValueError("Unknown reference: "+uid)
        user=q+("\n"+context if context else "")
        messages=[{"role":"system","content":SYSTEM},{"role":"user","content":user}]
        if turns: messages+=turns
        messages.append({"role":"assistant","content":a})
        identity=json.dumps(messages[:-1],ensure_ascii=False,sort_keys=True)
        if identity in seen:
            old=seen[identity]
            if old["answer"]!=a: raise ValueError("Compile prompt collision: "+q)
            return
        rid="v4:"+sha(identity+a)[:20]
        r={"id":rid,"question":q,"answer":a,"messages":messages,"source_ids":uids,
           "case_id":case_id,"format":fmt,"task":task,"source_mode":source_mode,"_keys":["source:"+u for u in uids]+list(group_keys)}
        if case_id:r["_keys"].append("case:"+case_id)
        keys=r["_keys"]
        for key in keys:g.union(rid,key)
        rows.append(r);seen[identity]=r
    # Only explicitly written short answers are used here; full-quote drafting modes
    # must be resolved by a separate human-readable decision file before compilation.
    resolutions=load(review_dir/"short_answer_resolutions.json")
    for m in manifests:
        for item in m.get("items",[]):
            a=item.get("a") or resolutions.get(item["q"])
            if not a: raise ValueError("Unresolved long-answer review: "+item["q"])
            refs=item.get("refs",[])+item.get("extra_refs",[])+item.get("carry_refs",[])
            refs += [raw_ref(x["section"],x["lines"]) for x in item.get("source_refs",[])]
            add(item["q"],a,refs)
    # Literal short table rules retain their complete conditional text. Longer
    # paragraphs are retained in source_units and coverage, not silently chopped.
    for m in manifests:
        for group in m.get("typed_groups",[]):
            strategy=group["strategy"]
            if strategy not in ("ordered_door_pairs","ordered_door_stem_pairs","timing_success_condition_carried",
                                "timing_failure_condition_carried","guest_host_explicit_dimension","month_pair_terms_with_boundary","branch_double_hour"):
                continue
            for n in range(group["keys"][0],group["keys"][1]+1):
                if n==1260:continue
                key=f"G{n:04d}";u=lookup[key];c=u.get("concept","");quote=u["original_quote"].strip()
                book=BOOKS[u["book_id"]]
                if strategy.startswith("ordered_door"):
                    prefix="door_over_door:" if strategy=="ordered_door_pairs" else "door_over_stem:"
                    if not c.startswith(prefix):continue
                    a,b=c[len(prefix):].split(":")
                    add(f"{book}门的克应条目中，{a}门加{b}{'门' if prefix=='door_over_door:' else '干'}怎样说？",quote,[key])
                    if n==336:add(f"{book}门的克应条目中，休门加癸干怎样说？",quote,[key])
                elif strategy.startswith("timing_"):
                    cond="已综合判断事情可成" if "success" in strategy else "已综合判断事情不成"
                    q=f"{book}断应期：{cond}时，本条以什么条件取期？"
                    # Distinct rule subject is stated, so a generic repeated question never has competing targets.
                    add(q+"\n所问条目："+quote,quote,[key],fmt="conditional_dialogue",source_mode="literal_rule_reading",task="conditional_timing_reading")
                elif strategy=="guest_host_explicit_dimension":
                    add(f"{book}怎样按“{quote.split('，')[0].lstrip('①②③④⑤⑥⑦⑧⑨⑩')}”分主客？",quote,[key])
                elif strategy=="month_pair_terms_with_boundary":
                    add(f"{book}传统月序表中，{c.split(':')[-1]}月列哪两个节气？",quote+"。月份以交节划界，不按阴历初一划界。",[key,"G0745"])
                elif strategy=="branch_double_hour":
                    add(f"{book}时辰表中，{c.split(':')[-1]}时对应几点？",quote,[key])
    # Manually transcribed, book-version-specific ordered names. No inferred inverse name uniqueness.
    names=next(m["pair_names"] for m in manifests if "pair_names" in m)
    for key,value in names.items():
        if not value:continue
        c=lookup[key]["concept"].split(":");h,e=c[-2:]
        a="、".join(value)+"。"
        if key in ("G1140","G1142"):a+="后一个名称是本书作者建议的改名。"
        add(f"《开悟之门》中，天盘{h}加地盘{e}的格名是什么？",a,[key],task="ordered_pair_name")
    # Explicitly reviewed fixed tables. Questions distinguish palace numbers from Hetu/Xiantian numbers.
    tables=[t for m in manifests for t in m.get("reference_tables",[])]
    palaces=next(t["values"] for t in tables if t["type"]=="palace_trigram_element")
    for t in tables:
        for k,v in t.get("values",{}).items():
            typ=t["type"];q=a=None
            if typ=="palace_trigram_element":q=f"后天九宫中，{v[0]}{k}宫是什么方位、属什么五行？";a=f"{v[1]}，属{v[2]}。"
            elif typ=="xiantian_numbers":q=f"先天八卦数中，{k}是多少？";a=f"{v}。"
            elif typ=="hetu_numbers":q=f"河图五行数中，{k}对应哪两个数？";a="、".join(map(str,v))+"。"
            elif typ=="branch_palace":q=f"后天八卦地支配宫中，{k}支归哪宫？";a=f"{palaces[str(v)][0]}{v}宫。"
            elif typ=="branch_yinyang_element":q=f"地支{k}本身属什么阴阳五行？";a=f"{v}。"
            elif typ=="stem_yinyang_element_direction":q=f"天干{k}本身属什么阴阳五行、方位？";a=f"{v[0]}，{v[1]}。"
            elif typ=="three_terms_by_palace":q=f"本书节气配宫表中，{palaces[k][0]}{k}宫列哪三个节气？";a="、".join(v)+"。"
            if q:add(q,a,t["refs"],task="literal_reference_table")
    # Taught deterministic relationship arithmetic, no invented outcome score.
    for i,(t,_,e) in palaces.items():
        for j,(u,_,f) in palaces.items():
            if i==j:continue
            ge={"木":"火","火":"土","土":"金","金":"水","水":"木"};ke={"木":"土","土":"水","水":"火","火":"金","金":"木"}
            relation="比和" if e==f else ("生" if ge[e]==f else "克" if ke[e]==f else "受生于" if ge[f]==e else "受克于")
            add(f"只核对宫间五行方向：{t}{i}宫对{u}{j}宫是什么关系？",f"{t}{i}宫属{e}，{u}{j}宫属{f}，前者{relation}后者。",["G0713","G0719","G0777"],fmt="chart_application",task="directed_palace_relation")
    growth_sources=next(m["growth_sources"] for m in manifests if "growth_sources" in m)
    stages="长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养".split()
    branch_palace=next(t["values"] for t in tables if t["type"]=="branch_palace")
    for stem,(section,line) in growth_sources.items():
        ref=raw_ref(section,[line,line]);quote=units[ref]["original_quote"]
        if stem=="戊":quote=quote.split("即戊土也是",1)[1].split("阴土己土",1)[0]
        if stem=="己":quote=quote.split("即己土",1)[1]
        quote=quote[quote.index("长生在"):]
        values={}
        for stage in stages:
            match=re.search(re.escape(stage)+r"在([子丑寅卯辰巳午未申酉戌亥])",quote)
            if not match:raise ValueError("Missing literal growth cell: "+stem+stage)
            values[match[1]]=stage
        if len(values)!=12:raise ValueError("Growth table is not bijective")
        for branch,stage in values.items():
            add(f"按《开悟之门》十干十二长生表，{stem}到{branch}是什么状态？",stage+"。",[ref],task="literal_stem_growth")
        for palace in "12346789":
            branches=[b for b,n in branch_palace.items() if str(n)==palace]
            answer="、".join(f"{b}为{values[b]}" for b in branches)+"。"
            add(f"按十干十二长生表，{stem}落{palaces[palace][0]}{palace}宫，宫内各支分别是什么状态？",answer,[ref,"G0736"],fmt="chart_application",task="palace_stem_growth")
    # Reviewed multi-turn conditions, with prefix masking for every assistant turn.
    for item in load(review_dir/"dialogue_decisions.json"):
        turns=item["turns"]
        add(item["q"],item["a"],item["refs"],fmt="conditional_dialogue",task="condition_followup",
            turns=turns,source_mode="book_condition_application")
    # Case family links prevent shared letters, recasts and known cross-book retellings crossing splits.
    families=[[2,105],[7,122],[13,14],[30,31,32,145,146],[52,75],[57,134],[123,124],[142,143,176],
              [153,158,159],[172,173],[188,189],[192,193,194]]
    for nums in families:
        for n in nums[1:]:g.union("case:"+dossiers[nums[0]-1]["case_id"],"case:"+dossiers[n-1]["case_id"])
    boards={}
    coordinates=load(Path(__file__).resolve().parents[2]/"data/knowledge/qwen_book_only_v3/case_source_coordinates_20261104.json")
    for d,note in zip(dossiers,notes):
        if d["case_id"]!=dossiers[note["n"]-1]["case_id"]:raise ValueError("Case note ordering changed")
        cid=d["case_id"];g.union("case:"+cid,"event:"+d["original_event_family"]);steps=d["author_steps"];refs=list(dict.fromkeys(s["source_id"] for s in steps))
        # Include whole case coordinates so feedback and teacher corrections have literal evidence too.
        for section,entries in coordinates.items():
            for entry in entries:
                if entry["case_id"]==cid:refs.append(raw_ref(section,entry["lines"]))
        refs=list(dict.fromkeys(refs))
        # Some final-source cases have no indexed reasoning; recover their literal coordinates.
        if not refs:
            phase=d["source_phase_events"]
            source=[u["id"] for u in units.values() if cid in u.get("case_ids",[])]
            refs=source[:1]
        if not refs: raise ValueError("Case without located evidence: "+cid)
        literal_board="\n".join(f"{c['palace_label_raw']}：神{c['deity_raw']}，门行{c['door_position_raw']}，星行{c['star_position_raw']}" for c in d["primary_printed_chart"])
        context="案例编号："+cid+"。\n背景及信息披露："+note["context"]
        if literal_board:context+="\n原书主盘抄录：\n"+literal_board
        else:context+="\n本案例没有完整主盘抄录，不补造宫位。"
        excerpt="\n".join(s["original"] for s in steps)
        # These are source-assisted review exercises, explicitly not independent unseen-board prediction.
        evidence_context=context+"\n作者原分析摘录：\n"+(excerpt if len(excerpt)<=1800 else excerpt[:0])
        if len(excerpt)>1800:evidence_context=context+"\n任务是复盘原书案；完整原文见本案例来源索引。"
        result=note["result"]+"\n原因与证据："+note["reason"]
        add("复盘这个原书案例：作者的主要判断是什么，依据是什么？",result,refs,fmt="complete_case",task="author_analysis_review",case_id=cid,context=evidence_context,source_mode="retrospective_source_review")
        add("核对这个原书案例的应期和反馈：哪些已反馈，哪些不能算事前命中？",note["timing_and_feedback"],refs,fmt="conditional_dialogue",task="chronology_review",case_id=cid,context=context,source_mode="retrospective_source_review")
        add("复盘这个原书案例时，最需要避免哪项误读？",note["review_note"],refs,fmt="conditional_dialogue",task="case_error_correction",case_id=cid,context=context,source_mode="retrospective_source_review")
        for cast,cells in [("primary",d["primary_printed_chart"]),*d["additional_printed_charts"].items()]:
            if not cells:continue
            fingerprint=printed_board_key(cells)
            if fingerprint in boards:g.union("case:"+cid,"case:"+boards[fingerprint])
            boards[fingerprint]=cid
            printed="\n".join(f"{c['palace_label_raw']}：神{c['deity_raw']}，门行{c['door_position_raw']}，星行{c['star_position_raw']}" for c in cells)
            for c in cells:
                raw=c.get("star_position_raw","")
                matches=[x for x in "蓬芮冲辅禽心柱任英" if x in raw]
                if len(matches)!=1:continue
                star=matches[0]
                if sum(star in v.get("star_position_raw","") for v in cells)!=1:continue
                add(f"读取这份原书抄盘：星行中的“{star}”落在哪一宫？",f"{c['palace_label_raw']}。",refs,fmt="chart_application",task="printed_star_location",case_id=cid,context=f"案例{cid}，盘次{cast}；仅按所列字面读取，不修补原盘。\n"+printed,source_mode="literal_printed_chart")
    # Link general paragraphs about specific cases, not every universal rule used in a case.
    numbered={733:7,734:92,773:3,1065:3,774:98,867:98,786:2,1074:2,1066:23,842:23,1075:85,1085:53,1086:59,1087:63,1249:122,1250:162,1253:6,1254:74,1269:176,1270:77}
    for n in [*range(1020,1026),*range(1033,1040),1045,1049]:numbered[n]=30
    for n in [1046,1050,1083,1084]:numbered[n]=70
    for n in range(1442,1451):numbered[n]=143
    for n,c in numbered.items():g.union("source:"+lookup[f"G{n:04d}"]["id"],"case:"+dossiers[c-1]["case_id"])
    spans=defaultdict(list)
    for section,entries in coordinates.items():
        for entry in entries:spans[int(section)].append(entry)
    for uid,u in units.items():
        if u.get("section_id") is None or not u.get("lines"):continue
        lo,hi=u["lines"]
        for entry in spans.get(int(u["section_id"]),[]):
            a,b=entry["lines"]
            if max(a,lo)<=min(b,hi):g.union("source:"+uid,"case:"+entry["case_id"])
    # Exact answer variants of the same question family cannot cross folds either.
    for r in rows:
        for uid in r["source_ids"]:
            g.union(r["id"],"source:"+uid)
    for r in rows:
        root=g.root(r["id"]);r["group"]="family:"+sha(root)[:16]
        bucket=int(sha("v4-fold:"+root)[:8],16)%100
        r["split"]="test" if bucket<10 else "validation" if bucket<22 else "train"
        del r["_keys"]
    source_checks=Counter()
    for uid,u in units.items():
        status=u.get("match_status")
        if status in ("literal","whitespace_only","literal_line_slice"):
            section=sections[int(u["section_id"])]
            if compact(u["original_quote"]) not in compact(section["original_text"]):
                raise ValueError("Source quote not found in immutable book: "+uid)
            if u["book_id"]!=section["book_id"]:raise ValueError("Wrong source book")
            source_checks["located_quote"]+=1
        else:source_checks["separately_labelled_sqlite_transcription"]+=1
    output.mkdir(parents=True,exist_ok=True)
    proof=validate_rows(rows,units)
    proof.update(schema=SCHEMA,source_sha256=SOURCE_SHA256,general_entries_reviewed=len(inv),cases_reviewed=len(notes),
                 author_steps_preserved=sum(len(d["author_steps"]) for d in dossiers),
                 review_policy="manual source reading and written decisions; fallibility retained",source_checks=dict(source_checks),
                 general_entries_used=len(covered),raw_general_entries_retained=len(inv),
                 unseen_full_case_prediction_verified=False,
                 case_supervision="retrospective review, chronological correction and literal chart reading")
    dump(output/"pack.json",{"source_sha256":SOURCE_SHA256,"records":rows,"units":units,"dossiers":dossiers,"review_notes":notes,"summary":proof})
    dump(output/"summary.json",proof)
    dump(output/"coverage.json",[{"key":x["review_key"],"used_in_general_sft":x["review_key"] in covered,
         "policy":"reviewed short target" if x["review_key"] in covered else "source retained; no approved short target in this release"} for x in inv])
    return proof
