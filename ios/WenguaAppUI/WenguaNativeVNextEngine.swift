import Foundation

// Wengua current V-next signed *traditional* engine. Everything here uses
// the actual native chart and the original 8×25 tables, never a screenshot,
// historical sealed answer, network LLM, or the discarded V4.2 formula.
// Private scores NEVER enter WenguaNativeCustomerReading / customer history.
struct WenguaVNextFactor {
    let symbol:String
    let strength:String?
    let value:Int?
}
// Private computation evidence, NEVER serialized into user-facing reading.
struct WenguaVNextStrengthEvidence {
    let source:String // star, cohost, door, god, pattern
    let symbol:String
    let monthStage:String? // god is ALWAYS nil: no monthly adjustment
    let palaceRelation:String?
    let tier:String?
    let internalScore:Int?
    let lifeStages:[String]
    let restrictions:[String]
}
struct WenguaVNextPalace {
    let id:Int
    let roles:[String]
    let star:Int?
    let door:Int?
    let deity:Int?
    let pattern:Int
    let raw:Int?
    let beforeVoid:Int?
    let afterVoid:Int?
    let void:String
    let doorBreak:Bool
    let patterns:[String]
    let unresolved:[String]
    let starStrength:String?
    let energyEvidence:[WenguaVNextStrengthEvidence]
}
struct WenguaVNextControl {
    let role:String
    let source:Int
    let target:Int
    let direction:String
    let attacker:String
    let scenario:String?
    let cell:String?
    let applicability:String
}
struct WenguaVNextAudit {
    let schema:String
    let palaces:[Int:WenguaVNextPalace]
    let roles:[String:Int]
    let firstMacroFiveNot:Bool
    let postVoidKnownSum:Int
    let score:Int?
    let pending:[Int]
    let controls:[WenguaVNextControl]
    let evidenceDirection:String
    let evidenceConflict:Bool
    let traditionalSentence:String
    let factSentences:[String]
    let roleConfidence:String
    let roleStatus:String
    let roleSourceNote:String
    let roleEnergy:[String:WenguaVNextFactor]
}
enum WenguaVNextEngine {
    static let tiers=["极小","小","中等","大","极大"]
    static let starElement=["天蓬星":"水","天芮星":"土","天冲星":"木",
      "天辅星":"木","天禽星":"土","天心星":"金","天柱星":"金",
      "天任星":"土","天英星":"火"]
    static let doorElement=["开门":"金","休门":"水","生门":"土",
      "伤门":"木","杜门":"木","景门":"火","死门":"土","惊门":"金"]
    static let godElement=["值符":"土","螣蛇":"火","太阴":"金",
      "六合":"木","白虎":"金","玄武":"水","九地":"土","九天":"金"]
    static let godPolarity=["值符":1,"螣蛇":-1,"太阴":1,"六合":1,
                             "白虎":-1,"玄武":-1,"九地":-1,"九天":1]
    static let starPolarity=["天辅星":1,"天禽星":1,"天心星":1,
      "天冲星":1,"天任星":1,"天英星":-1,"天蓬星":-1,"天芮星":-1,"天柱星":-1]
    static let doorPolarity=["开门":1,"休门":1,"生门":1,"死门":-1,
      "惊门":-1,"伤门":-1,"杜门":0,"景门":0]
    static let stemElement=WenguaNativeReadingRouter.stemElements
    static let elements=WenguaNativeReadingRouter.palaceElements
    static let generates=WenguaNativeReadingRouter.generating
    static let controls=WenguaNativeReadingRouter.controlling
    static let clash=["子":"午","午":"子","丑":"未","未":"丑",
       "寅":"申","申":"寅","卯":"酉","酉":"卯",
       "辰":"戌","戌":"辰","巳":"亥","亥":"巳"]
    static let striking=["戊":3,"己":2,"庚":8,"辛":9,"壬":4,"癸":4]
    static let godTiers=["符号生宫":"中等","符号克宫":"中等",
                        "比和":"大","宫克符号":"小","宫生符号":"极大"]
    static let topStages:Set<String>=["长生","冠带","临官","帝旺","沐浴"]
    static let middleStages:Set<String>=["胎","养"]

    private static func must(_ value:String?) throws -> String {
        guard let value else {throw WenguaHealthTemplateError.invalidCatalog}
        return value
    }
    private static func tierIndex(_ tier:String?) -> Int? {
        guard let tier else {return nil}
        return tiers.firstIndex(of:tier).map{$0+1}
    }
    private static func saturation(_ value:Int)->Int {max(-5,min(5,value))}
    private static func adverse(_ value:Int)->Int {
        value>0 ? max(1,value-2) : value<0 ? max(-5,value-2) : 0
    }
    private static func signed(_ tier:String?,_ polarity:Int)->Int? {
        guard polarity==0 || polarity == 1 || polarity == -1 else{return nil}
        if polarity==0 {return 0}
        return tierIndex(tier).map{$0*polarity}
    }
    private static func normalMonth(_ element:String,_ month:String) throws -> String {
        if element==month {return "旺"}
        if generates[month]==element {return "相"}
        if generates[element]==month {return "休"}
        if controls[element]==month {return "囚"}
        if controls[month]==element {return "死"}
        throw WenguaHealthTemplateError.invalidCatalog
    }
    private static func starMonth(_ element:String,_ month:String) throws -> String {
        if generates[element]==month {return "旺"}
        if element==month {return "相"}
        if generates[month]==element {return "废"}
        if controls[element]==month {return "休"}
        if controls[month]==element {return "囚"}
        throw WenguaHealthTemplateError.invalidCatalog
    }
    static func directed(_ symbol:String,_ palace:String) throws -> String {
        if symbol==palace {return "比和"}
        if generates[symbol]==palace {return "符号生宫"}
        if generates[palace]==symbol {return "宫生符号"}
        if controls[symbol]==palace {return "符号克宫"}
        if controls[palace]==symbol {return "宫克符号"}
        throw WenguaHealthTemplateError.invalidCatalog
    }
    private static func palaceRelation(_ source:Int,_ target:Int)->String {
        if source==target {return "同宫"}
        guard let a=elements[source],let b=elements[target] else{return "待核"}
        if a==b {return "比和"}
        if controls[a]==b {return "克"}
        if controls[b]==a {return "被克"}
        if generates[a]==b {return "生"}
        if generates[b]==a {return "被生"}
        return "待核"
    }
    static func monthly(_ branch:String) throws -> String {
        if "寅卯".contains(branch) {return "木"}
        if "巳午".contains(branch) {return "火"}
        if "申酉".contains(branch) {return "金"}
        if "亥子".contains(branch) {return "水"}
        if "辰未戌丑".contains(branch) {return "土"}
        throw WenguaHealthTemplateError.invalidCatalog
    }
    // Exactly Python health_palace_detailed_vnext.inspect_role_void priority.
    private static func actualVoid(_ p:WenguaNativePalace,_ c:WenguaNativeChart,
                                   month:String)->String {
        if p.voidBranches.isEmpty {return "not_void"}
        if p.id==c.hourHorsePalace {return "fake_void"}
        if p.voidBranches.contains(where:{clash[$0]==c.hourHorse}) {return "not_void"}
        guard let pe=elements[p.id] else {return "true_void"}
        if month==pe || generates[month]==pe {return "fake_void"}
        return "true_void"
    }
    private static func danger(_ p:WenguaNativePalace,
                               doorRelation:String)->[String] {
        var result:[String]=[]
        if !p.voidBranches.isEmpty {result.append("旬空待辨")}
        if p.tombs.contains(where:{$0.plane=="天盘"}) {result.append("天盘入墓")}
        if p.tombs.contains(where:{$0.plane=="地盘"}) {result.append("地盘入墓")}
        if p.heavenStars.contains(where:{striking[$0.carriedStem]==p.id}) {
            result.append("六仪击刑")
        }
        if doorRelation=="宫迫" {result.append("门迫")}
        return result
    }
    private static func doorRelation(_ symbol:String,_ palace:String) throws -> String {
        let rel=try directed(symbol,palace)
        let mapping=["宫生符号":"被宫生","宫克符号":"宫迫",
            "符号克宫":"门破","符号生宫":"生宫","比和":"比和"]
        return try must(mapping[rel])
    }
    static func factor(kind:String,symbol:String,palace:Int,
                               month:String,catalog:WenguaNativeEnergyCatalog,
                               stages:[WenguaNativeStage]=[]) throws ->WenguaVNextFactor {
        guard let pe=elements[palace] else {throw WenguaCastError.invalidChart}
        let se=try must((kind=="star" ? starElement[symbol] :
                          kind=="door" ? doorElement[symbol] : stemElement[symbol]))
        let relation=try directed(se,pe)
        let lookup:String?
        if kind=="star" {
            let stage=try starMonth(se,month)
            lookup=try WenguaNativeEnergyBundle.cell("star",row:stage,
               column:relation,catalog:catalog)
        } else if kind=="door" {
            let stage=try normalMonth(se,month)
            let column=try doorRelation(se,pe)
            lookup=try WenguaNativeEnergyBundle.cell("door",row:stage,
               column:column,catalog:catalog)
        } else if kind=="stem" {
            let column:String
            if se==month {column="比和"}
            else if generates[month]==se {column="被月令生"}
            else if controls[month]==se {column="被月令克"}
            else if controls[se]==month {column="克月令"}
            else if generates[se]==month {column="生月令"}
            else {throw WenguaHealthTemplateError.invalidCatalog}
            let rows=Set(stages.map { s -> String in
                topStages.contains(s.stage) ? "长生/冠带/临官/帝旺/沐浴" :
                middleStages.contains(s.stage) ? "胎 / 养" :
                ["衰","病"].contains(s.stage) ? "衰 / 病" :
                ["死","墓","绝"].contains(s.stage) ? "死 / 墓 / 绝" : "囚"
            })
            let possible=try Set(rows.map{
                try WenguaNativeEnergyBundle.cell("stem",row:$0,
                  column:column,catalog:catalog)
            })
            lookup=possible.count==1 ? possible.first : nil
        } else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        let polarity=kind=="star" ? starPolarity[symbol] :
                     kind=="door" ? doorPolarity[symbol] : nil
        return WenguaVNextFactor(symbol:symbol,strength:lookup,
                                 value:polarity.flatMap{signed(lookup,$0)})
    }
    private static func pattern(_ star:WenguaNativeStar,_ cell:WenguaNativePalace,
                                polarity:Int)->Int? {
        let levels=Set(star.stages.map{ topStages.contains($0.stage) ? 5 :
                  middleStages.contains($0.stage) ? 4 : 3 })
        guard levels.count==1,let initial=levels.first else {return nil}
        // In the Python V-next raw earth_tombs is a list of branch names,
        // not stem-labelled records. Do not silently charge that branch as
        // a stem-specific penalty. Preserve the original audited semantics.
        let heavenTomb=cell.tombs.contains{
            $0.plane=="天盘" && $0.stem==star.carriedStem
        }
        let striker=striking[star.carriedStem]==cell.id
        let earthStriker=cell.heavenStars.contains{
            $0.carriedStem==cell.earthStem && striking[$0.carriedStem]==cell.id
        }
        let grade=max(1,initial-(heavenTomb ? 1:0) -
            (striker ? 1:0) - (earthStriker ? 1:0))
        return grade*polarity
    }
    private static func wholeChartFiveNot(_ chart:WenguaNativeChart)->Bool {
        let hour=String(chart.pillars.hour.prefix(1))
        let day=String(chart.pillars.day.prefix(1))
        guard let i=WenguaNativeReadingRouter.stemOrder.firstIndex(of:hour),
              let j=WenguaNativeReadingRouter.stemOrder.firstIndex(of:day),
              let h=stemElement[hour],let d=stemElement[day] else {return false}
        return i%2==j%2 && controls[h]==d
    }
    private static func evaluate(_ p:WenguaNativePalace,role:String,
                                 chart:WenguaNativeChart,
                                 catalog:WenguaNativeEnergyCatalog,
                                 excel:[String:[String]],month:String,
                                 fiveNot:Bool) throws -> WenguaVNextPalace {
        guard p.id != 5,let pe=elements[p.id],let door=p.door,
              let deity=p.deity,let godEl=godElement[deity],
              let gp=godPolarity[deity] else {
            throw WenguaCastError.invalidChart
        }
        let v=actualVoid(p,chart,month:month)
        let doorRelation=try doorRelation(try must(doorElement[door]),pe)
        let br=doorRelation=="门破" && !(
            (door=="生门" && p.id==1) || (door=="景门" && p.id==6))
        var starScores:[Int]=[]
        var unresolved:[String]=[]
        var stars:[WenguaVNextFactor]=[]
        var underlying:[WenguaVNextStrengthEvidence]=[]
        for star in p.heavenStars {
            let part=try factor(kind:"star",symbol:star.star,palace:p.id,
                                 month:month,catalog:catalog)
            stars.append(part)
            let isRealHealthSignifier = role != "illness" || star.star=="天芮星"
            underlying.append(WenguaVNextStrengthEvidence(
                source:isRealHealthSignifier ? "star":"cohost",
                symbol:star.star,
                monthStage:try starMonth(try must(starElement[star.star]),month),
                palaceRelation:try directed(try must(starElement[star.star]),pe),
                tier:part.strength,
                internalScore:isRealHealthSignifier ? part.value : nil,
                lifeStages:star.stages.map{$0.stage},
                restrictions:[]))
            // Tianqin is real, but its health-illness factor and carried
            // pattern are not a second independent illness source.
            if role=="illness" && star.star != "天芮星" {continue}
            if let q=part.value {starScores.append(q)}
            else {unresolved.append("九星："+star.star)}
        }
        let doorFact=try factor(kind:"door",symbol:door,palace:p.id,
                                month:month,catalog:catalog)
        if doorFact.value==nil {unresolved.append("八门："+door)}
        underlying.append(WenguaVNextStrengthEvidence(
            source:"door",symbol:door,
            monthStage:try normalMonth(try must(doorElement[door]),month),
            palaceRelation:doorRelation,tier:doorFact.strength,
            internalScore:doorFact.value,lifeStages:[],
            restrictions:br ? ["门破加重不利"]:[]))
        let deityRel=try directed(godEl,pe)
        let godTier=try must(godTiers[deityRel])
        let godScore=signed(godTier,gp)
        if godScore==nil {unresolved.append("八神："+deity)}
        underlying.append(WenguaVNextStrengthEvidence(
            source:"god",symbol:deity,monthStage:nil,
            palaceRelation:deityRel,tier:godTier,internalScore:godScore,
            lifeStages:[],restrictions:[]))
        var patternPoints:[Int]=[]
        var patternNames:[String]=[]
        for star in p.heavenStars {
            if role=="illness" && star.star != "天芮星" {continue}
            let key=star.carriedStem+"|"+p.earthStem
            guard let fields=excel[key],fields.count==7 else {
                throw WenguaHealthTemplateError.invalidCatalog
            }
            patternNames.append(fields[2])
            let polarity=fields[3]=="吉" ? 1 : -1
            let score=pattern(star,p,polarity:polarity)
            if let score {patternPoints.append(score)}
            let relevantTombs=p.tombs.filter{$0.plane=="天盘" &&
                                             $0.stem==star.carriedStem}
            let restrictions=([striking[star.carriedStem]==p.id
                                  ? "六仪击刑" : nil] as [String?])
                .compactMap{$0} + relevantTombs.map{"天盘入墓："+$0.branch}
            underlying.append(WenguaVNextStrengthEvidence(
                source:"pattern",symbol:fields[2],
                monthStage:nil,palaceRelation:fields[3],
                tier:nil,internalScore:score,
                lifeStages:star.stages.map{$0.stage},
                restrictions:restrictions))
            
        }
        let allStar=unresolved.contains(where:{$0.hasPrefix("九星")}) ? nil :
                    Optional(starScores.reduce(0,+))
        let raw=(allStar != nil && doorFact.value != nil && godScore != nil) ?
          allStar!+doorFact.value!+godScore!+patternPoints.reduce(0,+) : nil
        var before=raw.map(saturation)
        if let score=before, fiveNot {before=adverse(score)}
        if let score=before, br {before=adverse(score)}
        let after=before.map{ score in
            if v=="not_void" || score==0 {return score}
            return score>0 ? score-3 : score+3
        }
        return WenguaVNextPalace(id:p.id,roles:[role],star:allStar,
              door:doorFact.value,deity:godScore,
              pattern:patternPoints.reduce(0,+),raw:raw,beforeVoid:before,
              afterVoid:after,void:v,doorBreak:br,patterns:patternNames,
              unresolved:unresolved,
              starStrength:stars.first(where:{$0.symbol=="天芮星"})?.strength
                            ?? stars.first?.strength,
              energyEvidence:underlying)
    }
    private static func primary(_ role:String,_ cell:WenguaNativePalace,
                                month:String,
                                catalog:WenguaNativeEnergyCatalog,
                                illness:Bool) throws -> WenguaVNextFactor {
        if role=="chief" {
            guard let deity=cell.deity,let elem=godElement[deity],
                  let pal=elements[cell.id] else {throw WenguaCastError.invalidChart}
            let direction=try directed(elem,pal)
            return WenguaVNextFactor(symbol:deity,strength:godTiers[direction],value:nil)
        }
        if role=="illness" || role=="doctor" ||
              role=="gender" || role=="qian" || role=="kun" {
            guard let star=cell.heavenStars.first(where:{
                illness ? $0.star=="天芮星" : true
            }) else {throw WenguaVNextReadingGate.unresolvedRole}
            return try factor(kind:"star",symbol:star.star,palace:cell.id,
                               month:month,catalog:catalog)
        }
        let stem=role=="medicine" ? "乙" :
                 role=="hour" ? String(cell.heavenStars.first?.carriedStem ?? "") :
                 ""
        // The caller passes selected role's specific visible stem separately;
        // generic sky first would be wrong in a dual Tianrui/Tianqin palace.
        guard !stem.isEmpty else {throw WenguaVNextReadingGate.unresolvedRole}
        guard let carrier=cell.heavenStars.first(where:{$0.carriedStem==stem}) else {
            throw WenguaVNextReadingGate.unresolvedRole
        }
        return try factor(kind:"stem",symbol:stem,palace:cell.id,
                          month:month,catalog:catalog,stages:carrier.stages)
    }
    private static func control(_ role:String,_ a:WenguaNativePalace,
                                _ b:WenguaNativePalace,
                                aFact:WenguaVNextFactor,
                                bFact:WenguaVNextFactor,
                                chart:WenguaNativeChart,
                                month:String,
                                catalog:WenguaNativeEnergyCatalog) throws -> WenguaVNextControl {
        let rel=palaceRelation(a.id,b.id)
        guard rel=="克" || rel=="被克" else {
            return WenguaVNextControl(role:role,source:a.id,target:b.id,
              direction:rel,attacker:"无克制方向",scenario:nil,cell:nil,
              applicability:"not_control_relation")
        }
        let attacker=rel=="克" ? a : b
        let target=rel=="克" ? b : a
        let factorA=rel=="克" ? aFact : bFact
        let factorB=rel=="克" ? bFact : aFact
        let va=actualVoid(attacker,chart,month:month)
        let vb=actualVoid(target,chart,month:month)
        let dA=try doorRelation(
           try must(doorElement[try must(attacker.door)]),
           try must(elements[attacker.id]))
        let dB=try doorRelation(
           try must(doorElement[try must(target.door)]),
           try must(elements[target.id]))
        let restrictionsA=danger(attacker,doorRelation:dA)
        let restrictionsB=danger(target,doorRelation:dB)
        let combined=restrictionsA+restrictionsB
        let voidCount=[va=="fake_void",vb=="fake_void",va=="true_void",
                       vb=="true_void"].filter{$0}.count
        var reason="matched"
        var scenario:String?="normal"
        if factorA.strength==nil || factorB.strength==nil {
            reason="factor_power_pending";scenario=nil
        } else if voidCount>1 {
            reason="both_void_unspecified";scenario=nil
        } else if va=="fake_void" {scenario="fake_void_attacker"}
        else if vb=="fake_void" {scenario="fake_void_target"}
        else if va=="true_void" {scenario="true_void_attacker"}
        else if vb=="true_void" {scenario="true_void_target"}
        else if combined.contains("旬空待辨") {
            reason="void_type_pending";scenario=nil
        }
        let result:String?
        if reason=="matched",let scenario,let ta=factorA.strength,let tb=factorB.strength {
            result=try WenguaNativeEnergyBundle.cell(
                scenario,row:ta,column:tb,catalog:catalog)
        } else {result=nil}
        // An actual strength result exists even when extra tomb/striking/
        // door-pressure gates stop it from becoming decisive evidence.
        let other=combined.filter{$0 != "旬空待辨"}
        let availability=reason != "matched" ? "pending" :
            !other.isEmpty ? "pending" :
            (["有效克制","高效克制","强力主克","绝对主克",
              "极限压制","有效主克","完全清除"].contains(result ?? "")
                 ? "strong" :
             ["微弱克制","减力克制","断续克制","效力递减"].contains(result ?? "")
                 ? "limited" : "failed")
        return WenguaVNextControl(role:role,source:attacker.id,target:target.id,
            direction:rel,attacker:rel=="克" ? role : "illness",
            scenario:scenario,cell:result,applicability:availability)
    }
    private static func tianruiVote(_ p:WenguaNativePalace,
        month:String) throws -> String {
        guard let pe=elements[p.id],let se=starElement["天芮星"] else {
            throw WenguaCastError.invalidChart
        }
        let star=try starMonth(se,month)
        let palace=try normalMonth(pe,month)
        let nominal=try directed(se,pe)
        let category:String
        switch nominal {
        case "宫克符号": category="宫克星"
        case "符号生宫": category="星生宫"
        case "符号克宫": category="星克宫"
        case "宫生符号": category="宫生星"
        default: category="宫星比和"
        }
        // Original inspect_tianrui_25 treats ANY void/tomb/strike/宫迫
        // as a restriction, regardless of latest independent void score.
        let doorPart=try doorRelation(
            try must(doorElement[try must(p.door)]),pe)
        if !p.voidBranches.isEmpty || !p.tombs.isEmpty ||
            p.heavenStars.contains(where:{striking[$0.carriedStem]==p.id}) ||
            doorPart=="宫迫" {return "pending"}
        let strong=["旺","相"]
        let weakStar=["囚","废"]
        let weakPal=["囚","死"]
        var supported=false
        if category=="宫克星" {
            supported=strong.contains(palace) && ["休","囚","废"].contains(star)
        } else if category=="星生宫" {
            supported=strong.contains(star) && strong.contains(palace)
        } else if category=="星克宫" {
            supported=strong.contains(star) && weakPal.contains(palace)
        } else if category=="宫生星" {
            supported=strong.contains(palace)
        } else {
            supported=strong.contains(star) && strong.contains(palace)
        }
        if !supported{return "pending"}
        if category=="宫克星" || category=="星生宫" {return "favorable"}
        if category=="宫生星" {return "adverse"}
        if (category=="星克宫" || category=="宫星比和") &&
              !weakStar.contains(star) {return "adverse"}
        return "pending"
    }

    // Validated against the original Python V-next stored factual snapshots.
    static func compute(chart:WenguaNativeChart,relationship:String,
                        energy:WenguaNativeEnergyCatalog,catalog:String,
                        actor:WenguaNativeActor? = nil) throws
     -> WenguaVNextAudit {
        guard WenguaNativeReadingRouter.supportedRelations.contains(relationship) else {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        guard chart.palaces.count==9 else {throw WenguaCastError.invalidChart}
        let all=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        let month=try monthly(String(chart.pillars.month.suffix(1)))
        var excel:[String:[String]]=[:]
        let lines=catalog.split(whereSeparator:\.isNewline).map(String.init)
        guard lines.count==82,
              lines.first==WenguaHealthTemplateBridge.header else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        for line in lines.dropFirst() {
            let c=line.components(separatedBy:"|")
            guard c.count==7 else {throw WenguaHealthTemplateError.invalidCatalog}
            excel[c[0]+"|"+c[1]]=c
        }
        guard excel.count==81 else {throw WenguaHealthTemplateError.invalidCatalog}
        func only(_ predicate:(WenguaNativePalace)->Bool)throws->WenguaNativePalace {
            let result=chart.palaces.filter(predicate)
            guard result.count==1,result[0].id != 5 else {
                throw WenguaVNextReadingGate.unresolvedRole
            }
            return result[0]
        }
        func stem(_ s:String)throws->WenguaNativePalace {
            try only{$0.heavenStars.contains(where:{$0.carriedStem==s})}
        }
        let patientStem=actor?.mainStem ?? String((relationship=="父亲" ?
                              chart.pillars.year:chart.pillars.day).prefix(1))
        let hourStem=String(chart.pillars.hour.prefix(1))
        let selected:[(String,WenguaNativePalace,String)]=[
            ("illness",try only{$0.heavenStars.contains(where:{$0.star=="天芮星"})},"天芮星"),
            ("doctor",try only{$0.heavenStars.contains(where:{$0.star=="天心星"})},"天心星"),
            ("medicine",try stem("乙"),"乙"),
            ("patient",try (actor == nil ?
                stem(patientStem) : only{$0.id==actor!.mainPalace}),patientStem),
            ("hour",try stem(hourStem=="甲" ? chart.hiddenStem : hourStem),hourStem),
            ("chief",try only{$0.deity=="值符"},"值符"),
        ]
        var personalized=selected
        if let actor {
            if let natal=actor.natalStem,let pid=actor.natalPalace {
                personalized.append(("natal",try only{$0.id==pid},natal))
            }
            if let pid=actor.genderPalace {
                let auxiliary=try only{$0.id==pid}
                let resident=auxiliary.heavenStars.first?.star ?? ""
                personalized.append(("gender",auxiliary,resident))
            }
        }
        guard let ill=selected.first?.1 else {throw WenguaVNextReadingGate.unresolvedRole}
        var physical:[Int:WenguaVNextPalace]=[:]
        var roles:[String:Int]=[:]
        var strength:[String:WenguaVNextFactor]=[:]
        let fiveNot=wholeChartFiveNot(chart)
        // Role binding order must match Python physical_cache. The first
        // role at a real palace is canonical; later co-palace roles share
        // its already evaluated score even if their signifier is different.
        var allSelected=personalized
        for (tag,id) in [("qian",6),("kun",2)] {
            guard let cell=all[id] else {throw WenguaCastError.invalidChart}
            allSelected.append((tag,cell,cell.heavenStars.first?.star ?? ""))
        }
        for (role,p,symbol) in allSelected {
            roles[role]=p.id
            if var prior=physical[p.id] {
                prior=WenguaVNextPalace(
                    id:prior.id,roles:prior.roles+[role],star:prior.star,
                    door:prior.door,deity:prior.deity,pattern:prior.pattern,
                    raw:prior.raw,beforeVoid:prior.beforeVoid,
                    afterVoid:prior.afterVoid,void:prior.void,
                    doorBreak:prior.doorBreak,patterns:prior.patterns,
                    unresolved:prior.unresolved,starStrength:prior.starStrength,
                    energyEvidence:prior.energyEvidence)
                physical[p.id]=prior
            } else {
                physical[p.id]=try evaluate(p,role:role,chart:chart,
                                            catalog:energy,excel:excel,
                                            month:month,fiveNot:fiveNot)
            }
            if role=="chief" {
                strength[role]=try primary(role,p,month:month,catalog:energy,
                                           illness:false)
            } else if role=="illness" || role=="doctor" ||
                       role=="gender" || role=="qian" || role=="kun" {
                guard let st=p.heavenStars.first(where:{$0.star==symbol}) else {
                    throw WenguaVNextReadingGate.unresolvedRole
                }
                strength[role]=try factor(kind:"star",symbol:st.star,palace:p.id,
                                          month:month,catalog:energy)
            } else {
                let actualStages:[WenguaNativeStage]
                if symbol=="甲" && chart.pillars.hour.hasPrefix("甲") &&
                   (role=="hour" || actor?.kind=="casting_hour_stem" ||
                    actor?.kind=="day_stem") {
                    // Only 甲时 is bound through xunShou hiddenStem to an
                    // ACTUAL palace; its factor stays 甲 and its 12 life is
                    // independently the stem 甲, never a forged visible 甲.
                    guard p.heavenStars.contains(where:{
                        $0.carriedStem==chart.hiddenStem
                    }),let jiaStages=WenguaNativeCore.stages["甲"] else {
                        throw WenguaVNextReadingGate.unresolvedRole
                    }
                    actualStages=try p.branches.map{ branch in
                        guard let stage=jiaStages[branch] else {
                            throw WenguaCastError.invalidChart
                        }
                        return WenguaNativeStage(branch:branch,stage:stage)
                    }
                } else {
                    guard let st=p.heavenStars.first(where:{
                        $0.carriedStem==symbol
                    }) else {throw WenguaVNextReadingGate.unresolvedRole}
                    actualStages=st.stages
                }
                strength[role]=try factor(kind:"stem",symbol:symbol,
                    palace:p.id,month:month,catalog:energy,
                    stages:actualStages)
            }
        }
        let counted=Set(personalized.map{$0.1.id})
        let scoreList=physical.values.filter{counted.contains($0.id)}
        let known=scoreList.compactMap{$0.afterVoid}.reduce(0,+)
        let pending=scoreList.filter{$0.afterVoid==nil}.map{$0.id}.sorted()
        let result=pending.isEmpty ? Optional(saturation(known)) : nil
        var controls:[WenguaVNextControl]=[]
        let diseaseStrength=try must(strength["illness"]?.strength)
        var votes=[String:String]()
        for (role,p,_) in personalized where role != "illness" {
            guard let a=strength[role],let b=strength["illness"] else {
                throw WenguaVNextReadingGate.unresolvedRole
            }
            let comparison=try control(role,p,ill,aFact:a,bFact:b,
                           chart:chart,month:month,catalog:energy)
            controls.append(comparison)
            let rel=comparison.direction
            var direction="pending"
            if rel=="克" && ["strong","limited"].contains(comparison.applicability) {
                direction="favorable"
            } else if rel=="被克" &&
                   ["strong","limited"].contains(comparison.applicability) {
                direction="adverse"
            } else if rel=="生" {
                let obstacles=try doorRelation(try must(doorElement[try must(p.door)]),
                                              try must(elements[p.id]))
                if (tierIndex(a.strength) ?? 0)>=3 && danger(p,doorRelation:obstacles).isEmpty {
                    direction="adverse"
                }
            }
            let pair=[p.id,ill.id].sorted().map(String.init).joined(separator:":")
            // One source->target physical relation gets one vote across
            // co-palace roles, just like health_role_majority_vnext.
            if votes[pair]==nil {votes[pair]=direction}
        }
        var favorable=votes.values.filter{$0=="favorable"}.count
        var adverse=votes.values.filter{$0=="adverse"}.count
        let tianrui=try tianruiVote(ill,month:month)
        if tianrui=="favorable" {favorable+=1}
        if tianrui=="adverse" {adverse+=1}
        if fiveNot {adverse+=1}
        // Python domain_selected_energy_vnext.selected_health_sequence
        // suppresses firm evidence polarity when the person's SOURCE binding
        // is conditional, regardless of the vote majority. A candidate
        // patient is not permission to issue a definite adverse reading.
        let confident=actor == nil || actor!.eligibleForFirmTraditionalJudgment
        let evidenceDirection=confident && (favorable+adverse)>0 ?
             (favorable>adverse ? "favorable" :
              adverse>favorable ? "adverse" : "unresolved") : "unresolved"
        let conflict = (result != nil && result != 0 &&
                  (evidenceDirection=="unresolved" ||
                   (result!>0 && evidenceDirection=="adverse") ||
                   (result!<0 && evidenceDirection=="favorable")))
        let sentence:String
        if let result {
            if conflict {sentence="宫位吉凶与人物关系证据仍有分歧，暂不强断吉凶。"}
            else {
                let grade=result==0 ? "不凶不吉" : result>0 ? "偏吉" : "偏凶"
                sentence="按各用神实际宫位、星门神与天地格综合，本次传统象意倾向"+grade+"。"
            }
        } else {
            sentence="相关宫位存在真实未核力量，暂不作确定的吉凶合断。"
        }
        // User-readable phrases are composed solely by the editable JSON layer.
        let factual:[String]=[]
        _ = diseaseStrength // Already independently bound via selected factor.
        return WenguaVNextAudit(
            schema:"wengua_native_vnext_exact_200_81_selected_five_v20261026",
            palaces:physical,roles:roles,firstMacroFiveNot:fiveNot,
            postVoidKnownSum:known,score:result,pending:pending,
            controls:controls,evidenceDirection:evidenceDirection,
            evidenceConflict:conflict,traditionalSentence:sentence,
            factSentences:factual,
            roleConfidence:actor?.confidence ?? "legacy_two_role_parity",
            roleStatus:(actor == nil || actor!.eligibleForFirmTraditionalJudgment)
                 ? "eligible" : "source_conditional_candidate",
            roleSourceNote:actor?.note ?? "",
            roleEnergy:strength)
    }
}
enum WenguaVNextReadingGate:Error {case unresolvedRole}
