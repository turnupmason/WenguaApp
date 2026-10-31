# 2026-10-31 · iOS 首屏短断语与专业解盘分层修复（用户纠正）

## 真实问题及复现

用户指出 Swift 第一页只剩泛化短语，「吉局／凶局」及 V8 已确定的十档结果不见了；上一轮只恢复十档标题并加一行文学解释，仍违反此前 V10.1「约150–200字综合短断语」约定。

源码：`ios/WenguaAppUI/WenguaPremiumReadingView.swift`，旧代码虽然定义 `WenguaHealthGradeCaption.forGrade` 及分类，实际 UI 却以 `WenguaNaturalSeveritySummary.text(grade)?.0/.1` 覆盖了真正的 V8 吉凶标题，产生「有利线索较集中」等泛用文字；后来单纯用 `caption.interpretation` 一句话替代，又丢失了专业综合证据。这两种都是不合格实现。旧版本及失败 Git 历史不删除。

## 正确两页交付契约

**第一页「专业解卦」**：必须直接从离线真实 V8+V11 的 `90_review` 提取唯一已决等级，单独显示「吉局／凶局」（零分按用户批准的「微恙」）和「极大吉：沉疴顿愈」等十档固定标题；其下显示**约150–200字的本盘综合短断语**，包含真实病星与患者、天心与乙奇、在场时干及选中的家属辅助、真实的合宫吉助/空亡/有效制约与时局提示。非要借助原事实时，仅引用现有原生章节 `01_macro` 和 `91_timing`；不能捏造星门神、宫、角色、五行方向、分数或应期。不因示例字数压力虚造新条件，不再用泛用文案盖过真实吉凶等级。

**第二页「专业解盘」**：`WenguaNativeCustomerView(reading:reading)` 遍历 `reading.sections`，全部保留 V11 真盘的用神逐宫详细事实、81格、真假空及限制、完整 `90_review` 与应期。首页短断语不可覆盖详细原文、删除章节或重复加分。

### 实现边界

仅调整展示层 `WenguaPremiumReadingView.swift` 的 `WenguaVerdictPresentation.from` 和 `frontNarrative`，新增真实源证据段与有条件时局展示；**不更改** `data/templates/health_severity_vnext/reading_template.json`、`src/wengua/domain_selected_energy_vnext.py`、`WenguaPythonVNextVerbatim.swift`、V8.0 源200格/81格/矩阵/评分；原先 Python ↔ Swift 的 `reading.sections` 全文逐字对照仍为正式硬门槛。 `frontNarrative` 是原始章节的本地显示摘编，不是重新调用 GPT 或另起一次断案。

当前六盘真实历时样本：`docs/HEALTH_V11_SIX_REAL_COMPLETE_PREVIEW_20261031.txt`，按 Swift 展示拼接逻辑预核正文字符数约为 179/181/149/179/187/145（不含分类标题；忽略段落空白）。数字只表示样本文字长度，不表示评分。若合法盘真正证据不足，不为了达到字数而编造额外依据。

### 必须实际运行的验收

- `tests/test_ios_health_grade_copy_20261028.py`：断言明确显示分类、十档标题与 `verdict.frontNarrative(caption)`；拒绝泛用 `WenguaNaturalSeveritySummary` 恢复。
- `tests/test_ios_premium_result_ui_20261028.py`：断言专业解盘仍完整使用原始 `reading.sections`。
- `tests/verify_ios_premium_verdict_runtime_20261028.py`：macOS `swiftc` 编译并真实运行源 `WenguaVerdictPresentation` 解析器，11个等级与历史5份真实结论加 V11 六份真实时辰，核查首页正文约140–215字、人物病星医药证据保留且不泄漏注释。
- 必须另跑主 CI（Python3.11/3.12）、Swift native 全文 parity、XcodeGen iOS Simulator 构建和 app 200/81/模板/人物资源检查，不可引用旧成功冒充当前成功；失败记录保留。

本记录不构成医疗预后有效性结论。待核源力量依旧明确标记，出生年命没有证据不可补造。
