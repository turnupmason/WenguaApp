import Foundation

// CLI acceptance only. Real clocks -> native board/actor -> six independent
// conditions. Python receives the board, not precomputed evidence or prose.
@main struct NativeInjuryContextAcceptance {
    static func main() throws {
        guard CommandLine.arguments.count==7 else {throw NSError(domain:"InjuryArgs",code:1)}
        let a=CommandLine.arguments
        let index=try WenguaNativeActorSource.fromData(Data(contentsOf:URL(fileURLWithPath:a[1])))
        let rules=try Data(contentsOf:URL(fileURLWithPath:a[2]))
        let stems=try Data(contentsOf:URL(fileURLWithPath:a[3]))
        let template=try Data(contentsOf:URL(fileURLWithPath:a[4]))
        let energy=try Data(contentsOf:URL(fileURLWithPath:a[5]))
        let pairs=try Data(contentsOf:URL(fileURLWithPath:a[6]))
        let parser=ISO8601DateFormatter()
        let encoder=JSONEncoder()
        let clocks=["2026-11-18T09:00:00-05:00","2026-12-02T21:00:00-05:00",
                    "2026-12-29T09:00:00-05:00","2027-02-07T11:00:00-05:00"]
        let contexts=["none","accident","bone","bleeding","severe_pain","surgery"]
        for iso in clocks {
            let chart=try WenguaNativeCore.compute(at:parser.date(from:iso)!,timezone:"America/New_York")
            let actor=try WenguaNativeActorSource.bind(chart:chart,
                inquiry:WenguaNativeInquiry.standard("丈夫"),index:index)
            let injury=chart.palaces.first(where:{$0.door=="伤门"})!
            for invalid in ["","unspecified","unknown"] {
                var rejected=false
                do {
                    _=try WenguaNativeDiscomfortV15.compose(chart:chart,relationship:"丈夫",actor:actor,
                        injuryContext:invalid,rules:rules,stems:stems,template:template,energy:energy,pairs:pairs)
                } catch {rejected=true}
                guard rejected else {throw NSError(domain:"InjuryMissingChoiceNotBlocked",code:2)}
            }
            for context in contexts {
                let reading=try WenguaNativeDiscomfortV15.compose(chart:chart,relationship:"丈夫",actor:actor,
                    injuryContext:context,rules:rules,stems:stems,template:template,energy:energy,pairs:pairs)
                let activated=context != "none"
                guard reading.sections.first?.id==(activated ? "02_injury":"01_location"),
                      reading.sections.last?.id=="09_conclusion",
                      reading.sections.contains(where:{$0.id=="02_injury"})==activated,
                      (reading.rolePalaces?["injury"] != nil)==activated else {
                    throw NSError(domain:"InjuryGateOrOrder",code:3)
                }
                if activated {
                    guard reading.rolePalaces?["injury"]==injury.id,
                          reading.sections[0].text.contains("伤门力量"),
                          reading.sections[0].text.contains("天盘"),
                          reading.sections[0].text.contains("地盘") else {
                        throw NSError(domain:"InjuryActualPalaceMissing",code:4)
                    }
                }
                var actorJSON:[String:Any]=["mainStem":actor.mainStem,"mainPalace":actor.mainPalace,
                    "profileID":actor.profileID,"kind":actor.kind]
                if let v=actor.sourceGanzhi {actorJSON["sourceGanzhi"]=v}
                let doc:[String:Any]=[
                    "chart":try JSONSerialization.jsonObject(with:encoder.encode(chart)),
                    "actor":actorJSON,"injuryContext":context,
                    "reading":try JSONSerialization.jsonObject(with:encoder.encode(reading))]
                let bytes=try JSONSerialization.data(withJSONObject:doc,options:[.sortedKeys])
                print(String(data:bytes,encoding:.utf8)!)
            }
        }
    }
}
