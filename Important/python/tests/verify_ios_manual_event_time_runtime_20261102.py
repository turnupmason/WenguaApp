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
    catalog=app[app.index('struct QuestionTopic:'):app.index('struct WenguaMark:')]
    policy=app[app.index('enum QIssuePolicy {'):app.index('struct LocalNativeCase:')]
    history=(UI/'WenguaLocalHistoryView.swift').read_text()
    store=history[history.index('struct WenguaStoredCase:'):history.index('// Keep List')]
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
    let otherPerson=inputs[(index+1)%inputs.count].reading.relationship
    let otherInquiry=WenguaNativeInquiry(relationship:otherPerson,context:"direct_proxy",
        patientSex:nil,birthOrder:nil,patientBirthGanzhi:nil,
        familyRelativeConfirmed:otherPerson=="哥哥" ? true : nil)
    let otherHealth=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"health.severity",
        relationship:otherPerson,inquiry:otherInquiry,bundle:bundle)
    let wrongPerson=WenguaCastTimePlan.annotate(original,mode:.plannedEvent,timezone:zone,
        confirmedAt:confirmed,groupID:"WRONG_PERSON",index:index,eventKind:"",healthReference:otherHealth)
    guard wrongPerson.timingGrade==nil else {fatalError("Different person's grade copied onto this patient")}
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
// p6: enforce the selected topic's clock mode at the native boundary.
var civil=WenguaScheduledClock(date:confirmed,timezone:zone)
civil.year=2028;civil.month=2;civil.day=29;civil.hour=12;civil.minute=34
guard civil.daysInMonth(timezone:zone)==29,
      try civil.instants(timezone:zone).count==1 else {fatalError("Leap day selection invalid")}
civil.day=30
rejects {_ = try civil.instants(timezone:zone)}
civil.year=2026;civil.month=3;civil.day=8;civil.hour=2;civil.minute=30
rejects {_ = try civil.instants(timezone:zone)}
civil.month=11;civil.day=1;civil.hour=1
let fold=try civil.instants(timezone:zone)
guard fold==repeated else {fatalError("Five-column civil wheel lost DST repeated choices")}
rejects {_ = try civil.instants(timezone:"Invalid/Zone")}
// Catalog gates retain all 15 ordinary routes and their separate elective routes.
guard QuestionCatalog.domains.count==15 else {fatalError("Domain catalog lost a domain")}
for domain in QuestionCatalog.domains {
    let elective=domain.topics.filter(\.isElective)
    guard elective.count==1,elective[0].canCast,
          elective[0].contract?.acceptsPlannedTime==true,
          elective[0].contract?.acceptsCurrentTime==false,
          elective[0].contract?.gradeScope==nil else {
        fatalError("Each domain needs an independent future-only elective route")
    }
    let future=try WenguaCastTimePlan.resolveForTopic(elective[0].id,mode:.plannedEvent,
        candidates:[dates[0]],confirmedAt:confirmed,timezone:zone)
    guard future==[dates[0]] else {fatalError("Elective event clock replaced by now")}
    rejects {_ = try WenguaCastTimePlan.resolveForTopic(elective[0].id,mode:.currentInquiry,
        candidates:[],confirmedAt:confirmed,timezone:zone)}
    rejects {_ = try WenguaCastTimePlan.resolveForTopic(elective[0].id,mode:.plannedEvent,
        candidates:[confirmed],confirmedAt:confirmed,timezone:zone)}
    let electiveReading=WenguaCastTimePlan.chartOnlyReading(chart:inputs[0].chart,
        eventKind:elective[0].title,topicID:elective[0].id)
    let electiveResult=WenguaCastTimePlan.annotate(electiveReading,mode:.plannedEvent,
        timezone:zone,confirmedAt:confirmed,groupID:"ELECTIVE",index:0,eventKind:elective[0].title)
    guard electiveResult.timingGrade==nil,electiveResult.rolePalaces==nil else {
        fatalError("Unfinished elective grading inherited medical scoring")
    }
    for topic in domain.topics where !topic.isElective {
        guard topic.canCast,topic.contract?.acceptsCurrentTime==true,
              topic.contract?.acceptsPlannedTime==false else {fatalError("Ordinary route is not current-only")}
        let now=try WenguaCastTimePlan.resolveForTopic(topic.id,mode:.currentInquiry,
            candidates:[dates[0]],confirmedAt:confirmed,timezone:zone)
        guard now==[confirmed] else {fatalError("Ordinary question did not use confirmation instant")}
        rejects {_ = try WenguaCastTimePlan.resolveForTopic(topic.id,mode:.plannedEvent,
            candidates:[dates[0]],confirmedAt:confirmed,timezone:zone)}
        if topic.contract?.interpretationReady != true {
            let reading=WenguaCastTimePlan.chartOnlyReading(chart:inputs[0].chart,eventKind:topic.title,topicID:topic.id)
            let projected=WenguaCastTimePlan.annotate(reading,mode:.currentInquiry,timezone:zone,
                confirmedAt:confirmed,groupID:"DOMAIN",index:0,eventKind:topic.title)
            guard projected.topicID==topic.id,projected.timingGrade==nil,
                  projected.rolePalaces==nil else {fatalError("Unready domain inherited medical rules")}
        }
    }
}
guard WenguaGradeScale.label(forFinalNetScore:5)=="极大吉",
      WenguaGradeScale.label(forFinalNetScore:0)=="不凶不吉",
      WenguaGradeScale.label(forFinalNetScore:-5)=="极大凶",
      WenguaGradeScale.label(forFinalNetScore:6)==nil else {fatalError("Common final net scale invalid")}
for input in inputs {
    for section in input.reading.sections {
        let layout=WenguaReadingLayout.blocks(section.text,sectionID:section.id)
        guard layout.flatMap(\.runs).joined()==section.text else {fatalError("Reading layout altered source characters")}
        if section.id=="01_location" {
            guard layout.count>1,layout.flatMap(\.runs).count>5 else {fatalError("Still a single wall of text")}
        }
    }
}
// Execute every real injury branch, preserving every character while grouping
// short clauses into readable paragraphs with explicit section headings.
var injuryChecks=0
for input in inputs {
    let person=input.reading.relationship
    for injury in ["none","accident","bone","bleeding","severe_pain","surgery"] {
        let inquiry=WenguaNativeInquiry(relationship:person,context:"direct_proxy",
            patientSex:nil,birthOrder:nil,patientBirthGanzhi:nil,injuryContext:injury,
            familyRelativeConfirmed:person=="哥哥" ? true : nil)
        let actual=try WenguaNativeReadingRouter.compose(chart:input.chart,topicID:"health.discomfort",
            relationship:person,inquiry:inquiry,bundle:bundle)
        for section in actual.sections {
            let layout=WenguaReadingLayout.blocks(section.text,sectionID:section.id)
            guard layout.flatMap(\.runs).joined()==section.text else {fatalError("Grouped injury source changed")}
            for block in layout {
                guard WenguaReadingLayout.paragraphs(block).joined()==block.runs.joined() else {
                    fatalError("Paragraph joining removed evidence")
                }
            }
            if section.id=="02_injury" {
                guard injury != "none",layout.count>=3,layout.first?.heading=="伤损部位" else {
                    fatalError("Injury evidence still ungrouped")
                }
            }
            if section.id=="09_conclusion" {
                guard layout.count>=2,layout.first?.heading=="主要结论" else {fatalError("Conclusion not grouped")}
            }
        }
        injuryChecks += 1
    }
}
print("PASS SETUP_UI 15 current-only ordinary domains; 15 future-only elective routes; year/month/day/hour/minute leap/gap/fold validation; \(injuryChecks) real injury/layout branches; exact source preserved")
let legacyNow=confirmed.addingTimeInterval(60)
let legacyKey=records[0].issueFingerprint
let encodedOld=try JSONEncoder().encode(records[0])
defaults.set(encodedOld,forKey:"wengua:nativecase:legacy")
defaults.set(confirmed,forKey:"wengua:completed:"+legacyKey)
let structuredKey=QIssuePolicy.structuredSignature(topic:records[0].topicID,relation:records[0].relation,subject:"")
guard QIssuePolicy.nextPermittedIssue(structuredKey,topic:records[0].topicID,
    relation:records[0].relation,asOf:legacyNow,defaults:defaults) != nil else {fatalError("Removing description reset legacy 15-day lock")}
defaults.removeObject(forKey:"wengua:nativecase:legacy")
// Remove the original group too: an orphan receipt still cannot disappear.
for name in defaults.dictionaryRepresentation().keys where name.hasPrefix("wengua:nativecase:") {defaults.removeObject(forKey:name)}
guard QIssuePolicy.nextPermittedIssue(structuredKey,topic:records[0].topicID,
    relation:records[0].relation,asOf:legacyNow,defaults:defaults) != nil else {fatalError("Orphan old receipt silently unlocked")}
let cleanDisplay=WenguaCastTimePlan.display(inputs[0].chart.iso,timezone:zone)
guard !cleanDisplay.contains("-05:00") else {fatalError("Picker offset leaked into human date display")}
print("PASS DOMAIN_UI 15 ordinary current routes; 15 separate elective future routes; common grade scale; exact reading source roundtrip; old receipt locks")
print("PASS MANUAL_EVENT_TIME current vs chosen minute; actual two-clock calendar/9-palace/grade; DST; invalid choices; one atomic group; legacy history; no cross-domain grade")
'''
    names=['WenguaNativeCore','WenguaHealthTemplateBridge','WenguaNativeEnergyBundle',
           'WenguaNativeActorBinding','WenguaNativeReadingRouter','WenguaNativeVNextEngine',
           'WenguaVNextCustomerComposer','WenguaVNextReasoner','WenguaVNextTianrui25',
           'WenguaPythonVNextVerbatim','WenguaNativeDiscomfortV15','WenguaCastTimePlan','WenguaReadingLayout']
    with tempfile.TemporaryDirectory(prefix='wengua-event-time-') as tmp:
        folder=Path(tmp); main=folder/'main.swift'
        main.write_text('import Foundation\nimport CryptoKit\n'+record+'\n'+catalog+'\n'+policy+'\n'+store+'\n'+source)
        binary=folder/'event_time'
        subprocess.run(['swiftc','-warnings-as-errors','-D','WENGUA_BODY_SITE',
            *[str(UI/(name+'.swift')) for name in names],str(main),'-o',str(binary)],check=True)
        executed=subprocess.run([str(binary),str(native_jsonl),str(bundle)],capture_output=True,text=True)
        if executed.returncode:
            print(executed.stdout)
            print(executed.stderr,file=sys.stderr)
            executed.check_returncode()
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
