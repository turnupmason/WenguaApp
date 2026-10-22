# WenguaApp 领域断语生产进度 — append-only V1

> 本文是下一轮 Agent/Codex/GPT 接手领域化断语开发的状态依据。每次完成实质增量须同时更新根 `AGENTS.md` 和 `docs/PROJECT_STATUS.md`。案例总数与短语数分开，绝不把“研究候选文案”当作可发布预测。

## 基础资产冻结

- 用户已提供的双书资料：来源章节 **43**（神奇21、开悟22）、整案 **194**，两书已收材料原书研究库完整继承，历史全文、案例、原案推理、19项明确初断错误等旧表保留不变。
- 1080状态：`2阴阳遁×9局×60时干支`，`state_index()` 结果**1080互不重复**。现有实际 `core.py` 返回 `status=index_only_unverified_chart`，该事实不等于1080个完整九宫已经逐一由起盘引擎验算成功。
- 每领域基础情境索引理论 **388,800 = 1080×60年命×3年龄组×2性别**。真实输出还要按问事子主题、代测关系、问事人/被问人、双方年命及当事人身份进行额外绑定；不是 388800个已验证答案或可发布结论。
- 限制：不允许缺九宫仍填一张虚构的盘；不得由GPT自行推断未知暗干、旬空、时区和九宫方位；对门迫不能杜撰源书没有的数值权重；按错局但书上断对必须与错案分开保存。

## 各领域状态

| 领域 | 阶段 | 书源历史事件 | 有条件GPT中文候选 | 已核完整JSON实盘实例 | 审核通过可发布 | 下一步 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| **婚姻 `marriage`** | **prototype_draft** | 14（神奇6+开悟6+错例2） | **4** | **0** | **0** | 复核确定性引擎的全九宫JSON与24项因素audit，绑定问者/对象/年命/性别、选择婚姻用神，然后逐条测试来源条件和自然成文 |
| 健康 `health` | not_started | 待独立统计 | 0 | 0 | 0 | 婚姻领域实现稳定后再开始 |
| 工作 `employment` | not_started | 待独立统计 | 0 | 0 | 0 | 不与婚姻共用无条件文案 |
| 失物 `lost_property` | not_started | 待独立统计 | 0 | 0 | 0 | 仅复用经确认通用的九宫事实 |
| 机运 `life_opportunity` | not_started | 待独立统计 | 0 | 0 | 0 | 依具体问事和关系选择用神 |
| 其余历史领域 | not_started | 仍保存在194书源完整库 | 0 | 0 | 0 | 逐领域后续排期，不在本批提前制造条目 |

## 婚姻第1批（2026-10-21）

- Prompt：`prompts/marriage_reading_v1.md`，版本`marriage_reading_v1.0`，SHA256 `f9a7a14f01e32353a2c97fc83d2be25ae18c621e9c491b37e30699ef968da099`，目标160–240汉字、约200字自然中文、非机械枚举串词。
- 协议：`docs/PHRASE_GENERATION_PROTOCOL.md`、根 `AGENTS.md` 的新高优先级章节。
- 核定层：`src/wengua/phrase_pipeline.py`，`FACTOR_IDS` **24类**逐项 checked/status/rule_ref/evidence/unknown-reason；`inspect_marriage_input` 即使数据全部字段提供，也仅返回 `ready_for_draft_review`，并明确 `cast_receipt_cryptographically_verified=false`, `eligible_to_publish_predictive_reading=false`。该类是**结构审计器，不是实际24类因素计算器和起盘引擎**；正式发词还需要从已有真实起局引擎验证这些证明材料。
- 数据：migration `schema/migrations/038_marriage_phrase_library.sql`，`phrase_domain_progress`、`phrase_template_drafts`、`phrase_source_links`、`phrase_context_instances`、`phrase_pipeline_audit`；4条候选文案，9处原书出处关联，0个实例与已获批短语。两书source书章SHA/行号与历史 case_id 外键约束。
- 四种场景：婚恋推进（多宫相生但不自动婚期）、母亲代问成年子女（人/时干与本人年命分开）、离婚与复婚（不能只看年命生克）、怀疑第三者（传统丁丙象≠现实出轨事实）。
- 数据导入：`scripts/seed_marriage_phrase_library.py` 从原全库SHA `c57153c296b1369e2b9bd78039dbe0cc191d67721f5042828e5ef54e70895e83` 使用 SQLite `backup()`；测试`tests/test_marriage_phrase_library.py`；GitHub归档 `.github/workflows/build_marriage_phrase_archive.yml` 已成功。写入完整二进制数据库、XZ及manifest。
- **现在唯一带断语新表的完整父数据库**：`archives/sqlite/WenguaApp_双书194案例_婚姻断语V1_完整研究库.sqlite3`（13,539,328字节），SHA256 `4c57e8bfdc4d745c19711542039c3f24aa95b7574de00843e64c1676082d4968`；压缩XZ1,116,872字节SHA `1607be07f470c94c7739e218e14185cabbb38500650e54e61a6d2e7805adff5e`，manifest `archives/sqlite/shenqi21_kaiwu22_marriage_phrase_v1_manifest.json`。
- 用户明确以后每一领域单独推进、短语存在SQLite、GPT负责自然润色。**不在目前阶段生成388800条静态语句**，也不要求用户重新提供已经收录两书原文；后续为可核真盘生成实例只需给可信来源的JSON和对齐的角色绑定。
- 质量验收：旧194个历史事件和43个来源完全不变、SQLite `integrity_check=ok`、foreign_key_check=0、4条原型160—240汉字、9条源链接、0虚构已核九宫、0批准发布。完成每轮需再查同一最新commit SHA的Python 3.11和3.12 CI。

## 下一个开发动作（不要重新初始化或做UI）

1. 在`src/wengua/core.py`已存在的索引以外，找现有实际九宫起盘算法与相关原书例盘校验，不可直接将状态索引当全九宫；给出可靠、结构稳定的JSON及引擎可验证签名。
2. 用第1个经过来源与算法比对的婚姻盘，验证24类因素全量实际计算（含不适用/未知），自动生成`evidence_json`；核对本次婚姻原型条件与反证。
3. GPT只在经过证据判断之后写约200字中文，自然、有重点、有保留；检索书源真实用神流程，错误案例作负面条件，而非对已知结局反向拟合。
4. 基于通过实际测试的独立情境逐步新增 `phrase_context_instances` 和新版本自然语言表述。逐领域统计真实覆盖率、可复用性与不同人物下的证据变化，**不要为了冲数量把条件不同的盘强行写出同一句断语**。
5. 每次递增版本产出SQLite/XZ/manifest，更新 `AGENTS.md`、本进度、status和提示词版本，GitHub CI必须指向最终main HEAD。

## 2026-10-21 PROMPT V1.1 AND IMMUTABLE PHRASE ARCHIVE TRACK

**版本区分（避免未来会话覆盖历史文案）：**
- 已生成并归档的**婚姻短语SQLite V1**是4条最初GPT风格原型、9处source关联，锁定当时Prompt `marriage_reading_v1.0` / SHA256 `f9a7a14f01e32353a2c97fc83d2be25ae18c621e9c491b37e30699ef968da099`。真实库SHA `4c57e8bfdc4d745c19711542039c3f24aa95b7574de00843e64c1676082d4968`，已归档永久保存，不得拿后来编辑的 `prompts/marriage_reading_v1.md` 文件字节去要求重新生成覆盖V1。数据库内原型仍`draft`、0成品实例。
- **当前工作Prompt已演进到V1.1**，现 `prompts/marriage_reading_v1.md` 已增加必须有条件地给出明确倾向与具体、可计算应期、不能靠“之后冲实”空话敷衍的需求；新的 `src/wengua/timing_engine.py` 有 `derive_timing_candidates()`、`finalize_traditional_decision()` 检查机制。它要求调用者提供带时区的干支/节气真实日期周期和方法版本，不会无中生有生成公历。源码对自报 `calendar_receipt` **尚不能提供密码学证明，也不保证预测实际事件有效性**；有真实缺项时应返回`unresolved_missing_decisive_evidence`并指出缺的具体证据，不能编日期。
- **Prompt V1.1 尚未另生成新数据库文件**。后续必须以带phrase表的V1全库SHA为父，用全新V1.1/V2文件名、迁移/版本行和manifest增量，而不能重用 `...婚姻断语V1_完整研究库.sqlite3`。研究原型数与审核实例数继续严格区分。
- 归档工作流 `.github/workflows/build_marriage_phrase_archive.yml` 已补**可重复执行的已有二进制库SHA、XZ及SQLite完整性核验**；当Prompt新版与旧archive所锁版本不同，保留旧快照并提示新版本必另建文件，不再因同名覆盖保护产生假的归档失败。另一个用于V1.1尝试的工作流 `.github/workflows/build_marriage_phrase_pilot.yml` 改为**只做3.11/3.12时法/短语回归测试并核验旧归档完整性**，它不再与前者同时写同名SQLite。两者都不会删除旧GitHub版本或修改UI。
- 实际待办：完成从经验证的真实起盘/历法引擎来的九宫全因子和具体应期的闭环，才将某个婚姻对象/关系/年命、判断及时间落到具体 `phrase_context_instances`，GPT负责明确、自然、约200字的最终表达；现在仍未有可发布实例。其余领域继续not_started。

## 2026-10-21 USER CLARIFICATION: DOMAIN INTENT ROUTING, NOT PREWRITTEN ALL VERDICTS

**明确架构：不是给每个大领域、每个小问题、每个1080盘都提前写死一条结论。** 提前整理的是两书中每个领域的基础知识、可复用取用神/证据/反证/应期方法、按小问事划分的决策目标，以及用于自然中文的表现规范。每次用户传盘JSON与真实问题时，先根据问题识别`domain -> intent -> target_event`，计算盘面所有因素，依据问者与被问者关系选主辅用神，检索作者实际证据链及其错案和书源限制，形成**这个问题专属**的成败判断与首选应期（由真实历法和证据计算），最后由GPT将已得到的结果写成约200字自然断案话语，才落实际实例表缓存。

工作大领域不是一句万能话。具体问：什么时候找到工作 -> 正式offer/入职；什么时候跳槽 -> 新岗位落地且离职/入职分别核算；未来工作顺不顺 -> 对**指定观察期**的趋势、重要转折及其时间窗口下判断；晋升、内调、保职、裁员、待遇等各有目标。**同一盘多个目标不是每个目标同一结果/同一应期**，也不能自动拆成不同历史独立事件；一人可在同一问事提出多个子问，依原书关系先逐目标断。同一书中多盘和同盘多人事件家族的区分沿用已有协议。

工作领域现在只是问题分类设计，并非已经入库生成工作断语；当前依用户要求**婚姻先做**，婚姻含恋爱、结婚登记、婚礼、离婚、复婚、稳定与第三者疑虑等问事子类型，各用不同的成功条件、结果事件和应期，继续只保存源书支持且附规则/来源的原型。婚姻V1.1全库真实存在：`archives/sqlite/WenguaApp_双书194案例_婚姻断语V1_1_应期强制_完整研究库.sqlite3` SHA256 `53bab00cefa4754753ab124b0653c0b7b2f68f0d63dae7783f6eea3d387f0e75`，还只有4条draft语言原型、**0个完整九宫经过联动验证的成品断语**、194旧书整案保持原样。不再回退到只有原书库/V1断语库当成最新父库。独立阶段指导见 `data/knowledge/phrase_library/domain_intent_registry_v1.json`。

用户要求“只要盘面完整、用神明确、应期规则有据可查就要断结果和具体应期”。这个**应当完成**的断案目标不允许以“之后再看空亡何时填实”糊弄：必须实际计算所选应期、选择首选日期/区间、给出明确的传统判断，列证据和反证。不表示每张盘的古籍条件都唯一对应现实确定发生的日期或现实准确率已验证；如果关键方法适用性冲突或真实节气历法缺失，必须精确给出为什么无法确定，不允许GPT臆造。未来每领域统一按相同标准，不预生成388800条重复结论。

## 2026-10-21 婚姻问事流程 V1.2 — 原书证据索引归档完成

- 原有婚姻V1.1四条自然文本样稿保留、不升级为真实断卦结果；新增9问事流程×8步=72个可逐条件跟踪的作者式方法节点，30个精确原书章SHA/原行号/原书案例ID的来源线索；其中明示非首次论证的案例反馈只能用于验证，书中错断不能拿后期解释洗成命中。
- 已完成的范围：恋爱、订婚、领证、婚礼、婚姻稳不稳、离婚、感情和好、复婚、信任疑虑；这是目前的**设计覆盖**，不是实际预测准确率覆盖。订婚与感情和好缺独立古籍验证案例，标记相邻案例外推；复婚章给出了月份但无后来实际复婚反馈；王大妈案例区分领证与婚礼两个应期。其余用户子问事仍可新增intent。
- 当前完整数据库SHA256 `2119735b5772feb0177c03b032be8070fef629060b509d30a26b5ce204c9aa2d`，路径 `archives/sqlite/WenguaApp_双书194案例_婚姻各类问事流程V1_2_完整研究库.sqlite3`，由V1.1 SHA `53bab00cefa4754753ab124b0653c0b7b2f68f0d63dae7783f6eea3d387f0e75` 无损备份增量。章节43、独立案例194、旧4原型、完整盘实例0、受审通过断语0。
- 下个进度门槛：真实JSON九宫全24因子、人物关系年命及每问事的主次用神条件核验；结合两书作者首次推理及后验错误审计计算传统成败、候选年/月/日应期并依据真实节气历法选首选窗口。GPT仅把已决定的结果写成人话。不能生成空泛“等填实再看”或编日期。之后逐领域复制同样方法。

## 2026-10-21 MARRIAGE 22 / GLOBAL SIX LAYERS V1.3 ARCHIVED

WenguaApp婚姻领域V1.3的“22大具体场景×六层强制执行”已归档，采用用户提供场景作为问题目录，以原有《神奇之门》《开悟之门》婚姻14个不同历史事件和9套旧方法的真实证据链作为基础。22场景并不是22个原书独立证明的预言方法，数据库保存132条六层详细步骤、89条携带原书HASH/原字行号/原案ID的来源关联，未经书内直接核实的场景明确标记研究草稿；用户示例里的身心疾病、家暴、出轨诈骗、强烈操控性格、法院判决、财产归属等“答案锁死”全部保留审计为不可从某一格局自动认定的现实事实，改为要查证的传统候选象意。婚姻细分场景的层三取用神与层五应期目标互不混淆。全领域统一六层：核九宫→算24全盘因素→绑定六亲/具体领域用神→检索全部古籍首断证据与错例→实际作出传统结果及计算应期→GPT自然约200字表达，完成合规检查率必须100%，现实预测准确率不得承诺。

**仅继承完整版V1.2** `archives/sqlite/WenguaApp_双书194案例_婚姻各类问事流程V1_2_完整研究库.sqlite3` SHA `2119735b5772feb0177c03b032be8070fef629060b509d30a26b5ce204c9aa2d`，迁移041使用sqlite3.backup保留所有旧表历史原行。最新完成的二进制完整版V1.3路径 `archives/sqlite/WenguaApp_双书194案例_婚姻22场景六层流程V1_3_完整研究库.sqlite3`，14,043,136字节、SHA256 `0eda2e3996192c31b7e75aeaf45745c6659dd2a73f5fe74bbf495dece36e6857`；xz 1,143,472字节、SHA256`d48491d9ce044d63f3e0ccdd4603e823ae3016c4fce55bf50fa548433006b827`；manifest`archives/sqlite/shenqi21_kaiwu22_marriage22_six_layer_v13_manifest.json`，integrity_check=ok，foreign keys 0。源书43节194历史整案、旧9流程72步30出处、旧4条GPT风格草稿全部保留。新增22场景132层、89个古籍重复来源见证、一个ALL_DOMAINS新合规合同与实例审批前层数trigger。**V1.3完整盘正式验收实例仍是0**，因为尚未实际接入九宫计算和独立节气历法。下一步连接JSON起盘与实际应期推理，对每个问事真正解盘和盲测。

全范围指令位置：根`AGENTS.md`、`prompts/global_six_layer_reasoning_v1_3.md`、`docs/MARRIAGE_22_SCENARIO_PROTOCOL_V1_3.md`、`data/knowledge/phrase_library/marriage_v1_3/twenty_two_scene_methods.json`，运行门禁`src/wengua/six_layer_contract.py`，数据库迁移041，专用回归测试和归档Workflow。之后每个领域都必须按六层阶段100%留痕、经测试后才有可发布断语，绝不能仅将某个神煞对应一个未经证实的现实指控。

## 2026-10-21 MARRIAGE V1.4 ACTUAL SOURCE CHART RUNTIME BRIDGE

婚姻V1.4首次运行**源码真实起盘结果 → 22场景分类 → 主次用神符号候选 → 部分可核盘面物理关系 → 两本书原始案例出处检索**。`src/wengua/marriage_runtime.py`使用现有Shenqi起盘模块在明确给定的节气和日/时干支下输出九宫地盘、天盘九星携干、八门八神、中五宫例外；得到日干/时干及乙庚、六合所在宫，计算真门迫（门克宫）、旬首旬空二支、宫五行。其余24因子没有真实古籍可执行规则或必要输入时明确标记unknown，不准GPT用“高权值”补算。两本书来源切换遵守后验反馈隔离。原书有两张完整起局实例：1995年6月11日阳3局丁巳时与1995年8月13日阴8局戊戌时，逐原印九宫对照；这**不**是两张婚姻真实问事盘，也没有独立现代历法核验。22场景×两张示例盘=44个完整的来源链调用研究fixture，**新增真实婚姻案例0、完整正式断语0、经验证具体应期0**。首次CI检测`door_press`误字段导致25而非24审计项目，经修复`door_press_palace`后双Python版本通过。

从V1.3完整研究库SHA `0eda2e3996192c31b7e75aeaf45745c6659dd2a73f5fe74bbf495dece36e6857`进行备份追加，迁移042与builder、source runtime tests和GitHub Archive流程全部成功，历史194个case/43source、9大问事/22场景方法及4草稿旧行未改。V1.4完整SQLite `archives/sqlite/WenguaApp_双书194案例_婚姻真实排盘接入V1_4_完整研究库.sqlite3`，大小14454784字节，SHA256 **`ac4401378302319799e0cbf07c906ffdc06ffb2f91ce49e149aac40261c235da`**；XZ同名`.sqlite3.xz`大小1149336字节SHA256 `369669099fe98654f8f8e5bdcfbb839349fd7586df13a2bc4707dbad331fd6d0`，manifest`archives/sqlite/shenqi21_kaiwu22_marriage_source_cast_runtime_v1_4_manifest.json`，integrity_check=ok、外键0。

下一个工程门槛：校验真实用户时区和节气、解决少数中五宫值使门特殊落宫起局法；逐条由原书建立其余全盘24因子事实计算；把真实问测对象的年命角色绑定到九宫；建立从作者首断案例选择主次证据与否定错误推导的综合判断器；采用已核干支历计算具体可辩应期，在真正未见盘上给出有界传统结论和GPT自然表达。不能说流程资料已齐就代表已经有任意盘全自动准确答案。

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

**最新已归档完整双书婚姻研究 V1.6**。不是重复写22场景流程；源码作者式初断可依据真实已起盘JSON及当事人年命形成带正反古籍依据的传统 success/failure 判断；在对应六合旬空且原书适用时可调用已有20条应期法及离线节气月真实换算。实现加入原书符号章节的六冲、六害、相刑、月日破、天干墓库和八门旺衰条件，但24项尚未全实现，不能把研究初断宣布为最终预测成品。

全家族初判隔离研究覆盖《开悟之门》婚姻例二一问、例三两问，共**3问、2个原书事件家族、24个与原文对照的外围门神宫位，1次吻合书内后验、2次错断**。女儿原婚姻和第二个相亲对象误判成，具体错误对照、原先作者出处和修正目标已保存；程序不读当前家族作者结论和反馈，得出结果后独立比较。注意本测试不是新从未见过的封存盲测，无法声称准确率或“已学会全部断案”。下一步按原书补全乙庚与年命主辅冲突、六合旺衰及反证、击刑墓空太岁和应期优先级等，使主年命关系不覆盖其他直接不利证据；用其他事件家族检测新增规则，不能据既看过的两个错例做机械答案修正。

完整 V1.6 SQLite archives/sqlite/WenguaApp_双书194案例_婚姻作者式判断与家族留出评测V1_6_完整研究库.sqlite3，14,534,656字节，SHA256 89cd5eb51f4eec7e41092a2bb8f5f624c1c6e7e4eb2225d00051e2d6c8e4a5f4；XZ 1,154,228字节，SHA256 168db015644c9ad4e86a8d1f8573703de80f7555dd400404d85b50a0afea8942；manifest archives/sqlite/shenqi21_kaiwu22_marriage_author_family_dev_v16_manifest.json。旧194案例、43章、22场景、9旧流程、20原书应期、4语言草稿均原行保留。迁移044 +独立后验标签物理分表+ 专用GitHub archive 均完成，数据库 integrity_check=ok，外键错误0。详细方法和错误报告 docs/MARRIAGE_SOURCE_BLIND_JUDGMENT_V1_6.md。

## 2026-10-21 V1.7 MARRIAGE ORIGINAL RULE COMBINATOR 27 CONDITIONS / TWO OTHER FAMILIES

**必须保持婚姻V1.7真实状态而非重开工程。** 已实现27条《开悟之门》第四章及婚姻原案逐字索引，含章节整SHA/原文行/条件用神/反证/应期范围；引擎`src/wengua/marriage_book_combinator_v17.py`已经计算天盘六仪指定击刑、三奇墓、时支马星、81对有方向的天盘/地盘干、门迫和月令旺衰、九星八门真伏吟/反吟、太岁支所在宫、日时干位置与关系；`analyze_marriage_v17()`在V1.6初判基础上按书中条件合取，年命主证不能静默覆盖乙庚、六合、刑墓空迫等反证。只在新旧成败相容且确有书源应期条件时使用已计算节气窗口，不能沿用结果已被反证改变的旧应期，不能做机械概率加权或编造时间。六甲天显伏吟例外、土转换月与门迫月令强弱，必须有原文对应。未做的24项仍unknown；不推算真实人格、性行为、法律裁判或健康结论。

**开发测试/错误账本强制保持**：V1.6看过的3问不能再作为新秘密盲测，结果仍为1吻合2错断；V1.7例四、五仅为其它事件家族source-holdout和原书八宫几何、缺失年命拒断回归，缺对方年命/最终结果都未评分，真实新命中评测为0。例六作者自承初断失误保留负例，性取向非疾病。我们接受原书真实案例无需用户逐件人工审批，但绝不把作者书中自述当做独立科学验证。不得根据旧错题结果反向拟合规则后宣布同批错误消失；下一轮使用新未参与调节的其它family，保留所有失败。

**当前唯一新版完整SQLite**：`archives/sqlite/WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3`，SHA256 **`e6bc297b10b0f911b1cc03392afe7e53bc51a34d8acffecd674a9f5e343af675`**，旧194案例和旧2个错断均在；独立`schema/migrations/045_marriage_conditional_combinations_other_family_v17.sql`、builder、回归和工作流已经GitHub归档成功。详细完成范围和下一验收门槛见`docs/MARRIAGE_BOOK_COMBINATOR_V1_7.md`。禁止覆盖V1.6原始二进制，禁止用旧SHA继续派生；不做UI，第六层成品断语须全24项和真实应期可辩后才发布。

## 2026-10-21 婚姻V1.8 年命可选、作者取用方法无年命实算（最终交接）

**用户明确修正——没有年命，不要求年命，不允许因缺年命直接判`unresolved`。** 任意领域的六层流程仍然100%强制逐项核验，但人的出生年命属于可选证据，`year_ganzhi`在`inquiry.subject/partner/querent`处未给就不使用、不猜、不从问事年份或时辰冒充推导。**日干/时干等不是年命的替代数值，而是原著针对不同问事关系的独立用神方法**。婚姻原书《神奇之门》原章lines5、9、11、54、107，以及《开悟之门》婚姻章lines39、75、79、281、285 的完整章SHA、具体原文字句SHA和行号保留，原著关键区别是：乙庚六合属传统婚姻象及男女符号，日干是问者、时干为问事事体；双方实际年命**有则兼看**，没有就继续从乙庚、六合、日时干、门星神格、月令、入墓空迫刑冲及具体角色判断，不能把有无年命当成占卦成败证据。

工程实现为`src/wengua/marriage_no_year_v18.py`：`analyze_marriage_v18`新增**三条条件化角色路由**：`both_years`继续调用原来V1.7年命及27条组合、`one_year_optional`只使用已提供一方年命为补充、`no_year_optional`完全不使用年命而以原书传统乙庚六合与日时干事件线比较支持反证。三条路均保留无法证实的真实他人心理、性行为、出轨、疾病等不能由象意确认的限制，特殊/同性关系不把男女传统符号映射为真实双方性别。只有不同源书象意基本同向且没有明确格局反证才可给`success`或`failure`传统候选；不一致就给`mixed`而非胡编精确命中结果。真空亡应期仅在原书条件真实触发且综合传统结果明确时以本地太阳黄经节气月计算；未满足不编日期。全部仍是研究级，不等于通过24项完整格局与新的封存独立预测评测，因此`publication_ready=false`，GPT第六层约200字正式断语仍不得偷跑。

**保存记录与完整母库**：从 V1.7 完整194案例真实母库 SHA256 `e6bc297b10b0f911b1cc03392afe7e53bc51a34d8acffecd674a9f5e343af675`以`sqlite3.backup` **增量** `schema/migrations/046_marriage_optional_nianming_v18.sql`。V1.8`marriage_v18_optional_year_scene_methods=22`，`marriage_v18_book_optional_role_sources=10`，`marriage_v18_missing_year_dev_studies=2`（《开悟之门》例四一方年命、例五双方未给年命，均已用原印八宫与程序复核；书中结局未证实，不能计算新命中数）；上一版27条件化古籍规则、194历史原案例/43来源节/1440历史盘格、既有**1次相符/2次误断**的V1.6开发数据原行不动。新的**唯一完整版下一轮父库**`archives/sqlite/WenguaApp_双书194案例_婚姻无年命作者取用方法V1_8_完整研究库.sqlite3` 14,673,920字节，SHA256 **`fbd2f6a5475e9f54cb9a98a42b1f96800cf8c1dd8d96f884951d900c7f287536`**；同名XZ压缩1,166,504字节 SHA256 `48c01e5603baac1f37baae41c9c32e6f5c70f7ab4abfa088f2a9e3b53e9f75cb`；`archives/sqlite/shenqi21_kaiwu22_marriage_optional_nianming_v18_manifest.json`完整性ok外键0。官方 workflow`.github/workflows/build_marriage_optional_year_v18.yml`以 Python3.11/3.12 全部通过并真实推送不可变二进制。

**实际运行**：`scripts/run_marriage_judgment_v18.py`接受已有起盘JSON、天文历法`calendar_inputs`（有时区时刻、四柱核盘）、婚姻`scene_id`与`question_text`；可以不提供`inquiry.subject.year_ganzhi`、`partner.year_ganzhi`乃至整段对象出生信息，结果中会清楚记录 no_year_optional 或 one_year_optional、原书SHA证据、没有发明出生年及真实应期触发。`tests/test_marriage_no_year_v18.py`遍历22种场景，`tests/test_marriage_optional_year_cli_v18.py`真实读写文件，`tests/test_marriage_optional_year_v18_archive.py`复核全194原书和旧两个错案。**未来所有领域参考同样处理“未提供年命”：必须先研究本领域古籍其他取用神，不问年命则正常按其他原书用神断，不得默认要求用户补充。**

核心方法细节及 JSON 调用：`docs/MARRIAGE_OPTIONAL_BIRTH_YEAR_V1_8.md`。未来下一步不是重启旧版本、更不能调参回看 V1.6 的两个错题当秘密测试，而是继续按原书逐条实现24项全部明确适用条件、不同问事领域主辅角色绑定和应期，使用真正未参与规则选择的整族事件作独立评测；所有失败样本保留，多轨原著来源保留。


## 2026-10-21 健康·病情严重程度动态模板 V1.9

用户新方向：弃用1080×60年命人工逐篇预写；各领域逐细分问事写一份包含真实条件、可填字段和证据冲突的长模板，代码每次根据真实九宫及原著条件填值。首发**health/severity**21段动态插槽及Python填充器，参考 docs/HEALTH_SEVERITY_DYNAMIC_TEMPLATE_V1_9.md。可定位天芮宫/体表内里及天心乙奇、天干有序克应和门迫/旬空；丁癸庚等疾病象意必须按内外盘、月令和门星神格上下文选取；24要素部分仍unknown不得胡填。当前研发draft，不发表任何实际医学严重程度、疾病类型或疗效断言。待CI归档的新V1.9全量SQLite只能以V1.8真194案库SHA fbd2f6a5475e9f54cb9a98a42b1f96800cf8c1dd8d96f884951d900c7f287536为父；历史原始书章和旧错断不变，其余领域/子问事尚未按本新模式完成。


## 2026-10-21 V1.9 健康病情严重程度动态断词成功归档（真正下一轮完整父库）

已由 GitHub Actions Archive V1.9 Health Severity Dynamic Template #39694290131 成功完成 Python 3.11/3.12 两套回归、无损 sqlite3.backup 和 SQLite/XZ+manifest 上传；对应 WenguaApp CI #39694290195 亦成功。构建源代码 commit 126165a00921fb9888e53936be3345c09d984703，归档机器人commit 383e2dc33a2ebfd87252de1881340006293fd3c3。之前调试阶段的失败 #39694070752、#39694207573 不删记录，也不当作当前成功状态。

**下一轮唯一完整父库** archives/sqlite/WenguaApp_双书194案例_疾病严重程度动态断词V1_9_完整研究库.sqlite3，14,714,880字节，SHA256 **b0b2aeaf9bfbb94be3f435391e8fb2b066b9c9da7a5a6675e3d22cf50c6ce55f**；同名.sqlite3.xz 1,169,532字节 SHA256 bfcef5a333c9500c77534ab53b7ee4f028860bfeef57dc429d6a5c01257d4a40；manifest archives/sqlite/shenqi21_kaiwu22_health_severity_dynamic_v19_manifest.json。父V1.8 SHA fbd2f6a5475e9f54cb9a98a42b1f96800cf8c1dd8d96f884951d900c7f287536 所有旧表原行保存，数据库 integrity_check=ok，外键错误0。计数 sections=43,cases=194,health_severity_v19_protocol=1,health_severity_v19_template_sections=21,health_severity_v19_archive_audit=1,marriage_v17_book_conditional_rules=27,marriage_v18_optional_year_scene_methods=22；V1.6两次错断继续保留。正式可批准实际医学预测0，真实疾病病情严重程度推断不可由古籍盘象证实。

后续疾病领域其他子问事都必须**基于这一版V1.9完整父库增量**，不得回退到婚姻V1.8或重新建空数据库。UI冻结，其他疾病子领域尚未开发。若还修改此模板，发布新迁移/新档案版本，不要覆写 V1.9。


## 2026-10-21 健康V2.0 多问事与人际角色绑定

21段「病情严重程度」详细模板由用户确认；必须填各星门神干代表意思、天地干病象、落宫内外身体对应、医药患者有向生克及条件化古籍综合，不可随意缩成一两句；对外只说“依据古籍”。朋友闻讯事件日干与朋友直接托测同辈月干候选不相同；自测、父母、孩子、侄辈、配偶亦不同。真实年龄性别排行由用户输入；无年命继续判断且不乱绑定个人宫。V2.0新增5具体健康问事及66段，文件 data/knowledge/phrase_library/health_v20/，执行 src/wengua/health_dynamic_v20.py，数据库迁移048，完整运行单测后归档。用户尚未批准其它病种模板，未来逐问题扩展，不能假称覆盖所有人体疾病方向。


## 2026-10-21 V2.0 正式归档验收及下一版本不可变保护

**GitHub原始程序专项验收成功**：Archive V2.0 Five Health Dynamic Intents #39700990517 对提交 2fa28e7e2269ec3f62d0e81d03ac8c9e9ba549f1 在 Python 3.11/3.12 回归全部通过；全库 WenguaApp CI #39700990516 全部通过。官方 Archive 工作流构建并推送真正的V2.0全量SQLite，commit e0a60cda3f68bd26fbf1c792bd09877329c29d34。数据库完整性 integrity_check=ok、foreign_key_check=0，且逐表逐行对照父库保留：194历史家族、43原书来源节、19原书错断记录索引、旧V1.6两个开发错断、婚姻V1.7 27条源规则、上一版V1.9 21段。

**之后的唯一父库**：archives/sqlite/WenguaApp_双书194案例_疾病五问事动态断词与人物关系V2_0_完整研究库.sqlite3，14,782,464 bytes，SHA256 **8c3914f47b3433d23ddf16b6ecf8fc2e2dc4380165646c010f49e87212fb913e**；同名 .sqlite3.xz 1,178,468 bytes，SHA256 **94d8be866314faebee1987ceb43394c3220e9f131c25c51af10a048b293f461d**。Manifest：archives/sqlite/shenqi21_kaiwu22_health_five_intents_v20_manifest.json。DB新增health_v20_actor_role_profiles=14、health_v20_intent_templates=5、health_v20_intent_steps=66、health_v20_archive_audit=1。医学真实预测验证数=0（此项目不能声称古籍预测医学准确）。

**重要：该完整V2.0数据库不可覆盖**；此前Workflow会被后续测试代码push再次触发，现增设archive_guard验证已存在文件必须等于manifest SHA及正式sha，并在已归档时只运行回归、不重新build/push相同版本；以后每次新的知识规则或真正断词版本都从此最新V2.0 SHA派生新迁移049、新V2.1文件及新工作流，不可借旧V1.9重写V2.0。追加跨阴阳、同一盘自测/父母/朋友/孩子、五意图×多盘50组动态填空回归以及全部九星八门八神十干象意字典覆盖审计，必须保持通过。UI仍冻结。


## 2026-10-21 V2.1 五行有向生克修正与历法信息自洽校验（专项修复）

新测试复核V2.0在中间解释器的一个**真实方向性bug**：字符串endswith("克")也匹配"受克"，导致某些天心星、乙奇、患者宫「受病宫克」被误说成「克病宫」。不能因V2.0 CI通过就宣称全部语义正确。**V2.0完整数据库、原代码和失败发现均保留不覆盖**；V2.1在独立 src/wengua/health_dynamic_v21.py 正确分支区分克、受克、生、受生、比和，且不同关系映射明确传统五行有向含义。针对治疗象，优先根据医生天心与乙奇宫是否确实克病宫生成条件化医药象，不再直接复用病重模板的普通综合结论；开门手术象按开门宫对病宫具体有向克制判断，不能自动视为实际手术建议。

新历法 guard 要求：用户提供的年/月/日/时各柱都符合六十甲子，month_ganzhi与month_branch必须同支，未给month_branch而month_ganzhi可验证则直接填实际月支，hour_ganzhi与真起局小时柱必须一致；不能将这个普通干支相容性检查冒充完整节气、时区或占验科学验证。患者出生年命仍完全可选。新运行脚本 scripts/run_health_dynamic_v21.py，tests/test_health_dynamic_v21.py（五个有向关系、实际月份/时柱冲突、阴遁五领域、多用户关系）；新迁移 schema/migrations/049_health_v21_directed_palace_relations.sql，append-only版本scripts/build_health_v21_archive.py，官方流程 .github/workflows/build_health_v21.yml。将从**最新完整V2.0库SHA 8c3914f47b3433d23ddf16b6ecf8fc2e2dc4380165646c010f49e87212fb913e** 全量备份并追加新五种关系规则和一条历法协议，不改194件案例、43原书节、两旧开发错判、V2.0的14人物和5问事66段；每次发布需独立SQLite+XZ+manifest，新V2.1工作流后续也必须检测已封存二进制不可重复写。此段仅为本轮执行交接，**CI尚未验收的版本不能写成完成**。全部五问事的用户文字仍只说“依据古籍”；不能给真实医学诊断或恢复日期。


## 2026-10-21 最终 V2.1 归档成功，唯一下一轮父库（健康方向人物/问事独立）

官方「Archive V2.1 Correct Directed Health Relations」运行 #39702020148 实际成功，Python3.11/3.12专项方向性+历法校验成功；「WenguaApp CI」 #39702020114 成功。源提交60f06bc39961ff8a45459b7fc85535718e840adf；机器人完整数据库归档提交 292b8b07cf68d773b46d24c186b627c67e7236f9。

**以后基于此唯一最新版完整父库递增**：archives/sqlite/WenguaApp_双书194案例_疾病有向生克修正与历法校验V2_1_完整研究库.sqlite3，14,798,848字节，SHA256 **25d95ed8df42ed0739d82cc930fcd5127ba187740c0b871fc3ae488d69bc81f3**。同名 .sqlite3.xz 1,180,032字节，SHA256 **a3a69f7bc8971cf9a90f4cc5e4fed2f4d5521e1b2bdccb256f3dfbf00980d372**。归档凭据 archives/sqlite/shenqi21_kaiwu22_health_directed_v21_manifest.json，PRAGMA integrity_check=ok、foreign key错误0。V2.0旧完整库SHA 8c3914f47b3433d23ddf16b6ecf8fc2e2dc4380165646c010f49e87212fb913e 保持不可变；V2.1无损保留两书原194件史案、43节、所有历史作者错断及开发两次错断、健康14人物、五问事66段、原婚姻27规则，仅新增有向生克五关系与月支/时柱相容检查审计。正式用户入口 scripts/run_health_dynamic_v21.py 与 src/wengua/health_dynamic_v21.py；旧V2.0代码保留，不要回退。

重要真实验收边界：测试通过的是九宫复算结构、角色路由、跨阴阳五意图填空、五种方向关系、历法相容、数据库行无损和接口回归；**并不证明所有24因素已全面实算、所有亲属源法都得到原书明确验证，亦不证明任何传统疾病判断具有医学预后准确性**。下个健康子领域要先有独立作者取用与单独长模板、正反例以及全24因素可用性条件，不许复用“病重”答案冒充其它问事。历史测试不能利用已看作者结局作为盲测。所有后续DB从此V2.1真完整SHA增量，新增迁移050/新version，不覆盖任何之前文件；界面冻结。对外说明依旧只写“依据古籍”，21段详细疾病严重程度模板的完整结构不可省略。


## 2026-10-21 用户真实四柱封关测试（必须停止其余四个健康子题的发布）

**最高优先级实时用户验收指令：**在开发任何更多健康细分问事之前，先用用户输入「丙午年、戊戌月、戊辰〔第三柱原写月，暂按日〕、壬戌时」运行**现有V2.1真正离线计算链路**，包括由历法推导真实时间、寒露节令/上中下元/阴阳遁及局数、完整九宫、按前期问事和对象选用神、21段详尽断词。禁止按想象的宫位或已见古籍故事拼结论。实测脚本 tests/test_user_health_20261021.py 首先核对2026-10-21当地戌时19:30、甲寅旬、寒露、阴遁六局，再调用astro_calendar.solar_chart_clock -> casting_shenqi.bureau_for_term -> casting_shenqi.layout_from_explicit_bureau -> health_dynamic_v21.analyze_health_v21()。测试的SELF只是为了程序能跑通而暂定的**未确认人物关系**；用户尚未选患者为自己、父母、朋友或孩子，未确认前不得将该篇作为现实正式出断。年命缺席，不猜。即便单测通过，也不等于用户认可21段的输出质量，更不等于古籍方法独立预测成功。

**另外四类 health/treatment、discharge、surgery、travel_for_treatment 完全未获用户模板审核通过，尽管V2.0里有对应草稿JSON及程序回归，发布状态必须是 draft/unapproved**。不得再用“另外四领域全部完成/已通过”向用户汇报。任何后续疾病子领域和其他领域一律暂停，只有用户明确验收这次severity实测结果后才可推进。此次只加测试/记录，不动V2.1已封存完整SQLite、194历史家族、失败账本、原始古籍或UI，不以新臆造测试事件污染书例数据库。用户只要文字输出全部21段，且每个星门神干有简短象意，真实触发的条件才能下结论，时间或角色缺项要显示。
