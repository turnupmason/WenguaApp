import Foundation

private struct ExpectedRole:Decodable {
    let palace:Int
    let components:ExpectedComponents
    let raw:Int?
    let score:Int?
    let void:String
}
private struct ExpectedComponents:Decodable {
    let star:Int?
    let door:Int?
    let deity:Int?
    let pattern:Int
}
private struct ExpectedAux:Decodable {let palace:Int;let score:Int?}
private struct ExpectedSummary:Decodable {
    let score:Int?
    let post_void_known_sum:Int
    let effective_palace_scores:[String:Int?]
}
private struct ExpectedControl:Decodable {
    let direction:String
    let cell:String?
    let scenario:String?
}
private struct ExpectedCast:Decodable {
    let evidenceDirection:String
    let controls:[String:ExpectedControl]
    let instant:String
    let relationship:String
    let summary:ExpectedSummary
    let roles:[String:ExpectedRole]
    let auxiliaries:[String:ExpectedAux]
    let firstStage:Bool
}
private struct ExpectedCases:Decodable {let cases:[ExpectedCast]}
@main struct VNextNativeParityCheck {
    static func main() throws {
        guard CommandLine.arguments.count==3 else {throw WenguaCastError.invalidChart}
        let bundle=try WenguaNativeEnergyBundle.fromData(
            Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
        let gold=try JSONDecoder().decode(ExpectedCases.self,
            from:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[2])))
        let catalog=try String(contentsOfFile:
            "data/knowledge/health_81_excel_20261025/81_pairs.tsv",encoding:.utf8)
        let iso=ISO8601DateFormatter()
        iso.formatOptions=[.withInternetDateTime]
        var tested=0
        for fixture in gold.cases {
            guard let d=iso.date(from:fixture.instant) else {throw WenguaCastError.invalidChart}
            let chart=try WenguaNativeCore.compute(at:d,timezone:"America/New_York")
            let audit=try WenguaVNextEngine.compute(chart:chart,relationship:fixture.relationship,
                                                    energy:bundle,catalog:catalog)
            func require(_ ok:Bool,_ explanation:String) throws {
                if !ok {throw NSError(domain:"WenguaSourceParity",code:1,
                       userInfo:[NSLocalizedDescriptionKey:fixture.instant+" "+explanation])}
            }
            try require(audit.firstMacroFiveNot==fixture.firstStage,"macro five-not mismatch")
            for (role,pid) in audit.roles.sorted(by:{$0.key<$1.key}) {
                let edge=audit.controls.first(where:{$0.role==role})
                let words=[role,String(pid),
                           String(describing:audit.palaces[pid]?.afterVoid),
                           edge?.direction ?? "illness",
                           edge?.applicability ?? "none",
                           edge?.cell ?? "none"]
                print("SWIFT_ROLE_GATE",fixture.instant,words.joined(separator:":"))
            }
            try require(audit.score==fixture.summary.score,"summary signed score mismatch: \(String(describing:audit.score)) / \(String(describing:fixture.summary.score))")
            try require(audit.postVoidKnownSum==fixture.summary.post_void_known_sum,"post-void sum mismatch \(audit.postVoidKnownSum) / \(fixture.summary.post_void_known_sum)")
            for (role,r) in fixture.roles {
                guard let p=audit.roles[role],let x=audit.palaces[p] else {
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                try require(p==r.palace,"role "+role+" palace mismatch")
                try require(x.afterVoid==r.score,"role "+role+" postvoid mismatch "+String(describing:x.afterVoid)+"/"+String(describing:r.score))
                try require(x.raw==r.raw,"role "+role+" raw mismatch "+String(describing:x.raw)+"/"+String(describing:r.raw))
                try require(x.star==r.components.star,"role "+role+" star mismatch")
                try require(x.door==r.components.door,"role "+role+" door mismatch")
                try require(x.deity==r.components.deity,"role "+role+" god mismatch")
                try require(x.pattern==r.components.pattern,"role "+role+" pattern mismatch")
                try require(x.void==r.void,"role "+role+" void mismatch")
            }
            for (k,r) in fixture.auxiliaries {
                guard let pid=audit.roles[k],let p=audit.palaces[pid] else {
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                try require(pid==r.palace,"auxiliary palace "+k+" mismatch")
                try require(p.afterVoid==r.score,"auxiliary score "+k+" mismatch")
            }
            try require(audit.evidenceDirection==fixture.evidenceDirection,
                "directional verdict mismatch Swift="+audit.evidenceDirection+" Python="+fixture.evidenceDirection)
            for (role,original) in fixture.controls {
                guard let current=audit.controls.first(where:{$0.role==role}) else {
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                try require(current.direction==original.direction,
                    "directed relation "+role+" mismatch")
                try require(current.cell==original.cell,
                    "actual directed 5x5 control "+role+" mismatch Swift="+String(describing:current.cell)+" Python="+String(describing:original.cell))
                try require(current.scenario==original.scenario,
                    "true/fake source-target 5x5 "+role+" mismatch")
            }
            print("SWIFT_PYTHON_FULL_VNEXT_MATCH "+fixture.instant+" score="+String(describing:audit.score))
            tested+=1
        }
        guard tested==5 else {throw WenguaCastError.invalidChart}
        print("WENGUA_VNEXT_PARITY_OK verified_five_current_live_Python_casts")
    }
}
