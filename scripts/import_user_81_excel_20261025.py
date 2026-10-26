"""Convert user's local .xlsx ('81格完整表') to the live, editable TSV.

Usage (on machine with artifact_tool installed):
    python scripts/import_user_81_excel_20261025.py "奇门遁甲_天地盘81格_古文吉凶化解取象.xlsx"

Checks 81 complete ordered pairs before replacing TSV. This conversion does
NOT change the archived input workbook or any prior catalog.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data/knowledge/health_81_excel_20261025/81_pairs.tsv"
HEADERS=("天盘干","地盘干","格局名称","吉凶","古文（摘句）","古诀大意","天地盘取象")
STEMS="戊乙丙丁己庚辛壬癸"


def extract(input_path):
    # Original XLSX read by the installed spreadsheet artifact_tool API.
    from artifact_tool import Blob,SpreadsheetFile
    book=SpreadsheetFile.import_xlsx(Blob.load(str(input_path)))
    sheet=book.worksheets.get_item("81格完整表")
    actual=sheet.get_range("B4:H85").values
    if tuple(actual[0])!=HEADERS:
        raise ValueError("Unexpected Excel columns B4:H4")
    lines=[]
    seen=set()
    for rowno,raw in enumerate(actual[1:],start=5):
        values=tuple("" if v is None else str(v).strip() for v in raw)
        if len(values)!=7 or not all(values):
            raise ValueError("Missing Excel cell, row "+str(rowno))
        if any("|" in v or "\n" in v or "\r" in v for v in values):
            raise ValueError("TSV delimiter or line break in Excel row "+str(rowno))
        h,e,_,polarity,*_=values
        if h not in STEMS or e not in STEMS or polarity not in ("吉","凶"):
            raise ValueError("Wrong pair or 吉凶, row "+str(rowno))
        if (h,e) in seen:raise ValueError("Duplicate "+h+e)
        seen.add((h,e))
        lines.append("|".join(values))
    if len(lines)!=81 or seen!={(h,e) for h in STEMS for e in STEMS}:
        raise ValueError("Source Excel must have 81 distinct ordered combinations")
    return "|".join(HEADERS)+"\n"+"\n".join(lines)+"\n"


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("xlsx",type=Path,help="The user's edited Excel source file")
    arg.add_argument("--check",action="store_true",
                     help="Show whether generated live TSV equals repo; do not write")
    ns=arg.parse_args()
    content=extract(ns.xlsx)
    if ns.check:
        old=DEST.read_text(encoding="utf-8") if DEST.exists() else ""
        print("81 complete source rows; matches checked-in TSV:",old==content)
        return
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(content,encoding="utf-8")
    print("Wrote",DEST,"with 81 complete rows. Commit this TSV to GitHub.")


if __name__=="__main__":
    main()
