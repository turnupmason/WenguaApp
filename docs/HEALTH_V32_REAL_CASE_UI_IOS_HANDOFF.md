# WenguaApp V3.2 真案例断案验收 → UI → iOS 上架交接（2026-10-22）

## 用户本轮明确的开发顺序

先通过**最新V3.1疾病轻重固定模板**实际断两件书源真实事件，用户本人逐段核对古籍作者实际断案；只有用户明确说**通过**，才开始UI定稿；UI确定后做iOS App，准备App Store上架，后续规则逐次小版本更新。**这轮不能提前做UI，不能声称App已上架**。下一新窗口应优先读根AGENTS.md的最新V3.2段、本文件、最新CI/manifest以及用户对两例的批评/通过状态；不要要求用户重讲此前全部规则。

## 已核实的完整父库（非V2.7/V3.0）

V3.1当前可用完整SQLite：`archives/sqlite/WenguaApp_双书194案例_患者时干病事有向修正V3_1_完整研究库.sqlite3`
SHA256 `3a72dbb798d73413c2ebb994e232b83039a483d91cfa8a8f60f246d4ad84b529`。
V3.1真实全CI#39789949250通过；上一版V3.0错误的“时干病事宫克身反判吉”必须保留为失败证据，不重用。最新正式离线断词器 `src/wengua/health_severity_v31.py` 与固定11段模板 `data/knowledge/phrase_library/health_v31/severity_fixed_template.json`。V3.1已经实现五不遇时、男性乾六宫/女性坤二宫、时干病事有向生克、天芮+坤宫本位、天心乙奇独立月令、时干或病宫与医药同宫即传统及时医治机会、实际刑墓空迫、伏吟反吟与内外盘、有序干克应若干条件；**42条干组合与17类复合规则仅索引并非全部执行**，不得夸大。全部原书194案例+43章节+两项历史错误和V2.7~V3.1档案须原样保留。其它四个疾病意图 treatment/discharge/surgery/travel_for_treatment 仍未经用户审核。

## 本轮用两件不同的新历史事件测V3.1（非清洁盲测）

`scripts/replay_two_new_historical_health_v32.py` + `tests/test_health_v32_fresh_two_families.py`：只从 `data/knowledge/shenqi/health_prediction_ch01/case_index.json` 读取最初问事可知的盘面、年份、日期、时辰、局数、值符值使与当时关系，**不向断词器传入作者断语、后续反馈、出生年等后来才知情报**。选择：

1. `shenqi.health.19960316.self_surgery`，1996-03-16 16:30中国时区，壬子日戊申时，阳遁3局。用户在书中最初“先看看我的身体如何”，故严格以 `severity` 自问本人日干分析，不能输入以后确认的肠部手术、1991年时间或后来告知的出生年；若原书起局值符值使不符必须停而不改盘。
2. `shenqi.health.19960727.father_illness`，1996-07-27 16:00中国时区，乙丑日甲申时，阴遁7局，女儿代问父亲，年干主用神与男性乾六宫；无父亲生辰不可猜年命。保留作者的原案例故事完整性，不能拆分同一事件。
   
这是**已在书源库的历史家族回测**，不是从未见过的保密盲测。要先按V3.1生成不可变文件 `data/evaluation/health_v32/two_new_source_families_V31_READOUTS_SEALED.json`，验证SHA和严格原局数、值符值使等元数据，再由用户人工对照作者断案。**不能调成与作者答案一致后假装盲测**。测试如有真实起盘差异、运行失败或偏差，必须如实记入本日志和AGENTS并停止宣称通过。

## V3.2附加数据库交接

新迁移 `schema/migrations/060_health_v31_real_cases_ui_handoff_v32.sql` 只追加两条封存历史预测哈希/验收状态和UI门禁，不动规则引擎、不破坏194个原历史；`scripts/build_health_v32_replay_archive.py` + `.github/workflows/health_v32_two_new_cases.yml` 会建立新V3.2完整SQL+XZ+manifest，**必须先真实CI通过才能记录新父库SHA**；此前V3.1完整库始终保留，不覆盖。若失败，先明确指出实错，不声称V3.2数据库完成。

## 进入UI/上架的明确审批和范围

只有两张真实案例的V3.1原样断词被用户核对并说可接受，进入UI设计/实现。UI定稿计划先以现有引擎做输入、角色及出生年命可选、明确患者性别、真正九宫、吉凶断词、用户可读出处、免责及本地存储；不必一口气把全部尚未实现书源条款展示成已完成。**iOS应用需要真实可运行App、签名、Apple开发者账号、隐私说明、应用审核和政策合规**，不可把静态效果图/设计稿当成已上架。模型运行不联网、独立真实盘计算和断词一体，不能在UI里暗插GPT润色；移动端Python/SQLite如何离线集成届时再选方案。用户验收UI之后可逐个模板/规则小步扩张，不把四个未批准的健康意图做成已通过功能。

所有古籍“病凶”“应期”是文化研究象意，绝非现实医学病情诊断、疗效或生死预后；App不得暗示医学确诊、劝停治疗或替代医生。
## V3.2 first-run historical source bug and narrowly book-grounded fix

First real GitHub Actions run #39793990638 caught **legitimate source casting failure** for shenqi.health.19960727.father_illness: 甲申旬 at 阴遁7, 六甲旬首庚落中五宫; original book source metadata explicitly records 天禽值符/死门值使/星门伏吟, while src/wengua/casting_shenqi.py previously rejected all "value door reaches centre 5" unconditionally. Rule is now minimally resolved **only when source palace is 5, hour is exact xun head (steps==0), and star position hosts 坤二**: actual value door is placed at source_host=坤2, not as a fictitious centre door. All OTHER non-zero timed routes reaching centre remain explicitly rejected. tests/test_health_v32_fresh_two_families.py asserts the actual father case yields 值符天禽/值使死门/坤2/星门俱伏吟 and the old unknown 阳1戊辰 case STILL raises. Earlier failed CI and all historical original records must be preserved. Do not accept an arbitrary central-door variant without source. V3.2 actual run and complete database SHA must be confirmed by CI before claiming success.
