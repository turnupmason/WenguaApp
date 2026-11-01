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
              let templateURL=bundle.url(forResource:"native_discomfort_v15",withExtension:"json") else {
            throw WenguaNativeReadingError.missingPhrases
        }
        return try compose(chart:chart,relationship:relationship,actor:actor,
                           rules:Data(contentsOf:rulesURL),
                           stems:Data(contentsOf:stemsURL),
                           template:Data(contentsOf:templateURL))
    }

    // Exposed as a pure data-in function for parity fixtures and fail-closed tests.
    static func compose(chart:WenguaNativeChart, relationship:String,
                        actor:WenguaNativeActor,
                        rules:Data, stems:Data, template:Data) throws
                        -> WenguaNativeCustomerReading {
        guard let ruleDoc=try JSONSerialization.jsonObject(with:rules) as? [String:Any],
              let allRules=ruleDoc["rules"] as? [[String:Any]], allRules.count==255,
              let cases=ruleDoc["cases"] as? [Any],cases.count==12,
              let conflicts=ruleDoc["conflicts"] as? [Any],conflicts.count==20,
              Set(allRules.compactMap{$0["ID"] as? String}).count==255,
              let stemDoc=try JSONSerialization.jsonObject(with:stems) as? [String:Any],
              let mapping=stemDoc["mapping"] as? [String:[String:[String]]],
              mapping.count==10,
              let words=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              words["schema"] as? String=="wengua_health_discomfort_native_v15_source_separated_20261101",
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
        let code=illness.gua+String(illness.id)
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
        let palaceName:String=(illness.gua+String(illness.id)+"宫")
        let values:[String:String]=[
            "palace":palaceName,"dun":chart.bureau.dun=="yang" ? "阳":"阴",
            "sector":sector,"region":region,"primary":primary,"external":external,
            "door":door,"deity":deity,"sky":sky,"earth":illness.earthStem,
            "companion":companion,
            "secret":secret.joined(separator:"、"),
            "viscera":viscera.joined(separator:"、"),
            "surface":surface.joined(separator:"、"),
            "injury":injury.gua+String(injury.id)+"宫",
            "hour_stem":hourStem,"hour_palace":hourPalace.gua+String(hourPalace.id)+"宫",
            "person":relationship,"patient_palace":patientPalace.gua+String(patientPalace.id)+"宫"
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
            version:"discomfort_v15_full_255_source_guard_20261101",
            topicID:"health.discomfort",relationship:relationship,iso:chart.iso,
            evidenceStatus:"traditional_textual_location_not_medical_diagnosis",
            sections:sections,rolePalaces:["illness":illness.id,"patient":actor.mainPalace,
                                          "injury":injury.id,"hour":hourPalace.id])
    }
}
