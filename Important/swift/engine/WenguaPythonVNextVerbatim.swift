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
        return first+" 九星"+ss+"、八门"+ds+"。"+pace+" 缓急不自动等于吉凶。"
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
        let col=try monthColumn(symbol,month)
        var rows:[String]=[]
        for st in stages {
            let row=lifeRow(st.stage)
            if !rows.contains(row){rows.append(row)}
        }
        let options=try rows.map{
            $0+"势"+(try WenguaNativeEnergyBundle.cell("stem",row:$0,
                                                   column:col,catalog:energy))
        }
        return symbol+"长生分支待核（"+options.joined(separator:"／")+"）"
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
        let heaven=try p.heavenStars.map{
            try powerStem($0.carriedStem,stages:$0.stages,
                          palace:p.id,month:month,energy:energy)
        }.joined(separator:"、")
        let earth=try powerStem(p.earthStem,stages:p.earthStages,
                                palace:p.id,month:month,energy:energy)
        let book=formation.sentences.isEmpty ? "；本宫没有实际天地盘有序格" :
            "；天地格："+formation.sentences.joined(separator:"；")
        let klass=row.void=="not_void" ? "不空" :
                  row.void=="fake_void" ? "假空" : "真空"
        let special=try conditions(p,chart)
        return "落"+label(p)+"；九星"+(stars.isEmpty ? "无已核星":stars)+"；八神"+(try god(deity,pe))+"；八门"+doorPart+"；天盘干"+(heaven.isEmpty ? "无":heaven)+"、地盘干"+earth+book+"；空亡"+klass+"；"+special+"。全部因素推断后，此宫为"+signed(row.afterVoid)+"。"
    }

    private static func roleAgainstIllness(
        _ role:String,review:WenguaVNextAudit)throws->String {
        guard let a=review.roles[role],let b=review.roles["illness"],
              let own=review.roleEnergy[role],
              let disease=review.roleEnergy["illness"],
              let names=roleLabels[role],names.count==4,
              let edge=review.controls.first(where:{$0.role==role}) else {
            return ""
        }
        let r=relation(a,b)
        let who=names[0],source=names[1],success=names[2],failure=names[3]
        let cond="本宫用神力量"+(own.strength ?? "待核")+"，天芮病星力量"+(disease.strength ?? "待核")
        let out=edge.cell
        if r=="克" {
            let result:String
            if out==nil || edge.scenario==nil {
                result="有克病的五行方向，但当前克制条件尚未形成唯一有效结论"
            } else if solid.contains(out!) {
                result=success+"，从传统盘象看有压制病势、缓解病象的机会"
            } else if weak.contains(out!) {
                result=source+"可形成一定制约，但力度有限，只能说勉强压制病宫"
            } else if failed.contains(out!) {
                result=failure+"，尚看不出由此推动病象缓解的有效力量"
            } else {
                result="克制原格为"+out!+"，应结合已核宫内证据"
            }
            var words=result
            if role=="chief" && out != nil && solid.contains(out!) {
                words="求测人有值符吉神护持，"+words
            }
            if role=="chief" && out != nil && failed.contains(out!) {
                words="本盘虽见值符大吉神，但"+words
            }
            return who+"宫克天芮病宫；"+cond+"；克制表为"+(out ?? "条件待核")+"，"+words+"。"
        }
        if r=="被克" {
            let statement:String
            if let out,solid.contains(out) {
                statement="病宫有力克制本方，"+source+"受到明显压制，难以形成有效的制病助力"
            } else if let out,weak.contains(out) {
                statement="病宫虽来克本方，但克力有限，仍有相持空间"
            } else if let out,failed.contains(out) {
                statement="病宫名义克本宫却难落实，不能因此反断病必重"
            } else {
                statement="病宫克本方的实际力度尚需按原格和限制核算"
            }
            return who+"宫受天芮病宫克；"+cond+"；病宫施克结果"+(out ?? "条件待核")+"，"+statement+"。"
        }
        if r=="生" {
            return who+"宫生天芮病宫；"+cond+"。此时"+source+"在五行上反而生扶病宫，不能仅凭用神吉性便认为已压制病象。"
        }
        if r=="被生" {
            return who+"宫得病宫生扶；"+cond+"。本方有受生之象，但这不是主动克病，是否转为有利仍看宫内吉凶及人物条件。"
        }
        if r=="比和" {
            return who+"宫与病宫比和；"+cond+"。双方同气相持，并非本方已经克住病宫，应结合本宫吉凶力量合断。"
        }
        if r=="同宫" {
            return who+"与天芮同宫；"+cond+"。病象与"+source+"在同一宫交织，不能虚构两宫的相克，需要看本宫神星门干格局。"
        }
        return who+"与病宫的作用方向仍未核。"
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
                full="与前述"+original+"同在"+label(p)+"。全部因素推断后，此宫为"+signed(review.palaces[pid]?.afterVoid)+"。"
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
            let roleText=try roleAgainstIllness(role,review:review)
            let concise=roleText.components(separatedBy:"；").first ?? ""
            let simple=concise.trimmingCharacters(in:CharacterSet(charactersIn:"。"))
            let relationshipPhrase=concise.isEmpty ? "" : simple+"。"
            let relationText=role=="illness" ? "" :
                try phrase("role_relation",["relation_text":relationshipPhrase])
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
        push("90_review",try title("verdict"),
             try phrase("verdict",["conclusion":verdict]))
        push("91_timing",try title("timing"),try phrase("timing",[
            "horse":chart.hourHorse]))
        return result
    }
}
