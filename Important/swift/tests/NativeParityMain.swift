import Foundation

// Foundation-only golden parity harness. Build on macOS or Linux:
// swiftc ios/WenguaAppUI/WenguaNativeCore.swift ios/WenguaAppUI/NativeParityMain.swift -o /tmp/wengua-native
// /tmp/wengua-native ios/WenguaAppUI/GoldenNativeCastCases.json
// Emits each newly computed actual chart as JSON, NOT mock/fixture copied data.
@main
struct NativeParityMain {
    static func main() {
        do {
            let url: URL
            if CommandLine.arguments.count > 1 {
                url = URL(fileURLWithPath: CommandLine.arguments[1])
            } else {
                throw WenguaCastError.invalidChart
            }
            let fixture = try JSONDecoder().decode(GoldenContainer.self,from: Data(contentsOf:url))
            let formatter=ISO8601DateFormatter()
            formatter.formatOptions=[.withInternetDateTime]
            var outputs=[WenguaNativeChart]()
            for (i,item) in fixture.samples.enumerated() {
                guard let date=formatter.date(from:item.iso) else {throw WenguaCastError.invalidChart}
                let actual=try WenguaNativeCore.compute(at:date,timezone:item.timezone)
                guard actual.pillars == item.pillars,
                      actual.solarTerm == item.solarTerm,
                      actual.bureau == item.bureau,
                      actual.xunShou == item.xunShou,
                      actual.valueStar == item.valueStar,
                      actual.valueDoor == item.valueDoor,
                      actual.voidBranches == item.voidBranches,
                      actual.hourHorse == item.hourHorse else {
                    fputs("Native vs original Python core mismatch at case \(i+1)\n",stderr)
                    exit(3)
                }
                let actualOuter=Dictionary(uniqueKeysWithValues:actual.palaces.map{($0.id,$0)})
                for ref in item.palaces {
                    guard let c=actualOuter[ref.id],
                          c.earthStem==ref.earthStem,
                          c.door==ref.door,
                          c.deity==ref.deity,
                          c.heavenStars==ref.heavenStars else {
                        fputs("Native nine palace discrepancy case \(i+1) palace \(ref.id)\n",stderr)
                        exit(4)
                    }
                }
                guard let center=actualOuter[5],
                      center.door == nil && center.deity == nil &&
                      center.heavenStars.isEmpty &&
                      actual.palaces.count == 9 else {
                    fputs("Center five invalid in native result\n",stderr)
                    exit(5)
                }
                outputs.append(actual)
            }
            let encoder=JSONEncoder()
            encoder.outputFormatting=[.prettyPrinted,.sortedKeys,.withoutEscapingSlashes]
            let data=try encoder.encode(outputs)
            FileHandle.standardOutput.write(data)
        } catch {
            fputs("Wengua source parity failure: \(error)\n",stderr)
            exit(2)
        }
    }
}
private struct GoldenContainer: Codable {
    let samples: [GoldenCase]
}
private struct GoldenCase: Codable {
    let iso: String
    let timezone: String
    let pillars: WenguaNativePillars
    let solarTerm: String
    let bureau: WenguaNativeBureau
    let xunShou: String
    let valueStar: String
    let valueDoor: String
    let voidBranches: [String]
    let hourHorse: String
    let palaces: [GoldenPalace]
}
private struct GoldenPalace: Codable {
    let id: Int
    let earthStem: String
    let door: String
    let deity: String
    let heavenStars: [WenguaNativeStar]
}
