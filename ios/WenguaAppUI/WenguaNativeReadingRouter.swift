import Foundation

// Native offline health evidence renderer (V-next integration stage 2).
// Real chart -> domain/subquestion -> patient relationship -> actual palaces
// -> editable GitHub-sourced Chinese phrases. No invented parity with the
// Python 200-cell +/-5 engine, no scores or clinical prognosis in this DTO.
struct WenguaNativeCustomerSection: Codable, Identifiable {
    let id: String
    let title: String
    let text: String
}
struct WenguaNativeCustomerReading: Codable {
    let version: String
    let topicID: String
    let relationship: String
    let iso: String
    let evidenceStatus: String
    let sections: [WenguaNativeCustomerSection]
}

enum WenguaNativeReadingError: Error, LocalizedError {
    case unsupportedTopic, unsupportedRelationship, missingRole, missingPhrases, invalidPhrase
    var errorDescription: String? {
        switch self {
        case .unsupportedTopic: return "这个细分领域的断案规则还没有通过原生一致性验收"
        case .unsupportedRelationship: return "当前人物关系尚缺经核的原生用神规则"
        case .missingRole: return "真实九宫中无法唯一确定本次选定的人物或病象用神"
        case .missingPhrases: return "本地最新断案话术模板缺失"
        case .invalidPhrase: return "断词模板有未定义的占位符"
        }
    }
}

enum WenguaNativeReadingRouter {
    // Current source-verified native binding: day stem for self, real year
    // stem for father. Other relatives retain their original book candidates
    // in actor_profiles.json, but CANNOT silently reuse self in a native app.
    static let supportedRelations = ["本人","父亲"]
    static let supportedTopics = ["health.severity"]
    static let palaceOrder = [4,9,2,3,7,8,1,6]
    static let homeStars = ["天蓬星":1,"天芮星":2,"天冲星":3,"天辅星":4,
                            "天心星":6,"天柱星":7,"天任星":8,"天英星":9]
    static let homeDoors = ["休门":1,"死门":2,"伤门":3,"杜门":4,
                            "开门":6,"惊门":7,"生门":8,"景门":9]
    static let opposites = [1:9,9:1,2:8,8:2,3:7,7:3,4:6,6:4]
    static let palaceElements = [1:"水",2:"土",3:"木",4:"木",
                                 6:"金",7:"金",8:"土",9:"火"]
    static let stemElements = ["甲":"木","乙":"木","丙":"火","丁":"火",
                               "戊":"土","己":"土","庚":"金","辛":"金",
                               "壬":"水","癸":"水"]
    static let stemOrder = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    static let controlling = ["木":"土","土":"水","水":"火","火":"金","金":"木"]
    static let generating = ["木":"火","火":"土","土":"金","金":"水","水":"木"]

    static func compose(chart:WenguaNativeChart, topicID:String, relationship:String,
                        bundle:Bundle = .main) throws -> WenguaNativeCustomerReading {
        guard let t=bundle.url(forResource:"reading_template",withExtension:"json"),
              let p=bundle.url(forResource:"81_pairs",withExtension:"tsv") else {
            throw WenguaNativeReadingError.missingPhrases
        }
        return try compose(chart:chart,topicID:topicID,relationship:relationship,
                           template:Data(contentsOf:t),
                           catalog:String(contentsOf:p,encoding:.utf8))
    }

    static func compose(chart:WenguaNativeChart, topicID:String, relationship:String,
                        template:Data, catalog:String) throws -> WenguaNativeCustomerReading {
        guard supportedTopics.contains(topicID) else {throw WenguaNativeReadingError.unsupportedTopic}
        guard supportedRelations.contains(relationship) else {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        // Reuse the exact 81/81 and format validation from the first bridge,
        // never maintain a duplicate list of formation names or quotations.
        let formations=try WenguaHealthTemplateBridge.fromText(
            chart:chart,template:template,catalog:catalog)
        guard let root=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              let phrases=root["native_customer"] as? [String:String] else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let required=["macro_five","macro_clear","macro_slow","macro_fast",
                      "macro_mixed","macro_unset","illness","doctor","medicine",
                      "patient","hour","chief","details","pending","disclaimer"]
        guard required.allSatisfy({ !(phrases[$0] ?? "").isEmpty }) else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let cells=chart.palaces
        guard cells.count==9 else {throw WenguaCastError.invalidChart}
        func unique(_ filter:(WenguaNativePalace)->Bool) throws -> WenguaNativePalace {
            let list=cells.filter(filter)
            guard list.count==1, list[0].id != 5 else {
                throw WenguaNativeReadingError.missingRole
            }
            return list[0]
        }
        func atStem(_ name:String) throws -> WenguaNativePalace {
            try unique { $0.heavenStars.contains(where:{$0.carriedStem==name}) }
        }
        let illness=try unique {$0.heavenStars.contains(where:{$0.star=="天芮星"})}
        let doctor=try unique {$0.heavenStars.contains(where:{$0.star=="天心星"})}
        let medicine=try atStem("乙")
        let patientStem=String((relationship=="父亲" ? chart.pillars.year :
                              chart.pillars.day).prefix(1))
        let patient=try atStem(patientStem)
        let hourStem=String(chart.pillars.hour.prefix(1))
        let hour=try atStem(hourStem)
        let chief=try unique {$0.deity=="值符"}
        func palaceName(_ p:WenguaNativePalace)->String {
            p.gua+String(p.id)+"宫"
        }
        func relation(_ p:WenguaNativePalace)->String {
            if p.id==illness.id {return "同宫"}
            guard let a=palaceElements[p.id],let b=palaceElements[illness.id] else {
                return "关系待核"
            }
            if a==b {return "五行比和"}
            if controlling[a]==b {return "宫位五行克病宫（实际能否制病还需力量条件）"}
            if controlling[b]==a {return "受病宫五行所克"}
            if generating[a]==b {return "五行生扶病宫"}
            if generating[b]==a {return "受病宫五行所生"}
            return "关系待核"
        }
        func fill(_ slot:String,_ values:[String:String]=[:]) throws -> String {
            guard var s=phrases[slot] else {throw WenguaNativeReadingError.missingPhrases}
            for (key,value) in values {
                s=s.replacingOccurrences(of:"{"+key+"}",with:value)
            }
            guard !s.contains("{"),!s.contains("}") else {
                throw WenguaNativeReadingError.invalidPhrase
            }
            return s
        }
        func facts(_ p:WenguaNativePalace,_ role:String,_ more:[String:String]=[:])
          throws -> String {
            var data=[
                "palace":palaceName(p),
                "star":p.heavenStars.map{$0.star}.joined(separator:"、"),
                "door":p.door ?? "未核",
                "deity":p.deity ?? "未核",
                "relation":relation(p),
                "person":relationship,
                "stem":role
            ]
            for (k,v) in more {data[k]=v}
            return try fill(role=="illness" ? "illness" :
                role=="doctor" ? "doctor" :
                role=="medicine" ? "medicine" :
                role=="patient" ? "patient" :
                role=="hour" ? "hour" : "chief",data)
        }
        let dayStem=String(chart.pillars.day.prefix(1))
        let i=stemOrder.firstIndex(of:hourStem)
        let j=stemOrder.firstIndex(of:dayStem)
        guard let hourIndex=i,let dayIndex=j,
              let hourEl=stemElements[hourStem],let dayEl=stemElements[dayStem] else {
            throw WenguaCastError.invalidChart
        }
        let fiveNot=hourIndex%2 == dayIndex%2 && controlling[hourEl]==dayEl
        // Compare *all* eight outer stars and doors, not a single symbolic
        // match. The centre remains without ordinary star/door/god.
        let actualStars=cells.flatMap{p in
            p.heavenStars.compactMap{s -> (String,Int)? in
                homeStars[s.star] != nil ? (s.star,p.id) : nil
            }
        }
        let actualDoors=cells.compactMap{p -> (String,Int)? in
            guard let d=p.door,homeDoors[d] != nil else {return nil}
            return (d,p.id)
        }
        func entire(_ items:[(String,Int)],_ homes:[String:Int],_ reverse:Bool)->Bool {
            items.count==8 && items.allSatisfy { name,id in
                guard let origin=homes[name] else {return false}
                return id == (reverse ? opposites[origin] : origin)
            }
        }
        let fuyin=entire(actualStars,homeStars,false) ||
                   entire(actualDoors,homeDoors,false)
        let fanyin=entire(actualStars,homeStars,true) ||
                    entire(actualDoors,homeDoors,true)
        let macro=try [
            fill(fiveNot ? "macro_five" : "macro_clear"),
            fill(fuyin && fanyin ? "macro_mixed" :
                 fuyin ? "macro_slow" : fanyin ? "macro_fast" : "macro_unset")
        ].joined(separator:" ")
        let roles:[(String,WenguaNativePalace,String)]=[
            ("illness",illness,""),("doctor",doctor,""),
            ("medicine",medicine,""),("patient",patient,patientStem),
            ("hour",hour,hourStem),("chief",chief,"")
        ]
        var roleSentences:[String]=[]
        for (kind,p,stem) in roles {
            roleSentences.append(try facts(p,kind,
                ["stem":stem,"person":relationship]))
        }
        let byID=Dictionary(uniqueKeysWithValues:formations.map{($0.id,$0)})
        var evidence:[String]=[]
        var used:Set<Int>=[]
        for (_,p,_) in roles {
            if !used.insert(p.id).inserted {continue}
            guard let lines=byID[p.id]?.sentences else {
                throw WenguaNativeReadingError.missingRole
            }
            let titles=lines.compactMap{line -> String? in
                guard let begin=line.firstIndex(of:"「"),
                      let end=line[begin...].firstIndex(of:"」") else{return nil}
                return String(line[line.index(after:begin)..<end])
            }
            guard !titles.isEmpty else {throw WenguaNativeReadingError.invalidPhrase}
            evidence.append(try fill("details",[
                "palace":palaceName(p),"names":titles.joined(separator:"、")]))
        }
        let sections=[
            WenguaNativeCustomerSection(id:"01",title:"局势与缓急",text:macro),
            WenguaNativeCustomerSection(id:"02",title:"选用神与宫位关系",
                                        text:roleSentences.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"03",title:"本盘格局依据",
                                        text:evidence.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"04",title:"综合研判",
                                        text:try fill("pending")),
            WenguaNativeCustomerSection(id:"05",title:"说明",
                                        text:try fill("disclaimer"))
        ]
        return WenguaNativeCustomerReading(
            version:"native_evidence_vnext_20261026_stage2",
            topicID:topicID,relationship:relationship,iso:chart.iso,
            evidenceStatus:"needs_200_cell_and_conflict_parity",sections:sections)
    }
}
