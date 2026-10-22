# WenguaApp 最新有效路线：V3.9 纯断词＋完整十二长生

**用户决定（2026-10-22）**：「算了我们放弃4.2分数，我觉得没啥用。保持3.9。」随后补充：「已补齐的十二长生计算保留，加入模版。然后给我看下我们模版什么样子。随机生成几个时辰，我看下。如果可以我们就封装了。」

## 0. 当前真正有效的执行路径

1. 实际日期＋时分＋时区 ⇒ `solar_chart_clock` 真节气与四柱，`bureau_for_term` 真阴阳遁元局，`layout_from_explicit_bureau` 真九宫盘。中五宫不能伪造常规八门、八神、九星。
2. 按问事身份取患者真实用神（日、年、月、时干、乙、庚、年命等，以原用神算法和确定输入为准）；区分天芮病宫、坤二宫地盘天芮本位、时干事体、天心医生、乙奇医药、乾坤性别辅助。
3. `analyze_health_severity_v39` 原有**完整**十一位置取用、月令、81原书天地干、42疾病补充、17复合条件、其他生克格局、负正证据与优先级、冲击刑门迫旬空墓库、时支驿马、伏吟反吟、应期条件与古籍式主要判断（无数字）。
4. 在**同一个 chart/calendar/inquiry** 中，`health_lifecycle_v391.source_full12`读取先前已校验的10天干×12阶段，并以原书索引10×5已知锚点逐个确认；枚举每个真实宫所辖一支/两支对应的全部阶段。不以某支对结论有利就遗漏另一支。
5. `analyze_health_severity_v391`**不修改 V3.9 原文任何字节**，在原先第03「天芮病宫」、05「患者用神宫」、07「医生医药」、08「时干事体」段后仅追加匹配生命周期短句，仍是**11个固定栏位（未知性别缺第06则客户实际十栏）**。不引入原来V4.0–V4.2分数、不当作医学概率。
6. **唯一公共入口** `src/wengua/health_text_pipeline.py:auto_cast_health_v39_text(iso=...,timezone_name=...,inquiry={"intent":"severity","relationship":"self"},db_path=...)`。无论网页或未来 iOS App 入口都使用这一条路径；禁止将用户问题转到 `health_severity_v42_integrated.py` 或 `health_symbolic_score_v40.py`。
7. 此轮是**V3.9.1待用户审查扩充稿**；用户看过随机测试且明确称合格后，才写 USER_APPROVED 锁定版并做正式 UI／iOS 封装。不可因为用户说「如果可以」就先标成已批准。

## 1. 文件

- 原 V3.9 原样保留：`src/wengua/health_severity_v39.py` + `data/knowledge/phrase_library/health_v39/severity_customer_template.json`。
- 无评分的十二长生复用模块：`src/wengua/health_lifecycle_v391.py`，依赖 `data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json`（**只复用 120 项盘面事实，不复用 V4.2 任何数值**）。
- 新十一段模板：`data/knowledge/phrase_library/health_v391/severity_text_full12_template.json`。
- 新 V3.9 纯文字调用：`src/wengua/health_severity_v391_active.py`，公共自动起盘入口 `src/wengua/health_text_pipeline.py`。
- 真4个随机时辰脚本：`scripts/replay_health_v391_four_seeded_real_times.py`，固定种子 SHA256 `182df84ae491bfdde4aa5da50488332877db742dcfe21b1219af89ea89b30059`，没有看结论再换样本。模拟本人问事、无出生年命、新旧病史预设。
- 真实起盘和旧V3.9原文不变测试：`tests/test_health_v391_source_12stage_four_random.py`；自动入口验证 `tests/test_health_v391_public_auto_cast.py`。
- 用户查看全部四份完整文本：`docs/HEALTH_V391_FOUR_RANDOM_COMPLETE_CUSTOMER_READINGS.md`。同组完整来源、八宫与所有生命阶段内部审计 `data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json`。
- 当前完整新 SQLite `archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3`，SHA256 **21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405**，15,175,680字节。精确完整父库 V4.2 SHA256 `f76b26200d8ed945621139217fcd63d55dddd010c1e4a2848d4e9ad544b3ec66`，原旧数字数据仅只读历史存档不进入新执行链。
- 完整清单 `archives/sqlite/wengua_health_v391_active_numerics_disabled_manifest.json`，迁移071，额外20个真实对象角色十二长生记录。老194原书案件、43章、81作者有序天地干、42疾病补充、17复合、老两次失败和全部旧SQL永久保留。
- 专项Python3.11/3.12 [V3.9.1测试](https://github.com/turnupmason/WenguaApp/actions/runs/39841974154) SUCCESS；[新全库归档](https://github.com/turnupmason/WenguaApp/actions/runs/39842377752) SUCCESS；[一条路径自动起盘](https://github.com/turnupmason/WenguaApp/actions/runs/39842910213) SUCCESS。

## 2. 固定随机四时辰及复核点

| 随机时辰（America/New_York） | 四柱 | 患者真十二长生 | 天芮携干真十二长生 | 原V3.9主断 |
|---|---|---|---|---|
| 2026-11-01 05:00 -05 | 丙午 戊戌 己卯 丁卯 | 己乾6 戌养、亥胎 | 辛艮8 丑养、寅胎 | 病凶 |
| 2026-11-04 05:00 -05 | 丙午 戊戌 壬午 癸卯 | 壬乾6 戌冠带、亥临官 | 辛离9 午病 | 病凶 |
| 2026-11-10 21:00 -05 | 丙午 己亥 戊子 癸亥 | 戊离9 午帝旺 | 丙坤2 未衰、申病 | 病凶 |
| 2026-11-21 17:00 -05 | 丙午 己亥 己亥 癸酉 | 己坎1 子绝 | 丙离9 午帝旺 | 病吉 |

**明确的当前已知文本问题，必须留给用户验收前看，不得藏掉：**
1. **2026-11-01，天心医生、乙奇药在同巽四宫，旧V3.9已有「乙加己」重复解释**，新增完整12阶段再次并列相同辰冠带、巳沐浴。当前这是按“原V3.9每字不动”的策略保留的文字冗余；正式封装前可在**新审批版本**中合并，不能改掉之前的已存完整读稿而不留修改痕迹。
2. **2026-11-21，病宫确见丙加戊「鸟跌穴」**，作者原书有疾病反向不利的专项判断，病宫又天芮土受生，但V3.9原有主断仍偏吉（患者宫克病宫），新增十二长生表亦显示病宫丙午帝旺、患者己子绝。属真实正反证据优先级冲突，不得为了眼前主断配分/篡改原文；应让用户看到全盘再审、未获批准前不能宣称正式封装万无一失。
3. 病程新旧、患者真实年命是**题外现实输入**，盘本身不能替用户编造；所有真实盘面事实必须完整计算。新稿继续用「原书有据/无具体应期不强断」风格；所有医学相关句子只是古籍文化象意，不是实际临床事实。

## 3. 禁令与下一工作阶段

**主线禁止数值评分**。绝不调用 V4.0、V4.1、V4.2 任何数字评分模块或提供「吉凶概率/生命体征指数」；历史代码、SQLite与失败不删除，只停用。V3.9 正文规则、年命、九宫、12阶段真实事实、用神、反证、应期保存和可复用。等用户对四篇实际断词认可后再制作 USER_APPROVED 稳定无分数封装，才进入扩展到其他预测领域及软件 UI。旧第4例需要专门审查原书鸟跌穴例外优先级，在认可前不宜宣告全领域病势模板精度充分。
