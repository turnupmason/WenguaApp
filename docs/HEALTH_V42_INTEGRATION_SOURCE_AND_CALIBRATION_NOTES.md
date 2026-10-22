# V4.2｜同一盘整合 V3.9 客户断词与六模块古籍象意实验分

## 用户新指令的准确解释

用户在 V4.1 之后要求：「开始弄。我们是要合并3.9的。按理说不会证据不足啊，一个盘起出来信息就有了啊」。

**实现状态**：V3.9 已阶段性接受的客户原文**逐字保留**，并非另建替代的新模板；新增 `src/wengua/health_severity_v42_integrated.py` 调用原 `analyze_health_severity_v39(...)`，同时从**同一 chart + inquiry + calendar**计算六模块分数，最后追加一节「传统病势象意分」。输入一次、同一盘面、多重正反证据源，不允许再让文字与分值分别假造宫位。

用户说得对，**自动起盘就能精确得到**四柱、用神对应宫、八宫天盘地盘星门神（中五宫按实际不设常规星门神）、天芮所携真天干、月令、十二长生、旬空、击刑、门迫、空墓库、时支驿马、真实六冲、值符值使、两类双重关系、来源81组有序天地干、42疾病补充、17复合格局的可执行部分。这些不可以笼统“信息不足”搪塞。

**只能真实的问事上下文提供**患者实际出生年命、某个未明人物的性别、是否新病或久病、就医相关事实。这些不是天文时辰变量，不可由六十甲子自动推断成现实既成事实。V4.2 对病程未给出时，自动在同一盘计算「病程未指定／假设新病／假设久病」**三路**，客户可看到新、久分数区间而非以一个凭空选择的病程给出死局。未知的复合规则是否可按原书无歧义执行属于**规则可执行性**，也不能误写成“起不出盘”。

## 全十天干完整十二长生：120项已程序核算

旧原著索引 `data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json` 有十干的长生、帝旺、死、墓、绝五项锚点。V4.2 新增 `data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json`，用阳干顺行、阴干逆行的十二支循环推导其余七个状态，且**逐个复核全部10×5既有源书锚点**，不改旧书内容。全表十干×十二=120不同状态。对于乾、坤、艮、巽这种一宫含两地支的宫，**两个支的状态都输出**，不能只选对结果有利的一个。例如2026-10-22 用户盘，患者己巽4辰衰、巳帝旺；天芮所携丙在乾6戌墓、亥绝；病宫的戌亥空与丙辛「月奇相合」保留真实互证。阶段墓、绝与旬空不是同一个事实、不是三次死亡迹象。

## 评分归一化与双重证据去重

旧 V4.0 100点基准会把本无足够喜证的盘输出90分，强吉114+被截断100。V4.2 新候选 `data/knowledge/score_models/health_severity_v42/integrated_budget_policy.json` 使用中性基准50，六模块**可正可负的绝对上限预算合计50**：主体与天芮及月令±17、时干事体±7、医药±10、刑冲破墓空马±9、原书81有序组合±5、复合格局节奏±2。计算每模块实际触发的源数据后按其独立分母换算并限幅，总分确定为0—100，绝不是疾病危险率、恢复概率、血压、免疫力数值。完整原加减与限幅前后值均在审计中，用户看到六模块结果与关键原断词。

它**复用 V4.1 原书优先的有序组合和具体角色门控**；戊丙、丙戊虽一般吉而测病不利，丙辛测病不凶，不能无差别病宫反号，天禽陪星同宫不视为另一病宫投票。同一宫三奇吉格可保留作反证，但不因别名重复加多次分。旧双重制病「人克病、病宫克天芮」与新提出「人、医药同克病且天芮弱」仍是两个不同复合概念，不能覆盖。年命或性别未给出时不臆造另外一个“病人”，乾坤只作对应人物的辅助宫。

## 实际运行与数字（未用于真实健康判断）

在**五份真实初占问题、无事后作者结局**输入下运行 `scripts/replay_health_v42_unified_five_actual_casts.py`；其中前三例的 V3.9 中文原断词 SHA 与 `data/evaluation/health_v39/user_noon_two_seeded_book_families_V39_SEALED.json` **字节一致**，后另增加两个本轮未用于新权重调参的真实古籍历史问题（但仍非保密临床盲测）。

| 真实第一问 | V3.9传统主判 | V4.2未指明病程的中心分 | 假设新病 | 假设久病 |
|---|---|---:|---:|---:|
| 2026-10-22 丙午戊戌己巳庚午本人问健康 | 偏凶 | 34 | 36 | 34 |
| 1995-02-19 癸巳问弟弟健康 | 偏凶 | 48 | 50 | 44 |
| 1996-11-02 庚申本人测 | 偏吉 | 53 | 53 | 53 |
| 1996-03-16 戊申本人问身体 | 偏凶 | 59 | 62 | 54 |
| 1996-07-27 甲申问父亲 | 偏凶 | 37 | 39 | 33 |

**存在明确未解决的分值与原判不一致：** 1996-03-16 V3.9 传统主判偏凶、V4.2 分数却59分，现已封存作为**失败/待查冲突**，绝不把59悄悄改成低分来迎合书中的故事结局。1995-02-19 之前原始90现为48，但这是新预算定义改变，不代表已通过独立统计验证；1996-11-02 原124饱和改为53，仍不代表预测准确性。

## 真实运行、不可变归档及下一阶段

- V4.2 新联合引擎：`src/wengua/health_severity_v42_integrated.py`，原来 `src/wengua/health_severity_v39.py`、V4.0、V4.1 unchanged；
- 完整10×12十干对应：`data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json`；
- 新六模块参数：`data/knowledge/score_models/health_severity_v42/integrated_budget_policy.json`；
- 真5个原始第一问回放：`scripts/replay_health_v42_unified_five_actual_casts.py`；
- 测试：`tests/test_health_v42_unified_full12_5cases.py`，Python 3.11、3.12 都通过；曾发生 Python 语法括号、测试类 `run` 名称覆盖失败，均保留失败CI痕迹，不假报首次通过；
- 新 V4.2 追加迁移：`schema/migrations/070_health_v42_unified_v39_full12_sixmodule.sql`，120条十二长生源事实、5份旧文本SHA＋新文本SHA与不同病程得分、30个独立模块账；
- **最新全194古籍库**：`archives/sqlite/WenguaApp_双书194案例_完整十二长生合并V39评分V4_2_完整研究库.sqlite3`，SHA256 **f76b26200d8ed945621139217fcd63d55dddd010c1e4a2848d4e9ad544b3ec66**，15,155,200字节。原完整 V4.1父库 SHA256 **f90e9de80b24a852c26d4957e4e91234f86b76c9289cbc9f4738eb1b735bf01a**；
- 新完整数据库清单 `archives/sqlite/wengua_health_v42_full12_unified_manifest.json`；原样5题与九宫证据明细 `data/evaluation/health_v42/verified_5_original_questions_full12_unified_SEALED.json` SHA256 **bcd77e5522b023d4cd712958ff4aaea3adba0b33fbf02578d88d6016e8413fd7**；
- 5份全部原断词+新增评分可逐字核对：`docs/HEALTH_V42_FIVE_UNIFIED_V39_AND_SCORE_READINGS.md` SHA256 **0d49eed7062496ca4803e19f573cf3f316e79ef70ccf5a1a7bf922fcad477e17**；
- 新 SQL 采用 full V4.1 只读父本、SQLite完整性与外键核对；194个旧事件、43章、81作者原文有序组合、42个另行疾病补充、17复合和历史两条失败，旧3.9/4.0/4.1表逐项保留。
- V4.2 专项跨语言CI `https://github.com/turnupmason/WenguaApp/actions/runs/39838333504` 两版本通过；完整新SQLite构建及提交CI `https://github.com/turnupmason/WenguaApp/actions/runs/39838979233` 成功。
- **状态依然是用户审核前的 V4.2 量化实验，不代表数字权重已获确认或可以用于真实医疗结论/UI。**

下一个迭代如用户提出继续，应结合全部原书证据和更多新家族具体案例，查清「V3.9偏凶但分数59」冲突，改善医药来源的病事取用与宫位权重，而不能照着已经看到的作者结局补丁造答案。每个新增版本必须另存完整 SQLite、继承当前原文件及AGENTS，并保留失败实验。
