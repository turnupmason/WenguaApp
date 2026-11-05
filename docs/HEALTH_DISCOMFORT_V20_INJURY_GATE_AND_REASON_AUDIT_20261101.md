# V20 伤门实际落宫条件门与九宫病位证据审计（2026-11-01）

## 缺陷复现和根因
- 旧 `WenguaNativeDiscomfortV15.swift` 原 `let injuryFull=...` 无论事因都打印“伤门在某宫，主筋骨牵扯之象，仅作旁线”，而 `witnesses`、`ranked` 无条件加入伤门原200五档。独立 Python `health_discomfort_v19_parity.py` 仿真同错，并非仅用户文案问题。
- 冻结复现：`https://github.com/turnupmason/WenguaApp/blob/course-v4-before-cleanup-20261105/docs/IOS_V80_XCODE_PASS_RUN_41341637870_ATTEMPT_1.md` 随机弟弟阴遁2026-11-14 11:00 -05 显示伤门坎一和固定筋骨旁证；当时并没有用户提供意外/剧痛/手术信息。过去实际：无条件触发。预期：未选择任何条件禁止起盘；显式普通不适不取伤门；条件激活才用伤门实际宫位符号与宫象。
- UI在 `CastSetupScreen`，人物绑定 DTO `WenguaNativeInquiry.injuryContext`，路由器和 Swift 实体对无效选项 fail-closed，Python对应字符串亦拒绝。所有用神按自身源力，不把有伤门的寓意自动等同具体骨折/流血/手术。
- 现有两份原始200/81及255文字来源冻结，未做古籍新章。三种应用场景是**用户确认业务门槛**，与独立核验到的原书章节条件需保持区分。

## 新分支与验收
| 选择 | 是否读伤门宫 | 位置优先级 |
|---|---|---|
| 未选择 | 拒绝起盘 | 无输出 |
| none 普通身体不适 | 否；九宫存在伤门但不作为用神或旁证 | 天芮与真实人物实宫 |
| accident 意外 / bone 骨肉 / bleeding 出血 | 是，取伤门实际落宫完整身体候选及原力限制 | 伤门部位优先，天芮作为独立相交或备用部位 |
| severe_pain 剧痛 | 是，实际落宫作为独立宫位证据 | 与病宫多宫交集评估 |
| surgery 已做/计划手术 | 是，并条件检查开门克伤门与同宫白虎 | 不据此认为医学上必须手术 |

同宫基础不重复投票；不同实宫取自己实际部位和源200，真空减看；九段原结构只输出有可用证据的段落。禁向用户透露源表计分，禁诊断。
后续以真实 Xcode/macOS Simulator bundle、Python tests、Swift CLI和新随机真实时辰 Python↔Swift full text parity 为验收，历史成功不得替代本版。

## 同宫伤门负例检查
未触发伤门门槛时，若天芮宫恰巧临伤门，不能让“门迫”备用断语绕过 none 门槛，也不得读取伤门源力作为病位候选。Swift 改用 `(useInjury || door != "伤门")` 限制对客条件文字，普通不适的门源档在该条件下不纳入；Python 独立生成相同字句，CI 固定文本与真实随机测试共同检查。


## 2026-11-01 · V20 实际 Xcode/Swift/Python 最终验收与真实独立失败保留

- 原因缺陷：旧 V19 客户稿对普通不适仍无条件说“伤门在某宫，筋骨旁证”；现在 health.discomfort 必须选 none/accident/bone/bleeding/severe_pain/surgery，未选不进入 30 秒静心或写入 15 天限制。仅五种伤痛/手术情况读取伤门实际物理宫及宫中星、携干、地干、白虎、开门实宫相克、真假空、墓刑迫；none 的天芮若碰巧临伤门亦不得借门迫文字泄露伤门。创伤类别伤门实宫部位优先，伤痛/手术须与天芮和人物真实宫位独立比较。
- 客户文案是具象证据因果：出于具体宫位、实宫阴阳体表内外、真正独立携干与地盘干及匹配的器官部位才输出，宫与宫的相同部位是互证；不同部位不假装同一病灶，体例允许省略无证据段落。不再套用所有人的“筋骨旁证”。源码 `ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift`、`src/wengua/health_discomfort_v19_parity.py`、iOS UI 和模板，Important 镜像/MANIFEST 已同步。
- **实际最新来源 SHA `67a23b23ea9af90839a6c87c9cbae23caa6fa0d5`**：macOS XcodeGen + unsigned iOS Simulator 真实构建、bundle 200/81/255/模板、六种条件各新抽的真实时辰 Swift 及独立 Python vs Swift 两新时辰客户中文逐字比较 [#41349563076](https://github.com/turnupmason/WenguaApp/actions/runs/41349563076) **PASS**。源全文在 `https://github.com/turnupmason/WenguaApp/blob/course-v4-before-cleanup-20261105/docs/IOS_V80_XCODE_PASS_RUN_41349563076_ATTEMPT_1.md`。弟弟 none 2026-11-11 03:00 -05 共四节无伤门；妻子 surgery 2027-02-14 17:00 -05，伤门震三，额外宫中天蓬携庚实取肺部线索，并辨开门乾六克伤门震三；妹妹 bone 2026-11-23 05:00 -05，伤门离九且真空减看；哥哥 bleeding 2027-02-14 19:00 -05，震三伤门与哥哥真实月干/排行宫证据交集。两份独立逐字测试：弟弟 2026-11-19 01:00 -05 四节 PASS；妻子 2027-02-14 19:00 -05 五节 PASS。病位盘文全都来自 Swift 实时自动起盘，不得视为现实病史、医生诊断或古籍原著中的未见盲测。
- 相同源 SHA 的主 Python3.11/3.12 CI [#41349563077](https://github.com/turnupmason/WenguaApp/actions/runs/41349563077) PASS；冻结 V8 选用神与原生 Python/Swift parity [#41349563147](https://github.com/turnupmason/WenguaApp/actions/runs/41349563147) PASS；V7.7专项 [#41349563172](https://github.com/turnupmason/WenguaApp/actions/runs/41349563172) PASS。**旧独立 V7.4 colleague/natal historical audit [#41349563095](https://github.com/turnupmason/WenguaApp/actions/runs/41349563095) FAIL**，失败保留，不能冒充全套旧工作流通过。非签名真机/App Store验收。
- 残余审计：用户三种伤门应用场景只是本次得到授权的用户业务规则，尚未逐条找到原著版本/章节/行号/hash和独立反例；不得称古籍全部直接认可或对真实外伤/痛点/手术有医学预测效力。保留冻结 V8 病情轻重算法，外伤和位置只做传统符号位置排序，绝不以五档力量推断疼痛程度、死亡或疾病轻重。
