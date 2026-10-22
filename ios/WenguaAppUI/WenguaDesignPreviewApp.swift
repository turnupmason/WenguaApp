import SwiftUI

// WenguaApp · iOS visual design preview only.
// No old V4 score calculations, no claims of medical accuracy,
// and NO local Python engine is silently assumed to work in SwiftUI.
// The sample board below is a clearly labeled, fixed historical test board.

@main
struct WenguaDesignPreviewApp: App {
    var body: some Scene {
        WindowGroup {
            WenguaRootView()
                .tint(WenguaTheme.inkGreen)
        }
    }
}

enum WenguaTheme {
    static let canvas = Color(red: 0.972, green: 0.969, blue: 0.947)
    static let card = Color.white
    static let ink = Color(red: 0.137, green: 0.169, blue: 0.161)
    static let inkGreen = Color(red: 0.082, green: 0.247, blue: 0.227)
    static let muted = Color(red: 0.431, green: 0.470, blue: 0.453)
    static let gold = Color(red: 0.686, green: 0.565, blue: 0.384)
    static let softGreen = Color(red: 0.906, green: 0.941, blue: 0.929)
    static let hairline = Color(red: 0.895, green: 0.902, blue: 0.871)
}

struct WenguaRootView: View {
    var body: some View {
        TabView {
            NavigationStack { HomeScreen() }
                .tabItem { Label("问事", systemImage: "square.grid.2x2") }
            NavigationStack { RecordsScreen() }
                .tabItem { Label("记录", systemImage: "clock.arrow.circlepath") }
            NavigationStack { MoreScreen() }
                .tabItem { Label("更多", systemImage: "text.book.closed") }
        }
    }
}

struct Pill: View {
    let text: String
    var emphasized = false
    var body: some View {
        Text(text)
            .font(.caption2.weight(.medium))
            .foregroundStyle(emphasized ? WenguaTheme.inkGreen : WenguaTheme.muted)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(emphasized ? WenguaTheme.softGreen : WenguaTheme.canvas)
            .clipShape(Capsule())
    }
}

struct Surface<Content: View>: View {
    @ViewBuilder let content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 14) { content }
            .padding(18)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(WenguaTheme.card, in: RoundedRectangle(cornerRadius: 20))
            .overlay(RoundedRectangle(cornerRadius: 20)
                .strokeBorder(WenguaTheme.hairline, lineWidth: 0.7))
    }
}

struct HomeScreen: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                HStack {
                    VStack(alignment: .leading, spacing: 5) {
                        Text("問 卦")
                            .font(.system(size: 34, weight: .semibold, design: .serif))
                            .tracking(5)
                            .foregroundStyle(WenguaTheme.ink)
                        Text("观时 · 识局 · 明理")
                            .font(.subheadline)
                            .foregroundStyle(WenguaTheme.muted)
                    }
                    Spacer()
                    Image(systemName: "circle.hexagongrid")
                        .font(.system(size: 26, weight: .light))
                        .foregroundStyle(WenguaTheme.gold)
                        .accessibilityHidden(true)
                }
                .padding(.top, 14)

                Surface {
                    HStack {
                        Pill(text: "时家转盘", emphasized: true)
                        Pill(text: "本地优先")
                    }
                    Text("心有所问\n自有一局")
                        .font(.system(size: 31, weight: .medium, design: .serif))
                        .foregroundStyle(WenguaTheme.ink)
                        .lineSpacing(6)
                    Text("选择问事类型，在真实起盘之后查看九宫、传统断词与支持和反对的依据。")
                        .font(.subheadline)
                        .foregroundStyle(WenguaTheme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                    NavigationLink {
                        NewQuestionScreen()
                    } label: {
                        HStack {
                            Spacer()
                            Text("开始问事").fontWeight(.semibold)
                            Image(systemName: "arrow.right")
                            Spacer()
                        }
                        .padding(.vertical, 16)
                        .foregroundStyle(.white)
                        .background(WenguaTheme.inkGreen, in: RoundedRectangle(cornerRadius: 13))
                    }
                }

                Text("问事领域")
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(WenguaTheme.ink)
                DomainTile(title: "身体健康", subtitle: "病情轻重 · V3.9.1 传统断词",
                           symbol: "heart.text.square", enabled: true)
                DomainTile(title: "婚姻感情", subtitle: "领域规则继续开发中",
                           symbol: "heart", enabled: false)
                DomainTile(title: "工作与求财", subtitle: "领域规则继续开发中",
                           symbol: "briefcase", enabled: false)
                Text("传统文化与古籍研究工具，不提供医学诊断、治疗或风险概率。")
                    .font(.caption)
                    .foregroundStyle(WenguaTheme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(20)
        }
        .background(WenguaTheme.canvas)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct DomainTile: View {
    let title: String
    let subtitle: String
    let symbol: String
    let enabled: Bool

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: symbol)
                .font(.title3)
                .foregroundStyle(WenguaTheme.inkGreen)
                .frame(width: 45, height: 45)
                .background(WenguaTheme.softGreen, in: RoundedRectangle(cornerRadius: 14))
            VStack(alignment: .leading, spacing: 5) {
                Text(title).font(.headline).foregroundStyle(WenguaTheme.ink)
                Text(subtitle).font(.caption).foregroundStyle(WenguaTheme.muted)
            }
            Spacer()
            Pill(text: enabled ? "首个专题" : "开发中", emphasized: enabled)
        }
        .padding(14)
        .background(.white, in: RoundedRectangle(cornerRadius: 18))
    }
}

enum ConsultedPerson: String, CaseIterable, Identifiable {
    case selfPerson = "本人"
    case father = "父亲"
    case mother = "母亲"
    case husband = "丈夫"
    case wife = "妻子"
    case brother = "兄弟"
    case sister = "姐妹"
    case son = "儿子"
    case daughter = "女儿"

    var id: String { rawValue }
}

struct NewQuestionScreen: View {
    @State private var person: ConsultedPerson = .selfPerson
    @State private var question: String = ""
    @State private var duration: String = "未说明"

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Text("所问之事")
                    .font(.system(size: 30, weight: .medium, design: .serif))
                    .foregroundStyle(WenguaTheme.ink)
                Surface {
                    Text("问事专题").font(.caption).foregroundStyle(WenguaTheme.muted)
                    HStack {
                        Image(systemName: "heart.text.square").foregroundStyle(WenguaTheme.inkGreen)
                        Text("健康 · 病情轻重").fontWeight(.medium)
                        Spacer()
                        Pill(text: "V3.9.1", emphasized: true)
                    }
                    Divider()
                    Text("你在为谁问事？").font(.headline)
                    Picker("被问者", selection: $person) {
                        ForEach(ConsultedPerson.allCases) { item in
                            Text(item.rawValue).tag(item)
                        }
                    }
                    .pickerStyle(.menu)
                    Text("人物关系会决定真正的用神，而不是统一套用日干。")
                        .font(.caption)
                        .foregroundStyle(WenguaTheme.muted)
                }
                Surface {
                    Text("补充说明（可选）").font(.headline)
                    TextField("写下此刻所问的问题", text: $question, axis: .vertical)
                        .lineLimit(2...4)
                    Divider()
                    Picker("病程", selection: $duration) {
                        ForEach(["未说明", "新病", "久病"], id: \.self) { Text($0) }
                    }
                    Text("未提供的出生年命和实际病程不从盘中猜测。")
                        .font(.caption).foregroundStyle(WenguaTheme.muted)
                }
                Surface {
                    Label("此刻起盘", systemImage: "clock")
                        .font(.headline).foregroundStyle(WenguaTheme.inkGreen)
                    Text("正式版在按下起盘按钮的一刻锁定设备时间和时区，再通过经过一致性验证的本地引擎计算九宫。")
                        .font(.subheadline).foregroundStyle(WenguaTheme.muted)
                }
                NavigationLink {
                    DemoResultScreen()
                } label: {
                    HStack {
                        Spacer()
                        Text("查看界面演示")
                        Image(systemName: "arrow.right")
                        Spacer()
                    }
                    .fontWeight(.semibold)
                    .padding(.vertical, 15)
                    .background(WenguaTheme.inkGreen, in: RoundedRectangle(cornerRadius: 14))
                    .foregroundStyle(.white)
                }
                Text("设计原型尚未接入 iOS 本地推理。演示结果使用固定历史样例，与本页输入无关。")
                    .font(.caption)
                    .foregroundStyle(WenguaTheme.muted)
            }
            .padding(20)
        }
        .background(WenguaTheme.canvas)
        .navigationTitle("新问事")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct DemoPalace: Identifiable {
    let id: Int
    let palaceName: String
    let star: String
    let door: String
    let deity: String
    let sky: String
    let ground: String
    let role: String

    static let originalSample: [DemoPalace] = [
        .init(id: 4, palaceName: "巽四", star: "天任", door: "死门", deity: "六合", sky: "己", ground: "癸", role: "患者"),
        .init(id: 9, palaceName: "离九", star: "天冲", door: "惊门", deity: "太阴", sky: "丁", ground: "戊", role: ""),
        .init(id: 2, palaceName: "坤二", star: "天辅", door: "开门", deity: "螣蛇", sky: "癸", ground: "丙", role: ""),
        .init(id: 3, palaceName: "震三", star: "天蓬", door: "景门", deity: "白虎", sky: "乙", ground: "丁", role: "乙奇"),
        .init(id: 5, palaceName: "中五", star: "", door: "", deity: "", sky: "", ground: "壬", role: ""),
        .init(id: 7, palaceName: "兑七", star: "天英", door: "休门", deity: "值符", sky: "戊", ground: "庚", role: ""),
        .init(id: 8, palaceName: "艮八", star: "天心", door: "杜门", deity: "玄武", sky: "辛", ground: "己", role: "天心"),
        .init(id: 1, palaceName: "坎一", star: "天柱", door: "伤门", deity: "九地", sky: "庚", ground: "乙", role: "时干"),
        .init(id: 6, palaceName: "乾六", star: "天芮·天禽", door: "生门", deity: "九天", sky: "丙·壬", ground: "辛", role: "天芮")
    ]
}

enum ResultSegment: String, CaseIterable, Identifiable {
    case chart = "九宫盘", reading = "断词", provenance = "依据"
    var id: String { rawValue }
}

struct DemoResultScreen: View {
    @State private var selected: ResultSegment = .chart
    @State private var selectedPalace: DemoPalace? = nil

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Pill(text: "固定历史样例 · 非实时起盘", emphasized: true)
                    Spacer()
                    Image(systemName: "lock.shield").foregroundStyle(WenguaTheme.muted)
                }
                Text("一局一问")
                    .font(.system(size: 30, weight: .medium, design: .serif))
                Text("丙午年 · 戊戌月 · 己巳日 · 庚午时")
                    .font(.subheadline).foregroundStyle(WenguaTheme.muted)
                HStack(spacing: 8) {
                    Pill(text: "阴遁九局")
                    Pill(text: "寒露")
                    Pill(text: "本人问身体")
                }
                Picker("结果视图", selection: $selected) {
                    ForEach(ResultSegment.allCases) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)

                switch selected {
                case .chart:
                    Surface {
                        HStack {
                            Text("九宫实盘结构").font(.headline)
                            Spacer()
                            Text("点击宫位展开").font(.caption).foregroundStyle(WenguaTheme.muted)
                        }
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 5), count: 3),
                                  spacing: 5) {
                            ForEach(DemoPalace.originalSample) { item in
                                Button { selectedPalace = item } label: {
                                    PalaceTile(item: item)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        Text("巽 · 离 · 坤 / 震 · 中 · 兑 / 艮 · 坎 · 乾")
                            .font(.caption2).foregroundStyle(WenguaTheme.muted)
                    }
                    legend
                case .reading:
                    reading
                case .provenance:
                    provenance
                }
                Text("传统文化与古籍研究解读，不是疾病诊断、预后、处方或治疗建议。")
                    .font(.caption).foregroundStyle(WenguaTheme.muted)
            }
            .padding(18)
        }
        .background(WenguaTheme.canvas)
        .navigationTitle("问卦 · 演示结果")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $selectedPalace) { palace in
            PalaceDetail(palace: palace)
                .presentationDetents([.medium])
        }
    }

    private var legend: some View {
        Surface {
            Text("盘面角色").font(.headline)
            HStack(spacing: 8) {
                Pill(text: "患者 · 巽四", emphasized: true)
                Pill(text: "天芮 · 乾六", emphasized: true)
            }
            HStack(spacing: 8) {
                Pill(text: "天心 · 艮八")
                Pill(text: "乙奇 · 震三")
                Pill(text: "时干 · 坎一")
            }
            Text("一宫多个角色分别记录，但不能因为同宫就重复认定为两项独立证据。")
                .font(.caption).foregroundStyle(WenguaTheme.muted)
        }
    }

    private var reading: some View {
        VStack(alignment: .leading, spacing: 12) {
            Surface {
                Text("传统主判断（样例）").font(.caption).foregroundStyle(WenguaTheme.muted)
                Text("偏凶 · 同时存在反向有利依据")
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(WenguaTheme.ink)
                Text("病宫克患者，患者巽四宫见死门；病宫丙辛「月奇相合」、天芮泄气及旬空则构成制衡。不是对现实病情的判定。")
                    .font(.subheadline).foregroundStyle(WenguaTheme.muted)
            }
            ForEach(DemoReadingSection.sections) { section in
                DisclosureGroup {
                    Text(section.body)
                        .font(.subheadline)
                        .foregroundStyle(WenguaTheme.ink)
                        .padding(.top, 10)
                } label: {
                    Text(section.title)
                        .font(.headline)
                        .foregroundStyle(WenguaTheme.ink)
                }
                .padding(15)
                .background(.white, in: RoundedRectangle(cornerRadius: 16))
            }
        }
    }

    private var provenance: some View {
        VStack(alignment: .leading, spacing: 12) {
            Surface {
                Text("为何这样判断").font(.headline)
                Text("来源：原有《神奇之门》《开悟之门》规则库与 V3.9.1 十二长生扩展。原书行号与哈希仅用于内部复核，不在普通断词中显示。")
                    .font(.subheadline).foregroundStyle(WenguaTheme.muted)
            }
            Surface {
                Text("需要同时保留的反证").font(.headline)
                Text("患者宫受病宫克，但病星天芮土生乾六金呈泄气。病宫亦见丙加辛「月奇相合」与戌亥旬空，不能只摘一条吉凶格局。")
                    .font(.subheadline).foregroundStyle(WenguaTheme.muted)
            }
            Surface {
                Text("隐私与数据").font(.headline)
                Text("正式设计为设备本地保存；不默认同步问事历史、个人健康文字或出生年份。")
                    .font(.subheadline).foregroundStyle(WenguaTheme.muted)
            }
        }
    }
}

struct PalaceTile: View {
    let item: DemoPalace

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(spacing: 2) {
                Text(item.palaceName).font(.caption2.weight(.semibold))
                Spacer(minLength: 0)
                if !item.role.isEmpty {
                    Circle().fill(WenguaTheme.gold).frame(width: 6, height: 6)
                }
            }
            .foregroundStyle(WenguaTheme.muted)
            Spacer(minLength: 0)
            if item.id == 5 {
                Text("地壬 · 中宫")
                    .font(.caption2)
                    .foregroundStyle(WenguaTheme.muted)
                    .minimumScaleFactor(0.7)
                    .lineLimit(1)
            } else {
                Text(item.star).font(.caption2.weight(.medium))
                    .lineLimit(1).minimumScaleFactor(0.65)
                Text(item.door + "  " + item.deity)
                    .font(.system(size: 9))
                    .lineLimit(1).minimumScaleFactor(0.65)
                Text("天" + item.sky + " · 地" + item.ground)
                    .font(.system(size: 10))
                    .lineLimit(1).minimumScaleFactor(0.65)
            }
            if !item.role.isEmpty {
                Text(item.role)
                    .font(.system(size: 9, weight: .medium))
                    .foregroundStyle(WenguaTheme.inkGreen)
            }
            Spacer(minLength: 0)
        }
        .padding(8)
        .frame(maxWidth: .infinity, minHeight: 103, maxHeight: 112, alignment: .topLeading)
        .background(item.role.isEmpty ? WenguaTheme.card : WenguaTheme.softGreen,
                    in: RoundedRectangle(cornerRadius: 11))
        .overlay(RoundedRectangle(cornerRadius: 11)
            .strokeBorder(item.role.isEmpty ? WenguaTheme.hairline : WenguaTheme.gold.opacity(0.7),
                          lineWidth: 1))
        .accessibilityLabel(item.id == 5 ? "中五宫，地壬，不设置常规八门星神" :
            "\(item.palaceName)，\(item.star)，\(item.door)，\(item.deity)，天\(item.sky)，地\(item.ground)，\(item.role)")
    }
}

struct PalaceDetail: View {
    let palace: DemoPalace
    var body: some View {
        NavigationStack {
            Form {
                Section("宫位") {
                    LabeledContent("九宫", value: palace.palaceName)
                    if !palace.role.isEmpty {
                        LabeledContent("角色", value: palace.role)
                    }
                }
                Section("真实结构样例") {
                    LabeledContent("地盘天干", value: palace.ground)
                    if palace.id == 5 {
                        Text("中五宫不套用八门、九星、八神的普通宫位解析器。")
                    } else {
                        LabeledContent("天盘干", value: palace.sky)
                        LabeledContent("九星", value: palace.star)
                        LabeledContent("八门", value: palace.door)
                        LabeledContent("八神", value: palace.deity)
                    }
                }
            }
            .navigationTitle("宫位详情 · 演示")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct DemoReadingSection: Identifiable {
    let id: Int
    let title: String
    let body: String

    static let sections: [DemoReadingSection] = [
        .init(id: 1, title: "01 · 问事取用", body: "本人以日干己为主要用神，落巽四宫；天芮病星落乾六宫。"),
        .init(id: 2, title: "02 · 值符值使", body: "值符天英星落兑七宫，值使景门落震三宫。"),
        .init(id: 3, title: "03 · 天芮病宫", body: "天芮携丙落乾六宫，丙辛月奇相合；丙在戌墓、亥绝，戌亥旬空。原书有正反条件，须同时取用。"),
        .init(id: 4, title: "04 · 病星月令", body: "戌月天芮相，病星有气；月令与宫位泄气、旬空需综合考虑。"),
        .init(id: 5, title: "05 · 患者用神宫", body: "己落巽四宫，死门、六合，己加癸地刑玄武。十二长生辰衰、巳帝旺。"),
        .init(id: 7, title: "07 · 医生医药", body: "天心在艮八宫；乙奇在震三宫，三奇得使、玉女守门是实际触发的传统有利条件。"),
        .init(id: 8, title: "08 · 时干事体", body: "庚落坎一宫，天柱、伤门、九地。庚在子死，仍须结合病星及患者宫。"),
        .init(id: 9, title: "09 · 特殊格局", body: "按真实盘分别检查六仪击刑、门迫、空亡、双重制病与双重不利；不把同一事实重复加权。"),
        .init(id: 10, title: "10 · 快慢及应期", body: "只有出现原书明确的冲合、出墓或实算应期条件，才能提出应期候选。"),
        .init(id: 11, title: "11 · 最后断词", body: "传统象意综合偏凶，但丙辛月奇相合、天芮泄气及病宫旬空构成重要反证。")
    ]
}

struct RecordsScreen: View {
    var body: some View {
        ContentUnavailableView {
            Label("暂无问事记录", systemImage: "clock.arrow.circlepath")
        } description: {
            Text("正式版将在设备本地保存原盘、问事时刻和断词版本。此设计预览不写入任何问事数据。")
        }
        .navigationTitle("记录")
        .background(WenguaTheme.canvas)
    }
}

struct MoreScreen: View {
    var body: some View {
        List {
            Section("典籍与方法") {
                Label("神奇之门 · 知识目录", systemImage: "books.vertical")
                Label("开悟之门 · 知识目录", systemImage: "text.book.closed")
                Text("典籍版权许可与移动端展示范围仍需核对。")
                    .font(.caption).foregroundStyle(.secondary)
            }
            Section("偏好与隐私") {
                Label("字体与外观（待开发）", systemImage: "textformat.size")
                Label("本地记录管理（待开发）", systemImage: "lock.shield")
            }
            Section {
                Text("Wengua iOS · 视觉设计预览")
                Text("这不是已连接本地 Python 断案引擎的上架版本。")
                    .font(.caption).foregroundStyle(.secondary)
            }
        }
        .navigationTitle("更多")
    }
}

#Preview {
    WenguaRootView()
}
