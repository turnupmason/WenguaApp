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
    // UI-only actual V8 selected role -> physical palace. Optional for old
    // saved readings; never a customer score or a second interpretation.
    var rolePalaces: [String:Int]? = nil
    // Optional time provenance keeps old saved readings decodable. It does
    // not change any frozen narration section or engine score.
    var topicTitle: String? = nil
    var castMode: String? = nil
    var castTimeZone: String? = nil
    var confirmedISO: String? = nil
    var comparisonGroupID: String? = nil
    var candidateIndex: Int? = nil
    var plannedEventKind: String? = nil
    var timingGrade: String? = nil
    var timingGradeScope: String? = nil
    var timingReferenceSections: [WenguaNativeCustomerSection]? = nil
    var timingReferenceVersion: String? = nil
    var recoveryState: String? = nil
    var recoveryWindows: [String]? = nil
    var recoverySourceVersion: String? = nil

    var resolvedHealthGrade: String? {
        guard topicID == "health.severity",
              let review = sections.first(where: { $0.id == "90_review" })?.text,
              let last = review.components(separatedBy: "\n\n").last else { return nil }
        let prefix = "综上所述，此病为"
        guard last.hasPrefix(prefix) else { return nil }
        let grade = String(last.dropFirst(prefix.count).prefix(while: {
            $0 != "。" && $0 != "；" && $0 != "\n" && $0 != "\r"
        })).trimmingCharacters(in: .whitespacesAndNewlines)
        return WenguaGradeScale.labels.contains(grade) ? grade : nil
    }

    var timingHeadline: String? {
        guard castMode == "planned_event" else { return nil }
        if let contract=WenguaDomainContract.lookup(topicID),
           contract.gradeScope != nil, contract.gradeScope == timingGradeScope,
           let grade=timingGrade, WenguaGradeScale.labels.contains(grade) {
            return "此时辰：" + grade
        }
        return "此时辰：吉凶待核"
    }

}

// Shared vocabulary and request contract; domain templates decide which
// independent symbols/relationships participate. No universal disease scorer.
enum WenguaGradeScale {
    static let labels=["极大吉","大吉","中吉","小吉","极小吉","不凶不吉",
                       "极小凶","小凶","中凶","大凶","极大凶"]
    // Domain providers supply an approved FINAL signed net score. This is
    // never a symbol-strength mapping or permission to borrow health rules.
    static let finalNetRange = -5...5
    static func label(forFinalNetScore score:Int) -> String? {
        finalNetRange.contains(score) ? labels[5-score] : nil
    }
}

struct WenguaDomainContract {
    enum Capability: Equatable { case healthSeverity, healthLocation, healthRecovery, chartOnly, electiveReserved, legacyOnly }
    let domainID: String
    let topicID: String
    let capability: Capability
    var canCast: Bool { capability != .legacyOnly }
    var interpretationReady: Bool { capability == .healthSeverity || capability == .healthLocation || capability == .healthRecovery }
    var acceptsPlannedTime: Bool { capability == .electiveReserved }
    var acceptsCurrentTime: Bool { canCast && capability != .electiveReserved }
    var gradeScope: String? { (capability == .healthSeverity || capability == .healthLocation) ? "health.severity.V9/V11" : nil }
    var selectedRoleIDs: [String] {
        switch capability {
        case .healthSeverity: return ["illness","doctor","medicine","patient","hour","chief","natal_if_provided","qualified_auxiliary"]
        case .healthLocation: return ["illness","patient","hour","injury_if_selected"]
        case .healthRecovery: return ["illness","patient","doctor","medicine","hour","qualified_effective_control"]
        default: return [] // Await each domain's reviewed template; never copy health roles.
        }
    }
    static let ordinaryTopicCounts=["marriage":3,"career":3,"business":3,"education":2,
        "travel":2,"missing":2,"property":2,"lawsuit":2,"crime":1,"weather":1,
        "sports":1,"geography":1,"life":1,"other":1]
    static let electiveTitles=["health":"看病／手术","marriage":"约会／结婚",
        "travel":"旅游／出行","career":"面试／入职","business":"开业／交易",
        "education":"考试／报名","missing":"寻访／会面","property":"查找／取回",
        "lawsuit":"调解／诉讼","crime":"相关事项","weather":"户外安排",
        "sports":"参赛／活动","geography":"搬迁／动土","life":"重要安排","other":"具体事项"]
    static func lookup(_ topic: String) -> WenguaDomainContract? {
        let parts=topic.split(separator:".").map(String.init)
        guard parts.count==2 else {return nil}
        let domain=parts[0], key=parts[1]
        guard electiveTitles[domain] != nil else {
            return topic=="timing.planned" ? .init(domainID:"timing",topicID:topic,capability:.legacyOnly) : nil
        }
        let capability:Capability
        if key=="elective" {capability = .electiveReserved}
        else if topic=="health.severity" {capability = .healthSeverity}
        else if topic=="health.discomfort" {capability = .healthLocation}
        else if topic=="health.recovery" {capability = .healthRecovery}
        else if topic=="health.treatment" {capability = .chartOnly}
        else if let count=ordinaryTopicCounts[domain],let index=Int(key),index>=0,index<count {
            capability = .chartOnly
        } else {return nil}
        return .init(domainID:domain,topicID:topic,capability:capability)
    }
    func approvedGrade(primary: WenguaNativeCustomerReading,
                       reference: WenguaNativeCustomerReading) -> String? {
        guard interpretationReady, gradeScope != nil, reference.topicID=="health.severity",
              primary.topicID==topicID, reference.iso==primary.iso,
              reference.relationship==primary.relationship else {return nil}
        return reference.resolvedHealthGrade
    }
}

enum WenguaNativeReadingError: Error, LocalizedError {
    case unsupportedTopic, unsupportedRelationship, missingRole, missingPhrases, missingEnergy, invalidPhrase, missingInjuryContext
    var errorDescription: String? {
        switch self {
        case .unsupportedTopic: return "这个细分领域的断案规则还没有通过原生一致性验收"
        case .unsupportedRelationship: return "当前人物关系尚缺经核的原生用神规则"
        case .missingRole: return "真实九宫中无法唯一确定本次选定的人物或病象用神"
        case .missingPhrases: return "本地最新断案话术模板缺失"
        case .missingEnergy: return "本机能量规则数据缺失，无法生成本次专业断词"
        case .missingInjuryContext: return "请先选择普通不适、意外受伤、骨肉受损、出血、剧痛或手术"
        case .invalidPhrase: return "断词模板有未定义的占位符"
        }
    }
}

enum WenguaNativeReadingRouter {
    // Current source-verified native binding: day stem for self, real year
    // stem for father. Other relatives retain their original book candidates
    // in actor_profiles.json, but CANNOT silently reuse self in a native app.
    static let supportedRelations = ["本人","父亲","母亲","爷爷","奶奶","父母","朋友","同事",
        "儿子","女儿","孩子","侄子","配偶","其他长辈",
        "哥哥","姐姐","弟弟","妹妹","哥哥或姐姐","弟弟或妹妹","妻子","丈夫","动物","母鸡","公鸡","女婿"]
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
                        inquiry:WenguaNativeInquiry? = nil,
                        bundle:Bundle = .main) throws -> WenguaNativeCustomerReading {
        #if canImport(UIKit) || WENGUA_RECOVERY
        if topicID=="health.recovery" {
            return try WenguaNativeRecovery.compose(chart:chart,relationship:relationship,
                                                    inquiry:inquiry,bundle:bundle)
        }
        #endif
        guard ["health.severity","health.discomfort"].contains(topicID) else {
            throw WenguaNativeReadingError.unsupportedTopic
        }
        // iOS native-only body-site module: Linux Swift V8 CLI parity deliberately
        // compiles the frozen V8 subset without this independent SwiftUI source.
        #if canImport(UIKit) || WENGUA_BODY_SITE
        // Independent body-site topic; never enter V8 severity scoring.
        if topicID=="health.discomfort" {
            let request=inquiry ?? WenguaNativeInquiry.standard(relationship)
            guard request.relationship==relationship else {
                throw WenguaNativeReadingError.unsupportedRelationship
            }
            let profile=try WenguaNativeActorSource.fromBundle(bundle)
            let actor=try WenguaNativeActorSource.bind(
                chart:chart,inquiry:request,index:profile)
            guard let injuryContext=request.injuryContext,
                  WenguaNativeDiscomfortV15.allowedContexts.contains(injuryContext) else {
                throw WenguaNativeReadingError.missingInjuryContext
            }
            return try WenguaNativeDiscomfortV15.compose(
                chart:chart,relationship:relationship,actor:actor,
                injuryContext:injuryContext,bundle:bundle)
        }
        #endif
        guard let t=bundle.url(forResource:"reading_template",withExtension:"json"),
              let p=bundle.url(forResource:"81_pairs",withExtension:"tsv") else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let energy=try WenguaNativeEnergyBundle.fromBundle(bundle)
        let source=try WenguaNativeActorSource.fromBundle(bundle)
        let request=inquiry ?? WenguaNativeInquiry.standard(relationship)
        guard request.relationship==relationship else {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        let actor=try WenguaNativeActorSource.bind(
            chart:chart,inquiry:request,index:source)
        return try compose(chart:chart,topicID:topicID,
                           relationship:relationship,
                           template:Data(contentsOf:t),
                           catalog:String(contentsOf:p,encoding:.utf8),
                           energy:energy,actor:actor)
    }

    static func compose(chart:WenguaNativeChart, topicID:String, relationship:String,
                        template:Data, catalog:String,
                        energy:WenguaNativeEnergyCatalog? = nil,
                        actor:WenguaNativeActor? = nil)
                        throws -> WenguaNativeCustomerReading {
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
                      "patient","hour","chief","details","disclaimer"]
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
        func atStem(_ name:String, sourceGanzhi:String?=nil) throws -> WenguaNativePalace {
            let carrier:String
            if name=="甲" {
                guard let sourceGanzhi,
                      let mapped=WenguaNativeActorSource.jiaCarrier(sourceGanzhi) else {
                    throw WenguaNativeReadingError.missingRole
                }
                carrier=mapped
            } else {carrier=name}
            return try unique {
                $0.heavenStars.contains(where:{$0.carriedStem==carrier})
            }
        }
        let illness=try unique {$0.heavenStars.contains(where:{$0.star=="天芮星"})}
        let doctor=try unique {$0.heavenStars.contains(where:{$0.star=="天心星"})}
        let medicine=try atStem("乙")
        let patientStem=actor?.mainStem ?? String(
            (relationship=="父亲" ? chart.pillars.year :
             chart.pillars.day).prefix(1))
        let patient:WenguaNativePalace
        if let actor {
            patient=try unique{$0.id==actor.mainPalace}
        } else {
            patient=try atStem(patientStem,sourceGanzhi:
                relationship=="父亲" ? chart.pillars.year:chart.pillars.day)
        }
        let hourStem=String(chart.pillars.hour.prefix(1))
        let hour=try atStem(hourStem,sourceGanzhi:chart.pillars.hour)
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
        // Retain phrase validation even though this legacy text is not displayed.
        _ = try [
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
        // STRICT source-text contract. The complete Python V-next text is
        // rendered from the fresh actual Swift audit and SAME editable JSON.
        // No extra native paraphrase, no inserted sections, no internal scores.
        // All mandatory arithmetic, actor, 81/200 and directional rules stay
        // inside WenguaVNextEngine; only the customer words cross this DTO.
        if let energy {
            let review=try WenguaVNextEngine.compute(
                chart:chart,relationship:relationship,energy:energy,
                catalog:catalog,actor:actor)
            let exact=try WenguaPythonVNextVerbatim.sections(
                chart:chart,review:review,actor:actor,template:template,
                catalog:catalog,energy:energy)
            return WenguaNativeCustomerReading(
                version:"health_severity_v9_scoring_v11_template_frozen_20261102",
                topicID:topicID,relationship:relationship,iso:chart.iso,
                evidenceStatus:"real_native_score_private_python_full_text_parity",
                sections:exact,rolePalaces:review.roles)
        }
        // Missing 200-cell sources are fatal; never render an obsolete,
        // half-wired customer result when the current engine is unavailable.
        throw WenguaNativeReadingError.missingEnergy
    }
}
