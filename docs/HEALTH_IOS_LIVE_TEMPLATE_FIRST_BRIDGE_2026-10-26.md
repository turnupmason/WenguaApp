# 2026-10-26 · 两个新随机时辰与 iOS 最新模板接线（第一阶段）

这次不改任何原书、案例和历史失败版本，不重开现有拆补排盘；只在现有开发版本中增加 **真正读取用户已编辑 JSON＋81格 TSV 的 iOS 原生桥接**，以及固定随机种子两张真实软件演示盘的自动回归。不是临床病人或古籍作者盲测。

## 两个无吉凶筛选的新增时辰

- 算法：Python `random.Random(20261026)`；按顺序在 2022–2025 年随机年份、月份1–12、日期1–28、奇数小时1..21 取两次；唯一时区 `America/New_York`，关系 `health/severity/self/direct_self`，没有出生年命、病程、真实性别，不替用户虚构输入。
- 抽中 1：**2022-04-22 05:00 America/New_York（EDT）**。
- 抽中 2：**2025-07-18 03:00 America/New_York（EDT）**。
- 真正逐盘完整报告**由** `tests/test_health_two_random_template_20261026.py` **在 GitHub WenguaApp CI Python 3.11/3.12 中运行当前真实函数** `auto_cast_health_review_text` 得出，日志前缀 `WENGUA_20261026_TWO_RANDOM=`；若实盘报错，保留失败并修程序，不为凶吉重抽。
- 输出结构包含四柱、节气、局、五不遇/伏反吟、真实用神宫、最新200格/81格/宫位分数相关 DTO、全部原模板段落、完整中文断词及吉凶结论。没有真实历史反馈，绝不把这些软件盘当作两书第195/196案。最终软件结果请以**同一最新 commit 的成功 CI 日志**为准，不把本文件的未来执行设计写成已通过。

## iOS 已接入的边界

- `ios/WenguaAppUI/WenguaNativeCore.swift` 原封保留九宫排盘算法。
- `ios/WenguaAppUI/WenguaHealthTemplateBridge.swift` 是 **Foundation-only、无网络连接** 的正式第一阶段资源桥：从 App Bundle 读取当前 checkout 的 `data/templates/health_severity_vnext/reading_template.json` 和 `data/knowledge/health_81_excel_20261025/81_pairs.tsv`，严格验证 81/81 × 七列、25吉56凶和格式占位符。只对 Swift **现场计算的真实本宫** 天盘每一携干 × 其实际地盘干输出 `formation` 字符串，天芮/天禽同居则各按真实携干列出；中五不能生成普通神门星／格局。
- `ios/WenguaAppUI/project.yml` 将**仓库唯一的两个权威源文件**作为资源打包，无重复维护的伪 JSON；`WenguaDesignPreviewApp.swift` 新盘解读页显示「本盘81格原文与模板实时替换（基础事实，尚非完整断案）」。模板缺失/81格错列则显示阻断信息，不从历史封存四盘补文，不提示吉凶有效。
- `ios/WenguaAppUI/HealthTemplateBridgeCheck.swift` 双真盘+81格缺行阻断测试通过 Linux Swift CLI 执行；`tests/test_ios_health_template_bridge_20261026.py` 验证真正资源路径与 UI 使用；`.github/workflows/ios_native_cast_parity.yml` 增加 Swift 编译实测及 macOS Simulator XcodeGen 编译。**并非 V-next Python 200格和±5全链已经移植**；也不是已签名的 iPhone/TestFlight 安装包。
- 下一工程阶段是按现有用户指定健康人物关系（含父亲年干、性别辅助与真实年命有则取）逐宫绑定、200格强弱、宫位±5和真假空±3、宏观五不遇/伏反吟、角色对天芮的有向生克、同宫一次计分、应期条件 → `verdict`/全部中文断词的原生移植，与 Python 逐盘逐字段比较。**达到这个门槛前不在 iOS 假称完成完整占断**。

## 自己如何立即人工改模板（GitHub）

1. [最新 V-next 断词 JSON](../data/templates/health_severity_vnext/reading_template.json)：改 `formation`、`section_titles`、`macros` 等可读汉字，保留所有 `{heaven}`/`{earth}`/`{name}`/`{polarity}`/`{classical_text}`/`{classical_meaning}`/`{imagery}`。Python 其他替换字段也不可随意改名。
2. [81格权威原文 TSV](../data/knowledge/health_81_excel_20261025/81_pairs.tsv)：按实际有序天盘干×地盘干七列调整格局/吉凶/古文/释义/象形；不删行、不交换天/地盘。
3. 用网页 Edit（铅笔）→ Commit changes 到 main；查看 `WenguaApp CI` 与 `iOS Offline Native Casting Parity`。GitHub 提交**不等于自动推送到 iPhone 已安装旧App**：下载最新代码后在 Mac 用 XcodeGen/Xcode 重编译安装才会带上修改后的 Bundle 资源。Python本地进程如果已缓存模板需重启。
4. 只有用户编辑 **话术** 才改 JSON；修改能量矩阵在 `src/wengua/user_domain_matrices_20261023.py` 及用户 V3 原表规范；更改角色算法/总分属于真实 Python/Swift 计算规则开发，不能仅靠编辑句式实现。

范围：**两书43章194事件数量完全不变**，旧 V3.9.1、弃用 V4.2、数据库归档、用户200格及 Excel81格、原起盘、所有失败Actions继续保留。


## 首次实跑发现的旧引擎守护拒盘（故意保留 CI 失败）

首次 CI `40342643735` 在抽样阶段真实触发 `ValueError: Timed value door falls into centre 5; hosting rule not yet confirmed`。这说明随机候选时辰**并非全部能出完整九宫**，不能为了满足数量把中五值使硬寄宫。原来文档列出的2022-04-22与2025-07-18是前两次**抽样候选**，不应在未通过引擎之前称作“两份已出结果”。修订测试只按相同 seed 和随机序列往下取，允许跳过这个已知寄宫保护/已核人物落宫失败；所有跳过记录 `WENGUA_20261026_TECH_REJECTION=`，成功的前两个可计算新盘才打印 `WENGUA_20261026_TWO_RANDOM=`。失败 run 历史保留不删除，实盘选择绝不检查吉凶再重抽。
