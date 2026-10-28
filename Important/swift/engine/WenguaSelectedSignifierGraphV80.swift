import Foundation

// V8.0 observation / future V8.next candidate ONLY.
// Never used to change the accepted illness V8 scores or customer template.
// All chosen real use-gods require FULL physical-palace observation:
// stars, door, deity, heaven/earth stems, ordered 81, void/tomb/striking.
// +/- grade is auspiciousness only. Real symbol strength is separate.
enum WenguaGraphError: Error {
    case invalid(String)
}

struct WenguaGraphIdentity: Hashable {
    let kind: String
    let symbolID: String
    let palaceID: Int
}

struct WenguaGraphUseGod {
    let roleKey: String
    let kind: String
    let symbolID: String
    let palaceID: Int
    let energyFactID: String
    let strength: String?
    let restrictions: Set<String>

    var identity: WenguaGraphIdentity {
        WenguaGraphIdentity(kind: kind, symbolID: symbolID, palaceID: palaceID)
    }
}

struct WenguaGraphResident {
    let category: String
    let symbolID: String
    let energyFactID: String
    let strength: String?
    let signedContribution: Int?
    let restrictions: Set<String>
}

struct WenguaGraphPalace {
    let palaceID: Int
    let stars: [WenguaGraphResident]
    let door: WenguaGraphResident?
    let deity: WenguaGraphResident?
    let heavenStems: [WenguaGraphResident]
    let earthStem: WenguaGraphResident?
    let ordered81Patterns: [WenguaGraphResident]
    let flags: Set<String>
    let auspiciousGrade: Int

    var residents: [WenguaGraphResident] {
        stars + (door.map { [$0] } ?? []) + (deity.map { [$0] } ?? [])
        + heavenStems + (earthStem.map { [$0] } ?? []) + ordered81Patterns
    }

    func validate() throws {
        let allowedFlags: Set<String> = ["真空","假空","驿马","天盘入墓",
            "地盘入墓","六仪击刑","门迫","伏吟","反吟"]
        let categories: Set<String> = ["star","door","deity",
            "heaven_stem","earth_stem","ordered_81_pattern"]
        let tiers: Set<String> = ["极小","小","中等","大","极大"]
        let allowedResidentRestrictions: Set<String> = [
            "真空","假空","入墓","击刑","被宫克","门迫"]
        guard (1...9).contains(palaceID) && (-5...5).contains(auspiciousGrade),
              flags.isSubset(of: allowedFlags) else {
            throw WenguaGraphError.invalid("Invalid real palace and conditions")
        }
        for f in residents {
            guard categories.contains(f.category), !f.symbolID.isEmpty,
                  !f.energyFactID.isEmpty,
                  f.strength == nil || tiers.contains(f.strength!),
                  f.signedContribution == nil ||
                    (-5...5).contains(f.signedContribution!),
                  f.restrictions.isSubset(of:allowedResidentRestrictions) else {
                throw WenguaGraphError.invalid("Original strength and source required")
            }
        }
        guard stars.allSatisfy({$0.category == "star"}),
              door == nil || door?.category == "door",
              deity == nil || deity?.category == "deity",
              heavenStems.allSatisfy({$0.category == "heaven_stem"}),
              earthStem == nil || earthStem?.category == "earth_stem",
              ordered81Patterns.allSatisfy({$0.category == "ordered_81_pattern"})
        else { throw WenguaGraphError.invalid("Misbound source category") }

        if palaceID == 5 {
            guard stars.isEmpty && door == nil && deity == nil &&
                  heavenStems.isEmpty && ordered81Patterns.isEmpty else {
                throw WenguaGraphError.invalid("No invented ordinary center stars/door/deity")
            }
        } else {
            guard !stars.isEmpty && door != nil && deity != nil &&
                  !heavenStems.isEmpty && earthStem != nil &&
                  !ordered81Patterns.isEmpty else {
                throw WenguaGraphError.invalid(
                    "Each selected palace MUST inspect all resident categories")
            }
        }
    }
}

struct WenguaGraphRelation {
    let actor: WenguaGraphIdentity
    let target: WenguaGraphIdentity
    let actorEnergyFactID: String
    let targetEnergyFactID: String
    let actorStrength: String?
    let targetStrength: String?
    let direction: String
    let spatialRelationship: String
    // Domain-owned rule engine, never this factual graph, decides effect.
    let scoredPoints: Int? = nil
}

struct WenguaGraphResidentEvidence {
    let roleKey: String
    let selectedSymbol: WenguaGraphIdentity
    let selectedStrength: String?
    let resident: WenguaGraphResident
    let signedPalaceGradeOnce: Int
    let isSelectedSymbolItself: Bool
    let independentCohostCandidate: Bool
    // Source fact is not a new health / other-domain conditional score.
    let scoredPoints: Int? = nil
}

struct WenguaGraphCohostCondition {
    let conditionID: String
    let domainID: String
    let hostRoles: Set<String>
    let helperKind: String
    let helperSymbolID: String
}

struct WenguaGraphCohostFact {
    let conditionID: String
    let selectedHost: WenguaGraphIdentity
    let independentHelper: WenguaGraphIdentity
    let hostStrength: String?
    let helperStrength: String?
    let palaceID: Int
    // Independent host and helper do NOT authorize a generic numerical bonus.
    let scoredPoints: Int? = nil
}

struct WenguaReadOnlySignifierGraphV80 {
    let domainID: String
    let byRole: [String: WenguaGraphUseGod]
    let uniqueSignifiers: [WenguaGraphIdentity: WenguaGraphUseGod]
    let palaces: [Int: WenguaGraphPalace]

    init(domainID: String, roles: [WenguaGraphUseGod],
         palaces: [Int: WenguaGraphPalace]) throws {
        guard !domainID.isEmpty, !roles.isEmpty else {
            throw WenguaGraphError.invalid("Explicit domain and selected use-gods required")
        }
        let tiers: Set<String> = ["极小","小","中等","大","极大"]
        let validKinds: Set<String> = ["star","door","deity","stem","palace","other"]
        let allowedRestrictions: Set<String> = [
            "真空","假空","入墓","击刑","被宫克","门迫"]
        var roleIndex: [String: WenguaGraphUseGod] = [:]
        var unique: [WenguaGraphIdentity: WenguaGraphUseGod] = [:]
        for entry in roles {
            guard !entry.roleKey.isEmpty, !entry.symbolID.isEmpty,
                  !entry.energyFactID.isEmpty, validKinds.contains(entry.kind),
                  (1...9).contains(entry.palaceID),
                  entry.strength == nil || tiers.contains(entry.strength!),
                  entry.restrictions.isSubset(of: allowedRestrictions),
                  roleIndex[entry.roleKey] == nil else {
                throw WenguaGraphError.invalid("Invalid or duplicate use-god binding")
            }
            if let first = unique[entry.identity] {
                guard first.energyFactID == entry.energyFactID &&
                      first.strength == entry.strength &&
                      first.restrictions == entry.restrictions else {
                    throw WenguaGraphError.invalid(
                        "Aliases of one real symbol cannot invent different strengths")
                }
            }
            roleIndex[entry.roleKey] = entry
            unique[entry.identity] = entry
        }
        let selected = Set(roles.map { $0.palaceID })
        guard selected == Set(palaces.keys) else {
            throw WenguaGraphError.invalid(
                "Every real selected palace must include the FULL environment")
        }
        for (key, palace) in palaces {
            guard key == palace.palaceID else {
                throw WenguaGraphError.invalid("Real palace coordinate mismatch")
            }
            try palace.validate()
        }
        self.domainID = domainID
        self.byRole = roleIndex
        self.uniqueSignifiers = unique
        self.palaces = palaces
    }

    var signedBaseTotalOnce: Int {
        palaces.values.reduce(0) { $0 + $1.auspiciousGrade }
    }

    static let elements: [Int: String] =
        [1:"水",2:"土",3:"木",4:"木",5:"土",6:"金",7:"金",8:"土",9:"火"]
    static let generates: [String: String] =
        ["木":"火","火":"土","土":"金","金":"水","水":"木"]
    static let controls: [String: String] =
        ["木":"土","土":"水","水":"火","火":"金","金":"木"]
    static let coordinates: [Int: (Int,Int)] = [
        4:(0,0),9:(0,1),2:(0,2),
        3:(1,0),5:(1,1),7:(1,2),
        8:(2,0),1:(2,1),6:(2,2),
    ]

    static func direction(_ a: WenguaGraphIdentity,
                          _ b: WenguaGraphIdentity) -> String {
        if a == b { return "同一符号" }
        if a.palaceID == b.palaceID { return "同宫" }
        let x = elements[a.palaceID]!, y = elements[b.palaceID]!
        if x == y { return "比和" }
        if controls[x] == y { return "克" }
        if controls[y] == x { return "被克" }
        if generates[x] == y { return "生" }
        return "被生"
    }

    static func spatial(_ a: Int, _ b: Int) -> String {
        if a == b { return "同宫" }
        let p = coordinates[a]!, q = coordinates[b]!
        let dr = abs(p.0 - q.0), dc = abs(p.1 - q.1)
        if dr + dc == 1 { return "九宫正邻位" }
        if dr == 1 && dc == 1 { return "九宫斜邻位" }
        return "九宫非邻位"
    }

    func edges() -> [WenguaGraphRelation] {
        let list = uniqueSignifiers.values.sorted {
            String(describing: $0.identity) < String(describing: $1.identity)
        }
        var out: [WenguaGraphRelation] = []
        for i in list.indices {
            for j in list.indices where i != j {
                let a = list[i], b = list[j]
                out.append(WenguaGraphRelation(
                    actor:a.identity,target:b.identity,
                    actorEnergyFactID:a.energyFactID,
                    targetEnergyFactID:b.energyFactID,
                    actorStrength:a.strength,targetStrength:b.strength,
                    direction:Self.direction(a.identity,b.identity),
                    spatialRelationship:Self.spatial(a.palaceID,b.palaceID)))
            }
        }
        return out
    }

    func allRoleResidentFacts() -> [WenguaGraphResidentEvidence] {
        var result: [WenguaGraphResidentEvidence] = []
        for role in byRole.keys.sorted() {
            let person = byRole[role]!
            let palace = palaces[person.palaceID]!
            for resident in palace.residents {
                let nominalKind = (resident.category=="heaven_stem" ||
                                   resident.category=="earth_stem")
                                  ? "stem" : resident.category
                let selfRef = nominalKind==person.kind &&
                              resident.symbolID==person.symbolID
                result.append(WenguaGraphResidentEvidence(
                    roleKey:role,selectedSymbol:person.identity,
                    selectedStrength:person.strength,resident:resident,
                    signedPalaceGradeOnce:palace.auspiciousGrade,
                    isSelectedSymbolItself:selfRef,
                    independentCohostCandidate:!selfRef &&
                        resident.category != "ordered_81_pattern"))
            }
        }
        return result
    }

    func independentCohosts(_ rule: WenguaGraphCohostCondition) throws
        -> [WenguaGraphCohostFact] {
        guard rule.domainID == domainID else {
            throw WenguaGraphError.invalid(
                "Illness domain bonuses cannot be inherited by a new domain")
        }
        var result:[WenguaGraphCohostFact] = []
        var seen:Set<String> = []
        for roleKey in rule.hostRoles.sorted() {
            guard let host=byRole[roleKey] else { continue }
            for helper in uniqueSignifiers.values {
                guard helper.kind == rule.helperKind,
                      helper.symbolID == rule.helperSymbolID,
                      helper.palaceID == host.palaceID,
                      helper.identity != host.identity else { continue }
                let id = rule.conditionID + ":" +
                    host.kind + ":" + host.symbolID + ":" +
                    String(host.palaceID) + ":" + helper.kind +
                    ":" + helper.symbolID
                if seen.insert(id).inserted {
                    result.append(WenguaGraphCohostFact(
                        conditionID:rule.conditionID,selectedHost:host.identity,
                        independentHelper:helper.identity,hostStrength:host.strength,
                        helperStrength:helper.strength,palaceID:host.palaceID))
                }
            }
        }
        return result
    }
}
