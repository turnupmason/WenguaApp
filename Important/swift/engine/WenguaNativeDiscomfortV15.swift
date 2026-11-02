import Foundation

// Independent offline body-SITE reader. It never calls V8 severity and
// cannot treat the 255 historic rules as 255 positive clinical observations.
enum WenguaNativeDiscomfortV15 {
    static let allowedContexts:Set<String>=[
        "none","accident","bone","bleeding","severe_pain","surgery"
    ]
    private static let physical = Set([1,2,3,4,6,7,8,9])
    private static let innerYang = Set([1,8,3,4])
    private static let innerYin = Set([9,2,7,6])

    static func compose(chart:WenguaNativeChart, relationship:String,
                        actor:WenguaNativeActor, injuryContext:String,
                        bundle:Bundle = .main) throws
                        -> WenguaNativeCustomerReading {
        guard let rulesURL=bundle.url(forResource:"complete_255_rules_v15_20261101",withExtension:"json"),
              let stemsURL=bundle.url(forResource:"three_source_stem_variants_v14_20261101",withExtension:"json"),
              let templateURL=bundle.url(forResource:"native_discomfort_v15",withExtension:"json"),
              let energyURL=bundle.url(forResource:"health_energy_200",withExtension:"json"),
              let pairsURL=bundle.url(forResource:"81_pairs",withExtension:"tsv") else {
            throw WenguaNativeReadingError.missingPhrases
        }
        return try compose(chart:chart,relationship:relationship,actor:actor,
                           injuryContext:injuryContext,rules:Data(contentsOf:rulesURL),
                           stems:Data(contentsOf:stemsURL),
                           template:Data(contentsOf:templateURL),
                           energy:Data(contentsOf:energyURL),
                           pairs:Data(contentsOf:pairsURL))
    }

    // Exposed as a pure data-in function for parity fixtures and fail-closed tests.
    static func compose(chart:WenguaNativeChart, relationship:String,
                        actor:WenguaNativeActor, injuryContext:String,
                        rules:Data, stems:Data, template:Data,
                        energy:Data, pairs:Data) throws
                        -> WenguaNativeCustomerReading {
        guard allowedContexts.contains(injuryContext) else {
            throw WenguaNativeReadingError.unsupportedTopic
        }
        let useInjury=injuryContext != "none"
        let trauma=["accident","bone","bleeding"].contains(injuryContext)
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
              words["schema"] as? String=="wengua_health_discomfort_native_v26_precise_injury_speech_20261101",
              let paragraphs=words["sections"] as? [[String:String]], paragraphs.count==9,
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
            // V24 health.discomfort only. Two real branch stages are each
            // looked up from the immutable original 200 cells, with the
            // user-approved upper tier chosen for interpretation.
            // DO NOT change the frozen V8 shared factor/scoring engine.
            if kind=="stem" && stages.count>1 {
                let levels=["极小","小","中等","大","极大"]
                let powers=try stages.map { stage ->String in
                    guard let tier=try WenguaVNextEngine.factor(
                        kind:"stem",symbol:symbol,palace:p.id,
                        month:month,catalog:powerCatalog,
                        stages:[stage]).strength,
                          levels.contains(tier) else {
                        throw WenguaNativeReadingError.missingPhrases
                    }
                    return tier
                }
                return powers.max { left,right in
                    levels.firstIndex(of:left)!<levels.firstIndex(of:right)!
                }!
            }
            return try WenguaVNextEngine.factor(kind:kind,symbol:symbol,palace:p.id,
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
        // Six-Jia's true identity is 甲 (wood); its carrier only locates the
        // physical cell. Read 甲's own stages and original stem 200 grid.
        func actualRolePower(_ stem:String,_ carrier:String,
                             _ p:WenguaNativePalace,
                             _ sourceGanzhi:String?) throws ->String {
            if stem=="甲" {
                guard let sourceGanzhi,
                      WenguaNativeActorSource.validatedGanzhi(sourceGanzhi),
                      WenguaNativeActorSource.jiaCarrier(sourceGanzhi)==carrier,
                      let originalStages=WenguaNativeCore.stages["甲"] else {
                    return "待核"
                }
                let liveStages=p.branches.compactMap { branch -> WenguaNativeStage? in
                    guard let name=originalStages[branch] else {return nil}
                    return WenguaNativeStage(branch:branch,stage:name)
                }
                guard liveStages.count==p.branches.count else {return "待核"}
                return try sourceStrength("stem","甲",p,liveStages)
            }
            return try stemPower(carrier,p)
        }
        let birdPower=try bird.map{ _ in try sourceStrength("star","天禽星",illness)} ?? "待核"
        let birdStemPower=try bird.map{try stemPower($0,illness)} ?? "待核"
        let illnessPower=try sourceStrength("star","天芮星",illness)
        // The physically co-located door is always read, including its
        // true 门克宫 pressure; selecting independent 伤门 is a separate gate.
        let doorPower=try sourceStrength("door",door,illness)
        let skyPower=try stemPower(sky,illness)
        let earthPower=try sourceStrength("stem",illness.earthStem,illness,illness.earthStages)
        let actorCarrier=actor.mainStem=="甲"
            ? (actor.sourceGanzhi.flatMap{WenguaNativeActorSource.jiaCarrier($0)} ?? "")
            : actor.mainStem
        let patientPower:String
        if actorCarrier.isEmpty { patientPower="待核" }
        else {
            patientPower=try actualRolePower(actor.mainStem,actorCarrier,
                                            patientPalace,actor.sourceGanzhi)
        }
        let injuryPower=useInjury ?
            try sourceStrength("door","伤门",injury) : "待核"
        let hourCarrier=hourStem=="甲" ?
            (WenguaNativeActorSource.jiaCarrier(chart.pillars.hour) ?? "") : hourStem
        let hourPower=try actualRolePower(hourStem,hourCarrier,
                                         hourPalace,chart.pillars.hour)
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
        let restrictionFocus=doorRel=="符号克宫"
            ? "门克落宫，构成门迫" :
            doorRel=="宫克符号" ? "宫克门，门受制而非门迫" :
            "门宫无相克限制"
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
                if !word.isEmpty && word != "头发" && !unique.contains(word) &&
                   !["病","疾","风","寒","症","虚","咳","疝"].contains(where:{word.contains($0)}) {
                    unique.append(word)
                }
            }
            return unique
        }
        func sameSite(_ a:String,_ b:String)->Bool {
            // Opposite laterality is not the same body site.
            if (a.contains("左") && b.contains("右")) ||
               (a.contains("右") && b.contains("左")) {return false}
            return a==b || a.contains(b) || b.contains(a) ||
                bodyAnchors.contains(where:{ a.contains($0) && b.contains($0) })
        }
        func tier(_ value:String)->Int {
            ["极小","小","中等","大","极大"].firstIndex(of:value).map{$0+1} ?? 0
        }
        func sourceLocation(_ p:WenguaNativePalace)->[String] {
            let code=label(p)
            let scope=(chart.bureau.dun=="yang" ? innerYang:innerYin).contains(p.id)
                ? "体内" : "体表"
            let rows=allRules.filter{
                ($0["类别"] as? String)=="九宫定位" &&
                ($0["子类"] as? String)=="神奇之门-"+scope &&
                ($0["符号组合"] as? String)==code+"·"+scope &&
                ($0["证据级别"] as? String)?.hasPrefix("A")==true
            }
            return rows.count==1 ? parts(rows[0]["古籍象意或候选"] as? String ?? "") : []
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

        // Source energy 200 determines symbol salience. 墓/刑 raise a
        // matching site's traditional concern, never V8 severity or source power.
        func badSigns(_ stem:String,_ p:WenguaNativePalace)->[String] {
            var result:[String]=[]
            if p.tombs.contains(where:{$0.stem==stem}) {result.append("入墓")}
            if p.heavenStars.contains(where:{$0.carriedStem==stem}) &&
               WenguaVNextEngine.striking[stem]==p.id {result.append("六仪击刑")}
            return result
        }
        var auxiliaries:[(WenguaNativePalace,String,String)]=[]
        let auxIDs=Set([actor.siblingAuxiliaryPalace,actor.genderPalace,
                        actor.natalPalace].compactMap{$0})
        for id in auxIDs.sorted() where physical.contains(id) {
            if let p=chart.palaces.first(where:{$0.id==id}),
               let star=p.heavenStars.first {
                auxiliaries.append((p,star.star,try sourceStrength("star",star.star,p)))
            }
        }
        var otherDoors:[(WenguaNativePalace,String,String)]=[]
        for p in chart.palaces where physical.contains(p.id) &&
             p.id != illness.id && p.id != injury.id {
            if let d=p.door {
                otherDoors.append((p,d,try sourceStrength("door",d,p)))
            }
        }
        // A genuinely separate location may enter only when (a) a strong
        // source sign is in true stem-specific tomb/striking, OR (b) a second,
        // distinct physical palace independently corroborates the same site.
        // Thus a single attractive door does not invent extra organs.
        let injurySites=useInjury ? sourceLocation(injury) : []
        guard !useInjury || !injurySites.isEmpty else {
            throw WenguaNativeReadingError.missingRole
        }
        let witnesses:[(WenguaNativePalace,String,String)]=[
            (patientPalace,actorCarrier,patientPower),
            (hourPalace,hourCarrier,hourPower)] +
            (useInjury ? [(injury,"伤门",injuryPower)] : []) +
            auxiliaries
        // Other doors may corroborate the chosen site, but must not
        // manufacture new distant organs by agreeing with one another.
        // An actual reported injury/bone damage/bleeding selects the true
        // 伤门 *palace* as the principal traditional site. No inferred diagnosis.
        var candidateSites=trauma ? injurySites : originalSites
        if trauma {
            for site in originalSites where !matched(site,candidateSites) {
                candidateSites.append(site)
            }
        }
        // Severe pain / surgery: 伤门 is a required conditional witness,
        // but ONLY explicit trauma / bone damage / bleeding can promote
        // the independent injury palace ahead of the real Tianrui site.
        // V21: patient, hour and auxiliary palaces are witnesses, NOT new
        // body-site origins. Even a strong striking symbol cannot overwrite
        // the Tianrui/explicit-injury primary location with a remote organ.
        let ranked:[(String,Int,Int)]=candidateSites.enumerated().map{ entry in
            let site=entry.element
            var rank=matched(site,originalSites) ? tier(illnessPower) : 0
            if trauma && matched(site,injurySites) {
                // Priority class, not an invented 200-cell source strength or
                // a symptom/severity score. Preserve source five-tier within.
                rank+=25+tier(injuryPower)
            }
            if matched(site,originalSites) && illnessVoid=="true_void" {rank=0}
            if matched(site,originalSites) && illnessVoid=="fake_void" {rank=max(0,rank-1)}
            if matched(site,alternateSites){rank+=2}
            if matched(site,skySites) {
                rank+=tier(skyPower)
                if !badSigns(sky,illness).isEmpty {rank+=5}
            }
            if matched(site,earthSites) {
                rank+=tier(earthPower)
                if !badSigns(illness.earthStem,illness).isEmpty {rank+=5}
            }
            if let bird,matched(site,birdSites) {
                rank+=tier(birdStemPower)
                if !badSigns(bird,illness).isEmpty {rank+=5}
            }
            var counted:Set<String>=[]
            for (p,stem,power) in [(patientPalace,actorCarrier,patientPower),
                                   (hourPalace,hourStem,hourPower)]
                    where p.id != illness.id {
                let key=String(p.id)+"/"+stem
                if matched(site,sourceLocation(p)) && counted.insert(key).inserted {
                    rank+=tier(power)
                    if !badSigns(stem,p).isEmpty {rank+=5}
                }
            }
            if useInjury && injury.id != illness.id &&
               matched(site,injurySites) {
                rank+=tier(injuryPower)
            }
            for (p,star,power) in auxiliaries where p.id != illness.id {
                let key=String(p.id)+"/"+star
                if matched(site,sourceLocation(p)) && counted.insert(key).inserted {
                    rank+=tier(power)
                }
            }
            for (p,doorName,power) in otherDoors
                    where matched(site,sourceLocation(p)) {
                let key=String(p.id)+"/door/"+doorName
                if counted.insert(key).inserted {rank+=tier(power)}
            }
            return (site,rank,entry.offset)
        }.sorted{ $0.1==$1.1 ? $0.2<$1.2 : $0.1>$1.1 }
        // The selected injury palace gets a location even when its door
        // strength is small: low force limits emphasis, not anatomy evidence.
        let leadSites=ranked.prefix(1).map{$0.0}
        let lead=leadSites.joined(separator:"、")
        let remaining=ranked.dropFirst(2).map{$0.0}
        let supportedAlt=alternateSites.filter{ site in
            !leadSites.contains(where:{sameSite(site,$0)}) &&
            (matched(site,skySites) || matched(site,earthSites) ||
             matched(site,birdSites))
        }
        let injurySecondary=useInjury && !trauma ?
            ranked.map{$0.0}.filter{matched($0,injurySites) &&
                !matched($0,leadSites)}.prefix(1).map{$0} : []
        let secondary=(injurySecondary+remaining+supportedAlt)
            .reduce(into:[String]()){items,part in
            if !items.contains(where:{sameSite($0,part)}) {items.append(part)}
        }
        // Keep secondary evidence for audit, never append a different
        // anatomical region merely to fill a customer-facing second clause.
        let secondSite=""
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
"另有部位线索可兼看"+secondSite+"。"
        // The casting actor is *not* another Tianrui disease site.
        // A father has Qian auxiliary; an older sister does not acquire
        // eldest-daughter status without verified birth order.
        let actorOverlap=patientPalace.id==illness.id ? nil :
            sourceLocation(patientPalace).first{matched($0,leadSites)}
        var actorLine=""
        if let actorOverlap {
            actorLine=String(format:"%@用神%@在%@宫，该宫亦见%@。",
                             relationship,actor.mainStem,label(patientPalace),actorOverlap)
        }
        if relationship=="父亲",let qian=chart.palaces.first(where:{$0.id==6}),
           qian.id != illness.id,qian.id != patientPalace.id {
            let corroboration=sourceLocation(qian).first{matched($0,leadSites)}
            if let corroboration {
                actorLine+="父亲乾六宫另见"+corroboration+"。"
            }
        }
        // Only actual, user-confirmed trauma, pain or surgery activates
        // the *physical* injury palace. Never infer that bone is broken.
        let injuryReason:[String:String]=[
            "accident":"意外受伤","bone":"骨肉受损",
            "bleeding":"伤口或出血","severe_pain":"剧烈疼痛",
            "surgery":"已做或拟做手术"
        ]
        let selectedInjurySites=(trauma ?
            ranked.map{$0.0}.filter{matched($0,injurySites)} :
            injurySites).prefix(1).map{$0}
        let injurySiteNames=selectedInjurySites.joined(separator:"、")
        let injuryScope=(chart.bureau.dun=="yang" ? innerYang:innerYin)
            .contains(injury.id) ? "体内" : "体表"
        let injuryOverlap=injurySites.first(where:{matched($0,originalSites)})
        let injuryRelation:String
        if injury.id==illness.id {
            injuryRelation="伤门与天芮同宫，两条线索落在同一处。"
        } else if let match=injuryOverlap {
            injuryRelation="两宫同指\(match)，因此这处有交叉印证。"
        } else {
            injuryRelation="天芮另在\(label(illness))宫，两宫须分别取证。"
        }
        let openPalace=chart.palaces.first(where:{$0.door=="开门"})
        let surgicalControl=injuryContext=="surgery" &&
            openPalace.map { p in
                p.id != injury.id &&
                WenguaVNextEngine.controls[
                    WenguaVNextEngine.elements[p.id] ?? ""] ==
                    WenguaVNextEngine.elements[injury.id]
            } == true
        let surgicalClue:String
        if surgicalControl,let opening=openPalace {
            surgicalClue="开门所在\(label(opening))宫五行克伤门宫，传统上有医伤相制之象，不据此认定必须手术。"
        } else {surgicalClue=""}
        // Inspect the activated 伤门 palace, not the meaning of the
        // character 伤: its stars, carried stems, ground stem, deity,
        // door-palace relation, tomb/striking and real 81 formation.
        // Each 200-grid factor is evaluated for its OWN physical symbol.
        var injuryRoomEvidence:[String]=[]
        if useInjury {
            for star in injury.heavenStars {
                let starPower=try sourceStrength("star",star.star,injury)
                let carrierPower=try stemPower(star.carriedStem,injury)
                let candidates=parts((mapping[star.carriedStem]?["qimen_secret_vol13"] ?? [])
                    .joined(separator:"/"))
                if tier(starPower)>=2 && tier(carrierPower)>=2,
                   let site=candidates.first(where:{matched($0,selectedInjurySites)}) {
                    injuryRoomEvidence.append(
                        "宫中\(star.star)携\(star.carriedStem)的部位干象也取\(site)，故这处有星与干的同宫互证。")
                }
            }
            let earthPower=try sourceStrength("stem",injury.earthStem,
                                               injury,injury.earthStages)
            let earthSites=parts((mapping[injury.earthStem]?["qimen_secret_vol13"] ?? [])
                .joined(separator:"/"))
            if tier(earthPower)>=2,
               let site=earthSites.first(where:{matched($0,selectedInjurySites)}) {
                injuryRoomEvidence.append(
                    "地盘\(injury.earthStem)的独立干象也指\(site)，再收窄到这一带。")
            }
            if injury.deity=="白虎" {
                injuryRoomEvidence.append(
                    "该宫同时临白虎，仅构成传统伤损同宫条件，不足以确认出血、骨折或手术必要性。")
            }
            if let injDoor=WenguaVNextEngine.doorElement["伤门"],
               let pe=WenguaVNextEngine.elements[injury.id],
               (try? WenguaVNextEngine.directed(injDoor,pe))=="符号克宫" {
                injuryRoomEvidence.append("伤门木克本宫土而成门迫，伤损部位线索须结合宫内星干审看。")
            }
            let activeSigns=Set(injury.tombs.map{$0.stem})
            if injury.heavenStars.contains(where:{ activeSigns.contains($0.carriedStem) }) ||
               activeSigns.contains(injury.earthStem) {
                injuryRoomEvidence.append("此宫实见携干或地盘干入墓，相关部位暂不单凭一条线索定死。")
            }
        }
        let injuryLimit:String
        if voidState(injury)=="true_void" {
            injuryLimit="伤门宫真空，须减看这一处的部位依据。"
        } else if tier(injuryPower)<=2 {
            injuryLimit="伤门自身取力偏弱，这处仍须其他符号印证。"
        } else {injuryLimit=""}
        let injuryFull:String
        if useInjury {
            let reason=injuryReason[injuryContext] ?? "特殊情况"
            let dn=chart.bureau.dun=="yang" ? "阳" : "阴"
            injuryFull="此次\(reason)，伤门落\(label(injury))宫，\(dn)遁\(injuryScope)取\(injurySiteNames)；\(injuryRelation)\(injuryRoomEvidence.joined())\(injuryLimit)\(surgicalClue)"
        } else {injuryFull=""}
        let doorsConfirming=otherDoors.filter { entry in
            tier(entry.2)>=2 && sourceLocation(entry.0).contains(where:{
                matched($0,leadSites)
            })
        }.sorted{tier($0.2)>tier($1.2)}
        let doorsFull=doorsConfirming.prefix(2).compactMap { entry ->String? in
            guard let hit=sourceLocation(entry.0).first(where:{
                matched($0,leadSites)
            }) else {return nil}
            return "\(entry.1)在\(label(entry.0))宫，该宫也取\(hit)，与已选病位重合，故可作为另一宫的交叉印证。"
        }.joined()
        let hourMatch=sourceLocation(hourPalace).first(where:{matched($0,leadSites)})
        let hourFull:String
        if hourPalace.id==illness.id && patientPalace.id==illness.id &&
           actorCarrier==hourCarrier {
            hourFull=""
        } else if hourPalace.id==illness.id {
            hourFull="时干\(hourStem)也落\(label(hourPalace))宫，与病星同宫参看。"
        } else if let hit=hourMatch {
            hourFull="时干\(hourStem)落\(label(hourPalace))宫，亦指\(hit)，与主位相互印证。"
        } else {
            hourFull="时干\(hourStem)落\(label(hourPalace))宫，与天芮分宫。"
        }
        let actorSiteHit=sourceLocation(patientPalace).first(where:{
            matched($0,leadSites)
        })
        let personFull:String
        if patientPalace.id==illness.id && hourPalace.id==illness.id &&
           actorCarrier==hourCarrier {
            personFull="\(relationship)用神\(actor.mainStem)就是时干，二者同符同落\(label(illness))宫，与天芮合看，不重复计位。"
        } else if patientPalace.id==illness.id {
            personFull="\(relationship)用神\(actor.mainStem)在\(label(illness))宫，与天芮同宫。"
        } else if patientPalace.id==hourPalace.id && actorCarrier==hourCarrier {
            personFull="\(relationship)用神\(actor.mainStem)与时干同属一干，落\(label(patientPalace))宫。"
        } else if let hit=actorSiteHit {
            personFull="\(relationship)用神\(actor.mainStem)在\(label(patientPalace))宫，另见\(hit)，与主位相合。"
        } else {
            personFull="\(relationship)用神\(actor.mainStem)在\(label(patientPalace))宫，与病星分宫取证。"
        }
        let auxFull=auxiliaries.map { entry ->String in
            let p=entry.0
            let name=p.id==actor.siblingAuxiliaryPalace ? "已确认的亲属排行辅助" :
                     p.id==actor.genderPalace ? "\(relationship)长辈辅宫" : "已提供的年命"
            if p.id==patientPalace.id || p.id==illness.id {
                return "\(name)在\(label(p))宫，与已取实宫相同，不另计一次。"
            }
            if let hit=sourceLocation(p).first(where:{matched($0,leadSites)}) {
                return "\(name)在\(label(p))宫，也见\(hit)，作为旁证。"
            }
            return "\(name)在\(label(p))宫，与主位分开参看。"
        }.joined()
        // A real sky symbol, earth symbol and (if physically hosted)
        // Tianqin carrier each retain independent original source power.
        // This is disease *imagery* attached to this palace, not a new
        // anatomical location or a clinical claim about pain intensity.
        // V24 original 200 source audit: two branch cells are both read,
        // and the higher ORIGINAL tier is selected for this one topic only. Every listed branch is real.
        func stemBranchFacts(_ stem:String,_ p:WenguaNativePalace,
                             _ stages:[WenguaNativeStage]) throws ->[(String,String)] {
            guard !stages.isEmpty else {throw WenguaNativeReadingError.missingPhrases}
            return try stages.map { stage in
                let power=try sourceStrength("stem",stem,p,[stage])
                guard tier(power)>0 else {throw WenguaNativeReadingError.missingPhrases}
                return (stage.branch+stage.stage,power)
            }
        }
        func selectedStemImage(_ stem:String,_ power:String,
                               _ stages:[WenguaNativeStage]) throws ->String {
            let candidates=parts((mapping[stem]?["qimen_secret_vol13"] ?? [])
                .joined(separator:"/"))
            let original=candidates.first(where:{matched($0,leadSites)}) ??
                         candidates.first ?? "无已核实的细部候选"
            let selected=original=="脏（笼统）" ? "脏腑泛象" : original
            _ = try stemBranchFacts(stem,illness,stages)
            return selected+"，力量"+power
        }
        // 81 grid is ordered sky + ground. Preserve the actual source name,
        // luck and gist; generic commercial idioms MUST NOT be turned into
        // an invented diagnosis. Tianqin's second pair takes the real centre
        // earth carrier, not the illness's ground stem a second time.
        func formationMeaning(_ top:String,_ ground:String)->String? {
            for line in pairText.split(separator:"\n").dropFirst() {
                let cells=line.split(separator:"|",omittingEmptySubsequences:false)
                if cells.count>=6 && cells[0]==top && cells[1]==ground {
                    // Keep the exact ancient title in immutable source TSV;
                    // a nonmedical sexually charged historical idiom must
                    // not become a disease label for an ordinary user.
                    let rawName=String(cells[2])
                    let name=rawName=="幼女奸淫" ? "壬加癸旧格" : rawName
                    let nature=String(cells[3])
                    // The literal historical 81-grid gist is preserved in
                    // the source TSV, but unrelated business/marriage words
                    // cannot be presented as if they were disease names.
                    let reading:String
                    if name.contains("伏吟") {reading="同干重叠，取缠滞反复之象"}
                    else if ["网","狱","牢","罗","困","地户","墓"].contains(where:{name.contains($0)}) {
                        reading="受困闭滞，取不畅之象"
                    } else if ["蛇","缠","夭矫"].contains(where:{name.contains($0)}) {
                        reading="纠缠牵扯，取反复之象"
                    } else if ["刑","伤","折","破","克"].contains(where:{name.contains($0)}) {
                        reading="上下干相制，取受损牵制之象"
                    } else if ["合","生","佐","返首","耀明"].contains(where:{name.contains($0)}) {
                        reading="两干相助，取有缓解条件之象"
                    } else {
                        reading=nature=="吉" ? "两干有相助之象" : "两干有牵制之象"
                    }
                    return "\(name)，\(nature)格，\(reading)"
                }
            }
            return nil
        }
        var orderedFormations:[String]=[]
        if let meaning=formationMeaning(sky,illness.earthStem) {
            orderedFormations.append("天盘\(sky)加地盘\(illness.earthStem)为"+meaning)
        }
        if let bird,let centre=chart.palaces.first(where:{$0.id==5}),
           let meaning=formationMeaning(bird,centre.earthStem) {
            orderedFormations.append("天禽携\(bird)加寄宫地干\(centre.earthStem)为"+meaning)
        }
        let skyText="天盘\(sky)主\(try selectedStemImage(sky,skyPower,illnessStar.stages))"
        let earthText="地盘\(illness.earthStem)主\(try selectedStemImage(illness.earthStem,earthPower,illness.earthStages))"
        let birdText:String
        if let bird {
            guard let hostStar=illness.heavenStars.first(where:{$0.star=="天禽星"}) else {
                throw WenguaNativeReadingError.missingPhrases
            }
            birdText="；同宫天禽星力量\(birdPower)，所携\(bird)主\(try selectedStemImage(bird,birdStemPower,hostStar.stages))"
        } else {birdText=""}
        let formsFull=[skyText,"；",earthText,birdText,"。天地格：",orderedFormations.joined(separator:"；"),"。"].joined()
        var danger:[String]=[]
        var recorded:Set<String>=[]
        // Grave and striking are real facts on the symbol, NOT a feature
        // limited to matching the single top-ranked anatomical candidate.
        for stem in [sky,illness.earthStem]+(bird.map{[$0]} ?? []) {
            let signs=badSigns(stem,illness)
            if !signs.isEmpty {
                let key=stem+"/"+signs.joined(separator:"、")
                if recorded.insert(key).inserted {
                    let rawSite=parts((mapping[stem]?["qimen_secret_vol13"] ?? [])
                        .joined(separator:"/")).first ?? "相应部位"
                    let site=rawSite=="脏（笼统）" ? "脏腑泛象" : rawSite
                    let meaning=signs.count==2 ? "伤痛损伤兼有隐伏之象" :
                        signs.contains("六仪击刑") ? "伤痛或损伤之象" :
                        "受压闭藏、不易显露之象"
                    danger.append("\(stem)主\(site)，见\(signs.joined(separator:"、"))，\(site)有\(meaning)")
                }
            }
        }
        if illnessVoid=="true_void" {
            danger.append("天芮宫真空，病位显象减看")
        } else if illnessVoid=="fake_void" {
            danger.append("天芮宫假空，不作全无")
        }
        let doorText:String
        if doorRel=="符号克宫" {
            let terms:[String:String]=[
                "开门":"金门迫木宫，传统指施治有阻",
                "休门":"水门迫火宫，传统指休养反复",
                "生门":"土门迫水宫，传统指生机受阻",
                "伤门":"木门迫土宫，传统指筋骨牵扯",
                "杜门":"木门迫土宫，传统指闭滞不畅",
                "景门":"火门迫金宫，传统指热象与肺系受扰",
                "死门":"土门迫水宫，传统指闭塞积滞",
                "惊门":"金门迫木宫，传统指惊扰、抽掣"]
            doorText="\(door)落\(palaceName)形成门迫，\(terms[door] ?? "门克落宫")"
        } else if doorRel=="宫克符号" {
            doorText="\(door)受\(palaceName)所克，门象受制，但不是门迫"
        } else {doorText=""}
        let doorClue=sourceClue("八门病象",door)
        let deityText=(deityClue=="其他传统象意" ? "传统神象待核" : deityClue)
        let starDoorGodFull=[
            "天芮星力量\(illnessPower)，主位依\(label(illness))宫确定；",
            "\(door)力量\(doorPower)，古籍记\(doorClue)；",
            "\(deity)力量\(deityPower)，古籍记\(deityText)。"
        ].joined()
        if !doorText.isEmpty {danger.append(doorText)}
        let dangerFull=danger.isEmpty ? "" :
            "本宫条件："+danger.joined(separator:"；")+"。"
        // V24 complete board: independently audit actual physical stem
        // identities and true tomb/striking, including unrelated palaces.
        // This evidence is a traditional warning, never a proven damaged
        // organ or proven cause. Do not fabricate a marker in mid-five.
        var crossEvents:[(Int,Int,String,String,String)]=[]
        for p in chart.palaces.filter({physical.contains($0.id) &&
                                     $0.id != illness.id}).sorted(by:{$0.id<$1.id}) {
            let realStems=Set(p.heavenStars.map{$0.carriedStem}+[p.earthStem])
            for stem in realStems.sorted() {
                let conditions=badSigns(stem,p)
                if conditions.isEmpty {continue}
                let sourceSites=parts((mapping[stem]?["qimen_secret_vol13"] ?? [])
                    .joined(separator:"/"))
                let rawSite=sourceSites.first ?? "身体相应部位"
                let site=rawSite=="脏（笼统）" ? "脏腑泛象" : rawSite
                let power=try stemPower(stem,p)
                if tier(power)==0 {
                    let diagnostic="V24_SOURCE_UNRESOLVED stem=\(stem) palace=\(p.id) sky=\(p.heavenStars.map{$0.carriedStem}.joined(separator:",")) earth=\(p.earthStem) stages=\(p.heavenStars.first(where:{$0.carriedStem==stem})?.stages.map{$0.branch+$0.stage}.joined(separator:",") ?? p.earthStages.map{$0.branch+$0.stage}.joined(separator:","))\n"
                    FileHandle.standardError.write(Data(diagnostic.utf8))
                    throw WenguaNativeReadingError.missingPhrases
                }
                let rel=palaceRelation(p)
                let relationText:String
                let priority:Int
                switch rel {
                case "此宫克病宫":
                    priority=0
                    relationText="\(label(p))宫\(five[p.id]!)克\(label(illness))宫\(five[illness.id]!)"
                case "此宫生病宫":
                    priority=1
                    relationText="\(label(p))宫\(five[p.id]!)生\(label(illness))宫\(five[illness.id]!)"
                case "病宫克此宫":
                    priority=2
                    relationText="\(label(illness))宫\(five[illness.id]!)克\(label(p))宫\(five[p.id]!)"
                case "病宫生此宫":
                    priority=3
                    relationText="\(label(illness))宫\(five[illness.id]!)生\(label(p))宫\(five[p.id]!)"
                default:
                    priority=4
                    relationText="\(label(p))宫与\(label(illness))宫同属\(five[illness.id]!)"
                }
                let conditionText=conditions.count==2 ?
                    "刑墓并见，"+site+"有伤痛损伤兼隐伏之象" :
                    conditions.contains("六仪击刑") ?
                    "六仪击刑，"+site+"有伤痛或损伤之象" :
                    "入墓，"+site+"有受压闭藏、不易显露之象"
                let message="\(label(p))宫\(stem)主\(site)，力量\(power)，\(conditionText)；\(relationText)"
                crossEvents.append((priority,p.id,stem,message,rel))
            }
        }
        crossEvents.sort{
            if $0.0 != $1.0 {return $0.0<$1.0}
            if $0.1 != $1.1 {return $0.1<$1.1}
            return $0.2<$1.2
        }
        let crossFull=crossEvents.isEmpty ? "" :
            "另宫刑墓："+crossEvents.map{$0.3}.joined(separator:"；")+"。"
        let ending="。"
        let dn=chart.bureau.dun=="yang" ? "阳" : "阴"
        let originalFocus=(!trauma && matched(lead,originalSites)) ?
            lead : originalSites.prefix(1).joined(separator:"、")
        let originalLocation=trauma ?
            "天芮在\(palaceName)，\(dn)遁\(sector)象先指\(originalFocus)；此次确有伤损，另从伤门实际落宫优先核位。" :
            "天芮在\(palaceName)，\(dn)遁\(sector)象先指\(originalFocus)。"
        // V23: A single disease-palace account contains star, door,
        // deity, distinct sky/earth, hosted Tianqin, formations and all
        // real tomb/striking/void/pressure. No second disconnected heading.
        let locationFull=[originalLocation,starDoorGodFull,formsFull,dangerFull,crossFull]
            .filter{ !$0.isEmpty }.joined(separator:"\n")
        let conclusionFocus=trauma ? "因属伤损，先从伤门落宫看" : "病位先看"
        // Do not invent anatomic laterality: 左肺 cannot be renamed 右侧内脏.
        let focusRegion:String
        if lead=="肝胆" {focusRegion="右上腹肝胆一带"}
        else if lead=="左肩" {focusRegion="左肩一带"}
        else if lead=="左耳" {focusRegion="左耳周围"}
        else if lead=="左臂" {focusRegion="左臂一带"}
        else if lead=="右肩" {focusRegion="右肩一带"}
        else if lead=="右耳" {focusRegion="右耳周围"}
        else if lead=="右臂" {focusRegion="右臂一带"}
        else if lead=="右肋" || lead=="右腰" {focusRegion="右侧肋腰一带"}
        else if lead=="外阴" || lead=="下部" {focusRegion="下身会阴一带"}
        else if lead=="左肺" {focusRegion="左侧胸部"}
        else {focusRegion=lead}
        // Only truly matching, independent physical symbols can sharpen
        // the chosen anatomy; the star's low energy does not erase an
        // independently strong earth stem on the same real palace.
        // Conservative corroboration: if both original branch rows are
        // at least 大, the image is salient without inventing ONE tier.
        let earthFacts=try stemBranchFacts(illness.earthStem,illness,illness.earthStages)
        let skyFacts=try stemBranchFacts(sky,illness,illnessStar.stages)
        let earthStrong=tier(earthPower)>=4 || earthFacts.allSatisfy{tier($0.1)>=4}
        let skyStrong=tier(skyPower)>=4 || skyFacts.allSatisfy{tier($0.1)>=4}
        var bodyEvidence:[String]=[]
        if let earthSite=earthSites.first(where:{matched($0,leadSites)}),
           earthStrong {
            let energyText=tier(earthPower)>0 ? "力量\(earthPower)" : "两支原格力量均至少为大"
            bodyEvidence.append("地盘\(illness.earthStem)主\(earthSite)，\(energyText)，与天芮同宫，定位更偏向\(earthSite)一带")
        } else if let skySite=skySites.first(where:{matched($0,leadSites)}),
                  skyStrong {
            let energyText=tier(skyPower)>0 ? "力量\(skyPower)" : "两支原格力量均至少为大"
            bodyEvidence.append("天盘\(sky)主\(skySite)，\(energyText)，与天芮同宫")
        }
        if tier(doorPower)>=4 && !trauma {
            bodyEvidence.append("\(door)力量\(doorPower)，旧籍\(doorClue)所指的\(door=="伤门" ? "筋脉牵扯" : "伴随征象")更显")
        }
        if tier(deityPower)>=4 && !trauma {
            bodyEvidence.append("\(deity)力量\(deityPower)，旧籍所指\(deityText)可作伴随线索")
        }
        if mainFormation.contains("伏吟") {
            bodyEvidence.append("本宫天地干伏吟，传统取反复迟滞之象")
        } else if formationNames.dropFirst().contains(where:{$0.contains("伏吟")}) {
            bodyEvidence.append(tier(birdPower)>=3 ?
                "天禽同宫又逢伏吟，传统取反复牵滞之象，可作旁证" :
                "天禽所携干虽见伏吟，但天禽力量偏弱，反复之象只作次要线索")
        }
        if let first=crossEvents.first,
           let p=chart.palaces.first(where:{$0.id==first.1}) {
            let rawSite=parts((mapping[first.2]?["qimen_secret_vol13"] ?? [])
                .joined(separator:"/")).first ?? "相应部位"
            let site=rawSite=="脏（笼统）" ? "脏腑泛象" : rawSite
            let signs=badSigns(first.2,p)
            let summary=signs.count==2 ? "伤痛损伤兼隐伏" :
                signs.contains("六仪击刑") ? "伤痛或损伤" : "闭藏不显"
            bodyEvidence.append("另见\(label(p))宫\(first.2)主\(site)，有\(summary)之象，与主病位分开核对")
        }
        let closing=bodyEvidence.isEmpty ? "" : "盘中"+bodyEvidence.joined(separator:"；")+"。"
        let conclusion=[
            "综上，\(relationship)本次\(conclusionFocus)\(focusRegion)。",
            closing,
            "以上为传统病位和症候象意，需以实际检查核实。"
        ].joined()
        let values:[String:String]=[
            "palace":palaceName,"dun":chart.bureau.dun=="yang" ? "阳":"阴",
            "sector":sector,"region":region,"primary":primary,"external":external,
            "door":door,"deity":deity,"sky":sky,"earth":illness.earthStem,
            "companion":bird.map{"同宫天禽星力"+birdPower+"，其携"+$0+"之干力"+birdStemPower+"，另见"+birdOther.joined(separator:"、")} ?? "本宫没有独立的天禽携干",
            "secret":secret.joined(separator:"、"),
            "viscera":viscera.joined(separator:"、"),
            "surface":surface.joined(separator:"、"),
            "injury":useInjury ? label(injury)+"宫" : "",
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
            "focus_site":lead,"location_full":locationFull,
            "site_detail":detailLine,
            "site_secondary":otherLine,"actor_site":actorLine,
            "injury_site":injuryFull,"injury_full":injuryFull,
             "other_doors":doorsFull,"hour_site":hourFull,
             "actor_full":personFull,"auxiliary_full":auxFull,
             "formation_full":"","danger_full":"",
             "final_site":conclusion
        ]
        let required=["01_location","02_injury","03_assist_doors",
                       "04_hour","05_person","06_auxiliary",
                       "07_formation","08_constraints","09_conclusion"]
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
            if (required[i]=="02_injury" && !useInjury) ||
               output.trimmingCharacters(in:.whitespacesAndNewlines).isEmpty {
                continue
            }
            sections.append(WenguaNativeCustomerSection(id:required[i],title:title,text:output))
        }
        guard sections.first?.id=="01_location",
              sections.last?.id=="09_conclusion",sections.count>=2,
              sections.map{$0.id}==required.filter{wanted in
                  sections.contains(where:{$0.id==wanted})
              },
              sections.contains(where:{$0.id=="02_injury"})==useInjury else {
            throw WenguaNativeReadingError.invalidPhrase
        }
        return WenguaNativeCustomerReading(
            version:"discomfort_v26_precise_injury_speech_20261101",
            topicID:"health.discomfort",relationship:relationship,iso:chart.iso,
            evidenceStatus:"traditional_textual_location_not_medical_diagnosis",
            sections:sections,rolePalaces:(
                useInjury ?
                ["illness":illness.id,"patient":actor.mainPalace,
                 "injury":injury.id,"hour":hourPalace.id] :
                ["illness":illness.id,"patient":actor.mainPalace,
                 "hour":hourPalace.id]))
    }
}
