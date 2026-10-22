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

struct ProfessionalChartScreen: View {
    @State private var chosenPalace: QPalace?
    @State private var showAsk = false
    @State private var showReading = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    Button {
                        showAsk = true
                    } label: {
                        Text("2026年11月1日 05:00  ⌄")
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
                    pillar("丙", "午", "年", color: QStyle.red)
                    pillar("戊", "戌", "月", color: QStyle.orange)
                    pillar("己", "卯", "日", color: QStyle.orange)
                    pillar("丁", "卯", "时", color: QStyle.blue)
                    Spacer(minLength: 0)
                    VStack(alignment: .leading, spacing: 6) {
                        Text("阴遁 · 五局  ›  甲子旬")
                        Text("值符：天禽  值使：死门")
                    }
                    .font(.system(size: 11))
                    .foregroundStyle(QStyle.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(QStyle.backing)

                HStack {
                    Text("时家转盘 · 霜降上元")
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

                LazyVGrid(
                    columns: Array(repeating: GridItem(.flexible(), spacing: 1), count: 3),
                    spacing: 1
                ) {
                    ForEach(QPalace.actualSourceFixture) { palace in
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
                    Text("时空：甲子旬，戌亥空")
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

                Text("固定源书研究样例 · 非实时起盘。演示盘不会对应你随后输入的新问题。")
                    .font(.caption2)
                    .foregroundStyle(QStyle.secondary)
                    .padding(14)
            }
        }
        .background(.white)
        .navigationTitle("局式 · 演示盘")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $chosenPalace) { palace in
            ProfessionalPalaceDetail(palace: palace)
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
        }
        .sheet(isPresented: $showAsk) { CastSetupScreen() }
        .sheet(isPresented: $showReading) { TraditionalReadingPreview() }
    }

    private func pillar(_ sky: String, _ branch: String, _ label: String, color: Color) -> some View {
        VStack(spacing: 1) {
            Text(sky).font(.system(size: 23, weight: .medium))
            Text(label).font(.system(size: 9)).foregroundStyle(QStyle.secondary)
            Text(branch).font(.system(size: 22, weight: .medium))
        }
        .foregroundStyle(color)
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

struct ProfessionalPalaceTile: View {
    let palace: QPalace

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            if palace.id == 5 {
                Spacer()
                Text("中五")
                    .font(.system(size: 22))
                    .foregroundStyle(QStyle.secondary)
                Text("特殊宫位")
                    .font(.system(size: 10))
                    .foregroundStyle(QStyle.secondary)
                Spacer()
            } else {
                HStack(spacing: 2) {
                    Text(palace.branches)
                    Text("·")
                    Text(palace.stages.replacingOccurrences(of: "天芮携", with: "")
                        .prefix(8) + "…")
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                    Spacer(minLength: 0)
                    Text("\(palace.id)")
                }
                .font(.system(size: 9))
                .foregroundStyle(QStyle.secondary)
                .lineLimit(1)

                HStack {
                    Text(palace.ground)
                        .foregroundStyle(QStyle.secondary)
                    Spacer()
                    Text(palace.deity)
                        .foregroundStyle(palace.deity == "白虎" ? QStyle.red : QStyle.orange)
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
                .font(.system(size: 16, weight: .medium))

                Spacer(minLength: 3)
                HStack(spacing: 2) {
                    Text(palace.stars)
                        .foregroundStyle(QStyle.green)
                        .lineLimit(1).minimumScaleFactor(0.6)
                    Spacer(minLength: 1)
                    Text(palace.sky)
                        .foregroundStyle(QStyle.red)
                        .lineLimit(1).minimumScaleFactor(0.65)
                }
                .font(.system(size: 15, weight: .medium))

                HStack(spacing: 2) {
                    Text(palace.door)
                        .foregroundStyle(QStyle.blue)
                    Spacer(minLength: 1)
                    Text(palace.ground)
                        .foregroundStyle(QStyle.orange)
                }
                .font(.system(size: 17, weight: .medium))

                HStack(spacing: 3) {
                    ForEach(palace.roles, id: \.self) { role in
                        Text(role)
                            .font(.system(size: 9))
                            .foregroundStyle(QStyle.blue)
                    }
                    if palace.id == 6 {
                        Text("戌亥空")
                            .font(.system(size: 9))
                            .foregroundStyle(QStyle.red)
                    }
                }
                .frame(minHeight: 12, alignment: .leading)
            }
        }
        .padding(.horizontal, 7)
        .padding(.vertical, 9)
        .frame(maxWidth: .infinity, minHeight: 156, maxHeight: 156, alignment: .topLeading)
        .background(.white)
        .contentShape(Rectangle())
        .accessibilityLabel(palace.id == 5
             ? "中五宫，不伪造普通星门神"
             : "\(palace.name)，\(palace.deity)，\(palace.stars)，\(palace.door)，天盘\(palace.sky)，地盘\(palace.ground)，\(palace.stages)")
    }
}

struct ProfessionalPalaceDetail: View {
    let palace: QPalace
    private let columns = [GridItem(.flexible()), GridItem(.flexible())]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 15) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(palace.name) · \(palace.element)行")
                        .font(.system(size: 27, weight: .semibold))
                        .foregroundStyle(QStyle.text)
                    Text("真实研究盘的宫位资料 · 不代表现实疾病")
                        .font(.caption)
                        .foregroundStyle(QStyle.secondary)
                }
                HStack(spacing: 7) {
                    ForEach(palace.roles, id: \.self) { role in
                        detailTag(role)
                    }
                    if palace.id == 6 { detailTag("戌亥旬空") }
                    detailTag("已校验样例")
                }

                if palace.id == 5 {
                    factCard("中五宫特殊规则", text: "中五不强行套用外围八门、九星与八神；研究库未提供的中宫事项不伪造。")
                } else {
                    LazyVGrid(columns: columns, spacing: 10) {
                        valueCard("八神", value: palace.deity, color: QStyle.orange)
                        valueCard("九星", value: palace.stars, color: QStyle.green)
                        valueCard("八门", value: palace.door, color: QStyle.blue)
                        valueCard("天 / 地盘干", value: palace.sky + " / " + palace.ground, color: QStyle.red)
                    }
                    factCard("十二长生", text: palace.stages)
                    factCard("宫位角色及实盘信息",
                        text: "\(palace.name)为\(palace.element)行，辖\(palace.branches)支。" +
                         (palace.roles.isEmpty ? "此宫没有被选为本问患者、病宫、天心、乙奇或时干主角色。" :
                            "此宫承担：" + palace.roles.joined(separator: "、") + "。") +
                         (palace.id == 6 ? " 本盘甲子旬，戌亥空。" : "") +
                         " 同一事实不会因为两个身份共宫而重复计入论断。")
                }
                Text("传统文化与古籍象意展示。具体断词使用 V3.9.1 原文，不输出分数或临床结论。")
                    .font(.footnote)
                    .foregroundStyle(QStyle.secondary)
            }
            .padding(20)
        }
        .background(QStyle.backing)
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

struct CastSetupScreen: View {
    @Environment(\.dismiss) private var dismiss
    @State private var subject = "本人"
    @State private var subjectName = ""
    @State private var question = ""
    @State private var duration = "未说明"
    @State private var chosenTime = Date()
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
                            Picker("病程（可选）", selection: $duration) {
                                ForEach(["未说明", "新病", "久病"], id: \.self) { Text($0) }
                            }
                            DatePicker("选择起局时刻",
                                selection: $chosenTime, displayedComponents: [.date, .hourAndMinute])
                                .datePickerStyle(.wheel)
                                .labelsHidden()
                                .frame(maxWidth: .infinity)
                            Button("使用现在时间") { chosenTime = .now }
                                .foregroundStyle(QStyle.blue)
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
                                    Button("完成静心 · 返回固定九宫演示") { dismiss() }
                                        .buttonStyle(.borderedProminent)
                                } else {
                                    Text("静心进行中 · 无跳过按钮")
                                        .foregroundStyle(QStyle.secondary)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 30)
                        }
                        Text("演示版不真正计算新盘，也不耗用15天正式起局记录。正式版在30秒结束后点击确认起局时锁定实际时间。")
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

    private func tryStartRitual() {
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
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 15) {
                    Text("古籍断词 · V3.9.1")
                        .font(.system(size: 28, weight: .medium))
                    Text("固定历史样例，不是刚输入的新问题。")
                        .font(.caption).foregroundStyle(QStyle.secondary)
                    Text("保留主证、反证、应期和完整十二长生，不显示任何分数。")
                        .font(.subheadline)
                    Divider()
                    ForEach(TraditionalChapter.demo, id: \.0) { row in
                        DisclosureGroup(row.0) {
                            Text(row.1)
                                .font(.subheadline)
                                .foregroundStyle(QStyle.secondary)
                                .padding(.top, 8)
                        }
                        .padding(13)
                        .background(.white, in: RoundedRectangle(cornerRadius: 12))
                    }
                    Text("演示条目仅展示结构，不冒充与实时用户相关的古籍断案。完整生成的V3.9.1原文以研究库封存版本为准。")
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
