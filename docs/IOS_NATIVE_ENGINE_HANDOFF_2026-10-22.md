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
