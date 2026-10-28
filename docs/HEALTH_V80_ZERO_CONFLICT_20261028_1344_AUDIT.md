# 2026-10-28 13:44 实时同盘本人／同事「中性0分」反例与慎断修复

## 1. 实际复现范围

用户提供的iOS截图显示`2026-10-28 13:44`、霜降、阴遁2局、四柱丙午年/戊戌月/乙亥日/癸未时。用完整生产 Python `auto_cast_health_review_text(iso="2026-10-28T13:44:00-04:00",timezone_name="America/New_York")`，分别用`{"relationship":"self","consultation_context":"direct_self"}`与`{"relationship":"colleague","consultation_context":"direct_proxy"}`做严格**同一实际时辰**对比。不使用截图库盘或示例静态盘冒充真实起局。复现测试在`tests/test_health_20261028_1344_two_person_audit.py`，GitHub Actions #40739720539 3.11/3.12 已证明独立实测打印。

| 字段 | 本人 | 同事 |
|---|---:|---:|
| 真实人物主用神 | 日干乙，艮八宫 | 月干戊，离九宫 |
| 人物角色来源信度 | `source_case_specific` | `research_candidate_only` |
| 天芮病宫 | 离九宫 -5 | 离九宫 -5 |
| 天心医生（及同宫时干） | 兑七宫 -2 | 兑七宫 -2 |
| 乙奇 | 艮八宫 +3 | 艮八宫 +3 |
| 值符 | 乾六宫 0 | 乾六宫 0 |
| 实际选中物理宫唯一集合 | 9/7/8/6 | 9/7/8/6 |
| 四物理宫基础分合计 | -4 | -4 |
| 克病专用奖励／弱病泄耗 | 0／0 | 0／0 |
| 同宫吉助奖励 | +4 | +4 |
| 五不遇时罚分 | 0 | 0 |
| 全局未封顶原始分 | 0 | 0 |
| 其它独立证据方向 | `adverse` | `unresolved` |

**为什么两案数学上同零：** 先依据真实人物关系找到不同的干和宫；恰好本人乙已经是入选的乙医药宫（艮8），同事戊已经是入选的天芮病宫（离9），所以按用户批准「一个真实物理宫基础只算一次」的 V8，角色变化没有增加新的物理宫；四宫唯一分和一致。同宫加分也没有改变。不能为了强行给两人不同数值重复计宫或假造第二组克病奖励。

**真正缺陷是逻辑合断，不是运算器把人物同一身份复用：** 两例都把`raw_final=0`直接翻译为「不凶不吉」及 UI 「微恙／病势平缓」。但本人有效证据方向为 adverse，同分值互相冲突，绝非「已经稳定」；同事月干只是未获原著条件审定的 `research_candidate_only`，不能以0分作确定判断。原 Swift `WenguaNativeVNextEngine.compute` `conflict`显式排除`result==0`；即使`traditionalSentence`发现冲突，`WenguaPythonVNextVerbatim.sections`对任何`review.score==0`仍直接发`overall_resolved`。Python `selected_health_sections`亦相同。

## 2. 定点修复：源数学不变，只收紧0分断言

保留原 V8 `post_void_known_sum`／source 200/81／角色绑定／物理去重／真实克病条件／空亡／五不遇时／全部典籍模板和原始两历史案数字不动。仅当**实际核定的原始0分**有下列之一时阻止「微恙／病势平缓」：
1. 当前独立源证据`favorable`或`adverse`，数学0与证据方向不一致；
2. 所选人物来源信度不在`source_case_specific`或`user_explicit_direction_verified_by_actual_chart`中（例如`research_candidate_only`）。

Python 只在`src/wengua/domain_selected_energy_vnext.py::selected_health_sections`的最终话术上判定`neutral_conflict`，改用已有 `overall_pending` 模板；Swift 在`WenguaNativeVNextEngine.compute`新增同义`neutralConflict`和`evidenceConflict`，`WenguaPythonVNextVerbatim.sections`仅对 score==0 且 conflict 为真改用**同一**已有模板。没有增改新评分矩阵、+/-原始数字、非零断词和任何具体治疗建议；不是把0硬改成-1、-5或别的讨好答案。证据中性且来源充分的真正0分仍可按用户定义显示「微恙」。

`tests/test_health_20261028_1344_two_person_audit.py`同时断言两个真盘的四柱、日/月人物干、物理宫集合、原始0和各自证据信度，并且新的`90_review`不再把此二者写成`此病为不凶不吉`；用户能在「专业解盘」中读完整不删减源事实。

## 3. 双星边界与风险

用户重复强调，**只在病宫真实天芮＋天禽携不同星干时**，两条真实天盘对同一地盘的81格各查原格计分；真实两星各携有合资格乙／丁奇才能按原规则分别得到同宫条件奖励；天禽**本星**并不作为另一份天芮病星基础分。同一病宫的基础计分仍仅一次，其它八宫星、天盘干和格局仍按原来的一星一干规则。该例恰好病宫天芮局总体偏凶，**不能因为客观分数0而向公众断病已平稳**。这些传统象意不构成医疗判断。

失败日志、历次已见案例原分数和来源版本完整保留；这些是用户已反馈的开发问题，**不是科学或未见盲测**。本轮最新CI和Xcode的具体 run ID 在源推送后追记，不拿上一版测试充当本轮成功。

## 4. 完全相同时刻的原生 Swift／Python 逐字一致性追加测试

为了消除“相同实时时辰、不同人物”的原生测试覆盖盲区，新增`scripts/ios_v80_same_clock_neutral_parity_20261028.py`固定原实盘分两次生成**互不覆盖**的一例输入，分别`本人`与`同事`，均保持同一`2026-10-28T13:44:00-04:00`。修改`.github/workflows/health_v80_real_selected_power_native_parity.yml`，通过现有正式`VNextThreeRandomNativeFullCheck.swift`使用相同两例的`WenguaNativeCore.compute`、实在人物绑定、V8真实200/81源数据和Python中文模板，各自逐段逐字比较。之所以分为两份输入，是原随机驱动单批次拒绝重复`instant`，但本审计必须严格保持相同时辰而不能为了测试随意篡改到不同分钟；两份输入通过两次完全相同命令独立核算。两固定已揭晓案、原20随机抽样测试仍继续独立运行；每次包括stdout、diff、Swift全文及stderr均保留在Artifacts。


## 2026-10-28 实测核查完成：病宫双星仅此处，其它宫一星；同一时刻0分暂不强断

- 在Python真时辰`2026-10-28T13:44:00-04:00`的本人、同事两个实盘上增加实际九宫原盘断言：**仅天芮病宫有真实天芮＋天禽两颗不同天盘星且各自不同携干**，中五没有普通星门神，其它八宫逐个最多只有一星（中五不计）；两条有序81格沿用原来各干独立吉凶/墓刑/长生，不将双星规则泛化到普通宫。新增断言在 `tests/test_health_20261028_1344_two_person_audit.py`。
- 实际精确审计原始0的同宫加分分项是：**兑七宫天心星逢空：原2折为+1；离九病宫实际天盘丁奇：+3**，所以另加合计4；并非因为本人/同事角色数重复算宫。同事入选月干戊离9与天芮共享，自己日干乙艮8与乙医药共享，故各自唯一物理宫恰巧同为9、7、8、6。这是**现行源算法实际事实**，不应人为改写0分。
- 当前唯一修复是零分但**独立证据有吉/凶方向**或**人物关系仍是未审定候选**时，Python和Swift只给“暂不强断吉凶”，绝不显示“微恙/病势平缓”的肯定语。旧V8其它评分、病宫双星、两本原文、原已知固定案未改。确凿来自同源最新测试：V8 主CI #40740609375 PASS；现行V8 Python/Swift逐字一致 #40740609566 PASS；真实 XcodeGen macOS Simulator 编译+200/81/人物/模板 bundle #40740609490 PASS；额外全同一真实13:44本人/同事逐字对照 **#40741011722 PASS**，main CI #40741011736 PASS。此后若任何源码更改，必须按新提交重新验证，不能继承旧通过状态。
