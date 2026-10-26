import Foundation

// Execute with: swiftc WenguaNativeCore.swift WenguaHealthTemplateBridge.swift
// HealthTemplateBridgeCheck.swift -o /tmp/check && /tmp/check template.json pairs.tsv
@main
struct HealthTemplateBridgeCheck {
    static func main() throws {
        guard CommandLine.arguments.count == 3 else {throw WenguaHealthTemplateError.unavailableResource}
        let template=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
        let catalog=try String(contentsOfFile:CommandLine.arguments[2],encoding:.utf8)
        let iso=ISO8601DateFormatter()
        iso.formatOptions=[.withInternetDateTime]
        var sampleCount=0
        for timestamp in ["2026-11-01T05:00:00-05:00","2026-11-04T05:00:00-05:00"] {
            guard let date=iso.date(from:timestamp) else {throw WenguaCastError.invalidChart}
            let actual=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
            let blocks=try WenguaHealthTemplateBridge.fromText(
                chart:actual,template:template,catalog:catalog)
            guard blocks.count==8,
                  blocks.reduce(0,{$0+$1.sentences.count}) >= 8,
                  blocks.allSatisfy({ !$0.sentences.isEmpty }) else {
                throw WenguaHealthTemplateError.invalidCatalog
            }
            sampleCount+=1
        }
        // A broken/incomplete user edit cannot silently display made-up phrases.
        var damaged=catalog.components(separatedBy:"\n")
        damaged.remove(at:1)
        let actual=try WenguaNativeCore.compute(
            at:iso.date(from:"2026-11-01T05:00:00-05:00")!,timezone:"America/New_York")
        do {
            _ = try WenguaHealthTemplateBridge.fromText(
                chart:actual,template:template,catalog:damaged.joined(separator:"\n"))
            throw WenguaCastError.invalidChart
        } catch WenguaHealthTemplateError.invalidCatalog {
            // expected
        }
        print("NATIVE_HEALTH_TEMPLATE_BRIDGE_OK charts=\(sampleCount) catalog=81/81")
    }
}
