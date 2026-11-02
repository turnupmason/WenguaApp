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
            ("yang","妻子",2027,2,Int.random(in:7...20),slots.randomElement()!),
            ("yin","妹妹",2026,11,Int.random(in:9...23),slots.randomElement()!),
            ("yang","哥哥",2027,2,Int.random(in:7...20),slots.randomElement()!),
            // Four user-requested V20 independent clocks: original father
            // accident and wife surgery above, plus two ordinary branches.
            ("yin","父亲",2026,11,Int.random(in:9...23),slots.randomElement()!),
            ("yang","女儿",2027,2,Int.random(in:7...20),slots.randomElement()!)
        ]
        for (position, entry) in selected.enumerated() {
            let (label,relationship,year,month,day,hour)=entry
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
                     familyRelativeConfirmed:["哥哥","姐姐","弟弟","妹妹"].contains(relationship) ? true : nil),index:index)
            let injuryContext=position>=6 ? "none" : [
                "父亲":"accident","姐姐":"severe_pain",
                "弟弟":"none","妻子":"surgery",
                "妹妹":"bone","哥哥":"bleeding"][relationship]!
            let reading=try WenguaNativeDiscomfortV15.compose(
                chart:chart,relationship:relationship,actor:actor,
                injuryContext:injuryContext,rules:rules,stems:stems,template:template,
                energy:energy,pairs:pairs)
            guard actor.profileID==(["父亲":"father","姐姐":"older_sister","弟弟":"younger_brother","妻子":"wife",
                 "妹妹":"younger_sister","哥哥":"older_brother","女儿":"daughter"][relationship] ?? ""),
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
            guard reading.sections.last!.text.contains("需以实际检查核实"),
                  !reading.sections.joinedDescription.contains("原书") else {
                throw NSError(domain:"SiteCustomerEvidenceBoundary",code:27)
            }
            let ids=reading.sections.map{ $0.id }
            let allowed=(injuryContext=="none" ? ["01_location"] : ["02_injury","01_location"])+["03_assist_doors",
                          "04_hour","05_person","06_auxiliary",
                          "07_formation","08_constraints","09_conclusion"]
            guard reading.topicID=="health.discomfort",
                ids.count>=2,
                ids.first==(injuryContext=="none" ? "01_location":"02_injury"),ids.last=="09_conclusion",
                ids.contains("02_injury")==(injuryContext != "none"),
                (reading.rolePalaces?["injury"] != nil)==(injuryContext != "none"),
                Set(ids).count==ids.count,
                ids==allowed.filter({ids.contains($0)}),
                reading.sections.allSatisfy({ !$0.text.contains("{") &&
                                             !$0.text.contains("}") }),
                reading.sections.last!.text.contains("需以实际检查核实"),
                !reading.sections.joinedDescription.contains("极大吉"),
                !reading.sections.joinedDescription.contains("极大凶"),
                !reading.sections.joinedDescription.contains("《"),
                !reading.sections.joinedDescription.contains("原书"),
                !reading.sections.joinedDescription.contains("异文"),
                reading.sections.joinedDescription.contains("病位先看") || reading.sections.joinedDescription.contains("伤门落宫"),
                reading.sections.joinedDescription.contains("综上"),
                !reading.sections.joinedDescription.contains("待核"),
                !reading.sections.joinedDescription.contains("（"),
                !reading.sections.joinedDescription.contains("）"),
                !reading.sections.joinedDescription.contains("("),
                !reading.sections.joinedDescription.contains(")"),
                reading.sections.first(where:{$0.id=="01_location"})!.text.contains("天芮星力量"),
                reading.sections.first(where:{$0.id=="01_location"})!.text.contains("天地格"),
                reading.sections.first(where:{$0.id=="01_location"})!.text.contains("天盘"),
                !reading.sections.contains(where:{$0.id=="07_formation" || $0.id=="08_constraints"}),
                !reading.sections.joinedDescription.contains("断定骨折"),
                !reading.sections.joinedDescription.contains("绝对受损"),
                !reading.sections.joinedDescription.contains("医学确认的潜伏疾病"),
                !reading.sections.joinedDescription.contains("确诊病因"),
                !reading.sections.joinedDescription.contains("吉凶"),
                reading.sections.joinedDescription.contains("天地格")
            else {
                let debug="V21_FAIL_GUARD role="+relationship+" ctx="+injuryContext+" ids="+ids.joined(separator:",")+" last="+(reading.sections.last?.text ?? "")+" all="+reading.sections.joinedDescription
                FileHandle.standardError.write(Data(debug.utf8))
                throw NSError(domain:"BodySiteV15",code:4,userInfo:[
                    NSLocalizedDescriptionKey:"Body-site customer sections broke the domain and source contract"])
            }
            // A co-located 伤门 is still a real eight-door fact even when
            // independent injury casting is OFF. Only the independent
            // injury section must remain absent for none.
            if injuryContext=="none" && reading.sections.contains(where:{$0.id=="02_injury"}) {
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
            // User-facing V20 preview: four distinct physical casts,
            // never fabricate a site from a preceding case.
            let previewIDs:[Int:String]=[
                0:"father_accident",3:"wife_surgery",
                6:"father_ordinary",7:"daughter_ordinary"]
            if let previewID=previewIDs[position] {
                print("V20_PREVIEW_BEGIN "+previewID)
                let metaFields=[
                    relationship,injuryContext,chart.iso,
                    chart.pillars.year,chart.pillars.month,
                    chart.pillars.day,chart.pillars.hour,label,
                    "illness="+String(reading.rolePalaces?["illness"] ?? -1),
                    "patient="+String(reading.rolePalaces?["patient"] ?? -1),
                    "person_stem="+actor.mainStem]
                print("V20_PREVIEW_META "+metaFields.joined(separator:" "))
                for section in reading.sections {
                    print(section.title+"："+section.text)
                }
                print("V20_PREVIEW_END "+previewID)
            }
        }
    }
}
private extension Array where Element==WenguaNativeCustomerSection {
    var joinedDescription:String {
        self.map(\.text).joined(separator:"\n")
    }
}
