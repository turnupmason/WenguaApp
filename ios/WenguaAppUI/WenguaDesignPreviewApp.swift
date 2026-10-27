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
        let chineseName=[1:"一",2:"二",3:"三",4:"四",5:"五",6:"六",7:"七",8:"八",9:"九"][p] ?? String(p)
        return QPalace(id:p,name:cell.gua + chineseName,
                       element:e,branches:cell.branches.joined(),
                       deity:cell.deity ?? "",stars:names.joined(separator:"·"),
                       door:cell.door ?? "",sky:sky,ground:cell.earthStem,
                       stages:life,roles:tags,computed:cell)
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
    var body: some View {
        if let topic {
            NavigationStack {
                ProfessionalChartScreen(topic:topic,changeTopic:{self.topic=nil})
            }
        } else {
            QuestionEntryScreen { next in topic=next }
        }
    }
}
struct QuestionEntryScreen: View {
    let select: (QuestionTopic) -> Void
    @State private var chosenDomain: String?
    @State private var chosenTopic: String?
    private var domain: QuestionDomain? {
        QuestionCatalog.domains.first(where:{$0.id==chosenDomain})
    }
    private var selected: QuestionTopic? {
        domain?.topics.first(where:{$0.id==chosenTopic})
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment:.leading,spacing:17) {
                    HStack(spacing:14) {
                        WenguaMark(size:62)
                        VStack(alignment:.leading,spacing:3) {
                            Text("问卦").font(.system(size:32,weight:.semibold,design:.serif))
                            Text("心诚则灵 · 尊重事实")
                                .font(.subheadline).foregroundStyle(QStyle.secondary)
                        }
                        Spacer(minLength:0)
                        NavigationLink {
                            WenguaLocalHistoryView()
                        } label: {
                            Label("记录",systemImage:"clock.arrow.circlepath")
                                .font(.subheadline)
                        }
                    }
                    .padding(.vertical,24)
                    Text(chosenDomain==nil ? "先选择问事领域" : "再选择具体事项")
                        .font(.system(size:24,weight:.semibold))
                    Text("选定领域和细分事项后，才会调用对应的离线排盘与断案模板。未完成的模板不会冒充可用。")
                        .font(.subheadline).foregroundStyle(QStyle.secondary)
                    if let domain {
                        Button("〈 返回领域") {chosenDomain=nil;chosenTopic=nil}
                            .font(.subheadline).foregroundStyle(QStyle.blue)
                        Text(domain.title).font(.headline)
                        ForEach(domain.topics) { item in
                            Button {chosenTopic=item.id} label: {
                                HStack {
                                    Image(systemName:chosenTopic==item.id ?
                                          "largecircle.fill.circle":"circle")
                                        .foregroundStyle(QStyle.blue)
                                    VStack(alignment:.leading,spacing:3) {
                                        Text(item.title).foregroundStyle(QStyle.text)
                                        Text(item.enabled ? "九宫离线实算已接入 · 完整断词仍在移植" :
                                                "本专题的独立断案规则尚未移植")
                                            .font(.caption).foregroundStyle(QStyle.secondary)
                                    }
                                    Spacer()
                                }
                                .padding(14)
                                .background(.white,in:RoundedRectangle(cornerRadius:14))
                            }
                            .buttonStyle(.plain)
                        }
                        if let selected {
                            Button(selected.enabled ? "继续设置时间与当事人" : "此项规则开发中") {
                                if selected.enabled {select(selected)}
                            }
                            .buttonStyle(.borderedProminent)
                            .disabled(!selected.enabled)
                            .frame(maxWidth:.infinity)
                            Text(selected.enabled ?
                                 "自动起盘与文字断案是独立阶段；当前上线前仍须完成新盘全文断词模块。" :
                                 "不调用疾病轻重模板代替其它问事。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                        }
                    } else {
                        LazyVGrid(columns:[GridItem(.flexible()),GridItem(.flexible())],spacing:11) {
                            ForEach(QuestionCatalog.domains) { item in
                                Button {
                                    chosenDomain=item.id
                                    chosenTopic=nil
                                } label: {
                                    VStack(alignment:.leading,spacing:11) {
                                        Image(systemName:item.symbol)
                                            .font(.system(size:24))
                                            .foregroundStyle(QStyle.blue)
                                        Text(item.title).font(.headline)
                                            .foregroundStyle(QStyle.text)
                                        Text(item.id=="health" ? "已接入起盘" : "规划中")
                                            .font(.caption).foregroundStyle(QStyle.secondary)
                                    }
                                    .frame(maxWidth:.infinity,minHeight:110,alignment:.leading)
                                    .padding(13)
                                    .background(.white,in:RoundedRectangle(cornerRadius:15))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                }
                .padding(18)
            }
            .background(QStyle.backing)
            .navigationTitle("问卦")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// The frozen V3.9.1 file remains in Git history for QA but is NOT
// bundled into the customer application and never appears as a reading.
private struct WenguaVNextInlineReading: View {
    let reading:WenguaNativeCustomerReading
    let details:()->Void
    var body:some View {
        VStack(alignment:.leading,spacing:12) {
            HStack {
                Text("本次 V-next 断案")
                    .font(.title2.weight(.semibold))
                Spacer()
                Text("离线实算").font(.caption).foregroundStyle(QStyle.green)
            }
            WenguaNativeCustomerView(reading:reading)
            Button("查看独立断案详情与九宫事实") {details()}
                .buttonStyle(.bordered)
                .frame(maxWidth:.infinity)
        }
        .padding(15)
        .background(.white,in:RoundedRectangle(cornerRadius:16))
        .padding(12)
    }
}

struct ProfessionalChartScreen: View {
    let topic: QuestionTopic
    let changeTopic: () -> Void
    @State private var chosenPalace: QPalace?
    @State private var showAsk = false
    @State private var showReading = false
    @State private var nativeChart: WenguaNativeChart?
    @State private var castRelation = "本人"
    @State private var nativeReading: WenguaNativeCustomerReading?

    private var palaces: [QPalace] {
        guard let chart=nativeChart else {return []}
        let byId=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        return WenguaNativeCore.branchOrderPalaces.compactMap {
            guard let cell=byId[$0] else {return nil}
            return QPalace.fromNative(cell,chart:chart,relation:castRelation)
        }
    }
    var body: some View {
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
                    Button("更换领域",action:changeTopic)
                        .font(.caption).buttonStyle(.bordered)
                }.padding(14)

                if let chart=nativeChart {
                    chartHeader(chart)
                    palaceBoard
                    HStack {
                        Text("点击九宫查看五行、十二长生、空马墓与出处条件")
                        Spacer()
                    }.font(.caption2).foregroundStyle(QStyle.secondary).padding(12)

                    if let reading=nativeReading {
                        WenguaVNextInlineReading(reading:reading,
                                                details:{showReading=true})
                    } else {
                        Text("本次只有真实九宫事实；V-next 断案尚未完成，不使用历史样本冒充。")
                            .font(.caption).foregroundStyle(QStyle.red)
                            .padding(14)
                    }
                } else {
                    VStack(alignment:.leading,spacing:15) {
                        Text("准备起局").font(.system(size:27,weight:.semibold))
                        Text("事项已选："+topic.domainTitle+" / "+topic.title)
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                        Text("你可以选择按确认时刻起局，或者手动指定年月日时分。两种模式都由同一套本机离线算法计算九宫。")
                            .font(.subheadline).foregroundStyle(QStyle.secondary)
                        Button("设置问事与时间") {showAsk=true}
                            .buttonStyle(.borderedProminent)
                            .frame(maxWidth:.infinity)
                        Text("之后需完整静心30秒。仅在成功起盘、保存记录后登记同一事项15天限制。")
                            .font(.caption).foregroundStyle(QStyle.secondary)
                    }
                    .frame(maxWidth:.infinity,alignment:.leading)
                    .padding(22)
                    .background(.white,in:RoundedRectangle(cornerRadius:18))
                    .padding(14)
                }
            }
        }
        .background(QStyle.backing)
        .navigationTitle("局式")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item:$chosenPalace) { palace in
            ProfessionalPalaceDetail(palace:palace,
                hourHorse:nativeChart?.hourHorse ?? "",
                hourHorsePalace:nativeChart?.hourHorsePalace ?? 0)
                .presentationDetents([.medium,.large])
                .presentationDragIndicator(.visible)
        }
        .sheet(isPresented:$showAsk) {
            CastSetupScreen(topic:topic) { computed,relation,reading in
                nativeChart=computed
                castRelation=relation
                nativeReading=reading
                showAsk=false
            }
        }
        .sheet(isPresented:$showReading) {
            TraditionalReadingPreview(nativeChart:nativeChart,sampleIndex:-1,nativeReading:nativeReading)
        }
        .onAppear {
            // Production: domain > subquestion > verified subject > instant > real
            // native V-next. No FrozenReadingV391 sample path is reachable.
            if nativeChart == nil {showAsk=true}
        }
    }
    private var palaceBoard: some View {
        LazyVGrid(columns:Array(repeating:GridItem(.flexible(),spacing:1),count:3),spacing:1) {
            ForEach(palaces) { palace in
                Button {chosenPalace=palace} label:{ProfessionalPalaceTile(palace:palace)}
                    .buttonStyle(.plain)
            }
        }
        .padding(.vertical,1)
        .background(QStyle.line)
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
                Button("选择时间") { showAsk=true }
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
        .background(.white)
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
struct ProfessionalPalaceTile: View {
    let palace: QPalace
    private let labelColor = Color(red:0.49,green:0.56,blue:0.63)

    var body: some View {
        VStack(alignment:.leading,spacing:7) {
            palaceHeading
            if palace.id == 5 {
                centralPalace
            } else {
                symbolsSection
                stemsSection
                statusSection
                Spacer(minLength:3)
                lifecycleSection
            }
            Text("宫位详解 ›")
                .font(.system(size:10))
                .foregroundStyle(QStyle.blue)
                .frame(maxWidth:.infinity,alignment:.trailing)
        }
        .padding(.horizontal,6)
        .padding(.vertical,11)
        .frame(maxWidth:.infinity,minHeight:274,alignment:.topLeading)
        .background(.white)
        .contentShape(Rectangle())
        .accessibilityLabel(accessibleText)
    }

    private var accessibleText: String {
        if palace.id == 5 {return "中五宫，按原书独立处理"}
        return [palace.name,"八神" + palace.deity,"九星" + palace.stars,
                "八门" + palace.door,"天盘" + palace.sky,"地盘" + palace.ground,
                palace.stages].joined(separator:"，")
    }
    private var palaceHeading: some View {
        HStack(alignment:.firstTextBaseline,spacing:3) {
            Text(palace.name).font(.system(size:13,weight:.bold))
                .foregroundStyle(QFive.palette[palace.element] ?? QStyle.text)
            Spacer(minLength:0)
            HStack(spacing:1) {
                ForEach(Array(palace.branches.map{String($0)}.enumerated()),id: \.offset) { part in
                    Text(part.element).foregroundStyle(QFive.shade("branch",part.element))
                }
            }
            .font(.system(size:10))
        }
    }
    private var centralPalace: some View {
        VStack(alignment:.center,spacing:10) {
            Spacer(minLength:24)
            Text("中五").font(.system(size:29,weight:.medium))
                .foregroundStyle(QStyle.secondary)
            if !palace.ground.isEmpty {
                Text("地盘　" + palace.ground)
                    .font(.system(size:14))
                    .foregroundStyle(QFive.shade("stem",palace.ground))
            }
            Text("神、门、星另论").font(.system(size:11)).foregroundStyle(labelColor)
            Spacer(minLength:18)
        }
        .frame(maxWidth:.infinity)
    }
    private var symbolsSection: some View {
        VStack(alignment:.leading,spacing:7) {
            namedSymbol("神",palace.deity,kind:"deity")
            multiSymbol("星",palace.stars,kind:"star")
            namedSymbol("门",palace.door,kind:"door")
        }
    }
    private var stemsSection: some View {
        VStack(spacing:5) {
            Rectangle().fill(QStyle.line.opacity(0.65)).frame(height:1)
            HStack(alignment:.firstTextBaseline,spacing:3) {
                stemLine("天",palace.sky)
                Spacer(minLength:0)
                stemLine("地",palace.ground)
            }
        }
    }
    private var statusSection: some View {
        VStack(alignment:.leading,spacing:3) {
            ForEach(palace.roles,id: \.self) { role in
                Text(role).foregroundStyle(QStyle.blue)
            }
            ForEach(QFive.void(palace),id: \.self) { branch in
                Text(branch + "空").foregroundStyle(QFive.shade("branch",branch))
            }
            if let horse=QFive.horse(palace) {
                Text("马" + horse).foregroundStyle(QFive.shade("branch",horse))
            }
            ForEach(QFive.heavenTombs(palace) + QFive.earthTombs(palace),id: \.self) { label in
                Text(label).foregroundStyle(
                    QFive.shade("stem",String(label.dropFirst().prefix(1))))
            }
        }
        .font(.system(size:10,weight:.medium))
        .fixedSize(horizontal:false,vertical:true)
    }
    private var lifecycleSection: some View {
        VStack(alignment:.leading,spacing:4) {
            Rectangle().fill(QStyle.line.opacity(0.55)).frame(height:1)
            ForEach(palace.lifeRows) { line in PalaceLifeRow(line:line) }
        }
        .frame(maxWidth:.infinity,alignment:.leading)
    }
    private func namedSymbol(_ label:String,_ value:String,kind:String) -> some View {
        HStack(alignment:.firstTextBaseline,spacing:4) {
            Text(label).font(.system(size:10)).foregroundStyle(labelColor)
                .frame(width:11,alignment:.leading)
            Text(value).font(.system(size:17,weight:.semibold))
                .foregroundStyle(QFive.shade(kind,value))
                .fixedSize(horizontal:false,vertical:true)
        }
    }
    private func multiSymbol(_ label:String,_ value:String,kind:String) -> some View {
        HStack(alignment:.firstTextBaseline,spacing:3) {
            Text(label).font(.system(size:10)).foregroundStyle(labelColor)
                .frame(width:11,alignment:.leading)
            ForEach(Array(value.components(separatedBy:"·").enumerated()),id: \.offset) { part in
                Text(part.element)
                    .font(.system(size:16,weight:.semibold))
                    .foregroundStyle(QFive.shade(kind,part.element))
            }
        }
    }
    private func stemLine(_ plane:String,_ values:String) -> some View {
        HStack(spacing:1) {
            Text(plane).font(.system(size:9)).foregroundStyle(labelColor)
            ForEach(Array(values.components(separatedBy:"·").enumerated()),id: \.offset) { part in
                Text(part.element)
                    .font(.system(size:15,weight:.semibold))
                    .foregroundStyle(QFive.shade("stem",part.element))
            }
        }
        .lineLimit(1)
        .minimumScaleFactor(0.85)
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
    @State private var chosenTime = Date()
    @State private var useCurrentInstant = true
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
                            if subject != "本人" {
                                Picker("问病情境",selection:$inquiryContext) {
                                    Text("当面代问").tag("direct_proxy")
                                    Text("闻讯按事件时间起局").tag("event_news")
                                }
                                .pickerStyle(.menu)
                            }
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
                            Text("关系用神取自现有20类人物来源索引。只有父母、祖辈等长辈才依性别参考乾宫或坤宫，并结合年干；普通男性朋友、女性朋友、配偶和其他非长辈不因为性别加入乾坤宫。未提供真实出生年命不补造。部分同辈用神仍属待核条件，出生公历年份不自动等于年命干支。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                            Picker("病程（可选）", selection: $duration) {
                                ForEach(["未说明", "新病", "久病"], id: \.self) { Text($0) }
                            }
                            Toggle("按当前时间起局",isOn:$useCurrentInstant)
                                .tint(QStyle.blue)
                            if !useCurrentInstant {
                                DatePicker("手动选择年月日时分",selection:$chosenTime,
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
                        Text("九宫由本机离线计算；本次断案内容尚未完成前，不会以历史样例替代。")
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
            let finalInstant=useCurrentInstant ? Date() : chosenTime
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

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 15) {
                    Text("完整解读")
                        .font(.system(size: 28, weight: .medium))
                    if let chart=nativeChart {
                        Text("本次九宫已在本机离线生成。")
                            .font(.caption).foregroundStyle(QStyle.secondary)
                        let actualPillars = [chart.pillars.year,chart.pillars.month,
                                             chart.pillars.day,chart.pillars.hour]
                        Text(actualPillars.joined(separator:" ") + " · " + chart.solarTerm)
                            .font(.headline)
                        if let reading=nativeReading {
                            WenguaNativeCustomerView(reading:reading)
                        } else {
                            Text("此九宫只有真实盘面事实，未能完成本次专题的原生断案依据校验。")
                                .foregroundStyle(QStyle.red)
                        }
                        Text("本盘九宫事实")
                            .font(.title3.weight(.semibold))
                            .padding(.top,10)
                        ForEach(chart.palaces.sorted(by:{
                            let a=WenguaNativeCore.branchOrderPalaces.firstIndex(of:$0.id) ?? 9
                            let b=WenguaNativeCore.branchOrderPalaces.firstIndex(of:$1.id) ?? 9
                            return a < b
                        })) { palace in
                            NativePalaceEvidenceCard(palace:palace)
                        }
                    } else {
                        Text("封存原始断词资源未加载；拒绝以其它测试盘文本替代。")
                            .foregroundStyle(QStyle.red)
                    }
                    Text("本软件仅用于传统文化研究及古籍象意展示，不提供医学诊断、预后或治疗建议。")
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
            Text("本盘81格原文与模板实时替换 · 基础事实，尚非完整断案")
                .font(.title3.weight(.semibold))
            Text("各条古文和取象对应本盘真实天盘携干与地盘干；200格能量、人物关系及最后吉凶尚未原生移植。")
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
        .background(.white,in:RoundedRectangle(cornerRadius:12))
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
                Text("地盘：" + palace.earthStem + "。中五不伪造普通星、门、神。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
            } else {
                Text("神：" + (palace.deity ?? "未核定") +
                     "　门：" + (palace.door ?? "未核定"))
                    .font(.subheadline)
                Text("天盘：" + stageText)
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Text("地盘：" + groundStages)
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Text(conditions)
                    .font(.caption).foregroundStyle(QStyle.blue)
            }
        }
        .frame(maxWidth:.infinity,alignment:.leading)
        .padding(16)
        .background(.white,in:RoundedRectangle(cornerRadius:14))
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
