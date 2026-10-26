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
    if not cases:
        issues.append("EMPTY_SOURCE_CASES")
    report=["# STRICT GPT-Python versus iOS native literal reading parity","",
       "Both entire paragraphs and their headings, line breaks, punctuation must match.",
       "No whitespace normalization or omitted sections is permitted.",""]
    if len(cases)!=len(native):
        issues.append("COUNT python=%d swift=%d"%(len(cases),len(native)))
    for i,one in enumerate(cases):
        if i>=len(native):break
        app=native[i]
        metadata_errors=[]
        if app.get("instant")!=one["instant"]:
            metadata_errors.append("clock mismatch")
        if app.get("relationship")!=one["relationship"]:
            metadata_errors.append("role mismatch")
        if app.get("ordinal")!=i+1:
            metadata_errors.append("ordinal mismatch")
        if app.get("section_count")!=len(app.get("sections",[])):
            metadata_errors.append("section count mismatch")
        if not isinstance(app.get("sections"),list):
            metadata_errors.append("missing native sections")
            app["sections"]=[]
        if not all(isinstance(s,dict) and all(k in s for k in ("id","title","text")) for s in app["sections"]):
            metadata_errors.append("incomplete native section fields")
            app["sections"]=[]
        actual="\n\n".join(s["title"]+"：\n"+s["text"] for s in app["sections"])
        expected=one["python_reading_text"]
        # Byte-identical prose alone does not prove stable app routing.
        # Require source-exact sections, order, IDs and all three raw fields
        # so the native product and Python cannot silently use different
        # subsections while reconstructing similar paragraphs.
        python_sections=one["source_sections"]
        native_sections=app["sections"]
        exact_sections=(python_sections==native_sections)
        if actual==expected and exact_sections and not metadata_errors:
            report.append("## %d %s: EXACT MATCH (text + all section IDs/titles/bodies)"%(
                i+1,one["instant"]))
        else:
            reason=("FULL_TEXT_MISMATCH" if actual!=expected else
                    "SECTION_STRUCTURE_MISMATCH" if not exact_sections else
                    "METADATA_MISMATCH")
            issues.append("%s %s %s %s"%(one["instant"],one["relationship"],reason,",".join(metadata_errors)))
            report.append("## %d %s (%s): MISMATCH"%(i+1,one["instant"],one["relationship"]))
            if metadata_errors:
                report.append("METADATA ERRORS: "+", ".join(metadata_errors))
            report.append("Python sections %d, Swift sections %d; character lengths %d and %d"%(
                len(one["source_sections"]),len(app["sections"]),len(expected),len(actual)))
            comparison="\n".join(difflib.unified_diff(
                expected.splitlines(),actual.splitlines(),
                fromfile="live_Python_GPT_Vnext",tofile="native_iOS_Vnext",
                lineterm="",n=2))
            if not exact_sections:
                report.append("Section records differ (including IDs, order or text):")
                report.append(json.dumps({
                    "python_sections":python_sections,
                    "ios_sections":native_sections
                },ensure_ascii=False,sort_keys=True)[:10000])
            report.extend(["", "DIFF START",comparison[:26000],"DIFF END",""])
            print("EXACT_WORDING_FIRST_DIFF_"+str(i+1)+" "+comparison[:4200])
    report.append("\nExact equality: %d of %d"%(
        sum(1 for line in report if ": EXACT MATCH" in line),len(cases)))
    report.append("ISSUES: "+(" | ".join(issues) if issues else "none"))
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
