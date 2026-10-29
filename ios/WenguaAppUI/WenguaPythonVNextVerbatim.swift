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
    private static func fullMacro(_ c:WenguaNativeChart,_ a:WenguaVNextAudit,
                                  macros:[String:String]) throws->String {
        let firstKey=a.firstMacroFiveNot ? "macro_five_customer":"macro_clear_customer"
        let byID=c.palaces
        let stars=byID.flatMap{p in p.heavenStars.compactMap{x->(String,Int)? in
            starOrigins[x.star] != nil ? (x.star,p.id) : nil
        }}
        let doors=byID.compactMap{p->(String,Int)? in
            guard let x=p.door,doorOrigins[x] != nil else {return nil}
            return (x,p.id)
        }
        guard stars.count==8,doors.count==8 else {throw WenguaCastError.invalidChart}
        func status(_ items:[(String,Int)],_ homes:[String:Int],_ inverse:Bool)->Bool {
            items.allSatisfy{row in
                guard let origin=homes[row.0] else{return false}
                return row.1 == (inverse
                    ? WenguaNativeReadingRouter.opposites[origin] : origin)
            }
        }
        let slow=status(stars,starOrigins,false) || status(doors,doorOrigins,false)
        let fast=status(stars,starOrigins,true) || status(doors,doorOrigins,true)
        let paceKey=slow && fast ? "macro_pace_mixed" :
                    slow ? "macro_pace_slow" :
                    fast ? "macro_pace_fast" : "macro_pace_unset"
        let goodKey=a.tianxianHour ?
            (slow ? "tianxian_fuyin" : "tianxian_regular") : nil
        guard let first=macros[firstKey],let pace=macros[paceKey] else {
            throw WenguaNativeReadingError.missingPhrases
        }
        let good:String
        if let key=goodKey {
            guard let word=macros[key] else {throw WenguaNativeReadingError.missingPhrases}
            good=word
        } else {good=""}
        return [first,good,pace].filter{ !$0.isEmpty }.joined(separator:" ")

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
                                   formations:[Int:WenguaHealthFormationBlock],
                                   kunHostNote:String,palaceTemplate:String)
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
        // Each actual sky carrier has a distinct 81 pattern; do not
        // mis-attribute Tianqin's carried stem to Tianrui.
        let accepted=p.heavenStars
        let heaven=try accepted.map{
            try powerStem($0.carriedStem,stages:$0.stages,
                          palace:p.id,month:month,energy:energy)
        }.joined(separator:"、")
        let earth=try powerStem(p.earthStem,stages:p.earthStages,
                                palace:p.id,month:month,energy:energy)
        var earthDesc=earth
        if p.id==2 {
            guard let hosted=chart.palaces.first(where:{$0.id==5})?.earthStem,
                  !hosted.isEmpty else {
                throw WenguaCastError.invalidChart
            }
            earthDesc+="、中五寄干"+hosted
        }
        let names=formation.sentences.map{
            String($0.components(separatedBy:"。古文").first ?? $0)
        }.joined(separator:"、")
        let klass=row.void=="not_void" ? "不空" :
                  row.void=="fake_void" ? "假空" : "真空"
        let special=try conditions(p,chart).replacingOccurrences(
            of:"无已核特殊刑墓迫",with:"无特别刑墓迫")
        var text=palaceTemplate
        let values:[String:String]=[
            "palace":label(p),"stars":(stars.isEmpty ? "无已核星":stars),
            "door":doorPart,"deity":try god(deity,pe),
            "heaven":(heaven.isEmpty ? "无":heaven),
            "earth":earthDesc,"patterns":(names.isEmpty ? "无已核天地格":names),
            "void":klass,"conditions":special,
            "grade":signed(review.roleScores[role])]
        for (key,value) in values {
            text=text.replacingOccurrences(of:"{"+key+"}",with:value)
        }
        if p.id==2 {text+=" "+kunHostNote}
        if text.contains("{") || text.contains("}") {
            throw WenguaNativeReadingError.invalidPhrase
        }
        return text

    }

    private static func roleAgainstIllness(
        _ role:String,review:WenguaVNextAudit,chart:WenguaNativeChart)throws->String {
        guard let aid=review.roles[role],
              let disease=review.roles["illness"],
              let energy=review.roleEnergy[role],
              let edge=review.controls.first(where:{$0.role==role}) else {
            return ""
        }
        let lead=energy.symbol+"势"+(energy.strength ?? "待核")
        let rel=relation(aid,disease)
        let note:String
        if role=="chief" && review.palaces[aid]?.void != "not_void" {
            note="逢空，护持受限"
        } else if rel=="克" {
            if review.controlBonusPalaces.contains(aid) &&
               ["strong","limited"].contains(edge.applicability) {
                note=(review.palaces[disease]?.void != "not_void"
                    ? "病宫逢空，制病有象" : "制病有象")
            } else if edge.applicability=="failed" {
                note="有克向而难成制"
            } else {note="虽有克向，效力未定"}
        } else if rel=="被克" {
            note="受病宫克，制约轻重依双方实际力量"
        } else if rel=="生" {
            note="生扶病宫，不作制病"
        } else if rel=="被生" {
            note="受病宫生，非主动制病"
        } else if rel=="比和" {
            note="与病宫比和，不等于等力"
        } else if rel=="同宫" {
            note="与病宫同宫，不另作跨宫克制"
        } else {note="与病宫关系待核"}
        return lead+"；"+note+"。"
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
        // Carry the RAW template until every factual placeholder is bound.
        // phrase() is intentionally strict and cannot be called yet here.
        guard let palacePattern=macros["palace_compact"] else {
            throw WenguaNativeReadingError.missingPhrases
        }
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
            "macro_text":fullMacro(chart,review,macros:macros)]))
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
                var kunNote=""
                if p.id==2 {kunNote=try phrase("kun_host_note")}
                full=try palaceText(p,role:role,chart:chart,review:review,
                                    energy:energy,formations:lookup,
                                    kunHostNote:kunNote,
                                    palaceTemplate:palacePattern)
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
                roleText=try roleAgainstIllness(role,review:review,chart:chart)
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
        // Real symbol aliases retain role identities but share one strength/direction narration.
        var seenSignifiers:Set<String>=[]
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
            let signifier=String(pid)+":"+symbol
            let repeatedSignifier=seenSignifiers.contains(signifier)
            if let existing=seenPalaces[pid] {
                head=name+"与"+existing+"同在"+label(p)
                if !repeatedSignifier {head+=suffix}
            } else {
                head=name+"落"+label(p)+"，宫象"+quality+suffix
                if state != "not_void" && key != "chief" {
                    head+="且逢"+(state=="true_void" ? "真空":"假空")
                }
                seenPalaces[pid]=name
            }
            if repeatedSignifier {
                desc.append(head)
                continue
            }
            seenSignifiers.insert(signifier)
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
                        head+="，制病能否成势未明"
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
        if review.firstMacroFiveNot {desc.insert(try phrase("summary_five_customer"),at:0)}
        let macroProse=try fullMacro(chart,review,macros:macros)
        if review.tianxianHour {
            let key=macroProse.contains("伏吟主慢")
                ? "tianxian_evidence_fuyin" : "tianxian_evidence_regular"
            desc.insert(try phrase(key),at:0)
        }
        let pace=macroProse.contains("缓急须看用神") ?
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
