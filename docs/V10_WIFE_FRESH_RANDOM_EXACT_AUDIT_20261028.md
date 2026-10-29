# 2026-10-28 V10 客户模板接线审计及妻子全新随机实盘

## 事实来源、版本与边界

- 正式 GitHub main 源码（本轮测试提交）：`e0ed3a06016795a519ea75ae422f3bc7b0687d09`；该 commit 仅追加独立妻子随机测试，**未改冻结的疾病 V8.0 200格/81格/人物规则或客户模板文字**。
- 模板 schema：`health_severity_user_editable_template_v20261028_v10_concise_confirmed_friend`。
- 真正双端原生工作流：[run #40791724841](https://github.com/turnupmason/WenguaApp/actions/runs/40791724841) **PASS**，包含新妻子单盘及朋友/两已揭晓盘/13:44四角色/其它随机盘；单盘 Python↔Swift 严格章节 ID、标题、正文逐字一致，1/1 EXACT MATCH。
- 当前主 V8 CI：[run #40791724790](https://github.com/turnupmason/WenguaApp/actions/runs/40791724790) **PASS**。对相同 V10 源码的最近真 macOS XcodeGen + Xcode Simulator + 四类包内资源校验：[run #40784209785](https://github.com/turnupmason/WenguaApp/actions/runs/40784209785) **PASS**；该构建为之前同一应用源码（498cc54d），不是本次工作流测试提交的新构建，不可偷换成新 Xcode run。
- 原生完整客户输出和原始对照结果：[追加归档](HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40791724841_ATTEMPT_1.md)；保留历史版本和失败记录。

## 随机方法（非已见朋友案例重用）

- 源自现有 `scripts/ios_vnext_three_random_20261026.py:produce`，随机种子 `202610282003`、`count=1`、`wife_only=True`；从 2020–2025 不同真实纽约本地整点辰时等随机技术候选中取首次可起盘的一盘；不按宫位、评分或结论择盘，技术拒绝样本也保留在 workflow artifact。
- 实际时辰 `2025-10-15T07:00:00-04:00`，寒露，中元阴遁九局，四柱 **乙巳/丙戌/丁巳/甲辰**。
- 问事 `health.severity`，人物 `wife`，`direct_proxy`，女性；妻子主用乙奇在坎一，乙奇医药同一真符号、同一坎一，不能重复算独立宫基础吉凶；日干五合另参，未提供年命不补，非长辈无乾坤性别辅助宫。
- 天芮落坤二，天心落乾六，值符实际八神同在坤二，时干甲辰同坤二；坤二有 `丙加丙/月奇孛师` 及 `壬加壬/蛇入地罗` 两个有序81格。中宫不另立普通宫象。
- 本盘天显逢伏吟；依正式规则 3 个去重真实选定外宫，天显半分按 3 × 1.5 = 4.5 **统一最后向下取整为4**，而非逐宫取1；伏吟主慢，五不遇时不成立。最终 V8 有符号总分饱和 -5，传统分档「极大凶」；不能据此推断真实健康或作为医疗依据。

## V10 全链接线证据

1. UI `WenguaDesignPreviewApp.swift:completeNativeCast` 通过 `WenguaNativeReadingRouter.compose` 加载 bundled `reading_template.json`、81对、200格、人物 `actor_profiles.json`，走 `WenguaNativeCore` + `WenguaVNextEngine.compute` + `WenguaPythonVNextVerbatim.sections`，再由 `WenguaNativeCustomerView` 显示；非静态假盘。
2. Python `src/wengua/domain_selected_energy_vnext.py:selected_health_sections` 及 Swift `WenguaPythonVNextVerbatim.sections` 都真实调用 V10 `palace_compact`、天显伏吟客户句、五不遇客户句及同宫去重；不把内部分数/矩阵显示给普通客户。两端此次妻子全文逐字 PASS。
3. `data/templates/...` 和 `Important/python`、`Important/swift` 的 V10 模板 Git blob SHA 相同；妻子人物规则JSON、Python领域主文案、Swift客户文案双镜像SHA也完全相同。
4. 精确比较并不自动证明八十一格资料的历史原著真实性、所有未出现的同宫组合已穷尽、真机签名或现实疾病预测的有效性。

## 审计发现而未私改的文本可读性问题

- 本盘 V10 主文逐宫仍重复「全部因素推断后，此宫为…」，综合段重复「乙势小，受病宫克」两次（医药与患者同一乙虽不重复计分，**公众文字仍有冗余**）。这属于表达优化候选，不是V8计算失败；未经审定不在本次演示前偷偷改词或改分。
- 当前 template JSON 内仍保留旧版本说明、可展开研究短语和原81古文字段，供审计/详情使用；客户实际 V10 仅输出精简分支。静态文件有旧语句不等于产品向观众展示旧模板。
- 其它领域仍非疾病模板的已验收生产范围；旧独立全库 CI 的历史失败和旧版约束未因此「全部通过」。

## 本轮交付结论

**V10 已经接入当前健康轻重的 Python 和离线 Swift 正式客户输出；新的妻子实盘以原生 Swift 严格逐字复算成功。** 保留源规则、已揭晓病例、未决审计和所有失败现场，不调整冻结 V8.0 评分。
