import SwiftUI
import CryptoKit

// Wengua iOS professional chart design V2, based on user's two screenshots.
// THIS IS A UI DEMO, NOT A LIVE NATIVE DIVINATION ENGINE.
// Never call V4 numeric scores. Do not treat samples as actual user casts.
// Source: verified V3.9.1 case 2026-11-01 05:00 -05, 阴遁五局.
// Stars, doors, gods, heavenly and earth stems copied from sealed actual chart.

@main
struct WenguaDesignPreviewApp: App {
    var body: some Scene {
        WindowGroup { WenguaRootView() }
    }
}

enum QStyle {
    static let blue = Color(red: 0.16, green: 0.49, blue: 1.0)
    static let red = Color(red: 0.90, green: 0.28, blue: 0.23)
    static let orange = Color(red: 0.89, green: 0.57, blue: 0.12)
    static let green = Color(red: 0.14, green: 0.68, blue: 0.39)
    static let text = Color(red: 0.20, green: 0.20, blue: 0.21)
    static let secondary = Color(red: 0.57, green: 0.58, blue: 0.60)
    static let backing = Color(red: 0.965, green: 0.965, blue: 0.968)
    static let line = Color(red: 0.86, green: 0.87, blue: 0.88)
}

// Consistent per-symbol five-element palette, never a per-layer color.
enum QFive {
    static let palette: [String: Color] = [
        "金": Color(red: 0.83, green: 0.60, blue: 0.10),
        "木": Color(red: 0.09, green: 0.65, blue: 0.34),
        "水": Color(red: 0.15, green: 0.47, blue: 0.91),
        "火": Color(red: 0.89, green: 0.29, blue: 0.25),
        "土": Color(red: 0.61, green: 0.46, blue: 0.28)
    ]
    static let stems = ["甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                        "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"]
    static let stars = ["天蓬":"水","天任":"土","天冲":"木","天辅":"木",
                        "天英":"火","天芮":"土","天柱":"金","天心":"金","天禽":"土"]
    static let doors = ["休门":"水","生门":"土","伤门":"木","杜门":"木",
                        "景门":"火","死门":"土","惊门":"金","开门":"金"]
    static let deities = ["值符":"土","螣蛇":"火","腾蛇":"火","太阴":"金","六合":"木",
                          "白虎":"金","玄武":"水","九地":"土","九天":"金"]
    static let branches = ["子":"水","亥":"水","寅":"木","卯":"木",
                           "巳":"火","午":"火","申":"金","酉":"金",
                           "丑":"土","辰":"土","未":"土","戌":"土"]
    static func shade(_ kind: String, _ name: String) -> Color {
        let t: [String:String]
        switch kind {
        case "stem": t=stems
        case "star": t=stars
        case "door": t=doors
        case "deity": t=deities
        case "branch": t=branches
        default: return QStyle.secondary
        }
        guard let five=t[name],let col=palette[five] else {return QStyle.secondary}
        return col
    }
    static let hourPillar="丁卯"
    static let voidBranches=["戌","亥"]
    static let tombBranches=["甲":"未","乙":"戌","丙":"戌","丁":"丑",
                             "戊":"戌","己":"丑","庚":"丑","辛":"辰","壬":"辰","癸":"未"]
    static let horseByHourBranch=["申":"寅","子":"寅","辰":"寅","寅":"申",
                                  "午":"申","戌":"申","巳":"亥","酉":"亥",
                                  "丑":"亥","亥":"巳","卯":"巳","未":"巳"]
    static var horseBranch: String { horseByHourBranch["卯"] ?? "" }
    static let opposite = [1:9,9:1,2:8,8:2,3:7,7:3,4:6,6:4]
    static let sixClash = ["子":"午","午":"子","丑":"未","未":"丑",
                           "寅":"申","申":"寅","卯":"酉","酉":"卯",
                           "辰":"戌","戌":"辰","巳":"亥","亥":"巳"]
    static func tombHorseRelation(palace: Int, tombBranch: String,
                                  horseBranch: String, horsePalace: Int) -> String {
        if sixClash[tombBranch] == horseBranch {
            return "墓支" + tombBranch + "与马支" + horseBranch +
              "地支六冲：仅为冲墓候选，不代表已冲开"
        }
        if palace == horsePalace {
            return "驿马与入墓同宫，但" + horseBranch + "与" + tombBranch + "并不六冲"
        }
        if opposite[palace] == horsePalace {
            return "驿马位于对宫，但" + horseBranch + "与" + tombBranch +
              "不六冲，不能以宫位相对代替地支冲"
        }
        return "马支与墓支不六冲，不能自动断墓开"
    }
    static func localBranches(_ p: QPalace) -> [String] {p.branches.map {String($0)}}
    static func void(_ p: QPalace) -> [String] {
        if let c=p.computed { return c.voidBranches }
        return localBranches(p).filter {voidBranches.contains($0)}
    }
    static func horse(_ p: QPalace) -> String? {
        if let c=p.computed { return c.horseBranch }
        return localBranches(p).contains(horseBranch) ? horseBranch : nil
    }
    static func heavenTombs(_ p: QPalace) -> [String] {
        if let c=p.computed {
            return c.tombs.filter{$0.plane=="天盘"}.map{"天"+$0.stem+$0.branch+"墓"}
        }
        return p.sky.components(separatedBy:"·").compactMap { stem in
            guard let tomb=tombBranches[stem],localBranches(p).contains(tomb) else {return nil}
            return "天\(stem)\(tomb)墓"
        }
    }
    static func earthTombs(_ p: QPalace) -> [String] {
        if let c=p.computed {
            return c.tombs.filter{$0.plane=="地盘"}.map{"地"+$0.stem+$0.branch+"墓"}
        }
        guard let tomb=tombBranches[p.ground],localBranches(p).contains(tomb) else {return []}
        return ["地\(p.ground)\(tomb)墓"]
    }
}

struct QPalace: Identifiable {
    let id: Int
    let name: String
    let element: String
    let branches: String
    let deity: String
    let stars: String
    let door: String
    let sky: String
    let ground: String
    let stages: String
    let roles: [String]
    var computed: WenguaNativePalace? = nil

    static let actualSourceFixture: [QPalace] = [
        .init(id: 4, name: "巽四", element: "木", branches: "辰巳",
              deity: "九地", stars: "天心", door: "杜门", sky: "乙", ground: "己",
              stages: "乙：辰冠带、巳沐浴", roles: ["天心", "乙奇"]),
        .init(id: 9, name: "离九", element: "火", branches: "午",
              deity: "玄武", stars: "天蓬", door: "景门", sky: "壬", ground: "癸",
              stages: "壬：午胎", roles: []),
        .init(id: 2, name: "坤二", element: "土", branches: "未申",
              deity: "白虎", stars: "天任", door: "死门", sky: "丁", ground: "辛",
              stages: "丁：未冠带、申沐浴", roles: ["时干"]),
        .init(id: 3, name: "震三", element: "木", branches: "卯",
              deity: "九天", stars: "天柱", door: "伤门", sky: "丙", ground: "庚",
              stages: "丙：卯沐浴", roles: []),
        .init(id: 5, name: "中五", element: "土", branches: "",
              deity: "", stars: "", door: "", sky: "", ground: "",
              stages: "", roles: []),
        .init(id: 7, name: "兑七", element: "金", branches: "酉",
              deity: "六合", stars: "天冲", door: "惊门", sky: "庚", ground: "丙",
              stages: "庚：酉帝旺", roles: []),
        .init(id: 8, name: "艮八", element: "土", branches: "丑寅",
              deity: "值符", stars: "天芮·天禽", door: "生门",
              sky: "辛·戊", ground: "丁",
              stages: "天芮携辛：丑养、寅胎；天禽携戊：丑养、寅长生",
              roles: ["天芮"]),
        .init(id: 1, name: "坎一", element: "水", branches: "子",
              deity: "螣蛇", stars: "天英", door: "休门", sky: "癸", ground: "壬",
              stages: "癸：子临官", roles: []),
        .init(id: 6, name: "乾六", element: "金", branches: "戌亥",
              deity: "太阴", stars: "天辅", door: "开门", sky: "己", ground: "乙",
              stages: "己：戌养、亥胎", roles: ["患者"])
    ]
}


extension QPalace {
    // Maps newly computed Swift chart directly into the exact original UI.
    // No hand-filled nine palace rows, and no false subject-specific day use
    // for persons whose V3.9 relationship binder is not yet ported.
    static func fromNative(_ cell: WenguaNativePalace,
                           chart: WenguaNativeChart,
                           relation: String) -> QPalace {
        let p=cell.id
        let e=["坎":"水","坤":"土","震":"木","巽":"木","中":"土",
               "乾":"金","兑":"金","艮":"土","离":"火"][cell.gua] ?? "土"
        let names=cell.heavenStars.map{$0.star.replacingOccurrences(of:"星",with:"")}
        let sky=cell.heavenStars.map{$0.carriedStem}.joined(separator:"·")
        let life = cell.heavenStars.map { star -> String in
            let starName = star.star.replacingOccurrences(of:"星",with:"")
            let stagesText = star.stages.map { $0.branch + $0.stage }.joined(separator:"、")
            return starName + "携" + star.carriedStem + "：" + stagesText
        }.joined(separator:"；")
        var tags=[String]()
        if cell.heavenStars.contains(where:{$0.star=="天芮星"}) {tags.append("病宫")}
        if cell.heavenStars.contains(where:{$0.star=="天心星"}) {tags.append("天心")}
        if cell.heavenStars.contains(where:{$0.carriedStem=="乙"}) {tags.append("乙奇")}
        if cell.heavenStars.contains(where:{$0.carriedStem==String(chart.pillars.hour.prefix(1))}) {
            tags.append("时干")
        }
        if relation=="本人" &&
           cell.heavenStars.contains(where:{$0.carriedStem==String(chart.pillars.day.prefix(1))}) {
            tags.append("患者")
        }
        return QPalace(id:p,name:cell.gua+(p==5 ? "五" : String(p)),
                       element:e,branches:cell.branches.joined(),
                       deity:cell.deity ?? "",stars:names.joined(separator:"·"),
                       door:cell.door ?? "",sky:sky,ground:cell.earthStem,
                       stages:life,roles:tags,computed:cell)
    }
}

struct WenguaRootView: View {
    var body: some View {
        TabView {
            NavigationStack { ProfessionalChartScreen() }
                .tabItem { Label("局式", systemImage: "house") }
            NavigationStack { NotReadyScreen(name: "多局") }
                .tabItem { Label("多局", systemImage: "square.grid.2x2") }
            NavigationStack { NotReadyScreen(name: "研习") }
                .tabItem { Label("研习", systemImage: "viewfinder") }
            NavigationStack { NotReadyScreen(name: "案例") }
                .tabItem { Label("案例", systemImage: "list.bullet") }
            NavigationStack { NotReadyScreen(name: "我") }
                .tabItem { Label("我", systemImage: "person.crop.circle") }
        }
        .tint(QStyle.blue)
    }
}

// Read-only V3.9.1 sample readings: NOT used to predict or read a newly cast chart.
struct FrozenReadingSection: Decodable, Identifiable {
    let id: String
    let title: String
    let text: String
}
struct FrozenReadingSample: Decodable {
    let id: String
    let iso: String
    let originalReading: String
    let readingSections: [FrozenReadingSection]
}
private struct FrozenReadingEnvelope: Decodable {
    let samples: [FrozenReadingSample]
}
enum FrozenPreview {
    static let isos = [
        "2026-11-01T05:00:00-05:00","2026-11-04T05:00:00-05:00",
        "2026-11-10T21:00:00-05:00","2026-11-21T17:00:00-05:00"
    ]
    static let labels = ["11/01 卯时","11/04 卯时","11/10 亥时","11/21 酉时"]
    static let readings: [FrozenReadingSample] = {
        guard let url=Bundle.main.url(forResource:"FrozenReadingV391",withExtension:"json"),
              let data=try? Data(contentsOf:url),
              let records=try? JSONDecoder().decode(FrozenReadingEnvelope.self,from:data),
              records.samples.map(\.iso)==isos else {return []}
        return records.samples
    }()
    static func cast(_ index: Int) -> WenguaNativeChart? {
        guard isos.indices.contains(index) else {return nil}
        let formatter=ISO8601DateFormatter()
        formatter.formatOptions=[.withInternetDateTime]
        guard let date=formatter.date(from:isos[index]) else {return nil}
        // This is an actual deterministic offline calculation from each FIXED
        // input instant, not a user query and never a persisted issue receipt.
        return try? WenguaNativeCore.compute(at:date,timezone:"America/New_York")
    }
}

struct ProfessionalChartScreen: View {
    @State private var chosenPalace: QPalace?
    @State private var showAsk = false
    @State private var showReading = false
    @State private var nativeChart: WenguaNativeChart? = nil
    @State private var castRelation = "本人"
    @State private var selectedSampleIndex = 0

    private var displayChart: WenguaNativeChart? {
        nativeChart ?? FrozenPreview.cast(selectedSampleIndex)
    }

    private var shownPalaces: [QPalace] {
        guard let chart=displayChart else {return QPalace.actualSourceFixture}
        let byId=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        return WenguaNativeCore.branchOrderPalaces.compactMap {
            guard let cell=byId[$0] else {return nil}
            return QPalace.fromNative(cell,chart:chart,relation:castRelation)
        }
    }
    private var shownPillars: WenguaNativePillars {
        displayChart?.pillars ?? WenguaNativePillars(year:"丙午",month:"戊戌",
                                                      day:"己卯",hour:"丁卯")
    }
    private var bureauInfo: String {
        let kind = displayChart?.bureau.dun == "yang" ? "阳遁" : "阴遁"
        let number = String(displayChart?.bureau.ju ?? 5)
        let head = displayChart?.xunShou ?? "甲子"
        return kind + " · " + number + "局 › " + head + "旬"
    }
    private var starDoorInfo: String {
        let star = (displayChart?.valueStar ?? "天禽星").replacingOccurrences(of:"星",with:"")
        let door = displayChart?.valueDoor ?? "死门"
        return "值符：" + star + "  值使：" + door
    }
    private var solarInfo: String {
        let term = displayChart?.solarTerm ?? "霜降"
        let yuan = displayChart?.bureau.yuan ?? "upper"
        return "时家转盘 · " + term + " · " + yuan
    }
    private var voidInfo: String {
        let head = displayChart?.xunShou ?? "甲子"
        let empties = displayChart?.voidBranches.joined(separator:"、") ?? "戌亥"
        return "时空：" + head + "旬，" + empties + "空"
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    Button {
                        showAsk = true
                    } label: {
                        Text(displayChart.map { String($0.iso.prefix(16)).replacingOccurrences(of:"T",with:" ") +
                              (nativeChart == nil ? " · 固定测试  ⌄" : " · 本机实算  ⌄") }
                             ?? "测试盘未能计算 · 请查看构建日志")
                            .font(.system(size: 16))
                            .foregroundStyle(QStyle.text)
                    }
                    Spacer()
                    Button("选时") { showAsk = true }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 13)

                HStack(alignment: .top, spacing: 8) {
                    pillar(String(shownPillars.year.prefix(1)),String(shownPillars.year.suffix(1)),"年",color:QStyle.red)
                    pillar(String(shownPillars.month.prefix(1)),String(shownPillars.month.suffix(1)),"月",color:QStyle.orange)
                    pillar(String(shownPillars.day.prefix(1)),String(shownPillars.day.suffix(1)),"日",color:QStyle.orange)
                    pillar(String(shownPillars.hour.prefix(1)),String(shownPillars.hour.suffix(1)),"时",color:QStyle.blue)
                    Spacer(minLength: 0)
                    VStack(alignment: .leading, spacing: 6) {
                        Text(bureauInfo)
                        Text(starDoorInfo)
                    }
                    .font(.system(size: 11))
                    .foregroundStyle(QStyle.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(QStyle.backing)

                HStack {
                    Text(solarInfo)
                        .font(.caption)
                        .foregroundStyle(QStyle.secondary)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .overlay(Capsule().stroke(QStyle.line))
                    Spacer()
                    Button { showAsk = true } label: {
                        Image(systemName: "calendar.badge.clock")
                    }
                    Button { showReading = true } label: {
                        Image(systemName: "text.book.closed")
                    }
                }
                .foregroundStyle(QStyle.secondary)
                .padding(.horizontal, 12)
                .padding(.vertical, 9)
                .background(QStyle.backing)

                if nativeChart == nil {
                    ScrollView(.horizontal, showsIndicators:false) {
                        HStack(spacing:7) {
                            ForEach(FrozenPreview.isos.indices,id: \.self) { index in
                                Button(FrozenPreview.labels[index]) {
                                    selectedSampleIndex=index
                                }
                                .font(.system(size: 11,weight: selectedSampleIndex==index ? .semibold : .regular))
                                .padding(.vertical,8)
                                .padding(.horizontal,9)
                                .background(selectedSampleIndex==index
                                    ? Color(red:0.88,green:0.94,blue:1) : .white,
                                    in:RoundedRectangle(cornerRadius:7))
                                .overlay(RoundedRectangle(cornerRadius:7)
                                    .stroke(QStyle.line))
                            }
                        }
                        .padding(.horizontal,10)
                        .padding(.vertical,7)
                    }
                    .background(QStyle.backing)
                }

                LazyVGrid(
                    columns: Array(repeating: GridItem(.flexible(), spacing: 1), count: 3),
                    spacing: 1
                ) {
                    ForEach(shownPalaces) { palace in
                        Button { chosenPalace = palace } label: {
                            ProfessionalPalaceTile(palace: palace)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.vertical, 1)
                .background(QStyle.line)

                HStack(spacing: 8) {
                    tag("十二长生")
                    tag("空亡")
                    tag("宫位详情")
                    Spacer()
                }
                .padding(12)
                .background(QStyle.backing)

                VStack(alignment: .leading, spacing: 10) {
                    Text("年命：未选择 · 不臆造")
                    Text(voidInfo)
                    HStack(spacing: 10) {
                        Button("问测何事") { showAsk = true }
                        Button("V3.9.1 断词") { showReading = true }
                    }
                    .buttonStyle(.bordered)
                }
                .foregroundStyle(QStyle.secondary)
                .font(.subheadline)
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(QStyle.backing)

                Text(nativeChart == nil
                     ? "当前为固定测试盘。点击选时并静心30秒后，即可用原生 Swift 离线实时生成新盘。"
                     : "本局由本机离线 Swift 实算四柱、九宫及空马墓。疾病 V3.9.1 自然断词尚未移植，勿将其视为已完成的诊断。")
                    .font(.caption2)
                    .foregroundStyle(QStyle.secondary)
                    .padding(14)
            }
        }
        .background(.white)
        .navigationTitle(nativeChart == nil ? "局式 · 固定测试盘" : "局式 · 原生实算")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $chosenPalace) { palace in
            ProfessionalPalaceDetail(palace: palace,
                hourHorse:displayChart?.hourHorse ?? "巳",
                hourHorsePalace:displayChart?.hourHorsePalace ?? 4)
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
        }
        .sheet(isPresented: $showAsk) {
            CastSetupScreen { computed, relation in
                nativeChart=computed
                castRelation=relation
                showAsk=false
            }
        }
        .sheet(isPresented: $showReading) { TraditionalReadingPreview(nativeChart:nativeChart,sampleIndex:selectedSampleIndex) }
    }

    private func pillar(_ sky: String, _ branch: String, _ label: String, color: Color) -> some View {
        VStack(spacing: 1) {
            Text(sky).font(.system(size: 23, weight: .medium))
                .foregroundStyle(QFive.shade("stem",sky))
            Text(label).font(.system(size: 9)).foregroundStyle(QStyle.secondary)
            Text(branch).font(.system(size: 22, weight: .medium))
                .foregroundStyle(QFive.shade("branch",branch))
        }
        .frame(width: 35)
    }

    private func tag(_ title: String) -> some View {
        Text(title)
            .font(.caption2)
            .foregroundStyle(QStyle.secondary)
            .padding(.horizontal, 10).padding(.vertical, 5)
            .overlay(Capsule().stroke(QStyle.line))
    }
}

// Both heaven and earth per-branch life stages share ONE display contract.
// Native casts read the actual Swift engine, frozen preview recalculates from
// the identical canonical full 10x12 dictionary, not hardcoded palace labels.
struct QLifeRow: Identifiable {
    let id: String
    let plane: String
    let stem: String
    let stages: [WenguaNativeStage]
}
extension QPalace {
    var lifeRows: [QLifeRow] {
        if let cell=computed {
            let tops=cell.heavenStars.enumerated().map { index, star in
                QLifeRow(id:"h"+String(index),plane:"天",
                         stem:star.carriedStem,stages:star.stages)
            }
            return tops + [QLifeRow(id:"earth",plane:"地",
                 stem:cell.earthStem,stages:cell.earthStages)]
        }
        let bs=QFive.localBranches(self)
        func actualStages(_ stem:String) -> [WenguaNativeStage] {
            bs.compactMap { branch in
                guard let state=WenguaNativeCore.stages[stem]?[branch] else {return nil}
                return WenguaNativeStage(branch:branch,stage:state)
            }
        }
        let tops=sky.components(separatedBy:"·").enumerated().compactMap { index, stem -> QLifeRow? in
            guard !stem.isEmpty else {return nil}
            return QLifeRow(id:"h"+String(index),plane:"天",
                            stem:stem,stages:actualStages(stem))
        }
        if id==5 {return []}
        return tops + [QLifeRow(id:"earth",plane:"地",
                      stem:ground,stages:actualStages(ground))]
    }
}
struct PalaceLifeRow: View {
    let line: QLifeRow
    var body: some View {
        HStack(spacing: 1) {
            Text(line.plane).foregroundStyle(QStyle.secondary)
            Text(line.stem).foregroundStyle(QFive.shade("stem",line.stem))
            ForEach(line.stages,id: \.branch) { stage in
                Text(stage.branch).foregroundStyle(QFive.shade("branch",stage.branch))
                Text(stage.stage).foregroundStyle(QStyle.secondary)
            }
        }
        .font(.system(size: 9))
        .lineLimit(1)
        .minimumScaleFactor(0.72)
    }
}

struct ProfessionalPalaceTile: View {
    let palace: QPalace

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            if palace.id == 5 {
                Spacer()
                Text("中五")
                    .font(.system(size: 22))
                    .foregroundStyle(QStyle.secondary)
                if !palace.ground.isEmpty {
                    Text("地盘 " + palace.ground)
                        .font(.system(size: 12))
                        .foregroundStyle(QFive.shade("stem",palace.ground))
                }
                Text("特殊宫位")
                    .font(.system(size: 10))
                    .foregroundStyle(QStyle.secondary)
                Spacer()
            } else {
                HStack(spacing: 2) {
                    ForEach(Array(palace.branches.map{String($0)}.enumerated()),id: \.offset) { part in
                        Text(part.element).foregroundStyle(QFive.shade("branch",part.element))
                    }
                    Text("·").foregroundStyle(QStyle.secondary)
                    Text(palace.element + "行")
                        .foregroundStyle(QFive.palette[palace.element] ?? QStyle.secondary)
                    Spacer(minLength: 0)
                    Text("\(palace.id)").foregroundStyle(QStyle.secondary)
                }
                .font(.system(size: 10)).lineLimit(1)

                HStack {
                    Text(palace.ground)
                        .foregroundStyle(QFive.shade("stem", palace.ground))
                    Spacer()
                    Text(palace.deity)
                        .foregroundStyle(QFive.shade("deity", palace.deity))
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
                .font(.system(size: 16, weight: .medium))

                Spacer(minLength: 3)
                HStack(spacing: 2) {
                    HStack(spacing: 1) {
                        ForEach(Array(palace.stars.components(separatedBy:"·").enumerated()),id: \.offset) { entry in
                            if entry.offset > 0 { Text("·").foregroundStyle(QStyle.secondary) }
                            Text(entry.element).foregroundStyle(QFive.shade("star",entry.element))
                        }
                    }
                    .lineLimit(1).minimumScaleFactor(0.6)
                    Spacer(minLength: 1)
                    HStack(spacing: 1) {
                        ForEach(Array(palace.sky.components(separatedBy:"·").enumerated()),id: \.offset) { entry in
                            if entry.offset > 0 { Text("·").foregroundStyle(QStyle.secondary) }
                            Text(entry.element).foregroundStyle(QFive.shade("stem",entry.element))
                        }
                    }
                    .lineLimit(1).minimumScaleFactor(0.65)
                }
                .font(.system(size: 15, weight: .medium))

                HStack(spacing: 2) {
                    Text(palace.door)
                        .foregroundStyle(QFive.shade("door",palace.door))
                    Spacer(minLength: 1)
                    Text(palace.ground)
                        .foregroundStyle(QFive.shade("stem",palace.ground))
                }
                .font(.system(size: 17, weight: .medium))

                VStack(alignment: .leading, spacing: 2) {
                    ForEach(palace.lifeRows) { line in PalaceLifeRow(line:line) }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                HStack(spacing: 3) {
                    ForEach(palace.roles, id: \.self) { role in
                        Text(role)
                            .font(.system(size: 9))
                            .foregroundStyle(QStyle.blue)
                    }
                }
                .frame(minHeight: 12, alignment: .leading)
                VStack(alignment: .leading, spacing: 2) {
                    HStack(spacing: 3) {
                        ForEach(QFive.void(palace),id: \.self) { branch in
                            Text(branch + "空").foregroundStyle(QFive.shade("branch",branch))
                        }
                        if let horse=QFive.horse(palace) {
                            Text("马" + horse).foregroundStyle(QFive.shade("branch",horse))
                        }
                    }
                    ForEach(QFive.heavenTombs(palace) + QFive.earthTombs(palace),id: \.self) { label in
                        Text(label)
                            .foregroundStyle(QFive.shade("stem",String(label.dropFirst().prefix(1))))
                            .fixedSize(horizontal: true,vertical: false)
                    }
                }
                .font(.system(size: 9, weight: .semibold))
            }
        }
        .padding(.horizontal, 7)
        .padding(.vertical, 9)
        .frame(maxWidth: .infinity, minHeight: 238, alignment: .topLeading)
        .background(.white)
        .contentShape(Rectangle())
        .accessibilityLabel(palace.id == 5
             ? "中五宫，不伪造普通星门神"
             : "\(palace.name)，\(palace.deity)，\(palace.stars)，\(palace.door)，天盘\(palace.sky)，地盘\(palace.ground)，\(palace.stages)")
    }
}

struct ProfessionalPalaceDetail: View {
    let palace: QPalace
    let hourHorse: String
    let hourHorsePalace: Int
    private let columns = [GridItem(.flexible()), GridItem(.flexible())]

    private var conditionDescription: String {
        let void = QFive.void(palace)
        let horse = QFive.horse(palace)
        let sky = QFive.heavenTombs(palace)
        let earth = QFive.earthTombs(palace)
        let emptiness = void.isEmpty ? "本宫无" : void.joined(separator:"、") + "空"
        let horseState = horse == nil ? "不落本宫" : "在本宫" + (horse ?? "")
        let top = sky.isEmpty ? "无" : sky.joined(separator:"、")
        let lower = earth.isEmpty ? "无" : earth.joined(separator:"、")
        let allTombBranches = palace.computed?.tombs.map{$0.branch} ??
            (sky + earth).compactMap { label -> String? in
                let chars=Array(label)
                return chars.count>=4 ? String(chars[2]) : nil
            }
        let conflictNotes=allTombBranches.map { branch in
            QFive.tombHorseRelation(palace:palace.id,tombBranch:branch,
                                    horseBranch:hourHorse,horsePalace:hourHorsePalace)
        }
        return ["旬空：" + emptiness,"时支驿马：" + horseState,
                "天盘干入墓：" + top,"地盘干入墓：" + lower,
                "冲墓条件：" + (conflictNotes.isEmpty ? "本宫无入墓" :
                  conflictNotes.joined(separator:"；"))].joined(separator:"；")
    }
    private var roleDescription: String {
        let identity = palace.roles.isEmpty
            ? "本宫未被选为此问主要角色"
            : "本宫角色：" + palace.roles.joined(separator:"、")
        let emptiness = QFive.void(palace).isEmpty
            ? "" : "；旬空：" + QFive.void(palace).joined(separator:"、")
        return palace.name + "属" + palace.element + "，辖" + palace.branches +
            "支。" + identity + emptiness + "。同宫同事实不得当作两个独立证据。"
    }
    private var statusTags: [String] {
        palace.roles + QFive.void(palace).map{$0 + "空"} +
            (palace.computed == nil ? ["测试盘"] : ["本机实算"])
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 15) {
                headerBlock
                tagBlock
                factsBlock
                Text("传统文化与古籍象意展示。新盘完整断词尚待 V3.9.1 原生移植。")
                    .font(.footnote)
                    .foregroundStyle(QStyle.secondary)
            }
            .padding(20)
        }
        .background(QStyle.backing)
    }
    private var headerBlock: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(palace.name + " · " + palace.element + "行")
                .font(.system(size:27,weight:.semibold))
                .foregroundStyle(QFive.palette[palace.element] ?? QStyle.text)
            Text(palace.computed == nil ? "已计算测试盘 · 古籍研究" :
                  "本机 Swift 实算九宫 · 不是现实疾病诊断")
                .font(.caption).foregroundStyle(QStyle.secondary)
        }
    }
    private var tagBlock: some View {
        HStack(spacing:7) {
            ForEach(statusTags,id: \.self) { tag in detailTag(tag) }
        }
    }
    @ViewBuilder private var factsBlock: some View {
        if palace.id == 5 {
            factCard("中五宫特殊规则",
                     text:"中五不套普通八门、九星与八神；中五地盘实测干："+palace.ground)
        } else {
            factsGrid
            lifeDetailCard
            factCard("空亡 · 驿马 · 入墓",text:conditionDescription)
            factCard("宫位与角色",text:roleDescription)
            factCard("旺相休囚废 · 击刑 · 门迫",
                     text:"目前原生结构尚无上述状态经书源校对的独立触发字段；不得伪造或将未计算当作未发生。")
        }
    }
    private var factsGrid: some View {
        LazyVGrid(columns: columns, spacing: 10) {
            valueCard("八神",value:palace.deity,
                      color:QFive.shade("deity",palace.deity))
            multiValueCard("九星",value:palace.stars,kind:"star")
            valueCard("八门",value:palace.door,
                      color:QFive.shade("door",palace.door))
            stemCard("天 / 地盘干",sky:palace.sky,ground:palace.ground)
        }
    }

    private var lifeDetailCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("十二长生 · 天盘／地盘分别实算").font(.headline)
            ForEach(palace.lifeRows) { line in
                VStack(alignment: .leading, spacing: 4) {
                    Text(line.plane + "盘干 " + line.stem)
                        .foregroundStyle(QFive.shade("stem",line.stem))
                    HStack(spacing: 7) {
                        ForEach(line.stages,id: \.branch) { stage in
                            HStack(spacing: 2) {
                                Text(stage.branch)
                                    .foregroundStyle(QFive.shade("branch",stage.branch))
                                Text(stage.stage).foregroundStyle(QStyle.secondary)
                            }
                        }
                    }.font(.subheadline)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(15)
        .background(.white, in: RoundedRectangle(cornerRadius:15))
    }
    private func multiValueCard(_ label:String,value:String,kind:String) -> some View {
        VStack(alignment:.leading,spacing:10) {
            Text(label).font(.caption).foregroundStyle(QStyle.secondary)
            HStack(spacing:2) {
                ForEach(Array(value.components(separatedBy:"·").enumerated()),id: \.offset) { entry in
                    Text(entry.element).foregroundStyle(QFive.shade(kind,entry.element))
                }
            }
            .font(.system(size:20,weight:.medium))
            .lineLimit(1).minimumScaleFactor(0.65)
        }
        .frame(maxWidth:.infinity,minHeight:90,alignment:.leading)
        .padding(13)
        .background(.white,in:RoundedRectangle(cornerRadius:15))
    }
    private func detailTag(_ label: String) -> some View {
        Text(label)
            .font(.caption2)
            .padding(.horizontal, 10).padding(.vertical, 7)
            .foregroundStyle(QStyle.blue)
            .background(Color(red: 0.91, green: 0.95, blue: 1.0), in: Capsule())
    }

    private func valueCard(_ label: String, value: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(label).font(.caption).foregroundStyle(QStyle.secondary)
            Text(value).font(.system(size: 21, weight: .medium))
                .foregroundStyle(color).minimumScaleFactor(0.7).lineLimit(1)
        }
        .frame(maxWidth: .infinity, minHeight: 90, alignment: .leading)
        .padding(13)
        .background(.white, in: RoundedRectangle(cornerRadius: 15))
    }

    private func stemCard(_ label: String, sky: String, ground: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(label).font(.caption).foregroundStyle(QStyle.secondary)
            HStack(spacing: 2) {
                ForEach(Array(sky.components(separatedBy:"·").enumerated()),id: \.offset) { entry in
                    if entry.offset>0 { Text("·").foregroundStyle(QStyle.secondary) }
                    Text(entry.element).foregroundStyle(QFive.shade("stem",entry.element))
                }
                Text(" / ").foregroundStyle(QStyle.secondary)
                Text(ground).foregroundStyle(QFive.shade("stem",ground))
            }
            .font(.system(size: 20,weight: .medium))
            .lineLimit(1).minimumScaleFactor(0.55)
        }
        .frame(maxWidth: .infinity, minHeight: 90, alignment: .leading)
        .padding(13)
        .background(.white, in: RoundedRectangle(cornerRadius: 15))
    }

    private func factCard(_ title: String, text: String) -> some View {
        VStack(alignment: .leading, spacing: 9) {
            Text(title).font(.headline)
            Text(text).font(.subheadline)
                .foregroundStyle(QStyle.secondary).fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(15)
        .background(.white, in: RoundedRectangle(cornerRadius: 15))
    }
}

// Exact normalized question + subject relationship is a lower bound of "same issue".
// Same event phrased differently or reinstalled on another phone can bypass this;
// no UI should claim these local exact-match records provide global guarantees.
enum QIssuePolicy {
    static let window: TimeInterval = 15 * 24 * 60 * 60

    static func signature(topic: String, relation: String, subject: String, question: String) -> String {
        func normalized(_ text: String) -> String {
            text.folding(options: [.widthInsensitive, .caseInsensitive],
                         locale: Locale(identifier: "zh_CN"))
                .filter { !$0.isWhitespace && !$0.isPunctuation }
        }
        let key = [topic, relation, subject.isEmpty ? "同一当事人" : subject, question]
            .map(normalized).joined(separator: "|")
        let digest = SHA256.hash(data: Data(("wengua-native-issue-v2|" + key).utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    static func nextPermitted(_ key: String, asOf now: Date = .now) -> Date? {
        let last = UserDefaults.standard.object(forKey: "wengua:completed:" + key) as? Date
        guard let last, last.addingTimeInterval(window) > now else { return nil }
        return last.addingTimeInterval(window)
    }

    static func commitRealCompletedCast(_ key: String, validated: Bool, stored: Bool) {
        // Strictly called AFTER real offline engine produced a valid chart,
        // user record persisted and transaction validated; NEVER for demo.
        guard validated && stored && nextPermitted(key) == nil else { return }
        UserDefaults.standard.set(Date(), forKey: "wengua:completed:" + key)
    }
}

private struct LocalNativeCase: Codable {
    let issueFingerprint: String
    let relation: String
    let optionalBirthYear: Int?
    let course: String?
    let completedAt: Date
    let chart: WenguaNativeChart
}

struct CastSetupScreen: View {
    let onNativeCast: (WenguaNativeChart, String) -> Void
    init(onNativeCast: @escaping (WenguaNativeChart,String)->Void) {
        self.onNativeCast=onNativeCast
    }
    @Environment(\.dismiss) private var dismiss
    @State private var subject = "本人"
    @State private var subjectName = ""
    @State private var birthYear = ""
    @State private var question = ""
    @State private var duration = "未说明"
    @State private var chosenTime = Date()
    @State private var useCurrentInstant = true
    @State private var phase = 0
    @State private var calmEnds: Date?
    @State private var validationMessage = ""
    private let relations = ["本人", "父亲", "母亲", "丈夫", "妻子", "兄弟", "姐妹", "儿子", "女儿"]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 17) {
                    if phase == 0 {
                        Text("问测何事？")
                            .font(.system(size: 28, weight: .medium))
                        Text("同一件具体事情，15天内只起一次。")
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                        Group {
                            Text("问事内容（必填）").font(.headline)
                            TextField("描述一件具体的事，至少四个字", text: $question, axis: .vertical)
                                .lineLimit(2...4)
                            Text("当事人").font(.headline)
                            Picker("你为谁问事", selection: $subject) {
                                ForEach(relations, id: \.self) { Text($0).tag($0) }
                            }
                            .pickerStyle(.menu)
                            TextField("当事人称呼 · 可选", text: $subjectName)
                            TextField("出生公历年份（选填，例如 1988）",text:$birthYear)
                                .keyboardType(.numberPad)
                            Text("未提供出生年份时不计算年命；填写年份也不代表关系取用神已完成原生移植。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                            Picker("病程（可选）", selection: $duration) {
                                ForEach(["未说明", "新病", "久病"], id: \.self) { Text($0) }
                            }
                            Toggle("此刻起局（静心结束后锁定当时的实时时刻）",isOn:$useCurrentInstant)
                                .tint(QStyle.blue)
                            if !useCurrentInstant {
                                DatePicker("指定复盘时间",selection:$chosenTime,
                                           displayedComponents:[.date,.hourAndMinute])
                                    .datePickerStyle(.wheel)
                                    .labelsHidden()
                                    .frame(maxWidth:.infinity)
                            }
                            Text(useCurrentInstant ?
                                 "30秒结束后按确认起局时，采集本机真实时刻与 IANA 时区。" :
                                 "当前选择指定时刻复盘，按你明确指定的时间起盘，仍须通过30秒静心。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                        }
                        .padding(12)
                        .background(.white, in: RoundedRectangle(cornerRadius: 14))
                        VStack(alignment: .leading, spacing: 8) {
                            Text("一事一占 · 尊重事实").font(.headline)
                            Text("静下心想这件事30秒。心诚则灵，尊重事实。同一件事15天内只完成一次真实起局。仅凭本机记录无法彻底识别换说法或换设备的同一件事。")
                                .font(.subheadline)
                        }
                        .padding(15)
                        .background(Color(red: 1.0, green: 0.98, blue: 0.92),
                                    in: RoundedRectangle(cornerRadius: 14))
                        if !validationMessage.isEmpty {
                            Text(validationMessage)
                                .font(.subheadline).foregroundStyle(QStyle.red)
                        }
                        Button("确认问题 · 进入30秒静心") { tryStartRitual() }
                            .buttonStyle(.borderedProminent)
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("静心 · 默想所问")
                            .font(.system(size: 28, weight: .medium))
                            .frame(maxWidth: .infinity)
                        Text("心诚则灵，尊重事实")
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                            .frame(maxWidth: .infinity)
                        TimelineView(.periodic(from: .now, by: 0.25)) { context in
                            let remaining = calmEnds.map { max(0, Int(ceil($0.timeIntervalSince(context.date)))) } ?? 30
                            VStack(spacing: 25) {
                                Text(String(format: "%02d", remaining))
                                    .font(.system(size: 70, weight: .ultraLight, design: .rounded))
                                    .foregroundStyle(QStyle.blue)
                                    .frame(width: 210, height: 210)
                                    .overlay(Circle().stroke(QStyle.blue.opacity(0.45), lineWidth: 2))
                                ProgressView(value: Double(30 - remaining), total: 30)
                                    .tint(QStyle.blue)
                                if calmEnds == nil {
                                    Button("开始静心30秒") { calmEnds = Date().addingTimeInterval(30) }
                                        .buttonStyle(.borderedProminent)
                                } else if remaining == 0 {
                                    Button("确认起局 · 离线实算九宫") { completeNativeCast() }
                                        .disabled(!validationMessage.isEmpty)
                                        .buttonStyle(.borderedProminent)
                                } else {
                                    Text("静心进行中 · 无跳过按钮")
                                        .foregroundStyle(QStyle.secondary)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 30)
                        }
                        if !validationMessage.isEmpty {
                            Text(validationMessage)
                                .font(.footnote).foregroundStyle(QStyle.red)
                        }
                        Text("九宫将由本地 Swift 真实计算；V3.9.1 自然断词移植尚未完成，因此不会用固定案例断词冒充本次结果。")
                            .font(.footnote).foregroundStyle(QStyle.secondary)
                    }
                }
                .padding(18)
            }
            .background(QStyle.backing)
            .navigationTitle(phase == 0 ? "问事与起局时间" : "静心三十秒")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
        }
    }


    // The only UI path that calls actual native astronomical chart creation.
    // Past 'fixed demo' never comes here and cannot consume the 15day lock.
    private func completeNativeCast() {
        guard let calmEnds, Date() >= calmEnds else {
            validationMessage="必须完成完整30秒静心后才能起局。"
            return
        }
        let key=QIssuePolicy.signature(topic:"health.severity",relation:subject,
                                       subject:subjectName,question:question)
        if let next=QIssuePolicy.nextPermitted(key) {
            validationMessage="同一件事未满15天；下次允许："+next.formatted()
            return
        }
        do {
            let finalInstant=useCurrentInstant ? Date() : chosenTime
            let localZone=TimeZone.current.identifier
            let result=try WenguaNativeCore.compute(at:finalInstant,timezone:localZone)
            // Persistent case receipt is ONLY original board/clock facts and
            // hashed issue ID. User's raw private question is NOT stored here.
            let record=LocalNativeCase(issueFingerprint:key,relation:subject,
                                       optionalBirthYear:Int(birthYear),
                                       course:duration=="未说明" ? nil : duration,
                                       completedAt:Date(),chart:result)
            let encoded=try JSONEncoder().encode(record)
            let recordId="wengua:nativecase:"+UUID().uuidString
            UserDefaults.standard.set(encoded,forKey:recordId)
            guard UserDefaults.standard.data(forKey:recordId)==encoded else {
                throw WenguaCastError.invalidChart
            }
            QIssuePolicy.commitRealCompletedCast(key,validated:true,stored:true)
            onNativeCast(result,subject)
            dismiss()
        } catch {
            validationMessage="本次未起局成功，也不会登记15天限制："+error.localizedDescription
        }
    }

    private func tryStartRitual() {
        let cleanedYear=birthYear.trimmingCharacters(in:.whitespacesAndNewlines)
        if !cleanedYear.isEmpty {
            guard let year=Int(cleanedYear), (1850...2150).contains(year) else {
                validationMessage="出生年份需是有效公历年份（1850–2150），或留空。"
                return
            }
        }
        let normalized = question.filter { !$0.isWhitespace && !$0.isPunctuation }
        guard normalized.count >= 4 else {
            validationMessage = "请先明确至少四个字的一件具体事情。"
            return
        }
        let key = QIssuePolicy.signature(topic: "health.severity",
             relation: subject, subject: subjectName, question: question)
        if let date = QIssuePolicy.nextPermitted(key) {
            validationMessage = "同一问题15天内已经起过局。下次允许：" +
                date.formatted(date: .abbreviated, time: .shortened)
            return
        }
        validationMessage = ""
        phase = 1
        calmEnds = nil
    }
}

struct TraditionalReadingPreview: View {
    let nativeChart: WenguaNativeChart?
    let sampleIndex: Int
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 15) {
                    Text("古籍断词 · V3.9.1")
                        .font(.system(size: 28, weight: .medium))
                    if let chart=nativeChart {
                        Text("当前九宫已由 iPhone Swift 离线引擎真实起盘。")
                            .font(.caption).foregroundStyle(QStyle.secondary)
                        let actualPillars = [chart.pillars.year,chart.pillars.month,
                                             chart.pillars.day,chart.pillars.hour]
                        Text(actualPillars.joined(separator:" ") + " · " + chart.solarTerm)
                            .font(.headline)
                        Text("V3.9.1 完整古籍推理和断词尚未移植到 iOS。本次只展示真实计算九宫，不输出假断词或分数。")
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                    } else if FrozenPreview.readings.indices.contains(sampleIndex) {
                        let sample=FrozenPreview.readings[sampleIndex]
                        Text("封存的 V3.9.1 固定计算测试盘：" + sample.iso)
                            .font(.caption).foregroundStyle(QStyle.secondary)
                        Text(sample.originalReading)
                            .font(.subheadline)
                            .textSelection(.enabled)
                            .fixedSize(horizontal:false,vertical:true)
                            .padding(14)
                            .background(.white,in:RoundedRectangle(cornerRadius:12))
                        ForEach(sample.readingSections) { section in
                            DisclosureGroup(section.title) {
                                Text(section.text).font(.subheadline)
                                    .foregroundStyle(QStyle.secondary)
                                    .padding(.top,8)
                                    .textSelection(.enabled)
                            }
                            .padding(13)
                            .background(.white,in:RoundedRectangle(cornerRadius:12))
                        }
                    } else {
                        Text("封存原始断词资源未加载；拒绝以其它测试盘文本替代。")
                            .foregroundStyle(QStyle.red)
                    }
                    Text("此软件仅展示传统古籍象意。尚无 iOS 原生 V3.9.1 本次断词；医疗问题须咨询专业医护人员。")
                        .font(.caption).foregroundStyle(QStyle.secondary)
                }
                .padding()
            }
            .background(QStyle.backing)
            .navigationTitle("断词")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
        }
    }
}

enum TraditionalChapter {
    static let demo: [(String, String)] = [
        ("01 · 问事取用", "本人用干己落乾六宫；天芮落艮八宫。"),
        ("02 · 值符值使", "值符天禽落艮八宫；值使死门落坤二宫。"),
        ("03 · 天芮病宫", "天芮携辛在丑养、寅胎，天禽携戊在丑养、寅长生。"),
        ("04 · 病星月令", "依据真实月令与病星宫位关系核算。"),
        ("05 · 患者用神", "本人己落乾六宫，戌养、亥胎，旬空。"),
        ("07 · 医生医药", "天心与乙奇都落巽四宫；乙辰冠带、巳沐浴。"),
        ("08 · 时干事体", "丁落坤二宫，未冠带、申沐浴。"),
        ("09 · 特殊格局", "真实核对刑冲墓空、门迫、冲开入墓等复合条件。"),
        ("10 · 伏吟反吟与应期", "按原书触发条件决定是否给出应期。"),
        ("11 · 最后断词", "完整原书自然断词以V3.9.1真实分析输出为准。")
    ]
}

struct NotReadyScreen: View {
    let name: String
    var body: some View {
        ContentUnavailableView {
            Label("\(name) · 开发中", systemImage: "books.vertical")
        } description: {
            Text("当前只展示已保存真实盘的九宫界面设计，其余领域不假装已经上线。")
        }
        .navigationTitle(name)
    }
}

#Preview {
    WenguaRootView()
}
