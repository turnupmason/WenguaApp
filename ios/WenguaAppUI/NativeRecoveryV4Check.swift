import Foundation
@main struct NativeRecoveryV4Check {
    struct Case:Decodable {
        let id:String;let iso:String;let timezone:String;let relationship:String;let context:String
        let patient_sex:String?;let patient_birth_ganzhi:String?;let source_replay:Bool?
    }
    struct Fixture:Decodable {let cases:[Case]}
    struct Output:Encodable {let id:String;let result:WenguaV4Result;let replay:WenguaV4Replay?}
    static func main()throws {
        let args=CommandLine.arguments
        if args.count==3 && args[1]=="--bundle" {
            guard let bundle=Bundle(path:args[2]) else {throw WenguaRecoveryError.invalidFacts}
            for iso in ["2026-11-10T04:00:00-05:00","2026-10-27T05:00:00-04:00"] {
                let chart=try WenguaNativeCore.compute(at:WenguaNativeRecovery.parse(iso),timezone:"America/New_York")
                let r=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"health.recovery",relationship:"本人",bundle:bundle)
                guard r.version=="health.recovery.V4",r.sections.count==4,
                      !r.sections.map({$0.text}).joined().contains("America"),r.recoveryWindows?.count==1 else {throw WenguaRecoveryError.invalidFacts}
                let saved=try JSONEncoder().encode(r),loaded=try JSONDecoder().decode(WenguaNativeCustomerReading.self,from:saved)
                guard r.sections.map({$0.text})==loaded.sections.map({$0.text}) else {throw WenguaRecoveryError.invalidFacts}
                print("RECOVERY_V4_BUNDLE_HISTORY_PASS",r.sections[0].text)
            }
            return
        }
        guard args.count==7 else {throw WenguaRecoveryError.invalidFacts}
        let runtime=try WenguaV4Runtime.fromData(Data(contentsOf:URL(fileURLWithPath:args[1])))
        let shared=try WenguaRecoveryRuntime.fromData(Data(contentsOf:URL(fileURLWithPath:args[2])))
        let energy=try WenguaNativeEnergyBundle.fromData(Data(contentsOf:URL(fileURLWithPath:args[3])))
        let source=try WenguaNativeActorSource.fromData(Data(contentsOf:URL(fileURLWithPath:args[4])))
        let pairs=try String(contentsOfFile:args[5],encoding:.utf8)
        let fixture=try JSONDecoder().decode(Fixture.self,from:Data(contentsOf:URL(fileURLWithPath:args[6])))
        for item in fixture.cases {
            fputs("RECOVERY_V4_CASE "+item.id+"\n",stderr)
            let chart=try WenguaNativeCore.compute(at:WenguaNativeRecovery.parse(item.iso),timezone:item.timezone)
            let inquiry=WenguaNativeInquiry(relationship:item.relationship,context:item.context,
                patientSex:item.patient_sex,birthOrder:nil,patientBirthGanzhi:item.patient_birth_ganzhi)
            let actor=try WenguaNativeActorSource.bind(chart:chart,inquiry:inquiry,index:source)
            let audit=try WenguaVNextEngine.compute(chart:chart,relationship:item.relationship,energy:energy,catalog:pairs,actor:actor)
            let facts=try WenguaNativeRecovery.facts(chart:chart,audit:audit,actor:actor)
            let context=try WenguaRecoveryConvergence.context(chart:chart,audit:audit,actor:actor)
            let result=try WenguaRecoveryConvergence.analyze(facts,context,runtime,shared)
            let replay:WenguaV4Replay?
            if item.source_replay==true {replay=try WenguaRecoveryConvergence.replaySource(facts,context,shared)} else {replay=nil}
            let output=try JSONEncoder().encode(Output(id:item.id,result:result,replay:replay))
            print(String(data:output,encoding:.utf8)!)
        }
    }
}
