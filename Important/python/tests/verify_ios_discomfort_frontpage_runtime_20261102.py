"""Compile the actual first-card adapter; test screenshot and fresh V27 readings."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/'ios/WenguaAppUI'

def check(native_jsonl=None):
    router=(UI/'WenguaNativeReadingRouter.swift').read_text()
    premium=(UI/'WenguaPremiumReadingView.swift').read_text()
    dto=router[router.index('struct WenguaNativeCustomerSection:'):router.index('enum WenguaNativeReadingError')]
    helper=premium[premium.index('struct WenguaDiscomfortVerdictPresentation {'):premium.index('struct WenguaVerdictPresentation {')]
    # Exercise the real card binding too: correct adapter must be displayed.
    assert 'WenguaDiscomfortVerdictPresentation.from(reading)' in premium
    assert 'Text(verdict.headline)' in premium and 'Text(verdict.details)' in premium
    assert '当前无足够实际盘面依据' not in premium
    readings=[]
    if native_jsonl:
        readings=[json.loads(line)['reading'] for line in Path(native_jsonl).read_text().splitlines() if line.strip()]
        assert len(readings)>=2
    swift=r'''
let screenshot="综上，本人本次病位先看大肠。盘中天禽同宫又逢伏吟，传统取反复牵滞之象，可作旁证；另见坤二宫己主胃，有伤痛或损伤之象，与主病位分开核对。以上为传统病位和症候象意，需以实际检查核实。"
func reading(_ text:String,_ topic:String="health.discomfort",_ key:String="09_conclusion") -> WenguaNativeCustomerReading {
    WenguaNativeCustomerReading(version:"discomfort_v27_ding_gods_inner_outer_hour_20261101",
        topicID:topic,relationship:"本人",iso:"UI_SCREENSHOT_FIXTURE_NOT_A_COMPUTED_CHART",
        evidenceStatus:"screenshot UI regression only",sections:[
            .init(id:"06_conclusion",title:"旧ID陷阱",text:"不能取这个旧字段"),
            .init(id:key,title:"病位结论",text:text)])
}
let input=reading(screenshot)
guard let result=WenguaDiscomfortVerdictPresentation.from(input),
      result.headline=="本次病位先看大肠",
      result.details.contains("坤二宫己主胃，有伤痛或损伤之象"),
      result.conclusion==screenshot,
      input.sections.last!.text==screenshot else {
    fatalError("Screenshot V27 conclusion not displayed on first page")
}
guard WenguaDiscomfortVerdictPresentation.from(reading(" \n"))==nil,
      WenguaDiscomfortVerdictPresentation.from(reading(screenshot,"health.severity"))==nil,
      WenguaDiscomfortVerdictPresentation.from(reading(screenshot,"health.discomfort","old_only"))==nil else {
    fatalError("Missing or wrong-topic V27 conclusion must fail closed")
}
let data=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
let actual=try JSONDecoder().decode([WenguaNativeCustomerReading].self,from:data)
for reading in actual {
    let source=reading.sections.first(where:{$0.id=="09_conclusion"})!.text
    guard let summary=WenguaDiscomfortVerdictPresentation.from(reading),
          !summary.headline.isEmpty,summary.conclusion==source,
          source.hasSuffix(summary.details),
          !summary.headline.contains("当前无足够") else {
        fatalError("Actual native V27 reading lost its first-page summary")
    }
}
print("PASS QIMEN_LUNJI_FRONT_PAGE screenshot, wrong-ID trap, missing/wrong topic, and \(actual.count) actual native V27 readings; stored source unchanged")
'''
    with tempfile.TemporaryDirectory(prefix='wengua-site-front-') as tmp:
        folder=Path(tmp);source=folder/'main.swift';source.write_text('import Foundation\n'+dto+'\n'+helper+'\n'+swift)
        fixtures=folder/'actual_readings.json';fixtures.write_text(json.dumps(readings,ensure_ascii=False))
        binary=folder/'site_front'
        subprocess.run(['swiftc',str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary),str(fixtures)],check=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native-jsonl',type=Path)
    check(p.parse_args().native_jsonl)
