import Foundation

@main struct NativeRecoveryCheck {
    struct Case:Decodable {
        let id:String
        let iso:String?
        let timezone:String?
        let relationship:String?
        let context:String?
        let patient_sex:String?
        let family_relative_confirmed:Bool?
        let time_scale:String?
        let deadline_iso:String?
        let facts:WenguaRecoveryFacts?
    }
    struct Fixture:Decodable {let cases:[Case]}
    struct Output:Encodable {
        let id:String
        let facts:WenguaRecoveryFacts
        let result:WenguaRecoveryResult
    }
    static func main() throws {
        let args=CommandLine.arguments
        if args.count==3 && args[1]=="--bundle" {
            guard let bundle=Bundle(path:args[2]) else {throw WenguaRecoveryError.invalidFacts}
            for (person,iso) in [("本人","2026-10-27T05:00:00-04:00"),("父亲","2026-11-10T04:00:00-05:00")] {
                let chart=try WenguaNativeCore.compute(at:WenguaNativeRecovery.parse(iso),timezone:"America/New_York")
                let reading=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"health.recovery",relationship:person,bundle:bundle)
                guard reading.topicID=="health.recovery",reading.version=="health.recovery.V3",reading.sections.count==4,
                      reading.recoveryState != nil,reading.rolePalaces?["patient"] != nil,
                      reading.resolvedHealthGrade==nil,reading.timingGrade==nil else {throw WenguaRecoveryError.invalidFacts}
                let saved=try JSONEncoder().encode(reading)
                let reopened=try JSONDecoder().decode(WenguaNativeCustomerReading.self,from:saved)
                guard reopened.sections.map({$0.text})==reading.sections.map({$0.text}),
                      reopened.recoveryState==reading.recoveryState,reopened.recoveryWindows==reading.recoveryWindows else {throw WenguaRecoveryError.invalidFacts}
                print("RECOVERY_BUNDLE_HISTORY_PASS",person,reading.recoveryState!,reading.recoveryWindows?.count ?? 0)
            }
            return
        }
        guard args.count==6 else {throw WenguaRecoveryError.invalidFacts}
        let runtime=try WenguaRecoveryRuntime.fromData(Data(contentsOf:URL(fileURLWithPath:args[1])))
        let energy=try WenguaNativeEnergyBundle.fromData(Data(contentsOf:URL(fileURLWithPath:args[2])))
        let source=try WenguaNativeActorSource.fromData(Data(contentsOf:URL(fileURLWithPath:args[3])))
        let pairs=try String(contentsOfFile:args[4],encoding:.utf8)
        let fixture=try JSONDecoder().decode(Fixture.self,from:Data(contentsOf:URL(fileURLWithPath:args[5])))
        for item in fixture.cases {
            let facts:WenguaRecoveryFacts
            if let supplied=item.facts {facts=supplied}
            else {
                guard let iso=item.iso,let zone=item.timezone,let who=item.relationship else {throw WenguaRecoveryError.invalidFacts}
                let chart=try WenguaNativeCore.compute(at:WenguaNativeRecovery.parse(iso),timezone:zone)
                let inquiry=WenguaNativeInquiry(relationship:who,context:item.context ?? (who=="本人" ? "direct_self":"direct_proxy"),
                    patientSex:item.patient_sex,birthOrder:nil,patientBirthGanzhi:nil,
                    familyRelativeConfirmed:item.family_relative_confirmed)
                let actor=try WenguaNativeActorSource.bind(chart:chart,inquiry:inquiry,index:source)
                let audit=try WenguaVNextEngine.compute(chart:chart,relationship:who,energy:energy,catalog:pairs,actor:actor)
                facts=try WenguaNativeRecovery.facts(chart:chart,audit:audit,actor:actor)
            }
            let result=try WenguaNativeRecovery.analyze(facts,runtime:runtime,timeScale:item.time_scale,deadline:item.deadline_iso)
            let data=try JSONEncoder().encode(Output(id:item.id,facts:facts,result:result))
            print(String(data:data,encoding:.utf8)!)
        }
    }
}
