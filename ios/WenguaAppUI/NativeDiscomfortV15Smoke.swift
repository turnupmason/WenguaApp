import Foundation

// Real offline Swift body-site runtime smoke: two distinct calendar clocks,
// source-exact 255 rules, native chosen patient and yin/yang branch. CLI-only.
@main struct NativeDiscomfortV15Smoke {
    static func main() throws {
        guard CommandLine.arguments.count==5 else {
            throw NSError(domain:"BodySiteV15",code:1,userInfo:[
                NSLocalizedDescriptionKey:"Usage: binary actors.json 255.json three.json template.json"])
        }
        let args=CommandLine.arguments
        let index=try WenguaNativeActorSource.fromData(Data(contentsOf:URL(fileURLWithPath:args[1])))
        let rules=try Data(contentsOf:URL(fileURLWithPath:args[2]))
        let stems=try Data(contentsOf:URL(fileURLWithPath:args[3]))
        let template=try Data(contentsOf:URL(fileURLWithPath:args[4]))
        let parser=ISO8601DateFormatter()
        for (label,instant) in [
            ("yin","2026-10-27T13:00:00-04:00"),
            ("yang","2026-12-27T13:00:00-05:00")
        ] {
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
                rules:rules,stems:stems,template:template)
            guard reading.topicID=="health.discomfort",
                reading.sections.map({$0.id})==[
                    "01_location","02_tianrui","03_comparison",
                    "04_person","05_review","06_conclusion"],
                reading.sections.allSatisfy({ !$0.text.contains("{") &&
                                             !$0.text.contains("}") }),
                reading.sections.last!.text.contains("不能由此判断实际不适"),
                !reading.sections.joinedDescription.contains("极大吉"),
                !reading.sections.joinedDescription.contains("极大凶")
            else {
                throw NSError(domain:"BodySiteV15",code:4,userInfo:[
                    NSLocalizedDescriptionKey:"Body-site customer sections broke the domain and source contract"])
            }
            print("V15_REAL_NATIVE_SITE_PASS "+label+" "+chart.iso+
                  " "+chart.pillars.day+" "+chart.pillars.hour+
                  " illness="+String(reading.rolePalaces?["illness"] ?? -1)+
                  " patient="+String(reading.rolePalaces?["patient"] ?? -1))
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
