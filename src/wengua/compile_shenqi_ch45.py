"""Compile exact user-supplied Shenqi Ch4/Ch5 into a PRIVATE local semantic SQLite.

Complete 9x9 stem pairs, 8x8 door pairs, 8x9 door/instrument pairs, 13
auspicious and 27 inauspicious top-level formations. Original commentary
is stored locally; GitHub publishes only compiler/schema/public metadata.
All claims are source transcriptions with draft status, NOT approved readings.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from .database import initialize, connect, import_section

SOURCE_SHA256 = "8b8d7f57fa539785f5613cb6f8fdbdc27090da559d6d2fe5ce0ffd03953c9147"
STEMS = "乙丙丁戊己庚辛壬癸"
DOORS = "开休生伤杜景死惊"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STARS = ("天蓬星","天芮星","天冲星","天辅星","天禽星","天心星","天柱星","天任星","天英星")
DEITIES = ("值符","螣蛇","太阴","六合","白虎","玄武","九地","九天")
TRIGRAMS = (("乾",25,48,6,"金","西北"),("坤",49,70,2,"土","西南"),
            ("震",71,94,3,"木","东"),("巽",95,118,4,"木","东南"),
            ("坎",119,142,1,"水","北"),("离",143,166,9,"火","南"),
            ("艮",167,190,8,"土","东北"),("兑",191,214,7,"金","西"))
DOOR_ELEMENT = dict(zip(DOORS,"金水土木木火土金"))
STAR_ELEMENT = dict(zip(STARS,("水","土","木","木","土","金","金","土","火")))
STEM_ELEMENT = dict(zip("甲乙丙丁戊己庚辛壬癸","木木火火土土金金水水"))
BRANCH_ELEMENT = dict(zip(BRANCHES,"水土木木土火火土金金土水"))
CHAPTERS = (("shijia_symbols_ch04","奇门预测符号的象数理含义",1,500),
            ("shijia_judgments_ch05","奇门预测的判断依据",501,1261))

def concept_pair(kind,left,right):
    """Cross-book reusable stable concept ID; sources remain separate records."""
    return f"{kind}:{left}:{right}"

def parse_original(text):
    lines=text.splitlines()
    if (len(lines)!=1261 or lines[0].strip()!="奇门预测符号的象数理含义"
            or lines[500].strip()!="第五章 奇门预测的判断依据"):
        raise ValueError("Unexpected edition/chapter boundary; refuse approximate extraction")
    entries=[]
    def put(kind,key,start,end,relation,body,condition=None,qualifier="source_transcribed_draft"):
        if not 1<=start<=end<=len(lines): raise ValueError("Incorrect source lines")
        entries.append({"kind":kind,"concept_id":key,"chapter":4 if start<=500 else 5,
                        "start":start,"end":end,"relation":relation,"source_text":body,
                        "predicate":condition,"qualifier":qualifier})
    # Trigram and their fine-grained aspects: original stays PRIVATE in local database.
    for name,start,end,palace,element,direction in TRIGRAMS:
        put("symbol",f"trigram:{name}",start,end,"trigram_profile",
            f"{name}:宫{palace};五行{element};后天方位{direction}",
            {"palace":palace,"element":element,"direction":direction})
        for i in range(start+1,end+1):
            line=lines[i-1].strip()
            if not line or line.startswith(("（","(")):continue
            aspect=next((a for a in ("天象","天时","在国家","在单位","在家庭","在社会",
                  "在场所","在方位","在方向","在时间","在数字","在动物","在静物",
                  "静物","在人体","人体","在颜色","颜色","在五味","五味")
                  if a in line),"general")
            put("symbol_aspect",f"trigram:{name}",i,i,aspect,line)
    for i in range(223,242,2):
        line=lines[i-1].strip();stem=line.split("：",1)[0]
        if len(stem)!=1 or stem not in STEM_ELEMENT:raise ValueError("Ten-stem profile incomplete")
        put("symbol",f"stem:{stem}",i,i,"stem_profile",line,
            {"element":STEM_ELEMENT[stem]})
    for i in range(287,310,2):
        line=lines[i-1].strip();branch=line.split("：",1)[0]
        if len(branch)!=1 or branch not in BRANCHES:raise ValueError("Twelve-branch profile incomplete")
        put("symbol",f"branch:{branch}",i,i,"branch_profile",line,
            {"element":BRANCH_ELEMENT[branch]})
    for i,door in zip((351,357,363,369,375,381,387,393),DOORS):
        end={351:356,357:362,363:368,369:374,375:380,381:386,387:392,393:398}[i]
        put("symbol",f"door:{door}",i,end,"door_profile",
            " ".join(x.strip() for x in lines[i-1:end] if x.strip()),
            {"element":DOOR_ELEMENT[door]})
    for i,star in zip((413,417,421,425,429,433,437,441,445),STARS):
        end={413:416,417:420,421:424,425:428,429:432,433:436,437:440,441:444,445:448}[i]
        put("symbol",f"star:{star}",i,end,"star_profile",
            " ".join(x.strip() for x in lines[i-1:end] if x.strip()),
            {"element":STAR_ELEMENT[star]})
    for i,deity in zip((483,485,487,489,491,493,495,497),DEITIES):
        put("symbol",f"deity:{deity}",i,i,"deity_profile",lines[i-1].strip())

    # Full 81-cell 天干(天盘) × 地干(地盘) ordered matrix.
    seen=set()
    for i in range(507,686):
        s=lines[i-1].strip()
        m=re.search(r"即\s*([乙丙丁戊己庚辛壬癸])加([乙丙丁戊己庚辛壬癸])",s)
        if not m:continue
        a,b=m.groups();key=concept_pair("heaven_over_earth",a,b)
        if key in seen:raise ValueError("Duplicate ordered stem combination")
        seen.add(key)
        put("stem_pair",key,i,i,"heaven_stem_over_earth_stem",s,
            {"heaven_stem":a,"earth_stem":b})
    if seen!={concept_pair("heaven_over_earth",a,b) for a in STEMS for b in STEMS}:
        raise ValueError("9x9 stem-pair table incomplete")
    door_pairs=set();door_stems=set()
    for i in range(691,976):
        s=lines[i-1].strip()
        m=re.match(r"(["+DOORS+r"])加(["+DOORS+r"乙丙丁戊己庚辛壬癸、]+)：",s)
        if not m:continue
        a,b=m.groups()
        if b in DOORS:
            key=concept_pair("door_over_door",a,b)
            if key in door_pairs:raise ValueError("Duplicate door pair")
            door_pairs.add(key)
            put("door_pair",key,i,i,"door_over_door_needs_layer_binding",s,
                {"upper_door":a,"lower_door":b,"layer_binding":"unresolved"})
        else:
            # User's text puts 休门+壬、癸 on one line; index each separately.
            for stem in b.replace("、",""):
                if stem not in STEMS:raise ValueError("Unexpected door+instrument")
                key=concept_pair("door_over_stem",a,stem)
                if key in door_stems:raise ValueError("Duplicate door-instrument")
                door_stems.add(key)
                put("door_stem",key,i,i,"door_over_instrument_needs_layer_binding",s,
                    {"door":a,"instrument":stem,"layer_binding":"unresolved"})
    if door_pairs!={concept_pair("door_over_door",a,b) for a in DOORS for b in DOORS}:
        raise ValueError(f"8x8 door table incomplete: {len(door_pairs)}")
    if door_stems!={concept_pair("door_over_stem",a,b) for a in DOORS for b in STEMS}:
        raise ValueError(f"8x9 door-instrument table incomplete: {len(door_stems)}")
    # Umbrella headings can have multiple OR alternatives: never auto-match
    # from heading alone (e.g. 九遁, 三诈五假, 三奇得使).
    for kind,start,end,total in (("good_formation",987,1088,13),
                                 ("bad_formation",1093,1261,27)):
        headings=[]
        for i in range(start,end+1):
            m=re.match(r"（(\d+)）\s*(.+?)[。.]?$",lines[i-1].strip())
            if m:headings.append((int(m.group(1)),i,m.group(2).strip()))
        if [x[0] for x in headings]!=list(range(1,total+1)):
            raise ValueError(f"Incomplete formation headings: {kind}")
        for n,(index,i,title) in enumerate(headings):
            finish=headings[n+1][1]-1 if n+1<len(headings) else end
            put(kind,f"formation:{kind}:{index:02d}",i,finish,
                "formation_heading_with_conditional_alternatives",
                " ".join(s.strip() for s in lines[i-1:finish] if s.strip()),
                {"title":title,"auto_matched":False})
    # Preserve author-specific distinctions and unverified opinions.
    notes=[
        ("door_palace_elements",399,402),("star_month_formula",451,477),
        ("celestial_eight_deities_only",479,499),
        ("three_wonders_getting_value_door_author_hypothesis",1017,1025),
        ("heaven_net_only_gui_plus_gui_author_opinion",1239,1253),
        ("five_no_encounter_has_case_caveat",1255,1261),
        ("9720_8640_vs_1080_different_count_basis",977,983),
        ("five_yang_five_yin_hour_convention",243,250),
        ("stem_clash_combination_and_growth",251,265),
        ("branch_punish_clash_harm_combination",311,327),
        ("travel_chant_is_not_sufficient",267,283),
        ("tianrui_health_yongshen_candidate",417,419)]
    for name,start,end in notes:
        put("method_guard",f"principle:{name}",start,end,name,
            " ".join(s.strip() for s in lines[start-1:end] if s.strip()),None,
            "author_hypothesis_draft" if "hypothesis" in name or "author_opinion" in name
            else "source_transcribed_draft")
    return entries

def ingest_local(db_path,source_file):
    p=Path(source_file)
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError("Wrong chapter 4+5 source hash: never import another edition silently")
    text=raw.decode("utf-8")
    entries=parse_original(text)   # validate COMPLETE coverage before any db mutation
    lines=text.splitlines(keepends=True)
    initialize(db_path)
    for slug,title,start,end in CHAPTERS:
        chunk="".join(lines[start-1:end])
        import_section(db_path,"shenqi",slug,title,chunk)
    with connect(db_path) as db:
        for slug,title,start,end in CHAPTERS:
            chunk="".join(lines[start-1:end])
            digest=hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            key=f"shenqi/{slug}/v1"
            old=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(key,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO chapter_knowledge
                    (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
                    VALUES (?,?,?,?,?,'1','draft')""",
                    (key,"shenqi",title,digest,len(chunk.encode("utf-8"))))
            elif old[0]!=digest:
                raise ValueError("Existing chapter source differs: versioned update required")
        for item in entries:
            slug=CHAPTERS[0][0] if item["chapter"]==4 else CHAPTERS[1][0]
            key=f"shenqi/{slug}/v1"
            start=item["start"]-(500 if item["chapter"]==5 else 0)
            end=item["end"]-(500 if item["chapter"]==5 else 0)
            meta=json.dumps({k:item[k] for k in ("kind","relation","predicate","qualifier","start","end")},
                           sort_keys=True,ensure_ascii=False)
            existing=db.execute("""SELECT metadata_json,original_excerpt FROM semantic_assertions
                WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",
                (key,item["concept_id"],start)).fetchone()
            wanted=(meta,item["source_text"])
            if existing is not None:
                if tuple(existing)!=wanted:
                    raise ValueError("Prior source assertion differs; no overwrite allowed")
                continue
            db.execute("""INSERT INTO semantic_assertions
                (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                 metadata_json,original_excerpt,review_status)
                VALUES (?,?,?,?,?,?,?,?,'draft')""",
                (key,item["concept_id"],item["kind"],item["relation"],start,end,*wanted))
    return {"source_sha256":SOURCE_SHA256,"chapters":2,"total_entries":len(entries),
            "by_kind":dict(sorted(Counter(x["kind"] for x in entries).items())),
            "approved":0,"historical_prediction_cases":0,
            "status":"source_transcribed_local_only_awaiting_professional_review"}
