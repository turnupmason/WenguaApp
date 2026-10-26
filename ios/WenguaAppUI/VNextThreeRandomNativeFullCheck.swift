import Foundation

private struct RoleScore:Decodable {
    let palace:Int
    let components:ScoreComponents
    let raw:Int?
    let score:Int?
    let void:String
}
private struct ScoreComponents:Decodable {
    let star:Int?
    let door:Int?
    let deity:Int?
    let pattern:Int
}
private struct FiveControl:Decodable {
    let direction:String
    let cell:String?
    let scenario:String?
}
private struct ResultSummary:Decodable {
    let score:Int?
    let post_void_known_sum:Int
}
private struct Auxiliary:Decodable {let palace:Int;let score:Int?}
private struct TianruiSource25:Decodable {
    let category:String
    let star_month:String
    let palace_month:String
    let traditional_title:String
    let effectiveness:String
    let eligible_evidence_direction:String
}
private struct TestCast:Decodable {
    let instant:String
    let relationship:String
    let patient_sex:String?
    let context:String
    let firstStage:Bool
    let tianrui25:TianruiSource25
    let summary:ResultSummary
    let roles:[String:RoleScore]
    let auxiliaries:[String:Auxiliary]
    let controls:[String:FiveControl]
    let evidenceDirection:String
}
private struct TestSet:Decodable {
    let seed:Int
    let cases:[TestCast]
}
private struct PublicCast:Encodable {
    let ordinal:Int
    let instant:String
    let relationship:String
    let pillars:[String]
    let solar_term:String
    let bureau:String
    let section_count:Int
    let source_direction:String
    let evidence_conflict:Bool
    let sections:[WenguaNativeCustomerSection]
}
@main struct VNextThreeRandomNativeFullCheck {
    static func main() throws {
        guard CommandLine.arguments.count==5 else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let fixture=try JSONDecoder().decode(TestSet.self,
            from:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
        let pairs=try String(contentsOfFile:CommandLine.arguments[2],encoding:.utf8)
        let energy=try WenguaNativeEnergyBundle.fromData(
            Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[3])))
        let template=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[4]))
        let actors=try WenguaNativeActorSource.fromData(
            Data(contentsOf:URL(fileURLWithPath:
            "data/knowledge/phrase_library/health_v20/actor_profiles.json")))
        let time=ISO8601DateFormatter()
        time.formatOptions=[.withInternetDateTime]
        let encoder=JSONEncoder()
        encoder.outputFormatting=[.sortedKeys]
        func require(_ condition:Bool,_ problem:String) throws {
            guard condition else {throw NSError(domain:"WenguaThreeFreshSourceParity",
                code:1,userInfo:[NSLocalizedDescriptionKey:problem])}
        }
        try require(fixture.cases.count==3,"expected 3 actual clocks")
        var times:Set<String>=[]
        for (i,test) in fixture.cases.enumerated() {
            guard let d=time.date(from:test.instant) else {
                throw WenguaCastError.invalidChart
            }
            try require(times.insert(test.instant).inserted,"duplicate clock")
            let chart=try WenguaNativeCore.compute(
                at:d,timezone:"America/New_York")
            let request=WenguaNativeInquiry(relationship:test.relationship,
                context:test.context,patientSex:test.patient_sex,
                birthOrder:nil,patientBirthGanzhi:nil)
            let actor=try WenguaNativeActorSource.bind(chart:chart,
                inquiry:request,index:actors)
            let audit=try WenguaVNextEngine.compute(chart:chart,
                relationship:test.relationship,energy:energy,
                catalog:pairs,actor:actor)
            let star25=try WenguaVNextTianrui25.caseFor(
                chart:chart,audit:audit)
            try require(star25.category==test.tianrui25.category,
                test.instant+" Tianrui-25 category")
            try require(star25.starMonth==test.tianrui25.star_month &&
                        star25.palaceMonth==test.tianrui25.palace_month,
                test.instant+" nine-star versus landing-palace month")
            try require(star25.title==test.tianrui25.traditional_title,
                test.instant+" exact user-proposed 25-case imagery")
            try require(star25.effectiveness==test.tianrui25.effectiveness,
                test.instant+" original 25-case applicability restriction")
            try require(star25.eligibleDirection==
                        test.tianrui25.eligible_evidence_direction,
                test.instant+" original 25-case eligible symbol only")
            let loc=test.instant+" ["+test.relationship+"] "
            try require(audit.firstMacroFiveNot==test.firstStage,loc+"five-not")
            try require(audit.score==test.summary.score,loc+"final score Swift "+String(describing:audit.score)+" Python "+String(describing:test.summary.score))
            try require(audit.postVoidKnownSum==test.summary.post_void_known_sum,
                loc+"real palace dedup + void three")
            for (name,expected) in test.roles {
                guard let p=audit.roles[name],let r=audit.palaces[p] else {
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                try require(p==expected.palace,loc+name+" palace")
                try require(r.star==expected.components.star,loc+name+" star 25")
                try require(r.door==expected.components.door,loc+name+" door 25")
                try require(r.deity==expected.components.deity,loc+name+" god no month")
                try require(r.pattern==expected.components.pattern,
                    loc+name+" 81+12stage+tomb+strike")
                try require(r.raw==expected.raw,loc+name+" four source factors")
                try require(r.afterVoid==expected.score,
                    loc+name+" door break/five-not/void")
                try require(r.void==expected.void,loc+name+" true/fake void")
            }
            for (name,expected) in test.auxiliaries {
                guard let p=audit.roles[name],let r=audit.palaces[p] else {
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                try require(p==expected.palace &&
                    r.afterVoid==expected.score,loc+name+" qian/kun dedup")
            }
            try require(audit.evidenceDirection==test.evidenceDirection,
                loc+"qualitative disease evidence priority Swift="+audit.evidenceDirection+" Python="+test.evidenceDirection)
            for (name,expected) in test.controls {
                guard let actual=audit.controls.first(where:{$0.role==name}) else{
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                try require(actual.direction==expected.direction,loc+name+" 5x5 direction")
                try require(actual.cell==expected.cell,loc+name+" actual control cell")
                try require(actual.scenario==expected.scenario,
                    loc+name+" true/fake source-target choice")
            }
            let reading=try WenguaNativeReadingRouter.compose(
                chart:chart,topicID:"health.severity",relationship:test.relationship,
                template:template,catalog:pairs,energy:energy,actor:actor)
            let joined=reading.sections.map{$0.text}.joined(separator:"\n")
            for forbidden in ["raw_sum","known_subtotal","净分","五档",
                "原始净分","±5","source_sha256","候选五档"] {
                try require(!joined.contains(forbidden),
                   loc+"internal numerical data leaked "+forbidden)
            }
            let conclusion=reading.sections.first(where:{$0.id=="90vnext"})?.text ?? ""
            let detailed=reading.sections.first(where:{$0.id=="87vnext"})?.text ?? ""
            let overview=reading.sections.first(where:{$0.id=="82vnext"})?.text ?? ""
            let controls=reading.sections.first(where:{$0.id=="83vnext"})?.text ?? ""
            try require(!conclusion.isEmpty && conclusion.contains("宫"),
                loc+"score-conditioned conclusion missing")
            try require(overview.contains("月令") && overview.contains("落宫") &&
                        overview.contains("「"+star25.title+"」"),
                loc+"monthly+palace powers absent from consumer reasoning")
            try require(overview.contains("天干十二长生"),
                loc+"81 original pair lifecycle condition lost in narrative")
            try require(detailed.contains("只按落宫") &&
                detailed.contains("不套月令"),
                loc+"God was silently subjected to a monthly rule")
            try require(controls.contains("力量") && controls.contains("病宫"),
                loc+"real person selected 25-cell power/directed relation lost")
            try require(!detailed.contains("净分") && !overview.contains("加分"),
                loc+"private arithmetic leaked into template")
            try require(reading.sections.contains(where:{$0.id=="90vnext"}),
                loc+"current native verdict missing")
            // Developer-only, signed original factor ledger. This STDOUT is
            // archived by CI; NEVER returned as customer section or saved
            // into LocalNativeCase on-device.
            var privatePalaces:[[String:Any]]=[]
            for id in audit.palaces.keys.sorted() {
                guard let row=audit.palaces[id] else{continue}
                privatePalaces.append([
                    "palace":id,"roles":row.roles,
                    "star":row.star as Any? ?? NSNull(),
                    "door":row.door as Any? ?? NSNull(),
                    "god":row.deity as Any? ?? NSNull(),
                    "pattern":row.pattern,
                    "raw":row.raw as Any? ?? NSNull(),
                    "before_void":row.beforeVoid as Any? ?? NSNull(),
                    "after_void":row.afterVoid as Any? ?? NSNull(),
                    "void":row.void,"door_break":row.doorBreak])
            }
            let developer:[String:Any]=[
                "instant":test.instant,"relationship":test.relationship,
                "unique_real_palaces":privatePalaces,
                "post_void_known_sum":audit.postVoidKnownSum,
                "final_private_score":audit.score as Any? ?? NSNull(),
                "direction":audit.evidenceDirection,
                "conflict":audit.evidenceConflict,
                "separation":"DEV_ONLY_NOT_EXPOSED_TO_CUSTOMER_TEMPLATE"
            ]
            let auditData=try JSONSerialization.data(withJSONObject:developer,
                                                      options:[.sortedKeys])
            print("VNEXT_IOS_INTERNAL_DEVELOPER_AUDIT="+
                  String(data:auditData,encoding:.utf8)!)
            let result=PublicCast(
                ordinal:i+1,instant:test.instant,
                relationship:test.relationship,
                pillars:[chart.pillars.year,chart.pillars.month,
                         chart.pillars.day,chart.pillars.hour],
                solar_term:chart.solarTerm,
                bureau:(chart.bureau.dun=="yin" ? "阴遁":"阳遁")+String(chart.bureau.ju)+"局",
                section_count:reading.sections.count,
                source_direction:audit.evidenceDirection,
                evidence_conflict:audit.evidenceConflict,
                sections:reading.sections)
            print("VNEXT_IOS_3_RANDOM="+String(data:try encoder.encode(result),
                                                encoding:.utf8)!)
            print("VNEXT_IOS_RANDOM_PARITY_PASS "+String(i+1)+" "+loc)
        }
        print("VNEXT_IOS_3_RANDOM_ALL_PASSED "+String(fixture.seed))
    }
}
