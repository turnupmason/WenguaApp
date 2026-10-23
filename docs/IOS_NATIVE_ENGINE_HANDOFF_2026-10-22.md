# WenguaApp iOS 离线起盘正式开发移交｜2026-10-22

## 决策

用户最后明确说：「开始，iOS 离线起盘引擎，而不再是反复手工填写九宫，开始做软件了。然后给我更新agent还有给我写prompt。这个对话上限了，我需要开新的号。」

**此时项目目标已从 UI 原型转为 iOS 可执行软件开发。绝对不能再以硬编码九宫演示数据代替真实起盘。** 保留用户确认的高密度九宫截图排版；所有神、星、门、干、地支逐个按其本身金木水火土五行上色：火红、金黄、木绿、水蓝、土棕。宫中必须可见确实发生的旬空、马星、入墓、十二长生，天盘与地盘入墓独立。

用户要求 30 秒静心、心诚则灵、尊重事实、同一件具体事15天内只成功起局一次。30 秒不能跳，点击「确认起局」时锁定真时间；用户主动选择指定时刻复盘是另一种有说明的模式。15天只从成功真实起局并持久化后开始，不因打开例子而记账；匿名本地SHA256同题不能跨设备或完美识别改写，绝不可声称全球保证。

用户已弃用所有 V4.0–V4.2 分数，保留 V3.9.1 的完整11栏自然中文、原书正反证据、推理、应期、完整十干×12长生。**iOS 新 Swift Core 当前完成起盘结构，不等于已移植 V3.9.1 推理/断词。**

## 已经真正提交的原生离线引擎

1. `ios/WenguaAppUI/WenguaNativeCore.swift`：Foundation-only Swift 实现。完全不依赖网络/云AI，也无需 Python 在 iPhone 跑。对齐：
   - `src/wengua/astro_calendar.py`：本地 Meeus/NOAA 太阳视黄经、24节气、以立春划年、以节划月、癸酉日1995-06-11历法锚、五鼠遁元日干推时柱、IANA时区和DST。位于节气0.05°内拒绝近似排盘；未有学校原书23点换日确定方法的盘拒绝；1850-2150界外拒绝。
   - `src/wengua/casting_shenqi.py`：原书三元符头、阴阳遁、局数、地盘九宫依序，坎艮震巽离坤兑乾转盘，旬首六甲遁干、值符星／值使门、星盘门盘按环旋转、神盘依阴阳顺逆转，天禽与天芮各携原地盘干同宫，不能在中宫伪造常规星门神。值使门非零步落中五且未经原书验寄宫一律拒绝。
   - `src/wengua/marriage_runtime.py`：九宫真实辖支、旬空。
   - `src/wengua/health_severity_v34.py`：时支对应真实驿马，不能改成按日支。
   - `data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json`：源书已校核十干×十二长生120事实（**只复用事实，不复用V4评分**）。每个天盘携干、地盘干在真实宫支的阶段，区分天墓、地墓，显示真实空马。
2. `ios/WenguaAppUI/GoldenNativeCastCases.json`：四个完整真实历史资料库盘对应日期（2026-11-01/11-04/11-10/11-21，都是2026-10-22预计算的**未来测试日期**，并非古籍真实案件），与 `data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json` 一一关联。
3. `ios/WenguaAppUI/NativeParityMain.swift`：单独的 `@main` 命令行对照入口，**只用于跨语言黄金样例测试，严禁加入真正iOS App的targets，因为与App的@main冲突**。在 Linux `swiftc` 真实编译执行，计算四个全新九宫（不是读取历史预填宫位）。
4. `tests/test_ios_native_cast_against_python.py`：逐一验证四柱、节气、三元遁局、旬首、值符值使、全部外围8宫的地盘干、星携干与全阶段、门、神，十二长生、空亡、时马、天地墓、中五无常规星门神等。
5. `.github/workflows/ios_native_cast_parity.yml`：Linux Foundation Swift 真编译+和原Python四盘一致性测试，以及**macos-15 XcodeGen完整原生模拟器build**。Linux CI已证明原Swift代码真实编译与星门神四盘完全对得上，早期Python测试因 Swift Codable 省略 nil 值报错现已修改；不要把以前的失败删掉，保留供回溯。macOS真Xcode构建需检查最新 Actions，未经通过不可声称可安装。
6. `ios/WenguaAppUI/project.yml`：XcodeGen生成的 iOS17+ SwiftUI 工程规格，App只包括 `WenguaDesignPreviewApp.swift` 与 `WenguaNativeCore.swift`，排除测试 CLI `NativeParityMain.swift`。在Mac进入 `ios/WenguaAppUI`，执行 `xcodegen generate --spec project.yml`、Xcode打开工程、iOS模拟器Build、无签名测试 `xcodebuild ... CODE_SIGNING_ALLOWED=NO build`。不需要直接复制Python仓库或改原书数据。
7. `ios/WenguaAppUI/WenguaDesignPreviewApp.swift` 原生SwiftUI九宫已由 **`@State nativeChart` + `WenguaNativeCore.compute(at:timezone:)`** 真生成：本次计算后的日期四柱、局数、值符值使、所有九宫、神星门天地干、空马墓及长生自动更新；默认的固定预览盘只在用户未起局时展示。`CastSetupScreen` 提供具体问事、角色、当事人称呼和30秒静心→确认真实起局。成功后只本地存储源九宫和 SHA256同事项摘要（不储存原始问句为同题键），并登记15天限制；起局失败不登记。真正用户的完整医疗断词iOS尚未接入，结果页要明确提示，禁止将固定样例推断用于新盘。

## 源仓库与封存数据不可重开

- GitHub：`https://github.com/turnupmason/WenguaApp` 分支 main。必须先读根 `AGENTS.md` 及 `docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`。
- Python唯一完整来源基线 `src/wengua/health_text_pipeline.py:auto_cast_health_v39_text`；现有源书194案例、43章、81个原书天地干有序组合＋42疾病补充＋17复合条件，失败实验均不得删除。
- 最新完整 SQLite `archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3` SHA256 `21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405`。UI与Swift源代码迭代不改原古籍库就不要无故生成新版研究SQLite。
- V4数值评分彻底停用，不能从旧分数恢复「健康指数／吉凶概率」。
- 前序视觉交互演示在 `ios/design-v1/preview.html`、`chart-facts-v3.js`、`five-element-colors.js`；这些是冻结对照并可保留，但不能成为正式计算引擎替代品。用户强调不再手工填九宫。

## 下一阶段的明确工程任务（优先级顺序）

1. **务必先检查最新 GitHub Actions** `iOS Offline Native Casting Parity` 和 `iOS V1 Design Contract`、整体CI，修复任何红灯。特别注意 Swift源码 parse 与 macOS XcodeGen真正 SwiftUI类型检查，不能把 Linux Swift parse 说成 iOS编译。若 Xcode build提示 Info.plist/签名/Deployment Target 或 generic SwiftUI ViewBuilder 错误，逐条修复并真实重跑。
2. 真机或模拟器检查：真实本地30秒完成点确认，当前时刻锁定，九宫不含硬编码；用户手动指定时刻只在显式复盘模式使用。Xcode 真build成功之后才可称有可运行的iOS原型。
3. 为 Swift Core 增加**更多未用于调参的新案例**（节气临界、DST春秋、年交界、换日、阴阳遁、甲首、中宫异常）回归；不为通过golden偷偷改底层。
4. 十干×十二长生、旬空、驿马、墓、击刑、门迫等全面从后端提供独立结构字段，UI不能按手填宫位判断；天墓／地墓不能重计；不符合原书确定条件不能妄报「马冲开墓」。
5. 再分模块移植 V3.9.1 的**人物关系取用、81组原书有序干、42条健康增补、17组复合及对冲优先级、11栏自然断词**，保留书/章/hash内部证据与客户自然中文；可嵌原文只读SQLite与查询/模板，但不能以静态样例或未经校验的AI替代规则。记住第一版只「健康·病情轻重」，其他领域待实现。
6. 实现正式本地数据持久化、安全删除/导出与严格事件ID，让15天一事一占得到适当隐私和跨话术限制；系统UserDefaults匿名本地摘要是初始实测逻辑，非跨设备绝对防重复。
7. 更新 `AGENTS.md`、项目状态、章节账本、回归测试后提交GitHub，报告准确SHA/CI通过证据并让用户查看软件，不要反复发设计模板拖延工程。用户可能在**新的ChatGPT账号/窗口**继续，不能假定之前账号的GitHub授权在新号里自动存在；必须请新号通过连接授权访问仓库或使用用户自己的git操作，禁止声称已写入如果没连接。

## 当前未完成／必须诚实说明

- Apple原生Mac Xcode正式构建状态以本轮最后 Actions 的实际结果为准；Swift Core Linux true compile+golden真实对照已实现，但不能等同 TestFlight或App Store。
- 真实iOS综合自然中文断词尚未移植，当前绝不能对新盘展示旧V3.9.1断词示例作为正式结果。
- 用户提供的《奇门》九宫排盘截图是视觉参考，**不替换书籍原有置闰/阴阳遁方法**。暂时未确认节气边界、晚子时和某些中五门寄宫须抛错/明确阻塞。
- 恢复下一阶段任务时直接编辑已有 main 分支、保留历史失败，不重置仓库、不重复整理全部原书、不回去画海报或做固定宫位JS演示。

### VERIFIED native iOS implementation checkpoint — 2026-10-22 late session

**Actual macOS Xcode build SUCCESS CONFIRMED**: https://github.com/turnupmason/WenguaApp/actions/runs/39868998543 (commit `d8a3a398be934b86fe31227762467f4ec11b35c5`), jobs `native_core` SUCCESS and `real_ios_xcode_build` SUCCESS; GitHub Actions used XcodeGen `ios/WenguaAppUI/project.yml` to create an iOS 17+ .xcodeproj and really compiled `WenguaDesignPreviewApp.swift` together with `WenguaNativeCore.swift` targeting the iOS Simulator on macos-15, **without signing**. This is not merely Swift parser validation: app compilation succeeded. Four-source-cast parity generated independently with Swift and fully compared to Python golden. Main WenguaApp CI & iOS design contract also SUCCESS on same source commit.

Most recent subsequent clean-up commit `c2aa4f86d68e8c6098e897ee0744532dbcfdc549` refactored the native palace detail ViewBuilder into separately typechecked parts. Check its latest CI run `https://github.com/turnupmason/WenguaApp/actions/runs/39869156240` before calling THAT later HEAD successfully built; earlier d8 checkpoint is definitively confirmed green. All old failures (unittest import side effect, Swift nil JSON fields, bad SwiftUI concatenation/type-check complexity) retained in workflow run history and fixed.

**Verified deliverable** = real native-cast Swift source plus generated-iOS-project definition, source-parity-tested and iOS Simulator BUILD-COMPILED. NOT YET = signed/installable IPA, physical device/testflight run, actual on-device clicks through 30sec and local issue persistence, V3.9.1 offline reading engine, cross-device 15 day enforcement, Apple release. The native computed board represents REAL casting; old precomputed fixture is preview-only. User asked for a new account handoff: `docs/NEXT_CHAT_PROMPT_IOS_NATIVE_2026-10-22.txt` is the complete prompt and `docs/IOS_NATIVE_ENGINE_HANDOFF_2026-10-22.md` is the complete scope/limits/history. Do not accidentally claim that the entire book's diagnostic reasoning was ported just because native calendar/board and app compile pass.

### Latest final parity / Xcode status after view refactor (verified)
**Latest genuine macOS Xcode Simulator BUILD PASS at commit `c2aa4f86d68e8c6098e897ee0744532dbcfdc549`**, https://github.com/turnupmason/WenguaApp/actions/runs/39869156240 ; **native_core=SUCCESS** (Swift compiler independently computes 4 true sealed Python casts), **real_ios_xcode_build=SUCCESS** (XcodeGen iOS17 App actually compiles for iOS Simulator). Also `iOS V1 Design Contract` https://github.com/turnupmason/WenguaApp/actions/runs/39869156637 SUCCESS and `WenguaApp CI` https://github.com/turnupmason/WenguaApp/actions/runs/39869156009 SUCCESS. Additional docs-only commits AFTER c2 do not change native code. This is a real compiling iOS Simulator app project, NOT a signed .ipa or a physical device run or full source-book narration port. Continue Xcode true simulator interactions and offline V3.9.1 reasoning next, not another hand-coded demo.

## 2026-10-22 — 九宫显示延续开发（基于现有原生引擎，保留历史）
- **不是新项目**。已读取本仓库 AGENTS / STATUS / LEDGER / iOS 设计和 NativeCore。现有的 `WenguaNativeCore.compute(at:timezone:)` 是真实离线历法/时家转盘计算，本轮没有变更底层原书起盘规则、四柱和原书已验来源，亦没有重建数据库。
- `ios/design-v1/preview.html`：九宫细分隔线不变；依据封存4张审计真盘，宫内逐行显示 **每个天盘携干与地盘干对应全部真实辖支的十二长生**（含天芮／天禽双星），地支及干按各自五行色，空亡／时支马／天墓／地墓仍直接可见。中五只显示真实地盘干，不伪造神星门及无辖支的十二长生。
- 同宫、对宫与**真实墓支-马支地支六冲**为独立条件；纯宫位相对不得称“冲开”。如存在六冲最多标为**冲墓候选**，需原书其他条件，不自动作结论。旺相休囚废、六仪击刑、门迫没有独立审计状态字段时标明未实现，不能伪造已发生或错误断言未发生。
- `ios/WenguaAppUI/WenguaDesignPreviewApp.swift`：九宫和宫详情共用实盘 `WenguaNativePalace` 携带的天/地两盘十二长生；固定第一盘也基于既有原书12长生常量生成显示行。详情里双星分色、宫支逐一上色、天/地墓按**真实干五行**区分，不按神门星类别上色；遵守中五特殊规则。
- **四张演示盘现在也能在原生 SwiftUI 中选择**：只读样例时间为 2026-11-01 05:00、11-04 05:00、11-10 21:00、11-21 17:00（`America/New_York`）。SwiftUI 对每个固定时刻调用 `WenguaNativeCore.compute` **重新实算**，不预填九宫字段；`FrozenReadingV391.json` 为从既有 `chart-facts-v3.js` 等量复制的4条已封存 V3.9.1 源文本，切换盘时自动同步断词。它们仅是 **固定测试盘而非本次真实问事**，不能占用15天事项次数；若 JSON 资源缺失，拒绝拿其他盘断词填充。
- 新用户真正按“具体问事→30秒完整静心→确认起局”后，`nativeChart` 仍来自实时本机计算，15天 SHA256 事项限制继续只在成功算盘且记录保存后登记；**V3.9.1 新盘真实完整离线断词仍待移植，绝不冒充已完成**。
- 回归：新增 Node 对外围八宫天地盘真实十二长生、中五排除、双星携干和对宫非六冲的检查；原有对四盘的测试、Python UI 契约、15天事项测试持续保留。2026-10-22 首次新增的 Node 检查错误地要求无辖支的中五拥有 `earthStages`，CI 红灯已保存并由下一提交修正，不能擦除失败历史。
- 不改旧194原书案例、43章、81天地干、42疾病补充、17复合格局、原书错断和失败记录；不用 V4.2 数值评分。未签名真机测试/IPA/App Store 未完成，UI 图片视觉比对与真实 Xcode Simulator 手动交互仍待完成。按本次代码最新 Actions 核验新提交，不能以旧成功覆盖新失败。

### 2026-10-22 · 补齐选填出生年份与病程
iOS SwiftUI `CastSetupScreen` 已恢复**出生公历年份选填**，严格要求填写时为1850–2150有效整数；未填即 nil，不得根据缺失资料虚构年命。已有的新/旧病程选项在实际本地成功起局收据中作为选填 `course` 持久化；出生年份作为 `optionalBirthYear`（用户主动填写后才保存）。HTML 测试界面也出现同样选填字段；**真实人物关系取用神／年命的原生推理仍未移植**，这些字段不会自行造成额外占断。新增 Python UI 契约测试锁定该输入行为。新盘30秒及15天成功起局才登记规则没有变。原书/研究 SQLite 无变动。

## 2026-10-22 — Mac Xcode 本地开发与消费者领域入口（连续开发）
- **用户当前目标：直接在自己 Mac 上用 Xcode + GitHub Desktop + XcodeGen 做 iOS App，未来发布 App Store，而不是依赖聊天工具运行软件。** 安装、克隆、模拟器、真机签名、CI 与正式发布边界的命令，见 `docs/MAC_XCODE_LOCAL_DEVELOPMENT.md`。工程原版 `ios/WenguaAppUI/project.yml` + `WenguaNativeCore.swift` 必须继续维护，不得重建仓库或拿四张静态盘代替实际计算。
- 原生入口现在 **问卦 Logo（程序化 SwiftUI 圆形印章，可在本机修改）→ 15领域列表 → 具体细项 → 问事、人物关系、选填生日年份与新旧病程 → 当前时刻/手动年月日时分 → 30秒静心 → 确认九宫实算 → 阅读**。初次打开不再默认显示4张固定演示盘；真实九宫仅从 `nativeChart = WenguaNativeCore.compute(at:timezone:)` 在最终确认后生成；按当前时间以最终按钮时间 `Date()` 计算，手动则按 `chosenTime` 计算，均记录本机 IANA 时区。原来四张黄金测试盘和文案继续保留在仓库，**只作审计测试源**。
- 领域分类是适配旧书跨书共用的展示路由，不意味着已经把所有领域断案规则移植。当前 **唯一可进入的子类为 `health.severity`（疾病健康/病情轻重）**，其余细分明确“待移植”而禁用，不能借用疾病轻重模板。路由标识 `topic.id` 进入成功起盘收据及 SHA256 事项指纹；更换事项或领域不会预先消耗15天额度。产品下一关卡应按各子类配套真正离线专业规则版本、前置条件及来源证据后才逐项启用。
- UI 全面隐藏消费者可见的 `V3.9.1 · 文字断词` 等内部版本标题。正式界面展示“完整解读”；已有封存原文的完整多章文本改为连续纵向卡片，无需一个个打开 DisclosureGroup，也不把“正反证据同列”塞入主判断。当前 **新用户实时盘的 V3.9.1 专业断词并未原生移植**；不能把历史样例文本当成此次完整断词，必须显示还未启用的明确提示。没有 V4.2 数值评分。
- `ios/design-v1/preview.html` 也改为问卦印章 / 领域→细项入口，以及可完整浏览所有原著测试章节、无内部分数和单项折叠；但该 HTML 仍是四张**只读历史审计盘的视觉原型，不具备原生 Swift 起盘能力**，时间随选的真正计算在 Xcode iOS App 中，不得夸大浏览器起盘。
- 四柱、阴阳遁、天芮/天禽同宫、十二长生、旬空、时支马、独立天/地墓、原宫位五行色、入墓与六冲分辨由先前真实核心保持。古籍43章194案例、81组原书天地干、42疾病补充、17复合格局、全部失败数据和历史 GitHub CI 不变。
- 新增 UI 契约检查：15个领域、只启用受支持细项、入口为领域页而非旧静态盘、双时间方式、SHA事项绑定、连续断词、隐藏内部版号、Logo存在。历史本轮最初 Swift 换行串联的 CI 失败已记录并修正，完整 Xcode Simulator iOS build 以 `.github/workflows/ios_native_cast_parity.yml` 实际运行结果为准；**未签名、未在用户 Mac/iPhone 真机运行，更不是已发布**。
- **下一步真实发行工作**：实现每个细项自己的离线解读编排，先把 V3.9.1 正反证据/反例/应期真实移植健康病情轻重完整断案 → 新盘实测归档 → 本地历史收据事务/导出/隐私保护 → 正式 iOS AppIcon、隐私政策、TestFlight、商店审核；绝不跨话题虚构预测准确度。

## 2026-10-22 · 根据 iPhone 网页实机截图重构九宫可读性与静心后严禁冒充起盘

- **触发：用户提供手机截图，指出旧预览四张固定盘仍在起局后出现、四柱与“阴遁几局”混挤、九宫神星门/天地干/十二长生太小且乱、底部被 Safari 遮挡。** 这是对 iOS UI 的修复，不是新增古籍、重置规则或模型训练。历史 194 书例/43 章、81/42/17 规则和失败记录均不删除。
- **严格修正真实性：** `ios/design-v1/preview.html` 已删除可见的 `sample-switcher` 四盘切换栏。历史 `chart-facts-v3.js` 四张封存真盘继续保留供回归验证，**不许**因完成30秒静心就把它当刚起的新局。浏览器点击30秒结束 → `cast-unavailable`（“静心已完成、本次未起局成功、不会登记15天”），**不再** `navigate("board")`。九宫页面只可通过领域页上标明“查看九宫排版示例（不是新起局）”的显式按钮进入。示例页顶部也有“仅供查看排版·非实时起盘”明显提示。
- **HTML 九宫排版：** 日期标题、年/月/日/时四柱改四等宽格和更大字；“阴阳遁几局/旬首”独立横条，节气/值符/值使明确标签；九宫使用无圆角独立卡片的 **3×3 细灰分隔九宫**，每宫标题独立+五行地支、神/星/门 17px 主符号、天/地盘两栏、大字优先、地支长生分行、空/马/天墓/地墓独立标签、点击宫位详情展示详细依据；中五仍不伪造八神门星。五行色始终按各符号自身元素，不按层统一颜色。
- **移动端安全：** 旧 absolute bottom navbar 改 sticky flex 底部控件并留 bottom safe-area；主内容可滚动，避免顶部巨大留白和手机底部控件盖字。CSS 375–430px 响应式；最终布局仍需 Mac Safari/iPhone 真机人工截图确认。
- **原生 SwiftUI 也已对应重排：** `ProfessionalChartScreen.chartHeader` 独立四柱与局信息，`ProfessionalPalaceTile` 重写神/星/门/天/地/空马墓/长生清晰分层，字号提高。真正根据当前时间/手动时间的排盘 **仍由 `WenguaNativeCore.compute(at:timezone:)`，不是 JS 动态算盘**；原生日志/数据库/事项限制/30秒静心逻辑均不改。用户打开原生 App 依旧先选择领域、细分，成功保存才登记15天；浏览器不能起局、不假称完成断案。
- **测试：** 更新 Python UI 契约反向确认 `sample-switcher` 不存在、无 `data-sample=`、只通过示例预览进入固定盘、完成静心不会显示历史盘、四柱/局式/九宫字层/移动底栏样式生效。Source fixture 全部留存。过程中旧测试误要求 visible sample-switcher 的 CI 失败记录保留并修正；Swift accessibilityLabel 换行解析错误单独修复。检查当前 HEAD 的 GitHub `iOS V1 Design Contract` 及 `iOS Offline Native Casting Parity`，不得以仅 syntax-parse 宣称模拟器正式 build 成功。
- **未完成的产品门槛**：独立手机版 V3.9.1 完整自然语言推理并未移植；仅在原生 App 上真实算盘后展示核定事实。HTML 样例只是静态视觉验证。未来 iOS 仍需真机、TestFlight、正式图标和 App Store 审核。
