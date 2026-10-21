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
