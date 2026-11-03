import Foundation

// Recovery is an independent deterministic topic. Frozen V9/V11 provides
// binding, actual void state and qualified control evidence without rescoring.
// All output is conditional traditional interpretation, never clinical proof.
struct WenguaRecoveryRole: Codable {
    let id:String
    let palace:Int
    let symbol:String
    let carrier:String
    let earth_stem:String
    let void_state:String
    let void_branches:[String]
    let horse_branch:String?
    let tomb_branches:[String]
}
struct WenguaRecoveryControl: Codable {
    let role:String
    let direction:String
    let cell:String?
    let eligible:Bool
    let attacker:String
}
struct WenguaRecoveryFacts: Codable {
    let reference_iso:String
    let timezone:String
    let pillars:WenguaNativePillars
    let dun:String
    let fuyin:Bool
    let fanyin:Bool
    let roles:[WenguaRecoveryRole]
    let controls:[WenguaRecoveryControl]
}
struct WenguaRecoveryMethod: Codable, Equatable {
    let role:String
    let palace:Int
    let method:String
    let branches:[String]
    let stems:[String]
    let rule_ids:[String]
    let status:String
}
struct WenguaRecoveryPeriod: Codable, Equatable {
    let scale:String
    let start_iso:String
    let end_iso:String
    let period_start_iso:String
    let period_end_iso:String
    let ganzhi:String
    let branch:String
    let stem:String
    let calendar_method:String
    var calendar_receipt:String
    var support_role:String? = nil
    var method_roles:[String]? = nil
    var rule_ids:[String]? = nil
    var role:String? = nil
    var kind:String? = nil
}
struct WenguaRecoverySearch: Codable {
    let support_role:String
    let scale:String
    let searched_periods:Int
    let matching_periods:Int
    let calendar_end_iso:String?
}
struct WenguaRecoveryPrecision: Codable {
    let scale:String
    let reason:String
}
struct WenguaRecoveryResult: Encodable {
    let version:String
    let topic_id:String
    let status:String
    let reference_iso:String
    let timezone:String
    let goal:String
    let time_scale:String?
    let deadline_iso:String?
    let sections:[WenguaNativeCustomerSection]
    let windows:[WenguaRecoveryPeriod]
    let methods:[WenguaRecoveryMethod]
    let alternative_windows:[WenguaRecoveryPeriod]
    let support:[WenguaRecoveryControl]
    let counterevidence:[WenguaRecoveryControl]
    let calendar_search:[WenguaRecoverySearch]
    let precision_limits:[WenguaRecoveryPrecision]
    let source_id:String
    let source_sha256:String
    let conditional_only:Bool = true
    let medical_validity_claimed:Bool = false
    enum CodingKeys:String,CodingKey {
        case version,topic_id,status,reference_iso,timezone,goal,time_scale,deadline_iso,sections,windows,methods,alternative_windows,support,counterevidence,calendar_search,precision_limits,source_id,source_sha256,conditional_only,medical_validity_claimed
    }
    init(version:String,topic_id:String,status:String,reference_iso:String,timezone:String,goal:String,time_scale:String?,deadline_iso:String?,sections:[WenguaNativeCustomerSection],windows:[WenguaRecoveryPeriod],methods:[WenguaRecoveryMethod],alternative_windows:[WenguaRecoveryPeriod],support:[WenguaRecoveryControl],counterevidence:[WenguaRecoveryControl],calendar_search:[WenguaRecoverySearch],precision_limits:[WenguaRecoveryPrecision],source_id:String,source_sha256:String) {
        self.version=version;self.topic_id=topic_id;self.status=status;self.reference_iso=reference_iso;self.timezone=timezone;self.goal=goal;self.time_scale=time_scale;self.deadline_iso=deadline_iso;self.sections=sections;self.windows=windows;self.methods=methods;self.alternative_windows=alternative_windows;self.support=support;self.counterevidence=counterevidence;self.calendar_search=calendar_search;self.precision_limits=precision_limits;self.source_id=source_id;self.source_sha256=source_sha256
    }
}
struct WenguaRecoveryRuntime: Decodable {
    struct Clock:Decodable {let method:String;let crossings_utc_ms:[Int64]}
    struct Tables:Decodable {
        let branches:[String];let stems:[String]
        let palace_branches:[String:[String]];let hidden:[String:String]
        let join:[String:String];let clash:[String:String];let stem_join:[String:String]
        let stem_elements:[String:String];let branch_elements:[String:String]
        let star_elements:[String:String];let strong_cells:[String]
        let ordinary_punishment:[String:[String]];let timing_tombs:[String:[String]]
        let home_stars:[String:Int];let home_doors:[String:Int];let opposite:[String:Int]
    }
    struct Policy:Decodable {
        let support_roles:[String];let role_priority:[String]
        let horizons:[String:Int];let maximum_windows_per_scale:Int
    }
    struct Text:Decodable {
        let titles:[String];let role_names:[String:String];let units:[String:String]
        let premise_missing:String;let premise_conflict:String;let method_conflict:String
        let no_candidate:String;let precision_missing:String;let flow_conflict:String
        let context_conflict:String;let stem_branch_conflict:String;let chief_xun_conflict:String
        let unknown_axis:String;let known_axis:String;let scale_line:String;let support:String
        let conditions:String;let summary:String;let footer:String;let not_ready_summary:String
        let method_names:[String:String];let role_method:String;let fact_names:[String:String];let window_zone:String
    }
    let schema:String;let version:String;let source_id:String;let source_sha256:String
    let calendar:Clock;let tables:Tables;let policy:Policy;let text:Text
    static func fromData(_ data:Data) throws -> WenguaRecoveryRuntime {
        let r=try JSONDecoder().decode(Self.self,from:data)
        guard r.schema=="wengua_health_recovery_runtime_v3",r.version=="health.recovery.V3",
              r.source_sha256=="db098ffb881fb1665b05a712ca634974c1365e0e40462b899a986d0dfe546fb5",
              r.calendar.crossings_utc_ms.count==385,r.text.titles.count==4,
              r.tables.branches==WenguaNativeCore.branches,r.tables.stems==WenguaNativeCore.stems else {
            throw WenguaNativeReadingError.invalidPhrase
        }
        return r
    }
}
enum WenguaRecoveryError:Error,LocalizedError {
    case invalidTime,precision(String),invalidFacts
    var errorDescription:String? {
        switch self {
        case .invalidTime:return "需要一致的起局时刻和发生地时区"
        case .precision(let s):return s
        case .invalidFacts:return "疾病应期所需的同盘人物和制病依据不完整"
        }
    }
}
enum WenguaNativeRecovery {
    static func parse(_ s:String) throws -> Date {
        let f=ISO8601DateFormatter()
        f.formatOptions=[.withInternetDateTime,.withFractionalSeconds]
        if let d=f.date(from:s) {return d}
        f.formatOptions=[.withInternetDateTime]
        guard let d=f.date(from:s) else {throw WenguaRecoveryError.invalidTime}
        return d
    }
    static func iso(_ d:Date,_ zone:TimeZone)->String {
        let f=ISO8601DateFormatter();f.timeZone=zone
        let millis=(d.timeIntervalSince1970*1000).rounded()
        f.formatOptions=abs(millis.truncatingRemainder(dividingBy:1000))>0.1 ? [.withInternetDateTime,.withFractionalSeconds] : [.withInternetDateTime]
        return f.string(from:Date(timeIntervalSince1970:millis/1000)).replacingOccurrences(of:"Z",with:"+00:00")
    }
    static func calendarPeriods(reference:String,zoneID:String,scale:String,
                                runtime r:WenguaRecoveryRuntime,deadline:String?=nil) throws -> [WenguaRecoveryPeriod] {
        guard let zone=TimeZone(identifier:zoneID),let days=r.policy.horizons[scale] else {throw WenguaRecoveryError.invalidTime}
        let ref=try parse(reference)
        guard iso(ref,zone)==reference.replacingOccurrences(of:"Z",with:"+00:00") else {throw WenguaRecoveryError.invalidTime}
        var cal=Calendar(identifier:.gregorian);cal.timeZone=zone
        guard let year=cal.dateComponents([.year],from:ref).year,(1850...2150).contains(year),
              var horizon=cal.date(byAdding:.day,value:days,to:ref) else {throw WenguaRecoveryError.invalidTime}
        if let deadline {
            let end=try parse(deadline)
            guard iso(end,zone)==deadline.replacingOccurrences(of:"Z",with:"+00:00"),end>ref else {throw WenguaRecoveryError.invalidTime}
            horizon=min(horizon,end)
        }
        var rows:[WenguaRecoveryPeriod]=[]
        func append(_ begin:Date,_ finish:Date,_ gz:String,_ method:String) {
            let lo=max(begin,ref),hi=min(finish,horizon)
            guard lo<hi else {return}
            let a=iso(begin,zone),b=iso(finish,zone)
            rows.append(.init(scale:scale,start_iso:iso(lo,zone),end_iso:iso(hi,zone),
                period_start_iso:a,period_end_iso:b,ganzhi:gz,branch:String(gz.suffix(1)),
                stem:String(gz.prefix(1)),calendar_method:method,
                calendar_receipt:method+"|"+zoneID+"|"+a+"|"+b+"|"+gz))
        }
        func dayGZ(_ d:Date)throws->String {
            var utc=Calendar(identifier:.gregorian);utc.timeZone=TimeZone(secondsFromGMT:0)!
            let parts=cal.dateComponents([.year,.month,.day],from:d)
            guard let now=utc.date(from:parts),let anchor=utc.date(from:DateComponents(year:1995,month:6,day:11)),
                  let offset=utc.dateComponents([.day],from:anchor,to:now).day else {throw WenguaRecoveryError.invalidTime}
            let i=((9+offset)%60+60)%60
            return r.tables.stems[i%10]+r.tables.branches[i%12]
        }
        if scale=="day" || scale=="hour" {
            var midnight=cal.startOfDay(for:ref)
            while midnight<horizon {
                guard let tomorrow=cal.date(byAdding:.day,value:1,to:midnight) else {throw WenguaRecoveryError.invalidTime}
                let gz=try dayGZ(midnight)
                if scale=="day" {append(midnight,tomorrow,gz,"source_book_day_anchor_civil_midnight_v1")}
                else {
                    for hour in stride(from:1,to:23,by:2) {
                        func boundary(_ h:Int)throws->Date {
                            var parts=cal.dateComponents([.year,.month,.day],from:midnight)
                            parts.hour=h;parts.minute=0;parts.second=0
                            guard let date=cal.date(from:parts),cal.component(.hour,from:date)==h else {
                                throw WenguaRecoveryError.precision("Ambiguous or nonexistent local hour boundary")
                            }
                            let clock=DateComponents(hour:h,minute:0,second:0)
                            let first=cal.nextDate(after:midnight.addingTimeInterval(-1),matching:clock,matchingPolicy:.strict,repeatedTimePolicy:.first)
                            let last=cal.nextDate(after:midnight.addingTimeInterval(-1),matching:clock,matchingPolicy:.strict,repeatedTimePolicy:.last)
                            guard first==last else {throw WenguaRecoveryError.precision("Ambiguous or nonexistent local hour boundary")}
                            return date
                        }
                        let begin=try boundary(hour),end=try boundary(hour+2),bi=(hour+1)/2
                        let starts=["甲":0,"己":0,"乙":2,"庚":2,"丙":4,"辛":4,"丁":6,"壬":6,"戊":8,"癸":8]
                        guard let start=starts[String(gz.prefix(1))] else {throw WenguaRecoveryError.invalidFacts}
                        append(begin,end,r.tables.stems[(start+bi)%10]+r.tables.branches[bi],"source_five_rat_non_zi_hour_v1")
                    }
                }
                midnight=tomorrow
            }
        } else {
            let selected=r.calendar.crossings_utc_ms.enumerated().filter { pair in
                let term=(1+pair.offset)%24
                return scale=="month" ? term%2==1 : term==3
            }.map{$0.element}
            let ms=Int64((ref.timeIntervalSince1970*1000).rounded())
            guard let k=selected.lastIndex(where:{$0<=ms}),k+1<selected.count else {
                throw WenguaRecoveryError.precision("Requested solar period outside strict crossing coverage")
            }
            horizon=min(horizon,Date(timeIntervalSince1970:Double(selected.last!)/1000))
            for i in k..<(selected.count-1) {
                let begin=Date(timeIntervalSince1970:Double(selected[i])/1000)
                let end=Date(timeIntervalSince1970:Double(selected[i+1])/1000)
                if begin>=horizon {break}
                let next=cal.date(byAdding:.day,value:1,to:begin)!
                let sample=cal.date(bySettingHour:12,minute:0,second:0,of:next)!
                let chart=try WenguaNativeCore.compute(at:sample,timezone:zoneID)
                append(begin,end,scale=="month" ? chart.pillars.month:chart.pillars.year,r.calendar.method)
            }
        }
        return rows
    }
    static func facts(chart:WenguaNativeChart,audit:WenguaVNextAudit,actor:WenguaNativeActor) throws -> WenguaRecoveryFacts {
        var roles:[WenguaRecoveryRole]=[]
        for key in audit.roles.keys.sorted() {
            guard let palace=audit.roles[key],let cell=chart.palaces.first(where:{$0.id==palace}),
                  let q=audit.rolePalaces[key],let symbol=audit.roleEnergy[key]?.symbol else {throw WenguaRecoveryError.invalidFacts}
            let carrier:String
            if let st=cell.heavenStars.first(where:{$0.star==symbol}) {carrier=st.carriedStem}
            else if key=="chief" {
                guard let st=cell.heavenStars.first(where:{$0.star==chart.valueStar}) else {throw WenguaRecoveryError.invalidFacts}
                carrier=st.carriedStem
            } else if symbol=="甲" {
                let source=key=="hour" ? chart.pillars.hour : key=="patient" ? actor.sourceGanzhi : actor.natalSourceGanzhi
                guard let source,let c=WenguaNativeActorSource.jiaCarrier(source) else {throw WenguaRecoveryError.invalidFacts}
                carrier=c
            } else {carrier=symbol}
            guard cell.heavenStars.contains(where:{$0.carriedStem==carrier}) else {throw WenguaRecoveryError.invalidFacts}
            roles.append(.init(id:key,palace:palace,symbol:symbol,carrier:carrier,earth_stem:cell.earthStem,
                void_state:q.void,void_branches:cell.voidBranches,horse_branch:cell.horseBranch,
                tomb_branches:Array(Set(cell.tombs.filter{$0.plane=="天盘" && $0.stem==carrier}.map{$0.branch})).sorted()))
        }
        let controls=audit.controls.map { c in
            WenguaRecoveryControl(role:c.role,direction:c.direction,cell:c.cell,
                eligible:["strong","limited"].contains(c.applicability),attacker:c.attacker)
        }
        let outer=chart.palaces.filter{$0.id != 5}
        let fuyin=outer.allSatisfy { p in p.heavenStars.filter{$0.star != "天禽星"}.allSatisfy{WenguaNativeReadingRouter.homeStars[$0.star]==p.id} && WenguaNativeReadingRouter.homeDoors[p.door ?? ""]==p.id }
        let fanyin=outer.allSatisfy { p in p.heavenStars.filter{$0.star != "天禽星"}.allSatisfy{WenguaNativeReadingRouter.opposites[WenguaNativeReadingRouter.homeStars[$0.star] ?? 0]==p.id} && WenguaNativeReadingRouter.opposites[WenguaNativeReadingRouter.homeDoors[p.door ?? ""] ?? 0]==p.id }
        return .init(reference_iso:chart.iso,timezone:chart.timezone,pillars:chart.pillars,dun:chart.bureau.dun,
                     fuyin:fuyin,fanyin:fanyin,roles:roles,controls:controls)
    }
    static func roleMethod(_ role:WenguaRecoveryRole,_ facts:WenguaRecoveryFacts,_ r:WenguaRecoveryRuntime) throws -> WenguaRecoveryMethod {
        let t=r.tables,p=role.palace,c=role.carrier,e=role.earth_stem
        guard let pb=t.palace_branches[String(p)] else {throw WenguaRecoveryError.invalidFacts}
        let a=t.hidden[c],b=t.hidden[e],key=c+":"+String(p)
        let clash=a.map { x in (b != nil && t.clash[x]==b) || pb.contains(t.clash[x] ?? "") } ?? false
        let join=t.stem_join[c]==e || (a.map {x in (b != nil && t.join[x]==b) || pb.contains(t.join[x] ?? "")} ?? false)
        let pun=t.ordinary_punishment[key] != nil || (a != nil && a==b && ["辰","午"].contains(a!))
        func out(_ method:String,_ branches:[String],_ refs:[String],_ status:String="selected",_ stems:[String]=[])->WenguaRecoveryMethod {
            let sorted=Array(Set(branches)).sorted{t.branches.firstIndex(of:$0)!<t.branches.firstIndex(of:$1)!}
            return .init(role:role.id,palace:p,method:method,branches:sorted,stems:stems,rule_ids:refs,status:status)
        }
        if role.id=="chief" {
            if clash,let a {return out("clash",[t.join[a]!],["T084","T088"])}
            if pun,let a {return out("punishment",[t.join[a]!],["T085","T088"])}
            if role.void_state=="true_void" {return out("void",role.void_branches,["T086","T088"],"chief_out_xun_requires_time_layer")}
        }
        if !["not_void","fake_void","true_void"].contains(role.void_state) {return out("void",[],["T051"],"void_unknown")}
        if role.void_state=="true_void" {
            if role.void_branches.isEmpty {return out("void",[],["T051"],"void_unknown")}
            return out("void",role.void_branches+role.void_branches.map{t.clash[$0]!},["T031","T051","T055"],"void_flow_unresolved",[c])
        }
        if let h=role.horse_branch {return out("horse",[h,t.clash[h]!],["T034","T056"])}
        let tombs=Array(Set(role.tomb_branches+(t.timing_tombs[key] ?? [])))
        if key=="庚:8" {return out("tomb",["申","丑","寅","未"],["T057","T066","T072"],"tomb_context_conflict")}
        if !tombs.isEmpty {return out("tomb",tombs.map{t.clash[$0]!},["T032","T057","T058","T063"])}
        if (pun || clash) && join && !(c=="辛" && p==2 && e=="戊") {return out("clash",[],["T060","T074"],"method_conflict")}
        if let special=t.ordinary_punishment[key] {return out("punishment",special,["T060","T064","T065","T066","T067"],key=="己:2" ? "punishment_context_conflict":"selected")}
        if let a,a==b,["辰","午"].contains(a) {return out("punishment",[t.join[a]!],["T061"])}
        if clash {
            let all=[a,b].compactMap{$0}+pb
            let parts=all.filter{x in all.contains(t.clash[x]!)}
            let stemAlternative=a != nil && b != nil && t.clash[a!]==b
            return out("clash",parts.map{t.join[$0]!},["T068","T069","T070","T071","T073"],stemAlternative ? "stem_branch_alternatives":"selected",stemAlternative ? [t.stem_join[c]!] : [])
        }
        if join {
            var targets:[String]
            if let a,pb.contains(t.join[a]!) {targets=[t.clash[a]!]}
            else {targets=[a,b].compactMap{$0}.map{t.clash[$0]!}}
            if targets.isEmpty {targets=t.palace_branches[String(t.opposite[String(p)]!)]!}
            return out("combination",targets,["T074","T075","T077","T078"])
        }
        if facts.fuyin {return out("fuyin",pb.map{t.clash[$0]!},["T080"])}
        if facts.fanyin {return out("fanyin",pb.map{t.join[$0]!},["T081"])}
        guard let el=t.star_elements[role.symbol] ?? t.stem_elements[role.symbol] else {return out("growth",[],["T079"],"growth_need_unknown")}
        return out("growth",t.branches.filter{t.branch_elements[$0]==el},["T028","T079"])
    }
    static func fill(_ text:String,_ fields:[String:String]) throws -> String {
        var s=text
        for (k,v) in fields {s=s.replacingOccurrences(of:"{"+k+"}",with:v)}
        guard !s.contains("{"),!s.contains("}") else {throw WenguaNativeReadingError.invalidPhrase}
        return s
    }
    static func analyze(_ facts:WenguaRecoveryFacts,runtime r:WenguaRecoveryRuntime,
                        timeScale:String?=nil,deadline:String?=nil) throws -> WenguaRecoveryResult {
        let tx=r.text,t=r.tables
        if let deadline,try parse(deadline)<=parse(facts.reference_iso) {throw WenguaRecoveryError.invalidTime}
        let roles=Dictionary(uniqueKeysWithValues:facts.roles.map{($0.id,$0)})
        guard let patient=roles["patient"],let hour=roles["hour"],roles["illness"] != nil else {throw WenguaRecoveryError.invalidFacts}
        if let timeScale,r.policy.horizons[timeScale]==nil {throw WenguaRecoveryError.invalidFacts}
        let supporters=facts.controls.filter{r.policy.support_roles.contains($0.role) && $0.direction=="克" && $0.attacker==$0.role && $0.eligible && t.strong_cells.contains($0.cell ?? "")}.sorted{r.policy.role_priority.firstIndex(of:$0.role)!<r.policy.role_priority.firstIndex(of:$1.role)!}
        let counter=facts.controls.filter{$0.role=="patient" && $0.direction=="被克" && $0.attacker=="illness" && $0.eligible && t.strong_cells.contains($0.cell ?? "")}
        let inner=facts.dun=="yang" ? [1,8,3,4]:[9,2,7,6]
        let pace=facts.fuyin ? "主迟滞、较慢":facts.fanyin ? "主变动、较快":inner.contains(patient.palace) && inner.contains(hour.palace) ? "内盘为主、较快":"内外盘交参、较慢"
        let paceText=(facts.fuyin ? "星门伏吟，":facts.fanyin ? "星门反吟，":"")+pace+"。"
        let scales=timeScale.map{[$0]} ?? ["day","month"]
        var state="recovery_premise_unresolved",reason=tx.premise_missing
        var methods:[WenguaRecoveryMethod]=[],windows:[WenguaRecoveryPeriod]=[],alternatives:[WenguaRecoveryMethod]=[]
        var traces:[WenguaRecoverySearch]=[],precision:[WenguaRecoveryPrecision]=[]
        if !supporters.isEmpty && !counter.isEmpty {state="recovery_premise_conflict";reason=tx.premise_conflict}
        else if !supporters.isEmpty {
            state=timeScale==nil ? "conditional_scales":"conditional_windows";reason=""
            let patientMethod=try roleMethod(patient,facts,r)
            let needsPatient=["void","horse","tomb","punishment","clash","combination"].contains(patientMethod.method)
            for support in supporters {
                guard let role=roles[support.role] else {throw WenguaRecoveryError.invalidFacts}
                var route=[try roleMethod(role,facts,r)]
                if needsPatient && support.role != "patient" {route.append(patientMethod)}
                for method in route where !methods.contains(method) {methods.append(method)}
                let bad=route.filter{$0.status != "selected"}
                if !bad.isEmpty {alternatives.append(contentsOf:bad);continue}
                for scale in scales {
                    let periods:[WenguaRecoveryPeriod]
                    do {periods=try calendarPeriods(reference:facts.reference_iso,zoneID:facts.timezone,scale:scale,runtime:r,deadline:deadline)}
                    catch {precision.append(.init(scale:scale,reason:error.localizedDescription));continue}
                    let matched=periods.filter{p in route.allSatisfy{$0.branches.contains(p.branch)}}
                    for var row in matched.prefix(r.policy.maximum_windows_per_scale) {
                        row.support_role=support.role;row.method_roles=route.map{$0.role}
                        row.rule_ids=Array(Set(route.flatMap{$0.rule_ids})).sorted()
                        if !windows.contains(row) {windows.append(row)}
                    }
                    traces.append(.init(support_role:support.role,scale:scale,searched_periods:periods.count,matching_periods:matched.count,calendar_end_iso:periods.last?.end_iso))
                }
            }
            if windows.isEmpty {
                if alternatives.contains(where:{["tomb_context_conflict","punishment_context_conflict"].contains($0.status)}) {state="method_conflict";reason=tx.context_conflict}
                else if alternatives.contains(where:{$0.status=="method_conflict"}) {state="method_conflict";reason=tx.method_conflict}
                else if alternatives.contains(where:{["void_flow_unresolved","chief_out_xun_requires_time_layer","stem_branch_alternatives"].contains($0.status)}) {
                    state="method_conflict";reason=alternatives.contains(where:{$0.status=="void_flow_unresolved"}) ? tx.flow_conflict:alternatives.contains(where:{$0.status=="chief_out_xun_requires_time_layer"}) ? tx.chief_xun_conflict:tx.stem_branch_conflict
                } else if !precision.isEmpty {state="precision_unavailable";reason=tx.precision_missing}
                else {state="missing_condition";reason=tx.no_candidate}
            }
        }
        var alternativeWindows:[WenguaRecoveryPeriod]=[]
        for method in alternatives {
            for scale in scales {
                guard let periods=try? calendarPeriods(reference:facts.reference_iso,zoneID:facts.timezone,scale:scale,runtime:r,deadline:deadline) else {continue}
                for (kind,items) in [("branch",periods.filter{method.branches.contains($0.branch)}),("stem",periods.filter{method.stems.contains($0.stem)})] {
                    for var row in items.prefix(3) {row.role=method.role;row.kind=kind;alternativeWindows.append(row)}
                }
            }
        }
        methods.sort{($0.role,$0.method)<($1.role,$1.method)}
        let timeText:String,summary:String
        if !windows.isEmpty {
            var lines=[timeScale==nil ? tx.unknown_axis:try fill(tx.known_axis,["unit":tx.units[timeScale!]!]),try fill(tx.window_zone,["zone":facts.timezone])]
            for scale in scales {
                var unique:[String]=[]
                for w in windows.filter({$0.scale==scale}).sorted(by:{$0.start_iso<$1.start_iso}) {
                    let label=String(w.start_iso.prefix(16)).replacingOccurrences(of:"T",with:" ")+" 至 "+String(w.end_iso.prefix(16)).replacingOccurrences(of:"T",with:" ")+"（"+w.ganzhi+tx.units[scale]!+"）"
                    if !unique.contains(label) {unique.append(label)}
                }
                if !unique.isEmpty {lines.append(try fill(tx.scale_line,["unit":tx.units[scale]!,"windows":unique.prefix(3).joined(separator:"；")]))}
            }
            timeText=lines.joined(separator:"\n\n");summary=tx.summary+tx.conditions
        } else {timeText=reason;summary=tx.not_ready_summary}
        var basis:[String]=[]
        for c in supporters {
            guard let role=roles[c.role] else {throw WenguaRecoveryError.invalidFacts}
            basis.append(try fill(tx.support,["role":tx.role_names[c.role]!,"palace":String(role.palace),"cell":c.cell!]))
        }
        for m in methods {
            basis.append(try fill(tx.role_method,["role":tx.role_names[m.role]!,"palace":String(m.palace),"fact":tx.fact_names[m.method]!,"method":tx.method_names[m.method]!,"branches":m.branches.isEmpty ? "未定":m.branches.joined(separator:"、")]))
        }
        if !counter.isEmpty {basis.append(tx.premise_conflict)}
        if !alternatives.isEmpty {basis.append(windows.isEmpty ? reason:"部分取法仍有分歧，未用其候选替代已成立的条件路径。")}
        if basis.isEmpty {basis.append("现有分析未形成条件完整的制病链，不能仅凭全盘等级套用成功类应期。")}
        if !precision.isEmpty {basis.append(tx.precision_missing)}
        let contents=[timeText,paceText,basis.joined(separator:"\n\n"),summary]
        let ids=["01_recovery_time","02_pace","03_method","04_summary"]
        let sections=(0..<4).map{WenguaNativeCustomerSection(id:ids[$0],title:tx.titles[$0],text:contents[$0])}
        return .init(version:r.version,topic_id:"health.recovery",status:state,reference_iso:facts.reference_iso,timezone:facts.timezone,goal:"recovery",time_scale:timeScale,deadline_iso:deadline,sections:sections,windows:windows,methods:methods,alternative_windows:alternativeWindows,support:supporters,counterevidence:counter,calendar_search:traces,precision_limits:precision,source_id:r.source_id,source_sha256:r.source_sha256)
    }
    static func compose(chart:WenguaNativeChart,relationship:String,inquiry:WenguaNativeInquiry?,bundle:Bundle = .main) throws -> WenguaNativeCustomerReading {
        guard let url=bundle.url(forResource:"runtime_v3_20261102",withExtension:"json"),
              let pairs=bundle.url(forResource:"81_pairs",withExtension:"tsv") else {throw WenguaNativeReadingError.missingPhrases}
        let runtime=try WenguaRecoveryRuntime.fromData(Data(contentsOf:url))
        let request=inquiry ?? .standard(relationship)
        guard request.relationship==relationship else {throw WenguaNativeReadingError.unsupportedRelationship}
        let source=try WenguaNativeActorSource.fromBundle(bundle)
        let actor=try WenguaNativeActorSource.bind(chart:chart,inquiry:request,index:source)
        let audit=try WenguaVNextEngine.compute(chart:chart,relationship:relationship,energy:WenguaNativeEnergyBundle.fromBundle(bundle),catalog:String(contentsOf:pairs,encoding:.utf8),actor:actor)
        let result=try analyze(facts(chart:chart,audit:audit,actor:actor),runtime:runtime)
        var reading=WenguaNativeCustomerReading(version:runtime.version,topicID:"health.recovery",relationship:relationship,iso:chart.iso,evidenceStatus:result.status,sections:result.sections,rolePalaces:audit.roles)
        reading.recoveryState=result.status
        reading.recoveryWindows=result.windows.map{$0.scale+"|"+$0.start_iso+"|"+$0.end_iso}
        reading.recoverySourceVersion=runtime.version
        return reading
    }
}
