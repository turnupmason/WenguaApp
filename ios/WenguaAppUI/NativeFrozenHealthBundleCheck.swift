import Foundation

// Executes BOTH production bundle router branches against the actual built app.
@main struct NativeFrozenHealthBundleCheck {
    static func main() throws {
        guard CommandLine.arguments.count == 2,
              let bundle = Bundle(path: CommandLine.arguments[1]) else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let parser = ISO8601DateFormatter()
        let cases = [("哥哥", "2026-11-19T11:00:00-05:00"),
                     ("妻子", "2026-12-18T03:00:00-05:00")]
        for (person, iso) in cases {
            let chart = try WenguaNativeCore.compute(at:parser.date(from:iso)!, timezone:"America/New_York")
            for topic in ["health.severity", "health.discomfort"] {
                let inquiry = WenguaNativeInquiry(
                    relationship:person, context:"direct_proxy", patientSex:nil,
                    birthOrder:nil, patientBirthGanzhi:nil,
                    injuryContext:topic == "health.discomfort" ? "none" : nil,
                    familyRelativeConfirmed:person == "哥哥" ? true : nil)
                let reading = try WenguaNativeReadingRouter.compose(
                    chart:chart, topicID:topic, relationship:person,
                    inquiry:inquiry, bundle:bundle)
                let expected = topic == "health.severity"
                    ? "health_severity_v9_scoring_v11_template_frozen_20261102"
                    : "discomfort_v27_ding_gods_inner_outer_hour_20261101"
                guard reading.version == expected, reading.topicID == topic,
                      !reading.sections.isEmpty, reading.rolePalaces?["illness"] != nil else {
                    throw WenguaNativeReadingError.invalidPhrase
                }
                print("SEALED_BUNDLE_ROUTER_PASS", topic, person, expected)
            }
            do {
                _ = try WenguaNativeReadingRouter.compose(
                    chart:chart, topicID:"marriage", relationship:person, bundle:bundle)
                throw WenguaNativeReadingError.invalidPhrase
            } catch WenguaNativeReadingError.unsupportedTopic { }
        }
    }
}
