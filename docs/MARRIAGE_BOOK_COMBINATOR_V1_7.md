# 婚姻作者式多证据条件判断 V1.7 — 原著27条与新历史家族

## 本次真实实现

源码 `src/wengua/marriage_book_combinator_v17.py` 调用 V1.6 已实算的九宫、天文节气和真实双方年命，再由**原著明定的条件**逐个扫描：六甲六仪击刑（戊3、己2、庚8、辛9、壬4、癸4，严格是天盘载干对应宫，不能说庚落震3便为六仪击刑）、三奇墓（乙乾6、丙乾6、丁艮8）、时马星（按时支三合固定寅申巳亥）、双方日时宫与真实年命、天盘对地盘顺序有别的81条干克应、门迫与当月宫旺衰、太岁支所在宫、九星和八门分别与原宫比较的伏吟/对宫反吟。传统婚恋用神优先包含实际双方年命、乙庚与六合，一项有利不能自动抵销冲克、刑、墓、空、迫。

**注意方法条件：** 月令为纲的五行旺相休囚死现采用十二支对应四季和四季土月的研究模型，`辰未戌丑`四个转换月内的精确旺衰尚需细分核验；门迫先判“门克宫”，但《开悟之门》第四章第550行规定休囚之门未必克得动旺相之宫。伏吟应分星伏吟、门伏吟与两者俱伏吟，第566行六甲时天显可动，不能一律说凶；反吟应分星/门是否真实对冲，并在婚姻领域依第574行优先考虑反复和不利。乙庚、六合只构成古籍象意证据，绝不能凭星门格局认定真实家暴、欺骗、出轨、疾病或性取向。

可追溯索引 `data/knowledge/phrase_library/marriage_v1_7/original_combo_rules.json`，27条完整记录包含 **book_id / source_section_key / original source entire SHA256 / exact source line / exact original Chinese line / applicable actor and domain / positive evidence / negative or counterexample / corresponding timing method**。运行加载器逐条校验两份《开悟之门》源文的整章SHA、原文逐行一致，并另校验81个有方向的干克应原句 SHA。程序计算格局并保留来源和反证，绝不按数字权重票决。

**当前可执行级别：** 代码能计算上述盘面关系与条件匹配。它会执行新的来源组合判断，并在原 V1.6 先判成败与新证据层一致、且有实际符合空亡条件的原书应期方法时，才继承已算出的具体节气时间；若证据矛盾而结果改变，必须撤销原先可能错误的时间选择。**目前不能声称24个全局因素都精确实现或所有22场景均已给出有书源首选应期。** 特别是每宫暗干与宫内特殊空亡远近/暗动、多轨生克冲害的法则优先级、太岁与真实对象多层合取、时干入墓入库的季令区分、部分原局值使门落中五及精细的时序仍需按原著补齐，未核不得伪造计算完毕。真实端到端六层正式发布仍为0份，GPT约200字自然断语仍应关闭。

## 不得窃取测试答案：三旧题保留、新家族不计预测命中

V1.6 旧开发案例《开悟之门》例二的“年命似比和却离婚”、例三两个相亲对象的成败总共3问：初断对书内反馈只有**1对2错**。这3问**曾经用于分析失败原因，绝不能再次作为“新秘密盲测”，更不能为取得更高数字直接重写上一版错误标签**。V1.7 独立增加原书例四和例五两个不同事件家族用于**初断前隔离整个该事件家族的引用**、核对原书全部8外围宫的门神，以及缺乏完整双方年命时的拒绝臆造。例四没有提供新男友年命；例五复婚双方真实年命没有列出，作者只提出有条件的十月、十一月建议而无日后是否复婚的回访。故两组旧书**不具备未来结果的完整可评分后验**，程序均返回`unresolved`，**新命中率分母为0、不得宣称0/2错误或2/2成功**。两本书的材料此前被开发者阅读过，规则索引也明确保留了例四、五的源例作为规则追溯，因此仍是**新事件家族的开发验证，不是未曾见过的封存测试**。

《开悟之门》例六作者承认首次断错，当事人涉及同性情感，属于**失败/纠错的历史来源**，不属于正向首断“正确”案例；性取向不是医学问题，不能根据盘面推断疾病或进行歧视性诊断。下一轮必须选择未用于新规则调节的别的事件家族，并将新旧训练、开发、封存测试彻底分开；没有可评分来源的事件只能作流程和资料缺项测试。

## 本轮文件、完成验收和后续强制工作

- 原文条件索引：`data/knowledge/phrase_library/marriage_v1_7/original_combo_rules.json`（27条）。
- 引擎：`src/wengua/marriage_book_combinator_v17.py`，`analyze_marriage_v17(db_path,payload,held_out_family_id=...)`；复用`astro_calendar.py`、V1.6 已有家族隔离索引、作者判断与应期。
- 另外事件家族测试：`scripts/evaluate_marriage_other_families_v17.py`，`tests/test_marriage_combinator_v17.py` 和 `tests/test_marriage_other_families_v17.py`。
- 完整数据库专用迁移：`schema/migrations/045_marriage_conditional_combinations_other_family_v17.sql`，builder `scripts/build_marriage_conditional_v17.py`，完整回归 `tests/test_marriage_conditional_v17_archive.py`，GitHub Actions `.github/workflows/build_marriage_conditional_v17.yml`。

**最新全库（下一轮唯一父库）：** `archives/sqlite/WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3`，14,616,576字节、SHA256 **`e6bc297b10b0f911b1cc03392afe7e53bc51a34d8acffecd674a9f5e343af675`**。xz `archives/sqlite/WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3.xz`，1,162,220字节 SHA256 `9c3efdd1a5da012dcc385b4ff3398fb14ed3d7cd6894a66ef95904067b519653`；manifest `archives/sqlite/shenqi21_kaiwu22_marriage_conditional_other_family_v17_manifest.json`。前驱V1.6 SHA256 `89cd5eb51f4eec7e41092a2bb8f5f624c1c6e7e4eb2225d00051e2d6c8e4a5f4`。所有194整案、43原文节、22个场景、9个旧婚姻流程、20应期方法、3份旧首断及独立3份后验标签和旧两条失败全部没改；新版本新增27条来源规则和2条不同事件家族不可评分研究记录。SQLite `integrity_check=ok`、外键错误0。

**下一轮的验收门槛**：逐条完成24全局字段的可执行规则和证据出处，不仅是checked=True；增加太岁年支/年干与三宫合取、月日破的真干支动态、用神空亡远近/填实/冲实的事件限定、六甲击刑与入墓出墓季令区分，真正解决日时主客与乙庚/六合/实际人物年命的优先级。再挑其它完整真实案例按事件家族不泄漏评测，保存错例、保留未见封存测试；**只有可以核验的传统结论和实际应期均完成时才开启第六层GPT约200字自然中文输出**。原著多轨冲突未解决则写明 unresolved，不得编造人话定论。