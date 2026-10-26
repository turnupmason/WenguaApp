import Foundation

// Converts the ACTUAL already-computed V-next factor ledger to editable
// qualitative prose. Internal points are consulted for every decision, but
// NEVER interpolated or returned in a customer section. This does not run
// another competing model or search the books/SQLite.
enum WenguaVNextReasoner {
    private static let roleTitles=[
        "illness":"天芮病宫","doctor":"天心医者","medicine":"乙奇医药",
        "patient":"患者用神","hour":"时干事体","chief":"值符",
        "natal":"出生年命","gender":"性别辅助",
        "qian":"乾宫辅助","kun":"坤宫辅助"
    ]
    private static func trend(_ n:Int?) ->String {
        guard let n else {return "尚有条件无法核定"}
        if n > 0 {return n >= 4 ? "助力明显" : "偏向有利"}
        if n < 0 {return n <= -4 ? "不利明显" : "偏向不利"}
        return "有利不利相持"
    }
    private static func factorTrend(_ value:Int?)->String {
        if value==0 {return "此项中性，不额外加重吉凶"}
        return trend(value)
    }
    private static func elementRelationText(_ original:String,
                                            kind:String)->String {
        let actor=kind=="god" ? "八神" : kind=="door" ? "门" : "星"
        switch original {
        case "符号生宫":return actor+"生落宫"
        case "宫生符号":return "落宫生"+actor
        case "符号克宫":return actor+"克落宫"
        case "宫克符号":return "落宫克"+actor
        case "比和":return "与落宫比和"
        default:return original
        }
    }
    private static func relation(_ source:Int,_ target:Int)->String {
        if source==target{return "同宫"}
        let e=WenguaNativeReadingRouter.palaceElements
        let gen=WenguaNativeReadingRouter.generating
        let ctrl=WenguaNativeReadingRouter.controlling
        guard let x=e[source],let y=e[target] else{return "待核"}
        if x==y{return "比和"}
        if ctrl[x]==y{return "克"}
        if ctrl[y]==x{return "被克"}
        if gen[x]==y{return "生"}
        if gen[y]==x{return "被生"}
        return "待核"
    }
    static func build(_ audit:WenguaVNextAudit,chart:WenguaNativeChart,
                      template:Data)throws->[WenguaNativeCustomerSection] {
        guard let root=try JSONSerialization.jsonObject(with:template) as? [String:Any],
              let words=root["native_customer"] as? [String:String] else{
            throw WenguaNativeReadingError.missingPhrases
        }
        let required=[
            "reason_role_palace","reason_factor_star","reason_factor_door",
            "reason_factor_god","reason_factor_pattern","reason_cohost",
            "reason_empty_source","reason_void","reason_break",
            "reason_palace_final","reason_role_strength","reason_control_applied",
            "reason_control_pending","reason_control_failed",
            "reason_relation_other","reason_shared","reason_detail",
            "reason_title_details","reason_title_illness","reason_title_relation",
            "reason_title_verdict","reason_verdict_candidate",
            "reason_verdict_conflict","reason_verdict_resolved",
            "reason_verdict_incomplete","reason_tianrui_25"
        ]
        guard required.allSatisfy({!(words[$0] ?? "").isEmpty}) else {
            throw WenguaNativeReadingError.missingPhrases
        }
        func fill(_ key:String,_ inputs:[String:String]=[:])throws->String {
            guard var result=words[key] else{throw WenguaNativeReadingError.missingPhrases}
            for (k,v) in inputs {
                result=result.replacingOccurrences(of:"{"+k+"}",with:v)
            }
            if result.contains("{") || result.contains("}") {
                throw WenguaNativeReadingError.invalidPhrase
            }
            return result
        }
        let byID=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        func name(_ id:Int)->String {
            guard let p=byID[id] else{return "未核宫"}
            return p.gua+String(id)+"宫"
        }
        func factorLine(_ f:WenguaVNextStrengthEvidence)throws->String {
            let stage=f.monthStage ?? "不适用"
            let sign=factorTrend(f.internalScore)
            let relation=elementRelationText(f.palaceRelation ?? "未核",kind:f.source)
            let tier=f.tier ?? "未核"
            let lifes=f.lifeStages.isEmpty ? "未核" : f.lifeStages.joined(separator:"、")
            let lim=f.restrictions.isEmpty ? "" :
                "，受"+f.restrictions.joined(separator:"、")+"影响"
            switch f.source {
            case "cohost":
                return try fill("reason_cohost",["symbol":f.symbol])
            case "star":
                return try fill("reason_factor_star",[
                    "symbol":f.symbol,"month":stage,"relation":relation,
                    "tier":tier,"effect":sign])
            case "door":
                return try fill("reason_factor_door",[
                    "symbol":f.symbol,"month":stage,"relation":relation,
                    "tier":tier,"effect":sign])
            case "god":
                return try fill("reason_factor_god",[
                    "symbol":f.symbol,"relation":relation,
                    "tier":tier,"effect":sign])
            case "pattern":
                return try fill("reason_factor_pattern",[
                    "symbol":f.symbol,"polarity":relation,"life":lifes,
                    "effect":sign,"restriction":lim])
            default:throw WenguaNativeReadingError.invalidPhrase
            }
        }
        func shifts(_ row:WenguaVNextPalace)throws->String {
            var parts:[String]=[]
            if row.doorBreak {
                parts.append(try fill("reason_break"))
            }
            if row.void != "not_void" {
                let adjustment:String
                if (row.beforeVoid ?? 0)>0 {adjustment="削弱原有有利因素"}
                else if (row.beforeVoid ?? 0)<0 {adjustment="减轻原有不利因素"}
                else {adjustment="没有额外改变原有吉凶方向"}
                parts.append(try fill("reason_void",[
                    "void":row.void=="fake_void" ? "假空":"真空",
                    "effect":adjustment]))
            }
            if !row.unresolved.isEmpty {
                parts.append(try fill("reason_empty_source",[
                    "conditions":row.unresolved.joined(separator:"、")]))
            }
            return parts.joined(separator:"；")
        }
        // Main judgment follows the actual PRIMARY roles only. One physical
        // palace is interpreted once, even if patient shares the medicine.
        var important:[String]=[]
        var printed:Set<Int>=[]
        for role in ["illness","doctor","medicine","patient"] {
            guard let id=audit.roles[role],let row=audit.palaces[id] else{continue}
            if !printed.insert(id).inserted {
                important.append(try fill("reason_shared",[
                    "role":roleTitles[role] ?? role,"palace":name(id)]))
                continue
            }
            let focus=(role=="illness" ? row.energyEvidence.first(where:{
                $0.source=="star" && $0.symbol=="天芮星"
            }) : row.energyEvidence.first(where:{$0.source=="star"}))
            let star=try focus.map{try factorLine($0)} ?? ""
            let door=try row.energyEvidence.first(where:{$0.source=="door"})
                .map{try factorLine($0)} ?? ""
            let god=try row.energyEvidence.first(where:{$0.source=="god"})
                .map{try factorLine($0)} ?? ""
            let pair=try row.energyEvidence.first(where:{$0.source=="pattern"})
                .map{try factorLine($0)} ?? ""
            important.append(try fill("reason_role_palace",[
                "role":roleTitles[role] ?? role,"palace":name(id),
                "star":star,"door":door,"god":god,"pattern":pair,
                "adjustment":try shifts(row),
                "conclusion":trend(row.afterVoid)]))
            if role=="illness" {
                let selected=try WenguaVNextTianrui25.caseFor(
                    chart:chart,audit:audit)
                important.append(try fill("reason_tianrui_25",[
                    "title":selected.title,"month":selected.starMonth,
                    "palace_month":selected.palaceMonth,
                    "relation":selected.category,"why":selected.why
                ]))
            }
        }
        // Full factor-level computation provenance is collapsible in the UI;
        // no scores or test-case outcomes in this customer DTO.
        var details:[String]=[]
        for id in audit.palaces.keys.sorted() {
            guard let row=audit.palaces[id] else{continue}
            var phrases:[String]=[]
            for item in row.energyEvidence {phrases.append(try factorLine(item))}
            let roles=row.roles.compactMap{roleTitles[$0]}.joined(separator:"、")
            details.append(try fill("reason_detail",[
                "palace":name(id),"roles":roles,
                "factors":phrases.joined(separator:"；"),
                "adjustment":try shifts(row),
                "conclusion":trend(row.afterVoid)]))
        }
        let illID=audit.roles["illness"] ?? 0
        var relations:[String]=[]
        var usedPairs:Set<String>=[]
        for role in ["doctor","medicine","patient","hour","chief",
                     "natal","gender"] {
            guard let id=audit.roles[role] else{continue}
            let pair=[id,illID].sorted().map(String.init).joined(separator:":")
            if !usedPairs.insert(pair).inserted {
                relations.append(try fill("reason_shared",[
                    "role":roleTitles[role] ?? role,"palace":name(id)]))
                continue
            }
            let control=audit.controls.first{$0.role==role}
            let direction=control?.direction ?? relation(id,illID)
            let strength=audit.roleEnergy[role]?.strength ?? "待核"
            let effect:String
            if let control, direction=="克" || direction=="被克" {
                if let text=control.cell {
                    let key=["strong","limited"].contains(control.applicability)
                        ? "reason_control_applied" :
                        control.applicability=="failed" ?
                        "reason_control_failed" : "reason_control_pending"
                    effect=try fill(key,[
                        "outcome":text,
                        "attacker":control.attacker=="illness" ?
                            "病宫制本方":"本方制病宫"])
                } else {
                    effect=try fill("reason_control_pending",[
                        "attacker":direction=="被克" ?
                            "病宫制本方":"本方制病宫",
                        "outcome":"待核"])
                }
            } else {
                let how:String
                switch direction {
                case "生":how="本方生扶病宫，但是否形成实际助病仍受本方强弱约束"
                case "被生":how="病宫生本方，不等于本方已制病"
                case "同宫":how="同宫不能当作独立的克制证据"
                case "比和":how="同气不能当作已制病"
                default:how="实际关系仍待证实"
                }
                effect=try fill("reason_relation_other",[
                    "explanation":how])
            }
            relations.append(try fill("reason_role_strength",[
                "role":roleTitles[role] ?? role,
                "palace":name(id),
                "strength":strength,
                "direction":direction,
                "effect":effect]))
        }
        let inner=trend(audit.score)
        let outer=audit.evidenceDirection=="favorable" ? "倾向有利" :
            audit.evidenceDirection=="adverse" ? "倾向不利" :
            "未能形成一致方向"
        let resolution:String
        if audit.roleStatus != "eligible" {
            resolution=try fill("reason_verdict_candidate",[
                "inner":inner,"outer":outer])
        } else if audit.score==nil {
            resolution=try fill("reason_verdict_incomplete",[
                "inner":inner,"outer":outer])
        } else if audit.evidenceConflict {
            resolution=try fill("reason_verdict_conflict",[
                "inner":inner,"outer":outer])
        } else {
            let qualified=audit.score!>0 ? "偏吉" :
                audit.score!<0 ? "偏凶" : "吉凶相持"
            resolution=try fill("reason_verdict_resolved",[
                "inner":inner,"outer":outer,"result":qualified])
        }
        return [
            WenguaNativeCustomerSection(id:"82vnext",
                 title:try fill("reason_title_illness"),
                 text:important.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"83vnext",
                 title:try fill("reason_title_relation"),
                 text:relations.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"87vnext",
                 title:try fill("reason_title_details"),
                 text:details.joined(separator:"\n")),
            WenguaNativeCustomerSection(id:"90vnext",
                 title:try fill("reason_title_verdict"),text:resolution)
        ]
    }
}
