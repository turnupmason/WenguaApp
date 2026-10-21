"""Add draft marriage phrase library to the exact full 194-case two-book SQLite.

Does NOT generate 388800 unverified charts or preapprove readings. Conditional
drafts are GPT-polished natural Chinese, grounded by source sha/lines and tied
to book case events. The app's real cast verification remains separate.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from src.wengua.phrase_pipeline import matrix_cardinality,state_key
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="c57153c296b1369e2b9bd78039dbe0cc191d67721f5042828e5ef54e70895e83"
OLD="WenguaApp_神奇之门21章_开悟之门22节_194案例_完整研究库.sqlite3"
NEW="WenguaApp_双书194案例_婚姻断语V1_完整研究库.sqlite3"
SOURCE_BOOKS={
 "shenqi":("marriage_prediction_ch02","64c7e9c1c0e646814c11644809277f71587d21736bdbd49679e6ad65611303c9"),
 "kaiwu":("marriage_prediction_ch02_section02","4df9dfe432daec759df4f0e01449bc4a2381eb4251e1290a0d99d199e467fa01"),
 "final":("questions_answers_errors_and_methods_ch03","2f52d1ed878f77f619e5cf48c088a9f2e25afe59daaae037b97fcb96b0bd947a")
}
VERSION="marriage_reading_v1.1"
FACTOR_NAMES=[
 "six_yi_striking_punishment","branch_opposition","branch_punishment",
 "branch_harm","month_day_break","door_press_palace","heaven_stem_tomb",
 "stem_storage","travel_horse","xun_kong","kong_near_far","kong_fill",
 "kong_clash","hidden_stems","seasonal_prosperity","palace_five_elements",
 "heaven_earth_stem_structure","star_door_deity_structure","fuyin_fanyin",
 "palace_interactions","auspicious_inauspicious_formations",
 "primary_secondary_yongshen","conflicting_evidence","timing_qualification"]
# Plain-language originals by GPT with no attached imaginary cast or asserted actual result.
PHRASES=[
 dict(id="marriage.pilot.courtship_balanced.v1",scenario="courtship_balanced",
  question="courtship_to_marriage",relationship="self_or_partner",age="any",sex="any",
  needs=["marriage_people_bound","yi_geng_mutual_support","liuhe_supports_contact",
         "partner_birth_year_considered","counterevidence_checked"],
  watch=["palace_conflict","void_over_promised_timing","partner_actual_willingness"],
  text="我先说你最关心的：这段关系并不是完全没有往前走的机会。盘里代表双方的用神有相互扶持的迹象，六合所代表的婚缘也接得上，所以按传统奇门的看法，我偏向于认为两个人还有继续商量的空间。不过，我不会只凭乙庚相生就说一定结婚，还要看双方年命、目前的态度，以及空亡和门星有没有牵制。尤其是定婚期，光有合象远远不够。你可以先看看对方会不会主动安排见面、把未来的事情认真谈起来。盘里的有利因素可以作参考，真正能不能走下去，还是看双方是不是都愿意行动。",
  sources=[
   ("shenqi",[5,11,54,58],"shenqi.marriage.mother_asks_son_courtship","相生不等于必成，六合与主次用神需合看","method_basis"),
   ("kaiwu",[39,41,43],"kaiwu.marriage.case01","年命、乙庚、日时与六合反证","author_example")]),
 dict(id="marriage.pilot.parent_asks_child.v1",scenario="parent_asks_adult_child",
  question="child_courtship_marriage",relationship="parent_of_subject",age="adult",sex="any",
  needs=["child_is_real_subject","birth_year_of_child_present","day_and_hour_roles_not_conflated",
         "yi_geng_link_checked","liuhe_and_counterevidence_checked"],
  watch=["child_does_not_consent","querent_role_confused_with_subject","calendar_timing_unverified"],
  text="你替孩子问这段感情，我会先把你和孩子分开来看：问事的人是你，真正要决定婚姻的却是孩子本人。盘里就算乙庚之间有相生的迹象，也不能据此认定孩子已经愿意成婚；我更在意孩子年命和代表其自身的位置是否受到牵制，再看六合、门星以及双方家长的态度能否配合。如果这些地方相互支持，可以说婚事有推动空间；若孩子的主用神仍受困，就可能是家里着急、当事人却还没想好。现阶段不必替孩子把结论说满，最好先听听他自己对关系和时间安排的真实想法。",
  sources=[
   ("shenqi",[54,64,107,125],"shenqi.marriage.mother_asks_son_courtship","母亲代测子女需区分问者和婚姻主体","method_basis"),
   ("kaiwu",[7,31,39,41,43],"kaiwu.marriage.case01","王大妈问儿子婚事，案例说明子女年命和实际意愿","author_example")]),
 dict(id="marriage.pilot.divorce_or_reunion.v1",scenario="divorce_remarriage_context",
  question="divorce_or_remarriage",relationship="self_or_partner",age="any",sex="any",
  needs=["marital_status_clarified","question_divorce_vs_reunion_clarified",
         "partners_year_stems_checked","spouse_palace_pair_checked",
         "contradicting_conditions_reconciled"],
  watch=["year_stem_compatibility_only","fuyin_opposes_claim","real_world_no_contact"],
  text="这件事不能只拿双方年命的生克下结论。相生不等于一定会复合，相克也不代表一定走到离婚那一步。我会先确认你问的是已经分开的两个人能否重新相处，还是仍在婚姻里的人是否要分开；两个问题取用神的重点不一样。再看双方各自所在的宫位、六合和门星的状态，以及有没有空亡、伏吟或其他相反证据。即便局里同时出现亲近和阻碍，也可能反映的是彼此还有牵挂、现实沟通却不顺。与其把一时的冲合说成最后结果，不如结合双方近期的互动，再谨慎判断关系有没有真正转变。",
  sources=[
   ("shenqi",[9,11,178,184],"shenqi.marriage.mother_asks_son_courtship","已婚/离异复杂问题不能仅按年命","method_basis"),
   ("kaiwu",[73,77,81,89],"kaiwu.marriage.case02","源书离婚案例须看多步条件","author_example"),
   ("final",[382,384,385,409,410,411,412,413],"kaiwu.final.divorce","同盘两人离婚复婚机械断错","counterexample_original_error")]),
 dict(id="marriage.pilot.third_party_caution.v1",scenario="suspected_third_party",
  question="relationship_trust_concern",relationship="self_or_partner",age="any",sex="any",
  needs=["third_party_question_explicit","symbol_roles_selected_by_context",
         "yi_geng_and_liuhe_checked","birth_stems_known_or_marked_unknown",
         "possible_false_positive_reviewed"],
  watch=["no_independent_behavior_evidence","third_party_symbol_ambiguous",
         "original_author_guess_proved_wrong"],
  text="问到感情里是不是出现了别人，我会格外慎重。书里确实有借丁、丙等符号观察第三者的传统方法，但这些象意本身不能证明现实中有人隐瞒感情，更不能据此给任何人定性。即使某个符号与配偶用神有联系，也要同时核对双方年命、六合、日时干的关系，并留意是否有空亡、反吟或用神定位不清等反证。如果这些信息没有相互印证，我不会给你一个肯定的判断。与其让盘面的猜测增加不必要的误会，不如先弄清楚你真正介意的行为是什么，以及双方是否愿意坦诚沟通。",
  sources=[
   ("shenqi",[13,229,293,361,365],"shenqi.marriage.wife_asks_husband_affair","丁丙第三者类象是古籍候选，不是事实鉴定","method_basis"),
   ("final",[384,385,409,410,411,413],"kaiwu.final.divorce","最后错例章反对万能生克判断","counterexample_original_error")])
]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def asjson(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def older_rows_equal(old,new):
 for (tab,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+tab+'")')]
  selection=",".join('"'+c+'"' for c in cols)
  before=list(old.execute('SELECT '+selection+' FROM "'+tab+'"'))
  after=set(new.execute('SELECT '+selection+' FROM "'+tab+'"'))
  if any(row not in after for row in before):raise ValueError("Replaced or lost original row in "+tab)
def seed(base,output,indexdir):
 base,output,indexdir=map(Path,(base,output,indexdir))
 if output.exists():raise ValueError("Append-only versioned phrase DB cannot overwrite any database")
 if sha(base.read_bytes())!=BASE_SHA:raise ValueError("194-event two-book FULL parent SHA required")
 if len(PHRASES)!=4 or matrix_cardinality()!=388800:raise ValueError("Matrix or pilot size wrong")
 prompt=ROOT/"prompts/marriage_reading_v1.md"
 prompt_hash=sha(prompt.read_bytes())
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/038_marriage_phrase_library.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   existing=db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
   if existing!=194:raise ValueError("Never alter 194 historical case families")
   book_marriage=db.execute("""SELECT COUNT(*) FROM cases
   WHERE domain_id='marriage' AND section_id IN
   (SELECT section_id FROM sections WHERE book_id IN ('shenqi','kaiwu'))""").fetchone()[0]
   if book_marriage!=14:raise ValueError(("Expected 12 marriage chapter cases + 2 final marriage errors",book_marriage))
   db.execute("""INSERT INTO phrase_domain_progress
   (domain_id,stage,source_family_count,source_note,last_prompt_version,update_note)
   VALUES('marriage','prototype_draft',14,? ,?,?)""",
   ("12 original domain book cases and 2 explicit final-chapter marriage failures",
    VERSION,"First four conditional, source-linked ~200 Hanzi prototype texts; 0 verified live charts/instances."))
   for p in PHRASES:
    text=p["text"];chinese=sum('\u4e00'<=ch<='\u9fff' for ch in text)
    if not 160<=chinese<=240:raise ValueError(("Not approximately 200 Hanzi",p["id"],chinese))
    when={"all":[{"fact":t,"must_be":True} for t in p["needs"]],
     "any_contrary_must_be_reported":True,"unknown":"abstain",
     "chart_must_be_verifiably_cast":True}
    counter={"check_before_final":p["watch"],"if_material_unresolved":"do_not_assert_positive_negative_or_date"}
    evidence={"mandatory_factor_checks":FACTOR_NAMES,
     "relationship_and_real_subject_binding":True,"primary_and_secondary_yongshen":True,
     "seasonal_stem_star_door_deity_palace_wuxing":True,
     "three_sources_crosschecked":False,"no_numeric_door_pressure_discount_without_source":True}
    trace={"source_phase":"original_author_reasoning_not_feedback",
     "linguistic_polishing_only":True,"requires_structured_evidence_first":True,
     "original_author_errors_accessible":True,"not_applied_to_any_1080_state":True}
    db.execute("""INSERT INTO phrase_template_drafts
    (phrase_id,domain_id,scenario,question_type,relationship_scope,
     target_age_band,target_sex,rule_conditions_json,obligatory_evidence_json,
     counterevidence_json,reasoning_trace_json,draft_text,draft_text_sha256,
     style_version,created_utc)
    VALUES (?,'marriage',?,?,?,?,?,?,?,?,?,?,?,?,'2026-10-21')""",
    (p["id"],p["scenario"],p["question"],p["relationship"],p["age"],p["sex"],
     asjson(when),asjson(evidence),asjson(counter),asjson(trace),
     text,sha(text.encode()),VERSION))
    for source_key,lines,case_id,note,kind in p["sources"]:
     book="kaiwu" if source_key=="final" else source_key
     section,expected_sha=SOURCE_BOOKS[source_key]
     row=db.execute("""SELECT original_text FROM sections
      WHERE book_id=? AND section_key=? AND sha256=?""",
      (book,section,expected_sha)).fetchone()
     if not row:raise ValueError(("Missing exact original book section SHA",source_key,section))
     count=len(row[0].splitlines())
     if any(i<1 or i>count for i in lines):raise ValueError(("Bad source line",source_key,lines,count))
     if not db.execute("SELECT 1 FROM cases WHERE case_id=?",(case_id,)).fetchone():
      raise ValueError(("Unknown original marriage family",case_id))
     db.execute("""INSERT INTO phrase_source_links
      (phrase_id,book_id,source_section_key,source_sha256,source_lines_json,
       case_id,relevance,epistemic_role)
      VALUES(?,?,?,?,?,?,?,?)""",
      (p["id"],book,section,expected_sha,asjson(lines),case_id,note,kind))
   db.execute("""INSERT INTO phrase_pipeline_audit VALUES
    ('marriage.seed.v1','marriage',?,?, 'prototype_draft',2,14,0,4,0,?)""",
    (VERSION,BASE_SHA,asjson({"prompt_sha256":prompt_hash,
      "domain":"marriage","all_194_prior_book_cases_preserved":True,
      "one_domain_per_iteration":True,
      "1080_states_unique_but_not_verified_nine_palaces":True,
      "never_materialize_unverified_388800_grid":True,
      "prototype_texts_are_not_published_predictive_readings":True})))
  older_rows_equal(old,db)
  if db.execute("SELECT COUNT(*) FROM phrase_context_instances").fetchone()[0]!=0:
   raise ValueError("Cannot preinstantiate bogus 388800 chart nodes")
  if db.execute("SELECT COUNT(*) FROM phrase_template_drafts WHERE review_status='draft'").fetchone()[0]!=4:
   raise ValueError("Expected exactly four source-linked unapproved pilot drafts")
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Phrase DB corrupt or unresolved source foreign keys")
  db.execute("VACUUM")
  db.commit()
  checks={table:db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0] for table in
   ("sections","cases","historical_chart_cells","phrase_domain_progress","phrase_template_drafts",
    "phrase_source_links","phrase_context_instances","phrase_pipeline_audit")}
 indexdir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_marriage_domain_phrase_pilot_v1",
  "upstream_full_source_archive_sha256":BASE_SHA,
  "new_full_database_sha256":sha(output.read_bytes()),
  "appended_migration":"038_marriage_phrase_library.sql",
  "prompt_version":VERSION,"prompt_sha256":prompt_hash,
  "domain":"marriage","source_marriage_event_families":14,
  "old_complete_book_sources":43,"old_historical_events":194,
  "distinct_verified_chart_state_indices":1080,
  "engine_verified_full_nine_palace_chart_states":0,
  "theoretical_state_year_age_sex_nodes":388800,
  "extra_dimensions_required":["marriage_question_type","querent_relationship","subject_identity","partner_birth_stem"],
  "prototype_human_style_phrase_count":len(PHRASES),
  "verified_chart_phrase_instances":0,"approved_phrase_instances":0,
  "all_previous_DB_rows_unchanged":True,
  "all_new_phrases_draft_only":True,"counts":checks}
 (indexdir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n","utf8")
 (indexdir/"source_prototypes.json").write_text(json.dumps([
  {"phrase_id":p["id"],"scenario":p["scenario"],"question":p["question"],
   "required_conditions":p["needs"],"counterevidence":p["watch"],
   "chinese_char_count":sum('\u4e00'<=c<='\u9fff' for c in p["text"]),
   "source_case_refs":[s[2] for s in p["sources"]],"review_status":"draft"} for p in PHRASES],ensure_ascii=False,indent=2)+"\n","utf8")
 return manifest
def main():
 ap=argparse.ArgumentParser()
 for k in ("base","output","index-dir"):ap.add_argument("--"+k,required=True)
 a=ap.parse_args();print(asjson(seed(a.base,a.output,a.index_dir)))
if __name__=="__main__":main()
