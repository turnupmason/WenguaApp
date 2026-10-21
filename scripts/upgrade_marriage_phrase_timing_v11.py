"""V1.1 append-only upgrade: retain V1 prose and all 194 historical cases."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD="WenguaApp_双书194案例_婚姻断语V1_完整研究库.sqlite3"
NEW="WenguaApp_双书194案例_婚姻断语V1_1_应期强制_完整研究库.sqlite3"
BASE_SHA="4c57e8bfdc4d745c19711542039c3f24aa95b7574de00843e64c1676082d4968"
FULL_BOOK_SHA="c57153c296b1369e2b9bd78039dbe0cc191d67721f5042828e5ef54e70895e83"
VERSION="marriage_reading_v1.1"
def h(b):return hashlib.sha256(b).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def keep_old(a,b):
 for (table,) in a.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  keys=[r[1] for r in a.execute('PRAGMA table_info("'+table+'")')]
  proj=','.join('"'+x+'"' for x in keys)
  current=set(b.execute('SELECT '+proj+' FROM "'+table+'"'))
  if any(v not in current for v in a.execute('SELECT '+proj+' FROM "'+table+'"')):
   raise ValueError("Old case/phrase row changed: "+table)
def run(base,out,index):
 base,out,index=map(Path,(base,out,index))
 if out.exists():raise ValueError("Existing V1.1 binary cannot be replaced")
 if h(base.read_bytes())!=BASE_SHA:raise ValueError("Must derive from preserved V1 binary SHA")
 prompt=ROOT/"prompts/marriage_reading_v1.md"
 prompt_bytes=prompt.read_bytes()
 if "必须断出明确结果与具体应期" not in prompt_bytes.decode("utf8"):
  raise ValueError("V1.1 user amendment absent")
 out.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base.resolve())+"?mode=ro",uri=True) as previous,sqlite3.connect(out) as db:
  previous.backup(db)
  db.executescript((ROOT/"schema/migrations/039_marriage_decisive_timing_v11.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   assert db.execute("SELECT count(*) FROM cases").fetchone()[0]==194
   assert db.execute("SELECT count(*) FROM phrase_template_drafts").fetchone()[0]==4
   assert db.execute("SELECT count(*) FROM phrase_context_instances").fetchone()[0]==0
   policy={"hard_requirement":"decisive_outcome_and_real_computed_primary_timing",
    "preexisting_four_texts_are_style_drafts_not_completed_readings":True,
    "missing_verified_cast_or_calendar_blocks_publication":True,
    "traditional_interpretation_not_certified_future_event":True}
   db.execute("""INSERT INTO phrase_version_progress
    (domain_id,prompt_version,prompt_sha256,release_stage,inherited_archive_sha256,
     asserted_original_events,created_utc,notes_json)
    VALUES ('marriage',?,?,'v1_1_concrete_timing_draft',?,194,'2026-10-21',?)""",
    (VERSION,h(prompt_bytes),BASE_SHA,js(policy)))
   for (pid,) in db.execute("SELECT phrase_id FROM phrase_template_drafts ORDER BY phrase_id").fetchall():
    db.execute("""INSERT INTO phrase_outcome_timing_contracts
      (phrase_id,contract_version,prompt_version,user_directive) VALUES (?,2,?,?)""",
      (pid,VERSION,"给明确成败、来源可追溯的主应期与经历法计算日期。缺数据不得编造，也不得用'以后填实再说'替代结果。"))
   db.execute("""INSERT INTO phrase_pipeline_audit VALUES
    ('marriage.timing_gate.v1_1','marriage',?,?,'mandatory_concrete_timing_design',2,194,0,4,0,?)""",
    (VERSION,FULL_BOOK_SHA,js(policy)))
  keep_old(previous,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Invalid SQLite V1.1")
  db.execute("VACUUM");db.commit()
  counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in
   ["sections","cases","historical_chart_cells","phrase_domain_progress",
   "phrase_template_drafts","phrase_source_links","phrase_context_instances",
   "phrase_pipeline_audit","phrase_version_progress",
   "phrase_outcome_timing_contracts","phrase_instance_timing_windows"]}
 assert counts=={"sections":43,"cases":194,"historical_chart_cells":1440,
   "phrase_domain_progress":1,"phrase_template_drafts":4,
   "phrase_source_links":9,"phrase_context_instances":0,
   "phrase_pipeline_audit":2,"phrase_version_progress":1,
   "phrase_outcome_timing_contracts":4,"phrase_instance_timing_windows":0}
 manifest={"domain":"marriage","prompt_version":VERSION,
  "prompt_sha256":h(prompt_bytes),"inherited_complete_V1_sha256":BASE_SHA,
  "source_194_case_archive_sha256":FULL_BOOK_SHA,"new_SQLite_sha256":h(out.read_bytes()),
  "historical_events":194,"historical_chapters":43,"old_draft_phrases":4,
  "concrete_phrase_instances_without_real_boards":0,
  "required_concrete_primary_time_if_calculable":True,
  "original_source_rows_and_v1_phrases_unchanged":True,
  "source_only_not_scientifically_verified":True,"counts":counts}
 index.mkdir(parents=True,exist_ok=True)
 (index/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n","utf8")
 return manifest
def main():
 p=argparse.ArgumentParser()
 for k in ("base","output","index-dir"):p.add_argument("--"+k,required=True)
 a=p.parse_args();print(js(run(a.base,a.output,a.index_dir)))
if __name__=="__main__":main()
