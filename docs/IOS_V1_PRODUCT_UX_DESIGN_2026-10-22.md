# WenguaApp / 问卦 · iOS UI/UX 设计方案 V1（2026-10-22）

## 决策状态与历史来源

**用户明确转入软件设计阶段**：「先这样吧。我们开始进入软件设计」。用户不要求恢复数字评分。V3.9.1 保持疾病轻重**纯自然断词＋全部实际十二长生**，设计阶段可开始；UI 设计稿并不意味着 V3.9.1 所有规则冲突已经消失或 iOS 已通过上架审核。既有早期 `app/` PWA 是用户不满意的旧原型；**不再以旧静心60秒+假九宫盘作为新 iOS 的默认界面，不覆盖它**。本文件与 `ios/design-v1/` 是独立、用户待审设计基线。

## 产品定位

- 名称：**问卦 · Wengua**；东方古籍研究与传统时家奇门问事工具，非医学诊断、治疗或疗效产品。
- 技术目标：**原生 SwiftUI iPhone 应用**、完整九宫盘、离线优先、可扩领域、不在移动端运行远端GPT。
- 首个已实现断词子场景：`健康 / 病情轻重`（V3.9.1 文本，不含分数）。其他健康子问题（用药、手术、出院、病愈应期）与婚姻、求财、考试等先是领域目录，**引擎未接入则显示“开发中”而非可占断**。
- 手机推理模块和 UI 相互隔离：原 Python `src/wengua/health_text_pipeline.py:auto_cast_health_v39_text` 是**研究参考及结果对照基准**，iOS 不可假设已能直接调用本地 CPython。须迁移/封装等价离线算法，逐盘验证四柱、九宫、断词和 81/42/17；**在原生执行引擎接通前仅演示设计、绝不呈现假算实时结论**。

## 视觉体系（苹果原生可读性优先）

- 设计方向：**东方简约 × 现代 iOS**，避免大面积阴影、轮盘动画、极低对比金字、故作玄虚装饰；九宫专业人士可读，普通用户先读摘要。
- 浅色画布 `#F7F6F1`，主文字 `#232B29`，墨绿 `#153F3A`，柔金 `#AF9062`，淡青 `#E8F0ED`，描边 `#E5E6DF`；深色支持系统适配，不把深色模式硬编码成唯一风格。
- 字体：iOS 系统字体作为正文（动态字重 / Dynamic Type）；重要栏目标题可用系统衬线中文字族回退；支持 VoiceOver、44pt+ 可触区、减弱动态效果、触觉反馈可选。
- 页面：首页、问事、结果、记录、典籍、设置。Tab 一级仅三个：**问事 / 记录 / 更多**（“典籍”和“设置”归入更多），减少底栏拥挤；“开始问事”是首页主按钮，不是 tab 项。符合 Apple HIG: tabs 用于顶层导航而不是操作。
- 九宫**巽4/离9/坤2；震3/中5/兑7；艮8/坎1/乾6**，天盘干/地盘干/星/门/神独立位置，中心五只显示真实的中五事实，不填常规星门神。用户可以切换显示层级“简洁 / 专业”；高亮**患者 / 天芮病宫 / 天心医者 / 乙奇医药 / 时干事体**，同宫多个身份用并列标签不重复计票。

## 关键流程

**A 首页（不强迫60秒）**：
- 顶部「问卦」，副标「观时 · 识局 · 明理」；说明“依据古籍的传统解读，离线保存”。
- 今日入口卡：健康 · 病情轻重（可用的研究能力），其他大类以真实状态说明“内容建设中”。
- [开始问事] 点击 -> B。静心60秒是**可选的仪式**，不可替代真实起盘或暗示提高预测准确度。

**B 问事信息**：
- 问事域=健康，具体问题=病情轻重。
- 独立必选**被问者与问者关系**：本人、父亲、母亲、丈夫、妻子、兄弟、姐妹、儿子、女儿、朋友其他（未定义关系需角色映射，不能默默映射成“本人”）。性别/出生年命和新病/久病若问事者掌握可填，缺少不伪造，不许一张盘推断实际患病事实。
- 用户自述描述选填，默认存在设备本地。可以选择“此刻起盘”，需要比较历史案例时另外进入“按指定时刻复盘”，两者**明显区分标签**。
- 显示设备日期、时间、系统时区；真实生成必须在用户点击“起盘”瞬间锁定时间，严格处理 DST 和所在地节气时点；除非用户明确选择历史复盘，否则不得偷偷改时辰。
- [静心片刻] 可选，[起盘并解读] 仅真实离线引擎已通过一致性验收时启用；原型用户点的是 [查看界面演示]，必须明确 **演示九宫非实时起盘**。

**C 结果（用户主要价值）**：
1. 标题「本次所问 · 病情轻重」、锁定四柱与阴阳遁局、可再次进入“盘面”的操作；
2. **九宫盘**默认占屏最多一屏，可滚动下看到结论；每宫点击展示星/门/神、天干关系、天/地盘、有序原书组合名、旺衰十二长生、空亡/墓库/击刑/马星、特殊角色；“简洁”界面仅显示简短星门标记，专业标签完整。
3. **一句话传统判断**来自 V3.9.1 最后断词的实际主证反证，不另生成新的 AI 概率、健康指数；与真正传出的原断词保持一致。未解决原书证据冲突要显示“含相反依据”，不假称确定无误。
4. 原完整十一栏目 V3.9.1（性别不明时十栏目）按层次组织：先「主要依据」「反面依据」「病情变化及应期」「完整断词」。可展开全文，**但绝不丢掉 11 栏源文字节**；可以折叠显示，不改写内容。
5. 「古籍依据」默认不显示 SQL、内部 hash 和行号，用户点击可看书名/章节/原文适度节选；不将有版权争议的整本古籍原文直接嵌入上架 App。
6. 底部常用 [保存本地记录] [重新问事]；分享明确先预览敏感内容，默认不上传。
7. 医疗题声明：“传统文化研究与象意解读，不是实际疾病诊断、治疗建议或医学风险评估。”不可根据象意建议停药、改医院或预测死亡。

**D 记录/典籍/设置**：
- 记录：本地保存时刻、问事关系、起盘版本、原盘和文本快照、引擎/知识版本（含原文可独立回溯），不默认云同步，不自动将健康问事用于广告。
- 典籍：方法目录/出处/术语，标注“已验证原书/实验补充/待校验”。如有整本原书版权许可问题，上架只给可合法展示的摘要和来源。
- 设置：深浅色/字体/数据导出和删除、隐私说明、流派（V1固定时家转盘）、版本号、离线状态。

## 技术契约与封装前闸门

入口参考 `auto_cast_health_v39_text(iso,timezone_name,inquiry)`。iOS SwiftUI 消费同结构 DTO：
```json
{
  "case_id": "local UUID",
  "engine_version": "v3.9.1",
  "mode": "traditional_text",
  "locked_instant_iso": "ISO8601 with timezone offset",
  "timezone_name": "IANA timezone",
  "domain": "health",
  "intent": "severity",
  "relationship": "self",
  "input_context": {"duration": null, "natal": null},
  "calendar": {"year": "丙午", "month": "戊戌", "day": "己巳", "hour": "庚午"},
  "board": {"palaces": "8 real outer + centre 5 special"},
  "roles": {"patient": 4, "tianrui": 6, "doctor": 8, "yi": 3, "hour": 1},
  "reading": {"sections": "ordered V3.9.1 10 or 11 original sections", "full_text": "original string"},
  "evidence": {"positive": [], "adverse": [], "counter": [], "conditions": []},
  "numerical_score": null,
  "statistical_probability": null
}
```
以上是**UI 数据格式草案**，不是已运行的 native Python/Swift bridge。优先用 Swift 端对照移植确定性排盘算法，iOS 内嵌只读 SQLite 与模板/来源层数据；对照原 Python 真四柱/九宫/十二长生/断词例子验证；是否应用 Rust共享核心可待实际 iOS 工程构建评估。不得靠静态示例盘假装成功移植。

- V0 交互设计原型：只使用明显标示的静态演示盘；不称可正式预测，不替代 V3.9.1。
- V1 本地计算：完成真实 Swift/Rust离线 port＋历史家族一致性测试＋本机 Xcode 编译调试，才解除起盘按钮。
- V1 Beta：真机、多语言字体、深色/大字、离线/后台、时区与夏令时、自定义时间、保存删除记录、隐私政策/法律版权/App Review 文案验收。
- 正式 App Store：按时最新 Apple review rules，尤其 health claim, privacy, false functionality, app-like native utility 做独立审核。不承诺“已可上架”。

## 当前阶段结果

现有早期 `app/` 网页占位不修改。新增 `ios/WenguaAppUI/...` 为 SwiftUI 的**独立原生设计源码起点**和样例数据；原生项目构建和 Python/Swift 真引擎绑定在后续工程阶段。请用户就**界面层级、配色与九宫密度**审核，不需重复古籍资料，不要求重启数据库。

## 用户两张界面参考图后的 V2 UI 修订（2026-10-22）

**用户新要求**：「我的九宫图要这样。而且我们还要静下心想这件事30秒，心诚则灵，尊重事实，一件事15天内只能起这一次。重新修改UI，宫位详情要弄得更好看。」来自用户本人上传的两张 iPhone 参考图。**这条修订覆盖上文“米白墨绿简单九宫卡片、静心可选、3 Tab”旧视觉方案**，保留时家转盘原书真起盘和 V3.9.1 纯断词/十二长生不变。

### 九宫图 V2 —— 参考截图的信息密度，而非修改源书计算方法

- iPhone 主界面采用**白色专业九宫**，三行三列用1pt细灰线无缝分隔；宫序严格巽4离9坤2／震3中5兑7／艮8坎1乾6。**不再是圆角分隔卡片**。
- 顶部先显示选定年月日时分、四柱天干地支四列、阴阳遁局、节气、旬、值符值使、时家转盘方式；日期时间页面使用平台原生日期时间选择器，SwiftUI 使用 `.datePickerStyle(.wheel)`。
- 每个正常宫采用截图风格：微字地支及已核算的十二长生、宫名/五行、八神（橙或红）、九星（绿）、八门（蓝）、天盘干（红）、地盘干（橙）、真实占事角色（患者、天芮、天心、乙奇、时干）与空亡小字提示。没有从截图抄入可能与本站算法不一致的门神星；**内容来自项目真实九宫计算**。中五只展示已知中宫结构，绝不填普通星门神。
- 固定设计示例采用项目 `data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json` 的第一盘：2026-11-01 05:00 America/New_York，丙午／戊戌／己卯／丁卯，霜降上元、阴遁五局、值符天禽、值使死门、甲子旬戌亥空。该日期是**固定已计算测试时辰（当前日期2026-10-22时在未来）**，不是历史真实问事案例、也不是当前用户实时起盘。八宫天干／星门神、角色／十二长生严格对应封存研究盘。第一张参考截图上的 2026-10-22 16:39 按其他软件规则显示阴遁八局，只作为视觉参考，不与本研究项目算法混合。
- 参考图里的五个 tab 可以采用「局式／起局／断词／案例／我」，其中案例／我部分仍是开发中占位，不假装已能办理真实断案。旧「多局／研习」移动原生版先作为占位，可继续研究导航；用户主要关心九宫视觉。
- 宫位点击后由底部精致详情 sheet 展开，不是原版表格：宫名／五行／辖支标题 → 当前用神角色与旬空胶囊 → 2×2神/星/门/天地盘干大字四色分类 → 原书十二长生与有序格局证据 → 宫位与问事角色关系／证据去重 → 原书非临床免责声明。长生宫含双支时两个支都显示，天芮天禽同宫分开标识但不重复病宫。
- 不在结果页引入V4评分、LVI、寿命预测或医疗指导。

### 一事一占、30秒静心和15天限制（不可误实现）

正式 **起局流程**：
1. 用户先明确具体一件事、被问者与当事人关系（真正用神绑定）、可选区分同类别人物的称呼、真实新病久病（如知）、年月日时与时区；
2. **必须静下心想这件事30秒**，文案「心诚则灵，尊重事实」，倒计时按实际经过的30,000毫秒，不允许中途“跳过”；离开页面中断本次静心步骤；
3. 完成后仍需用户主动点击「确认起局」，正式版在那一瞬间锁定实际起盘时间（如用户主动选历史复盘，须明确与当前起局不同），调用本地真九宫引擎、V3.9.1断词和完整十二长生；
4. **同一件具体事15天内只允许一次成功起局**。不错误地把「所有健康问题」或「同一人所有事情」等同一个问题。匿名离线初版使用专题＋关系＋人物标识＋规范化问题制作 SHA256 本地摘要，不存用户原文到去重键；读取上次真正完成的时间，15×24小时内拒绝重复，满15天才可再占；
5. **只有实际引擎成功计算并已把问事记录持久化后**才能提交15天记录；进入原型、预览固定样例、点击30秒静心、不完整起盘或出错，都不能把事件误标成已占。防止看到预览就被锁15天；
6. 真实语义同一问题即使改写用词，本地精确摘要未必识别；换设备、删除记录、篡改时钟也可绕开单设备锁。承认限制，App 不宣称全世界跨设备不可重复。若要严格意义的同题识别，必须保留用户能确认的“同一事项ID”，UI 可复用本地事项档案，而不是任意搜索患者敏感问题。所有记录本地优先，不上传病史/问事内容用于服务器比对；
7. 静心及“一事一占”作为用户希望体现的**传统仪式/自律原则**，不是科学预测准确性保证。健康专题仍非诊断。

### 实际已修改和测试

- `ios/design-v1/preview.html` 已直接更新为**可点击新版**：专业宫位彩色九宫、四柱顶部、真固定测试局、表单本地日期时间、原30秒倒计时、五项导航及现代宫详情底部弹层。可通过 `python3 -m http.server 8000 --directory ios/design-v1` 打开 `http://localhost:8000/preview.html`。
- `ios/design-v1/issue-policy.js`：SHA256本地同题键、15天从真正成功后开始、接口 `checkIssue` 与 `commitCompletedCast`；网页演示**不调用提交方法**，不假称完成真的起局。
- `ios/WenguaAppUI/WenguaDesignPreviewApp.swift` 已整体更新：图示源自同一冻结真实九宫、彩色专业3×3网格、分栏详情 sheet、真正iOS日期时间 `.wheel` 滚轮、`TimelineView` 30秒仪式、Swift CryptoKit/UserDefaults哈希锁定接口。**尚未本机 Xcode typecheck/真机测试，也还不能在 iOS 直接调用仓库 Python 起盘。**
- `tests/test_ios_design_v1_contract.py` 自动核查九宫内容与项目已经封存的八宫事实、宫序/中五特殊、30秒/15天流程与不调用评分；`tests/ios_issue_policy_v2.test.cjs` 用 Node 真测试同题规范化、15天到期、不同问事不误锁、无引擎计算不立锁、原文不留本地摘要记录。
- `.github/workflows/ios_v1_ui_design_contract.yml` 运行 Python 静态对照 + Node 十五天校验 + swiftc源语法解析（不是Xcode/SwiftUI编译）。真实本地 Swift 计算和保存结果之后才可能宣告15天限制端到端运行。此改动只涉及UI和客户端协议，不修改原书、全部194个案例、43章、81＋42＋17条规则，不生成新研究库来伪装研究前进。

**V2视觉基调**已改为截图的白/淡灰背景＋红/橙/绿/蓝专业符号，不再以旧版墨绿首页卡片九宫为正式主视图。用户继续审核宫位文字大小、密度和详情分组。

## 2026-10-22 V3 FINAL PREVIEW — STRICT FIVE-ELEMENT COLORS AND REAL PALACE STATUS

This section **overrides** the earlier V2 claim 'deity orange, star green, door blue, heaven stem red, earth stem orange.' The user explicitly corrected: **colors come from EACH SYMBOL'S OWN 金木水火土**, NOT its category, and **空亡、马星、入墓必须在九宫盘面直接显示**. User said “弄，我要看效果”，so actual browser/native source has already been modified; this is not just a design proposal.

- New `ios/design-v1/five-element-colors.js`: strict single color palette across deity/star/door/heaven+earth stems and relevant horse branch: 金 `#D39A19` gold/yellow, 木 `#18A557` green, 水 `#2679E7` blue, 火 `#E34B3F` red, 土 `#9C7447` earthy brown. 八神 fixed for THIS named tradition: 值符土、螣蛇火、太阴金、六合木、白虎金、玄武水、九地土、九天金. Other sources sometimes put 值符木; change requires new explicitly sourced variant, not random UI colors. 九星天蓬水、天任土、天冲木、天辅木、天英火、天芮土、天柱金、天心金、天禽土; 八门开惊金、休水、生死土、伤杜木、景火; ten stems standard 5 elements. Even mixed companion stems 辛（金）＋戊（土） within one palace get individually correct colors. 元盘四柱干 and branch also colored independently by five elements.
- **Real source-driven 4 complete boards and matching V3.9.1 natural readings** are now bundled as `ios/design-v1/chart-facts-v3.js`. Generated directly from frozen `data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json`, joined to all 10×12 stem-stage source records and the earlier V3.4 `HORSE[hour_branch]` mapping. Full four actual ancient-style cast samples have 8 accurate cells, separate center5, correct role names, all original customer sections (10 when sex unknown), no scores.
- Full browser `ios/design-v1/preview.html` updated IN PLACE. It now offers 4 frozen REAL COMPUTED sample time tabs (not new real live divinations), exact matching four pillars/solar term/bureau/void/horse/roles/sealed V3.9.1 text. Actual cell badges: `空戌亥`, `马巳`, `地乙戌墓`, `地丁丑墓` where real. Both heaven and earth tombs are **separate** labels; changing tabs recomputes all visible statuses from frozen true source facts, never hardcode 乾六 as always void.
- Specifically source sample #1 `2026-11-01T05:00:00-05:00` 丙午／戊戌／己卯／丁卯: hour 卯 ⇒ 驿马巳 **巽4**; hour 甲子旬 戌亥空 ⇒ **乾6**; true `地盘乙戌墓` in **乾6**, true `地盘丁丑墓` in **艮8**. IMPORTANT: none of its heavenly carried stems actually enters 墓, so do NOT label celestial illness stem as 墓 in this sample. Source sample #2 `2026-11-04` has **天盘庚丑墓** in 艮8; available through selector to visually test visible sky tomb.
- Detail sheet: five-element colored big cards for 八神、九星、八门、天盘干、地盘干, actual heavenly AND earthly lifecycle independently shown; every matched void/horse/tomb clause explains what exact branch and which plane triggered it; distinct source roles tagged; symbolic 古籍 not clinical diagnosis. Additional "冲墓" may be claimed ONLY with actual source-attested clash predicate; four default samples have **no real hour-horse six clash with listed tomb branches**, so none are falsely labeled 'opened tomb'. The user's earlier proposed opposite/diagonal horse as a possible tomb-opening condition remains an UNVALIDATED candidate rule; show horse and tomb independently until source-condition is finalized.
- Native `ios/WenguaAppUI/WenguaDesignPreviewApp.swift` now uses unified `QFive` five-element map, with source-derived 2026-11-01 hour horse 巳, 戌亥 void, source-verified tomb branch per stem (10*墓 anchors). It shows color by each symbol (including 辛金 and 戊土 individually in 天芮/天禽 same cell), colored stems/branches separately in four pillars, void/horse/heaven+earth tomb compact labels inside palaces and detailed palace sheet. No two-choice time selector for four samples in SwiftUI yet: it remains native UI source scaffold on sample1, not an iPhone-completed app.
- Source verification: `tests/ios_five_element_board_v3.test.cjs` checks five colors per symbol, 4 actual real computed source boards, horse/void/tomb source, both celestial/terrestrial distinction and missing false opened tomb. `tests/test_ios_design_v1_contract.py` checks same source history direct vs UI fixture, exact 4 reading sections and feature text. `.github/workflows/ios_v1_ui_design_contract.yml` checks Python source, Node static mapping, 15-day issue-lock tests, **real Node --check browser inline JS syntax**, external scripts and optional Swift source syntax parsing. Last full V3 passing workflow `https://github.com/turnupmason/WenguaApp/actions/runs/39858923586`, old failures retained (including discovered extra ] JS syntax error).
- Existing 30-second calm interval and specific-issue 15-day local lock unchanged (only successful real engine + record persist counts; demo never counts); no score or V4 numeric restored. Existing 194 ancient event sources, 43 chapters, original 81 pairs/42 distinct illness/17 composites, SQLite, AGENTS studies untouched. No new research database for UI-only changes. No iOS simulator / compiled Xcode test yet.

**Status: actual interactive preview implemented and syntactically/source tested, waiting for user appearance review, NOT real mobile native casting.** Open `ios/design-v1/preview.html` with its siblings `five-element-colors.js` and `chart-facts-v3.js` under local static server. Never claim GitHub blob itself runs JavaScript inside GitHub page; browser must serve HTML/JS from same origin.
