import Foundation

// All user-facing V-next words are in the authoritative editable JSON.
// The score and 5x5 internals are never copied to the public DTO or saved
// customer record. Missing custom text fails closed.
enum WenguaVNextCustomerComposer {
    static let titles=["illness":"天芮病宫","doctor":"天心医生",
        "medicine":"乙奇医药","patient":"患者用神","hour":"时干事体",
        "chief":"值符护持","qian":"乾宫辅助","kun":"坤宫辅助"]

    static func sections(_ review:WenguaVNextAudit,
                         chart:WenguaNativeChart,
                         template:Data) throws -> [WenguaNativeCustomerSection] {
        guard let json=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              let strings=json["native_customer"] as? [String:String] else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let slots=[
            "vnext_palace","vnext_role","vnext_control_effective",
            "vnext_control_limited","vnext_control_failed",
            "vnext_control_pending","vnext_no_control","vnext_void_fake",
            "vnext_void_true","vnext_verdict_good","vnext_verdict_bad",
            "vnext_verdict_neutral","vnext_verdict_conflict",
            "vnext_verdict_pending","vnext_timing","vnext_title_palace",
            "vnext_title_role","vnext_title_verdict","vnext_title_timing"
        ]
        guard slots.allSatisfy({!(strings[$0] ?? "").isEmpty}) else {
            throw WenguaNativeReadingError.missingPhrases
        }
        func phrase(_ slot:String,_ vars:[String:String]=[:]) throws -> String {
            guard var value=strings[slot] else {
                throw WenguaNativeReadingError.missingPhrases
            }
            for (key,contents) in vars {
                value=value.replacingOccurrences(of:"{"+key+"}",with:contents)
            }
            if value.contains("{") || value.contains("}") {
                throw WenguaNativeReadingError.invalidPhrase
            }
            return value
        }
        let byID=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        var palaces:[String]=[]
        for id in review.palaces.keys.sorted() {
            guard let cell=byID[id],let item=review.palaces[id] else {
                throw WenguaCastError.invalidChart
            }
            let voidText=item.void=="fake_void" ? try phrase("vnext_void_fake") :
                item.void=="true_void" ? try phrase("vnext_void_true") : ""
            palaces.append(try phrase("vnext_palace",[
                "palace":cell.gua+String(id)+"宫",
                "stars":cell.heavenStars.map{$0.star}.joined(separator:"、"),
                "door":cell.door ?? "未核",
                "deity":cell.deity ?? "未核",
                "patterns":item.patterns.map{"「"+$0+"」"}.joined(separator:"、"),
                "void_note":voidText
            ]))
        }
        var roleTexts:[String]=[]
        for role in ["illness","doctor","medicine","patient",
                     "hour","chief","qian","kun"] {
            guard let pid=review.roles[role],let p=byID[pid] else{continue}
            let c=review.controls.first{$0.role==role}
            let relation=c?.direction ?? (pid==review.roles["illness"] ? "同宫" : "关系需合断")
            let control:String
            if let comparison=c,let outcome=comparison.cell {
                let slot=comparison.applicability=="strong" ?
                    "vnext_control_effective" :
                    comparison.applicability=="limited" ?
                    "vnext_control_limited" :
                    comparison.applicability=="failed" ?
                    "vnext_control_failed" : "vnext_control_pending"
                control=try phrase(slot,["outcome":outcome])
            } else if c?.applicability=="pending" {
                control=try phrase("vnext_control_pending")
            } else {
                control=try phrase("vnext_no_control")
            }
            roleTexts.append(try phrase("vnext_role",[
                "role":titles[role] ?? role,
                "palace":p.gua+String(pid)+"宫",
                "relation":relation,
                "control_note":control
            ]))
        }
        let final:String
        if review.score==nil {final=try phrase("vnext_verdict_pending")}
        else if review.evidenceConflict {final=try phrase("vnext_verdict_conflict")}
        else if review.score==0 {final=try phrase("vnext_verdict_neutral")}
        else {final=try phrase(review.score!>0 ?
            "vnext_verdict_good" : "vnext_verdict_bad")}
        return [
            WenguaNativeCustomerSection(id:"82vnext",title:try phrase("vnext_title_palace"),
                                        text:palaces.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"83vnext",title:try phrase("vnext_title_role"),
                                        text:roleTexts.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"90vnext",title:try phrase("vnext_title_verdict"),
                                        text:final),
            WenguaNativeCustomerSection(id:"91vnext",title:try phrase("vnext_title_timing"),
                                        text:try phrase("vnext_timing",[
                                            "horse":chart.hourHorse]))
        ]
    }
}
