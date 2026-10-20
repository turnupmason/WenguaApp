from pathlib import Path
import sqlite3,hashlib,json,os,lzma,base64,textwrap
import argparse
p=argparse.ArgumentParser();p.add_argument('--db',required=True,type=Path);a=p.parse_args()
d=a.db;R=d.parent
with sqlite3.connect(d) as c:
 c.execute('PRAGMA foreign_keys=ON')
 c.executescript('''CREATE TABLE IF NOT EXISTS historical_outcome_reclassification_audit (
   case_id TEXT PRIMARY KEY REFERENCES cases(case_id),previous_verdict TEXT NOT NULL,
   corrected_verdict TEXT NOT NULL,evidence_source_lines_json TEXT NOT NULL CHECK(json_valid(evidence_source_lines_json)),
   reasoning_original_retained INTEGER NOT NULL,explanation TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS historical_center_derivation_rule (rule_key TEXT PRIMARY KEY,
   source_chapter TEXT NOT NULL,source_term TEXT NOT NULL,derived_palace INTEGER NOT NULL,
   rule_status TEXT NOT NULL,notes TEXT NOT NULL);
 ''')
 c.execute('INSERT OR IGNORE INTO historical_center_derivation_rule VALUES (?,?,?,?,?,?)',('five_center_hosts_kun_2','shijia_qiju','中五宫寄坤二宫',2,'method_source_supported_derived_not_literal','76 historical cast centers carry source center stem; hosting is a separate derived field; never insert unprinted center deity/door/star'))
 cid='shenqi.missing.taxi_driver_student_wrong_teacher_revised'
 row=c.execute('SELECT verdict FROM historical_case_book_verdicts WHERE primary_case_id=?',(cid,)).fetchone()
 assert row and row[0] in ('author_book_success_default','author_book_error_explicit'), row
 if row[0]=='author_book_success_default':
  c.execute('INSERT OR IGNORE INTO historical_outcome_reclassification_audit VALUES (?,?,?,?,?,?)', (cid,row[0],'author_book_error_explicit',json.dumps([455,457,459,461,463,465,467,469,471,473,475]),1,'Source chapter explicit first-call incorrect prediction, teacher correction later. Status was not corrected in supplied 12-chapter baseline. Original author text and source preserved.'))
 if row[0]=='author_book_success_default':
  c.execute("UPDATE historical_case_book_verdicts SET verdict='author_book_error_explicit',explicit_source_correction=1,source_correction_lines_json=?, note=note||' | Correction of original first call, see teacher analysis lines 459-475' WHERE primary_case_id=?",(json.dumps([457,459,461,463,465,467,469,471,473,475]),cid))
 c.execute("UPDATE historical_case_review_audit SET review_status='explicit_original_error_corrected_then_requires_complete_chain',warning=warning||'; teacher correction cannot be used as initial positive learning' WHERE case_id=?",(cid,))
 # document user authorization overriding older no-public-upload internal snapshot labels
 c.execute("UPDATE chapter_archival_versions SET repo_public_archive_policy='OWNER_EXPLICITLY_AUTHORIZED_PUBLIC_SQLITE_ARCHIVING' WHERE archive_label='shenqi_14_chapters_71_cases'")
 assert c.execute('SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2').fetchone()[0]==76
 assert c.execute('SELECT count(*) FROM historical_case_reasoning_trace').fetchone()[0]==319
 assert c.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]==4
 assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
 c.commit()
# lzma archival snapshot and base64 of both for GitHub blob bridge
raw=d.read_bytes()
(R/'published_archive.b64.txt').write_text('\n'.join(textwrap.wrap(base64.b64encode(raw).decode('ascii'),2048)),encoding='ascii')
comp=lzma.compress(raw,preset=9)
(R/'published_archive.sqlite3.xz').write_bytes(comp)
(R/'published_archive.xz.b64.txt').write_text('\n'.join(textwrap.wrap(base64.b64encode(comp).decode('ascii'),2048)),encoding='ascii')
summary={'name':d.name,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'compressed_size':len(comp),'compressed_sha256':hashlib.sha256(comp).hexdigest(),'base64_lines':len((R/'published_archive.b64.txt').read_text().splitlines()),'sql_tables':[]}
with sqlite3.connect(d) as c:
 summary['sql_tables']={t:c.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['sections','cases','historical_chart_cells','historical_case_additional_cast_cells','historical_case_reasoning','semantic_assertions','historical_case_reasoning_trace','historical_palace_standardization','historical_case_review_audit']}
 summary['source_shas']={k:s for k,s in c.execute('SELECT section_key,sha256 FROM sections')}
(R/'public_snapshot_manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
