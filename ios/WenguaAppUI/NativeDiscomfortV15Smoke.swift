import Foundation

// Real offline Swift body-site runtime smoke: two distinct calendar clocks,
// source-exact 255 rules, native chosen patient and yin/yang branch. CLI-only.
@main struct NativeDiscomfortV15Smoke {
    static func main() throws {
        guard CommandLine.arguments.count==7 else {
            throw NSError(domain:"BodySiteV15",code:1,userInfo:[
                NSLocalizedDescriptionKey:"Usage: binary actors.json 255.json three.json template.json 200.json 81.tsv"])
        }
        let args=CommandLine.arguments
        let index=try WenguaNativeActorSource.fromData(Data(contentsOf:URL(fileURLWithPath:args[1])))
        let rules=try Data(contentsOf:URL(fileURLWithPath:args[2]))
        let stems=try Data(contentsOf:URL(fileURLWithPath:args[3]))
        let template=try Data(contentsOf:URL(fileURLWithPath:args[4]))
        let energy=try Data(contentsOf:URL(fileURLWithPath:args[5]))
        let pairs=try Data(contentsOf:URL(fileURLWithPath:args[6]))
        let parser=ISO8601DateFormatter()
        // Randomly draw the calendar day and true two-hour slot, not a
        // handpicked historic clock. Both seasons are deliberately sampled.
        let slots=[1,3,5,7,9,11,13,15,17,19,21]
        let selected:[(String,String,Int,Int,Int,Int)]=[
            ("yin","父亲",2026,11,Int.random(in:9...23),slots.randomElement()!),
            ("yang","姐姐",2027,2,Int.random(in:7...20),slots.randomElement()!),
            ("yin","弟弟",2026,11,Int.random(in:9...23),slots.randomElement()!),
            ("yang","妻子",2027,2,Int.random(in:7...20),slots.randomElement()!)
        ]
        for (label,relationship,year,month,day,hour) in selected {
            let instant=String(format:"%04d-%02d-%02dT%02d:00:00-05:00",
                               year,month,day,hour)
            print("V18_RANDOM_SELECTED "+relationship+" "+label+" "+instant)
            guard let date=parser.date(from:instant) else {
                throw NSError(domain:"BodySiteV15",code:2)
            }
            let chart=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
            guard chart.bureau.dun==label else {
                throw NSError(domain:"BodySiteV15",code:3,userInfo:[
                    NSLocalizedDescriptionKey:"Unexpected actual yin/yang branch: "+chart.bureau.dun])
            }
            let actor=try WenguaNativeActorSource.bind(
                chart:chart,inquiry:WenguaNativeInquiry(
                     relationship:relationship,context:"direct_proxy",
                     patientSex:nil,birthOrder:relationship=="姐姐" ? "eldest" : nil,
                     patientBirthGanzhi:nil,
                     familyRelativeConfirmed:["姐姐","弟弟"].contains(relationship) ? true : nil),index:index)
            let injuryContext=[
                "父亲":"accident","姐姐":"severe_pain",
                "弟弟":"none","妻子":"surgery"][relationship]!
            let reading=try WenguaNativeDiscomfortV15.compose(
                chart:chart,relationship:relationship,actor:actor,
                injuryContext:injuryContext,rules:rules,stems:stems,template:template,
                energy:energy,pairs:pairs)
            guard actor.profileID==(["父亲":"father","姐姐":"older_sister","弟弟":"younger_brother","妻子":"wife"][relationship] ?? ""),
                actor.natalStem==nil,
                relationship != "父亲" || actor.genderPalace==6,
                relationship != "姐姐" || actor.siblingAuxiliaryPalace==4,
                relationship != "弟弟" || actor.siblingAuxiliaryPalace==8,
                relationship != "妻子" || (actor.mainStem=="乙" && actor.siblingAuxiliaryPalace==nil)
            else { throw NSError(domain:"SiteV18Binding",code:5) }
            // Print every actual source sentence before validation, so a
            // failed random branch remains auditable rather than disappearing.
            for section in reading.sections {
                print("V18_DIAGNOSTIC_"+relationship+"_"+section.id+" "+section.text)
            }
            if !reading.sections.last!.text.contains("不是") && !reading.sections.last!.text.contains("不等于") {
                print("V18_GUARD_FAILURE ending")
            }
            if reading.sections.joinedDescription.contains("原书") {
                print("V18_GUARD_FAILURE source_name")
            }
            let ids=reading.sections.map{ $0.id }
            let allowed=["01_location","02_injury","03_assist_doors",
                          "04_hour","05_person","06_auxiliary",
                          "07_formation","08_constraints","09_conclusion"]
            guard reading.topicID=="health.discomfort",
                ids.count>=2,
                ids.first=="01_location",ids.last=="09_conclusion",
                ids.contains("02_injury")==(injuryContext != "none"),
                (reading.rolePalaces?["injury"] != nil)==(injuryContext != "none"),
                Set(ids).count==ids.count,
                ids==allowed.filter{ids.contains($0)},
                reading.sections.allSatisfy({ !$0.text.contains("{") &&
                                             !$0.text.contains("}") }),
                reading.sections.last!.text.contains("不等于医学诊断"),
                !reading.sections.joinedDescription.contains("极大吉"),
                !reading.sections.joinedDescription.contains("极大凶"),
                !reading.sections.joinedDescription.contains("《"),
                !reading.sections.joinedDescription.contains("原书"),
                !reading.sections.joinedDescription.contains("异文"),
                reading.sections.joinedDescription.contains("病位先看") || reading.sections.joinedDescription.contains("伤门落宫"),
                reading.sections.joinedDescription.contains("综上"),
                !reading.sections.joinedDescription.contains("干力"),
                !reading.sections.joinedDescription.contains("病星力量"),
                !reading.sections.joinedDescription.contains("门力"),
                !reading.sections.joinedDescription.contains("断定骨折"),
                !reading.sections.joinedDescription.contains("吉凶"),
                !reading.sections.joinedDescription.contains("极小")
            else {
                throw NSError(domain:"BodySiteV15",code:4,userInfo:[
                    NSLocalizedDescriptionKey:"Body-site customer sections broke the domain and source contract"])
            }
            if injuryContext=="none" && reading.sections.joinedDescription.contains("伤门") {
                throw NSError(domain:"UnexpectedInjuryEvidence",code:8)
            }
            let fields = [
                "V18_NATIVE_SITE_PASS", relationship, label, chart.iso,
                chart.pillars.day, chart.pillars.hour,
                "illness="+String(reading.rolePalaces?["illness"] ?? -1),
                "patient="+String(reading.rolePalaces?["patient"] ?? -1),
                "role="+actor.profileID,
                "actorStem="+actor.mainStem,
                "sourcePillar="+(actor.sourceGanzhi ?? "")
            ]
            print(fields.joined(separator:" "))
            for section in reading.sections {
                print(section.title+"："+section.text)
            }
        }
    }
}
private extension Array where Element==WenguaNativeCustomerSection {
    var joinedDescription:String {
        self.map(\.text).joined(separator:"\n")
    }
}
