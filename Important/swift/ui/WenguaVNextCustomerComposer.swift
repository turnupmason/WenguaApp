import Foundation

// All user-facing V-next words are in the authoritative editable JSON.
// The score and 5x5 internals are never copied to the public DTO or saved
// customer record. Missing custom text fails closed.
enum WenguaVNextCustomerComposer {
    static let titles=["illness":"天芮病宫","doctor":"天心医生",
        "medicine":"乙奇医药","patient":"患者用神","hour":"时干事体",
        "chief":"值符护持","qian":"乾宫辅助","kun":"坤宫辅助",
        "natal":"患者年命","gender":"病人性别辅助"]

    private static func actualRelation(_ a:Int,_ b:Int)->String {
        if a==b {return "同宫"}
        let elements=WenguaNativeReadingRouter.palaceElements
        let generates=WenguaNativeReadingRouter.generating
        let controls=WenguaNativeReadingRouter.controlling
        guard let x=elements[a],let y=elements[b] else {return "待核"}
        if x==y {return "比和"}
        if controls[x]==y {return "克"}
        if controls[y]==x {return "被克"}
        if generates[x]==y {return "生"}
        if generates[y]==x {return "被生"}
        return "待核"
    }

    static func sections(_ review:WenguaVNextAudit,
                         chart:WenguaNativeChart,
                         template:Data,
                         actor:WenguaNativeActor? = nil) throws -> [WenguaNativeCustomerSection] {
        guard let json=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              let strings=json["native_customer"] as? [String:String] else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let slots=[
            "vnext_palace","vnext_role","vnext_control_effective",
            "vnext_control_limited","vnext_control_failed",
            "vnext_control_pending","vnext_no_control",
            "vnext_disease_control_effective","vnext_disease_control_limited",
            "vnext_disease_control_failed","vnext_void_fake",
            "vnext_void_true","vnext_verdict_good","vnext_verdict_bad",
            "vnext_verdict_neutral","vnext_verdict_conflict",
            "vnext_role_candidate","vnext_actor_harmony",
            "vnext_actor_auxiliary","vnext_actor_note","vnext_actor_natal_pending",
            "vnext_actor_details_title",
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
        var subjectEvidence:[String]=[]
        if let actor {
            if let harmony=actor.harmonyStem,
               let id=actor.harmonyPalace,let p=byID[id] {
                subjectEvidence.append(try phrase("vnext_actor_harmony",[
                    "stem":harmony,"palace":p.gua+String(id)+"宫"
                ]))
            }
            if !actor.extraPalaces.isEmpty {
                let places=actor.extraPalaces.compactMap{
                    byID[$0].map{$0.gua+String($0.id)+"宫"}
                }.joined(separator:"、")
                subjectEvidence.append(try phrase("vnext_actor_auxiliary",[
                    "palaces":places
                ]))
            }
            if actor.natalStem != nil && actor.natalPalace==nil {
                subjectEvidence.append(try phrase("vnext_actor_natal_pending"))
            }
            if !actor.note.isEmpty {
                subjectEvidence.append(try phrase("vnext_actor_note",[
                    "note":actor.note
                ]))
            }
        }
        var reading=try WenguaVNextReasoner.build(
            review,chart:chart,template:template)
        reading.append(WenguaNativeCustomerSection(
            id:"91vnext",title:try phrase("vnext_title_timing"),
            text:try phrase("vnext_timing",["horse":chart.hourHorse])))
        if !subjectEvidence.isEmpty {
            reading.insert(WenguaNativeCustomerSection(
                id:"88subject",title:try phrase("vnext_actor_details_title"),
                text:subjectEvidence.joined(separator:"\n")),at:2)
        }
        return reading
    }
}
