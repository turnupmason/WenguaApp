# WenguaApp · GPT/Python 与 iOS/Swift 严格一致性契约（2026-10-26）

## 用户设定的最终验收标准

同一个真实时辰、IANA 时区、领域+细分、问事关系、性别/年命等明确条件，使用 **同一份最新用户规则、源数据和编辑模板**，两个运行端分别执行计算。只有当：
1. 原生起盘和 Python 九宫盘事实一致；
2. 200 格用户能量表及 81 有序天地格、十二长生、墓、击刑、五不遇时、全盘伏反吟、门破、真假空、同宫去重、五类八神（无月令）、实际五张克制表和择取角色 **每一项已触发内部证据**都一致；
3. 内部评分和导向证据一致（内部记录，客户文字不展示任何加减分）；
4. **Python 真正的 `auto_cast_health_review_text(...).reading_text` 与 iOS 正式入口 `WenguaNativeReadingRouter.compose(...).sections` 重组后的整篇中文原字完全一致**，包括 section ID、顺序、标题、正文、古诀、标点、换行，**任何不同即 CI 红灯**；
才允许称为该领域当前已验收条件的「同实现跨平台移植」。不得只因为九宫或最终内部总分相同就宣布完整接通。

## 当前唯一完成严格全文对照的专题：健康 → 病情轻重（health.severity）

| 职责 | Python（研究权威源） | iOS Swift（产品离线执行） |
|---|---|---|
| 天文历算、时家起盘 | `astro_calendar.py`、`casting_shenqi.py` | `WenguaNativeCore.swift` |
| 病情领域选择、人物用神 | `health_severity_vnext_review.py`、`patient_role_binding`及已有20类人物档案 | `WenguaNativeActorBinding.swift`、`WenguaNativeReadingRouter.swift` |
| 200 格星门干强弱及五张克制表 | `user_domain_matrices_20261023.py`、`factor_energy_25_rules.py`、`health_quant_overlay_vnext.py` | `data/mobile/health_vnext/health_energy_200.json`（同源导出并 CI 逐格校验）、`WenguaNativeEnergyBundle.swift`、`WenguaNativeVNextEngine.swift` |
| 81 有序天地格及古诀 | `health_81_excel_catalog_vnext.py`、同一 `81_pairs.tsv` | `WenguaHealthTemplateBridge.swift`、同一 `81_pairs.tsv` |
| 天芮星宫25类命名/证据限制 | `health_tianrui_25_matrix.py` | `WenguaVNextTianrui25.swift`，源代码并行验收（尚非全组合穷举） |
| 最新用户断词 | `domain_selected_energy_vnext.py:selected_health_sections`、`health_reading_template_vnext.py`、`health_palace_detailed_vnext.py`、`health_relationship_language_vnext.py`、`health_macro_facts_vnext.py` | **正式生产入口** `WenguaPythonVNextVerbatim.swift`，使用同一 `data/templates/health_severity_vnext/reading_template.json` 的 `macros` 与 `section_titles`，不再走独立概括文本 |
| 客户机 UI | Python `reading_text` 的全量原字 | `WenguaNativeReadingRouter.compose` → `WenguaNativeCustomerView`，客户只有文字、不显示内部计算分数 |

**注意：** 仓库里的全部 `.py` 辅助/入库/训练/研究实验、全部古籍原文和 SQLite 保留 GitHub，不需要复制成 Swift 或随 App 发到用户设备。只有真正用于运行当前专题的规则计算必须等价移植，不可偷改原规则。未来每次人工更新本地 JSON/TSV 后必须重新构建手机 App 并跑源一致性 CI，已经发布的设备不会自动从 GitHub 更新。

## 2026-10-26 可复现的严格测试（保留每次失败）

- 随机种子 `202610263311`，固定 UTC offset-aware America/New_York 真实时辰：`2024-09-02T05:00:00-04:00` 本人、`2022-04-05T17:00:00-04:00` 父亲、`2024-10-13T15:00:00-04:00` 妻子。
- **完整客户文本逐字对照通过**：[GitHub iOS parity #40390048734](https://github.com/turnupmason/WenguaApp/actions/runs/40390048734)；Python 端实际计算不是读取 Swift 结果，Swift 真正编译运行。该源码还通过真 macOS iOS Simulator 编译。其后改进测试又要求同源 section ID/顺序/标题/正文与生产入口严格一致，最新结果按相应 head_sha 的 Actions 为准。
- 研究内部 5 个既有真盘逐因素评分及 3 个新随机盘九宫/天芮25/角色/200格/81格/真假空及定向克制表输入输出已进行逐项对照。这只是针对**已测分支**，不代表每个日期、宫位和取用关系均穷举。
- 失败 [#40389982048](https://github.com/turnupmason/WenguaApp/actions/runs/40389982048)：3盘里第一盘全文相同，父亲/妻子盘只有「乾坤辅助宫」称谓 `受生/比和` 与 `被生/同宫` 不一致，修复为 Python 原函数 `marriage_runtime.element_relation` 的独立辅助规则，保留失败数据；其它历史失败均保留。
- `.github/workflows/ios_native_cast_parity.yml` → `tests/compare_gpt_ios_exact_wording_20261026.py` 是**硬阻断发布的字节/字符级门槛**，不允许合并或忽略 FAIL。先以真实源码逐项对齐，再修改 Swift，不可拿 Python 生成的断词作为 Swift 的运行时查表答案。
- Python 源分别输出 `source_sections` 与 `python_reading_text`，Swift 必须取自**手机生产 compose** 而不是孤立样例或临时替代函数。客户存本地 `LocalNativeCase.reading` 时不能包含内部 `score`、`postVoidKnownSum`、`raw`、`energyEvidence` 的数值。
- 任何未来新的子领域先列出精确 Python 源模块、输入 DTO、规则表、模板，然后移植 Swift、建立同盘逐因素+全文章节逐字双重测试。其它领域不能套用病情轻重模板，更不能声称全 App 已完成；目前明确只有 `health.severity` 有上述严格验收。

## 当前未交付与上架边界

1. 未做到所有20类人物关系×全部时辰的独立实盘覆盖；条件性取用和年命缺失要明确暂不强断。
2. 未穷举全部历法节气边缘、值使中五未核寄宫、墓刑/空亡冲填所有分支和天芮25×实际角色情境。不能将3盘结果外推为「任何盘永久逐字一致」。
3. 其它14大领域及疾病其它细分尚无同等级原生 Swift 规则移植/严格全文对照，**不能宣布 GitHub 全部 Python 代码均已转换 Swift**。
4. 未签真机 IPA、未完成 App Store Connect/TestFlight 和 Apple 审核。本轮是研究性传统文化软件计算一致性，不是临床真实性证明。

开发原项目 `turnupmason/WenguaApp` 不 reset，不清除旧版本/历史失败；更新进展同步 `AGENTS.md`、`docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`。


## 2026-10-26 本对话扩大随机原字验收批次（等待该提交 CI 实测）

- 保留种子 `202610263311` 的既有3张真盘、旧成功和失败 GitHub Run，不重写历史结论。
- 新增**独立随机种子 `202610265117`、9个技术可计算的有效真实钟点**，`scripts/ios_vnext_three_random_20261026.py --seed 202610265117 --count 9 --output ...`；按第1至第9个成功技术盘循环本人、父亲、妻子，不凭凶吉筛盘，技术拒盘按抽样次序入 `rejected`，不计成功。
- **手机正式路由端**用与原三盘相同的已编译 `VNextThreeRandomNativeFullCheck.swift`：逐实际真盘重新调用 `WenguaNativeCore.compute`、`WenguaVNextEngine.compute`、`WenguaNativeReadingRouter.compose`，无缓存的预存九盘断词。源端则对同一 `instant/timezone/inquiry` 独立调用 `auto_cast_health_review_text`。
- `tests/compare_gpt_ios_exact_wording_20261026.py` 除全部中文与段落 `id/title/text` 完全相同外，另强制对齐时辰、人物、顺序号和分段数量；不能把其它盘答案放到当前盘后仍报通过。新增独立防伪比较器 unittest，故意错换时辰、漏盘、改标点必须红灯。
- GitHub Actions 每次同时保留这9盘的 Python 金标、Swift 原生 stdout、差异日志，即使失败亦不删除。**在该源码最新 HEAD 对应 native_core 和 macOS `real_ios_xcode_build` 确认成功前，该9盘状态为待验，不得预报9/9通过。** 不变：健康病情轻重专题才有已移植路径；其他14专题与全部20人事条件不能因此冒称完成；评分仅内部，保留历史V3.9.1和43章194古籍案例。
