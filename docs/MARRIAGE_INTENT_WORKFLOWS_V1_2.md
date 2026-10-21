# 婚姻九类问事 · 两本书作者方法断案流程 V1.2

## 范围与约束
本专题只针对婚姻领域，从《神奇之门》婚姻篇6案、《开悟之门》婚姻篇6案及其最终错例篇2案学习，共14个已入库婚姻事件家族；不同领域案例不在此重复计数。**目的不是九条万能断语，而是九套针对不同目标事件、不同当事人关系的完整取用与证据推理步骤**。每套均引用真实原著章节 SHA、行号、原书案例ID及首次分析或后验反馈角色。数据完整版与机器流程：`data/knowledge/phrase_library/marriage_v1_2/intent_workflows.json`。

《神奇之门》默认取天盘乙奇表示女方、天盘庚表示男方，比较乙庚落宫相生克刑冲、门星神吉凶、六合和双方年命（《神奇》婚姻篇第5、9、11、13行）。**这些是作者原书传统候选规则，不是所有真人性别与关系结构的通用固定代数等式。**《神奇》母问女儿案在乙庚不匹配背景时重点换用女儿年命/时干与六合；《开悟》王大妈案综合乙庚、日时干、双方实际年命、父母宫与六合旬空（第39/41/43行）；第45行后来领证及举办婚礼的结果不得当初断证据；最后错例章中两名女性问离婚复婚，机械年命取用均错，见第382及409–413行。年代久远的出轨与性别类象不得作为现在人物隐私的事实证据。现代婚姻、健康、法律问题仍以实际行为和专业信息为准。

共有八个步骤：问题目标→人物关系→主次用神→支持证据→反证→明确传统结论→按历法实际计算应期→GPT自然中文。盘面全项刑冲破害、门迫、墓库、驿马、旬空、暗干及旺衰的24因子审核为所有子类型的**共同前置过程**，不是选择性遗漏。默认推理产物都只在古籍传统模型范围内，不宣称科学上能够确定预测现实成败。数据不足时必须指出确切缺失而非虚构期限。独立流程没有直接书例的要特别标明“相邻案例推导”。

## 九个问事子类型详细流程
### 1. 恋爱是否谈成 · `relationship_form`
**要断的事件**：互相确认关系；持续交往。**原书证据等级**：`direct_examples`。具体回答能否谈成、谁主动、成事窗口；不要把互有好感断成已经订婚。

1. **resolve_query**：先识别正在谈对象、双方是否已有相识/接触以及问测人是本人或父母；不能盲猜来意。
2. **role_bind**：问者≠婚恋当事人时先绑定本人年命及其对象年命；代测儿女优先查看时干、乙庚、六合及实际年命的相对证据。
3. **select_primary_secondary**：乙/庚为传统候选，结合日时干、双方年命和六合，确定这一次用来代表谁、谁主动，记录九宫位置。
4. **evaluate_support**：检验两方宫位生克比和、门星神旺衰、六合及内外盘、相合或太岁助力是否形成实际促进。
5. **evaluate_counterevidence**：检验年命六仪击刑、空亡、入墓、门迫、伏吟、对方不积极、家长阻挠等；《开悟》两个对象不成却次年另成不能混为一个对象。
6. **form_outcome**：对指定双方给出能谈成/不能谈成/延迟以及可能由谁推动，避免泛指未来总能遇到对象。
7. **calculate_timing**：按支持成立的目标选择乙庚/六合/年命可应的月令、空亡填冲、旺相及值使/日时，准确给出交往关系确立的期间，反馈日期不准倒灌。
8. **write_and_audit**：约200字先说该对象结果与首选时间，再点明最强两项证据与重要反证，引用古籍仅作内部依据。

**原书引用**：`shenqi/marriage_prediction_ch02` · `shenqi.marriage.mother_asks_son_courtship` · 行 54、58、64（original_reasoning）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.mother_asks_daughter_marriage` · 行 107、113、119、125（alternative_role_binding）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case03` · 行 123、125、127、129、131、133（original_reasoning_and_initial_future_claim）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case03` · 行 135（later_feedback_do_not_train）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case04` · 行 173、175（new_partner_evidence）。


### 2. 求婚订婚双方议婚 · `marriage_proposal`
**要断的事件**：明确接受求婚；双方同意订婚。**原书证据等级**：`adjacent_cases_no_independent_engagement_prediction`。婚事谈成不等于领证或办婚礼；可分问本人态度与两家意见。

1. **resolve_query**：明确用户问求婚接受、正式订婚还是两家谈妥，不默认三者一日完成。
2. **role_bind**：确认是否本人发问；问儿女时以实际结婚双方为主体，另外绑定父母年干与双方父母态度。
3. **select_primary_secondary**：主选双方乙庚、实际年命，合看六合及父母对应年干/宫位、日时干。
4. **evaluate_support**：看本人两方愿意程度的相生比和与六合、有利门宫、双方家长宫位是否支持；王大妈案例中父母同意是明确支撑。
5. **evaluate_counterevidence**：检验虽相合却逢空亡、彼此年命刑、乙庚克、本人态度不积极、父母阻碍的相反信息；不能仅父母催促就推定当事人同意。
6. **form_outcome**：明确双方是否答应议婚/订婚，不把复合、领证当求婚已经接受。
7. **calculate_timing**：比较用神、六合、家长宫与时干的旺衰/出空、交节/月合候选，选出议婚/订婚窗口；此子流程以相邻结婚案例推导，不能称原书独立实证。
8. **write_and_audit**：先说是否订下及何时，说明两家/双方中的主要促进或阻碍及证据不足时的确定缺项。

**原书引用**：`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case01` · 行 9、31、35、39、41、43（parents_and_marriage_progress）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.mother_asks_daughter_marriage` · 行 107、113、119、125（parents_opposition）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case03` · 行 123、127、129、133（counterexample_past_suitor）。


### 3. 结婚登记 · `marriage_registration`
**要断的事件**：法定婚姻登记完成。**原书证据等级**：`direct_case_feedback_separate_events`。必须区分登记日与婚礼日。

1. **resolve_query**：明确问登记何时完成，不是何时办酒或何时认识；登记作为单独target_event。
2. **role_bind**：核对双方年命、男女双方是否真实有意登记、问者代测关系，保留亲家宫位角色。
3. **select_primary_secondary**：乙庚及双方实际年命为主，六合婚姻象与日时干、父母年干为辅；作者例一重点使用年命与两家。
4. **evaluate_support**：乙庚宫位、双方年命相生及吉门、六合、家长支持、日时内盘与年支相合作为支持链。
5. **evaluate_counterevidence**：检查双方年命未戌半刑、用神空亡、年命与六合相克、婚期或人员态度不合；六合空亡有应期作用也可提示当前未成。
6. **form_outcome**：输出能否完成登记，可能延迟还是当年具备条件；不能从后续真的登记来修改当时用神。
7. **calculate_timing**：本书例一甲申旬午未空，作者以子丑月冲实并配寅亥合、内盘快断年内；日期转换需真实干支历。书报12月16登记只是独立反馈，不能照搬为新盘日期。
8. **write_and_audit**：用自然语言明确登记能否成功及首选历法窗口；婚礼日期不得冒充登记日。

**原书引用**：`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case01` · 行 31、35、39、41、43（pre_feedback_methods）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case01` · 行 45（later_feedback_date_not_training_label）。


### 4. 婚礼举办 · `wedding_date`
**要断的事件**：举办婚礼仪式。**原书证据等级**：`direct_case_with_distinct_wedding_outcome`。须另断婚礼举行，不把能登记等于马上办酒。

1. **resolve_query**：先把举办酒席/举行婚礼与恋爱确定、订婚、登记严格分开。
2. **role_bind**：绑定新人双方、婚事主导的家庭问者与两家支持情况；宾客及社会角色只在书源有证据时辅助。
3. **select_primary_secondary**：双方乙庚与年命、六合婚姻象为主，年干双方家长与时间宫、日时辅助，需检查是否已经登记的现实背景。
4. **evaluate_support**：六合与新人两宫及两家相生，日时内盘快、太岁年月支相合和驿马发动有可能参与快慢。
5. **evaluate_counterevidence**：登记已完成不代表婚礼必然举办；六合空、伏吟、冲刑/墓库、现实推迟须考虑，不能填充不存在的婚礼安排。
6. **form_outcome**：明确举办/延期/未有证据，不自动把登记日期当婚礼完成。
7. **calculate_timing**：另算婚礼应期，按出空/冲实、宫位旺月、马星冲动等有书源条件选择。王大妈案例晚于登记的婚礼为后验独立报告，仅用于验证方法。
8. **write_and_audit**：一句话区分办婚礼和领证的两个时间，说明依据而非重复恭喜话。

**原书引用**：`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case01` · 行 35、39、41、43（author_original_wedding_expectation）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case01` · 行 45（later_distinct_wedding_date）。


### 5. 婚姻是否稳定 · `marriage_stability`
**要断的事件**：指定期间内婚姻关系稳定性与关键转折。**原书证据等级**：`direct_examples`。趋势目标应有观察期和波动窗口，不强行单日作行政事件；不能宣称全部家庭隐私。

1. **resolve_query**：问的是未来哪段时间的相处、还是能否长期维持婚姻，确认已有婚姻与观察窗口。
2. **role_bind**：以夫妻本人为主体，代问者另记；双方乙庚及本人年命与配偶合干综合，允许非异性关系按角色而非固定性别类象重新选择。
3. **select_primary_secondary**：主选双方本人和配偶年命，乙庚/相合干为传统附参，六合婚姻、日时干与值使为辅，源中初断不得混事后。
4. **evaluate_support**：看双方宫位相生比和、旺相吉门、六合得生、伏吟在具体条件下持续之象，先形成维持支持。
5. **evaluate_counterevidence**：看宫位冲克、夫妻年命落宫、伏吟是否为困局或长期不动、空亡/刑破/门迫，避免机械“伏吟必稳定”。
6. **form_outcome**：对指定期间断稳/有明显矛盾/分阶段改善或恶化；不凭一个冲说必离婚。
7. **calculate_timing**：求旬空冲实/生助/旺月在观察期内的转折时间，输出阶段范围及关键变化窗口，不把趋势问题硬变成法院登记日。
8. **write_and_audit**：直说指定期间稳不稳、什么时候有可能出现明显变化和为什么，书源预测不等于现实安全或家庭法律结论。

**原书引用**：`shenqi/marriage_prediction_ch02` · `shenqi.marriage.wife_asks_husband_affair` · 行 361、363、365、367（couple_palaces_and_longevity）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.middle_aged_woman_divorce` · 行 223、229、235、241（spouse_conflict）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case05` · 行 211、223、229（remarriage_stability_questions）。


### 6. 离婚与办完手续 · `divorce`
**要断的事件**：双方关系走向破裂；离婚协议或法律登记完成。**原书证据等级**：`direct_and_explicit_counterexamples`。心生离意、分居、法院判决/登记是不同事件，分别算应期。

1. **resolve_query**：查明目前已婚/分居/拟离婚/已离婚，具体问是否会离还是行政/司法何时办完。
2. **role_bind**：绑定两个夫妻本人、离婚代问家长与双方年命；避开把亲属年命误作被测夫妻。
3. **select_primary_secondary**：乙庚两宫、夫妻实际年命、六合、日时干与合干/开门等作为多层证据，离婚证/法院用神只在书源步骤支持时辅助。
4. **evaluate_support**：原书逐步看夫妻宫互冲克、年命太岁冲克、六合受制、杜门/死门/芮星/伏宫等是否共同显示关系破裂。
5. **evaluate_counterevidence**：双方年命相克或乙庚冲不能单独断离；最后章两女性同盘年命推断错例必须作为强制反证，需核对现实婚姻进展及反向宫证。
6. **form_outcome**：针对离婚倾向和法律手续分别断成败：可能感情破裂而暂不办手续，不可合并成一个结果。
7. **calculate_timing**：书中1997腊月矛盾与1998寅月法院办理为两个时间：按太岁、六合、双方年命同克与月令逐目标择月，必须用核实的节气干支历转换，不把反馈应期泄漏给首断。
8. **write_and_audit**：给出是否离、主要阶段和手续窗口，提醒古籍象意不能替代真实法律/安全支持。

**原书引用**：`shenqi/marriage_prediction_ch02` · `shenqi.marriage.young_man_divorce` · 行 178、180、182、184（divorce_original_reasoning）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.middle_aged_woman_divorce` · 行 223、229、235、241（divorce_and_timing）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case02` · 行 73、77、81、83、85、87、89、91（marital_years_and_timing）；`kaiwu/questions_answers_errors_and_methods_ch03` · `kaiwu.final.divorce` · 行 382、384、385、409、410、411、413（year_born_stems_cannot_prove_divorce）。


### 7. 分手争执后和好 · `reconciliation`
**要断的事件**：恢复联系与情感和解。**原书证据等级**：`adjacent_case_inference`。和好不是重新办理结婚手续，应期独立。

1. **resolve_query**：确定问的是争执后恢复联系、结束分居还是已离婚后复婚，先把目标锁定为情感和解。
2. **role_bind**：确定问者主体和分开的对象，二人年命、近期是否仍有联系，不把家庭成员作为亲密关系双方。
3. **select_primary_secondary**：乙庚/双方年命、本人及相合干、六合、日时盘为取用候选；婚姻登记门只在真正问登记时才升主用。
4. **evaluate_support**：核对双方宫位是否互生、六合支持、对方是否主动或时干有动象，找促成沟通的证据。
5. **evaluate_counterevidence**：核对伏吟拖延、空亡、刑冲、已断联系和年命假合、现实意愿相反，不能见生便说会复合。
6. **form_outcome**：明确能和好/不能/只能短暂缓和，不能把家人希望当本人愿意。
7. **calculate_timing**：按双方宫位生助、六合填冲、对方年命旺月/马星变化择恢复联系窗口；如果无直接案例，只保留相邻复婚论法的待核来源标签。
8. **write_and_audit**：先说能不能和好及哪段时间，不自动把复婚登记写进回答。

**原书引用**：`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case05` · 行 223、225、227、229、231（ex_spouse_contact_and_potential_reunion）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.wife_asks_husband_affair` · 行 361、363、365（marriage_restoration_condition）；`kaiwu/questions_answers_errors_and_methods_ch03` · `kaiwu.final.remarriage` · 行 382、384、385、409、410、412、413（counterexample_year_stem_compatibility）。


### 8. 已离婚复婚 · `remarriage`
**要断的事件**：原夫妻重新建立婚姻并办理登记。**原书证据等级**：`direct_book_example_without_followup_plus_counterexample`。原配重归、重新恋爱与正式复婚三层独立，必须检验双方真实意愿。

1. **resolve_query**：确认为曾依法离婚的原配双方要再次登记，区别只是纠缠/联系或新恋爱。
2. **role_bind**：两位原配与代问者角色分清；双方实际年命、目前主动一方以及现实复婚意向明确。
3. **select_primary_secondary**：乙庚为关系框架，本人日干和配偶合干、双方年命、六合、开休二门为候选。
4. **evaluate_support**：《开悟》案例辛日丙辛合、乾生坎、乙庚互生显示愿意复婚，但庚宫逢空、丙水休囚制约；要同时留下有利和阻碍。
5. **evaluate_counterevidence**：年命相生不必复婚——末章一女子根据年命合而判断会复婚但书报未成；反向年份空亡与伏吟先检查。
6. **form_outcome**：明确双方能否真正复婚，单纯前配偶追求不视为办成登记；可分别判断有联系但尚未登记。
7. **calculate_timing**：《开悟》案例作者给农历十、十一月（乾坎旺相，空亡影响减弱）的**书源候选**但未提供未来兑现反馈。新盘据真实月令/空冲/扶生算合适窗口，并明示此书例未验证。
8. **write_and_audit**：给出复婚登记的主预测、时间与现实沟通阻碍，不能拿作者未证实的话当已实现。

**原书引用**：`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case05` · 行 211、217、223、225、227、229、231、245（author_conditional_later_remarriage_prediction_without_followup）；`kaiwu/questions_answers_errors_and_methods_ch03` · `kaiwu.final.remarriage` · 行 382、384、385、409、410、412、413（author_initial_miss）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.middle_aged_woman_divorce` · 行 223、229、241（past_partner_cross_palace）。


### 9. 婚外关系疑虑 · `trust_question`
**要断的事件**：双方信任变化；用户提供的具体可核实关系行为。**原书证据等级**：`direct_traditional_symbols_but_not_independent_reality_proof`。传统符号不能证实真实私生活、出轨行为或性取向；不得指定某人作第三者。

1. **resolve_query**：明确问实际哪种行为：信任变差、联系减少或是否存在第三人；不从模糊盘面猜隐私。
2. **role_bind**：夫妻本人、伴侣、可能存在的第三人必须作为独立角色；未证实第三人身份只能虚位，不套‘男/女固定出轨’。
3. **select_primary_secondary**：传统书源丁/丙为第三者类象只在问事已锁定且用神确认时列候选；先检查乙庚双方、年命、六合及日时干。
4. **evaluate_support**：核对多宫联动的干合关系、宫位旺衰、生克、相关人信息，形成传统象意倾向而非事实裁决。
5. **evaluate_counterevidence**：检验空亡/门迫/刑冲、第三者符号歧义、源书不同性别/代问错误；《开悟》同性情感错例说明问事未知时猜对象性别会严重误断，且性取向不是疾病。
6. **form_outcome**：最多给出盘面对于关系信任和沟通的传统趋向，不以盘证明某人现实出轨、怀孕或犯罪；绝不鼓励监控/侵犯隐私。
7. **calculate_timing**：只针对指定阶段信任或双方联系变化尝试计算应期，不把某个人‘出轨发生日’虚构为可断日期；若无法对应具体可靠事件则明确不可确定。
8. **write_and_audit**：输出自然但审慎的信任状况断词，预测与事实认定保持严格区分。

**原书引用**：`shenqi/marriage_prediction_ch02` · `shenqi.marriage.middle_aged_woman_divorce` · 行 229、235、241（third_party_symbol_in_context）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.third_party_asks_marriage` · 行 287、293、299、305（third_party_askers_role_changes）；`shenqi/marriage_prediction_ch02` · `shenqi.marriage.wife_asks_husband_affair` · 行 361、363、365、367（couple_main_yongshen）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case06` · 行 283、285、287、289、293、295（incorrect_initial_gender_assumption_and_first_forecast）；`kaiwu/marriage_prediction_ch02_section02` · `kaiwu.marriage.case06` · 行 297、299、301（later_feedback_do_not_train）。

## 共同结果与应期输出契约
对输入一个实际完整已核盘面JSON：`domain=marriage`→选`intent_id`→按8步推理→形成有来源的`target_event/outcome`→按真正已核历法计算并选择日期或观察期间→自然中文约200字。输出审计至少记录`primary_yongshen,secondary_yongshen,people_role_map,source_refs,author_initial_evidence,counterexamples,all_factor_checks,event_outcome,timing_candidate_windows,timing_primary_window,timing_selection_rule,book_error_flags`。每次新的受测盘都必须重新算宫位、年命与时序，不能重复使用前人案例中的应期。现存作者事后反馈只能作为测试和错误学习层，不能泄漏进推理。

## 当前验证结果与下一步
9个婚姻子流程定义、72个阶段步骤和30条逐行原书出处已完成入库，194个古籍整案、43来源节、4个旧自然表达草稿不变。**目前0个新完整已核九宫断语实例、0个正式批准的婚姻成品断语**。请勿把建好流程等于已经实现能对任意JSON输出可靠日期：仍需将本项目真正起盘/历法计算器与条件证据评估链接起来，并用未见过的事件家族执行盲测。其余领域以后遵守同一八步框架依次扩展，不能拿婚姻的用神强行套工作。
