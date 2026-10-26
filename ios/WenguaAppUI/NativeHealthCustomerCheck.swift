import Foundation
@main
struct NativeHealthCustomerCheck {
    static func main() throws {
        guard CommandLine.arguments.count==4 else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let template=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
        let catalog=try String(contentsOfFile:CommandLine.arguments[2],encoding:.utf8)
        let energy=try WenguaNativeEnergyBundle.fromData(
            Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[3])))
        let iso=ISO8601DateFormatter()
        iso.formatOptions=[.withInternetDateTime]
        guard let date=iso.date(from:"2026-11-01T05:00:00-05:00") else {
            throw WenguaCastError.invalidChart
        }
        let chart=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
        let reading=try WenguaNativeReadingRouter.compose(
            chart:chart,topicID:"health.severity",relationship:"本人",
            template:template,catalog:catalog,energy:energy)
        guard reading.sections.count==9,
              reading.sections[0].id=="01_macro",
              reading.sections[0].text.contains("五不遇"),
              reading.sections.contains(where:{$0.id=="02" && $0.text.contains("天芮星")}),
              reading.sections.contains(where:{$0.id=="03" && $0.text.contains("天地格：")}),
              !reading.sections.contains(where:{$0.id=="08"}),
              !reading.sections.contains(where:{$0.id=="09_qian"}),
              !reading.sections.contains(where:{$0.id=="09_kun"}),
              reading.sections.contains(where:{$0.id=="90_review"}),
              reading.sections.contains(where:{$0.id=="91_timing"}),
              !reading.sections.map(\.text).joined().contains("净分"),
              !reading.sections.map(\.text).joined().contains("±5"),
              !reading.sections.map(\.text).joined().contains("raw_sum") else {
            throw WenguaNativeReadingError.invalidPhrase
        }
        do {
            _=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"marriage.0",
                relationship:"本人",template:template,catalog:catalog)
            throw WenguaNativeReadingError.invalidPhrase
        } catch WenguaNativeReadingError.unsupportedTopic {}
        do {
            _=try WenguaNativeReadingRouter.compose(chart:chart,topicID:"health.severity",
                relationship:"姐妹",template:template,catalog:catalog)
            throw WenguaNativeReadingError.invalidPhrase
        } catch WenguaNativeReadingError.unsupportedRelationship {}
        print("NATIVE_CUSTOMER_READING_ROUTED_VALIDATED: "+reading.iso)
    }
}
