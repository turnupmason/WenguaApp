import Foundation

// Exact 5 x 5 traditional Tianrui star month versus star-palace symbolic
// cases from current Python health_tianrui_25_matrix.py. These are 25
// USER-PROPOSED hypotheses, NOT book-proven medical severity predictions.
// One actual case only; not 25 separate votes and not added to ±5 score.
struct WenguaTianrui25Case {
    let category:String
    let starMonth:String
    let palaceMonth:String
    let title:String
    let effectiveness:String
    let why:String
    let eligibleDirection:String
}
enum WenguaVNextTianrui25 {
    static let stages=["旺","相","休","囚","废"]
    static let keys=["宫克星","星生宫","星克宫","宫生星","宫星比和"]
    static let titles=[
        "宫克星":["强弩受挫","萌芽被扼","兵败如山倒","关押绞杀","斩草除根"],
        "星生宫":["疯狂消耗","排毒宣泄","残存流逝","油尽灯枯","灰飞烟灭"],
        "星克宫":["病魔猖獗","病情扩散","贼心不死","自不量力／反侮","蚍蜉撼树"],
        "宫生星":["养虎为患","迅速恶化","养精蓄锐","顽固包庇","百足之虫"],
        "宫星比和":["全面爆发","结党营私","负隅顽抗","潜伏菌群","无害残留"]
    ]
    private static let generates=WenguaNativeReadingRouter.generating
    private static let controls=WenguaNativeReadingRouter.controlling
    private static let elements=WenguaNativeReadingRouter.palaceElements
    private static let monthElements=[
        "寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土",
        "申":"金","酉":"金","戌":"土","亥":"水","子":"水","丑":"土"]
    static func caseFor(chart:WenguaNativeChart,
                        audit:WenguaVNextAudit)throws->WenguaTianrui25Case {
        guard let id=audit.roles["illness"],
              let p=chart.palaces.first(where:{$0.id==id}),
              let row=audit.palaces[id],
              let el=elements[id],
              let monthElement=monthElements[
                  String(chart.pillars.month.suffix(1))],
              let starMonth=row.energyEvidence.first(where:{
                  $0.source=="star" && $0.symbol=="天芮星"
              })?.monthStage,
              let idx=stages.firstIndex(of:starMonth) else {
            throw WenguaVNextReadingGate.unresolvedRole
        }
        let month:String
        if el==monthElement {month="旺"}
        else if generates[monthElement]==el {month="相"}
        else if generates[el]==monthElement {month="休"}
        else if controls[el]==monthElement {month="囚"}
        else if controls[monthElement]==el {month="死"}
        else {throw WenguaCastError.invalidChart}
        let category:String
        if controls[el]=="土" {category="宫克星"}
        else if generates["土"]==el {category="星生宫"}
        else if controls["土"]==el {category="星克宫"}
        else if generates[el]=="土" {category="宫生星"}
        else if el=="土" {category="宫星比和"}
        else {throw WenguaCastError.invalidChart}
        guard let title=titles[category]?[idx] else {
            throw WenguaCastError.invalidChart
        }
        let danger = !p.voidBranches.isEmpty || !p.tombs.isEmpty ||
            p.heavenStars.contains(where:{
                ["戊":3,"己":2,"庚":8,"辛":9,"壬":4,"癸":4][$0.carriedStem]==id
            }) || row.energyEvidence.contains(where:{
                $0.source=="door" && $0.palaceRelation=="宫迫"
            })
        let strong=["旺","相"]
        let weakStar=["囚","废"]
        let weakPalace=["囚","死"]
        var status="conditional"
        var reason=""
        if danger {
            status="obstructed"
            reason="宫内空墓刑迫等限制尚待合断，不能仅由月令与星宫关系定有效"
        } else if category=="宫克星" {
            if strong.contains(month) && ["休","囚","废"].contains(starMonth) {
                status="supported";reason="宫较有力、病星较弱，制病方向有条件发挥"
            } else if weakPalace.contains(month) && strong.contains(starMonth) {
                status="limited";reason="弱宫难克旺星，不把名义宫克当作已经制病"
            } else {reason="宫克星虽已核，双方强弱不足以单独定制病成败"}
        } else if category=="星生宫" {
            if strong.contains(starMonth) && strong.contains(month) {
                status="supported";reason="星有余气、宫可承受，泄气象有条件显现"
            } else if weakStar.contains(starMonth) && strong.contains(month) {
                status="limited";reason="星本弱、生宫有心无力，仍只记录轻微泄气候选"
            } else {reason="星生宫已核，但泄气的实际作用仍须合宫气"}
        } else if category=="星克宫" {
            if strong.contains(starMonth) && weakPalace.contains(month) {
                status="supported";reason="旺星克弱宫，传统攻宫象较易发生"
            } else if weakStar.contains(starMonth) && strong.contains(month) {
                status="limited";reason="弱病难克旺宫，仅是反制候选而非病人已无恙"
            } else {reason="星克宫方向已核，宫的抵抗力仍须合断"}
        } else if category=="宫生星" {
            if strong.contains(month) {
                status="supported";reason="宫旺相有生扶能力，病星受扶候选"
            } else if weakPalace.contains(month) && strong.contains(starMonth) {
                status="limited";reason="宫弱难生旺星，不把名义生扶算成有效滋养"
            } else {reason="宫生星虽已核，弱宫的生扶效力尚不确定"}
        } else {
            if strong.contains(starMonth) && strong.contains(month) {
                status="supported";reason="星宫同气且均有月令支持"
            } else if weakStar.contains(starMonth) && weakPalace.contains(month) {
                status="limited";reason="星宫同气但双方均弱，不自动推出吉凶"
            } else {reason="同五行不等于同力量，须继续审查空墓门神"}
        }
        let proposed:String
        if category=="宫克星" || category=="星生宫" {proposed="favorable"}
        else if category=="宫生星" {proposed="adverse"}
        else if idx>=3 {proposed="pending"}
        else {proposed="adverse"}
        let eligible = status=="supported" && proposed != "pending"
            ? proposed : "pending"
        return WenguaTianrui25Case(category:category,
          starMonth:starMonth,palaceMonth:month,title:title,
          effectiveness:status,why:reason,eligibleDirection:eligible)
    }
}
