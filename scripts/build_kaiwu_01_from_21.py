"""Incremental Kaiwu Part 1 ingestion into the immutable 21-chapter Shenqi archive.

One canonical concept can have many independent book/edition tracks. Do not
overwrite older claims, infer missing Qimen charts, or turn cited Shenqi cases
into new Kaiwu event families. Source quotations remain in the versioned SQL.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "97e2285b25fd97f120ac1015104c6bf750fbba8c3c8bd0228be82b53563d4598"
BASE_SHA = "31707ea58f3854b948c58cee4dc3b0d3d3705ba36a2318812ba092b0ade016e8"
SECTION = "space_time_model_part01"
CHAPTER = "kaiwu/space_time_model_part01/v1"
BOOK = "kaiwu"
TRACK = "kaiwu:source_v1:shijia_zhuanpan"
STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STEM_WUXING = "木木火火土土金金水水"
BRANCH_WUXING = "水土木木土火火土金金土水"
BRANCH_PALACES = [1,8,8,3,4,4,9,2,2,7,6,6]
BRANCH_HOURS = [(23,1),(1,3),(3,5),(5,7),(7,9),(9,11),
                (11,13),(13,15),(15,17),(17,19),(19,21),(21,23)]
BRANCH_MONTH_TERMS = [
 ("子",11,("大雪","冬至")),("丑",12,("小寒","大寒")),
 ("寅",1,("立春","雨水")),("卯",2,("惊蛰","春分")),
 ("辰",3,("清明","谷雨")),("巳",4,("立夏","小满")),
 ("午",5,("芒种","夏至")),("未",6,("小暑","大暑")),
 ("申",7,("立秋","处暑")),("酉",8,("白露","秋分")),
 ("戌",9,("寒露","霜降")),("亥",10,("立冬","小雪"))
]
TERM_PALACES = {
 1:("冬至","小寒","大寒"),8:("立春","雨水","惊蛰"),
 3:("春分","清明","谷雨"),4:("立夏","小满","芒种"),
 9:("夏至","小暑","大暑"),2:("立秋","处暑","白露"),
 7:("秋分","寒露","霜降"),6:("立冬","小雪","大雪")}
PALACE_NUMBERS = {
 4:(3,4,5,8),9:(2,3,7,9),2:(2,5,8,10),
 3:(3,4,8),5:(5,10),7:(2,4,7,9),
 8:(5,7,8,10),1:(1,6),6:(1,4,6,9)}
PALACE_TRIGRAMS = {4:"巽",9:"离",2:"坤",3:"震",7:"兑",8:"艮",1:"坎",6:"乾"}
PALACE_ELEMENTS = {4:"木",9:"火",2:"土",3:"木",5:"土",7:"金",8:"土",1:"水",6:"金"}
PRIOR_NUMBERS = {"乾":1,"兑":2,"离":3,"震":4,"巽":5,"坎":6,"艮":7,"坤":8}
CITATIONS = [
 (90,"161","height_from_kang_numbers"),
 (92,"320","capital_eight_or_fourteen_hundred_million"),
 (147,"154~155","discharge_timing_empty_branches"),
 (149,"334","marriage_year_branch_palace"),
 (173,"152~154","father_health_retrospective"),
 (281,"185~187","license_letter_timing")
]

def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def lines_of(raw):
    if digest(raw)!=SOURCE_SHA: raise ValueError("Kaiwu original SHA256 mismatch")
    text=raw.decode("utf-8")
    lines=text.splitlines()
    if len(lines)!=281 or lines[0]!="奇门遁甲是中国人认知世界的一种时空模型":
        raise ValueError("Kaiwu source line structure changed")
    assert "第一节" in lines[4] and "第二节" in lines[32] and "第三节" in lines[93]
    return lines

def source_text(lines,a,b=None):
    b=a if b is None else b
    if not 1<=a<=b<=len(lines): raise ValueError("Source line outside uploaded chapter")
    return "\n".join(lines[a-1:b])

def extract(lines):
    """Machine-checkable source-grounded concept assertions; no prediction labels."""
    items=[]
    seen=set()
    def add(cid,kind,line,detail,*,relation="supplements",track=TRACK,end=None):
        end=line if end is None else end
        raw=source_text(lines,line,end)
        if not raw.strip(): raise ValueError(("Blank claim evidence",cid,line))
        identity=(cid,line)
        if identity in seen: raise ValueError(("Duplicated concept-source occurrence",identity))
        seen.add(identity)
        items.append(dict(concept_id=cid,kind=kind,source_start_line=line,
             source_end_line=end,source_excerpt_sha256=digest(raw.encode("utf-8")),
             track_id=track,relation_to_shenqi=relation,normalized=detail,
             review_status="draft",positive_training_eligible=False))
    add("model:taiji:parts","historical_model",23,
        {"author_account":"four cuts and nine segments","scientific_validation":"not_verified"},
        relation="additional_exposition",end=31)
    add("model:xiantian_vs_houtian","model_variant",57,
        {"former":"dynamic_yang","latter":"static_yin","not_equivalent_to_casting_method":True},
        relation="supplements")
    add("calendar:jieqi_first","casting_calendar_boundary",113,
        {"example":"2001-08-07T19:34","after":"丙申月","before":"乙未月",
         "timezone_and_astronomical_ephemeris":"not_specified_do_not_assume"},
        relation="clarifies")
    add("calendar:lichun_year","casting_calendar_boundary",263,
        {"year_boundary":"立春","month_boundary":"节","not":"lunar_first_day"},
        relation="clarifies")
    add("numerology:conditional_selection","interpretation_constraint",88,
        {"depends_on":["用神","旺相休囚","星","门","神","事物常理"],
         "numeric_scale_unknown_without_context":True},relation="extends")
    add("calendar:solar_term_application","interpretation_constraint",281,
        {"source_claim":"solar_terms_more_precise_than_lunar_month_dates",
         "external_validation":False,"is_author_historical_claim":True},relation="extends")

    # Extract the actual rows of the manuscript's figure 9, not a guessed nine-palace chart.
    for line in (84,85,86):
        row=source_text(lines,line)
        cells=[x.strip() for x in row.split("|")]
        if len(cells)!=3:raise ValueError(("Figure 9 broken",line))
        for cell in cells:
            number_list=tuple(int(v) for v in re.findall(r"\d+",cell))
            label=cell[0:2] if cell.startswith("中五") else cell[0]
            palace=5 if label=="中五" else next((p for p,t in PALACE_TRIGRAMS.items() if t==label),None)
            if palace is None or number_list!=PALACE_NUMBERS[palace]:
                raise ValueError(("Mismatch published palace numbers",line,cell))
            add("palace:"+str(palace)+":number_options","numerical_symbolism",line,
                {"palace":palace,"source_numbers":number_list,"conditional_not_fixed_prediction":True},
                relation="extends",track=TRACK+":number_selection")
    for p,t in PALACE_TRIGRAMS.items():
        add("trigram:"+t,"trigram_palace_mapping",51 if p in (4,9,2) else 52 if p in (3,7) else 53,
            {"trigram":t,"palace":p,"element":PALACE_ELEMENTS[p],
             "xiantian_number":PRIOR_NUMBERS[t]},relation="reaffirms")
        add("trigram:"+t,"xiantian_number",44,
            {"trigram":t,"xiantian_number":PRIOR_NUMBERS[t],"different_number_system":True},
            relation="clarifies",track=TRACK+":xiantian")
    add("palace:5:element","center_symbolism",63,
        {"palace":5,"element":"土","no_printed_center_deity_door_star":True},
        relation="reaffirms")
    for index,(b,pal) in enumerate(zip(BRANCHES,BRANCH_PALACES)):
        base=103 if index in (4,5,6,7,8) else 104 if index in (3,9) else 105
        add("branch:"+b,"branch_fixed_palace",base,
            {"branch":b,"palace":pal,"coordinate_kind":"fixed_palace_not_term_sector"},
            relation="reaffirms",track=TRACK+":branch_palace")
        add("branch:"+b,"branch_polarity_element",153,
            {"branch":b,"element":BRANCH_WUXING[index],
             "polarity":"yang" if index%2==0 else "yin"},
            relation="reaffirms")
        hh=BRANCH_HOURS[index]
        add("branch:"+b,"branch_double_hour",132+index,
            {"branch":b,"hour_start":hh[0],"hour_end":hh[1],
             "last_hour_rolls_over_midnight":b=="子"},
            relation="clarifies")
    for j,(b,month,terms) in enumerate(BRANCH_MONTH_TERMS):
        l=116+j
        if b not in lines[l-1]:raise ValueError(("Month label not in source",b,l))
        add("branch:"+b,"branch_month_and_terms",l,
            {"branch":b,"traditional_month":month,"solar_terms":terms,
             "boundary_policy":"starts_at_jie_not_lunar_new_moon"},
            relation="clarifies",track=TRACK+":branch_month")
    for i,stem in enumerate(STEMS):
        element=STEM_WUXING[i]
        add("stem:"+stem,"stem_polarity_element",238,
            {"stem":stem,"element":element,"polarity":"yang" if i%2==0 else "yin"},
            relation="reaffirms")
        add("stem:"+stem,"stem_direction_symbolism",185,
            {"stem":stem,"traditional_direction":{0:"东",1:"东",2:"南",3:"南",
             4:"中",5:"中",6:"西",7:"西",8:"北",9:"北"}[i],
             "not_a_claim_of_chart_center_deity_or_door":True},
            relation="clarifies",track=TRACK+":static_symbolic_direction")

    # Six original sixty-cycle xun tables. Their 10 stems + 2 void branches remain one sequence claim.
    for starter,ln,blank_ln in zip(["甲子","甲戌","甲申","甲午","甲辰","甲寅"],
                                    [199,205,211,217,223,229],[200,206,212,218,224,230]):
        full=source_text(lines,ln)
        blanks=source_text(lines,blank_ln)
        if starter not in full or "旬空" not in blanks:raise ValueError(("Xun source",starter,ln))
        tokens=re.findall(r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]",full)
        void=re.findall(r"[子丑寅卯辰巳午未申酉戌亥]",blanks)
        if len(tokens)!=10 or len(void)!=2:raise ValueError(("Xun cardinality",starter,ln))
        add("calendar:xun:"+starter,"sexagenary_xun",ln,
            {"ten_pairs":tokens,"two_void_branches":void,"void_source_line":blank_ln},
            relation="reaffirms",end=blank_ln)

    relations=[
       ("branch_clash",157,["子午","卯酉","丑未","寅申","辰戌","巳亥"]),
       ("branch_six_harmony",159,["子丑","寅亥","卯戌","辰酉","巳申","午未"]),
       ("branch_three_harmony",163,["申子辰","寅午戌","亥卯未","巳酉丑"]),
       ("branch_three_meeting",163,["寅卯辰","巳午未","申酉戌","亥子丑"]),
       ("branch_punishment",165,["子卯"]),
       ("branch_punishment",167,["寅巳申"]),
       ("branch_punishment",169,["丑戌未"]),
       ("branch_self_punishment",171,["辰辰","午午","酉酉","亥亥"]),
       ("branch_harm",175,["寅巳","卯辰","丑午","子未","亥申","戌酉"]),
       ("stem_combine",242,["甲己","乙庚","丙辛","丁壬","戊癸"]),
       ("stem_clash",244,["甲庚","乙辛","丙壬","丁癸"]),
    ]
    for kind,ln,groups in relations:
        for s in groups:
            if not all(x in source_text(lines,ln) for x in s):
                raise ValueError(("Missing relation characters",kind,s,ln))
            # Canonical identity follows the existing Shenqi symbols relation catalog where possible.
            canonical_members=s
            if kind=="stem_clash" and s in ("丙壬","丁癸"):
                canonical_members={"丙壬":"壬丙","丁癸":"癸丁"}[s]
            if kind=="branch_harm" and s in ("寅巳","卯辰","丑午","子未","亥申","戌酉"):
                canonical_members={"寅巳":"寅巳","卯辰":"卯辰","丑午":"丑午",
                 "子未":"子未","亥申":"申亥","戌酉":"酉戌"}[s]
            if kind=="branch_punishment" and s=="丑戌未":canonical_members="丑未戌"
            add(kind+":"+":".join(canonical_members),kind,ln,
               {"source_order":list(s),"canonical_order":list(canonical_members),
                "directional_sequence_must_be_preserved":kind=="branch_punishment",
                "lexical_shared_concept_not_automatically_equivalent_author_condition":True},
               relation="reaffirms",track=TRACK+":symbol_relations")

    term_dates={}
    for ln in range(268,280):
        for term,month,day in re.findall(r"([^；：\s]+)：(\d+)月(\d+)日",source_text(lines,ln)):
            term_dates[term]=(int(month),int(day),ln)
    if len(term_dates)!=24 or set(term_dates)!={v for vs in TERM_PALACES.values() for v in vs}:
        raise ValueError("Exactly 24 original solar-term dates required")
    for palace,terms in TERM_PALACES.items():
        for term in terms:
            mo,day,ln=term_dates[term]
            add("solar_term:"+term,"term_reference_date",ln,
               {"source_approximate_month_day":[mo,day],
                "not_exact_ephemeris_for_arbitrary_year":True},relation="supplements",
                track=TRACK+":approximate_calendar_dates")
            pl=257 if palace in (4,9,2) else 258 if palace in (3,7) else 259
            add("solar_term:"+term,"three_terms_per_palace",pl,
                {"seasonal_sector_palace":palace,
                 "separate_from_branch_fixed_palace":True,
                 "not_a_lunar_month_assignment":True},relation="extends",
                track=TRACK+":evenly_distributed_solar_sectors")

    for b,month,terms in BRANCH_MONTH_TERMS:
        # Distinct from the equal 3-term-per-palace solar sectors above.
        add("calendar:month_jie:"+b,"solar_calendar_month_boundary",263,
            {"branch":b,"month":month,"starts_on":terms[0],
             "second_term":terms[1],"not_on_lunar_day_one":True},relation="clarifies",
            track=TRACK+":jie_month_boundaries")
    return items

def figure_index(lines):
    indexed=[]
    for ln,line in enumerate(lines,1):
        m=re.match(r"^\[?图(\d+)\b",line.strip())
        if m: indexed.append({"figure":int(m.group(1)),"source_line":ln,
          "caption":line.strip(),"is_historical_qimen_cast":False})
    if sorted({e["figure"] for e in indexed})!=list(range(1,23)):
        raise ValueError("All 22 text diagrams/figures must be preserved")
    return indexed

def verify_old_rows(old,new):
    """Old columns and values must survive (new additive rows/tables permitted)."""
    for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
        names=",".join('"'+x+'"' for x in cols)
        previous=list(old.execute('SELECT '+names+' FROM "'+table+'"'))
        now=set(new.execute('SELECT '+names+' FROM "'+table+'"'))
        if not all(row in now for row in previous):
            raise ValueError("Prior chapter source rows changed: "+table)

def build(base,source,output,index_dir,migration):
    base,source,output,index_dir,migration=map(Path,(base,source,output,index_dir,migration))
    if output.exists():raise ValueError("Never overwrite a versioned database")
    if digest(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong 21-chapter base sha256")
    raw=source.read_bytes()
    lines=lines_of(raw)
    items=extract(lines)
    figures=figure_index(lines)
    out_ref=[]
    for ln,page,topic in CITATIONS:
        if "《神奇之门》" not in source_text(lines,ln) or page not in source_text(lines,ln):
            raise ValueError(("Cannot find source crossreference",ln,page))
        out_ref.append({"source_line":ln,"cited_book":"shenqi","cited_print_page":page,
             "reference_id":"kaiwu:ref:"+topic,"reference_role":"illustrates_previous_source_event",
             "new_event_family":False,"new_qimen_cast":False,
             "verified_original_event_match":False,"review_status":"draft"})
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(migration.read_text("utf-8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
                raise ValueError("Kaiwu first part already imported")
            db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
                          VALUES (?,?,?,?,?,1,0)""",
                       (BOOK,SECTION,lines[0],raw.decode("utf-8"),SOURCE_SHA))
            sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
                          source_length_bytes,knowledge_version,review_status)
                          VALUES (?,?,?,?,?,'1','draft')""",
                       (CHAPTER,BOOK,lines[0],SOURCE_SHA,len(raw)))
            for x in items:
                raw_part=source_text(lines,x["source_start_line"],x["source_end_line"])
                md={k:v for k,v in x.items() if k not in ("concept_id","kind","source_start_line","source_end_line")}
                db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
                  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
                  VALUES (?,?,?,?,?,?,?,?,'draft')""",
                  (CHAPTER,x["concept_id"],x["kind"],x["relation_to_shenqi"],
                   x["source_start_line"],x["source_end_line"],canonical(md),raw_part))
                db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,source_start_line,
                   source_end_line,source_section_id,source_sha256,excerpt_sha256,track_id,
                   relation_to_prior,comparison_state,normalized_json,review_status)
                   VALUES (?,?,?,?,?,?,?,?,?, 'candidate_not_human_verified',?,'draft')""",
                   (CHAPTER,x["concept_id"],x["source_start_line"],x["source_end_line"],sid,SOURCE_SHA,
                    x["source_excerpt_sha256"],x["track_id"],x["relation_to_shenqi"],canonical(x["normalized"])))
            for c in out_ref:
                db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,source_line,
                    target_book_id,target_printed_page,reference_key,metadata_json,verified_target_case_id)
                    VALUES (? ,? ,'shenqi',?,?,?,NULL)""",
                   (CHAPTER,c["source_line"],c["cited_print_page"],c["reference_id"],canonical(c)))
            db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
             contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
             VALUES (?, ?,NULL,1,'additive_multi_book_multi_track_source','2026-10-20',
             'user_authorized_public_full_sqlite_versions')""",
             ("shenqi_21_chapters_kaiwu_01_103_existing_cases",BASE_SHA))
        verify_old_rows(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Bad DB consistency")
        expected={"sections":22,"cases":103,"historical_case_reasoning":495,
                 "historical_palace_standardization":1008,
                 "semantic_assertions":1257+len(items),
                 "cross_book_concept_tracks":len(items),
                 "cross_book_example_references":len(out_ref)}
        actual={key:db.execute('SELECT COUNT(*) FROM "'+key+'"').fetchone()[0] for key in expected}
        if actual!=expected:raise ValueError(("Unexpected cumulative counts",actual,expected))
        if db.execute("SELECT COUNT(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]:
            raise ValueError("Unapproved source training!")
        if db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
            raise ValueError("Historical errors must not change")
        assert db.execute("SELECT COUNT(*) FROM cases WHERE case_id LIKE 'kaiwu.%'").fetchone()[0]==0
        db.execute("VACUUM")
        db.commit()
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Final snapshot corruption")
    index_dir.mkdir(parents=True,exist_ok=True)
    summary={"schema":"wengua_multibook_source_chapter_v1","source_book":"kaiwu","section_key":SECTION,
             "chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,"source_bytes":len(raw),
             "source_lines":len(lines),"source_title":lines[0],"section_headings":[
               {"line":i,"title":lines[i-1]} for i in (5,33,94)],
             "legacy_shenqi_chapters":21,"kaiwu_parts":1,"total_source_sections":22,
             "new_concept_occurrences":len(items),"new_cross_book_citations":len(out_ref),
             "source_figures":len(figures),"new_independent_event_families":0,
             "new_original_qimen_charts":0,"total_event_families":103,
             "cumulative_semantic_assertions":expected["semantic_assertions"],
             "cumulative_author_steps":495,"all_legacy_rows_preserved":True,
             "multi_track_behavior":"source_not_overwritten_duplicate_concept_keeps_versioned_occurrence",
             "author_reliability_not_scientifically_verified":True,"review_status":"draft",
             "positive_training_eligible":False,"baseline_sha256":BASE_SHA,
             "produced_db_sha256":digest(output.read_bytes()),"counts":actual}
    def save(name,obj):
        (index_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    save("chapter_manifest.json",summary)
    save("concept_tracks.json",{"schema":"wengua_multitrack_occurrence_index_v1",
        "chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,"entries":items})
    save("cross_book_links.json",{"schema":"wengua_cross_book_source_link_v1",
        "chapter_key":CHAPTER,"links":out_ref,
        "do_not_add_new_case_family_for_citations":True})
    save("figure_index.json",{"source_sha256":SOURCE_SHA,"figures":figures})
    save("source_audit.json",{"source_sha256":SOURCE_SHA,
        "separate_track_for_branch_fixed_palace_and_three_term_season_sector":True,
        "number_selection_is_conditional_not_one_fixed_value":True,
        "exact_solar_term_time_requires_ephemeris_not_book_approximation":True,
        "older_shenqi_case_references_are_not_new_predictions":True,
        "scientific_claims_in_source_are_book_author_claims_not_independent_proof":True,
        "complete_human_audited_causal_chains":0,"positive_training_eligible":False})
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base",required=True);p.add_argument("--source",required=True)
    p.add_argument("--output",required=True);p.add_argument("--index-dir",required=True)
    p.add_argument("--migration",default=str(ROOT/"schema/migrations/017_cross_book_multitrack.sql"))
    a=p.parse_args()
    print(json.dumps(build(a.base,a.source,a.output,a.index_dir,a.migration),
          ensure_ascii=False,indent=2))
if __name__=="__main__":main()
