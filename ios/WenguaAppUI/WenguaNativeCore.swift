import Foundation

// Wengua Native Cast v0.1: full deterministic, offline, Foundation-only port.
// Reference: src/wengua/astro_calendar.py (Meeus/NOAA approximation) and
//            src/wengua/casting_shenqi.py (original Shenqi zhuanpan).
// Strict UTC terms within 2025-2028; outside coverage conservatively reject
// 0.05-degree uncertainty and unsupported 23h day rollover,
// outside 1850...2150. Never "best guess".
// No patient prognosis, model V4 scores, cloud calls or fabricated symbols.

enum WenguaCastError: Error, LocalizedError {
    case invalidTimezone, outOfRange, lateZi, termBoundary, noBureau, invalidChart
    var errorDescription: String? {
        switch self {
        case .invalidTimezone: return "需要有效的 IANA 时区"
        case .outOfRange: return "超出已测试的 1850–2150 年范围"
        case .lateZi: return "23点子初换日流派未校定，拒绝直接起盘"
        case .termBoundary: return "此年份距节气交界过近但缺少核准交节时间，拒绝猜盘"
        case .noBureau: return "节气／符头／遁局无法按原书规则确定"
        case .invalidChart: return "实际九宫结构内部计算不完整"
        }
    }
}

struct WenguaNativePillars: Codable, Equatable {
    let year: String
    let month: String
    let day: String
    let hour: String
}

struct WenguaNativeBureau: Codable, Equatable {
    let dun: String
    let ju: Int
    let yuan: String
    let futou: String
    let solarTerm: String
}

struct WenguaNativeStage: Codable, Equatable {
    let branch: String
    let stage: String
}

struct WenguaNativeStar: Codable, Equatable {
    let star: String
    let carriedStem: String
    let stages: [WenguaNativeStage]
}

struct WenguaNativeTomb: Codable, Equatable {
    let plane: String
    let stem: String
    let branch: String
    let star: String?
}

struct WenguaNativePalace: Codable, Equatable, Identifiable {
    let id: Int
    let gua: String
    let earthStem: String
    let earthStages: [WenguaNativeStage]
    let heavenStars: [WenguaNativeStar]
    let door: String?
    let deity: String?
    let branches: [String]
    let voidBranches: [String]
    let horseBranch: String?
    let tombs: [WenguaNativeTomb]
}

struct WenguaNativeChart: Codable, Equatable {
    let engineVersion: String
    let iso: String
    let timezone: String
    let pillars: WenguaNativePillars
    let solarTerm: String
    let sunLongitude: Double
    let bureau: WenguaNativeBureau
    let xunShou: String
    let hiddenStem: String
    let valueStar: String
    let valueStarPalace: Int
    let valueDoor: String
    let valueDoorPalace: Int
    let voidBranches: [String]
    let hourHorse: String
    let hourHorsePalace: Int
    let palaces: [WenguaNativePalace]
    // Not a qualified report. Only real machine-generated plate facts.
}

enum WenguaNativeCore {
    static let stems = Array("甲乙丙丁戊己庚辛壬癸").map { String($0) }
    static let branches = Array("子丑寅卯辰巳午未申酉戌亥").map { String($0) }
    static let ring = [1,8,3,4,9,2,7,6]
    static let earthOrder = Array("戊己庚辛壬癸丁丙乙").map { String($0) }
    static let stars = [1:"天蓬星",2:"天芮星",3:"天冲星",4:"天辅星",
                        5:"天禽星",6:"天心星",7:"天柱星",8:"天任星",9:"天英星"]
    static let doors = [1:"休门",8:"生门",3:"伤门",4:"杜门",
                        9:"景门",2:"死门",7:"惊门",6:"开门"]
    static let guas = [1:"坎",2:"坤",3:"震",4:"巽",5:"中",6:"乾",7:"兑",8:"艮",9:"离"]
    static let palaceBranches: [Int:[String]] = [
        1:["子"],2:["未","申"],3:["卯"],4:["辰","巳"],5:[],
        6:["戌","亥"],7:["酉"],8:["丑","寅"],9:["午"]]
    static let deities = ["值符","螣蛇","太阴","六合","白虎","玄武","九地","九天"]
    static let sixJia = ["甲子":"戊","甲戌":"己","甲申":"庚",
                         "甲午":"辛","甲辰":"壬","甲寅":"癸"]
    static let dayStart = ["甲":"甲","己":"甲","乙":"丙","庚":"丙",
                           "丙":"戊","辛":"戊","丁":"庚","壬":"庚",
                           "戊":"壬","癸":"壬"]
    static let yearMonthStart = ["甲":"丙","己":"丙","乙":"戊","庚":"戊",
                                 "丙":"庚","辛":"庚","丁":"壬","壬":"壬",
                                 "戊":"甲","癸":"甲"]
    static let solarTerms = ["冬至","小寒","大寒","立春","雨水","惊蛰",
                             "春分","清明","谷雨","立夏","小满","芒种",
                             "夏至","小暑","大暑","立秋","处暑","白露",
                             "秋分","寒露","霜降","立冬","小雪","大雪"]
    static let yangTerms: [String:[Int]] = [
        "冬至":[1,7,4],"惊蛰":[1,7,4],"小寒":[2,8,5],
        "大寒":[3,9,6],"春分":[3,9,6],"芒种":[6,3,9],
        "谷雨":[5,2,8],"小满":[5,2,8],"立春":[8,5,2],
        "立夏":[4,1,7],"清明":[4,1,7],"雨水":[9,6,3]]
    static let yinTerms: [String:[Int]] = [
        "夏至":[9,3,6],"白露":[9,3,6],"小暑":[8,2,5],
        "秋分":[7,1,4],"大暑":[7,1,4],"立秋":[2,5,8],
        "霜降":[5,8,2],"小雪":[5,8,2],"大雪":[4,7,1],
        "处暑":[1,4,7],"立冬":[6,9,3],"寒露":[6,9,3]]
    static let horseByHour = [
        "申":"寅","子":"寅","辰":"寅","寅":"申","午":"申","戌":"申",
        "巳":"亥","酉":"亥","丑":"亥","亥":"巳","卯":"巳","未":"巳"]
    // Generated from original source-checked 10*12 branch_to_stage (not V4 scoring).
    static let stages: [String: [String:String]] = [
        "甲": ["亥":"长生","子":"沐浴","丑":"冠带","寅":"临官","卯":"帝旺","辰":"衰","巳":"病","午":"死","未":"墓","申":"绝","酉":"胎","戌":"养"],
        "乙": ["午":"长生","巳":"沐浴","辰":"冠带","卯":"临官","寅":"帝旺","丑":"衰","子":"病","亥":"死","戌":"墓","酉":"绝","申":"胎","未":"养"],
        "丙": ["寅":"长生","卯":"沐浴","辰":"冠带","巳":"临官","午":"帝旺","未":"衰","申":"病","酉":"死","戌":"墓","亥":"绝","子":"胎","丑":"养"],
        "丁": ["酉":"长生","申":"沐浴","未":"冠带","午":"临官","巳":"帝旺","辰":"衰","卯":"病","寅":"死","丑":"墓","子":"绝","亥":"胎","戌":"养"],
        "戊": ["寅":"长生","卯":"沐浴","辰":"冠带","巳":"临官","午":"帝旺","未":"衰","申":"病","酉":"死","戌":"墓","亥":"绝","子":"胎","丑":"养"],
        "己": ["酉":"长生","申":"沐浴","未":"冠带","午":"临官","巳":"帝旺","辰":"衰","卯":"病","寅":"死","丑":"墓","子":"绝","亥":"胎","戌":"养"],
        "庚": ["巳":"长生","午":"沐浴","未":"冠带","申":"临官","酉":"帝旺","戌":"衰","亥":"病","子":"死","丑":"墓","寅":"绝","卯":"胎","辰":"养"],
        "辛": ["子":"长生","亥":"沐浴","戌":"冠带","酉":"临官","申":"帝旺","未":"衰","午":"病","巳":"死","辰":"墓","卯":"绝","寅":"胎","丑":"养"],
        "壬": ["申":"长生","酉":"沐浴","戌":"冠带","亥":"临官","子":"帝旺","丑":"衰","寅":"病","卯":"死","辰":"墓","巳":"绝","午":"胎","未":"养"],
        "癸": ["卯":"长生","寅":"沐浴","丑":"冠带","子":"临官","亥":"帝旺","戌":"衰","酉":"病","申":"死","未":"墓","午":"绝","巳":"胎","辰":"养"]
    ]
    static let branchOrderPalaces = [4,9,2,3,5,7,8,1,6]

    private static func mod(_ value: Int, _ modulus: Int) -> Int {
        ((value % modulus) + modulus) % modulus
    }
    private static func mod360(_ value: Double) -> Double {
        let x = value.truncatingRemainder(dividingBy: 360)
        return x < 0 ? x + 360 : x
    }
    private static func ganzhiCycle() -> [String] {
        (0..<60).map { stems[$0 % 10] + branches[$0 % 12] }
    }
    private static func dateParts(_ date: Date, _ zone: TimeZone) -> DateComponents {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = zone
        return calendar.dateComponents([.year,.month,.day,.hour,.minute,.second], from: date)
    }
    private static func localISO(_ date: Date, _ zone: TimeZone) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.timeZone = zone
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.string(from: date)
    }
    private static func daysFromAnchor(_ components: DateComponents) throws -> Int {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(secondsFromGMT: 0)!
        let anchor = DateComponents(year: 1995, month: 6, day: 11)
        let current = DateComponents(year: components.year, month: components.month, day: components.day)
        guard let a = cal.date(from: anchor), let b = cal.date(from: current),
              let offset = cal.dateComponents([.day], from: a, to: b).day else {
            throw WenguaCastError.invalidChart
        }
        return offset
    }
    private static func solarLongitude(_ date: Date) -> Double {
        // Identical constants/order to astro_calendar.py::_sun_longitude.
        let jd = 2440587.5 + date.timeIntervalSince1970 / 86400
        let t = (jd - 2451545) / 36525
        let l0 = mod360(280.46646 + t * (36000.76983 + 0.0003032 * t))
        let a = 357.52911 + t * (35999.05029 - 0.0001537 * t)
        func radians(_ x: Double) -> Double { x * Double.pi / 180 }
        let corr = (1.914602 - t * (0.004817 + 0.000014 * t)) * sin(radians(a))
            + (0.019993 - 0.000101 * t) * sin(radians(2*a))
            + 0.000289 * sin(radians(3*a))
        let omega = 125.04 - 1934.136 * t
        return mod360(l0 + corr - 0.00569 - 0.00478 * sin(radians(omega)))
    }


    // Swiss/Moshier crossing instants (UTC ms) 2025--2028. NEW term at instant.
    private static let strictFirstUTCms: Int64 = 1736044366945
    private static let strictDeltasBase36 = "l1ku06.l3448j.l6w468.lbcd2a.lhjhjp.lnpsly.luvhkk.m12w33.m7dkvx.mbtm33.mfj6it.mguqfq.mgwz4a.meoskx.mb4ea6.m5yxof.lzvgbg.lt8ua0.lmds59.lg2nh1.laauqk.l5x9w3.l2ovth.l1bgqb.l1dnlk.l3cxw5.l6o0gh.lbkjoy.lha6ot.lnyqp6.lukrpu.m1dqu2.m71fsl.mc650j.mf6tuj.mh78ln.mgm8rx.meyhfh.mawei4.m64m0q.lzqzyy.ltbpla.lmcd98.lg3yjc.laaig0.l5xiey.l2nuxq.l1b0nb.l1b886.l3byxq.l6knoq.lbj8ay.lh7vgw.lnx5c7.lum2uj.m1b3jj.m77xh3.mc0x0t.mfi91m.mgz8pl.mh104s.meorsm.mbb5zk.m5tutw.m030jq.lt0hjb.lmlkow.lft3lw.laiqeo.l5nk1k.l2wkud.l11pkl.l1kqq8.l32scm.l6ufiw.lb9wld.lhh3d8.lnod0b.luu49v.m14uns.m7dsyo.mbz4uo.mfjijo.mh1wa5.mgvymt.mevaqw.mb15wt.m62zs8.lzq03x.ltak30.lm7imi.lg3ms9.la56fg.l5yxbo.l2kdzn"
    private static let strictCrossings: [Int64] = {
        var items: [Int64] = [strictFirstUTCms]
        for token in strictDeltasBase36.split(separator: ".") {
            guard let diff=Int64(String(token),radix:36),
                  diff>0, let previous=items.last else {return []}
            items.append(previous+diff)
        }
        return items.count == 96 ? items : []
    }()
    private static func strictSolarIndex(_ date: Date) -> Int? {
        let times=strictCrossings
        guard let first=times.first, let last=times.last else {return nil}
        let ms=date.timeIntervalSince1970*1000
        guard ms>=Double(first) && ms<=Double(last) else {return nil}
        var lo=0,hi=times.count
        while lo<hi {
            let mid=(lo+hi)/2
            if Double(times[mid])<=ms {lo=mid+1} else {hi=mid}
        }
        return (1+lo-1)%24
    }

    static func compute(at instant: Date, timezone identifier: String) throws -> WenguaNativeChart {
        guard let zone = TimeZone(identifier: identifier) else { throw WenguaCastError.invalidTimezone }
        let local = dateParts(instant,zone)
        guard let year=local.year, let month=local.month, let hour=local.hour else {
            throw WenguaCastError.invalidChart
        }
        guard (1850...2150).contains(year) else { throw WenguaCastError.outOfRange }
        guard hour != 23 else { throw WenguaCastError.lateZi }
        let longitude = solarLongitude(instant)
        let angle = longitude.truncatingRemainder(dividingBy: 15)
        let preciseIndex = strictSolarIndex(instant)
        if preciseIndex == nil && min(angle,15-angle) < 0.05 {
            throw WenguaCastError.termBoundary
        }
        let solarIndex = preciseIndex ?? Int(floor(mod360(longitude-270)/15))
        let solarTerm = solarTerms[solarIndex]
        let cycle = ganzhiCycle()
        let offset = try daysFromAnchor(local)
        // day-cycle anchor 癸酉 1995-06-11 is book verified.
        guard let anchorIndex = cycle.firstIndex(of:"癸酉") else { throw WenguaCastError.invalidChart }
        let day = cycle[mod(anchorIndex+offset,60)]
        let priorSolarYear = (month <= 2 && [0,1,2].contains(solarIndex)) ? 1 : 0
        let solarYear = year - priorSolarYear
        let yearPillar = cycle[mod(solarYear-1984,60)]
        let monthIndex = ((solarIndex - 3 + 24) % 24) / 2
        let firstStem = String(yearPillar.prefix(1))
        guard let monthStart = yearMonthStart[firstStem],
              let monthBase=stems.firstIndex(of:monthStart) else {
            throw WenguaCastError.invalidChart
        }
        let monthPillar = stems[(monthBase+monthIndex)%10]+branches[(2+monthIndex)%12]
        let hourBranch=branches[((hour+1)/2)%12]
        let dayStem=String(day.prefix(1))
        guard let start=dayStart[dayStem], let startIndex=stems.firstIndex(of:start),
              let branchIndex=branches.firstIndex(of:hourBranch) else {
            throw WenguaCastError.invalidChart
        }
        let hourPillar=stems[(startIndex+branchIndex)%10]+hourBranch
        let pillars=WenguaNativePillars(year:yearPillar,month:monthPillar,day:day,hour:hourPillar)
        // Fu-tou is 甲/己 no more than 4 days before the current day.
        guard let dayIndex=cycle.firstIndex(of:day) else { throw WenguaCastError.invalidChart }
        let futou=(0..<5).map { cycle[mod(dayIndex-$0,60)] }
            .first { $0.hasPrefix("甲") || $0.hasPrefix("己") }
        guard let futou, let fuBranch=futou.last.map({String($0)}) else {
            throw WenguaCastError.noBureau
        }
        let yuan: String
        if "子午卯酉".contains(fuBranch) { yuan="upper" }
        else if "寅申巳亥".contains(fuBranch) { yuan="middle" }
        else { yuan="lower" }
        let vals = yangTerms[solarTerm] ?? yinTerms[solarTerm]
        guard let vals, vals.count == 3 else {throw WenguaCastError.noBureau}
        let dun = yangTerms[solarTerm] == nil ? "yin" : "yang"
        let ju = vals[yuan == "upper" ? 0 : (yuan == "middle" ? 1 : 2)]
        let bureau=WenguaNativeBureau(dun:dun,ju:ju,yuan:yuan,futou:futou,solarTerm:solarTerm)

        // Source identical ring+earth+heaven/door/deity rotations.
        let dir = dun=="yang" ? 1 : -1
        var earth=[Int:String]()
        for (i,stem) in earthOrder.enumerated() {
            earth[mod(ju-1+i*dir,9)+1]=stem
        }
        guard let hourCycleIndex=cycle.firstIndex(of:hourPillar) else {
            throw WenguaCastError.invalidChart
        }
        let steps=hourCycleIndex%10
        let head=cycle[hourCycleIndex-steps]
        guard let hidden=sixJia[head],
              let src=earth.first(where:{$0.value==hidden})?.key else {
            throw WenguaCastError.invalidChart
        }
        let host = src==5 ? 2 : src
        let valueStar=stars[src]!
        let valueDoor=doors[host]!
        let timeSymbol=hourPillar.hasPrefix("甲") ? hidden : String(hourPillar.prefix(1))
        guard let timeEarth=earth.first(where:{$0.value==timeSymbol})?.key else {
            throw WenguaCastError.invalidChart
        }
        let starTarget = timeEarth==5 ? 2 : timeEarth
        // 时家转盘值使随时辰过九宫：当数到中五，门盘寄坤二。
        // Count the actual nine-palace progression FIRST, then place
        // the door in its Kun-2 host; all eight outer doors rotate once.
        // Middle five retains no ordinary door, star or deity.
        let countedDoorTarget=mod(src-1+steps*dir,9)+1
        let doorTarget=countedDoorTarget==5 ? 2 : countedDoorTarget
        func rotate(from: Int,to:Int) throws -> [Int:Int] {
            guard let sourceIndex=ring.firstIndex(of:from),
                  let destIndex=ring.firstIndex(of:to) else {
                throw WenguaCastError.invalidChart
            }
            let shift=mod(destIndex-sourceIndex,8)
            var result=[Int:Int]()
            for (i,p) in ring.enumerated() {result[p]=ring[(i+shift)%8]}
            return result
        }
        let starMap=try rotate(from:host,to:starTarget)
        let doorMap=try rotate(from:host,to:doorTarget)
        var heaven=[Int:[(String,String)]]()
        for p in 1...9 {heaven[p]=[]}
        for p in ring {
            guard let target=starMap[p],let star=stars[p],let carried=earth[p] else {
                throw WenguaCastError.invalidChart
            }
            heaven[target,default:[]].append((star,carried))
        }
        guard let centralDest=starMap[2],let centre=earth[5] else {
            throw WenguaCastError.invalidChart
        }
        heaven[centralDest,default:[]].append((stars[5]!,centre))
        var doorAt=[Int:String]()
        for p in ring {
            guard let target=doorMap[p],let door=doors[p] else {
                throw WenguaCastError.invalidChart
            }
            doorAt[target]=door
        }
        guard let startDeityIndex=ring.firstIndex(of:starTarget) else {
            throw WenguaCastError.invalidChart
        }
        var deityAt=[Int:String]()
        for (i,deity) in deities.enumerated() {
            deityAt[ring[mod(startDeityIndex+i*dir,8)]]=deity
        }
        let xunBranches=(0..<10).map {String(cycle[(hourCycleIndex-steps+$0)%60].last!)}
        let empties=branches.filter { !xunBranches.contains($0) }
        guard empties.count==2, let horse=horseByHour[hourBranch],
              let horsePalace=palaceBranches.first(where:{$0.value.contains(horse)})?.key else {
            throw WenguaCastError.invalidChart
        }
        var palaceRows=[WenguaNativePalace]()
        for p in 1...9 {
            guard let earthStem=earth[p],let name=guas[p] else {throw WenguaCastError.invalidChart}
            let bs=palaceBranches[p]!
            let earthStages=bs.map {WenguaNativeStage(branch:$0,stage:stages[earthStem]![$0]!)}
            let heavenly=(heaven[p] ?? []).map { entry in
                WenguaNativeStar(star:entry.0,carriedStem:entry.1,
                  stages:bs.map {WenguaNativeStage(branch:$0,stage:stages[entry.1]![$0]!)})
            }
            var tombs=[WenguaNativeTomb]()
            for star in heavenly {
                for stage in star.stages where stage.stage=="墓" {
                    tombs.append(WenguaNativeTomb(plane:"天盘",stem:star.carriedStem,
                                                 branch:stage.branch,star:star.star))
                }
            }
            for stage in earthStages where stage.stage=="墓" {
                tombs.append(WenguaNativeTomb(plane:"地盘",stem:earthStem,
                                             branch:stage.branch,star:nil))
            }
            palaceRows.append(WenguaNativePalace(id:p,gua:name,earthStem:earthStem,
              earthStages:earthStages,heavenStars:heavenly,
              door:doorAt[p],deity:deityAt[p],branches:bs,
              voidBranches:bs.filter{empties.contains($0)},
              horseBranch:bs.contains(horse) ? horse : nil,tombs:tombs))
        }
        guard palaceRows.filter({$0.id != 5 && $0.door != nil && $0.deity != nil}).count==8,
              palaceRows.first(where:{$0.id==5})?.door == nil,
              palaceRows.first(where:{$0.id==5})?.deity == nil,
              palaceRows.flatMap(\.heavenStars).count==9 else {
            throw WenguaCastError.invalidChart
        }
        return WenguaNativeChart(
            engineVersion:"ios_offline_native_cast_v01",iso:localISO(instant,zone),
            timezone:identifier,pillars:pillars,solarTerm:solarTerm,
            sunLongitude:longitude,bureau:bureau,xunShou:head,
            hiddenStem:hidden,valueStar:valueStar,valueStarPalace:starTarget,
            valueDoor:valueDoor,valueDoorPalace:doorTarget,voidBranches:empties,
            hourHorse:horse,hourHorsePalace:horsePalace,palaces:palaceRows)
    }
}
