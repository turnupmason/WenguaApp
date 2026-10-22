"""V28 immutable complete 194-case SQLite; source, old predictions unchanged."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_two_historical_health_v28 import evaluate
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="2e0929d0823d2e69547ed09bd5cd2927d705f484965662d092bdd02fead627f7"
MIG=ROOT/"schema/migrations/056_health_medical_timing_tomb_v28.sql"
TPL=ROOT/"data/knowledge/phrase_library/health_v28/severity_fixed_template.json"
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def build(parent,output,sealed,ledger):
    parent,output,sealed,ledger=map(Path,(parent,output,sealed,ledger))
    if output.exists() or sealed.exists():raise ValueError("Never overwrite original archived trials")
    if sha(parent)!=PARENT_SHA:raise ValueError("Incorrect full V27 parent checksum")
    template=json.loads(TPL.read_text("utf8"))
    report=evaluate(db_path=parent)
    if len(template["sections"])!=11 or len(report["new_predictions"])!=2:
        raise ValueError("Missing source sections or original pair")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as con:
        old.backup(con)
        con.executescript(MIG.read_text("utf8"))
        con.execute("PRAGMA foreign_keys=ON")
        with con:
            for table,count in {"cases":194,"sections":43,
                "health_v22_customer_severity_sections":21,
                "health_v27_fixed_customer_sections":11,
                "health_v27_sealed_historical_predictions":2}.items():
                if con.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0]!=count:
                    raise ValueError("Original source or seals missing: "+table)
            for i,s in enumerate(template["sections"],1):
                con.execute("""INSERT INTO health_v28_fixed_customer_sections
                    (ordinal,section_id,title,source_template_format,optional_context,pure_offline_no_gpt)
                    VALUES(?,?,?,?,?,1)""",(i,s["id"],s["title"],s["format"],s.get("optional")))
            for id,condition,origin,limit in [
                ("event_with_tianxin_or_yi",
                 "hour stem event palace equals Tianxin or Yi medicine palace",
                 "2026-10-22 user method addition",
                 "early medical attention symbol; not efficacy or medical diagnosis"),
                ("illness_with_tianxin_or_yi",
                 "Tianrui illness palace equals Tianxin or Yi medicine palace",
                 "2026-10-22 user method addition",
                 "requires independent review of doctor/Yi palace month states and obstacles"),
                ("tianxin_nine_star_month_state",
                 "nine_star_month_status(Tianxin,MONTH_ELEMENTS[month_branch])",
                 "shenqi star monthly formula",
                 "九星月废 differs from Yi stem normal month 五行死"),
                ("yi_wood_stem_month_state",
                 "Yi wood stem 旺相休囚死 by actual month element",
                 "shenqi four-symbol lifecycle; 2026 user demand",
                 "medicinal opportunities weakened by tomb/void/pressure/punishment"),
                ("exact_tomb_six_yi_striking",
                 "乙丙乾6丁艮8; 戊3己2庚8辛9壬4癸4",
                 "kaiwu chapter 4 lines 506-544",
                 "only actual relevant heavenly stem matched to palace; distinguish 墓地 vs 墓库")]:
                con.execute("""INSERT INTO health_v28_medical_timing_rules
                    (rule_id,condition_text,source_book_or_user,important_limit,clinically_validated)
                    VALUES(?,?,?,?,0)""",(id,condition,origin,limit))
            for x in report["new_predictions"]:
                state=("user_approved_prior_v27_only" if "19960523" in x["case_id"] else "pending")
                con.execute("""INSERT INTO health_v28_historical_review
                    (case_id,v27_original_sha256,v28_readout_sha256,previous_book_case_outcome_used,
                     user_review_state,full_original_v27_unchanged)
                    VALUES (?,?,?,0,?,1)""",
                    (x["case_id"],x["old_sealed_readout_sha256"],
                     x["new_readout_sha256"],state))
        preserve(old,con)
        assert con.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert con.execute("PRAGMA foreign_key_check").fetchall()==[]
        con.execute("VACUUM")
        con.commit()
    sealed.parent.mkdir(parents=True,exist_ok=True)
    sealed.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    manifest={"schema":"wengua_v28_194_original_full_2_source_case_medical_timing",
       "parent_sha256":PARENT_SHA,"new_full_sha256":sha(output),
       "readouts_sha256":sha(sealed),"original_family_count":194,
       "original_sections":43,"original_v27_two_readouts_untouched":True,
       "user_approval":"second old V27 output only; both updated V28 pending",
       "first_original_outcome_unreviewed":True,
       "no_gpt_or_network":True,
       "no_real_clinical_prognosis":True,
       "other_four_intents_remain_frozen":True}
    ledger.parent.mkdir(parents=True,exist_ok=True)
    ledger.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n","utf8")
    return manifest
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for a in ("base","output","sealed","ledger"):p.add_argument("--"+a,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.base,a.output,a.sealed,a.ledger),ensure_ascii=False))
