import Foundation

// Small, source-provenanced rule INDEX from the existing Python project.
// This is NOT book SQLite content and contains no original books. The app
// carries only rules actually needed for person/relationship binding.
struct WenguaActorSourceRef:Decodable {
    let kind:String
    let status:String
    let source:String
}
struct WenguaActorSourceProfile:Decodable {
    let id:String
    let label:String
    let palaces:[Int]
    let references:[WenguaActorSourceRef]
    let note:String
    let sibling_auxiliary:WenguaSiblingAuxiliary? 
}
struct WenguaSiblingAuxiliary:Decodable {
    let palace:Int
    let role_sex:String
    let kind:String
    let source:String
    let requires:String
    let scoring_policy:String
}
struct WenguaActorEventOverride:Decodable {
    let eligible:[String]
    let role_kind:String
    let source:String
}
struct WenguaActorSourceIndex:Decodable {
    let profiles:[WenguaActorSourceProfile]
    let legacy_composite_profiles:[WenguaActorSourceProfile]?
    let event_news_override:WenguaActorEventOverride
}
struct WenguaNativeInquiry {
    let relationship:String
    let context:String // direct_self, direct_proxy, event_news
    let patientSex:String? // male, female
    let birthOrder:String? // eldest, middle, youngest
    let patientBirthGanzhi:String? // optional complete Ganzhi, NOT Gregorian year only
    let patientBirthStem:String? // source-supplied lone natal heavenly stem
    let patientAgeBand:String? // explicit real youth; never guessed from younger
    let relativeAge:String? // friend only: older/younger than asker
    init(relationship:String,context:String,patientSex:String?,birthOrder:String?,
         patientBirthGanzhi:String?,patientBirthStem:String?=nil,
         patientAgeBand:String?=nil,relativeAge:String?=nil) {
        self.relationship=relationship
        self.context=context
        self.patientSex=patientSex
        self.birthOrder=birthOrder
        self.patientBirthGanzhi=patientBirthGanzhi
        self.patientBirthStem=patientBirthStem
        self.patientAgeBand=patientAgeBand
        self.relativeAge=relativeAge
    }
    static func standard(_ relation:String)->WenguaNativeInquiry {
        WenguaNativeInquiry(relationship:relation,
            context:relation=="本人" ? "direct_self":"direct_proxy",
            patientSex:nil,birthOrder:nil,patientBirthGanzhi:nil)
    }
}
struct WenguaNativeActor {
    let profileID:String
    let label:String
    let mainStem:String // selected symbolic identity, e.g. 甲
    let sourceGanzhi:String? // original role-specific 年/月/日/时 complete pillar
    let mainPalace:Int
    let kind:String
    let confidence:String
    let source:String
    let extraPalaces:[Int]
    let harmonyStem:String?
    let harmonyPalace:Int?
    let genderPalace:Int?
    let natalStem:String?
    let natalSourceGanzhi:String?
    let natalPalace:Int?
    let note:String
    let siblingAuxiliaryPalace:Int?
    let siblingAuxiliarySource:String?
    var eligibleForFirmTraditionalJudgment:Bool {
        ["source_case_specific",
         "user_explicit_direction_verified_by_actual_chart"].contains(confidence)
    }
}

enum WenguaNativeActorSource {
    static func fromBundle(_ bundle:Bundle = .main)throws->WenguaActorSourceIndex {
        guard let url=bundle.url(forResource:"actor_profiles",withExtension:"json") else {
            throw WenguaNativeReadingError.missingPhrases
        }
        return try fromData(Data(contentsOf:url))
    }
    static func fromData(_ data:Data)throws->WenguaActorSourceIndex {
        let decoded=try JSONDecoder().decode(WenguaActorSourceIndex.self,from:data)
        let ids=decoded.profiles.map(\.id)
        let labels=decoded.profiles.map(\.label)
        guard ids.count==24,Set(ids).count==24,Set(labels).count==24,
              decoded.profiles.allSatisfy({ !$0.references.isEmpty }) else {
            throw WenguaNativeReadingError.invalidPhrase
        }
        return decoded
    }
    static let sixJia:[String:String] = [
        "甲子":"戊","甲戌":"己","甲申":"庚",
        "甲午":"辛","甲辰":"壬","甲寅":"癸"
    ]
    static func jiaCarrier(_ sourceGanzhi:String)->String? {
        sixJia[sourceGanzhi]
    }
    static func actualStem(_ stem:String, chart:WenguaNativeChart,
                           sourceGanzhi:String?=nil)->Int? {
        let carrier:String
        if stem=="甲" {
            guard let sourceGanzhi,
                  validatedGanzhi(sourceGanzhi),
                  let mapped=jiaCarrier(sourceGanzhi) else {return nil}
            carrier=mapped
        } else {
            carrier=stem
        }
        let found=chart.palaces.filter{
            $0.id != 5 && $0.heavenStars.contains(where:{$0.carriedStem==carrier})
        }
        return found.count==1 ? found[0].id : nil
    }
    static func validatedGanzhi(_ value:String)->Bool {
        let stems=WenguaNativeCore.stems
        let branches=WenguaNativeCore.branches
        guard value.count==2 else {return false}
        return (0..<60).contains{ i in
            stems[i%10]+branches[i%12]==value
        }
    }
    static func bind(chart:WenguaNativeChart,
                     inquiry:WenguaNativeInquiry,
                     index:WenguaActorSourceIndex)throws->WenguaNativeActor {
        guard let profile=(index.profiles+((index.legacy_composite_profiles) ?? []))
                    .first(where:{$0.label==inquiry.relationship}),
              let first=profile.references.first else {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        let ctx=inquiry.context
        guard ["direct_self","direct_proxy","event_news"].contains(ctx),
              (profile.id=="self" ? ctx=="direct_self" : ctx != "direct_self") else {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        if ctx=="event_news" &&
           !index.event_news_override.eligible.contains(profile.id) {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        let sex=inquiry.patientSex
        guard sex==nil || sex=="male" || sex=="female" else {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        let knownMale=["father","grandfather","older_brother","younger_brother",
                       "son","husband","animal_rooster"]
        let knownFemale=["mother","grandmother","older_sister","younger_sister",
                         "daughter","wife","animal_hen"]
        if knownMale.contains(profile.id) && sex != nil && sex != "male" ||
           knownFemale.contains(profile.id) && sex != nil && sex != "female" {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        // Friends always use the true casting month stem, independent
        // of optional demographic inputs. No sibling or elder palace.
        if profile.id != "friend" && inquiry.relativeAge != nil {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        let kind=ctx=="event_news" ? index.event_news_override.role_kind : first.kind
        let confidence=profile.id=="friend" ?
            "user_explicit_direction_verified_by_actual_chart" :
            ctx=="event_news" ? "source_case_specific_event_time" : first.status
        let source=ctx=="event_news" ?
            index.event_news_override.source : first.source
        let candidateStem:String
        var roleSourceGanzhi:String?=nil
        var harmony:String?=nil
        if kind=="spouse_gender_harmony" {
            let decidedSex = profile.id=="wife" ? "female" :
                             profile.id=="husband" ? "male" : sex
            guard let decidedSex,
                sex == nil || sex==decidedSex else {
                throw WenguaNativeReadingError.unsupportedRelationship
            }
            candidateStem=decidedSex=="female" ? "乙":"庚"
            let day=String(chart.pillars.day.prefix(1))
            harmony=["甲":"己","己":"甲","乙":"庚","庚":"乙",
                     "丙":"辛","辛":"丙","丁":"壬","壬":"丁",
                     "戊":"癸","癸":"戊"][day]
        } else {
            let pillar:String
            switch kind {
            case "day_stem","casting_day_stem":pillar=chart.pillars.day
            case "casting_year_stem":pillar=chart.pillars.year
            case "casting_month_stem":pillar=chart.pillars.month
            case "casting_hour_stem":pillar=chart.pillars.hour
            default:throw WenguaNativeReadingError.unsupportedRelationship
            }
            candidateStem=String(pillar.prefix(1))
            roleSourceGanzhi=pillar
        }
        // Every independent Jia role uses its OWN complete source pillar,
        // never the hour-xun for a casting year/month/day.
        guard let patient=actualStem(candidateStem,chart:chart,
                                    sourceGanzhi:roleSourceGanzhi) else {
            throw WenguaNativeReadingError.missingRole
        }
        var extra=profile.palaces
        if profile.id=="parent" {
            guard let sex else {throw WenguaNativeReadingError.unsupportedRelationship}
            extra.append(sex=="male" ? 6:2)
        }
        if profile.id=="older_relative" { // no forced aunt/mother mapping
            // Fixed palace only when original profile has an exact candidate.
        }
        if let rank=inquiry.birthOrder,let sex,
           ["child","son","daughter","nephew"].contains(profile.id) {
            let table=[
              "male:eldest":3,"male:middle":1,"male:youngest":8,
              "female:eldest":4,"female:middle":9,"female:youngest":7]
            if let p=table[sex+":"+rank] {extra.append(p)}
        }
        // V9: 哥/姐/弟/妹 relation implies relative age and biological sex.
        // Source examples and analogy statuses remain explicitly in JSON.
        if let sibling=profile.sibling_auxiliary {
            extra.append(sibling.palace)
        }
        // Only a true brother/sister relationship selects排行辅助.
        // A friend has no trigram auxiliary even if age/sex were supplied.
        let siblingSelected=profile.id=="friend" ? nil :
            profile.sibling_auxiliary?.palace
        let genuineHarmony=harmony.flatMap{actualStem($0,chart:chart)}
        if let genuineHarmony {extra.append(genuineHarmony)}
        let natal=inquiry.patientBirthGanzhi
        if let natal, !validatedGanzhi(natal) {
            throw WenguaNativeReadingError.unsupportedRelationship
        }
        let natalStem=natal.map{String($0.prefix(1))} ?? inquiry.patientBirthStem
        let natalPalace=natalStem.flatMap{actualStem($0,chart:chart,
                                                   sourceGanzhi:natal)}
        // Only older-generation roles receive Qian/Kun; this is NOT a
        // generic male/female auxiliary for friends, spouses or children.
        let elder=["father","mother","parent","older_relative",
                   "grandfather","grandmother"].contains(profile.id)
        let elderSex=["father","grandfather"].contains(profile.id) ? "male" :
                     ["mother","grandmother"].contains(profile.id) ? "female" : sex
        let gender:Int?=elder ? (elderSex=="male" ? 6 :
                                elderSex=="female" ? 2 : nil) : nil
        return WenguaNativeActor(profileID:profile.id,label:profile.label,
            mainStem:candidateStem,sourceGanzhi:roleSourceGanzhi,
            mainPalace:patient,kind:kind,
            confidence:confidence,source:source,
            extraPalaces:Array(Set(extra)).sorted(),
            harmonyStem:harmony,harmonyPalace:genuineHarmony,
            genderPalace:gender,natalStem:natalStem,
            natalSourceGanzhi:natal,natalPalace:natalPalace,note:profile.note,
            siblingAuxiliaryPalace:siblingSelected,
            siblingAuxiliarySource:siblingSelected == nil ? nil :
                profile.sibling_auxiliary?.source)
    }
}
