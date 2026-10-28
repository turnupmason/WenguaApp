import Foundation

// Standalone read-only V8.0 graph invariants for actual Linux swiftc.
// Does NOT invoke or change illness V8.0 native score/reading templates.
@main
struct V80GraphNativeSmoke {
    static func resident(_ category:String,_ symbol:String,_ strength:String?="中等")
        -> WenguaGraphResident {
        WenguaGraphResident(category:category,symbolID:symbol,
            energyFactID:"synthetic-source-only:"+category+":"+symbol,
            strength:strength,signedContribution:nil,restrictions:[])
    }

    static func palace(_ id:Int,_ grade:Int,
                       flags:Set<String>=[]) -> WenguaGraphPalace {
        WenguaGraphPalace(
            palaceID:id,
            stars:[resident("star","天芮星","极小"),
                   resident("star","天心星","极大"),
                   resident("star","天柱星","小")],
            door:resident("door","开门"),
            deity:resident("deity","值符","小"),
            heavenStems:[resident("heaven_stem","乙","大"),
                          resident("heaven_stem","丁","中等")],
            earthStem:resident("earth_stem","戊","大"),
            ordered81Patterns:[resident("ordered_81_pattern","乙加戊","小")],
            flags:flags,auspiciousGrade:grade)
    }

    static func actor(_ role:String,_ kind:String,_ symbol:String,
                      _ palace:Int,_ power:String?) -> WenguaGraphUseGod {
        WenguaGraphUseGod(roleKey:role,kind:kind,symbolID:symbol,
           palaceID:palace,energyFactID:"role:"+kind+":"+symbol,
           strength:power,restrictions:[])
    }

    static func main() throws {
        let entries:[(String,String,String,String)] = [
            ("illness","star","天芮星","极小"),
            ("doctor","star","天心星","极大"),
            ("medicine","stem","乙","大"),
            ("patient","stem","戊","小"),
            ("hour","stem","丁","中等"),
            ("natal","stem","乙","大"),
            ("gender","star","天柱星","大"),
            ("chief","deity","值符","小"),
        ]
        let roles=entries.map{actor($0.0,$0.1,$0.2,3,$0.3)}
        let env=palace(3,4,flags:["真空","天盘入墓","六仪击刑"])
        let graph=try WenguaReadOnlySignifierGraphV80(
            domainID:"health.severity",roles:roles,palaces:[3:env])
        precondition(graph.byRole.count==8)
        precondition(graph.uniqueSignifiers.count==7)
        precondition(graph.signedBaseTotalOnce==4)
        precondition(graph.edges().count==42)
        precondition(graph.allRoleResidentFacts().count==8*env.residents.count)
        precondition(env.residents.map{$0.category}.contains("ordered_81_pattern"))
        let rule=WenguaGraphCohostCondition(
            conditionID:"health:independentYi",domainID:"health.severity",
            hostRoles:["doctor","medicine","natal","patient","chief"],
            helperKind:"stem",helperSymbolID:"乙")
        let matched=try graph.independentCohosts(rule)
        precondition(matched.count==3)
        precondition(matched.allSatisfy{$0.scoredPoints==nil})
        precondition(WenguaReadOnlySignifierGraphV80.spatial(3,8)=="九宫正邻位")
        precondition(WenguaReadOnlySignifierGraphV80.spatial(3,1)=="九宫斜邻位")
        precondition(WenguaReadOnlySignifierGraphV80.direction(
            actor("patient","stem","戊",8,"极大").identity,
            actor("illness","star","天芮星",1,"小").identity)=="克")
        let pairRoles=[actor("patient","stem","戊",8,"极大"),
                       actor("illness","star","天芮星",1,"小")]
        let paired=try WenguaReadOnlySignifierGraphV80(
            domainID:"health.severity",roles:pairRoles,
            palaces:[8:palace(8,-5,flags:["假空"]),1:palace(1,-3)])
        precondition(paired.signedBaseTotalOnce == -8)
        precondition(paired.edges().count==2)
        precondition(paired.edges().contains{$0.direction=="克"})
        var rejected=false
        do {
            _=try WenguaReadOnlySignifierGraphV80(
                domainID:"health.severity",roles:roles,palaces:[:])
        } catch {rejected=true}
        precondition(rejected,"Do not skip whole chosen-palace context")
        rejected=false
        do {
            _=try graph.independentCohosts(WenguaGraphCohostCondition(
                conditionID:"incorrect:otherDomain",domainID:"marriage",
                hostRoles:["doctor"],helperKind:"stem",helperSymbolID:"乙"))
        } catch {rejected=true}
        precondition(rejected,"No cross-domain inferred Yi medical bonus")
        print("V80_NATIVE_GENERAL_GRAPH_PASS roles=8 source_symbols=7 all_residents=\(env.residents.count) signed_grade_once=4 cohost_evidence=\(matched.count) points=none")
    }
}
