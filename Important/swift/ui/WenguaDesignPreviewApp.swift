import SwiftUI
import CryptoKit

// Wengua native iOS app: source-checked deterministic chart plus separate
// domain-gated offline narration. No numeric scores or fabricated new readings.

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
    static let text = Color(uiColor: .label)
    static let secondary = Color(uiColor: .secondaryLabel)
    static let backing = Color(uiColor: .systemGroupedBackground)
    static let surface = Color(uiColor: .secondarySystemGroupedBackground)
    static let line = Color(uiColor: .separator)
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
    var hostedCentreEarthStem: String? = nil // Only used for on-screen Tianqin host.

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
        let chineseName=[1:"一",2:"二",3:"三",4:"四",5:"五",6:"六",7:"七",8:"八",9:"九"][p] ?? String(p)
        return QPalace(id:p,name:cell.gua + chineseName,
                       element:e,branches:cell.branches.joined(),
                       deity:cell.deity ?? "",stars:names.joined(separator:"·"),
                       door:cell.door ?? "",sky:sky,ground:cell.earthStem,
                       stages:life,roles:tags,computed:cell,
                       hostedCentreEarthStem:
                         cell.heavenStars.contains{$0.star=="天禽星"}
                         ? chart.palaces.first(where:{$0.id==5})?.earthStem : nil)
    }
}

// Stable, explicit routing IDs. Only approved offline narration templates may
// be enabled. The other book domains remain visible as roadmap, NOT runnable.
struct QuestionTopic: Identifiable, Equatable {
    let id: String
    let title: String
    let domainTitle: String
    let enabled: Bool
}
struct QuestionDomain: Identifiable {
    let id: String
    let title: String
    let symbol: String
    let topics: [QuestionTopic]
}
enum QuestionCatalog {
    static func domain(_ id:String,_ title:String,_ symbol:String,
                       _ subjects:[String]) -> QuestionDomain {
        QuestionDomain(id:id,title:title,symbol:symbol,
            topics:subjects.enumerated().map { index, name in
                QuestionTopic(id:id+"."+String(index),title:name,
                              domainTitle:title,enabled:false)
            })
    }
    static let domains: [QuestionDomain] = [
        QuestionDomain(id:"health",title:"疾病健康",symbol:"cross.case",
          topics:[
            QuestionTopic(id:"health.severity",title:"病情轻重",domainTitle:"疾病健康",enabled:true),
            QuestionTopic(id:"health.trend",title:"病势发展",domainTitle:"疾病健康",enabled:false),
            QuestionTopic(id:"health.treatment",title:"医药效果",domainTitle:"疾病健康",enabled:false),
            QuestionTopic(id:"health.recovery",title:"病愈应期",domainTitle:"疾病健康",enabled:false)]),
        domain("marriage","恋爱婚姻","heart",["恋爱进展","婚姻关系","复合与分离"]),
        domain("career","工作就业","briefcase",["求职面试","在职发展","升迁调动"]),
        domain("business","经营求财","chart.line.uptrend.xyaxis",["经营项目","投资求财","债务借贷"]),
        domain("education","求学考试","graduationcap",["升学申请","考试结果"]),
        domain("travel","出行出国","airplane",["出行安全","海外发展"]),
        domain("missing","行人走失","figure.walk",["寻找行人","是否归来"]),
        domain("property","钱物丢失","shippingbox",["遗失物品","寻找财物"]),
        domain("lawsuit","官司诉讼","building.columns",["诉讼结果","纠纷处理"]),
        domain("crime","刑事案件","shield.lefthalf.filled",["案件调查"]),
        domain("weather","天时气象","cloud.sun",["天气变化"]),
        domain("sports","体育竞赛","sportscourt",["赛事结果"]),
        domain("geography","地理环境","map",["环境与方位"]),
        domain("life","人生命运","person.crop.circle",["人生机遇"]),
        domain("other","其他杂项","square.grid.2x2",["其它具体事项"])
    ]
    static let defaultTopic = domains[0].topics[0]
}

struct WenguaMark: View {
    var size: CGFloat = 44
    var body: some View {
        ZStack {
            Circle().fill(Color(red:0.12,green:0.22,blue:0.31))
            Circle().stroke(Color(red:0.83,green:0.67,blue:0.33),lineWidth:1.5)
                .padding(size*0.10)
            Circle().stroke(Color(red:0.83,green:0.67,blue:0.33).opacity(0.55),lineWidth:1)
                .padding(size*0.19)
            Text("问").font(.system(size:size*0.40,weight:.semibold,design:.serif))
                .foregroundStyle(Color(red:0.95,green:0.83,blue:0.55))
        }
        .frame(width:size,height:size)
        .accessibilityLabel("问卦")
    }
}

struct WenguaRootView: View {
    @State private var topic: QuestionTopic?
    @State private var entered = false
    @AppStorage("wengua:appearance") private var appearance = "system"

    private var chosenScheme: ColorScheme? {
        appearance=="dark" ? .dark : appearance=="light" ? .light : nil
    }
    var body: some View {
        Group {
            if let topic {
                NavigationStack {
                    ProfessionalChartScreen(topic:topic,changeTopic:{self.topic=nil})
                }
            } else if entered {
                WenguaDomainJourneyScreen(select:{next in topic=next},
                                          goHome:{withAnimation { entered=false }})
            } else {
                WenguaCloudWelcomeScreen {
                    withAnimation(.easeInOut(duration:0.3)) { entered=true }
                }
            }
        }
        .preferredColorScheme(chosenScheme)
    }
}
struct ProfessionalChartScreen: View {
    let topic: QuestionTopic
    let changeTopic: () -> Void
    @State private var chosenPalace: QPalace?
    @State private var showAsk = false
    @State private var nativeChart: WenguaNativeChart?
    @State private var castRelation = "本人"
    @State private var nativeReading: WenguaNativeCustomerReading?
    @State private var selectedReadingTab = 0

    private var palaces: [QPalace] {
        guard let chart=nativeChart else {return []}
        let byId=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        return WenguaNativeCore.branchOrderPalaces.compactMap {
            guard let cell=byId[$0] else {return nil}
            return QPalace.fromNative(cell,chart:chart,relation:castRelation)
        }
    }
    var body: some View {
        GeometryReader { viewport in
        ScrollViewReader { reader in
        ScrollView {
            VStack(alignment:.leading,spacing:0) {
                HStack(spacing:12) {
                    WenguaMark(size:43)
                    VStack(alignment:.leading,spacing:3) {
                        Text("问卦").font(.system(size:22,weight:.semibold,design:.serif))
                        Text(topic.domainTitle + " · " + topic.title)
                            .font(.caption).foregroundStyle(QStyle.secondary)
                    }
                    Spacer()
                    WenguaAppearanceMenu()
                    Button("更换领域",action:changeTopic)
                        .font(.caption).buttonStyle(.bordered)
                }.padding(.horizontal,11).padding(.vertical,7).id("readingTop")

                if let chart=nativeChart {
                    chartHeaderCompact(chart)
                    WenguaReadingTabStrip(selection:$selectedReadingTab)
                        .padding(.horizontal,14)
                        .padding(.vertical,5)
                    if selectedReadingTab == 0 {
                        VStack(alignment:.leading,spacing:6) {
                            HStack {
                                Text("本盘九宫")
                                    .font(.system(size:16,weight:.semibold,design:.serif))
                                Spacer()
                                Text("点击宫位 · 看完整依据")
                                    .font(.system(size:11))
                                    .foregroundStyle(QStyle.secondary)
                            }
                            .padding(.horizontal,13)
                            Text("神看环境 · 星看趋势 · 门看行动 · 天地干看格局；点宫看含义与力量")
                                .font(.system(size:11))
                                .foregroundStyle(QStyle.secondary)
                                .fixedSize(horizontal:false,vertical:true)
                                .padding(.horizontal,13)
                            palaceBoard(tileSide:max(80,min(
                                (viewport.size.width-30)/3,
                                (viewport.size.height-274)/3)))
                            if let reading=nativeReading {
                                WenguaPremiumVerdictCard(reading:reading)
                                    .padding(.horizontal,14)
                                Button {
                                    selectedReadingTab=1
                                } label: {
                                    HStack {
                                        Text("查看专业解盘与完整依据")
                                        Spacer()
                                        Image(systemName:"arrow.right")
                                    }
                                    .font(.system(size:14,weight:.medium))
                                    .foregroundStyle(QStyle.text)
                                    .padding(18)
                                    .background(QStyle.surface,
                                                in:RoundedRectangle(cornerRadius:15))
                                }
                                .buttonStyle(.plain)
                                .padding(.horizontal,14)
                            } else {
                                Text("本次仅有真实九宫，断词未通过原生核验，不能生成专业解卦结论。")
                                    .font(.subheadline).foregroundStyle(QStyle.red)
                                    .padding(16)
                            }
                        }
                        .padding(.bottom,24)
                    } else {
                        VStack(alignment:.leading,spacing:15) {
                            Text("专业解盘")
                                .font(.system(size:26,weight:.semibold,design:.serif))
                            Text("依据本次真实时辰，逐项查看用神、各宫格局、条件限制与应期。")
                                .font(.subheadline).foregroundStyle(QStyle.secondary)
                            if let reading=nativeReading {
                                WenguaNativeCustomerView(reading:reading)
                            } else {
                                Text("本次专业断词校验未完成。")
                                    .foregroundStyle(QStyle.red)
                            }
                            Text("完整九宫事实")
                                .font(.title3.weight(.semibold))
                                .padding(.top,8)
                            ForEach(chart.palaces.sorted(by:{
                                let a=WenguaNativeCore.branchOrderPalaces.firstIndex(of:$0.id) ?? 9
                                let b=WenguaNativeCore.branchOrderPalaces.firstIndex(of:$1.id) ?? 9
                                return a < b
                            })) { palace in
                                NativePalaceEvidenceCard(palace:palace)
                            }
                            WenguaReturnToTop {
                                withAnimation(.easeInOut(duration:0.38)) {
                                    reader.scrollTo("readingTop",anchor:.top)
                                }
                            }
                        }
                        .padding(.horizontal,16)
                        .padding(.bottom,24)
                    }
                } else {
                    VStack(alignment:.leading,spacing:15) {
                        Text("准备起局").font(.system(size:27,weight:.semibold))
                        Text("事项已选："+topic.domainTitle+" / "+topic.title)
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                        Text("无需选择时辰。静心结束后按手机确认时刻起局推演。")
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                        Button("填写问事人与事项") {showAsk=true}
                            .buttonStyle(.borderedProminent)
                            .frame(maxWidth:.infinity)
                        Text("之后需完整静心30秒。仅在成功起盘、保存记录后登记同一事项15天限制。")
                            .font(.caption).foregroundStyle(QStyle.secondary)
                    }
                    .frame(maxWidth:.infinity,alignment:.leading)
                    .padding(22)
                    .background(QStyle.surface,in:RoundedRectangle(cornerRadius:18))
                    .padding(14)
                }
            }
        }
        .background(QStyle.backing)
        .navigationTitle("问卦 · 本局")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item:$chosenPalace) { palace in
            ProfessionalPalaceDetail(palace:palace,
                hourHorse:nativeChart?.hourHorse ?? "",
                hourHorsePalace:nativeChart?.hourHorsePalace ?? 0,
                     monthBranch:String(nativeChart?.pillars.month.suffix(1) ?? ""),
                     identityLabels:WenguaPalaceIdentity.labels(nativeReading,palaceID:palace.id))
                .presentationDetents([.medium,.large])
                .presentationDragIndicator(.visible)
        }
        .sheet(isPresented:$showAsk) {
            CastSetupScreen(topic:topic) { computed,relation,reading in
                nativeChart=computed
                castRelation=relation
                nativeReading=reading
                selectedReadingTab=0
                showAsk=false
            }
        }
        .onAppear {
            // Production: domain > subquestion > verified subject > instant > real
            // native V-next. No FrozenReadingV391 sample path is reachable.
            if nativeChart == nil {showAsk=true}
        }
        }
        }
    }
    private func palaceBoard(tileSide:CGFloat) -> some View {
        LazyVGrid(columns:Array(repeating:GridItem(.fixed(tileSide),spacing:3),count:3),
                  spacing:3) {
            ForEach(palaces) { palace in
                Button {if palace.id != 5 {chosenPalace=palace}} label:{
                    ProfessionalPalaceTile(palace:palace,
                        identityLabels:WenguaPalaceIdentity.labels(nativeReading,palaceID:palace.id))
                        .frame(width:tileSide,height:tileSide)
                }
                    .buttonStyle(.plain)
            }
        }
        .frame(maxWidth:.infinity)
        .padding(.horizontal,9)
    }

    // The first viewport is for the complete 3×3 board, not an oversized
    // header. Full clock, calendar, palace conditions remain in specialist UI.
    private func chartHeaderCompact(_ chart: WenguaNativeChart) -> some View {
        VStack(spacing:7) {
            HStack(spacing:4) {
                Text((chart.bureau.dun=="yang" ? "阳遁 " : "阴遁 ") +
                     String(chart.bureau.ju)+"局")
                    .font(.system(size:13,weight:.semibold,design:.serif))
                Text("· "+chart.solarTerm)
                    .font(.system(size:11))
                    .foregroundStyle(QStyle.secondary)
                Spacer(minLength:0)
                Text(String(chart.iso.replacingOccurrences(of:"T",with:" ").prefix(16)))
                    .font(.system(size:10,weight:.medium,design:.monospaced))
                    .foregroundStyle(QStyle.secondary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.76)
            }
            HStack(spacing:4) {
                pillarMini("年",chart.pillars.year)
                pillarMini("月",chart.pillars.month)
                pillarMini("日",chart.pillars.day)
                pillarMini("时",chart.pillars.hour)
            }
        }
        .padding(.horizontal,11)
        .padding(.vertical,9)
        .background(QStyle.surface,in:RoundedRectangle(cornerRadius:10))
        .padding(.horizontal,11)
    }

    private func pillarMini(_ label:String,_ stem:String) -> some View {
        HStack(spacing:3) {
            Text(label).foregroundStyle(QStyle.secondary)
            HStack(spacing:0) {
                Text(String(stem.prefix(1)))
                    .foregroundStyle(QFive.shade("stem",String(stem.prefix(1))))
                Text(String(stem.suffix(1)))
                    .foregroundStyle(QFive.shade("branch",String(stem.suffix(1))))
            }
            .fontDesign(.monospaced)
        }
        .font(.system(size:12,weight:.medium))
        .frame(maxWidth:.infinity)
        .lineLimit(1)
        .minimumScaleFactor(0.75)
    }
    private func chartHeader(_ chart: WenguaNativeChart) -> some View {
        VStack(alignment:.leading,spacing:15) {
            HStack {
                VStack(alignment:.leading,spacing:4) {
                    Text("起盘时间")
                        .font(.system(size:12,weight:.medium))
                        .foregroundStyle(QStyle.secondary)
                    Text(String(chart.iso.replacingOccurrences(of:"T",with:" ").prefix(16)))
                        .font(.system(size:18,weight:.semibold))
                        .foregroundStyle(QStyle.text)
                }
                Spacer(minLength:5)
                Button("再次问事") { showAsk=true }
                    .font(.system(size:13,weight:.medium))
                    .buttonStyle(.bordered)
            }
            HStack(spacing:5) {
                pillarDisplay("年柱",chart.pillars.year)
                pillarDisplay("月柱",chart.pillars.month)
                pillarDisplay("日柱",chart.pillars.day)
                pillarDisplay("时柱",chart.pillars.hour)
            }
            .padding(.vertical,15)
            .padding(.horizontal,7)
            .background(QStyle.backing,in:RoundedRectangle(cornerRadius:15))
            VStack(alignment:.leading,spacing:12) {
                HStack(alignment:.firstTextBaseline) {
                    Text((chart.bureau.dun == "yang" ? "阳遁 " : "阴遁 ") +
                         String(chart.bureau.ju) + "局")
                        .font(.system(size:23,weight:.semibold))
                        .foregroundStyle(QStyle.text)
                    Spacer()
                    Text(chart.xunShou + "旬")
                        .font(.system(size:14,weight:.medium))
                        .foregroundStyle(QStyle.secondary)
                        .padding(.horizontal,11)
                        .padding(.vertical,7)
                        .background(QStyle.backing,in:RoundedRectangle(cornerRadius:8))
                }
                Rectangle().fill(QStyle.line).frame(height:1)
                HStack(alignment:.top,spacing:9) {
                    factLabel("节气",chart.solarTerm)
                    factLabel("值符",chart.valueStar,kind:"star")
                    factLabel("值使",chart.valueDoor,kind:"door")
                }
                Text("时家转盘 · " + chart.timezone + " · 旬空：" +
                     chart.voidBranches.joined(separator:"、") + " · 时马：" +
                     chart.hourHorse + "（" + String(chart.hourHorsePalace) + "宫）")
                    .font(.system(size:12))
                    .foregroundStyle(QStyle.secondary)
                    .fixedSize(horizontal:false,vertical:true)
            }
            .padding(.horizontal,3)
        }
        .padding(16)
        .background(QStyle.surface,in:RoundedRectangle(cornerRadius:20))
        .padding(.horizontal,12)
        .padding(.top,6)
    }

    private func pillarDisplay(_ title: String, _ value: String) -> some View {
        VStack(spacing:9) {
            Text(title)
                .font(.system(size:11,weight:.medium))
                .foregroundStyle(QStyle.secondary)
            HStack(spacing:1) {
                Text(String(value.prefix(1)))
                    .foregroundStyle(QFive.shade("stem",String(value.prefix(1))))
                Text(String(value.suffix(1)))
                    .foregroundStyle(QFive.shade("branch",String(value.suffix(1))))
            }
            .font(.system(size:26,weight:.semibold))
        }
        .frame(maxWidth:.infinity)
    }

    private func factLabel(_ title:String,_ value:String,kind:String? = nil) -> some View {
        let normalized=value.replacingOccurrences(of:"星",with:"")
        let ink=kind.map{QFive.shade($0,normalized)} ?? QStyle.text
        return VStack(alignment:.leading,spacing:5) {
            Text(title).font(.system(size:11)).foregroundStyle(QStyle.secondary)
            Text(value).font(.system(size:15,weight:.semibold))
                .foregroundStyle(ink)
                .lineLimit(1).minimumScaleFactor(0.82)
        }
        .frame(maxWidth:.infinity,alignment:.leading)
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
         .font(.system(size: 11))
        .lineLimit(2)
        .fixedSize(horizontal:false,vertical:true)
    }
}

// The board keeps high-contrast 神/星/门 glyphs and independently computed
// 天盘/地盘, 空亡/时马/分层入墓 and exact branch life states.
// Compact factual nine-palace typography. Corner icons reflect only facts
// attached to THIS computed physical palace; no style-level divination.
// Nine compact equal-size tiles modelled on the supplied traditional board:
// name/true void/horse, deity+heaven stem, star+earth stem and door.
// Reserved burgundy right rail is ONLY for selected V8 roles, not an
// additional symbol or scoring signal. Detailed restrictions are in the sheet.
struct ProfessionalPalaceTile: View {
    let palace: QPalace
    var identityLabels:[String] = []
    @Environment(\.colorScheme) private var colorScheme
    private var identityInk:Color {
        colorScheme == .dark
            ? Color(red:0.96,green:0.78,blue:0.52)
            : Color(red:0.53,green:0.28,blue:0.23)
    }

    private var rightText:String {
        identityLabels.isEmpty ? "" : identityLabels.joined(separator:"／") + "宫"
    }
    // Keep each actual native star attached to its own sky carrier.
    // Every star contributes its own ordered 81 cell with the same earth stem.
    private var starCarriers:[(String,String)] {
        if let real=palace.computed {
            return real.heavenStars.map{
                ($0.star.replacingOccurrences(of:"星",with:""),$0.carriedStem)
            }
        }
        let starNames=palace.stars.components(separatedBy:"·")
        let stems=palace.sky.components(separatedBy:"·")
        return starNames.enumerated().map { index,name in
            (name,index<stems.count ? stems[index] : "")
        }
    }

    // Presentation-only: identical fixed tracks for one or two actual stars.
    // No V8 source, source-power, score or 81 calculation in this view.
    var body: some View {
        GeometryReader { geo in
            let scale = max(CGFloat(0.80),min(CGFloat(1.12),geo.size.width/114))
            let primary = CGFloat(15) * scale
            let secondary = CGFloat(13) * scale
            let roleWidth:CGFloat = identityLabels.isEmpty ? 0 :
                max(27,min(33,geo.size.width*0.28))
            VStack(alignment:.leading,spacing:0) {
                if palace.id == 5 {
                    Color.clear.frame(maxWidth:.infinity,maxHeight:.infinity)
                } else {
                    palaceHeading.frame(height:25*scale,alignment:.top)
                    HStack(alignment:.center,spacing:2) {
                        glyphColumn(primary:primary,secondary:secondary)
                            .frame(maxWidth:.infinity,maxHeight:.infinity)
                        if !identityLabels.isEmpty {
                            roleColumn.frame(width:roleWidth)
                                .frame(maxHeight:.infinity)
                        }
                    }.frame(maxWidth:.infinity,maxHeight:.infinity)
                }
            }
            .padding(.horizontal,4*scale)
            .padding(.vertical,3*scale)
            .frame(width:geo.size.width,height:geo.size.height,alignment:.topLeading)
        }
        .aspectRatio(1,contentMode:.fit)
         .background(palace.id==5 ? Color.clear : QStyle.surface,
                    in:RoundedRectangle(cornerRadius:4))
        .overlay(RoundedRectangle(cornerRadius:4)
            .stroke(palace.id==5 ? Color.clear : QStyle.line.opacity(0.75),
                    lineWidth:0.8))
        .contentShape(Rectangle())
        .accessibilityLabel(accessibleText)
    }

    private func glyphColumn(primary:CGFloat,secondary:CGFloat)->some View {
        VStack(alignment:.leading,spacing:0) {
            symbolRow(palace.deity,kind:"deity",stem:"",
                      primary:primary,secondary:secondary)
            Spacer(minLength:0)
            starLine(primary:primary)
            Spacer(minLength:0)
            skyStemLine(size:secondary)
            earthStemLine(size:secondary)
            Spacer(minLength:0)
            symbolRow(palace.door,kind:"door",stem:"",
                      primary:primary,secondary:secondary)
        }.frame(maxWidth:.infinity,maxHeight:.infinity,alignment:.leading)
    }

    private func starLine(primary:CGFloat)->some View {
        HStack(spacing:0) {
            ForEach(0..<starCarriers.count,id:\.self) { index in
                let pair=starCarriers[index]
                if index>0 {Text("／").foregroundStyle(QStyle.secondary)}
                Text(index==0 ? pair.0 : (pair.0=="天禽" ? "禽" : pair.0))
                    .foregroundStyle(QFive.shade("star",pair.0))
            }
        }
        .font(.system(size:primary,weight:.semibold,design:.serif))
        .lineLimit(1).minimumScaleFactor(0.75)
        .frame(maxWidth:.infinity,alignment:.leading)
    }

    private func skyStemLine(size:CGFloat)->some View {
        HStack(spacing:2) {
            Text("天").font(.system(size:10)).foregroundStyle(QStyle.secondary)
            // A fixed-width carrier track: 丁 and 戊 share ONE row. 81 source
            // ownership still follows the real native star->stem mapping.
            HStack(spacing:0) {
                ForEach(Array(starCarriers.reversed().enumerated()),id:\.offset) { pair in
                    Text(pair.element.1)
                        .foregroundStyle(QFive.shade("stem",pair.element.1))
                        .frame(maxWidth:.infinity)
                }
            }.frame(width:38)
        }
        .font(.system(size:size,weight:.semibold,design:.monospaced))
        .lineLimit(1)
        .frame(maxWidth:.infinity,alignment:.center)
        .accessibilityLabel("天盘星干："+starCarriers.map{$0.0+"携"+$0.1}.joined(separator:"、"))
    }

    private func earthStemLine(size:CGFloat)->some View {
        HStack(spacing:2) {
            Text("地").font(.system(size:10)).foregroundStyle(QStyle.secondary)
            HStack(spacing:0) {
                if let centre=palace.hostedCentreEarthStem {
                    Text(centre).foregroundStyle(QFive.shade("stem",centre))
                        .frame(maxWidth:.infinity)
                }
                Text(palace.ground).foregroundStyle(QFive.shade("stem",palace.ground))
                    .frame(maxWidth:.infinity)
            }.frame(width:38)
        }
        .font(.system(size:size,weight:.semibold,design:.monospaced))
        .frame(maxWidth:.infinity,alignment:.center)
    }

    private var roleColumn:some View {
        VStack(spacing:4) {
            ForEach(Array(identityLabels.enumerated()),id:\.offset) { entry in
                Text(entry.element)
                    .font(.system(size:9,weight:.semibold,design:.serif))
                    .foregroundStyle(identityInk)
                    .lineLimit(2).minimumScaleFactor(0.74)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth:.infinity)
            }
        }
        .frame(maxHeight:.infinity,alignment:.center)
        .accessibilityLabel("本宫用神："+rightText)
    }

    private var accessibleText:String {
        if palace.id == 5 {return "中五宫画面留空，地盘干随天禽寄宫展示"}
        let facts=[palace.name,"八神"+palace.deity,"九星"+palace.stars,
                   "八门"+palace.door,"天盘"+palace.sky,"地盘"+palace.ground]
        return (facts + (identityLabels.isEmpty ? [] : ["用神："+rightText]) +
                QFive.void(palace).map{$0+"空"} +
                (QFive.horse(palace).map{["驿马"+$0]} ?? []))
                .joined(separator:"，")
    }

    private var palaceHeading:some View {
        ZStack {
            Text(palace.name+"宫")
                .font(.system(size:16,weight:.bold,design:.serif))
                .foregroundStyle(QFive.palette[palace.element] ?? QStyle.text)
                .lineLimit(1).minimumScaleFactor(0.82)
                .frame(maxWidth:.infinity,alignment:.center)
            HStack(spacing:2) {
                Spacer(minLength:0)
                if !QFive.void(palace).isEmpty {
                    Circle().stroke(identityInk,lineWidth:1.5)
                        .frame(width:9,height:9)
                        .accessibilityLabel("逢空："+QFive.void(palace).joined(separator:"、"))
                }
                if let horse=QFive.horse(palace) {
                    Text("🐎").font(.system(size:12))
                        .accessibilityLabel("驿马："+horse)
                }
            }
        }.frame(maxWidth:.infinity)
    }

    private func symbolRow(_ value:String,kind:String,stem:String,
                           primary:CGFloat,secondary:CGFloat,
                           display:String?=nil)->some View {
        HStack(alignment:.firstTextBaseline,spacing:2) {
            Text(display ?? value)
                .foregroundStyle(QFive.shade(kind,value))
                .font(.system(size:primary,weight:.semibold,design:.serif))
            .lineLimit(1)
            .minimumScaleFactor(0.68)
            Spacer(minLength:0)
            if !stem.isEmpty {
                HStack(spacing:0) {
                    ForEach(Array(stem.components(separatedBy:"·").enumerated()),
                            id:\.offset) { part in
                        Text(part.element)
                            .foregroundStyle(QFive.shade("stem",part.element))
                    }
                }
                .font(.system(size:secondary,weight:.medium))
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            }
        }
        .frame(maxWidth:.infinity,alignment:.leading)
    }
}

struct ProfessionalPalaceDetail: View {
    let palace: QPalace
    let hourHorse: String
    let hourHorsePalace: Int
    var monthBranch: String = ""
    var identityLabels: [String] = []
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
        let identity = identityLabels.isEmpty
            ? "本宫未担当本次问事用神"
            : "本宫担当：" + identityLabels.joined(separator:"／") + "宫"
        let emptiness = QFive.void(palace).isEmpty
            ? "" : "；旬空：" + QFive.void(palace).joined(separator:"、")
        return palace.name + "宫，五行属" + palace.element + "，宫支" + palace.branches +
            "。" + identity + emptiness + "。"
    }
    private var statusTags: [String] {
        identityLabels + QFive.void(palace).map{$0 + "空"} +
            (palace.computed == nil ? ["测试盘"] : ["本机实算"])
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 15) {
                headerBlock
                tagBlock
                factsBlock
                Text("传统古籍宫象展示。完整专题判断请查看「专业解盘」，不以宫位外观代替断案依据。")
                    .font(.footnote)
                    .foregroundStyle(QStyle.secondary)
            }
            .padding(20)
        }
        .background(QStyle.backing)
    }
    private var headerBlock: some View {
        VStack(alignment: .center, spacing: 4) {
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
            factCard("宫位属性 · 用神角色",text:roleDescription)
            WenguaPalacePowerDetail(palace:palace,monthBranch:monthBranch)
            lifeDetailCard
            factCard("空亡 · 驿马 · 入墓",text:conditionDescription)
        }
    }
    private var lifeDetailCard: some View {
        VStack(alignment: .center, spacing: 10) {
            Text("十二长生 · 天盘干／地盘干分别实算")
                .font(.headline).frame(maxWidth:.infinity,alignment:.center)
            ForEach(palace.lifeRows) { line in
                VStack(alignment: .center, spacing: 4) {
                    Text(line.plane + "盘干：" + line.stem)
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
        .frame(maxWidth: .infinity, alignment: .center)
        .padding(15)
        .background(QStyle.surface, in: RoundedRectangle(cornerRadius:15))
    }
    private func detailTag(_ label: String) -> some View {
        Text(label)
            .font(.caption2)
            .padding(.horizontal, 10).padding(.vertical, 7)
            .foregroundStyle(QStyle.blue)
            .background(Color(red: 0.91, green: 0.95, blue: 1.0), in: Capsule())
    }

    private func factCard(_ title: String, text: String) -> some View {
        VStack(alignment: .center, spacing: 9) {
            Text(title).font(.headline)
            Text(text).font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(QStyle.secondary).fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .center)
        .padding(15)
        .background(QStyle.surface, in: RoundedRectangle(cornerRadius: 15))
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

struct LocalNativeCase: Codable {
    let topicID: String
    let issueFingerprint: String
    let relation: String
    let optionalBirthYear: Int?
    let course: String?
    let completedAt: Date
    let chart: WenguaNativeChart
    let reading: WenguaNativeCustomerReading?
}

struct CastSetupScreen: View {
    let topic: QuestionTopic
    let onNativeCast: (WenguaNativeChart, String, WenguaNativeCustomerReading) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var subject = "本人"
    @State private var inquiryContext = "direct_proxy"
    @State private var patientSex = "unspecified"
    @State private var birthOrder = "unspecified"
    @State private var patientBirthGanzhi = ""
    @State private var subjectName = ""
    @State private var birthYear = ""
    @State private var question = ""
    @State private var duration = "未说明"
    @State private var phase = 0
    @State private var calmEnds: Date?
    @State private var validationMessage = ""
    private let relations = WenguaNativeReadingRouter.supportedRelations

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 17) {
                    if phase == 0 {
                        Text(topic.domainTitle + " · " + topic.title)
                            .font(.system(size: 28, weight: .medium))
                        Text("同一件具体事情，15天内只起一次。")
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                        Group {
                            Text("具体事项（必填）").font(.headline)
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
                            Picker("病人性别（可选）",selection:$patientSex) {
                                Text("未说明").tag("unspecified")
                                Text("男").tag("male")
                                Text("女").tag("female")
                            }.pickerStyle(.menu)
                            if ["儿子","女儿","孩子","侄子"].contains(subject) {
                                Picker("出生排行（可选）",selection:$birthOrder) {
                                    Text("未说明").tag("unspecified")
                                    Text("长").tag("eldest")
                                    Text("中").tag("middle")
                                    Text("幼").tag("youngest")
                                }.pickerStyle(.menu)
                            }
                            TextField("出生年命干支（选填，如辛酉）",text:$patientBirthGanzhi)
                                .textInputAutocapitalization(.never)
                            Text("请务必准确选择与测算人的关系。本模型严格遵循古籍用神规则，关系的错位将直接影响推演结果的准确性。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                            Picker("病程（可选）", selection: $duration) {
                                ForEach(["未说明", "新病", "久病"], id: \.self) { Text($0) }
                            }
                            Text("不提供手选时辰。完成30秒静心后点击确认起局，现场采集手机真实时刻及 IANA 时区。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                        }
                        .padding(12)
                        .background(QStyle.surface, in: RoundedRectangle(cornerRadius: 14))
                        VStack(alignment: .leading, spacing: 8) {
                            Text("一事一占 · 尊重事实").font(.headline)
                            Text("静下心想这件事30秒。心诚则灵，尊重事实。同一件事15天内只完成一次真实起局。仅凭本机记录无法彻底识别换说法或换设备的同一件事。")
                                .font(.subheadline)
                        }
                        .padding(15)
                        .background(QStyle.surface,
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
                                    Button("确认起局 · 逻辑推演") { completeNativeCast() }
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
                        Text("本模型基于古籍规则算法进行推演计算，无人工主观干预，严密还原事情发展之底层逻辑。")
                            .font(.footnote).foregroundStyle(QStyle.secondary)
                    }
                }
                .padding(18)
            }
            .background(QStyle.backing)
            .navigationTitle(phase == 0 ? "问事与人物" : "静心三十秒")
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
        guard topic.enabled && topic.id == "health.severity" else {
            validationMessage="该领域的断案模板尚未接入，不能套用其它领域模板。"
            return
        }
        guard let calmEnds, Date() >= calmEnds else {
            validationMessage="必须完成完整30秒静心后才能起局。"
            return
        }
        let key=QIssuePolicy.signature(topic:topic.id,relation:subject,
                                       subject:subjectName,question:question)
        if let next=QIssuePolicy.nextPermitted(key) {
            validationMessage="同一件事未满15天；下次允许："+next.formatted()
            return
        }
        do {
            let finalInstant=Date()
            let localZone=TimeZone.current.identifier
            let result=try WenguaNativeCore.compute(at:finalInstant,timezone:localZone)
            // A successful chart is not enough: fail before issuing the 15-day
            // receipt unless the selected native domain and role can read its
            // true local evidence from the bundled, user-editable template.
            let context=WenguaNativeInquiry(
                relationship:subject,
                context:subject=="本人" ? "direct_self" : inquiryContext,
                patientSex:patientSex=="unspecified" ? nil : patientSex,
                birthOrder:birthOrder=="unspecified" ? nil : birthOrder,
                patientBirthGanzhi:patientBirthGanzhi.trimmingCharacters(
                    in:.whitespacesAndNewlines).isEmpty ? nil :
                    patientBirthGanzhi.trimmingCharacters(in:.whitespacesAndNewlines))
            let reading=try WenguaNativeReadingRouter.compose(
                chart:result,topicID:topic.id,relationship:subject,
                inquiry:context)
            // Persistent case receipt is ONLY original board/clock facts and
            // hashed issue ID. User's raw private question is NOT stored here.
            let record=LocalNativeCase(topicID:topic.id,issueFingerprint:key,relation:subject,
                                       optionalBirthYear:Int(birthYear),
                                       course:duration=="未说明" ? nil : duration,
                                       completedAt:Date(),chart:result,reading:reading)
            let encoded=try JSONEncoder().encode(record)
            let recordId="wengua:nativecase:"+UUID().uuidString
            UserDefaults.standard.set(encoded,forKey:recordId)
            guard UserDefaults.standard.data(forKey:recordId)==encoded else {
                throw WenguaCastError.invalidChart
            }
            QIssuePolicy.commitRealCompletedCast(key,validated:true,stored:true)
            onNativeCast(result,subject,reading)
            dismiss()
        } catch {
            validationMessage="本次未起局成功，也不会登记15天限制："+error.localizedDescription
        }
    }

    private func tryStartRitual() {
        guard topic.enabled && topic.id == "health.severity" else {
            validationMessage="请选择有实际计算支持的细分事项。"
            return
        }
        let cleanedYear=birthYear.trimmingCharacters(in:.whitespacesAndNewlines)
        if !cleanedYear.isEmpty {
            guard let year=Int(cleanedYear), (1850...2150).contains(year) else {
                validationMessage="出生年份需是有效公历年份（1850–2150），或留空。"
                return
            }
        }
        let supplied=patientBirthGanzhi.trimmingCharacters(in:.whitespacesAndNewlines)
        if !supplied.isEmpty && !WenguaNativeActorSource.validatedGanzhi(supplied) {
            validationMessage="出生年命须填写完整六十甲子干支，例如辛酉；不确定可留空。"
            return
        }
        if (subject=="配偶" || subject=="父母") && patientSex=="unspecified" &&
           inquiryContext != "event_news" {
            validationMessage="此人物关系必须先明确病人性别，以决定真正的用神。"
            return
        }
        let normalized = question.filter { !$0.isWhitespace && !$0.isPunctuation }
        guard normalized.count >= 4 else {
            validationMessage = "请先明确至少四个字的一件具体事情。"
            return
        }
        let key = QIssuePolicy.signature(topic: topic.id,
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
    let nativeReading: WenguaNativeCustomerReading?
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTab = 0
    @State private var chosenPalace: QPalace?

    private var board: [QPalace] {
        guard let chart=nativeChart else {return []}
        let byId=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        return WenguaNativeCore.branchOrderPalaces.compactMap {
            guard let cell=byId[$0] else{return nil}
            return QPalace.fromNative(cell,chart:chart,
                                     relation:nativeReading?.relationship ?? "")
        }
    }
    var body: some View {
        NavigationStack {
            ScrollViewReader { reader in
            ScrollView {
                VStack(alignment:.leading,spacing:16) {
                    HStack {
                        WenguaMark(size:40)
                        VStack(alignment:.leading,spacing:3) {
                            Text("问卦 · 本次记录")
                                .font(.system(size:23,weight:.semibold,design:.serif))
                            if let chart=nativeChart {
                                HStack(spacing:6) {
                                    ForEach(0..<4,id:\.self) { index in
                                        let pillars=[chart.pillars.year,chart.pillars.month,
                                                     chart.pillars.day,chart.pillars.hour]
                                        let value=pillars[index]
                                        HStack(spacing:0) {
                                            Text(String(value.prefix(1)))
                                                .foregroundStyle(QFive.shade("stem",String(value.prefix(1))))
                                            Text(String(value.suffix(1)))
                                                .foregroundStyle(QFive.shade("branch",String(value.suffix(1))))
                                        }
                                        .font(.system(size:14,weight:.semibold,design:.monospaced))
                                    }
                                    Text(chart.solarTerm)
                                        .font(.caption).foregroundStyle(QStyle.secondary)
                                }
                            }
                        }
                    }
                    WenguaReadingTabStrip(selection:$selectedTab)
                        .id("readingTop")
                    if selectedTab == 0 {
                        if !board.isEmpty {
                            Text("本盘九宫")
                                .font(.title3.weight(.semibold))
                            Text("神看环境 · 星看趋势 · 门看行动 · 天地干看格局；点宫可查看解释")
                                .font(.caption)
                                .foregroundStyle(QStyle.secondary)
                            LazyVGrid(columns:Array(repeating:GridItem(.flexible(),spacing:3),count:3),
                                      spacing:3) {
                                ForEach(board) { palace in
                                    Button {if palace.id != 5 {chosenPalace=palace}} label:{
                                        ProfessionalPalaceTile(palace:palace,
                                            identityLabels:WenguaPalaceIdentity.labels(nativeReading,palaceID:palace.id))
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                        if let reading=nativeReading {
                            WenguaPremiumVerdictCard(reading:reading)
                        } else {
                            Text("历史盘的断词未能核验；不使用其它时辰代替。")
                                .foregroundStyle(QStyle.red)
                        }
                    } else {
                        if let reading=nativeReading {
                            WenguaNativeCustomerView(reading:reading)
                        } else {
                            Text("本盘无可用专业断词。").foregroundStyle(QStyle.red)
                        }
                        if let chart=nativeChart {
                            Text("完整九宫事实").font(.title3.weight(.semibold))
                            ForEach(chart.palaces.sorted(by:{
                                let a=WenguaNativeCore.branchOrderPalaces.firstIndex(of:$0.id) ?? 9
                                let b=WenguaNativeCore.branchOrderPalaces.firstIndex(of:$1.id) ?? 9
                                return a < b
                            })) { palace in
                                NativePalaceEvidenceCard(palace:palace)
                            }
                        }
                        WenguaReturnToTop {
                            withAnimation(.easeInOut(duration:0.38)) {
                                reader.scrollTo("readingTop",anchor:.top)
                            }
                        }
                    }
                    Text("仅供传统文化与古籍象意研究，不提供医学诊断、预后或治疗建议。")
                        .font(.caption).foregroundStyle(QStyle.secondary)
                }
                .padding(16)
            }
            .background(QStyle.backing)
            .navigationTitle("专业解卦")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement:.topBarTrailing) {
                    Button("关闭") {dismiss()}
                }
            }
            .sheet(item:$chosenPalace) { palace in
                ProfessionalPalaceDetail(palace:palace,
                     hourHorse:nativeChart?.hourHorse ?? "",
                     hourHorsePalace:nativeChart?.hourHorsePalace ?? 0,
                     monthBranch:String(nativeChart?.pillars.month.suffix(1) ?? ""),
                     identityLabels:WenguaPalaceIdentity.labels(nativeReading,palaceID:palace.id))
                    .presentationDetents([.medium,.large])
            }
            }
        }
    }
}

// Extracted from TraditionalReadingPreview to avoid a single giant SwiftUI
// result-builder expression exhausting the Xcode type-checker.
// No score/prognosis is derived here: only real carried-stem ordered 81 facts.
private struct WenguaHealthFormationSection: View {
    let chart: WenguaNativeChart

    var body: some View {
        Group {
            if let blocks = try? WenguaHealthTemplateBridge.fromBundle(chart:chart) {
                formationList(blocks)
            } else {
                Text("本机81格或断词模板校验失败；拒绝显示伪造的格局与合断。")
                    .foregroundStyle(QStyle.red)
            }
        }
    }

    private func formationList(_ blocks: [WenguaHealthFormationBlock]) -> some View {
        VStack(alignment:.leading,spacing:12) {
            Text("本盘81天地格 · 原文依据")
                .font(.title3.weight(.semibold))
            Text("本节仅列本盘真实81天地格出处；完整用神、能量及吉凶结论请查看本次问事解读。")
                .font(.caption).foregroundStyle(QStyle.secondary)
            ForEach(blocks) { block in
                formationCard(block)
            }
        }
    }

    private func formationCard(_ block: WenguaHealthFormationBlock) -> some View {
        VStack(alignment:.leading,spacing:7) {
            Text(block.palace).font(.headline)
            ForEach(Array(block.sentences.enumerated()),id: \.offset) { pair in
                Text(pair.element)
                    .font(.subheadline)
                    .textSelection(.enabled)
                    .fixedSize(horizontal:false,vertical:true)
            }
        }
        .padding(14)
        .frame(maxWidth:.infinity,alignment:.leading)
        .background(QStyle.surface,in:RoundedRectangle(cornerRadius:12))
    }
}

// Separate fact report: fully expanded authentic offline nine-palace facts,
// NOT a substitute for V3.9.1 domain reasoning or a clinical prognosis.
struct NativePalaceEvidenceCard: View {
    let palace: WenguaNativePalace
    private var stageText: String {
        palace.heavenStars.map { star in
            star.star + "携" + star.carriedStem + "：" +
            star.stages.map{$0.branch+$0.stage}.joined(separator:"、")
        }.joined(separator:"；")
    }
    private var groundStages: String {
        palace.earthStem + "：" +
            palace.earthStages.map{$0.branch+$0.stage}.joined(separator:"、")
    }
    private var conditions: String {
        let blanks: [String] = palace.voidBranches.map { branch in branch + "空" }
        let horseMarkers: [String] = palace.horseBranch.map { ["马" + $0] } ?? []
        let tombMarkers: [String] = palace.tombs.map { item in
            let plane = item.plane == "天盘" ? "天" : "地"
            return [plane,item.stem,item.branch,"墓"].joined()
        }
        let markers: [String] = blanks + horseMarkers + tombMarkers
        return markers.isEmpty ? "无已核定的空、马、墓标记" : markers.joined(separator:"、")
    }
    var body: some View {
        VStack(alignment:.leading,spacing:9) {
            HStack {
                Text(palace.gua + String(palace.id) + "宫")
                    .font(.headline)
                Spacer()
                Text(palace.branches.joined(separator:"、"))
                    .font(.caption).foregroundStyle(QStyle.secondary)
            }
            if palace.id == 5 {
                Text("地盘干：" + palace.earthStem + "。中五不伪造普通星、门、神。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
            } else {
                Text("神：" + (palace.deity ?? "未核定") +
                     "　门：" + (palace.door ?? "未核定"))
                    .font(.subheadline)
                Text("天盘干：" + stageText)
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Text("地盘干：" + groundStages)
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Text(conditions)
                    .font(.caption).foregroundStyle(QStyle.blue)
            }
        }
        .frame(maxWidth:.infinity,alignment:.leading)
        .padding(16)
        .background(QStyle.surface,in:RoundedRectangle(cornerRadius:14))
    }
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
