"""Exact GPT/Python vs native iOS user text parity. Any mismatch FAILS CI.

Compare current Python reading_text including full titles, punctuation,
ordered paragraphs and whitespace against the production native router.
Keep original diffs for debugging. No fixture-only substitution is allowed.
"""
import argparse
import difflib
import json
from pathlib import Path

MARKER="VNEXT_IOS_PYEXACT="
def compare(python_path,swift_path,report_path):
    source=json.loads(Path(python_path).read_text(encoding="utf8"))
    raw=Path(swift_path).read_text(encoding="utf8").splitlines()
    native=[json.loads(line.split(MARKER,1)[1])
            for line in raw if MARKER in line]
    cases=source["cases"]
    issues=[]
    report=["# STRICT GPT-Python versus iOS native literal reading parity","",
       "Both entire paragraphs and their headings, line breaks, punctuation must match.",
       "No whitespace normalization or omitted sections is permitted.",""]
    if len(cases)!=len(native):
        issues.append("COUNT python=%d swift=%d"%(len(cases),len(native)))
    for i,one in enumerate(cases):
        if i>=len(native):break
        app=native[i]
        actual="\n\n".join(s["title"]+"：\n"+s["text"] for s in app["sections"])
        expected=one["python_reading_text"]
        if actual==expected:
            report.append("## %d %s: EXACT MATCH"%(i+1,one["instant"]))
        else:
            issues.append("%s %s FULL_TEXT_MISMATCH"%(one["instant"],one["relationship"]))
            report.append("## %d %s (%s): MISMATCH"%(i+1,one["instant"],one["relationship"]))
            report.append("Python sections %d, Swift sections %d; character lengths %d and %d"%(
                len(one["source_sections"]),len(app["sections"]),len(expected),len(actual)))
            comparison="\n".join(difflib.unified_diff(
                expected.splitlines(),actual.splitlines(),
                fromfile="live_Python_GPT_Vnext",tofile="native_iOS_Vnext",
                lineterm="",n=2))
            report.extend(["", "DIFF START",comparison[:26000],"DIFF END",""])
    report.append("\nExact equality: %d of %d"%(
        sum(1 for line in report if ": EXACT MATCH" in line),len(cases)))
    report.append("VERDICT: "+("PASS" if not issues else "FAIL - cannot claim complete iOS migration."))
    Path(report_path).write_text("\n".join(report)+"\n",encoding="utf8")
    print("VNEXT_GPT_IOS_EXACT_WORDING "+("PASS" if not issues else "FAIL"))
    for issue in issues:print("EXACT_WORDING_FAIL "+issue)
    return not issues

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("python_truth")
    parser.add_argument("swift_public")
    parser.add_argument("diff_report")
    args=parser.parse_args()
    if not compare(args.python_truth,args.swift_public,args.diff_report):
        raise SystemExit(1)
