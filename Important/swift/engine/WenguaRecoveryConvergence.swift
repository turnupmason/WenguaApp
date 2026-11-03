import Foundation

// V4 binds the user's five-path reasoning to separate real objects. The
// recovery UI and historical adverse replay are distinct entry points.
struct WenguaV4StemRole:Codable {
    let symbol:String;let carrier:String;let palace:Int;let earth_stem:String
}
struct WenguaV4Executor:Codable {
    let palace:Int;let name:String;let sky_stems:[String];let sky_sources:[String];let earth_stem:String
}
struct WenguaV4Context:Codable {
    let executor:WenguaV4Executor;let year:WenguaV4StemRole;let natal:WenguaV4StemRole?
    let illness_palace:Int;let illness_palace_element:String;let illness_element:String;let month_branch:String
}
struct WenguaV4Month:Codable {
    let month_branch:String;let palace_stage:String;let illness_star_stage:String;let palace_controls_star:Bool
}
struct WenguaV4Corroboration:Encodable {
    let role:String;let carrier:String;let hidden:String;let palace:Int;let joins:[String];let clashes:[String]
}
struct WenguaV4Chosen:Encodable {
    let period:WenguaRecoveryPeriod;let support_role:String;let conditional_release:Bool
    let executor_stem_matched:Bool;let patient_ready_iso:String?
    enum CodingKeys:String,CodingKey {case support_role,conditional_release,executor_stem_matched,patient_ready_iso}
    func encode(to encoder:Encoder)throws {
        try period.encode(to:encoder)
        var c=encoder.container(keyedBy:CodingKeys.self)
        try c.encode(support_role,forKey:.support_role);try c.encode(conditional_release,forKey:.conditional_release)
        try c.encode(executor_stem_matched,forKey:.executor_stem_matched);try c.encodeIfPresent(patient_ready_iso,forKey:.patient_ready_iso)
    }
}
struct WenguaV4Result:Encodable {
    let version:String;let topic_id:String;let status:String;let sections:[WenguaNativeCustomerSection]
    let selected_day:WenguaV4Chosen?;let methods:[WenguaRecoveryMethod];let corroboration:[WenguaV4Corroboration]
    let internal_restraint:WenguaV4Month;let context:WenguaV4Context
    let uses_reported_outcome:Bool;let medical_validity_claimed:Bool
}
struct WenguaV4CaseDay:Encodable {let date:String;let ganzhi:String;let elapsed_days:Int}
struct WenguaV4Replay:Encodable {
    let kind:String;let month_branch:String;let duration_days:[Int];let duration_is_case_specific:Bool
    let natal_hidden_branch:String;let natal_palace_join:[String];let year_clash_palace_branches:[String]
    let year_half_join:Bool;let natal_tomb_branch:String;let day_branch:String
    let executor_stems:[String];let executor_stem_sources:[String];let executor_month_stage:String;let case_numbers:[Int];let month_evidence:WenguaV4Month
    let computed_dates:[WenguaV4CaseDay];let original_exact_date_prediction_made:Bool
}
struct WenguaV4Runtime {
    let priority:[String];let palaces:[String:String];let text:[String:Any]
    static func fromData(_ data:Data)throws->Self {
        guard let root=try JSONSerialization.jsonObject(with:data) as? [String:Any],
              root["schema"] as? String=="wengua_health_recovery_v4_convergence",
              root["version"] as? String=="health.recovery.V4",
              let priority=root["priority"] as? [String],let palaces=root["palaces"] as? [String:String],
              let text=root["text"] as? [String:Any] else {throw WenguaNativeReadingError.invalidPhrase}
        return .init(priority:priority,palaces:palaces,text:text)
    }
    func phrase(_ key:String,_ fields:[String:String]=[:])throws->String {
        guard let text=text[key] as? String else {throw WenguaNativeReadingError.invalidPhrase}
        return try WenguaNativeRecovery.fill(text,fields)
    }
}
enum WenguaRecoveryConvergence {
    static func context(chart:WenguaNativeChart,audit:WenguaVNextAudit,actor:WenguaNativeActor)throws->WenguaV4Context {
        guard let door=chart.palaces.first(where:{$0.door==chart.valueDoor}),
              let ill=audit.roles["illness"],let pe=WenguaNativeReadingRouter.palaceElements[ill] else {throw WenguaRecoveryError.invalidFacts}
        func stem(_ symbol:String,_ gz:String?)throws->WenguaV4StemRole {
            let carrier:String
            if symbol=="甲" {
                guard let gz,let value=WenguaNativeActorSource.jiaCarrier(gz) else {throw WenguaRecoveryError.invalidFacts}
                carrier=value
            } else {carrier=symbol}
            let found=chart.palaces.filter{$0.heavenStars.contains(where:{$0.carriedStem==carrier})}
            guard found.count==1 else {throw WenguaRecoveryError.invalidFacts}
            return .init(symbol:symbol,carrier:carrier,palace:found[0].id,earth_stem:found[0].earthStem)
        }
        let natal=try actor.natalStem.map{try stem($0,actor.natalSourceGanzhi)}
        return .init(executor:.init(palace:door.id,name:door.door!,sky_stems:door.heavenStars.map{$0.carriedStem},sky_sources:door.heavenStars.map{$0.star},earth_stem:door.earthStem),
            year:try stem(String(chart.pillars.year.prefix(1)),chart.pillars.year),natal:natal,
            illness_palace:ill,illness_palace_element:pe,illness_element:"土",month_branch:String(chart.pillars.month.suffix(1)))
    }
    static func monthFacts(_ context:WenguaV4Context,_ branch:String,_ shared:WenguaRecoveryRuntime)throws->WenguaV4Month {
        guard let el=shared.tables.branch_elements[branch] else {throw WenguaRecoveryError.invalidFacts}
        let p=context.illness_palace_element
        return .init(month_branch:branch,palace_stage:try WenguaVNextEngine.normalMonth(p,el),
            illness_star_stage:try WenguaVNextEngine.starMonth("土",el),
            palace_controls_star:WenguaNativeReadingRouter.controlling[p]==context.illness_element)
    }
    static func halfJoin(_ a:String,_ b:String)->Bool {
        a != b && [Set(["申","子","辰"]),Set(["亥","卯","未"]),Set(["寅","午","戌"]),Set(["巳","酉","丑"])].contains{Set([a,b]).isSubset(of:$0)}
    }
    static func monthConsensus(_ context:WenguaV4Context,_ shared:WenguaRecoveryRuntime)->[String] {
        let t=shared.tables
        guard let natal=context.natal,let h=t.hidden[natal.carrier],let yh=t.hidden[context.year.carrier],
              t.palace_branches[String(natal.palace)]!.contains(t.join[h]!) else {return []}
        let target=t.clash[h]!
        let opposing=t.palace_branches[String(context.year.palace)]!.filter{t.clash[yh]==$0}
        return opposing.contains(where:{halfJoin(target,$0)}) ? [target]:[]
    }
    static func constrain(_ rows:[WenguaRecoveryPeriod],_ facts:WenguaRecoveryFacts,_ shared:WenguaRecoveryRuntime,
                          duration:[Int]?=nil,months:[String]=[],branches:[String]=[],stems:[String]=[])throws->[WenguaRecoveryPeriod] {
        guard let zone=TimeZone(identifier:facts.timezone) else {throw WenguaRecoveryError.invalidTime}
        var cal=Calendar(identifier:.gregorian);cal.timeZone=zone
        let ref=try WenguaNativeRecovery.parse(facts.reference_iso)
        return try rows.filter { row in
            if !branches.isEmpty && !branches.contains(row.branch) {return false}
            if !stems.isEmpty && !stems.contains(row.stem) {return false}
            let d=try WenguaNativeRecovery.parse(row.start_iso)
            if let duration {
                let elapsed=cal.dateComponents([.day],from:cal.startOfDay(for:ref),to:cal.startOfDay(for:d)).day!
                if elapsed<duration[0] || elapsed>duration[1] {return false}
            }
            if !months.isEmpty {
                let noon=cal.date(bySettingHour:12,minute:0,second:0,of:d)!
                let clock=try WenguaNativeCore.compute(at:noon,timezone:facts.timezone)
                if !months.contains(String(clock.pillars.month.suffix(1))) {return false}
            }
            return true
        }
    }
    static func scopedMethod(_ role:WenguaRecoveryRole,_ facts:WenguaRecoveryFacts,_ shared:WenguaRecoveryRuntime)throws->WenguaRecoveryMethod {
        let t=shared.tables
        if ["not_void","fake_void"].contains(role.void_state),role.horse_branch==nil,role.tomb_branches.isEmpty,
           let a=t.hidden[role.carrier],let joined=t.join[a],t.palace_branches[String(role.palace)]!.contains(joined) {
            return .init(role:role.id,palace:role.palace,method:"combination",branches:[t.clash[a]!],stems:[],rule_ids:["T078","U003"],status:"selected")
        }
        return try WenguaNativeRecovery.roleMethod(role,facts,shared)
    }
    static func humanDate(_ iso:String)throws->String {
        let chunks=String(iso.prefix(10)).split(separator:"-")
        guard chunks.count==3,let year=Int(chunks[0]),let month=Int(chunks[1]),let day=Int(chunks[2]) else {throw WenguaRecoveryError.invalidTime}
        return "\(year)年\(month)月\(day)日"
    }
    static func replaySource(_ facts:WenguaRecoveryFacts,_ context:WenguaV4Context,_ shared:WenguaRecoveryRuntime)throws->WenguaV4Replay {
        let t=shared.tables
        guard let natal=context.natal,let hidden=t.hidden[natal.carrier],
              let pb=t.palace_branches[String(natal.palace)],let yhidden=t.hidden[context.year.carrier],
              let ypb=t.palace_branches[String(context.year.palace)] else {throw WenguaRecoveryError.invalidFacts}
        let joins=pb.filter{t.join[hidden]==$0},target=t.clash[hidden]!
        let opposing=ypb.filter{t.clash[yhidden]==$0}
        let evidence=try monthFacts(context,target,shared)
        guard !joins.isEmpty,evidence.palace_controls_star,evidence.palace_stage=="死",
              opposing.contains(where:{halfJoin(target,$0)}),
              let stages=WenguaNativeCore.stages[natal.symbol],let tomb=stages.first(where:{$0.value=="墓"})?.key,
              let zone=TimeZone(identifier:facts.timezone) else {throw WenguaRecoveryError.invalidFacts}
        let branch=t.clash[tomb]!,ref=try WenguaNativeRecovery.parse(facts.reference_iso)
        var cal=Calendar(identifier:.gregorian);cal.timeZone=zone
        var days:[WenguaV4CaseDay]=[]
        let periods=try WenguaNativeRecovery.calendarPeriods(reference:facts.reference_iso,zoneID:facts.timezone,scale:"day",runtime:shared)
        let matched=try constrain(periods,facts,shared,duration:[30,38],months:[target],branches:[branch],stems:context.executor.sky_stems)
        for row in matched {
            let d=try WenguaNativeRecovery.parse(row.start_iso)
            let elapsed=cal.dateComponents([.day],from:cal.startOfDay(for:ref),to:cal.startOfDay(for:d)).day!
            days.append(.init(date:String(row.start_iso.prefix(10)),ganzhi:row.ganzhi,elapsed_days:elapsed))
        }
        return .init(kind:"retrospective_adverse_source_reconstruction_not_recovery_prediction",month_branch:target,duration_days:[30,38],duration_is_case_specific:true,natal_hidden_branch:hidden,natal_palace_join:joins,year_clash_palace_branches:opposing,year_half_join:true,natal_tomb_branch:tomb,day_branch:branch,executor_stems:context.executor.sky_stems,executor_stem_sources:context.executor.sky_sources,executor_month_stage:try WenguaVNextEngine.normalMonth(WenguaNativeReadingRouter.palaceElements[t.home_doors[context.executor.name]!]!,t.branch_elements[context.month_branch]!),case_numbers:[3,8],month_evidence:evidence,computed_dates:days,original_exact_date_prediction_made:false)
    }
    static func analyze(_ facts:WenguaRecoveryFacts,_ context:WenguaV4Context,
                        _ c:WenguaV4Runtime,_ shared:WenguaRecoveryRuntime)throws->WenguaV4Result {
        let t=shared.tables,executor=context.executor
        let roles=Dictionary(uniqueKeysWithValues:facts.roles.map{($0.id,$0)})
        let paths=facts.controls.filter{c.priority.contains($0.role) && $0.direction=="克" && $0.attacker==$0.role && t.strong_cells.contains($0.cell ?? "")}.sorted {a,b in
            if a.eligible != b.eligible {return a.eligible}
            return c.priority.firstIndex(of:a.role)!<c.priority.firstIndex(of:b.role)!
        }
        let counter=facts.controls.contains{$0.role=="patient" && $0.direction=="被克" && $0.attacker=="illness" && $0.eligible && t.strong_cells.contains($0.cell ?? "")}
        let internalFact=try monthFacts(context,context.month_branch,shared)
        var basis:[String]=[],methods:[WenguaRecoveryMethod]=[],chosen:WenguaV4Chosen?=nil
        if internalFact.palace_controls_star {
            basis.append(try c.phrase("internal",["palace":c.palaces[String(context.illness_palace)]!,"stage":internalFact.palace_stage,"star_stage":internalFact.illness_star_stage]))
        }
        let coarse=monthConsensus(context,shared)
        if !coarse.isEmpty {
            let loss=try coarse.contains{let m=try monthFacts(context,$0,shared);return m.palace_controls_star && m.palace_stage=="死"}
            basis.append(try c.phrase(loss ? "coarse_adverse":"coarse",["branches":coarse.joined(separator:"、")]))
        }
        let periods=try WenguaNativeRecovery.calendarPeriods(reference:facts.reference_iso,zoneID:facts.timezone,scale:"day",runtime:shared)
        for path in paths {
            guard let role=roles[path.role],let patient=roles["patient"] else {throw WenguaRecoveryError.invalidFacts}
            let method=try scopedMethod(role,facts,shared);methods.append(method)
            if method.status != "selected" {continue}
            if !path.eligible && ["growth","fuyin","fanyin"].contains(method.method) {continue}
            let loss=try coarse.contains{let m=try monthFacts(context,$0,shared);return m.palace_controls_star && m.palace_stage=="死"}
            if loss {continue}
            var candidates=try constrain(periods,facts,shared,months:coarse,branches:method.branches)
            let pm=try scopedMethod(patient,facts,shared)
            var ready:String?=nil
            if patient.void_state=="true_void" || !patient.tomb_branches.isEmpty {
                guard let release=periods.first(where:{pm.branches.contains($0.branch)}) else {continue}
                ready=release.start_iso;candidates=candidates.filter{$0.start_iso>=release.start_iso}
            }
            guard !candidates.isEmpty else {continue}
            if let natal=roles["natal"],!natal.tomb_branches.isEmpty {
                let narrowed=try constrain(candidates,facts,shared,branches:natal.tomb_branches.map{t.clash[$0]!})
                if !narrowed.isEmpty {candidates=narrowed}
            }
            let refined=try constrain(candidates,facts,shared,stems:executor.sky_stems)
            let row=refined.first ?? candidates[0]
            chosen = .init(period:row,support_role:path.role,conditional_release:!path.eligible || counter,executor_stem_matched:!refined.isEmpty,patient_ready_iso:ready)
            basis.append(try c.phrase("control",["role":shared.text.role_names[path.role]!,"palace":c.palaces[String(role.palace)]!,"cell":path.cell!]))
            basis.append(try c.phrase("method",["method":shared.text.method_names[method.method]!,"branches":method.branches.joined(separator:"、")]))
            if let ready {basis.append(try c.phrase("patient_ready",["date":try humanDate(ready)]))}
            if !path.eligible {basis.append(try c.phrase("release_condition"))}
            if counter {basis.append(try c.phrase("patient_counter"))}
            break
        }
        basis.append(try c.phrase("executor",["door":executor.name,"palace":c.palaces[String(executor.palace)]!,"stems":executor.sky_stems.joined(separator:"、")]))
        if let chosen,chosen.executor_stem_matched {basis.append(try c.phrase("stem_refinement",["stem":chosen.period.stem]))}
        if context.natal==nil {basis.append(try c.phrase("no_natal"))}
        var corroboration:[WenguaV4Corroboration]=[]
        for (name,optional) in [("year",Optional(context.year)),("natal",context.natal)] {
            guard let role=optional,let h=t.hidden[role.carrier] else {continue}
            let pb=t.palace_branches[String(role.palace)]!,joins=pb.filter{t.join[h]==$0},clashes=pb.filter{t.clash[h]==$0}
            corroboration.append(.init(role:name,carrier:role.carrier,hidden:h,palace:role.palace,joins:joins,clashes:clashes))
            if !joins.isEmpty {basis.append(try c.phrase("hidden_join",["role":name=="year" ? "年干":"年命","a":h,"b":joins.joined(separator:"、"),"target":t.clash[h]!]))}
            if !clashes.isEmpty {basis.append(try c.phrase("year_clash",["role":name=="year" ? "年干":"年命","a":h,"b":clashes.joined(separator:"、")]))}
        }
        let status:String,headline:String
        if let chosen {
            status=chosen.conditional_release ? "release_day":"recovery_day"
            headline=try c.phrase(status,["date":try humanDate(chosen.period.start_iso),"ganzhi":chosen.period.ganzhi])
        } else {
            status="recovery_not_established";headline=try c.phrase("no_day")
            if paths.isEmpty {basis.append(try c.phrase("no_control"))}
            else if !methods.isEmpty {basis.append(try c.phrase("unresolved_method"))}
        }
        let pace=facts.fuyin ? "星门伏吟，进展偏慢。":facts.fanyin ? "星门反吟，变化较快。":"合看本次用神与病情取期。"
        let ids=["01_recovery_time","02_pace","03_method","04_summary"],titles=["病愈应期","缓急","取期依据","综合断语"]
        let content=[headline,pace,basis.joined(separator:"\n\n"),headline]
        return .init(version:"health.recovery.V4",topic_id:"health.recovery",status:status,sections:(0..<4).map{.init(id:ids[$0],title:titles[$0],text:content[$0])},selected_day:chosen,methods:methods,corroboration:corroboration,internal_restraint:internalFact,context:context,uses_reported_outcome:false,medical_validity_claimed:false)
    }
    static func compose(chart:WenguaNativeChart,relationship:String,inquiry:WenguaNativeInquiry?,bundle:Bundle = .main)throws->WenguaNativeCustomerReading {
        guard let v4URL=bundle.url(forResource:"runtime_v4_20261103",withExtension:"json"),
              let v3URL=bundle.url(forResource:"runtime_v3_20261102",withExtension:"json"),
              let pairURL=bundle.url(forResource:"81_pairs",withExtension:"tsv") else {throw WenguaNativeReadingError.missingPhrases}
        let c=try WenguaV4Runtime.fromData(Data(contentsOf:v4URL)),shared=try WenguaRecoveryRuntime.fromData(Data(contentsOf:v3URL))
        let request=inquiry ?? .standard(relationship)
        guard request.relationship==relationship else {throw WenguaNativeReadingError.unsupportedRelationship}
        let actor=try WenguaNativeActorSource.bind(chart:chart,inquiry:request,index:WenguaNativeActorSource.fromBundle(bundle))
        let audit=try WenguaVNextEngine.compute(chart:chart,relationship:relationship,energy:WenguaNativeEnergyBundle.fromBundle(bundle),catalog:String(contentsOf:pairURL,encoding:.utf8),actor:actor)
        let facts=try WenguaNativeRecovery.facts(chart:chart,audit:audit,actor:actor)
        let result=try analyze(facts,context(chart:chart,audit:audit,actor:actor),c,shared)
        var reading=WenguaNativeCustomerReading(version:result.version,topicID:"health.recovery",relationship:relationship,iso:chart.iso,evidenceStatus:result.status,sections:result.sections,rolePalaces:audit.roles)
        reading.recoveryState=result.status;reading.recoverySourceVersion=result.version
        reading.recoveryWindows=result.selected_day.map{[$0.period.start_iso+"|"+$0.period.end_iso]} ?? []
        return reading
    }
}
