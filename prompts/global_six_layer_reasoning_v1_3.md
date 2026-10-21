# WenguaApp 跨领域六层断案总 Prompt V1.3

这是一条**对所有领域和每一问事强制执行**的管线，不能由用户的例子、GPT自发推理、书中错误结论或口头“锁死答案”覆盖。本契约已入 `AGENTS.md` 和 SQLite `domain_six_layer_contract`；六层任何一层缺失或未经验证，必须 fail-closed，返回具体缺项并停止把它当正式断案。

## 第一层：九宫真实事实
要求既有时家转盘起盘引擎输出经真实核验的九宫JSON和时区、节气、干支日时、起局法、值符值使、中五宫特殊处理、天地盘干、神门星、暗干、旬空、马星。1080只是2×9×60互不重复的基础状态索引，不能假冒1080盘全部可确认。未经核盘任何“锁定宫位”都只是研究符号。

## 第二层：24个全盘因素逐项审计
准确读取 `src/wengua/phrase_pipeline.py:FACTOR_IDS`（24项），逐项记录 checked/status/palace_ids/rule_ref/evidence/applicable_conditions。包括地支刑冲破害与月日破、六仪击刑、门迫（**门五行克宫五行**；杜门木落震宫木**不构成门迫**）、墓库、旺衰、天地干格局、伏吟反吟、空亡近远/暗动/填冲、马星暗干、星门神以及支持反证。unknown不能当未触发。不能将传统门迫量化成自定“削减50%”，也不能把单一神煞当必然成事或“百分百失败”的公式。

## 第三层：关系+具体问题+主辅用神绑定
判清domain、intent、target_event、问者、真正当事人、对象/父母/子女/其他人、年命、年龄、性别（允许未知）。自测日干/长辈年干/晚辈时干/平辈月干仅为依问题而用的候选，不是铁律。婚姻乙庚/六合/年命须先按真人与事件绑定；同性/非异性关系不可预设乙庚对应实际性别，亦不可在无书据时强制“日干+月干”。当一盘同时问登记和婚礼，分别定事与应期。

## 第四层：原书基础规则 + 作者整案完整证据
从已保存的《神奇之门》《开悟之门》43来源章节194整案和今后每书多轨版本中，按domain+intent+真实用神+格局条件索引：基础取用法、逐步作者首断原话、组合生克、反证、出空与应期、后续反馈、明确断错/错盘正断。原书反馈和老师事后改局**不得冒充初断输入**。必须输出chapter/source_sha/line/scene_match/old_case_id/phase，并注明每个子问题是否有**直接完整案例**或仅有相邻案例推导；不从作者年命相生相克硬套绝对婚姻结论。未见来源的断言不可称书本已验证。

## 第五层：全量证据综合 + 明确成败 + 实算应期
先让支持、反证、冲突与未知按问事适用条件聚合，输出针对`target_event`的传统`success/failure/delayed/mixed`结果与主要理由。当真实历法、原书应期法及起盘齐全且事件适于定应期时，使用原书旬空填实/冲实、旺衰、岁月日时、墓库逢冲等**真实适用**条件计算出首选公历日期或有界窗口；保留所有候选与为何排除其他候选。**不允许“以后空亡填实再说”当成成品解盘**，也不能靠算法凭空肯定未来事件会发生。指定时期的婚姻走势取时间范围和转折，而不是伪造唯一事件日。缺真正历法或主用神则返回`unresolved_missing_decisive_evidence`并列具体缺失，禁止自编应期。书本传统占断不能保证现实命中率。

## 第六层：GPT人话润色
结构化结果、主应期、关键支持及反证都已经决定之后，GPT才写约160–240个汉字，开门见山说明“我判断……，主要应在……，因为……，但……”。不堆砌符号列表，也不要改成模糊心理建议；**不得捏造现实中的出轨、杀猪盘、家暴、性传播疾病、生理障碍、性取向、违法行为、法院判决、财产或抚养权归属**，即便某古籍传统符号与这些词相联也不足以证明现代事实。涉及现实风险，应建议独立查证和相应正规专业支持，而不是把古籍象意写成“实锤”。

## 严格执行校验
每个问题产出`layer_trace`含6层、24项factor audit、真实可查原书refs、当事人用神坐标、成败证据冲突、计算后时间或具体缺项、GPT润色无新事实检查。调用`src/wengua/six_layer_contract.py:audit_all_domains`，若未`passed_six_layers_ready_for_external_review`就不能进入批准流程；该validator只是审核完整性，真正起局算法与历法receipt仍须引擎独立校验。数据库`six_layer_instance_trace`支持全部六层存证，审批前SQL trigger强制六个passed，并沿用已有独立计算应期的V1.1 SQL trigger。**过程检查100%执行不等于传统预测结果100%准确。**

## 22个婚姻场景与九套源书大流程的衔接
读取 `data/knowledge/phrase_library/marriage_v1_3/twenty_two_scene_methods.json` 的22个 `scene_id`；每一个继承 `marriage_v1_2/intent_workflows.json` 中某个可查原书的八步骤主流程。新增第3层场景人物坐标、第2层额外相互作用，第4层出处和错误案例，第5层目标事件及应期/禁断现实指控。22条不是22个书上独立验证的故事；只有可引用到原著的才留 source provenance，未覆盖的子问事标记`draft_source_grounded`，不得升为真实可靠预测方法。**继续按真实古籍及未见家族测试逐条完善，不重新起盘编假数据，不改UI。**

## V1.4 盘面 JSON 实际接入状态（更新）

按照`AGENTS.md`六层强制架构，婚姻22场景启动实际工程链路。现在服务`src/wengua/marriage_runtime.py:inspect_marriage_study_cast`支持将已有`casting_shenqi.layout_from_explicit_bureau`算出的真实九宫符号与场景原书规则数据库联结：读给定节气/日时干支得到阴阳遁和九局，提取日/时干与乙庚天盘所在宫、六合宫、实际门克宫即门迫、旬首旬空二支、全九宫元素以及九星天干组合，按场景从`marriage22_original_case_links`拿原章节SHA、作者首次推理与独立后验反馈。古籍两张完整原著起局图与source_test以18格核对；无法从源支撑的因子保留unknown，不可口头宣布“已经全部计算”。

现在`marriage_runtime_source_cast_fixture`的2张原著示例盘和`marriage_runtime_scenario_study`的44条研究记录只是端到端**部分**真实运算事实回归，绝不是44次现实婚恋预测。原书未确定的中心五宫值使落点、独立节气历法与未见盘核验、人物年命关系、剩余24项组合条件、成败/具体应期尚在开发，需拒绝对外真实断言/杜撰时间。当输入是真正有完整条件、由引擎核验的盘，未来才可由第5层推论阶段性传统结局，令真实历法推出有界首选应期，然后第6层GPT自然约200字口语化；条件缺失则明确指出缺项。源码不允许模型臆造`status=engine_verified`来绕过卡点。

新最新版完整研究数据库 V1.4 SHA256 **`ac4401378302319799e0cbf07c906ffdc06ffb2f91ce49e149aac40261c235da`**，路径 `archives/sqlite/WenguaApp_双书194案例_婚姻真实排盘接入V1_4_完整研究库.sqlite3`，此前193/194历史库和V1.3保留为历史存档。`src/wengua/phrase_pipeline.py:FACTOR_IDS`准确包含24项（`door_press_palace`为唯一门迫id）；禁止另创建`door_press`造成双计。

## 2026-10-21 MARRIAGE V1.4 JSON-IN CLI AND IMMUTABLE SOURCE REPLAY

新增真实运行入口`scripts/run_marriage_json_study.py`：以`--input`接收真实盘JSON + `inquiry.domain=marriage`、22场景`scene_id`、用户`question_text`及问者/实际对象/伴侣年命，以`--database`只读打开**最新版婚姻V1.4全量194历史案例SQLite**；`--output`输出独立结构化JSON审计文件，不触碰输入JSON和旧完整数据库。程序调用`src/wengua/marriage_runtime.py:inspect_marriage_chart_json`，依据已给出的日干支/节气/时干支重新算阴阳局、九宫、值星值门/旬首，然后和传入的所有原九宫门星神天地干数据逐字段核对，任一宫位或值使不匹配立即拒绝；自行把`status`改成`engine_verified`也不被当成可信签名。JSON要符合当前已有`casting_shenqi.layout_from_explicit_bureau`生成的数据结构（九宫字典`"1".."9"`、各宫`heaven_stars`载干、八门、八神，中五宫无常规门神），不能拿其它学校九宫风格硬塞。

真实问者和婚姻当事人绑定：用输入的六十甲子出生年`year_ganzhi`对应真实天盘载干落宫，六甲须按原书六仪遁干映射；如给定`subject`和`partner`双方年命，会计算各自候选落宫及两宫五行关系，**但绝不因年份组合自动决定夫妻主次用神/成败**。全24因素审计中目前可基于已对照的盘事实计算旬首旬空、门迫、宫位五行、天地干携星及门星神组合，真实人物给齐后还可计算人物年命候选宫的纯五行关系；其他原书尚无明确可执行方法或时序的因素一律`unknown`。实际`source JSON`输入如果年命或节气缺失就阻断相关下一层，而不是给假应期。古籍方法按22个场景读取，并将作者首断证据和后期回访分开，保留当前完整盘与真正历法尚未完全验明导致的`missing_to_publish`清单。

**当前source-only规则重要**：根据已有两张《神奇之门》起盘章示例盘可做九宫文本一致性检验，不等于独立验证真实当下时间的天文节气；未实现的24因素、同年命不同具体提问、作者全链成败和实算应期尚未补全。由此产生的是研究性JSON证据审计，绝对不能声称已经正式完成六层/给出婚姻成败或经过验证日期，也不能凭GT/模型声称“有calendar_receipt”自动提升。执行示例及输入字段见`docs/MARRIAGE_RUNTIME_JSON_V1_4.md`；测试`tests/test_marriage_runtime_source_cast_v14.py`已加真实命令行JSON回归和假核验标志/篡改九宫的拒绝测试，原194书案、V1.4真实二进制母库不变。

当前数据库仍是`archives/sqlite/WenguaApp_双书194案例_婚姻真实排盘接入V1_4_完整研究库.sqlite3` SHA256 `ac4401378302319799e0cbf07c906ffdc06ffb2f91ce49e149aac40261c235da`，用户后续全部研究以它为唯一父库；`build_marriage_runtime_v14.yml`已按字节重算校验历史 V1.4 immutable SQL，当源码与历史归档生成结果不一致则失败并要求新的数据库版本，不可覆盖已有文件。后续关键是逐条对照两书完成每一项物理规则的实际计算、现代历法真正核验、中五宫值使挂宫未明分支、规则优先级和负例，加上真实用户案例后才能产出正式成败+具体应期+GPT的人话。此约束对所有领域依根`AGENTS.md`仍是100%强制流程。

## 2026-10-21 MARRIAGE V1.5 FULL ORIGINAL BOOK TIMING + OFFLINE ASTRONOMY

**已从“只会检查盘面是否完整”推进到“真正计算古籍作者应期”，且没有倒灌书中结局。** 根`AGENTS.md`规定六层方法跨领域100%执行，新增`src/wengua/astro_calendar.py`离线太阳黄经/节气干支内核，`src/wengua/book_timing_runtime.py`读取《开悟之门》`data/knowledge/kaiwu/analysis_judgment_ch04/timing_methods.json`共20条完整原始方法（成功8、失败6、庚格3、适用限制3）；每条按原字计算sha256核对并保留作者前置条件。先判成败，再选应期：不能拿“用神旬空逢冲”直接当成“婚姻必成”的唯一理由，更不得把庚格刑事追查专法用于婚姻。

**首次真正运行的婚姻历史案例**：`kaiwu.marriage.case01`王大妈问儿子婚期（原文`sources/kaiwu/开悟之门_恋爱婚姻预测.txt`第39/41/43行首断，第45行后验报告）。作者原文先看乙庚、双方年命、日时、父母宫和六合，给出能成；第43行指出甲申旬中午未空，子丑月冲实，判断年内婚事。新的`book_case01_marriage_timing_study()`在读取反馈前，调用本地节气算法独立计算子月候选**1998-12-07约15:53至1999-01-06约03:06（中国时）**，丑月候选**1999-01-06约03:06至1999-02-04约14:46（中国时）**；作者随后第45行报告的**1998-12-16领证（甲子月丁酉日）**落子月、**1999-01-17婚礼（乙丑月己巳日）**落丑月，完全由独立代码计算月分与日干支后交叉核查。**这说明两项反馈日期确实落在作者事前所列的两个传统候选月份，不代表他曾准确断出12月16或1月17单个日期，也不证明未见新盘的现实预测准确率。** 两个事件必须分开，反馈不得当预测输入。作者后续错例同样保持。

历法实现为本地**Meeus/NOAA太阳黄经近似模型**，不联网、不调用云端，不使用简单公历月替代节气月。已与原著三个相距多年的干支日`1995-06-11癸酉`、`1995-08-13丙子`、`2001-08-20乙卯`比较；附独立可选Swiss Ephemeris cross-check，原书婚姻1998–1999年月日计算亦入独立回归。用户所在地时区必须是IANA与offset一致的真实时间，23:00日界尚有派系差异必须明确、算法保守拒绝；接近黄经15度节气交界不足0.05度的时间输入拒绝定月，以避免约1小时精度模型给假准确；输出到微秒的边界是数值近似不是天文官方授时。这项历法是跨古籍的**天文辅助计算**而非书上对预测准度的实验认证。

婚姻实际JSON入口`src/wengua/marriage_runtime.py:inspect_marriage_chart_json`已经可接受额外`calendar_inputs.local_time_iso`、`calendar_inputs.iana_timezone`；如提供真时刻，可用`solar_chart_clock`对照日期时支及当前节气、年/月柱（若传）以及全部九宫的起局重新核对，杜绝用户自己写`engine_verified`绕过。若实际六合宫落在该旬空支宫，软件会按`successful_outcome:4`、`failed_outcome:3`计算后续填实/冲实的**候选真实节气月区间**，但必须在完整作者式用神/全盘反证/领域成败推断后才能从中选首选实断；如果六合并未旬空，就不能强套此应期法。缺剩余24项原著条件和主用神解释时仍不能发布具体一例真实婚姻成败/日期，不能用好听的“套话结论”冒充算出结果。此限制是执行正确性，不是用户书籍资料不充分。后续项目要继续实现更多源书条件和作者完整证据综合的规则执行、用原书未见家族盲测、再给GPT润色200字。

**DB继续增量，不重置**：以最新版婚姻V1.4 SHA256 `ac4401378302319799e0cbf07c906ffdc06ffb2f91ce49e149aac40261c235da` 为唯一本轮上游，迁移`schema/migrations/043_marriage_original_book_timing_astro_v15.sql`新增20条规则、1个作者首断历史研究、2个天文节气月候选、2个书源反馈检验与审计记录；原194案例/43章、9基本婚姻方法/22细场景、2古籍起盘样本44回归均原字未改，SQLite `integrity_check=ok`、外键0。**V1.5最新完整SQLite** `archives/sqlite/WenguaApp_双书194案例_婚姻原书应期天文推算V1_5_完整研究库.sqlite3`，大小14495744字节，SHA256 **`619867ef0f81234c662fbc1796de1c6844e9c1ecf12f59a904d20f9c90b757f3`**，XZ同名`.sqlite3.xz`大小1151600字节 SHA256`e1ceb920ac1e675e869aad0b30c11f7db26e6db7710d41ffab8446283b605159`，manifest`archives/sqlite/shenqi21_kaiwu22_marriage_author_timing_astro_v15_manifest.json`。有书中历史已知预判择月的研究回归，但**未见现实婚姻事件的全六层正式预测实例仍为0**。之后凡新增知识/方法/细领域/历史反馈均以V1.5完整SHA为上游，用新的编号新文件名版本增量。

## 2026-10-21 V1.6 INDEPENDENT MARRIAGE AUTHOR-JUDGMENT + FAMILY HOLDOUT FINAL

**已实际建立不依赖书上作者现成结论的独立婚姻初断程序**：src/wengua/marriage_judgment_v16.py。在已核盘面JSON与本地四柱节气基础上，绑定真实subject和partner的年命天盘干与六合，进行五行相生比和、克制、双方主辅、门迫、旬空、月日冲破、地支刑害、天干入墓及八门四季旺衰源规则审计；对每项保留支持、反证、历史 source_sha 与规则出处，原书已知作者判断与事后反馈**不作为初断输入**。传统结果明确取 success/failure/mixed/unresolved；在符合书上“先判成败、再择对应空亡填冲”的条件时由离线实际节气月和天干支转换产生可重现首选时间窗口；如果其他格局组合仍未能完成，完整第六层人话不得伪装为已完整通过。

**家族级留出开发评测已真实做出，且明确记录误断不能删：** 两个不同历史 event_family，《开悟之门》婚姻第二例、第三例中的三个问事，三个生成盘与原书八个外围宫门/神的合计24次对照一致；heldout整族完全排除初断引用，作者预测和书内后续结果只在结果算出之后做 evaluator 比较。结果 **3次明确成败、仅1次吻合书内后验、2次错断**：例二真实婚姻不能维系被程序误断能维系；例三第一位对象断不成吻合；例三第二位对象断能成而原书报告不成。这里是**已经接触过整体书料的历史研究dev测试，不是一次性封存测试，也不是独立现实准确率证明**。失败原因是程序在年命比和/相生时未充分落实作者示范的乙庚男女宫、六合多宫制化、岁令和六仪击刑等反证；下一轮须依古籍增强完整组合，而不是看过2错案就硬调权重掩盖错误。原书同性情感明确首断失误案继续只能在负例/纠错层出现，绝不能升为正向首断样板。

存储追溯：schema/migrations/044_marriage_source_initial_judgment_and_family_holdout_v16.sql；scripts/evaluate_marriage_family_holdout_v16.py；scripts/build_marriage_judgment_v16.py；tests/test_marriage_source_blind_v16.py；tests/test_marriage_family_eval_v16.py；tests/test_marriage_judgment_v16_archive.py；独立Actions归档workflow .github/workflows/build_marriage_judgment_v16.yml。**唯一后续父库** archives/sqlite/WenguaApp_双书194案例_婚姻作者式判断与家族留出评测V1_6_完整研究库.sqlite3，大小14534656字节，SHA256 **89cd5eb51f4eec7e41092a2bb8f5f624c1c6e7e4eb2225d00051e2d6c8e4a5f4**，XZ SHA256 168db015644c9ad4e86a8d1f8573703de80f7555dd400404d85b50a0afea8942；前驱全库V1.5 SHA256 619867ef0f81234c662fbc1796de1c6844e9c1ecf12f59a904d20f9c90b757f3。原194案例、43节、22场景、20原著应期、原研究44条及原字全部保持，SQLite完整性和外键检查通过；V1.6额外3份作者式首断和**独立存放3份事后书中事实标签**，1个记录真2错的开发评测审计，没有新增真实陌生人的预测认证。每次新增一个新版本SQLite和清单上传GitHub，不改UI。完整方法和两条错断见 docs/MARRIAGE_SOURCE_BLIND_JUDGMENT_V1_6.md。

## 2026-10-21 V1.7 MARRIAGE ORIGINAL RULE COMBINATOR 27 CONDITIONS / TWO OTHER FAMILIES

**必须保持婚姻V1.7真实状态而非重开工程。** 已实现27条《开悟之门》第四章及婚姻原案逐字索引，含章节整SHA/原文行/条件用神/反证/应期范围；引擎`src/wengua/marriage_book_combinator_v17.py`已经计算天盘六仪指定击刑、三奇墓、时支马星、81对有方向的天盘/地盘干、门迫和月令旺衰、九星八门真伏吟/反吟、太岁支所在宫、日时干位置与关系；`analyze_marriage_v17()`在V1.6初判基础上按书中条件合取，年命主证不能静默覆盖乙庚、六合、刑墓空迫等反证。只在新旧成败相容且确有书源应期条件时使用已计算节气窗口，不能沿用结果已被反证改变的旧应期，不能做机械概率加权或编造时间。六甲天显伏吟例外、土转换月与门迫月令强弱，必须有原文对应。未做的24项仍unknown；不推算真实人格、性行为、法律裁判或健康结论。

**开发测试/错误账本强制保持**：V1.6看过的3问不能再作为新秘密盲测，结果仍为1吻合2错断；V1.7例四、五仅为其它事件家族source-holdout和原书八宫几何、缺失年命拒断回归，缺对方年命/最终结果都未评分，真实新命中评测为0。例六作者自承初断失误保留负例，性取向非疾病。我们接受原书真实案例无需用户逐件人工审批，但绝不把作者书中自述当做独立科学验证。不得根据旧错题结果反向拟合规则后宣布同批错误消失；下一轮使用新未参与调节的其它family，保留所有失败。

**当前唯一新版完整SQLite**：`archives/sqlite/WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3`，SHA256 **`e6bc297b10b0f911b1cc03392afe7e53bc51a34d8acffecd674a9f5e343af675`**，旧194案例和旧2个错断均在；独立`schema/migrations/045_marriage_conditional_combinations_other_family_v17.sql`、builder、回归和工作流已经GitHub归档成功。详细完成范围和下一验收门槛见`docs/MARRIAGE_BOOK_COMBINATOR_V1_7.md`。禁止覆盖V1.6原始二进制，禁止用旧SHA继续派生；不做UI，第六层成品断语须全24项和真实应期可辩后才发布。
