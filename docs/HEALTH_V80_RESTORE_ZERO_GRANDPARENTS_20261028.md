# 2026-10-28 用户纠正：疾病0分恢复中性／爷爷奶奶独立长辈候选

原始同一盘：2026-10-28 13:44 America/New_York，丙午、戊戌、乙亥、癸未，阴遁2局。本人用日干乙艮八；同事用月干戊离九；物理入选宫同为9/7/8/6，基础-4 + 合格同宫吉助4 = 真实0。这个同分不是私自复用人物；绝不可改200格、81格或多计一次同宫来人为区分。

**用户明确改回：** 已真正解析的0分使用原`overall_resolved`之「不凶不吉」，UI既存「微恙／病势平缓／病情稳定不凶不急，调理即可」不改；之前自主引入的0分`neutral_conflict`慎断文案不再参与最后客户结论。真正缺评分`None/nil`仍待定，非0分的源冲突仍追踪。旧反例及失败原始记录见 `docs/HEALTH_V80_ZERO_CONFLICT_20261028_1344_AUDIT.md`，不删除。

**实际病宫：** 离九实有天芮/天禽两颗，天禽携丁，病宫天盘不含乙；真正乙奇在艮八。病宫两天盘携干对同一个地盘干分别各算一条有序81格，天禽不再作为第二天芮星重复记基础。丁奇已按源强度、限制符合条件+3，兑七天心逢空加1，特殊吉助总4。除非实际两颗星各带独立合格乙丁，否则不得假加第二个乙奇+3。

**人物：** 原App只列父母、其他长辈，本次增加爷爷（问时年干人物候选＋男性乾六）、奶奶（问时年干人物候选＋女性坤二），出生年命未提供绝不补造。原书未发现爷爷奶奶各自专例，严格标注`conditional_older_generation_analogy_not_exact_case`，不伪称原著明确同等验证。Python v21 + V8 selected roles 与原生Swift共同按角色独立绑定并拒绝输入性别冲突；宫分去重及全宫事实规则不改。

变更代码 `src/wengua/domain_selected_energy_vnext.py`、`ios/WenguaAppUI/WenguaNativeVNextEngine.swift`、`WenguaPythonVNextVerbatim.swift`、`WenguaNativeActorBinding.swift`、`WenguaNativeReadingRouter.swift`、`health_dynamic_v21.py`、`actor_profiles.json`；原盘回归 `tests/test_health_20261028_1344_two_person_audit.py` 和 `tests/test_health_v80_grandparents_neutral_20261028.py`。修改新HEAD后必须重新执行CI/Swift全文parity/Xcode资源核对，未跑不得称通过。已揭晓旧病案不是盲测；传统象意不是医学预后。


## 2026-10-28 本次真盘修正的实际回归结果（失败先留档）

- 首提交 `81b84fc`：现行Python V8主CI `#40744813221` 3.11与3.12 PASS。原生全文 parity `#40744813493` FAIL：不是算分或Swift失配，`scripts/ios_v80_same_clock_neutral_parity_20261028.py` 第33行仍错误断言「0分不许输出不凶不吉」；失败归档 `docs/HEALTH_V80_FAILURE_RUN_40744813493_ATTEMPT_1.md` 永久保留。修正于 `bb42698`，主CI `#40745150935` PASS，V8真盘+20随机Native Swift逐字 `#40745151126` PASS。
- 进一步扩大到四种人物：`de86559`更新同一真时辰源数据导出，`4bfbaaf`更新专项CI循环；全套原生Swift与Python逐字对照 `#40745505469` PASS（本人、同事、爷爷、奶奶，同一真实13:44）。总分分别0、0、5、5，爷爷奶奶实际未封顶和分别9、7，并非复用人物；这些均为传统计分，不能声称预后准确。
- 初始本次macOS Xcode Simulator工作流 `#40744813002` FAIL：SwiftUI真正编译成功，**bundle验收脚本仍断言20角色**，新增后实际22；旧失败文件 `docs/IOS_V80_XCODE_FAIL_RUN_40744813002_ATTEMPT_1.md` 已保留。修正于 `3618af6`，验收明确检查22身份和爷爷乾6／奶奶坤2。新构建 `#40745274121` 启动并等待返回最终结果，未返回前不得宣称PASS或bundle验收成功。
- 最新V8主CI `#40745504665` Python3.11/3.12 PASS。原200/81、冻结两已揭晓原盘、旧失败历史没有被修改。
