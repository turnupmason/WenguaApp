import Foundation

// Cross-language V19 verification: two freshly sampled native charts and
// their full nine-part Swift reading, plus RAW chart and selected actor only.
// Python independently recomputes 200-cell power, 255 source, 81 formations.
@main struct NativeDiscomfortV19Parity {
    static func main() throws {
        guard CommandLine.arguments.count == 7 else {
            throw NSError(domain:"V19ParityUsage",code:1)
        }
        let args=CommandLine.arguments
        let index=try WenguaNativeActorSource.fromData(
            Data(contentsOf:URL(fileURLWithPath:args[1])))
        let rules=try Data(contentsOf:URL(fileURLWithPath:args[2]))
        let stems=try Data(contentsOf:URL(fileURLWithPath:args[3]))
        let template=try Data(contentsOf:URL(fileURLWithPath:args[4]))
        let energy=try Data(contentsOf:URL(fileURLWithPath:args[5]))
        let pairs=try Data(contentsOf:URL(fileURLWithPath:args[6]))
        let parser=ISO8601DateFormatter()
        parser.formatOptions=[.withInternetDateTime]
        let slots=[1,3,5,7,9,11,13,15,17,19,21]
        let selected:[(String,String,Int,Int,Int,Int)]=[
            ("yin","弟弟",2026,11,Int.random(in:9...23),slots.randomElement()!),
            ("yang","妻子",2027,2,Int.random(in:7...20),slots.randomElement()!)
        ]
        let encoder=JSONEncoder()
        encoder.outputFormatting=[.sortedKeys]
        for (dun,person,year,month,day,hour) in selected {
            let iso=String(format:"%04d-%02d-%02dT%02d:00:00-05:00",
                           year,month,day,hour)
            guard let date=parser.date(from:iso) else {
                throw NSError(domain:"V19ParityClock",code:2)
            }
            let chart=try WenguaNativeCore.compute(
                at:date,timezone:"America/New_York")
            guard chart.bureau.dun==dun else {
                throw NSError(domain:"V19ParityDun",code:3)
            }
            let inquiry=WenguaNativeInquiry(
                relationship:person,context:"direct_proxy",patientSex:nil,
                birthOrder:nil,patientBirthGanzhi:nil,
                familyRelativeConfirmed:person=="弟弟" ? true : nil)
            let actor=try WenguaNativeActorSource.bind(
                chart:chart,inquiry:inquiry,index:index)
            guard (person=="弟弟" && actor.profileID=="younger_brother" &&
                   actor.siblingAuxiliaryPalace==8 &&
                   actor.sourceGanzhi==chart.pillars.month) ||
                  (person=="妻子" && actor.profileID=="wife" &&
                   actor.mainStem=="乙" && actor.siblingAuxiliaryPalace==nil)
            else {throw NSError(domain:"V19ParityActor",code:4)}
            let reading=try WenguaNativeDiscomfortV15.compose(
                chart:chart,relationship:person,actor:actor,
                rules:rules,stems:stems,template:template,
                energy:energy,pairs:pairs)
            guard reading.sections.count==9 else {
                throw NSError(domain:"V19ParitySections",code:5)
            }
            var actorJSON:[String:Any]=[
                "mainStem":actor.mainStem,
                "mainPalace":actor.mainPalace,
                "profileID":actor.profileID,
                "kind":actor.kind
            ]
            if let v=actor.sourceGanzhi {actorJSON["sourceGanzhi"]=v}
            if let v=actor.siblingAuxiliaryPalace {actorJSON["siblingAuxiliaryPalace"]=v}
            if let v=actor.genderPalace {actorJSON["genderPalace"]=v}
            if let v=actor.natalPalace {actorJSON["natalPalace"]=v}
            let doc:[String:Any]=[
                "chart":try JSONSerialization.jsonObject(with:encoder.encode(chart)),
                "actor":actorJSON,
                "reading":try JSONSerialization.jsonObject(with:encoder.encode(reading))
            ]
            let data=try JSONSerialization.data(withJSONObject:doc,options:[.sortedKeys])
            guard let line=String(data:data,encoding:.utf8) else {
                throw NSError(domain:"V19ParityJSON",code:6)
            }
            print(line)
        }
    }
}
