"""Apply an editorial-only first-page change; never change frozen V8 rules."""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"ios/WenguaAppUI"
P=UI/"WenguaPremiumReadingView.swift"
D=UI/"WenguaNativeCustomerView.swift"
rows={
"极大吉":("有利线索较集中","有利条件较多，但不代表现实已经康复。"),
"大吉":("可见较明显的转机","盘中的帮助较为相合，仍须核实条件。"),
"中吉":("有改善的线索","吉象与牵制并见，还需观察。"),
"小吉":("有些值得留意的转机","仍有未解的阻碍，不能视为万事已定。"),
"极小吉":("吉象初显，尚有牵绊","有利线索尚浅，不宜过早断定。"),
"极小凶":("局部仍见阻滞","传统象意不能用于判定现实只是小病。"),
"小凶":("已有一些需要留意的阻力","不利条件显现，扶助是否奏效尚待核实。"),
"中凶":("阻力较明显，转机尚未稳固","诸宫相互牵制，不能凭单一吉象断言见效。"),
"大凶":("不利线索较多，宜审慎看待","阻碍较集中，已有的扶助未必足以解局。"),
"极大凶":("不利迹象集中，尚难言转机","有制约与帮助的线索，但多项条件受限，不宜轻断局势已经转好。"),
"不凶不吉":("吉凶线索互有牵制","传统盘象尚不能明确判断趋向，不代表现实健康无忧。")
}
p=P.read_text()
if "struct WenguaNaturalSeveritySummary {" not in p:
    anchor="// UI-only labels, projected from the exact V8 role binding"
    assert anchor in p
    clauses="\n".join(
        '        case "'+key+'": return ("'+head+'","'+desc+'")'
        for key,(head,desc) in rows.items())
    s='''// Audience language only. V8 grade and score remain frozen private inputs.
struct WenguaNaturalSeveritySummary {
    static func text(_ grade:String)->(String,String)? {
        switch grade {
'''+clauses+'''
        default: return nil
        }
    }
}

'''
    p=p.replace(anchor,s+anchor)
    old='Text((grade=="不凶不吉" ? "" : grade+"：") + caption.epithet)'
    assert old in p
    p=p.replace(old,'Text(WenguaNaturalSeveritySummary.text(grade)?.0 ?? caption.epithet)')
    p=p.replace('Text(caption.interpretation)',
                'Text(WenguaNaturalSeveritySummary.text(grade)?.1 ?? caption.interpretation)')
    p=p.replace('Text(caption.category)','Text("传统盘象解读")')
    p=p.replace('.accessibilityLabel("传统古籍等级：" + grade)','')
    P.write_text(p)
d=D.read_text()
before="据本次真实九宫，逐层呈现古籍条件、用神落宫、吉凶及应期依据。"
after="逐项保留九宫、人物用神、星门神干、天地格、空墓刑迫与应期依据；首页摘要不代替详细原文。"
if before in d:D.write_text(d.replace(before,after))
assert "WenguaNaturalSeveritySummary.text(grade)" in P.read_text()
for file in (P,D):
    snap=ROOT/"Important/swift/ui"/file.name
    snap.write_bytes(file.read_bytes())
catalog=ROOT/"Important/MANIFEST.json"
data=json.loads(catalog.read_text())
for file in (P,D):
    item=[i for i in data["entries"] if i["canonical"]=="ios/WenguaAppUI/"+file.name]
    assert len(item)==1
    b=file.read_bytes()
    item[0]["sha"]=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\\0"+b).hexdigest()
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
for dest in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
    file=ROOT/dest
    note="\n2026-10-29 首屏语言研究：冻结V8等级仍作内部匹配，不直接面向用户展示「极大凶」字样。SwiftUI改用无医学预后承诺的自然文字；第二页完整V10.2原始细断一字不删。Important两镜像及MANIFEST哈希同步。纯九宫对照只读取 docs/HEALTH_TWO_CLOCKS_RAW_NINE_ONLY_20261029.json；不算独立盲测，详见 docs/HEALTH_FIRSTPAGE_STYLE_GUIDE_20261029.md。\n"
    if note not in file.read_text():
        with file.open("a") as f:f.write(note)
print("NATURAL_FIRST_PAGE_SYNCED",len(rows))
