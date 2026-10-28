# iOS 云境欢迎页与分领域问卦 · 2026-10-28

本次仅为正式 SwiftUI 原生离线 App 的展示与用户步骤调整，不调整V8.0疾病起盘、200/81源格、专业打分、原中文断词、两固定原时辰回归与原书原文。

## 首次打开
- 全屏「欢迎来到问卦」：本机 SwiftUI 渐变、柔光、流云缓慢动画、金色品牌主按钮。视觉素材无联网请求、账号、云模型调用与下载依赖。
- 宣传措辞「根植《神奇之门》《开悟之门》；以古籍为据，以规则为尺；依真实时辰起局，逐宫推演」。强调真正的传统象意解盘而非仅排九宫；**不声称已科学证实预测正确率或能保证避险**。
- 点击「开始问卦」才进入「请问你有什么疑惑？」的双列领域卡渐显页；点领域后再选细分事项，再填写人物、问题与情境。未正式验收的领域显示「开发中」并不可提交起盘，疾病V8.0专属断案不向其它领域复用。
- 白天／夜间／跟随系统在欢迎页、领域页、结果页可直接切换（`@AppStorage("wengua:appearance")`），主要卡片颜色使用动态系统surface；欢迎舞台固定深海云境风格，模式影响内部页面而非伪造另一套主题算法。

## 现行计时与静心
- 用户这次明确取消前端「手选日期时辰」和「闻讯按事件时间起局」选项。仍需明确一个具体问事、选领域/人物/可选年命与病程，完整30秒静心后按「确认起局」键。
- **只有按确认键当刻 `Date()` 与 `TimeZone.current.identifier` 进入 `WenguaNativeCore.compute`**，且只有原生 V8 完整断词和本机存档成功才登记同一事项15日限制。保留历史回看；不修改旧记录中的原盘原断词，历史若无新UI角色元数据则不凭空猜标记。

## 真用神宫位视觉层
- 唯一现行疾病模型 `WenguaVNextEngine.compute` 产生 `review.roles`（`role_key -> palace_id`），仅在`WenguaNativeCustomerReading.rolePalaces?`另存**只读显示元数据**。只加真实落宫映射，不暴露原始评分，不重新选用神。旧存档字段缺失时可选解码且背景身份留空。
- 落宫透明底字：天芮=「病」，天心=「西医」，乙奇=「中医」，值符=「大吉神」，时干=「病事」，关系主用神=「被测人」。本领域存在实际年命/长辈乾坤选择时才加「年命／长辈辅助」。同一宫多角色按固定显示顺序以「／」组合，如「病／被测人」；**同一位置显示多标签不新增宫分、更不认定其实际克病成功**。
- 字样为微透明衬底，不遮蔽星门神天地干，中央中五宫不补普通神门星。🐎与逢空圆圈仍仅由每宫真实`horseBranch`、`voidBranches`产生，墓与长生在宫详情可查；应用户要求去掉八门之下、天盘之上的分割线。

## 两级解盘、滚回顶部
- 「接卦」先显示九宫与 V8 已核验`90_review`结论、`91_timing`条件应期，未核验不填结论；「专业解盘」用读原文的暖金版块排出完整原生V8段落、九宫事实和完整附注。两处含「回到顶部」按钮，`ScrollViewReader.scrollTo("readingTop")`，历史记录也支持。
- 200格、81格、天芮克制矩阵、V8源模板、所有真实强弱、五不遇时、15日锁存原状。**其它领域一个领域一个独立`DomainProfile/SignifierRole/RelationRule/Timing`和可编辑模板**，可共享真盘及月令五行基础事实，但不共享疾病条件分或全领域固定应期。

## 修改与验收入口
- `ios/WenguaAppUI/WenguaDesignPreviewApp.swift`：root导航、结果标签、宫格身份/遮罩、设备当前时刻、滚回顶部与适配色。
- `ios/WenguaAppUI/WenguaCloudWelcome.swift`：离线科技云舞台、品牌欢迎和3选1外观设置。
- `ios/WenguaAppUI/WenguaDomainJourneyScreen.swift`：疑惑引导→领域→细项并渐显。
- `ios/WenguaAppUI/WenguaNativeReadingRouter.swift`：仅多存一个可选`rolePalaces` UI元数据，不影响校验过的sections。
- `ios/WenguaAppUI/WenguaNativeCustomerView.swift`、`WenguaPremiumReadingView.swift`：专业分节、标签背景和滚回顶端。
- `ios/WenguaAppUI/project.yml`、`Important/MANIFEST.json`与各Swift镜像同提交。
- `tests/test_ios_immersive_journey_20261028.py`：本次新的静态契约测试；实际macOS iOS Simulator XcodeGen编译和四项资源打包检查仍须读相同提交触发的workflow。静态测试或Python/Swift文字一致不等于真机UI交互验收。

本次是UI增量而非逐书新章：0新原书、0新原著案例、0V8计算规则改动。历史失败和旧版文件全部保留。
