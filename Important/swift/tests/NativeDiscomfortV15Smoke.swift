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
        let selected:[(String,Int,Int,Int,Int)]=[
            ("yin",2026,11,Int.random(in:9...23),slots.randomElement()!),
            ("yang",2027,2,Int.random(in:7...20),slots.randomElement()!)
        ]
        for (label,year,month,day,hour) in selected {
            let instant=String(format:"%04d-%02d-%02dT%02d:00:00-05:00",
                               year,month,day,hour)
            print("V16_RANDOM_SELECTED "+label+" "+instant)
            guard let date=parser.date(from:instant) else {
                throw NSError(domain:"BodySiteV15",code:2)
            }
            let chart=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
            guard chart.bureau.dun==label else {
                throw NSError(domain:"BodySiteV15",code:3,userInfo:[
                    NSLocalizedDescriptionKey:"Unexpected actual yin/yang branch: "+chart.bureau.dun])
            }
            let actor=try WenguaNativeActorSource.bind(
                chart:chart,inquiry:.standard("本人"),index:index)
            let reading=try WenguaNativeDiscomfortV15.compose(
                chart:chart,relationship:"本人",actor:actor,
                rules:rules,stems:stems,template:template,
                energy:energy,pairs:pairs)
            // Print every actual source sentence before validation, so a
            // failed random branch remains auditable rather than disappearing.
            for section in reading.sections {
                print("V17_DIAGNOSTIC_"+section.id+" "+section.text)
            }
            if !reading.sections.last!.text.contains("不等于实际疼痛强度") {
                print("V17_GUARD_FAILURE ending")
            }
            if reading.sections.joinedDescription.contains("原书") {
                print("V17_GUARD_FAILURE source_name")
            }
            guard reading.topicID=="health.discomfort",
                reading.sections.map({$0.id})==[
                    "01_location","02_tianrui","03_comparison",
                    "04_person","05_review","06_conclusion"],
                reading.sections.allSatisfy({ !$0.text.contains("{") &&
                                             !$0.text.contains("}") }),
                reading.sections.last!.text.contains("不等于实际疼痛强度"),
                !reading.sections.joinedDescription.contains("极大吉"),
                !reading.sections.joinedDescription.contains("极大凶"),
                !reading.sections.joinedDescription.contains("《"),
                !reading.sections.joinedDescription.contains("原书"),
                !reading.sections.joinedDescription.contains("异文"),
                reading.sections.joinedDescription.contains("病星本身"),
                reading.sections.joinedDescription.contains("天地格为")
            else {
                throw NSError(domain:"BodySiteV15",code:4,userInfo:[
                    NSLocalizedDescriptionKey:"Body-site customer sections broke the domain and source contract"])
            }
            let fields = [
                "V15_REAL_NATIVE_SITE_PASS", label, chart.iso,
                chart.pillars.day, chart.pillars.hour,
                "illness="+String(reading.rolePalaces?["illness"] ?? -1),
                "patient="+String(reading.rolePalaces?["patient"] ?? -1)
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
