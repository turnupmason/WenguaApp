import Foundation
@main struct NativeActorProfileCheck {
  static func main() throws {
    guard CommandLine.arguments.count==2 else {throw WenguaCastError.invalidChart}
    let idx=try WenguaNativeActorSource.fromData(
      Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
    guard idx.profiles.count==20 else {throw WenguaCastError.invalidChart}
    let format=ISO8601DateFormatter()
    format.formatOptions=[.withInternetDateTime]
    guard let date=format.date(from:"2025-07-18T03:00:00-04:00") else {
      throw WenguaCastError.invalidChart
    }
    let chart=try WenguaNativeCore.compute(at:date,timezone:"America/New_York")
    func make(_ label:String,sex:String?=nil,context:String="direct_proxy")
      throws -> WenguaNativeActor {
      try WenguaNativeActorSource.bind(chart:chart,
        inquiry:WenguaNativeInquiry(relationship:label,context:context,
          patientSex:sex,birthOrder:nil,patientBirthGanzhi:nil),index:idx)
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
    let friend=try make("朋友")
    let event=try make("朋友",context:"event_news")
    let nephew=try make("侄子")
    guard friend.mainStem=="癸",!friend.eligibleForFirmTraditionalJudgment,
      event.mainStem=="戊",nephew.mainStem=="甲",
      nephew.mainPalace != 5 else {throw WenguaCastError.invalidChart}
    do { _=try make("配偶");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    do { _=try make("本人",context:"direct_proxy");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    do { _=try make("侄子",context:"event_news");throw WenguaCastError.invalidChart }
    catch WenguaNativeReadingError.unsupportedRelationship {}
    print("WENGUA_NATIVE_ACTOR_SOURCE_OK 20 indexed, source-gated")
  }
}
