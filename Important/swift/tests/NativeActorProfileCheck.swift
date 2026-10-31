import Foundation
@main struct NativeActorProfileCheck {
  static func main() throws {
    guard CommandLine.arguments.count==2 else {throw WenguaCastError.invalidChart}
    let idx=try WenguaNativeActorSource.fromData(
      Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
    guard idx.profiles.count==24 else {throw WenguaCastError.invalidChart}
    let format=ISO8601DateFormatter()
    format.formatOptions=[.withInternetDateTime]
    guard let date=format.date(from:"2025-07-18T03:00:00-04:00") else {
      throw WenguaCastError.invalidChart
    }
    let chart=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
    func make(_ label:String,sex:String?=nil,context:String="direct_proxy",relativeAge:String?=nil)
      throws -> WenguaNativeActor {
      try WenguaNativeActorSource.bind(chart:chart,
        inquiry:WenguaNativeInquiry(relationship:label,context:context,
          patientSex:sex,birthOrder:nil,patientBirthGanzhi:nil,
          relativeAge:relativeAge),index:idx)
    }
    let myself=try make("本人",context:"direct_self")
    guard myself.mainStem=="戊",myself.eligibleForFirmTraditionalJudgment else {
      throw WenguaCastError.invalidChart
    }
    let father=try make("父亲")
    let mother=try make("母亲")
    guard father.mainStem=="乙",father.extraPalaces.contains(6),
      mother.extraPalaces.contains(2),!mother.eligibleForFirmTraditionalJudgment
      else {throw WenguaCastError.invalidChart}
    let wife=try make("妻子")
    let husband=try make("丈夫")
    guard wife.mainStem=="乙",husband.mainStem=="庚",
      wife.harmonyStem=="癸",husband.harmonyStem=="癸"
      else {throw WenguaCastError.invalidChart}
    for (person,sex,kind) in [
      ("哥哥","male","casting_month_stem"),("姐姐","female","casting_month_stem"),
      ("弟弟","male","casting_month_stem"),("妹妹","female","casting_month_stem")] {
      let a=try make(person)
      guard a.kind==kind,a.sourceGanzhi==chart.pillars.month,
            a.mainPalace != 5,a.genderPalace == nil,a.extraPalaces.count==1
      else {throw WenguaCastError.invalidChart}
      do { _=try make(person,sex:sex=="male" ? "female":"male")
           throw WenguaCastError.invalidChart }
      catch WenguaNativeReadingError.unsupportedRelationship {}
    }
    func conditioned(_ who:String,_ rank:String?,_ youth:String?,_ palace:Int)throws {
      let req=WenguaNativeInquiry(relationship:who,context:"direct_proxy",
        patientSex:nil,birthOrder:rank,patientBirthGanzhi:nil,patientAgeBand:youth)
      let a=try WenguaNativeActorSource.bind(chart:chart,inquiry:req,index:idx)
      guard a.mainStem==String(chart.pillars.month.prefix(1)),
            a.siblingAuxiliaryPalace==palace,a.extraPalaces.contains(palace),
            a.genderPalace == nil else {throw WenguaCastError.invalidChart}
    }
    try conditioned("姐姐","eldest",nil,4)
    try conditioned("弟弟",nil,"young",8)
    try conditioned("哥哥","eldest",nil,3)
    try conditioned("妹妹",nil,"young",7)
    let friend=try make("朋友",sex:"female",relativeAge:"older")
    let event=try make("朋友",sex:"male",context:"event_news",relativeAge:"younger")
    guard friend.siblingAuxiliaryPalace==4,
          event.siblingAuxiliaryPalace==8,friend.extraPalaces.contains(4),
          event.extraPalaces.contains(8) else {throw WenguaCastError.invalidChart}
    do { _=try make("朋友");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    do { _=try make("朋友",sex:"male");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    let nephew=try make("侄子")
    guard friend.mainStem=="癸",friend.eligibleForFirmTraditionalJudgment,
      event.mainStem=="戊",nephew.mainStem=="甲",
      nephew.mainPalace != 5 else {throw WenguaCastError.invalidChart}
    do { _=try make("配偶");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    do { _=try make("本人",context:"direct_proxy");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    do { _=try make("侄子",context:"event_news");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    print("WENGUA_NATIVE_ACTOR_SOURCE_OK 24 indexed, source-gated")
  }
}
