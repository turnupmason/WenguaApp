import Foundation

// Verbatim candidate port of Python's CURRENT selected_health_sections +// render_complete_selected_palace + render_first_stage_macro +// explain_selected_role. NO fixed/secret past chart text or lookup by instant.
// We retain both engines and compare the entire generated text byte-for-byte
// before this renderer may replace the current production Swift customer view.
enum WenguaPythonVNextVerbatim {
    private static let digits=[1:"一",2:"二",3:"三",4:"四",
                               5:"五",6:"六",7:"七",8:"八",9:"九"]
    private static let roleLabels=[
        "doctor":["天心医生","医药之助","医生制病","医生难以发挥制病作用"],
        "medicine":["乙奇医药","药力","医药制病","药力难以压住病象"],
        "patient":["患者用神","患者自身之力","患者有力抗病","患者自身制病能力受限"],
        "hour":["时干事体","求测事体之力","事体可制病","事体难以形成制病之助"],
        "chief":["值符大吉神","值符的护持力","吉神护持可制病","值符未形成制病之助"],
        "natal":["患者年命","年命之力","年命有制病之象","年命难形成有效制病之助"],
        "gender":["性别辅助宫","辅助宫之力","辅助宫可协助制病","辅助宫护持有限"]
    ]
    private static let solid:Set<String>=["有效克制","高效克制","有效主克",
        "强力主克","绝对主克","极限压制","完全清除"]
    private static let weak:Set<String>=["微弱克制","减力克制","断续克制","效力递减"]
    private static let failed:Set<String>=["克制失效","反侮受损","完全失控",
        "系统性失控","终极解体","丧失能力"]
    private static let starOrigins=WenguaNativeReadingRouter.homeStars
    private static let doorOrigins=WenguaNativeReadingRouter.homeDoors
    private static let generating=WenguaNativeReadingRouter.generating
    private static let controlling=WenguaNativeReadingRouter.controlling
    private static let elements=WenguaNativeReadingRouter.palaceElements

    private static func label(_ palace:WenguaNativePalace)->String {
        palace.gua+(digits[palace.id] ?? String(palace.id))+"宫"
    }
    private static func month(_ chart:WenguaNativeChart)throws->String {
        try WenguaVNextEngine.monthly(String(chart.pillars.month.suffix(1)))
    }
    private static func relation(_ a:Int,_ b:Int)->String {
        if a==b{return "同宫"}
        guard let x=elements[a],let y=elements[b] else {return "待核"}
        if x==y{return "比和"}
        if controlling[x]==y{return "克"}
        if controlling[y]==x{return "被克"}
        if generating[x]==y{return "生"}
        if generating[y]==x{return "被生"}
        return "待核"
    }
    private static func fullMacro(_ c:WenguaNativeChart,_ a:WenguaVNextAudit)
      throws->String {
        let day=String(c.pillars.day.prefix(1))
        let hour=String(c.pillars.hour.prefix(1))
        let first=a.firstMacroFiveNot
            ? "五不遇时成立（时干"+hour+"克日干"+day+"且阴阳相同）；按用户规则，五不遇时主诸事凶，为全局一项不利象，不能单凭此象断病亡。"
            : "不构成五不遇时（已按日干、时干五行克制及阴阳同类核对）。"
        let byID=c.palaces
        let stars=byID.flatMap{p in p.heavenStars.compactMap{x->(String,Int)? in
            starOrigins[x.star] != nil ? (x.star,p.id) : nil
        }}
        let doors=byID.compactMap{p->(String,Int)? in
            guard let x=p.door,doorOrigins[x] != nil else {return nil}
            return (x,p.id)
        }
        guard stars.count==8,doors.count==8 else {
            throw WenguaCastError.invalidChart
        }
        func status(_ items:[(String,Int)],_ originals:[String:Int])->String {
            let ordered=items.allSatisfy{$0.1==originals[$0.0]}
            let reverse=items.allSatisfy{
                guard let native=originals[$0.0] else{return false}
                return $0.1==WenguaNativeReadingRouter.opposites[native]
            }
            return ordered ? "伏吟" : reverse ? "反吟" : "非伏吟反吟"
        }
        let ss=status(stars,starOrigins),ds=status(doors,doorOrigins)
        let slow=ss=="伏吟" || ds=="伏吟"
        let fast=ss=="反吟" || ds=="反吟"
        let pace=slow && fast
            ? "伏吟主慢，反吟主快；本盘星门分别命中，缓急并列待具体条件核定。"
            : slow ? "伏吟主慢。" : fast ? "反吟主快。"
            : "本盘无整盘伏吟反吟，不凭此三项擅断缓急。"
        let good=a.tianxianHour ? "天显时成立，全局得吉时之助。" : ""
        return first+" "+good+"九星"+ss+"、八门"+ds+"。"+pace+" 缓急不自动等于吉凶。"
    }
    private static func monthColumn(_ stem:String,_ month:String)throws->String {
        guard let e=WenguaNativeReadingRouter.stemElements[stem] else{
            throw WenguaCastError.invalidChart
        }
        if e==month{return "比和"}
        if generating[month]==e{return "被月令生"}
        if controlling[month]==e{return "被月令克"}
        if controlling[e]==month{return "克月令"}
        if generating[e]==month{return "生月令"}
        throw WenguaCastError.invalidChart
    }
    private static func lifeRow(_ stage:String)->String {
        if WenguaVNextEngine.topStages.contains(stage) {
            return "长生/冠带/临官/帝旺/沐浴"
        }
        if WenguaVNextEngine.middleStages.contains(stage){return "胎 / 养"}
        if stage=="衰" || stage=="病" {return "衰 / 病"}
        if ["死","墓","绝"].contains(stage){return "死 / 墓 / 绝"}
        return "囚"
    }
    private static func powerStem(_ symbol:String,
                                   stages:[WenguaNativeStage],
                                   palace:Int,month:String,
                                   energy:WenguaNativeEnergyCatalog)throws->String {
        let source=try WenguaVNextEngine.factor(
            kind:"stem",symbol:symbol,palace:palace,
            month:month,catalog:energy,stages:stages)
        if let x=source.strength{return symbol+"势"+x}
        // Keep unresolved lifecycle variants in source audit, not public prose.
        return symbol
    }
    private static func power(_ kind:String,_ symbol:String,_ palace:Int,
                               _ month:String,_ energy:WenguaNativeEnergyCatalog)
       throws->String {
        let power=try WenguaVNextEngine.factor(
            kind:kind,symbol:symbol,palace:palace,
            month:month,catalog:energy)
        return symbol+(power.strength ?? "待核")
    }
    private static func god(_ name:String,_ palaceElement:String)throws->String {
        guard let element=WenguaVNextEngine.godElement[name] else{return "未核"}
        let direction=try WenguaVNextEngine.directed(element,palaceElement)
        let rel=["宫生符号":"被宫生","宫克符号":"被宫克",
                 "符号克宫":"克宫","符号生宫":"生宫","比和":"比和"]
        guard let tier=WenguaVNextEngine.godTiers[direction],
              let polarity=WenguaVNextEngine.godPolarity[name] else {
            return name+(rel[direction] ?? "待核")+"、吉凶待核"
        }
        return name+(rel[direction] ?? "待核")+"、"+(tier=="中等" ? "中" : tier)+(polarity > 0 ? "吉" : "凶")
    }
    private static func voidReason(_ p:WenguaNativePalace,
                                   chart:WenguaNativeChart,
                                   month:String,klass:String)->String {
        guard !p.voidBranches.isEmpty else{return ""}
        if p.id==chart.hourHorsePalace {return "马星与旬空处于同一真实宫：假空"}
        if p.voidBranches.contains(where:{
            WenguaVNextEngine.clash[$0]==chart.hourHorse
        }) {return "马星与逢空宫实际地支相冲：冲空后不按逢空处理"}
        if let e=elements[p.id],e==month || generating[month]==e {
            return "逢空且落宫受月令生扶或比和：假空"
        }
        return "逢空且无同宫马星、对宫冲空或月令生扶：真空"
    }
    private static func conditions(_ p:WenguaNativePalace,
                                   _ chart:WenguaNativeChart)throws->String {
        var terms:[String]=[]
        guard let pe=elements[p.id],let door=p.door,
              let doorElement=WenguaVNextEngine.doorElement[door] else {
            throw WenguaCastError.invalidChart
        }
        let relation=try WenguaVNextEngine.directed(doorElement,pe)
        // Current table: door controls palace = 门破; palace controls door = 宫迫.
        if relation=="符号克宫" {
            let noExtra=(door=="生门" && p.id==1) ||
                        (door=="景门" && p.id==6)
            _ = noExtra // only audit retains the extra-tier exception
            terms.append("门破")
        }
        if p.tombs.contains(where:{$0.plane=="天盘"}){terms.append("天盘入墓")}
        if p.tombs.contains(where:{$0.plane=="地盘"}){terms.append("地盘入墓")}
        if p.heavenStars.contains(where:{
            WenguaVNextEngine.striking[$0.carriedStem]==p.id
        }) {terms.append("六仪击刑")}
        if relation=="宫克符号"{terms.append("门迫")}
        if p.id==chart.hourHorsePalace {terms.append("本宫驿马")}
        return terms.joined(separator:"、").isEmpty
          ? "无已核特殊刑墓迫" : terms.joined(separator:"、")
    }
    private static func signed(_ score:Int?)->String {
        guard let score else {return "吉凶待核"}
        if score==0{return "中平"}
        let tier=WenguaVNextEngine.tiers[abs(score)-1]
        return (tier=="中等" ? "中" : tier)+(score>0 ? "吉":"凶")
    }
    private static func signedSymbol(_ kind:String,_ symbol:String,
                                     palace:Int,month:String,
                                     energy:WenguaNativeEnergyCatalog)throws->String {
        let factor=try WenguaVNextEngine.factor(
            kind:kind,symbol:symbol,palace:palace,month:month,catalog:energy)
        guard let tier=factor.strength,
              let idx=WenguaVNextEngine.tiers.firstIndex(of:tier) else {
            return symbol+"吉凶待核"
        }
        let polarity=kind=="star" ? WenguaVNextEngine.starPolarity[symbol] :
                                     WenguaVNextEngine.doorPolarity[symbol]
        guard let polarity else{return symbol+"吉凶待核"}
        return symbol+signed((idx+1)*polarity)
    }
    private static func palaceText(_ p:WenguaNativePalace,role:String,
                                   chart:WenguaNativeChart,
                                   review:WenguaVNextAudit,
                                   energy:WenguaNativeEnergyCatalog,
                                   formations:[Int:WenguaHealthFormationBlock])
       throws ->String {
        let month=try month(chart)
        guard let row=review.palaces[p.id],let pe=elements[p.id],
              let deity=p.deity,let door=p.door,
              let formation=formations[p.id] else {
            throw WenguaVNextReadingGate.unresolvedRole
        }
        let stars=try p.heavenStars.filter{$0.star != "天禽星"}.map{
            try signedSymbol("star",$0.star,palace:p.id,
                             month:month,energy:energy)
        }.joined(separator:"、")
        let doorPart=try signedSymbol("door",door,palace:p.id,
                                      month:month,energy:energy)
        let hasIllness=p.heavenStars.contains{$0.star=="天芮星"}
        // Each actual sky carrier has a distinct 81 pattern; do not
        // mis-attribute Tianqin's carried stem to Tianrui.
        let accepted=p.heavenStars
        let heaven=try accepted.map{
            try powerStem($0.carriedStem,stages:$0.stages,
                          palace:p.id,month:month,energy:energy)
        }.joined(separator:"、")
        let earth=try powerStem(p.earthStem,stages:p.earthStages,
                                palace:p.id,month:month,energy:energy)
        let chosen=formation.sentences
        let book=chosen.isEmpty ? "；本宫没有实际天地盘有序格" :
            "；天地格："+chosen.joined(separator:"；")
        let klass=row.void=="not_void" ? "不空" :
                  row.void=="fake_void" ? "假空" : "真空"
        let special=try conditions(p,chart)
        let broken=special.components(separatedBy:"、").contains("门破")
        let brokenNote=broken ? "。八门压制宫力量，吉事不吉，凶事更凶" : ""
        return "落"+label(p)+"；九星"+(stars.isEmpty ? "无已核星":stars)+"；八神"+(try god(deity,pe))+"；八门"+doorPart+"；天盘干"+(heaven.isEmpty ? "无":heaven)+"、地盘干"+earth+book+"；空亡"+klass+"；"+special+brokenNote+"。全部因素推断后，此宫为"+signed(review.roleScores[role])+"。"
    }

    private static func powerNote(_ role:String,_ p:WenguaNativePalace,
        _ own:WenguaVNextFactor,chart:WenguaNativeChart)throws->String {
        let strength=own.strength ?? "待核"
        guard let pe=elements[p.id] else{throw WenguaCastError.invalidChart}
        if role=="chief" {
            guard let deity=p.deity,let ge=WenguaVNextEngine.godElement[deity]
                else {throw WenguaCastError.invalidChart}
            let r=try WenguaVNextEngine.directed(ge,pe)
            let map=["宫生符号":"被宫生","宫克符号":"被宫克",
                     "符号克宫":"克宫","符号生宫":"生宫","比和":"比和"]
            return "值符按神宫"+(map[r] ?? r)+"，用神力量为"+strength+"。"
        }
        if role=="doctor" || role=="gender" {
            guard let se=WenguaVNextEngine.starElement[own.symbol] else {
                throw WenguaCastError.invalidChart
            }
            let month=try month(chart)
            let stage=try WenguaVNextEngine.starMonth(se,month)
            let rel=try WenguaVNextEngine.directed(se,pe)
            let map=["宫生符号":"被宫生","宫克符号":"被宫克",
                     "符号克宫":"克宫","符号生宫":"生宫","比和":"比和"]
            return own.symbol+"月令"+stage+"、"+(map[rel] ?? rel)+"，用神力量为"+strength+"。"
        }
        let m=try month(chart)
        let col=try monthColumn(own.symbol,m)
        let carried=p.heavenStars.first{$0.carriedStem==own.symbol}
        var rows:[String]=[]
        if let carried {
            for st in carried.stages {
                let row=lifeRow(st.stage)
                if !rows.contains(row){rows.append(row)}
            }
        } else if own.symbol=="甲",let stages=WenguaNativeCore.stages["甲"] {
            // Hidden Xunshou 甲 never appears as a visible sky carrier,
            // but its independently verified natal/hour life stage MUST use
            // actual branch seats, not an invented unresolved fallback.
            for branch in p.branches {
                if let actual=stages[branch] {
                    let row=lifeRow(actual)
                    if !rows.contains(row){rows.append(row)}
                }
            }
        }
        let stage=rows.count==1 ? rows[0] : "长生分支待核"
        if stage=="长生分支待核" {
            return own.symbol+"天干与月令关系为"+col+"，其本宫力量仍待核实。"
        }
        return own.symbol+"天干十二长生"+stage+"、"+col+"，用神力量为"+strength+"。"
    }

    private static func roleAgainstIllness(
        _ role:String,review:WenguaVNextAudit,
        chart:WenguaNativeChart,targetPowerSentence:String)throws->String {
        guard let aid=review.roles[role],
              let pid=review.roles["illness"],
              let p=chart.palaces.first(where:{$0.id==aid}),
              let own=review.roleEnergy[role],
              let names=roleLabels[role],
              let edge=review.controls.first(where:{$0.role==role}) else{
            return ""
        }
        let who=names[0]
        let rel=relation(aid,pid)
        let baseNote=try powerNote(role,p,own,chart:chart)
        // Each edge compares THIS selected signifier with Tianrui, not the
        // net +/- score of either resident physical palace.
        let note=baseNote+targetPowerSentence
        let outcome=edge.cell
        let applicable=["strong","limited"].contains(edge.applicability)
        let eligible:Bool
        if role=="chief" {
            eligible=review.palaces[aid]?.void=="not_void" &&
                rel=="克" && applicable
        } else {
            eligible=rel != "克" || applicable
        }
        if role=="medicine" && rel=="同宫" {
            return note+"乙奇与天芮病宫同宫，表示正在接受治疗，医药与病象同宫发挥作用。"
        }
        if role=="chief" && rel=="同宫" {
            return note+"值符大吉神与天芮病宫同宫，表示大吉神在同宫护持，能够发挥作用。"
        }
        if role=="chief" && review.palaces[aid]?.void != "not_void" {
            return note+"因值符空亡，护持力明显减弱，尚存少许余气。"
        }
        if rel=="克" {
            let meaning:String
            if review.controlBonusPalaces.contains(aid) &&
               ["strong","limited"].contains(edge.applicability) {
                if review.palaces[pid]?.void != "not_void" {
                    meaning="病宫逢空，病气减弱，更易受到"+who+"的克制。"
                } else {
                    meaning="病象受到"+who+"的克制。"
                }
            } else if edge.applicability=="failed" {
                meaning=who+"虽然在五行上克病宫，但双方实际力量比较未能成功克制。"
            } else {
                meaning=who+"虽有克病方向，具体用神力量或矩阵限制未能支持确定的克病加分。"
            }
            return note+who+"宫克天芮病宫，"+meaning
        }
        let explanation:String
        switch rel {
        case "生":
            explanation=who+"宫生天芮病宫，方向上生扶病宫，实际助病强弱须根据双方各自用神力量判断。"
        case "被克":
            let effect:String
            if edge.applicability=="strong" {
                effect="病宫用神有力压制本方，制约较明显。"
            } else if edge.applicability=="limited" {
                effect="病宫有克向但施力受限，不能直接断本方完全失力。"
            } else if edge.applicability=="failed" {
                effect="病宫虽有克向，但用神力量比较不能形成有效压制。"
            } else {
                effect="病宫虽有克向，双方力量或空墓条件待核，不能直接断已受制。"
            }
            explanation=who+"宫受天芮病宫克，"+effect
        case "被生":
            explanation=who+"宫受天芮病宫生，方向上受病宫生扶，实际承受力量按双方用神判断，非主动克病。"
        case "比和":
            explanation=who+"宫与天芮病宫比和，同气但不等于双方力量相同，也不是主动克病。"
        case "同宫":
            explanation=who+"与天芮病宫同宫，意思为：双方同宫，不另论跨宫克制。"
        default:
            explanation=who+"与病宫的五行关系待核。"
        }
        return note+explanation
    }

    static func sections(chart:WenguaNativeChart,review:WenguaVNextAudit,
                         actor:WenguaNativeActor?,
                         template:Data,catalog:String,
                         energy:WenguaNativeEnergyCatalog)
      throws ->[WenguaNativeCustomerSection] {
        guard let root=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              let macros=root["macros"] as? [String:String],
              let titles=root["section_titles"] as? [String:String] else {
            throw WenguaNativeReadingError.missingPhrases
        }
        func substitute(_ text:String,_ vars:[String:String]=[:])throws->String {
            var t=text
            for (name,value) in vars {
                t=t.replacingOccurrences(of:"{"+name+"}",with:value)
            }
            guard !t.contains("{"),!t.contains("}") else {
                throw WenguaNativeReadingError.invalidPhrase
            }
            return t
        }
        func phrase(_ key:String,_ vars:[String:String]=[:])throws->String {
            guard let text=macros[key] else {
                throw WenguaNativeReadingError.missingPhrases
            }
            return try substitute(text,vars)
        }
        func title(_ key:String,_ vars:[String:String]=[:])throws->String {
            guard let text=titles[key] else {
                throw WenguaNativeReadingError.missingPhrases
            }
            return try substitute(text,vars)
        }
        let formations=try WenguaHealthTemplateBridge.fromText(
            chart:chart,template:template,catalog:catalog)
        let lookup=Dictionary(uniqueKeysWithValues:formations.map{($0.id,$0)})
        let cells=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        var result:[WenguaNativeCustomerSection]=[]
        func push(_ id:String,_ heading:String,_ body:String) {
            var text=body
            for (old,new) in [("。；","；"),("；；","；"),
                              ("。。","。"),("，；","；"),("。。，","。")] {
                while text.contains(old) {
                    text=text.replacingOccurrences(of:old,with:new)
                }
            }
            result.append(WenguaNativeCustomerSection(id:id,title:heading,
                                                       text:text.trimmingCharacters(in:.whitespacesAndNewlines)))
        }
        push("01_macro",try title("macro"),try phrase("macro",[
            "macro_text":fullMacro(chart,review)]))
        var viewed:[Int:String]=[:]
        var powerSeen:Set<String>=[]
        for (role,id,key) in [
            ("illness","02","illness"),("doctor","03","doctor"),
            ("medicine","04","medicine"),("patient","05","patient"),
            ("hour","06","hour"),("chief","07","chief"),
            ("natal","08","natal"),("gender","09","gender")
        ] {
            guard let pid=review.roles[role],let p=cells[pid] else {
                continue
            }
            let full:String
            if let original=viewed[pid] {
                full="与前述"+original+"同在"+label(p)+"，合看该宫象。"
            } else {
                full=try palaceText(p,role:role,chart:chart,review:review,
                                    energy:energy,formations:lookup)
                viewed[pid]=try title(key)
            }
            var extra=""
            if role=="illness" {
                let t25=try WenguaVNextTianrui25.caseFor(chart:chart,audit:review)
                extra=try phrase("illness",["name":t25.title,"explanation":t25.why])
            }
            let marker=String(pid)+":"+(review.roleEnergy[role]?.symbol ?? "")
            let roleText:String
            if role=="illness" || (powerSeen.contains(marker) && role != "chief") {
                roleText=""
            } else {
                let targetPower=try phrase("selected_target_power",[
                    "strength":review.roleEnergy["illness"]?.strength ?? "待核"
                ])
                roleText=try roleAgainstIllness(
                    role,review:review,chart:chart,
                    targetPowerSentence:targetPower)
                powerSeen.insert(marker)
            }
            let relationText=role=="illness" ? "" :
                try phrase("role_relation",["relation_text":roleText])
            let genderNote=role=="gender" ? try phrase("gender_note") : ""
            let defaultTitle=try title(key)
            let displayTitle=role=="gender" && pid==2 ? "坤宫辅助（女）" :
                             role=="gender" && pid==6 ? "乾宫辅助（男）" :
                             defaultTitle
            push(id,displayTitle,try phrase("role",[
                "palace_detail":full,"palace_score":"",
                "extra_illness":extra,"role_relation":relationText,
                "gender_note":genderNote]))
        }
        // Qian and Kun remain full source facts in internal audit; the
        // patient's selected sex already uses one real gender palace once.
        // V7.3: a dynamic two-sentence account of THIS chart, never a
        // hardcoded success case or duplicated real-person/palace score.
        let summaryTitles:[String:String]=[
            "illness":"天芮病宫","doctor":"天心医生","medicine":"乙奇医药",
            "patient":"患者用神","hour":"时干事体","chief":"值符",
            "natal":"患者年命","gender":"长辈辅助宫"]
        var desc:[String]=[]
        let directions:[String:String]=[
            "克":"克病宫","生":"生扶病宫","被克":"受病宫克",
            "被生":"受病宫生","比和":"与病宫比和","同宫":"与病宫同宫"]
        var seenPalaces:[Int:String]=[:]
        for key in ["illness","doctor","medicine","patient",
                    "hour","chief","natal","gender"] {
            guard let pid=review.roles[key],let p=cells[pid] else{continue}
            let quality=signed(review.roleScores[key])
            let name=key=="gender" ? (pid==2 ? "长辈坤宫":"长辈乾宫") :
                        (summaryTitles[key] ?? key)
            let state=review.palaces[pid]?.void ?? "not_void"
            var head:String
            let symbol=review.roleEnergy[key]?.symbol ?? "未核"
            let power=review.roleEnergy[key]?.strength ?? "待核"
            let suffix=try phrase("selected_role_summary",[
                "symbol":symbol,"strength":power
            ])
            if let existing=seenPalaces[pid] {
                head=name+"与"+existing+"同在"+label(p)+suffix
            } else {
                head=name+"落"+label(p)+"，宫象"+quality+suffix
                if state != "not_void" && key != "chief" {
                    head+="且逢"+(state=="true_void" ? "真空":"假空")
                }
                seenPalaces[pid]=name
            }
            // Same physical palace is described only once, while every
            // different selected cohost keeps its OWN real source strength
            // and control result in the two-sentence customer template.
            if key != "illness" {
                let edge=review.controls.first(where:{$0.role==key})
                let direction=edge?.direction
                if let direction,let note=directions[direction] {
                    head+="，"+note
                }
                if direction=="克" {
                    let qualified=["strong","limited"].contains(
                        edge?.applicability ?? "")
                    let point=qualified ? review.controlBonusPoints[pid] : nil
                    if point==5 {
                        head+="，病宫又逢空，受制更易"
                    } else if point==3 {
                        head+="，该用神有力制病"
                    } else if point==1 {
                        head+="，该用神施力受空或宫克限制，仅存余气"
                    } else if edge?.applicability=="failed" {
                        head+="，该用神实际克制未成"
                    } else {
                        head+="，该用神克病力量或限制待核"
                    }
                } else if key=="chief" && state != "not_void" {
                    head+="，逢空护持减弱，不能据此断已经制病"
                }
            }
            desc.append(head)
        }
        if !review.drainBonusPalaces.isEmpty {
            desc.append("病星势弱而外泄，病气有耗损之象")
        }
        desc+=review.auspiceBonusNotes.map{
            $0.trimmingCharacters(in:CharacterSet(charactersIn:"。"))
        }
        if review.firstMacroFiveNot {desc.insert("五不遇时成立，各实际参与实宫均减两分",at:0)}
        let macroProse=try fullMacro(chart,review)
        let pace=macroProse.contains("缓急并列待具体条件核定") ?
            "伏吟反吟并见，缓急合参" :
            macroProse.contains("伏吟主慢") ? "伏吟主慢" :
            macroProse.contains("反吟主快") ? "反吟主快" :
            "无整盘伏吟反吟，缓急另核"
        desc.insert(pace,at:0)
        let evidence=desc.joined(separator:"；")
        let verdict:String
        if let score=review.score {
            let grade=score==0 ? "不凶不吉" : signed(score)
            verdict=try phrase("overall_resolved",["grade":grade,
                "score":String(score),"post_void_sum":String(review.postVoidKnownSum),
                "palace_count":String(review.palaces.count)])
        } else {
            verdict=try phrase("overall_pending",[
                "post_void_sum":String(review.postVoidKnownSum)])
        }
        let second=verdict.trimmingCharacters(in:CharacterSet(charactersIn:"。"))
        push("90_review",try title("verdict"),
             try phrase("verdict",["evidence":evidence,"conclusion":second]))
        push("91_timing",try title("timing"),try phrase("timing",[
            "horse":chart.hourHorse]))
        return result
    }
}
