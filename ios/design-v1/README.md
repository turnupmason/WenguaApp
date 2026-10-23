# 问卦 · iOS V1 设计预览

这是 **2026-10-22 进入软件设计阶段** 后独立建立的可交互 UI 草稿，不是已构建、已接入推理或可以上架的 iOS 二进制程序。

## 最方便的交互预览：无依赖 HTML

仓库内 `ios/design-v1/preview.html` 是一个**完整单文件**原型，可在 Safari 中查看、点击：
- [首页] 今日问事领域（只有健康·病情轻重标记为首个已开发研究子主题，其他不伪装为已完成）
- [问事] 关系、可选问句、新病久病情况及明确的「此刻起盘」概念
- [九宫] 固定的、完全标示**「演示／非实时起盘」**的 2026-10-22 丙午 戊戌 己巳 庚午已验证真实源盘；点宫看星门神/天干；中五宫不造八神门星
- [断词] 展示 V3.9.1 11 栏顺序（样例未提供性别，因此10栏），不展示数值评分
- [依据] 查看支持和反证，不堆 SQL/古籍页码/哈希
- [记录/更多] 未来的本地历史、典籍、隐私配置占位

从项目根目录运行：

```bash
python3 -m http.server 8000 --directory ios/design-v1
```

然后在本机浏览器或同一局域网的手机 Safari 中打开：

```text
http://localhost:8000/preview.html
```

若用 iPhone 访问运行在 Mac 上的服务，需要把 `localhost` 换成 Mac 在局域网的 IP 并确保端口可达。HTML 设计预览不调用网络、不记录问事数据、不进行虚假的实时起盘。

## 原生 SwiftUI 设计源码（iPhone）

`../WenguaAppUI/WenguaDesignPreviewApp.swift` 提供完整的**独立 SwiftUI 视觉骨架**（首页/问事/固定样例九宫/宫位详情/断词与依据/记录/更多）。
- 推荐用 Xcode 新建 iOS App (SwiftUI，iOS 17+)；将该文件加入 target。若模板默认也有一个 `@main` 的 App 入口，请移除或替换原入口，**只保留本文件一个 `@main`**。
- 本版本不依赖第三方 Swift package；App Store 部署、签名和真机编译/验收尚未执行。
- Demo result 使用老版已核验的某个固定历史测试盘，与问事界面用户刚输入的问题**无关**；每页都明确标为演示。并非真正把 Python 运行在 iPhone 上。
- 未来接真实数据时只替换 `DemoPalace.originalSample`、`DemoReadingSection.sections` 和结果 DTO，不改整体页面导航/视觉组件。
- 目前项目中的 Python **权威参考入口** `src/wengua/health_text_pipeline.py:auto_cast_health_v39_text` 不可直接当成 iOS 本地 Swift 接口。需要移植确定性真实排盘与断词，或者经严格验证的本地原生桥接方案；必须通过跨语言每个宫位及11栏断词与原版一致性测试后才能启用正式「立即起盘」按钮。

## 视觉基线

- 颜色：米白画布 `#F7F6F1`，墨黑正文 `#232B29`，墨绿 `#153F3A`，金色辅助 `#AF9062`，浅绿 `#E8F0ED`。
- 清晰层级：首页轻量、问事关系取用先行、九宫全盘可点击、先综合断词后完整11栏、反证不隐藏。
- 顶层 3 tab：问事 / 记录 / 更多。保持可扩领域，不一次塞15个首页按钮。
- 每个九宫展示天盘干、地盘干、星、门、神、人物标记；特殊中五单独解析；点击宫位看详情。
- 标准手机系统正文可读性、辅助功能、深色外观、Dynamic Type、iPad 自适应需要在后续原生 Xcode/真机测试中完成。
- 历史书籍作者原文可以内部校核，消费者界面仅显示有合法授权的内容和适量来源提示。

完整产品、状态及下一工程门槛：[`docs/IOS_V1_PRODUCT_UX_DESIGN_2026-10-22.md`](../../docs/IOS_V1_PRODUCT_UX_DESIGN_2026-10-22.md)。

## 当前迭代边界

**现在是 UI 设计与原生代码骨架阶段**，不是完整 iOS app 完工。保持 V3.9.1 自然断词和全十二长生，无 V4.2 分数。新的评分、医学预测、云 GPT、强制60秒、假盘正式占断、提前标注 App Store 已通过均不可进入这版 UI。用户可就界面审美、问事输入步骤及九宫信息密度提出修改，确定后进行 iOS 真引擎移植与 TestFlight 测试。

## 2026-10-22 V2 参考图改版（以此节为准）

用户提供两张 iPhone 排盘截图，要求专业细线九宫排版、四柱/阴遁/值符值使顶部栏、宫中神星门天地干的四色高密度显示，**点击宫位展开精致分组详情**，并且**静心30秒、心诚则灵、尊重事实、同一件具体事15天内只能完成一次真实起局**。

- 直接打开 **[preview.html](preview.html)**：新版已覆盖旧简约卡片布局。手机 Safari 上九宫显示巽/离/坤、震/中/兑、艮/坎/乾，神橙、星绿、门蓝、天干红、地干橙，宫内标记实盘角色、十二长生与旬空；宫位详情可点击弹出。
- **起局入口**：选事项、患者真实关系、可选当事人称呼和新久病、日期时间选择器 → 静心30秒倒计时（不能跳过）→ 完成后**只查看固定测试盘视觉演示**。网页端尚无真实本机排盘引擎，不能把用户填写的时间冒充真的演算结果。
- **本地15天同题策略代码**：[issue-policy.js](issue-policy.js)。问事专题、关系、当事人、规范化事项的 SHA-256，只保存摘要与成功时间，锁定15×24小时；**仅正式离线起盘成功、记录已保存后**通过 `commitCompletedCast` 记一卦。网页演示绝不调用它，所以不会因为预览被锁。改写问句、换设备等无法靠这个简单摘要完美识别，正式应用需有明确事项ID管理。
- 同步原生 SwiftUI：[`../WenguaAppUI/WenguaDesignPreviewApp.swift`](../WenguaAppUI/WenguaDesignPreviewApp.swift)，使用 iOS 日期时间滚轮、不可跳过的 30 秒 `TimelineView` 与 CryptoKit/UserDefaults 的同题15天接口；还没有 Xcode 真机类型检查或完成本地 Python 算法移植。
- 实际固定示范盘改为**2026-11-01 05:00 美国东部时区**，这是已起盘核对的**未来测试时辰**，不是历史真实案件。来源是 `data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json` 的第一盘：阴遁五局，十天干完整十二长生。截图中的 10/22 16:39 排法仅供界面视觉参照，不移植其他产品流派差异。
- 运行测试：`python3 -m unittest discover -s tests -p test_ios_design_v1_contract.py -v` 和 `node --test tests/ios_issue_policy_v2.test.cjs`。Github 专项CI运行源书盘面对照与真实15天算法，不等于已 Xcode 上架。

**请以 V2 改版为当前视觉规范；前文首次 V1 文字仅是历史留存**。

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

## 2026-10-22 — 九宫显示延续开发（基于现有原生引擎，保留历史）
- **不是新项目**。已读取本仓库 AGENTS / STATUS / LEDGER / iOS 设计和 NativeCore。现有的 `WenguaNativeCore.compute(at:timezone:)` 是真实离线历法/时家转盘计算，本轮没有变更底层原书起盘规则、四柱和原书已验来源，亦没有重建数据库。
- `ios/design-v1/preview.html`：九宫细分隔线不变；依据封存4张审计真盘，宫内逐行显示 **每个天盘携干与地盘干对应全部真实辖支的十二长生**（含天芮／天禽双星），地支及干按各自五行色，空亡／时支马／天墓／地墓仍直接可见。中五只显示真实地盘干，不伪造神星门及无辖支的十二长生。
- 同宫、对宫与**真实墓支-马支地支六冲**为独立条件；纯宫位相对不得称“冲开”。如存在六冲最多标为**冲墓候选**，需原书其他条件，不自动作结论。旺相休囚废、六仪击刑、门迫没有独立审计状态字段时标明未实现，不能伪造已发生或错误断言未发生。
- `ios/WenguaAppUI/WenguaDesignPreviewApp.swift`：九宫和宫详情共用实盘 `WenguaNativePalace` 携带的天/地两盘十二长生；固定第一盘也基于既有原书12长生常量生成显示行。详情里双星分色、宫支逐一上色、天/地墓按**真实干五行**区分，不按神门星类别上色；遵守中五特殊规则。
- **四张演示盘现在也能在原生 SwiftUI 中选择**：只读样例时间为 2026-11-01 05:00、11-04 05:00、11-10 21:00、11-21 17:00（`America/New_York`）。SwiftUI 对每个固定时刻调用 `WenguaNativeCore.compute` **重新实算**，不预填九宫字段；`FrozenReadingV391.json` 为从既有 `chart-facts-v3.js` 等量复制的4条已封存 V3.9.1 源文本，切换盘时自动同步断词。它们仅是 **固定测试盘而非本次真实问事**，不能占用15天事项次数；若 JSON 资源缺失，拒绝拿其他盘断词填充。
- 新用户真正按“具体问事→30秒完整静心→确认起局”后，`nativeChart` 仍来自实时本机计算，15天 SHA256 事项限制继续只在成功算盘且记录保存后登记；**V3.9.1 新盘真实完整离线断词仍待移植，绝不冒充已完成**。
- 回归：新增 Node 对外围八宫天地盘真实十二长生、中五排除、双星携干和对宫非六冲的检查；原有对四盘的测试、Python UI 契约、15天事项测试持续保留。2026-10-22 首次新增的 Node 检查错误地要求无辖支的中五拥有 `earthStages`，CI 红灯已保存并由下一提交修正，不能擦除失败历史。
- 不改旧194原书案例、43章、81天地干、42疾病补充、17复合格局、原书错断和失败记录；不用 V4.2 数值评分。未签名真机测试/IPA/App Store 未完成，UI 图片视觉比对与真实 Xcode Simulator 手动交互仍待完成。按本次代码最新 Actions 核验新提交，不能以旧成功覆盖新失败。
