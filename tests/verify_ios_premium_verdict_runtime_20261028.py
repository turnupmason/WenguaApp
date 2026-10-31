"""Run the EXACT iOS Swift result-card parser with macOS swiftc.

The inputs include five genuine, previously archived V10.2 native readings
and eleven source-verdict grade samples. This is a UI presentation test,
not a new Qimen calculation or an undisclosed case blind test.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREMIUM = ROOT / "ios/WenguaAppUI/WenguaPremiumReadingView.swift"
ROUTER = ROOT / "ios/WenguaAppUI/WenguaNativeReadingRouter.swift"
ARCHIVE = ROOT / "docs/HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40794999535_ATTEMPT_1.md"
V11_SIX = ROOT / "docs/HEALTH_V11_SIX_REAL_COMPLETE_PREVIEW_20261031.txt"

def v11_actual_sections() -> list[dict[str,str]]:
    """Parse six published real-clock source sections, not fabricated UI text."""
    source=V11_SIX.read_text(encoding="utf-8")
    samples=[]
    for part in source.split("="*64):
        if not re.search(r"V11 [1-6]/6",part):
            continue
        assert "综合断语：" in part and "时空及应期：" in part
        review=part.split("综合断语：",1)[1].split("时空及应期：",1)[0].strip()
        macro=part.split("时局总纲：",1)[1].split("\n",1)[0].strip()
        timing=part.split("时空及应期：",1)[1].split("\n",1)[0].strip()
        match=re.search(r"综上所述，此病为([^；。\\s]+)",review)
        assert match, "Real V11 grade must be explicitly resolvable"
        samples.append({"text":review,"grade":match.group(1),
                        "macro":macro,"timing":timing})
    assert len(samples)==6,"six complete real V11 source readings required"
    return samples


def native_sections() -> list[dict[str,str]]:
    original=ARCHIVE.read_text(encoding="utf-8")
    # This archive also contains many OLDER fixed cases; select only the
    # dedicated five V10.2 repeat-clock readings, never all 90_review sections.
    marker="## V10.2 已见五个真实时辰"
    assert original.count(marker)==1,"V10.2 actual five-case archive section missing"
    same_clock=original.split(marker,1)[1].split(
        "### 五份Python↔Swift全章节逐字差异报告",1)[0]
    readings=re.findall(r"#### 综合断语\n(.*?)\n\n#### 时空及应期",same_clock,re.S)
    assert len(readings)==5, "Five known V10.2 real Swift archive readings required"
    return [{"text":content,"grade":grade} for content,grade in
        zip(readings,["极大吉","不凶不吉","极大吉","极小凶","极大凶"])]

def source_fragment(text:str,start:str,end:str) -> str:
    a=text.index(start)
    b=text.index(end,a)
    return text[a:b]

def check():
    ui=PREMIUM.read_text(encoding="utf-8")
    # Check the ACTUAL first-tab Swift UI composition, not only its grade
    # caption lookup. A generic one-line override used to pass the old test.
    assert 'Text(caption.category)' in ui
    assert 'Text(grade+"："+caption.epithet)' in ui
    assert 'Text(verdict.frontNarrative(caption))' in ui
    assert 'WenguaNaturalSeveritySummary' not in ui
    native=ROUTER.read_text(encoding="utf-8")
    parts=[
        "import Foundation\n",
        source_fragment(native,"struct WenguaNativeCustomerSection:","enum WenguaNativeReadingError"),
        source_fragment(ui,"struct WenguaVerdictPresentation {","// UI-only labels")
    ]
    main=r'''
struct ActualReading: Decodable {
    let text:String
    let grade:String
}
struct V11ActualReading: Decodable {
    let text:String
    let grade:String
    let macro:String
    let timing:String
}
func checkReading(_ text:String,_ expected:String?) {
    let reading=WenguaNativeCustomerReading(
        version:"v10.2",topicID:"health.severity",relationship:"本人",
        iso:"2026-10-28T20:00:00-04:00",evidenceStatus:"verified",
        sections:[
            .init(id:"01_macro",title:"时局总纲",text:"测试源已验证"),
            .init(id:"90_review",title:"综合断语",text:text),
            .init(id:"91_timing",title:"时空及应期",text:"原文应期")]
    )
    guard let rendered=WenguaVerdictPresentation.from(reading) else {
        fatalError("native customer 90_review disappeared")
    }
    guard rendered.grade == expected else {
        fatalError("wrong UI grade: got \(String(describing:rendered.grade)), expected \(String(describing:expected))")
    }
    guard rendered.timing=="原文应期" else {fatalError("timing not retained")}
    if let expected {
        if expected == "未知" {
            guard WenguaHealthGradeCaption.forGrade(expected)==nil else {
                fatalError("unexpected unknown grade UI caption")
            }
        } else {
            guard let caption=WenguaHealthGradeCaption.forGrade(expected) else {
                fatalError("known ten-level grade not represented")
            }
            guard caption.category == (expected == "不凶不吉" ? "微恙" :
                                      expected.hasSuffix("吉") ? "吉局" : "凶局") else {
                fatalError("wrong category")
            }
        }
    }
}
let data=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
let archived=try JSONDecoder().decode([ActualReading].self,from:data)
guard archived.count==5 else {fatalError("not five real source readings")}
for x in archived {checkReading(x.text,x.grade)}
let actualGrades=["极大吉","大吉","中吉","小吉","极小吉",
                  "极小凶","小凶","中凶","大凶","极大凶","不凶不吉"]
for word in actualGrades {
    // Native V10.2 current wording, predecessor wording, and period-delimited.
    checkReading("天芮宫真实依据。\n\n综上所述，此病为"+word+"；以上仅作传统古籍象意参考，不作现实病情判断。",word)
    checkReading("天芮宫真实依据。\n\n综上所述，此病为"+word+"；以上只作传统古籍象意参考。",word)
    checkReading("综上所述，此病为"+word+"。",word)
}
checkReading("说明。\n\n部分宫位条件未能确认，暂不强断吉凶；以上仅作参考。",nil)
checkReading("说明。\n\n综上所述，此病为未知；以上仅作参考。","未知")
guard WenguaHealthGradeCaption.forGrade("未知")==nil else {
    fatalError("unknown value must fail closed")
}
// The REAL first-screen composition must be more than the single caption
// sentence. Existing full V11 specialist paragraphs remain immutable.
let sixData=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[2]))
let six=try JSONDecoder().decode([V11ActualReading].self,from:sixData)
guard six.count==6 else {fatalError("missing real V11 six cases")}
for item in six {
    let reading=WenguaNativeCustomerReading(
        version:"v11",topicID:"health.severity",relationship:"实时",
        iso:"",evidenceStatus:"verified",sections:[
            .init(id:"01_macro",title:"时局总纲",text:item.macro),
            .init(id:"90_review",title:"综合断语",text:item.text),
            .init(id:"91_timing",title:"时空及应期",text:item.timing)])
    guard let resolved=WenguaVerdictPresentation.from(reading),
          resolved.grade==item.grade,
          let caption=WenguaHealthGradeCaption.forGrade(item.grade) else {
        fatalError("wrong current V11 grade and caption binding")
    }
    let front=resolved.frontNarrative(caption)
    let count=front.filter{ !$0.isWhitespace }.count
    guard (140...215).contains(count) else {
        fatalError("real V11 first-tab summary should be ~150–200 Chinese characters, got \\(count)")
    }
    guard front.contains("病星天芮"), front.contains("医药两端分别看"),
          front.contains("患者"), !front.contains("以上仅作传统古籍象意参考") else {
        fatalError("first tab lost real patient/medical evidence or leaked footer")
    }
    print("PASS_V11_FRONT_REAL_GRADE \\(item.grade) \\(count)")
}
print("PASS: five archived real verdicts, all 11 grades, and six actual V11 ~150–200-char source summaries; no scoring change")
'''
    with tempfile.TemporaryDirectory(prefix="wengua-verdict-") as tmp:
        base=Path(tmp)
        source=base/"main.swift"
        source.write_text("\n".join(parts)+"\n"+main,encoding="utf-8")
        fixtures=base/"real_v102_cases.json"
        fixtures.write_text(json.dumps(native_sections(),ensure_ascii=False),encoding="utf-8")
        v11_fixtures=base/"real_v11_six_cases.json"
        v11_fixtures.write_text(json.dumps(v11_actual_sections(),ensure_ascii=False),encoding="utf-8")
        binary=base/"grade_ui_check"
        subprocess.run(["swiftc",str(source),"-o",str(binary)],check=True)
        subprocess.run([str(binary),str(fixtures),str(v11_fixtures)],check=True)
if __name__=="__main__":check()
