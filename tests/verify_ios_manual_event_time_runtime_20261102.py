"""Execute real time selection, both sealed routers and atomic grouped storage.

Runs on macOS against the just-built actual App bundle. No replacement rules
or hand-selected good charts: both input clocks are the retained V27 regressions.
"""
import argparse
import json
import sys
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/'ios/WenguaAppUI'

def check(native_jsonl, bundle):
    app=(UI/'WenguaDesignPreviewApp.swift').read_text()
    record=app[app.index('struct LocalNativeCase: Codable {'):app.index('struct CastSetupScreen: View {')]
    source=r'''
struct Input: Decodable { let chart: WenguaNativeChart; let reading: WenguaNativeCustomerReading }
let data=try String(contentsOfFile:CommandLine.arguments[1],encoding:.utf8)
let inputs=try data.split(separator:"\n").map {try JSONDecoder().decode(Input.self,from:Data($0.utf8))}
guard inputs.count>=2,let bundle=Bundle(path:CommandLine.arguments[2]) else {fatalError("Need actual clocks and built App")}
let parser=ISO8601DateFormatter()
let confirmed=parser.date(from:"2026-11-02T15:00:00Z")!
let dates=inputs.map {parser.date(from:$0.chart.iso)!}
let zone="America/New_York"
let chosen=try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:dates,confirmedAt:confirmed,timezone:zone)
let current=try WenguaCastTimePlan.resolve(mode:.currentInquiry,candidates:dates,confirmedAt:confirmed,timezone:zone)
guard current==[confirmed],chosen==dates else {fatalError("Picker clocks replaced by now or vice versa")}
func rejects(_ action:() throws -> Void) {
    do {try action();fatalError("Invalid time choice was accepted") } catch { }
}
rejects {_ = try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:[],confirmedAt:confirmed,timezone:zone)}
rejects {_ = try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:[confirmed],confirmedAt:confirmed,timezone:zone)}
rejects {_ = try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:[dates[0],dates[0].addingTimeInterval(10)],confirmedAt:confirmed,timezone:zone)}
rejects {_ = try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:dates,confirmedAt:confirmed,timezone:"Invalid/Zone")}
// Repeated local 01:30 during DST is two explicit instants, never collapse or
// silently reconstruct a different wall clock from year/month/day/hour fields.
let repeated=[parser.date(from:"2026-11-01T01:30:00-04:00")!,parser.date(from:"2026-11-01T01:30:00-05:00")!]
let dst=try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:repeated,
    confirmedAt:parser.date(from:"2026-10-25T00:00:00Z")!,timezone:zone)
guard dst[1].timeIntervalSince(dst[0])==3600 else {fatalError("DST fold collapsed")}
var records:[LocalNativeCase]=[]
for (index,input) in inputs.enumerated() {
    let chart=try WenguaNativeCore.compute(at:chosen[index],timezone:zone)
    guard chart==input.chart else {fatalError("Selected event clock did not reproduce its full real chart")}
    let person=input.reading.relationship
    let inquiry=WenguaNativeInquiry(relationship:person,context:"direct_proxy",
        patientSex:nil,birthOrder:nil,patientBirthGanzhi:nil,injuryContext:"none",familyRelativeConfirmed:person=="哥哥" ? true : nil)
    let original=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"health.discomfort",
        relationship:person,inquiry:inquiry,bundle:bundle)
    let health=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"health.severity",
        relationship:person,inquiry:inquiry,bundle:bundle)
    guard let grade=health.resolvedHealthGrade else {fatalError("Missing actual sealed V11 grade")}
    let selected=WenguaCastTimePlan.annotate(original,mode:.plannedEvent,timezone:zone,
        confirmedAt:confirmed,groupID:"ACTUAL_TWO_CLOCK_GROUP",index:index,eventKind:"健康事项",healthReference:health)
    guard selected.timingHeadline=="此时辰："+grade,
          selected.timingReferenceSections?.map({$0.text})==health.sections.map({$0.text}),
          selected.sections.map({$0.text})==input.reading.sections.map({$0.text}),
          selected.sections.map({$0.id})==input.reading.sections.map({$0.id}),
          selected.iso==chart.iso else {fatalError("Time grade not from SAME chart or V27 original changed")}
    let inquiryNow=WenguaCastTimePlan.annotate(original,mode:.currentInquiry,timezone:zone,
        confirmedAt:confirmed,groupID:"CURRENT",index:0,eventKind:"",healthReference:health)
    guard inquiryNow.timingHeadline==nil else {fatalError("Current inquiry incorrectly labeled future timing")}
    let foreignHealth=try WenguaNativeReadingRouter.compose(chart:inputs[(index+1)%inputs.count].chart,
        topicID:"health.severity",relationship:person,inquiry:inquiry,bundle:bundle)
    let rejected=WenguaCastTimePlan.annotate(original,mode:.plannedEvent,timezone:zone,
        confirmedAt:confirmed,groupID:"WRONG_CLOCK",index:index,eventKind:"",healthReference:foreignHealth)
    guard rejected.timingGrade==nil else {fatalError("Unrelated clock or body-location reading donated a grade")}
    for kind in WenguaCastTimePlan.eventKinds {
        let factual=WenguaCastTimePlan.chartOnlyReading(chart:chart,eventKind:kind)
        let ungraded=WenguaCastTimePlan.annotate(factual,mode:.plannedEvent,timezone:zone,
            confirmedAt:confirmed,groupID:"GENERIC",index:index,eventKind:kind,healthReference:health)
        guard ungraded.timingGrade==nil,ungraded.rolePalaces==nil,
              ungraded.timingHeadline=="此时辰：吉凶待核" else {fatalError("Non-health event borrowed disease score")}
    }
    records.append(LocalNativeCase(topicID:original.topicID,issueFingerprint:"HASHED_GROUP_NO_RAW_QUESTION",
        relation:person,optionalBirthYear:nil,course:nil,completedAt:confirmed,chart:chart,reading:selected))
    print("EVENT_TIME_SAME_CHART_GRADE_PASS \(person) \(chart.iso) \(grade)")
    print("EVENT_TIME_HEALTH_JSON="+String(data:try JSONEncoder().encode(health),encoding:.utf8)!)
}
let suite="WenguaTimeAcceptance-"+UUID().uuidString
let defaults=UserDefaults(suiteName:suite)!
defer {defaults.removePersistentDomain(forName:suite)}
try WenguaCaseBatchStore.save(records,defaults:defaults)
let values=defaults.dictionaryRepresentation().filter {$0.key.hasPrefix("wengua:nativecase:")}
guard values.count==1,let saved=values.values.first as? Data else {fatalError("Comparison not stored as one atomic value")}
let decoded=WenguaCaseBatchStore.decode(saved)
guard decoded.count==records.count,decoded.allSatisfy({$0.completedAt==confirmed}),
      decoded[0].reading?.comparisonGroupID==decoded[1].reading?.comparisonGroupID else {
    fatalError("Future event time polluted completion clock or grouped history")
}
let legacy=try JSONEncoder().encode(records[0])
guard WenguaCaseBatchStore.decode(legacy).count==1 else {fatalError("Single-record history migration failed")}
rejects {try WenguaCaseBatchStore.save([],defaults:defaults)}
// Core's late-Zi refusal is preserved: no changing a failed candidate to a
// convenient known-good clock, and no partial group written on failure.
rejects {
    let invalid=parser.date(from:"2026-11-19T23:00:00-05:00")!
    _ = try [dates[0],invalid].map {try WenguaNativeCore.compute(at:$0,timezone:zone)}
}
guard defaults.dictionaryRepresentation().filter({$0.key.hasPrefix("wengua:nativecase:")}).count==1 else {
    fatalError("Failed choice left a partial group")
}
print("PASS MANUAL_EVENT_TIME current vs chosen minute; actual two-clock calendar/9-palace/grade; DST; invalid choices; one atomic group; legacy history; no cross-domain grade")
'''
    names=['WenguaNativeCore','WenguaHealthTemplateBridge','WenguaNativeEnergyBundle',
           'WenguaNativeActorBinding','WenguaNativeReadingRouter','WenguaNativeVNextEngine',
           'WenguaVNextCustomerComposer','WenguaVNextReasoner','WenguaVNextTianrui25',
           'WenguaPythonVNextVerbatim','WenguaNativeDiscomfortV15','WenguaCastTimePlan']
    with tempfile.TemporaryDirectory(prefix='wengua-event-time-') as tmp:
        folder=Path(tmp); main=folder/'main.swift'
        main.write_text('import Foundation\n'+record+'\n'+source)
        binary=folder/'event_time'
        subprocess.run(['swiftc','-warnings-as-errors','-D','WENGUA_BODY_SITE',
            *[str(UI/(name+'.swift')) for name in names],str(main),'-o',str(binary)],check=True)
        executed=subprocess.run([str(binary),str(native_jsonl),str(bundle)],check=True,capture_output=True,text=True)
        sys.path.insert(0,str(ROOT))
        from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
        profiles=json.loads((ROOT/'data/knowledge/phrase_library/health_v20/actor_profiles.json').read_text())['profiles']
        native=[]
        for line in executed.stdout.splitlines():
            if line.startswith('EVENT_TIME_HEALTH_JSON='):
                native.append(json.loads(line.split('=',1)[1]))
            else:
                print(line)
        assert len(native)>=2
        for reading in native:
            person=reading['relationship']
            relation=next(row['id'] for row in profiles if row['label']==person)
            expected=auto_cast_health_review_text(iso=reading['iso'],timezone_name='America/New_York',
                inquiry={'intent':'severity','relationship':relation,'consultation_context':'direct_proxy'})
            assert expected['sections']==reading['sections'], (person,reading['iso'],'manual same-chart health full wording mismatch')
            assert {key:value['palace'] for key,value in expected['full_health_role_strength_network']['nodes'].items()}==reading['rolePalaces']
            print('PASS MANUAL_EVENT_TIME_PYTHON_SWIFT_BYTE_EXACT',person,reading['iso'])

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--native-jsonl',type=Path,required=True)
    p.add_argument('--bundle',type=Path,required=True)
    args=p.parse_args();check(args.native_jsonl,args.bundle)
