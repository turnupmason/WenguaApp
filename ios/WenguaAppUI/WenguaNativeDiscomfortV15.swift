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
              words["schema"] as? String=="wengua_health_discomfort_native_v18_site_rank_20261101",
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
        // Source-backed 200 powers (NOT V8 net +/-5 or any clinical scale).
        let month=try WenguaVNextEngine.monthly(String(chart.pillars.month.suffix(1)))
        func sourceStrength(_ kind:String,_ symbol:String,
                            _ p:WenguaNativePalace,
                            _ stages:[WenguaNativeStage]=[]) throws ->String {
            try WenguaVNextEngine.factor(kind:kind,symbol:symbol,palace:p.id,
                    month:month,catalog:powerCatalog,stages:stages).strength ?? "待核"
        }
        func stemPower(_ stem:String,_ p:WenguaNativePalace) throws ->String {
            if let carrier=p.heavenStars.first(where:{$0.carriedStem==stem}) {
                return try sourceStrength("stem",stem,p,carrier.stages)
            }
            if p.earthStem==stem {
                return try sourceStrength("stem",stem,p,p.earthStages)
            }
            return "待核"
        }
        let birdPower=try bird.map{ _ in try sourceStrength("star","天禽星",illness)} ?? "待核"
        let birdStemPower=try bird.map{try stemPower($0,illness)} ?? "待核"
        let illnessPower=try sourceStrength("star","天芮星",illness)
        let doorPower=try sourceStrength("door",door,illness)
        let skyPower=try stemPower(sky,illness)
        let earthPower=try sourceStrength("stem",illness.earthStem,illness,illness.earthStages)
        let actorCarrier=actor.mainStem=="甲"
            ? (actor.sourceGanzhi.flatMap{WenguaNativeActorSource.jiaCarrier($0)} ?? "")
            : actor.mainStem
        let patientPower:String
        if actorCarrier.isEmpty { patientPower="待核" }
        else { patientPower=try stemPower(actorCarrier,patientPalace) }
        let injuryPower=try sourceStrength("door","伤门",injury)
        let hourPower=try stemPower(hourStem,hourPalace)
        let deityElement=WenguaVNextEngine.godElement[deity]
        guard let godElement=deityElement,
              let palaceElement=WenguaVNextEngine.elements[illness.id],
              let godRelation=try? WenguaVNextEngine.directed(godElement,palaceElement),
              let deityPower=WenguaVNextEngine.godTiers[godRelation] else {
            throw WenguaNativeReadingError.missingRole
        }
        func formation(_ top:String,_ bottom:String)->String? {
            for line in pairText.split(separator:"\n").dropFirst() {
                let cells=line.split(separator:"|",omittingEmptySubsequences:false)
                if cells.count>=4 && cells[0]==top && cells[1]==bottom {
                    return String(cells[2])
                }
            }
            return nil
        }
        guard let mainFormation=formation(sky,illness.earthStem) else {
            throw WenguaNativeReadingError.missingPhrases
        }
        var formationNames=[mainFormation]
        if let bird,let centre=chart.palaces.first(where:{$0.id==5}),
           let hostedFormation=formation(bird,centre.earthStem) {
            formationNames.append(hostedFormation)
        }
        func isProminent(_ tier:String)->Bool {
            ["极大","大"].contains(tier)
        }
        func voidState(_ p:WenguaNativePalace)->String {
            if p.voidBranches.isEmpty {return "not_void"}
            if p.id==chart.hourHorsePalace {return "fake_void"}
            if p.voidBranches.contains(where:{
                WenguaVNextEngine.clash[$0]==chart.hourHorse
            }) {return "not_void"}
            guard let pe=WenguaVNextEngine.elements[p.id] else {
                return "true_void"
            }
            return (month==pe || WenguaVNextEngine.generates[month]==pe)
                ? "fake_void" : "true_void"
        }
        let illnessVoid=voidState(illness)
        let illnessFocus=illnessVoid=="true_void"
            ? "病星逢真空，即使原力较大，此处病位显象也受限"
            : illnessVoid=="fake_void"
                ? "病宫假空，原始力量须结合空亡条件看"
                : isProminent(illnessPower)
            ? "病星自身力量较足，这一宫的病位线索较突出"
            : illnessPower=="中等" ? "病星力量居中，此处取作主要病位"
            : ["小","极小"].contains(illnessPower)
                ? "病星力量偏弱，这里的不适象不宜夸大"
                : "病星力量未能定档，病位轻重不作强断"
        let injuryFocus=isProminent(injuryPower)
            ? "伤门自身力量较足，筋骨牵扯的旁象较显"
            : ["小","极小"].contains(injuryPower)
                ? "伤门力量偏弱，筋骨牵扯只作轻微旁象"
                : "伤门仅作独立的筋骨与动作线索"
        let hourFocus=isProminent(hourPower)
            ? "时干作用较显，病事宫可进一步核对"
            : "时干力量不强，不把其余宫位扩大为主病位"
        let secondaryFocus=injury.id==illness.id
            ? "伤门也在病星宫，门象与病位同处一宫"
            : "另宫伤门在"+label(injury)+"宫，"+injuryFocus
        let locationFocus=isProminent(skyPower)
            ? "天芮携干之势较足，可优先细查相应部位"
            : ["小","极小"].contains(skyPower)
                ? "携干力量较弱，其对应部位只作次线"
                : "携干所示部位作为分辨线索"
        let doorElem=WenguaVNextEngine.doorElement[door] ?? ""
        let palaceElem=WenguaVNextEngine.elements[illness.id] ?? ""
        let doorRel=try? WenguaVNextEngine.directed(doorElem,palaceElem)
        let restrictionFocus=doorRel=="宫克符号"
            ? "门受宫迫，相关门象须减看" :
            doorRel=="符号克宫" ? "门克本宫，门象另有破局限制" :
            "门宫无迫克限制"
        // V18: choose *where*, not how badly. Raw five-tier source power
        // ranks distinct physical symbol evidence without exposing a severity.
        let bodyAnchors=["肩","耳","臂","手","头","眼","鼻","面","颈","喉",
                         "胸","心","肺","脾","肝","胆","胃","肠","肾","腹",
                         "腰","腿","足","脚","膝","股","背","筋","骨","皮",
                         "肤","膀胱","阴","胰","血管","食道","经络","脑"]
        func parts(_ raw:String)->[String] {
            let bits=raw.replacingOccurrences(of:"／",with:"/")
                .replacingOccurrences(of:"、",with:"/")
                .replacingOccurrences(of:"，",with:"/")
                .split(separator:"/").map(String.init)
            var unique:[String]=[]
            for bit in bits {
                let word=bit.trimmingCharacters(in:.whitespacesAndNewlines)
                if !word.isEmpty && !unique.contains(word) &&
                   !["病","疾","风","寒","症","虚","咳","疝"].contains(where:{word.contains($0)}) {
                    unique.append(word)
                }
            }
            return unique
        }
        func sameSite(_ a:String,_ b:String)->Bool {
            a==b || a.contains(b) || b.contains(a) ||
                bodyAnchors.contains(where:{ a.contains($0) && b.contains($0) })
        }
        func tier(_ value:String)->Int {
            ["极小","小","中等","大","极大"].firstIndex(of:value).map{$0+1} ?? 0
        }
        let originalSites=parts(primary)
        guard !originalSites.isEmpty else {throw WenguaNativeReadingError.missingRole}
        let alternateSites=parts(external)
        let skySites=parts((secret+viscera+surface).joined(separator:"/"))
        let earthSites=parts(skyOther.joined(separator:"/"))
        let birdSites=parts(birdOther.joined(separator:"/"))
        // Identical sky glyph from one physical symbol and its three textual
        // source families count once. Sky, earth and Tianqin are independent.
        func matched(_ candidate:String,_ sites:[String])->Bool {
            sites.contains(where:{sameSite(candidate,$0)})
        }
        let ranked:[(String,Int,Int)]=originalSites.enumerated().map{ entry in
            let index=entry.offset
            let site=entry.element
            var rank=tier(illnessPower)
            if illnessVoid=="true_void" {rank=0}
            if illnessVoid=="fake_void" {rank=max(0,rank-1)}
            if matched(site,alternateSites){rank+=2}
            if matched(site,skySites){rank+=tier(skyPower)}
            if matched(site,earthSites){rank+=tier(earthPower)}
            if matched(site,birdSites){rank+=tier(birdStemPower)}
            return (site,rank,index)
        }.sorted{ $0.1==$1.1 ? $0.2<$1.2 : $0.1>$1.1 }
        let leadSites=ranked.prefix(2).map{$0.0}
        let lead=leadSites.joined(separator:"、")
        let remaining=ranked.dropFirst(2).map{$0.0}
        let supportedAlt=alternateSites.filter{ site in
            !leadSites.contains(where:{sameSite(site,$0)}) &&
            (matched(site,skySites) || matched(site,earthSites) ||
             matched(site,birdSites))
        }
        let secondary=(remaining+supportedAlt).reduce(into:[String]()){items,part in
            if !items.contains(where:{sameSite($0,part)}) {items.append(part)}
        }
        let secondSite=secondary.prefix(2).joined(separator:"、")
        let focusedDetails=[("天芮携"+sky,skySites,skyPower),
                            ("地盘"+illness.earthStem,earthSites,earthPower),
                            ("天禽携"+(bird ?? ""),birdSites,birdStemPower)]
            .compactMap{ evidence ->String? in
                let tag=evidence.0
                let sites=evidence.1
                let power=evidence.2
                guard tier(power)>0,
                      let site=sites.first(where:{matched($0,leadSites)})
                else{return nil}
                return tag+"亦见"+site
            }
        let detailLine=focusedDetails.isEmpty ? "" :
            focusedDetails.joined(separator:"，")+"。"
        let otherLine=secondSite.isEmpty ? "" :
            "同宫另一处可兼看"+secondSite+"。"
        // The casting actor is *not* another Tianrui disease site.
        // A father has Qian auxiliary; an older sister does not acquire
        // eldest-daughter status without verified birth order.
        func sourceLocation(_ p:WenguaNativePalace)->[String] {
            let code=label(p)
            let scope=(chart.bureau.dun=="yang" ? innerYang:innerYin).contains(p.id)
                ? "体内" : "体表"
            let rows=allRules.filter{
                ($0["类别"] as? String)=="九宫定位" &&
                ($0["子类"] as? String)=="神奇之门-"+scope &&
                ($0["符号组合"] as? String)==code+"·"+scope
            }
            return rows.count==1 ? parts(rows[0]["古籍象意或候选"] as? String ?? "") : []
        }
        let actorOverlap=patientPalace.id==illness.id ? nil :
            sourceLocation(patientPalace).first{matched($0,leadSites)}
        var actorLine=""
        if let actorOverlap {
            actorLine=relationship+"用神"+actor.mainStem+"在"+label(patientPalace)+
                "宫，该宫亦见"+actorOverlap+"。"
        }
        if relationship=="父亲",let qian=chart.palaces.first(where:{$0.id==6}),
           qian.id != illness.id,qian.id != patientPalace.id {
            let corroboration=sourceLocation(qian).first{matched($0,leadSites)}
            if let corroboration {
                actorLine+="父亲乾六宫另见"+corroboration+"。"
            }
        }
        let limbSites=["肩","臂","手","足","腿","背","膝","筋","骨","腰","股"]
        let injuryCorroborates=injury.id==illness.id
        let injuryMatching=leadSites.contains{site in
            limbSites.contains(where:{site.contains($0)})
        }
        let injuryCross=sourceLocation(injury).first{matched($0,leadSites)}
        let injuryLine:String
        if injuryCorroborates && injuryMatching {
            injuryLine="伤门也在"+label(illness)+"宫，与肢体部位相接。"
        } else if !injuryCorroborates,tier(injuryPower)>=3,
                  let overlap=injuryCross {
            injuryLine="另看"+label(injury)+"宫的伤门，亦指"+overlap+"。"
        } else {
            injuryLine=""
        }
        let ending=secondSite.isEmpty ? "。" : "；另参"+secondSite+"。"
        let conclusion=String(format:"综上，%@本次病位首先看%@%@这是传统部位取象，不等于医学诊断。",
                              relationship,lead,ending)
        let values:[String:String]=[
            "palace":palaceName,"dun":chart.bureau.dun=="yang" ? "阳":"阴",
            "sector":sector,"region":region,"primary":primary,"external":external,
            "door":door,"deity":deity,"sky":sky,"earth":illness.earthStem,
            "companion":bird.map{"同宫天禽星力"+birdPower+"，其携"+$0+"之干力"+birdStemPower+"，另见"+birdOther.joined(separator:"、")} ?? "本宫没有独立的天禽携干",
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
            "patient_relation":"患者宫与病宫的关系为"+palaceRelation(patientPalace),
            "patient_coincidence":patientPalace.id==illness.id ? "两个用神在同一实宫，应合看但不重复计位" : "患者宫另有宫象，不能据此改写天芮所定部位",
            "natal_scope":actor.natalStem.map{"另知年命"+$0+"，须按真实年命位置另看"} ?? "出生年命未提供，因此不额外指定年命宫",
            "injury_deity":injury.deity ?? "无神",
            "illness_power":illnessPower,"door_power":doorPower,
            "deity_power":deityPower,"sky_power":skyPower,
            "earth_power":earthPower,"patient_power":patientPower,
            "injury_power":injuryPower,"hour_power":hourPower,
            "formation":formationNames.joined(separator:"、"),
            "restriction_focus":restrictionFocus,
            "illness_focus":illnessFocus,"injury_focus":injuryFocus,
            "hour_focus":hourFocus,"secondary_focus":secondaryFocus,
            "location_focus":locationFocus,
            "injury_relation":palaceRelation(injury),
            "hour_relation":palaceRelation(hourPalace),
            "focus_site":lead,"site_detail":detailLine,
            "site_secondary":otherLine,"actor_site":actorLine,
            "injury_site":injuryLine,"final_site":conclusion
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
            if output.trimmingCharacters(in:.whitespacesAndNewlines).isEmpty {
                continue
            }
            sections.append(WenguaNativeCustomerSection(id:required[i],title:title,text:output))
        }
        guard sections.first?.id=="01_location",
              sections.last?.id=="06_conclusion",sections.count>=2 else {
            throw WenguaNativeReadingError.invalidPhrase
        }
        return WenguaNativeCustomerReading(
            version:"discomfort_v18_location_only_rank_20261101",
            topicID:"health.discomfort",relationship:relationship,iso:chart.iso,
            evidenceStatus:"traditional_textual_location_not_medical_diagnosis",
            sections:sections,rolePalaces:["illness":illness.id,"patient":actor.mainPalace,
                                          "injury":injury.id,"hour":hourPalace.id])
    }
}
