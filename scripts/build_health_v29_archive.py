"""Immutable, append-only V2.9 full original 194-case archive."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_two_historical_health_v29 import evaluate
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="1837107123d78f1da47e1046c9043827484985e6cb1ff01689e70057c7d6c301"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v29/severity_fixed_template.json"
MIG=ROOT/"schema/migrations/057_health_medical_no_duplicate_v29.sql"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(parent,out,sealed,manifest):
    parent,out,sealed,manifest=map(Path,(parent,out,sealed,manifest))
    if out.exists() or sealed.exists():raise ValueError("Previous results immutable")
    if sha(parent)!=PARENT_SHA:raise ValueError("Full exact V2.8 parent SHA mismatch")
    j=json.loads(TEMPLATE.read_text("utf8"))
    report=evaluate(db_path=parent)
    assert len(j["sections"])==11 and len(report["samples"])==2
    out.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for table,count in (("cases",194),("sections",43),
              ("health_v27_sealed_historical_predictions",2),
              ("health_v28_historical_review",2)):
                assert db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]==count
            for x in j["sections"]:
                db.execute("""INSERT INTO health_v29_no_duplicate_medical_template
                   (section_id,format_text,no_gpt_runtime,user_review_status)
                   VALUES(?,?,1,'pending')""",(x["id"],x["format"]))
            for x in report["samples"]:
                db.execute("""INSERT INTO health_v29_archival_readouts
                    (case_id,v28_original_sha256,v29_updated_sha256,old_user_approved_v27,
                     original_results_used,original_seals_preserved)
                    VALUES(?,?,?,?,0,1)""",
                    (x["case_id"],x["unchanged_v28_sha"],x["sha256"],
                     int("19960523" in x["case_id"])))
        preserve(old,db)
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall()==[]
        db.execute("VACUUM");db.commit()
    sealed.parent.mkdir(parents=True,exist_ok=True)
    sealed.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    data={"version":"V2.9","parent_sha256":PARENT_SHA,"new_full_sha256":sha(out),
       "new_sealed_sha256":sha(sealed),"original_cases":194,"original_sections":43,
       "original_v27_v28_readings_preserved":True,
       "older_second_user_approved_v27_only":True,"new_v29_review":"pending",
       "pure_offline_no_GPT":True,"medical_accuracy_not_validated":True}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n","utf8")
    return data
if __name__=="__main__":
    arg=argparse.ArgumentParser()
    for name in ("parent","output","sealed","manifest"):
        arg.add_argument("--"+name,required=True)
    a=arg.parse_args()
    print(json.dumps(build(a.parent,a.output,a.sealed,a.manifest),ensure_ascii=False))
