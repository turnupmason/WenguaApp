import Foundation

// Independent offline body-SITE reader. It never calls V8 severity and
// cannot treat the 255 historic rules as 255 positive clinical observations.
enum WenguaNativeDiscomfortV15 {
    private static let physical = Set([1,2,3,4,6,7,8,9])
    private static let innerYang = Set([1,8,3,4])
    private static let innerYin = Set([9,2,7,6])

    static func compose(chart:WenguaNativeChart, relationship:String,
                        actor:WenguaNativeActor, bundle:Bundle = .main) throws
                        -> WenguaNativeCustomerReading {
        guard let rulesURL=bundle.url(forResource:"complete_255_rules_v15_20261101",withExtension:"json"),
              let stemsURL=bundle.url(forResource:"three_source_stem_variants_v14_20261101",withExtension:"json"),
              let templateURL=bundle.url(forResource:"native_discomfort_v15",withExtension:"json"),
              let energyURL=bundle.url(forResource:"health_energy_200",withExtension:"json"),
              let pairsURL=bundle.url(forResource:"81_pairs",withExtension:"tsv") else {
            throw WenguaNativeReadingError.missingPhrases
        }
        return try compose(chart:chart,relationship:relationship,actor:actor,
                           rules:Data(contentsOf:rulesURL),
                           stems:Data(contentsOf:stemsURL),
                           template:Data(contentsOf:templateURL),
                           energy:Data(contentsOf:energyURL),
                           pairs:Data(contentsOf:pairsURL))
    }

    // Exposed as a pure data-in function for parity fixtures and fail-closed tests.
    static func compose(chart:WenguaNativeChart, relationship:String,
                        actor:WenguaNativeActor,
                        rules:Data, stems:Data, template:Data,
                        energy:Data, pairs:Data) throws
                        -> WenguaNativeCustomerReading {
        let powerCatalog=try WenguaNativeEnergyBundle.fromData(energy)
        guard let pairText=String(data:pairs,encoding:.utf8),
              pairText.split(separator:"\n",omittingEmptySubsequences:true).count==82 else {
            throw WenguaNativeReadingError.missingPhrases
        }
        guard let ruleDoc=try JSONSerialization.jsonObject(with:rules) as? [String:Any],
              let allRules=ruleDoc["rules"] as? [[String:Any]], allRules.count==255,
              let cases=ruleDoc["cases"] as? [Any],cases.count==12,
              let conflicts=ruleDoc["conflicts"] as? [Any],conflicts.count==20,
              Set(allRules.compactMap{$0["ID"] as? String}).count==255,
              let stemDoc=try JSONSerialization.jsonObject(with:stems) as? [String:Any],
              let mapping=stemDoc["mapping"] as? [String:[String:[String]]],
              mapping.count==10,
              let words=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              words["schema"] as? String=="wengua_health_discomfort_native_v17_power_and_81_20261101",
              let paragraphs=words["sections"] as? [[String:String]], paragraphs.count==6,
              chart.palaces.count==9, physical.contains(actor.mainPalace) else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let illnessCells=chart.palaces.filter{$0.heavenStars.contains(where:{$0.star=="天芮星"})}
        guard illnessCells.count==1,let illness=illnessCells.first,
              physical.contains(illness.id),
              let sky=illness.heavenStars.first(where:{$0.star=="天芮星"})?.carriedStem,
              let door=illness.door,let deity=illness.deity,
              let variants=mapping[sky],
              let secret=variants["qimen_secret_vol13"],!secret.isEmpty,
              let viscera=variants["sanming_viscera"],!viscera.isEmpty,
              let surface=variants["sanming_body_surface"],!surface.isEmpty else {
            throw WenguaNativeReadingError.missingRole
        }
        guard chart.bureau.dun=="yang" || chart.bureau.dun=="yin" else {
            throw WenguaNativeReadingError.missingRole
        }
        let sector=(chart.bureau.dun=="yang" ? innerYang:innerYin).contains(illness.id)
            ? "体内":"体表"
        let chineseDigits:[Int:String]=[1:"一",2:"二",3:"三",4:"四",
                                        6:"六",7:"七",8:"八",9:"九"]
        func label(_ p:WenguaNativePalace)->String {
            p.gua+(chineseDigits[p.id] ?? String(p.id))
        }
        let code=label(illness)
        let side=sector=="体内" ? "体内":"体表"
        let book=allRules.filter{ row in
            row["类别"] as? String=="九宫定位" &&
            row["子类"] as? String=="神奇之门-"+side &&
            (row["符号组合"] as? String)==code+"·"+side &&
            (row["证据级别"] as? String)?.hasPrefix("A")==true
        }
        let originalSide=sector=="体内" ? "内":"外"
        let other=allRules.filter{ row in
            row["类别"] as? String=="九宫定位" &&
            row["子类"] as? String=="秘笈大全-"+originalSide &&
            (row["符号组合"] as? String)==code+"·"+originalSide &&
            (row["证据级别"] as? String)?.hasPrefix("A")==true
        }
        guard book.count==1,other.count==1,
              let primary=book[0]["古籍象意或候选"] as? String,
              let external=other[0]["古籍象意或候选"] as? String,
              !primary.isEmpty,!external.isEmpty,
              let injury=chart.palaces.first(where:{$0.door=="伤门"}),
              chart.palaces.filter({$0.door=="伤门"}).count==1 else {
            throw WenguaNativeReadingError.missingRole
        }
        let hourStem=String(chart.pillars.hour.prefix(1))
        guard let hourID=WenguaNativeActorSource.actualStem(hourStem,chart:chart,
                                                          sourceGanzhi:chart.pillars.hour),
              let hourPalace=chart.palaces.first(where:{$0.id==hourID}),
              let patientPalace=chart.palaces.first(where:{$0.id==actor.mainPalace}) else {
            throw WenguaNativeReadingError.missingRole
        }
        let bird=illness.heavenStars.first(where:{$0.star=="天禽星"})?.carriedStem
        let companion=bird.map{"同宫天禽另携"+$0+"，仅作独立辅象；"} ??
            "本宫无另行天禽携干；"
        let region=([9,4,2].contains(illness.id) ? "上部" :
                     [3,7].contains(illness.id) ? "中部":"下部")
        let palaceName:String=code+"宫"
        func sourceClue(_ category:String,_ symbol:String)->String {
            let rows=allRules.filter {
                ($0["类别"] as? String)==category &&
                ($0["符号组合"] as? String)==symbol &&
                ($0["证据级别"] as? String)?.hasPrefix("A")==true
            }
            guard rows.count==1,
                  let raw=rows[0]["古籍象意或候选"] as? String
            else {return "暂无可独立定位的细项"}
            let phrase=raw.components(separatedBy:"；")[0]
                .components(separatedBy:"（")[0]
            return phrase.contains("原文") || phrase.contains("不是") || phrase.contains("节气群") ? "无可用于细分身体部位的额外信息" : phrase
        }
        let matchingDeity=allRules.filter {
            ($0["类别"] as? String)=="八神病象" &&
            ($0["符号组合"] as? String)?
                .components(separatedBy:"／").contains(deity)==true
        }
        let deityClue=(matchingDeity.first?["古籍象意或候选"] as? String ?? "其他传统象意")
            .components(separatedBy:"；")[0].components(separatedBy:"（")[0]
        let illnessStar=illness.heavenStars.first{$0.star=="天芮星"}!
        let phaseText=illnessStar.stages.map{$0.branch+$0.stage}.joined(separator:"、")
        let voidText=illness.voidBranches.isEmpty ? "本宫无空亡支标记" :
            "本宫临"+illness.voidBranches.joined(separator:"、")+"空"
        let horseText=illness.horseBranch.map{"本宫见"+$0+"马"} ?? "本宫无驿马标记"
        let tombText=illness.tombs.isEmpty ? "本宫无入墓标记" :
            illness.tombs.map{$0.plane+$0.stem+$0.branch+"墓"}.joined(separator:"、")
        let five:[Int:String]=[1:"水",2:"土",3:"木",4:"木",6:"金",7:"金",8:"土",9:"火"]
        let control=["木":"土","土":"水","水":"火","火":"金","金":"木"]
        let generate=["木":"火","火":"土","土":"金","金":"水","水":"木"]
        func palaceRelation(_ p:WenguaNativePalace)->String {
            if p.id==illness.id {return "同宫"}
            guard let a=five[illness.id],let b=five[p.id] else {return "另宫"}
            if a==b{return "比和"}
            if control[a]==b{return "病宫克此宫"}
            if control[b]==a{return "此宫克病宫"}
            if generate[a]==b{return "病宫生此宫"}
            if generate[b]==a{return "此宫生病宫"}
            return "关系待辨"
        }
        let patientDoor=patientPalace.door ?? "无门"
        let patientDeity=patientPalace.deity ?? "无神"
        let skyOther=mapping[illness.earthStem]?["qimen_secret_vol13"] ?? []
        let birdOther=bird.flatMap{mapping[$0]?["qimen_secret_vol13"]} ?? []
        let values:[String:String]=[
            "palace":palaceName,"dun":chart.bureau.dun=="yang" ? "阳":"阴",
            "sector":sector,"region":region,"primary":primary,"external":external,
            "door":door,"deity":deity,"sky":sky,"earth":illness.earthStem,
            "companion":bird.map{"同宫天禽另携"+$0+"，干象还可参看"+birdOther.joined(separator:"、")+"，与天芮各自独立"} ?? "本宫没有另一组天禽携干",
            "secret":secret.joined(separator:"、"),
            "viscera":viscera.joined(separator:"、"),
            "surface":surface.joined(separator:"、"),
            "injury":label(injury)+"宫",
            "hour_stem":hourStem,"hour_palace":label(hourPalace)+"宫",
            "person":relationship,"patient_palace":label(patientPalace)+"宫",
            "palace_position":"以这一实宫的具体部位为先",
            "star_group":illness.heavenStars.map{$0.star}.joined(separator:"、"),
            "door_clue":sourceClue("八门病象",door),
            "deity_clue":deityClue,
            "palace_clue":sourceClue("九宫病象",code),
            "stage_clue":"天芮携"+sky+"的十二长生为"+phaseText,
            "void_clue":voidText,"horse_clue":horseText,"tomb_clue":tombText,
            "earth_hint":skyOther.joined(separator:"、"),
            "stem_scope":"天盘与地盘按实际上下位置分别参看",
            "patient_stem":actor.mainStem,
            "patient_door":patientDoor,"patient_deity":patientDeity,
            "patient_relation":"患者宫和病宫"+palaceRelation(patientPalace),
            "patient_coincidence":patientPalace.id==illness.id ? "两个用神在同一实宫，应合看但不重复计位" : "患者宫另有宫象，不能据此改写天芮所定部位",
            "natal_scope":actor.natalStem.map{"另知年命"+$0+"，须按真实年命位置另看"} ?? "出生年命未提供，因此不额外指定年命宫",
            "injury_deity":injury.deity ?? "无神"
        ]
        let required=["01_location","02_tianrui","03_comparison",
                      "04_person","05_review","06_conclusion"]
        var sections:[WenguaNativeCustomerSection]=[]
        for (i,entry) in paragraphs.enumerated(){
            guard entry["id"]==required[i],let title=entry["title"],
                  let body=entry["text"],!body.isEmpty else {
                throw WenguaNativeReadingError.invalidPhrase
            }
            var output=body
            for (key,value) in values {
                output=output.replacingOccurrences(of:"{"+key+"}",with:value)
            }
            guard !output.contains("{"),!output.contains("}") else {
                throw WenguaNativeReadingError.invalidPhrase
            }
            sections.append(WenguaNativeCustomerSection(id:required[i],title:title,text:output))
        }
        return WenguaNativeCustomerReading(
            version:"discomfort_v16_full_facts_no_customer_sources_20261101",
            topicID:"health.discomfort",relationship:relationship,iso:chart.iso,
            evidenceStatus:"traditional_textual_location_not_medical_diagnosis",
            sections:sections,rolePalaces:["illness":illness.id,"patient":actor.mainPalace,
                                          "injury":injury.id,"hour":hourPalace.id])
    }
}
