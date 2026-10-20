# WenguaApp · 当前 GitHub 项目状态（2026-10-19）

> 任一新对话先读根目录 **[AGENTS.md](../AGENTS.md)**、本文件、[章节账本](CHAPTER_LEDGER.md)、[逐章流程](CHAPTER_WORKFLOW.md) 和 [跨章知识架构](SEMANTIC_KNOWLEDGE_MODEL.md)，然后再动数据库/代码。历史账本不可删除或从旧聊天记忆补写。

## V1 核心方向

- 独立公开仓库：`turnupmason/WenguaApp`。优先**时家转盘**；先完成《神奇之门》《开悟之门》两本书；后续古籍及流派逐本、逐派验证。
- 用户明确表示**现有 UI 不合格，当前 UI 冻结**。不要设计动画、界面或默认云端问事；优先做数据库、组合检索、专业用神方法与可靠断词。
- GPT 可辅助开发及来源查阅，但正式离线 App 运行依赖经过验证的算法、已核实规则和审核发布的文字。未经审查不输出吉凶预测。
- **公开仓库只保存索引/源代码/测试/审校元数据，不存两书整章原文或私密问事**。原书需要用户自己备份 `local/books/`，或者保留已生成的私有 SQLite。
- 旧 `QimenLLM` 训练项目不动，不自动沿用旧十书抽取、废弃规则或旧模型输出。

## 已处理的《神奇之门》实际章节：10章

| 章节 | 真实来源 | 主要已入库内容 | 专业审核状态 |
| --- | --- | --- | --- |
| 时家奇门的起局方法 | 独立上传的191行文字，原文SHA `177f6ecba2bf4c165524a48adbdab8fdbd535cdb700dca12b5e5f29b1a75afb2` | 第一章12基础+17起盘步骤+2完整九宫文字例+1局部例；程序依已知阴阳遁/局数/时干支进行四盘排布 | 文字示例一致性测试通过，但历法/完整起局和原印刷图未独立验证 |
| 第四章·奇门预测符号的象数理含义 | 与第五章同一上传文件，行1–500；SHA `15ce23c3fff0c9d3a48b595ee3bbf115d0c1e98a64ce1efc88bdb27e67eab22a` | **55符号档+87八卦象意分条**；归档门、星、神、干支、九宫五行及原文特殊公式 | 来源抽取草稿，不等于最终发布规则 |
| 第五章·奇门预测的判断依据 | 同文件行501–1261；SHA `e153de133f4c5b6c325361ff30a572e782becbb245bb471599d678bb6349679d` | **81干干+64门门+72门仪有序组合；13吉格+27凶格一级条目**；39个复合格局AND/OR候选，另附判断例外 | 来源抽取草稿，未具备全部可执行/审核条件 |

**本次合并上传文件**：`神奇之门_第四章与第五章_完整纯文字精校版(1).txt`，1261行、86,324 UTF-8字节，总SHA256 `8b8d7f57fa539785f5613cb6f8fdbdc27090da559d6d2fe5ce0ffd03953c9147`。

**本次新增本地私有来源断言**：411条，其中55符号+87八卦象意分条+81+64+72有序组合+13+27格局标题+12重要推导、分歧与限制。**39是格局候选子变体的额外条件索引，不应与411原文断言重复计算。**

## 已存在且可跨章调用的具体代码/公共数据

- 原第一章排盘：`src/wengua/casting_shenqi.py`。输出状态仍为 `source_text_consistency_only`，不应自动变为 `engine_verified`。
- 两章来源/语义编译：`src/wengua/compile_shenqi_ch45.py` + `scripts/import_shenqi_ch45.py` + SQLite migration `schema/migrations/002_semantic_assertions.sql`。本地独立执行后逐条原文带行号及谓词，重复入库幂等；**完整原文字节只存本地**。
- 两章公共索引：`data/knowledge/shenqi/shijia_symbols_ch04/{chapter_manifest,symbol_index}.json` 和 `data/knowledge/shenqi/shijia_judgments_ch05/{chapter_manifest,concept_index,formation_variants_draft}.json`。
- 组合与知识检索：`src/wengua/semantic_lookup.py` 可以把第一章九宫内的天盘携带干和地盘干映射 `heaven_over_earth:天干:地干`，同时交叉检索八卦、干、门、星、神及来源。门宫生克与九星季节状态按原书专用函数计算，**不直接输出最终吉凶**。
- 39复合格局研究候选：`src/wengua/formation_candidates.py` 使用同一宫内 AND/OR 条件，不跨宫凑证据；输出明确是草稿候选，绝不自动升级为approved。
- 相关完整测试：`tests/test_shenqi_ch45_semantics.py`、`tests/test_formation_candidates.py`、第一章原先两套完整文字盘回归测试。
- 公共设计契约：[docs/SEMANTIC_KNOWLEDGE_MODEL.md](SEMANTIC_KNOWLEDGE_MODEL.md)。

## 严格区分工程完成 vs. 正式专业能力

| 指标 | 当前实际值 |
| --- | --- |
| 《神奇之门》按 WenguaApp 新规范处理章节 | **3章** |
| 《开悟之门》按 WenguaApp 新规范处理章节 | **0章** |
| 第一章来源基础/起盘候选 | 12 + 17（未专业批准） |
| 第四、第五章完整私有来源断言 | 411（全部draft） |
| 可索引的有序组合矩阵 | 81＋64＋72＝217 |
| 吉/凶一级格局 | 13＋27＝40 |
| 可审查复杂格局子条件候选 | 39（额外结构化，不是39新案例） |
| **正式审批通过的断案用神规则/断词** | **0 / 0** |
| **真正完整“提问—排盘—作者分析—反馈”的预测案例** | **0** |
| 100%验证的公历→节气/干支→完整九宫起局 | **尚未完成** |
| 用户确认满意的 UI | **无；现有UI冻结** |
| 1080局完整独立盘/断词 | **未生成/未验收**；1080是18局×60时的索引 |
| 本书另提的9720/8640格局 | 不同的九宫/八宫统计口径，非局态 |

## 关键尚未解决/不得强行推断

1. 节气精确瞬时、择元及置闰/拆补、时区和23点子时日界、公历干支换算；中五宫寄宫及全盘多样本校对。
2. **门加门/门加三奇六仪的上下层绑定**原文仍需更完整的流派说明，当前64/72项保留 `layer_binding=unresolved`，不能当规则全部能立即用于当前盘。
3. 星门季节、墓迫击刑及其他格局冲突需要先后条件，不能单一吉凶标签当最终结论。
4. “三奇得使”作者的独到解释尚属初步意见；“天网四张”原作者只认可癸加癸且网高网低异说冲突；不同流派神盘不能混用（本书采用天盘八神）。
5. 历史起盘样本与完整预测案例不等价，仍然没有完整事件家族，也没有已批准的手机端断词。
6. 目前本地下载的私有SQLite中已保存第一章原文+第四、第五章原文与411语义断言。**第一章原先32项公共结构化资料需通过 `scripts.import_casting_chapter01` 另外加载到此私有库；不能说已经自动含全部第一章32项。** 用户必须真正保存这份私有数据库/原文以便换聊天后逐字校对。

## 第六章新增：奇门遁甲应用概述（2026-10-19）

- 用户上传：`奇门遁甲应用概述.txt`，**240行、31549字节**，SHA256 `50c76ce5354d3378a842d6117f06c239bcdfe2f04786663c2e89f606d98c402e`。
- 已从这一章提取 **20项原书判断方法、68条有条件的用神候选、14种应期方法和10个五不遇时对照**，共**112条不同粒度、来源行号可检索的候选**，全部draft，正式批准0；不是112件断案案例。
- 新增数据 `data/knowledge/shenqi/application_overview_ch06/{chapter_manifest,method_index,historical_cases_index}.json`；新代码 `src/wengua/ch06_knowledge.py`、`src/wengua/compile_shenqi_ch06.py`、`scripts/import_shenqi_ch06.py`，新迁移 `schema/migrations/003_incomplete_historical_case_parts.sql`，回归测试 `tests/test_shenqi_ch06.py`。
- **现累计处理4章**（起局＋第四＋第五＋第六），此前第四第五章411条来源断言、39个吉凶格子变体仍原样保留；新的112条是另外一章的可导入候选，**不能声称 GitHub 公共数据库有原书全文**。未处理《开悟之门》，用户满意UI仍未完成。
- **完整预测历史事件家族仍是0**；本章1995-01-26卫星发射只保留1个不完整的原书历史实例：部分盘面、作者预言、事后反馈不同字段；不可假称完整九宫，也不作为封存独立测试。原书关于实际结果的事实尚未通过独立外部资料验证。
- **取用重点**：依用户/当事人关系动态选用，年干父母、月干兄弟同事、日干起问人、时干子女/所问事；健康等专题还要兼看其他星门神与乾坤等；“帮朋友问”没有直接一对一唯一干支规则，需补充问事人物关系而非虚构。
- **判断重点**：横看不同用神**落宫**之间五行生克，竖看同宫四盘关系；阳遁内1/8/3/4，阴遁内9/2/7/6，中五宫暂unknown；吉凶具相对性，应期要按条件优先次序，不能编明确日期。
- 用户提出“8640总局，1080唯一局，7560完全重复”经原书数学定义核对：**第五章8640为8个外宫×1080局态的宫位条目**，并未证明全年重复8次或7560张完整盘重复。详见 `docs/CH06_LINKED_REASONING_PROTOCOL.md`；完整盘真正去重需将实际九宫输出标准化、哈希后验证。
- 接下来继续收到用户下一章，直接沿用共享 `concept_id` 与私有原文SQLite，逐条抽取、关联、添加单元测试，**并且更新AGENTS/STATUS/LEDGER**。不能改动旧QimenLLM，也不恢复UI开发。

## 下一步/交接要求

等待用户下一章。收到即读取 `AGENTS.md`、本文件、`docs/CHAPTER_LEDGER.md`、`docs/CHAPTER_WORKFLOW.md`、`docs/SEMANTIC_KNOWLEDGE_MODEL.md` 和对应知识目录；只增量更新，不推倒重建。
未来若用户发送具体领域规则/真实案例，映射现有概念ID→各宫证据→问测人与当事人关系→专题用神→作者断案过程→待审断词；原书事后反馈与事前盘面严格分离。

**每处理新章节后：更新原书哈希、章节知识目录、数据库迁移/查询代码、测试、CHAPTER_LEDGER、PROJECT_STATUS及根AGENTS.md，并实际推送GitHub、核验最新CI。禁止只在对话声称已存档。**

## GitHub测试说明

GitHub Actions只证明代码结构回归，不代表专业预测有效；每次最终报告应读取当时**最新commit**的CI状态，不复制旧commit的成功结果。



## 2026-10-19 第四章结构化关系补充（与三章总数同时有效）

除前述411条本地原文断言之外，GitHub提供 **42条天干地支组合关系、10条天干长生墓绝阶段表、8条八门季节旺衰表**的公开原创结构化索引；它们是对第四章已有来源的可执行抽象，**不重复计为411之外的独立来源**。路径 `data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json`；查询 `src/wengua/symbol_relations.py`；测试 `tests/test_symbol_relations.py`。保留地支相刑的有向循环、对称组合的无序匹配、原文未注明阶段的未知状态；任何规则只能用在真实盘面允许的对应关系上。39格局子变体已使用 `formation_concept_id` 回指本章257个组合/格名索引，供跨书引用。**UI依然暂停。**


## 2026-10-19 · 新阶段：从理论转向各领域六个完整案例（最新状态）

**按 WenguaApp 新规范累计已处理《神奇之门》5章**：时家起局、第四章象数理、第五章判断依据、第六章应用概述、以及本次**第一章《人体疾病预测》**（该第一章属于后面的专题预测部分，与“时家奇门的起局方法”不是同一源章）。《开悟之门》0章。原书基础信息与组合体系仍可互查，后续进入逐领域“取用方法＋作者完整案例”知识整理；UI冻结，旧QimenLLM不动。

### 本次原书与真实产物

- 文件 `神奇之门_人体疾病预测_精校完整版(1).txt`：**298行、34,625 UTF-8字节**，SHA256 `3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a`；文件行293–298为整理者非原书附注。
- **6个完整的原书事件家族、6张九宫原字转写盘、共54个宫位、作者29条带原文行号的编号分析步骤**。4次分阶段新信息披露（案例1三次、案例3一次）单独保存，原先已知事实、作者预测、事后反馈严格分离。
- `data/knowledge/shenqi/health_prediction_ch01/{chapter_manifest,method_index,case_index,source_audit}.json`：8套八宫体表/体内映射、14条按场景关系取用神候选、8阶段分析方法；共30条来源参考条目。原书历史报道不是独立科学/临床证实，**全部draft、正式批准0**。
- `src/wengua/compile_shenqi_health_cases.py` 与 `scripts/import_shenqi_health.py`：严格校验SHA和6×9宫原始字面后增量导入私有SQLite，不触碰旧案原文；`schema/migrations/004_health_case_evidence.sql` 保存54九宫、29作者原文步骤、4个逐步披露、6事件协议；`src/wengua/health_research.py` 区分`initial_question`（不含判断/反馈）和`source_study`（学习完整作者步骤）。
- **数据库已经在本轮制作私人下载副本**：`WenguaApp_V1_神奇之门_五章_疾病六例_私有研究库.sqlite3`（约 795KB），包含旧四章及疾病章全部原文；SQLite检查 `integrity_check=ok`、无外键错误，`sections=5`，`cases=6`，`historical_chart_cells=54`，`historical_case_reasoning=29`，`historical_case_disclosures=4`，`semantic_assertions=441`（前411＋疾病章30）。
- **私有库中尚未包含第六章在GitHub公开的112条结构化候选索引**，但第六章原文仍在 `sections`。未来可用仓库现有 `scripts.import_shenqi_ch06` 补入该索引；第一章起局的32条公开结构化素材同样可以按 `scripts.import_casting_chapter01` 另补入。不得称私有库已包含这两部分数据。
- 案例归档细则见 `docs/HEALTH_CASE_REASONING_PROTOCOL.md` 与账本 `docs/CHAPTER_LEDGER.md`。
- 跨章审核：本健康章第四例用`庚申日丙戌时`称“五不遇时”，上章举表是`庚日丙子时`；按时干克日干的定义尚有适用范围待核，具体记`source_audit.json`，不改原书时柱或把书中一个列表未经审查当全集。
- **未来断词**：根据问测人/患者关系确定主用神和辅助用神、真实九宫、病星/医药星、门星神干组合、时令内外与病星生克反证、应期再按原书条件推导，最后给出来源明晰、经过审核的传统解释。**不得自动对真实患者作疾病、癌症、生命年限或治疗有效性的医学诊断/预言，更不能使用户放弃医疗。**
- 所有6个事件暂处于 `unassigned_do_not_train_and_test_same_family`；不得将29步当作29个独立实案、也不得以已经看到后来反馈的故事冒充独立盲测。

### 计数概览（最新）

| 项目 | 数量/状态 |
| --- | --- |
| 神奇之门已处理章 | **5** |
| 开悟之门已处理章 | **0** |
| 跨章来源事实（第四/第五章） | 411 |
| 第六章公开研究候选 | 112（本私有下载库未注册） |
| 本疾病专题公开抽象 | 8身体宫位＋14用神＋8工作流＝30 |
| 完整古籍历史故事家族 | **6**（书中有完整盘与作者论述） |
| 历史作者编号推理步骤 | **29** |
| 医疗/预测专业获批准入 | **0** |
| 独立未见事件预测准确率 | **尚未测试** |
| 真正可由设备公历全自动经验证起盘 | **尚未完成** |
| UI / 27B训练 | 均暂停 |

**1080与8640定义仍旧**：`1080=18×60`个候选局态键、`8640=1080×8`个外宫条目（第五章原书口径），不能把“8宫×局态”直接声称全年每张完整盘重复8次；即使在用户理想化360天/72候/4320时辰下，`4320/1080=4`而不是8。对真实是否重复，只有按明确起盘变体、完整盘面规范化后去重才能给出可靠计数。

**下一步**：用户提供下一个预测领域章节，优先整章方法/取用/有条件断法及每个事件的全盘、作者逐句证据、断语与反馈，按既有 `concept_id`/SQLite/双视图持续入库；每章必更新 `AGENTS.md`、`docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`，核实最新 GitHub main SHA、每个远端文件和对应最新CI。禁止继续UI开发或恢复旧27B。


## 2026-10-19 · 婚姻案例与用户默认书内判对新协议（最新）

**此节为最新实际进度**：WenguaApp 《神奇之门》累计**6章**（时家起局、第四象数理、第五判断依据、第六应用概述、第一专题人体疾病预测、第二专题恋爱婚姻预测）；《开悟之门》0章。**累计12个完整原书九宫事件家族、108个原始宫位、52条作者编号推理**，用户指定的12案**书内判对默认标签**已在新私有SQLite落实。书内成功是项目的作者解法学习标签，不是独立现实科学有效性认证。UI暂停，旧QimenLLM/27B均不碰。

### 本次婚姻章节

- 原文 `神奇之门_恋爱婚姻预测_精校完整版(1).txt`，367行、35777字节，SHA256 `64c7e9c1c0e646814c11644809277f71587d21736bdbd49679e6ad65611303c9`，版权全文仅用户私有。
- **6个整体婚姻问事家族＋6张九宫源文转写盘（54宫）＋23条逐步断案**。第一节乙女、庚男、六合媒人、年命、配偶相合之干、丁第三者女性、丙第三者男性，以及按实际问事灵活调整用神；独立公开方法候选18条／解释流程7步，**全部研究草稿**。
- `data/knowledge/shenqi/marriage_prediction_ch02/` 包括 `chapter_manifest.json`、`case_index.json`、`method_index.json`、`source_audit.json`；完整原文九宫与作者逐句论证仅在用户私有SQLite。
- 新源码 `src/wengua/compile_shenqi_marriage.py`，一次性整案读取 `src/wengua/book_case_retrieval.py`；旧六例书内判对同步 `src/wengua/book_verdict_sync.py`、`scripts/sync_author_book_verdicts.py`，新增 `schema/migrations/005_book_case_verdicts.sql`。测试 `tests/test_marriage_case_import.py`。
- 原书编辑核对问题：婚姻例三、例五文字盘与作者叙述局部干位有差异；例六有1997年无盘回忆和1998-04-22有盘再问，不能混用盘；该上传到第367行例六第4步便止，不可臆造之后作者结尾。
- 详细案例研究规范 `docs/MARRIAGE_CASE_REASONING_PROTOCOL.md`。

### 用户最新绝对优先的历史案例判定规则

完整见 **`docs/CASE_OUTCOME_POLICY.md`**，并已经在**根目录 `AGENTS.md` 和 `docs/CHAPTER_WORKFLOW.md`**强制同步：
1. **一个事情、一个真实时辰、一张实际提供的原盘、一份完整作者解盘**；书中多个问题往返、补充后验信息仅是同一家族验证，不分出另一独立预测任务。
2. **原书作者没有明确断错、改断、纠错、复盘承认失误的，全部默认作者书内判对**（`author_book_success_default`）；只有其原书明确纠错时才标 `author_book_error_explicit`，须附来源位置与复盘。
3. V1离线App交付**一次性完整答案＋推理证据＋最终总结**，不做对话式一步一步补信息后再给第二版答案。
4. 独立验证专列 `independent_external_verification`，不能把“书内断对”说成客观历史、医学、现实预测准确率100%；尊重所有反馈已是同一事件的验证信息。
5. 不主动把旧病案6个降级为断错或待定；已经在本轮`health_prediction_ch01/case_index.json`及用户私有SQLite重分类为六个书内成功。维持原书记录可溯源但不用往返分裂故事。

### 最新私人六章合并库

[用户工作文件名] `WenguaApp_V1_神奇之门_六章_健康婚姻十二例_私有研究库.sqlite3`（`/mnt/data` 生成，需用户自行下载保留）：源自五章旧库**增量复制**，已经保存6章原文+全部12例完整转写九宫、52步分析、22条书内验证/信息披露、12项书内成功标签。当前 SQLite 检验：

`sections=6; chapter_knowledge=6; cases=12; historical_chart_cells=108; historical_case_reasoning=52; historical_case_disclosures=22; historical_case_book_verdicts=12; semantic_assertions=441; integrity_check=ok; foreign_key_check=empty`。

**尚未在该私有库物化的公开方法条目**：新婚姻18条、旧第六章112条、第一起局章32个元数据可按各自GitHub源导入器增量登记；这些条目在 GitHub 公开索引及源码真实存在，不应混称已经在私有库的441条内。

### 接下来的发展

用户会继续提供《神奇之门》下一预测领域章节。必须精读其领域取用与分析流程、**整案逐步来源及所有后补的书内验证**，依本次`marriage_prediction_ch02`完整流程跨章连 `concept_id`、保存原九宫、一次性结果，绝不把一个家族拆N个任务。每章须更新根 `AGENTS.md`、`docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`、公开结构知识/测试/私有库；查看最新main SHA对应GitHub CI均通过并逐项拉远端文件确认。

**2026-10-19 私有六章数据库最终复核（比上述中间导出更新）**：婚姻专题18条公开的方法候选现已**按同一规范写入本轮私有 SQLite**，故该最终下载件的 `semantic_assertions=459`（原有441＋婚姻18）。`sections=6`、`cases=12`、`historical_chart_cells=108`、`historical_case_reasoning=52`、`historical_case_book_verdicts=12`，`integrity_check=ok`、外键无违规。旧第六章112条方法和起局章32个结构化记录仍有独立导入事项，不能说已入最终下载件。文件名继续为 `WenguaApp_V1_神奇之门_六章_健康婚姻十二例_私有研究库.sqlite3`。此前正文对本下载件“只有441/婚姻18未同步”的表述只描述**中间阶段**，以后以本段最新验证状态为准。


## 2026-10-19 最新状态：七章，疾病案例规则已追溯补齐＋怀孕分娩六例

**这是当前最新实数**。按 WenguaApp 新流程《神奇之门》累计**7章**：起局方法、第四章象数理、第五章判断依据、第六章应用概述、人体疾病、恋爱婚姻、怀孕分娩；《开悟之门》0章。**现累计18个独立原书起盘事件、18张来源九宫文字盘、162个宫位记录、75条作者编号分析步骤，18案均按用户要求标记“书内判对默认”**。这不代表18次经外界独立证明正确。

### 对之前《人体疾病预测》的要求已实际落实到数据库，不只是改名

用户强调一个案例只按**一件事一个时辰一张盘一份完整解盘**登记，书中后来确认与补充全部作为此案 `validation_information`，不能因为原作者多轮交谈就拆成多个预测任务。已有疾病6案的原书验证行已完整补充到 `historical_case_disclosures` 中并分类，全部有原文字节支持；原案54个宫位与29条作者步骤仍原封保留，且6个 `author_book_success_default` 不变。公开 `health_prediction_ch01/case_index.json` 增 `validation_information_lines`，新模块 `compile_shenqi_pregnancy.py` 默认的 `retroactively_sync_health_book_validation` 对以后私人数据库重复导入保持此规则。学习作者书内判词不等于医学诊断或独立有效性。

### 怀孕分娩新章

`神奇之门_怀孕分娩预测_精校完整版(1).txt`：313行，28082字节，SHA256 `51af5117a1390f8af44e27c70fde83722d5df98d9c517e303a1dde7d433b5b9e`。六案、每案9宫源文字面共54条、23条作者分析。来源方法 `data/knowledge/shenqi/pregnancy_prediction_ch03/method_index.json` 为**24个带具体行号的研究候选**，存取用孕妇/胎儿的坤宫、天芮、时干、值符六合、门星阴阳，产室生克、时间选择、应期，所有字段只用于古籍研究，不提供临床预测。

需要忠实保留作者疑点：①第一、二例同女儿**不同时间和不同起局**，不可混为一卦；②第二例作者对性别“拿不准”，听到医院预产期后调整日期推法；③第四、第五例学员断法经过张志春修改加工；④第五例指出五不遇时并非必凶；⑤第六例的B超报告在问卦前已知，复查及胎儿分娩后续单列验证资料。任何古籍推断不能用于真实胎儿性别、畸形、是否终止妊娠或手术决定。

**源/代码**：`data/knowledge/shenqi/pregnancy_prediction_ch03/{chapter_manifest,case_index,method_index,source_audit}.json`、`src/wengua/compile_shenqi_pregnancy.py`、`scripts/import_shenqi_pregnancy.py`、`tests/test_pregnancy_case_import.py`、`docs/PREGNANCY_CASE_REASONING_PROTOCOL.md`。复用既有 schema`historical_case_book_verdicts` 等；原书完整文本仍只在私人 SQLite。

**本轮本地实际七章数据库下载**：`WenguaApp_V1_神奇之门_七章_健康婚姻孕产十八例_私有研究库.sqlite3`；SQLite验证 `sections=7, cases=18, historical_chart_cells=162, historical_case_reasoning=75, historical_case_disclosures=38, historical_case_book_verdicts=18, semantic_assertions=483`，`integrity_check=ok`、外键无错误。原六章的全部原文没有被覆盖。第六章以前公开的112条、起局章32条可复用索引仍有独立本地导入项，不应和已物化的483条混淆。

后续依旧只逐章处理专题取用、案例和作者证据；**UI及旧QimenLLM训练不动**；每一章更新 `AGENTS.md`、`PROJECT_STATUS.md`、`CHAPTER_LEDGER.md`，实际 fetch 核对远程提交/全部文件和最新GitHub Actions双Python测试。


## 2026-10-19 最新实际状态：第八章《求学考试预测》五案已入库

**本节为最新准确进度，之前3/4/5/6/7章各小节属于历史过程。** WenguaApp 《神奇之门》累计已处理**8章**：时家起局、象数理、判断依据、应用概述、人体疾病、恋爱婚姻、怀孕分娩、**求学考试预测**；《开悟之门》0章。

**累计23个古籍完整起盘事件家族、23张原始九宫转写盘、207宫位、92组作者或学员编号分析；全部23案按用户要求为作者书内默认判对**，结果并未经独立外部验算或现实准确率验证。UI依旧暂停，旧QimenLLM与27B训练不动。

本次用户上传的 `神奇之门_求学考试预测_精校完整版(1).txt` 真实SHA256 `88d641e3b2ba541e5ea2acce40cd73af28c362befbff7cbc39fb558f3d84eb43`，**30539字节、349行**；本章第一节6–20行明确日干本人、父母代问时干、考生年命；天辅考试院、值符主考、值使副考、丁文章、景试卷、年干录取学校，并讨论旺衰生克和正规/自费录取的区分。历史旧武试和拜师学艺独立标注为专门规则。公开 `education_prediction_ch04/method_index.json` **35条**可调用来源候选及8阶段一次断词流程，全部`source_draft`。

五例共有**45宫原字、17组作者原书编号推理**；第5例是一件执照考试与申诉录取的复合问题，原书先写断语及10月结果，再在284行展示8月23日局，在325–349行分五组解释，应完整保存五组的多段内容而非只抽题目。**其初始问事被明确限制为原书第264行，后来的10月9日结果不能泄漏给首次预测输入。** 第4例1997未考取与1998再考录取属于不同考试年份的原书反馈，不是原作者对1997之断认错。五例全部采用用户`CASE_OUTCOME_POLICY.md`所定一事一盘一次解盘、默认书内判对，后补信息当同案验证。

新增公有文件：`data/knowledge/shenqi/education_prediction_ch04/{chapter_manifest,case_index,method_index,source_audit}.json`；`src/wengua/compile_shenqi_education.py`、`scripts/import_shenqi_education.py`、`tests/test_education_case_import.py`、`tests/test_education_handoff_consistency.py`、`docs/EDUCATION_CASE_REASONING_PROTOCOL.md`。已有第一章起局/第四第五象意格局/第六章用神应期均可按`concept_id`关联。原书不在公开GitHub。

**私有八章SQLite已在本次实际生成**：`WenguaApp_V1_神奇之门_八章_求学考试二十三例_私有研究库.sqlite3`；`sections=8`，`cases=23`，`historical_chart_cells=207`，`historical_case_reasoning=92`，`historical_case_disclosures=53`，`historical_case_book_verdicts=23`，`semantic_assertions=518`，`integrity_check=ok`，外键检查无错误。此库从用户七章库SQLite的`backup()`构建，**旧七章全部原文与18案都在**。老第六章112个公开方法、起局章32个公开条目仍未全部补进私有库，不能误称518已包含这些。

**现实边界**：古籍的大学考试、资格执照、申诉/诉讼判断属于传统历史文本，不是现代招生/证照/法律预测的可靠依据；入学及考试争议请以实际官方信息决定。

未来每章必须真实同步根 `AGENTS.md`、`docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`，严格校验用户原文SHA、完整九宫和作者整案全文，生成新私有库，添加案例/源条件/后验隔离单测，然后查最新GitHub HEAD的CI双Python job全成功并逐项读远端确认成功，不能只认之前旧commit通过。


## 2026-10-19 最新真实进度：九章《工作就业预测》与五例完整原书断案

**本节取代上面7/8章的历史进度**。《神奇之门》累计按新WenguaApp来源流程处理**9章**（起局、象数理、判断依据、应用概述、人体疾病、恋爱婚姻、怀孕分娩、求学考试、工作就业预测）；《开悟之门》0章。累计**28个整体源中事件家族、28张九宫文字原盘、252条原字宫位、112个编号作者/学员断案分析、28个书内默认判对**，未以外部独立验证证明任何现实预测准确率。旧QimenLLM、27B训练及UI冻结。

- 本次原书 `神奇之门_工作就业预测_精校完整版(1).txt`，**228行、25748字节，SHA256 `b78ab538a090cc8f59474b49bac613318e130dd78a563929b097ac6922e7fa05`**；整个正文仅在私人SQLite。预测专题第五章，与前面理论章“第五章判断依据”不是同一源，不覆盖。
- 新公开章节目录 `data/knowledge/shenqi/employment_prediction_ch05/`：`chapter_manifest.json`、`case_index.json`、`method_index.json`、`source_audit.json`。**五个完整案例、45宫原字、20条作者/学员编号分析、53条有来源行号的职业/调动/军职/退休/空间竞争条件方法**及8阶段一次性断词流程。所有规则仍为研究draft，跨章以`concept_id/ref_concept_id`关联，不可依据古籍断言真实求职成败或他人品行。
- 案例一（毕业分配）还利用问者**当时座位东南方**的巽宫作特别取用；案例二母代子问外经部/外交部，**11月25日作者仍拿原11月4日盘判断**，这是同一整案的四条步骤；案例三军官免职及同僚影响，五步；案例四杜新会自测工作调动，**全章只提供1997-04-15首次完整盘，虽说总共预测5次其余4盘没给，绝不伪造**；案例五一个1996-10-27申时局供5个住址方位不同的村支书候选比较，学员**只预测乾6第一、坤2第二**，原书事后报告完整排序；张志春另在226–228行从旺相休囚优先复盘，不能事后移作学员原话。
- 新迁移`schema/migrations/006_employment_ranked_candidates.sql`引入两张仅追加表`historical_event_candidates`、`historical_case_source_segments`；`src/wengua/database.py`已调用。新增编译/导入`src/wengua/compile_shenqi_employment.py`、`scripts/import_shenqi_employment.py`、`tests/test_employment_case_import.py`；研究完整说明`docs/EMPLOYMENT_CASE_REASONING_PROTOCOL.md`。私有源保存原3×3压缩格式，不据已有起盘引擎覆盖。
- **本轮真实生成私人九章SQLite** `WenguaApp_V1_神奇之门_九章_工作就业二十八例_私有研究库.sqlite3`（约1.35 MB）：上一八章SQLite`backup()`后增量追加本章完整原书、五案45宫、20步骤、五名候选和五段源叙述与53条来源断法索引。核实`sections=9; chapter_knowledge=9; cases=28; historical_chart_cells=252; historical_case_reasoning=112; historical_case_disclosures=65; historical_case_book_verdicts=28; semantic_assertions=571; historical_case_source_segments=5; historical_event_candidates=5`；`PRAGMA integrity_check=ok`且无外键错误。原八章23案及全文不丢失。
- 公共知识`method_index.json`包含53条详尽`ref_concept_id/scenario/summary`；此私有下载副本中同53条记录保留真实原句、概念ID及公开文件指针，尚未逐条复制所有详细metadata；另有理论第六章112项和起局章32条源索引仍待私有物化，**不能声称571已含这两批**。
- 用户永久规则继续生效：**一件事、一实际时辰、一张真实原盘、一套完整解盘；后来的补充及书内反馈是同案验证；默认作者书内判对，明确作者承认断错才更正；外部验证状态独立；App一次给全部结果而非逐轮对话**。每章必须更新根`AGENTS.md`、本状态、`docs/CHAPTER_LEDGER.md`，并逐项从远端读取核实文件及同一最新main SHA的双Python CI都成功。


## 最新状态 2026-10-19：十章《经营求财预测》14案、16张真实源盘

**此节为最新当前状态，上面3–9章记录只是历史快照。** 按WenguaApp独立逐章流程，《神奇之门》累计完成**10章**：时家起局、象数理、判断依据、应用概述、人体疾病、恋爱婚姻、怀孕分娩、求学考试、工作就业、经营求财预测；《开悟之门》仍0章。**累计42个事件家族、44张真实原书九宫盘（主盘42张＋同一事件另外两张）、396个来源宫位、171组原书分析、42个书内默认判对标签，私有知识652条**。独立外部真实预测有效性仍未证明。App UI与旧QimenLLM/27B训练不启动。

本次原文 `神奇之门_经营求财预测_精校完整版.txt`，**717行、67599字节、SHA256 `c955d56bc7deb1b5c4a99f5b2594625d3d7f690e60063eed10f55864b514698c`**，有第一节交易、投资、买卖货、房地产、开店、合伙、借款、放贷、讨债共**10个主场景**。第二节14个完整事件，**其中抽奖例十二有3张不同时辰的打印原盘**，分别1997-01-25丙午与丁未、01-26丁巳；1月27–28日原书只有文字解析不得补盘。因此新一章新增**14事件、16盘144宫、59组作者/学员实际说明（56有编号＋贷款例十无编号3种方法）、81个来源条件方法**。原书最后一行717未收尾，保持原样。

**防后验污染**：例7租赁首问和预测在308同一段、例9企业前景420行先给判断、例12初问与未来开奖在550行同一段，研究初始查看只能使用起盘前已知信息。例12学员当时分析与张志春在582/610/639行复盘分开保留；其余第三四日缺完整原盘不许捏造。例13结果实际还款在679行属于同案验证，不是作者第677步。14案按用户规范`author_book_success_default`，不等于真投资收益/贷款/司法/医学/艺术品鉴定有独立准确性。

新增 `data/knowledge/shenqi/business_profit_prediction_ch06/`（manifest/index/audit）、`schema/migrations/007_business_multi_casts.sql`（只增两表）、`src/wengua/compile_shenqi_business.py`、`src/wengua/business_case_retrieval.py`、`scripts/import_shenqi_business.py`、`tests/test_business_case_import.py`、`tests/test_business_handoff_consistency.py`、`docs/BUSINESS_CASE_REASONING_PROTOCOL.md`。新增原书十类用途与既有干星门神/旺相主客统一概念引用；不私自另造通用格局。

**本回合已实际生成私人SQLite新文件**：`WenguaApp_V1_神奇之门_十章_经营求财四十二例_私有研究库.sqlite3`。以前九章28案完整原文均保留，增量备份后检验`sections=10; chapter_knowledge=10; cases=42; historical_chart_cells=378; historical_case_additional_casts=2; historical_case_additional_cast_cells=18; historical_case_reasoning=171; historical_case_book_verdicts=42; historical_case_disclosures=89; semantic_assertions=652; historical_case_source_segments=14`；`PRAGMA integrity_check=ok`且无外键违规。**378个主表宫位＋额外18宫=总396宫、44张实盘**。之前第六章112候选和起局章32结构材料还有单独入私有库事项，不能冒称已包含在652条内。

仍严格按`docs/CASE_OUTCOME_POLICY.md`处理**一个事件家族、实际每次有来源的时辰盘、一个完整分析和同案反馈**；对单次App用户只一次解盘，不进行预测聊天。每章同步根`AGENTS.md`、当前状态与账本，远端确认所有文件实际保存，最新HEAD的两份Python CI真正通过以后才能宣布成功。


## 2026-10-19 最新第十一处理章：《出行出国预测》及#186失败提醒复核

本节为最新交接；前面十章的进度记录是历史快照。上一章Run **39343195782**（commit `c405993`）确实Failure，后续Run **39343304392**（commit `8af463e`）已success（Python3.11/3.12），不是失败未修复；失败的历史邮件不会自动撤回。

最新《神奇之门》累计**11章、48个完整事件家族、51张原书真实打印的九宫、459个原字宫位（主盘432＋附加时局27）、200组作者/学员编号分析、690条有出处的研究候选、48个默认书内判对标签**，《开悟之门》0章。新增原书文件`神奇之门_出行出国预测_精校完整版(2).txt`，**350行31026字节 SHA256 `c273c803eb78a02cfb3c6c00065da81312c1851a679a1e3bca4911acdbc3bc55`**，实际6故事7盘29编号分析38方法。原书首页标题只写“出行出国预测”，仓库`ch07`仅是顺序标识，不能伪造书内第七章原题。UI、旧QimenLLM/27B训练仍不启动。

**本章硬性例外**：例1于1月17咨询，但原作者依据1月20将起飞的计划时刻起局；例4 2月23出国一案10月25再联络母亲时仍使用二月**旧盘**，原作者3条初断+复看5条疾病及家属分析都在同一原事件，不新增十月盘；例6 6月21问时盘和6月24预计下午3点起飞机盘**两张确实打印的不同盘**属于一个出国考察故事，实际因雨拖延到6点属后验反馈，350行事后天气复盘不能提前当作者初断。任何书内叙述不构成航班安全、道路交通或疾病的独立可靠预测。详见`docs/TRAVEL_CASE_REASONING_PROTOCOL.md`。

公有`data/knowledge/shenqi/travel_abroad_prediction_ch07/`四索引、`src/wengua/compile_shenqi_travel.py`、`scripts/import_shenqi_travel.py`与`tests/test_travel_case_import.py`；**完整原书版权TXT与私有SQLite绝不自动上传公开Github**。私有新SQLite`WenguaApp_V1_神奇之门_十一章_出行出国四十八例_私有研究库.sqlite3`由十章库`backup()`无损增量生成，旧十章全部不变，实际计数`sections=11; cases=48; historical_chart_cells=432; historical_case_additional_casts=3; historical_case_additional_cast_cells=27; historical_case_reasoning=200; historical_case_book_verdicts=48; historical_case_disclosures=102; semantic_assertions=690`，integrity_check ok/无外键违规。上一理论第六章112公开规则、起局32结构条目仍有未全部入私有库事项，不宣称已物化。

下一章遵守`docs/CASE_OUTCOME_POLICY.md`：作者若未明确承认断错仍标`author_book_success_default`（不等于外部科学有效），事件后补同案验证，严格保留实际出现的每张不同时间盘，绝不造盘；问用户App仍一问一时一盘一次完整回答。远端逐文件重新读回+GitHub Actions**最新main对应的两Python任务都success**才宣称完成。减少重复推送通知，优先一个原子GitHub提交；禁止拿旧绿灯替代最新。

## 2026-10-19 最新第十二处理章：《行人走失预测》及之前多次CI失败的归档原则

**本段为最新事实；早期3–11章小节属于历史过程。** 用户提供原书`神奇之门_行人走失预测_精校完整版(1).txt` **477行、49372字节、SHA256 `5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574`**。新增**10完整案例家族、11真正来源盘、99九宫、54编号作者步骤、81条来源条件候选**。本章例二在同一孩子失踪事件中同时给出问时和走失时两张盘，另外提及六次占测**没有原盘**；旧规则同一事件不因多次交流另增事件家族。

**强制不能遗漏书里明说断错**：例5第239行明确“此例断错”、后面241自复盘；例9第401行明确“此例断错”、403-413修订推理；例10学员前4组误断归来后第455行未验、第457行找老师复核、老师第459-475行重新判断（包括7组修正证据）。这三例保留`author_book_error_explicit`的初始错误标签，原断错证据与后来的新逻辑均在同一个案例，**初始错误不可当正面断词训练**。其他7例按用户政策书内默认成功；但**不是独立现实预测验证**。全库累计**12章、58案、62张有据原盘、558宫（522主表+36额外宫）、254条来源作者分析、771条知识候选，55默认书内成功+3有明确初断错误**。《开悟之门》依旧0章。

**本章与准确性特别相关**：原书第一节的日干/时干/月干/年干依实际走失时或问时取用、不同人物关系；六合初始去向/杜门躲藏/用神落宫最终地点，阴阳内外盘远近、空亡冲宫、旺相制凶、庚格和马星归期均为*条件化来源规则*，不允许凭一个凶门直接断死亡。实例3的源叙述在复盘前就已有后来结果，盲测的`known_before`必须裁断后验。实例10最后第477行仅称另用出行时盘可见恶兆、**没有印出该盘，不得自动捏造**。个人失踪或刑事指控只能依警方和实际证据，术数文献不可作为现实断定依据。

**真正创建的私有SQLite**：`WenguaApp_V1_神奇之门_十二章_行人走失五十八例_私有研究库.sqlite3`，从用户十一章库`backup()`只增量写本章，先前48案与十一章原文不改。经实际检查`sections=12,cases=58,historical_chart_cells=522,historical_case_additional_casts=4,historical_case_additional_cast_cells=36,historical_case_reasoning=254,historical_case_book_verdicts=58,historical_case_disclosures=113,semantic_assertions=771`，SQLite`integrity_check=ok`且`foreign_key_check=[]`。第六章老112理论知识候选与起局章32结构记录仍有部分待补私有物化，勿说771已完全包含。

公开`data/knowledge/shenqi/missing_person_prediction_ch08/{chapter_manifest,case_index,method_index,source_audit}.json`与`src/wengua/compile_shenqi_missing.py`、`scripts/import_shenqi_missing.py`、`tests/test_missing_case_import.py`、`docs/MISSING_PERSON_CASE_REASONING_PROTOCOL.md`、本交接文档仅含非版权原文的抽象索引及来源行号。**私有原文、未加密原书SQLite不上传公开repo**。上一批CI通知中的失败属历史旧commit；本轮必须一次合并提交、核对远端每个文件、验证当前main HEAD的Python3.11和3.12两个job均success才标成功。旧QimenLLM和App UI保持不动。

## 2026-10-19 重复原书与完整案例教学方法补充

本轮收到 神奇之门_行人走失预测_精校完整版(2).txt，实际检查477行、49372字节、SHA256 5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574，与已处理的 (1).txt 原字节完全相同。没有第13章、没有新修订或新案例，故不重复入库；当前累计仍是《神奇之门》12章、58个完整事件家族、62张真实九宫、558宫、254组作者分析、771条候选，其中55个书内默认成功与3个明确初断错误；《开悟之门》0章。

已将用户再次强调的永久方法写进根AGENTS与CHAPTER_WORKFLOW：各预测领域第一节提供选用神、看宫位、适用条件、结合旧知识、证据冲突、应期和注意事项的解题方法；每一个完整案例应逐步追踪作者如何在原盘事实与前章概念基础上综合解题，保留初断、反证、明确失误、纠正与后续反馈的时序隔离，最终迁移到新盘的有据解释。此轮只更新规范与来源别名去重状态，并未声称重新训练、重新审核旧58案或增设数据库字段。下一步仍等待真正新章。
## 2026-10-19 第十三章《钱物丢失预测》与历史案例强制补齐计划
新章SHA256 `ed3c80f32c213563bf35d9f9790e330ea04e4def404f6e6ca904006a94a9eaf9`，362行34197字节，8完整故事、8张真实书稿文字盘72宫、36原文作者分析（含两条无编号）、18领域通法＋36实例分析候选＝**54草稿来源知识候选**。8案没有已证实的外部预测成效。新故事分别涉及发票、身份证、皮衣、BP机、现金、文件、出行衍生身份证、汽车。例3先凭坐宫猜测，例6现场补充事实且作者第253行明示未断出车内具体位置，例7初问旅行后第293行才披露身份证失踪，第307行张志春后验按语；末尾编辑校字不等于原印盘校验。旧12章不重建。
累计**13章、66事件、70实际源盘、630宫、290作者分析、825来源候选**。新建逐一涵盖旧58案的 `data/knowledge/shenqi/case_reasoning_retroaudit.json`：目前全部标注**待完成完整人审证据链**；迁移008和 backfill_case_reasoning_traces 可在用户先前真正的12章私人SQLite中对原254步骤安全创建源行号／旧概念候选，但这不是完成审查。本对话中没有上次的12章SQLite文件，因此没有假称已将旧58案逐一完成或生成13章无损合并库。可用私有原文补审后逐案解除待完成状态。所有规则与审计已纳入根AGENTS/WORKFLOW，UI与旧QimenLLM冻结。

## 第十三章案例逐步证据链补充（36个来源锚定草稿）
已为钱物丢失8个独立事件36个真实分析步骤逐条补录观察宫位、证据组合、反证或未见反证、跨章词面候选及信息披露层，路径 `data/knowledge/shenqi/lost_money_property_prediction_ch09/author_reasoning_evidence_index.json`。在实际私人SQLite导入时使用 `attach_lost_property_source_drafts` 更新新章36条追踪记录为 `source_grounded_reconstruction_draft_human_review_required`，**全部仍是draft、禁止正向训练、未独立验盘、未获人工专业批准**。此前58个历史案也必须按同一标准补齐；自动词面回填不能等同于最终专业核对。没有原12章私有SQLite就不谎称已处理完历史254步。

## 2026-10-19 最新完成阶段：新《刑事案件预测》＋12章SQLite继承＋完整公开数据库归档

用户本次亲自交付了真实12章 SQLite 基库和《神奇之门·刑事案件预测》261行/37260字节原书，SHA256 `289465c220a0701545b9f093b4b91d041d600a4c9da67bf58e33a10ece0f0ea9`。根据此前相邻《钱物丢失预测》原稿又增量导入8个完整案件，和本轮刑事5案一并构建新的版本，而不是从 GitHub 公开摘要凭空假装以前基库存在。当前确切总数：**14个来源 `sections`、71事件、76真实时局、684原字宫、319原作者分析、891语义候选（含实际12章基库774条）、71案319个source-anchored候选证据、76张盘中宫独立干及寄坤二宫解释**。新刑事专题5案、6盘、29步骤、34通法概念候选。其第四例银行运钞车抢劫初次阳3局应期原作者承认没断准，后来阳2局是已知结果后的另一排盘，必须永久隔离。

新用户明确授权完整 SQLite 在公开 GitHub 作永久版档，**旧文档的“公开仓库不可上传私人SQLite”条款对此项目版本归档已被最高优先级覆盖**。完整归档路径 `archives/sqlite/WenguaApp_神奇之门_14章_71案例_完整研究库.sqlite3`，SHA256 `bcffc72c0801dfd46ea0fffad3b67550a4aa533764a0bf2d46373031912a8dd2`；另有 `.sqlite3.xz` 压缩校验版和 `14chapters_71cases_manifest.json`。库 `integrity_check=ok`，外键违规0，历史主盘与辅助时辰盘均保留，原12章所有原书原文、案例内容及九宫原字段逐行保留；旧走失10号案例原12章库的“默认成功”错误标签已建单独审计记录并修正为明示初判错误（其原文不变）。**四例有明示错误**（走失原3、刑事应期1）。

无损补审：有71个事件的审计行、319作者分析的来源与符号候选层；但作者完整人工验证的精细推理链仍为**0完成**。后续必须用现在已公开归档的私有原书正文进行真正逐案证据链补审（用神依据、逐宫、引用的旧概念、反证、应期、断错及老师修订）。整本书案例结局不得提前放入初断，刑事类象不是现实犯罪定罪依据。UI及旧QimenLLM不动。**此时段早先各章进度统计均为历史快照。**

## 2026-10-19 最新第十五章：《官司诉讼预测》、77完整事件和新版本化SQLite

本轮用户提供《官司诉讼预测》源书SHA256 `a0cf2a05700bfb832420d3318b2982d25f6150e7a5c5e8c5ecc1ae07f5c810d2`（30547字节/267行）；来自正式GitHub14章71案库（SHA256 `bcffc72c0801dfd46ea0fffad3b67550a4aa533764a0bf2d46373031912a8dd2`）执行SQLite backup，只增加**6故事、6原印九宫54格、25源分析、31通法和25案例推理研究候选**。全库**15章/77个事件/82个实际盘/738宫/344条作者分析/947研究候选**；82个中宫都保留独立原干和寄坤2宫来源派生，外围八宫确有神门星而中宫不编造。

**保真/负例**：本章例5学生用乙奇代被告被张志春220、222行明确否定，原书后说欠款追回不意味着错误方法正确。第6例初断在228、后续披露在230/232、结果在236/238、最后原盘与解释在245/263/267，严格分层不能以结果泄漏盲测。旧14章全部原字案例/作者文字和裁判阶段记录逐条保留。新6案 `historical_case_phase_events` 26条、`historical_case_reasoning_corrections` 2条、步骤全文/已见事实候选25条。全部仍draft与初断训练未批准；77案真实专业证据链人工全部完成数量0。历史刑事4号明确应期错误+失踪原3个错误保存，诉讼5号方法纠错不虚增整案结局错数。

本轮完整公开SQLite：`archives/sqlite/WenguaApp_神奇之门_15章_77案例_完整研究库.sqlite3`（44efe2ed11023c763558f3eabd4cc98f55c515482515d89a78a7641cdb1fde4e），压缩同名`.xz`，完整15章原书与历史事件都在其中。`integrity_check=ok`、`foreign_key_check=[]`、旧14章`sections`逐行源原文未变、旧case/盘/步骤行未变。累计自旧14章的GitHub归档版本新增不覆盖，UI旧模型继续冻结。

## 2026-10-20 第16来源章节《体育竞赛预测》增量开发
用户最新原书标题自称**“第十二章”**，按仓库实际累计记**第16个来源章节**；来源276行26814字节SHA `784f49224b8a540850dde469a0fe720d23ee4ab551fa9600dca6137eb4fb5a2b`。7故事7真实印九宫63原字宫，32原作者分析（包括甲戌初断未印盘、三套方法试探和圈号⑥），11领域方法条件，总共43条新的来源知识候选，全都draft。第6例原书明确初断客胜错而主队法国胜，应保存为明示错误及事后修正；其余6例默认书内作者成功而无独立现实验证。旧15章77案真实归档SHA `44efe2ed11023c763558f3eabd4cc98f55c515482515d89a78a7641cdb1fde4e`必须不变；增量目标16章84案89真盘801宫376分析990候选和5个初断明确失误。**当前提交源码与归档工作流，完整新SQLite以GitHub Actions输出的实际归档核验为准**，不得将“已索引”冒充新DB已产生。保留历史84案的专业逐案推理证据链待人审，UI及QimenLLM冻结。

## 2026-10-20 第16章公开完整数据库归档实际验收（完成，覆盖前面“预计/待归档”阶段叙述）
**真正在GitHub main从15章完整SQLite backup()生成及上传的16章84案快照已经存在。** GitHub Actions Archive Run [#1](https://github.com/turnupmason/WenguaApp/actions/runs/39417351916) 已成功提交 `b65c4a73f85eeafee9771ddd0b4ab5d26c1d9d2a`；原始二进制 `archives/sqlite/WenguaApp_神奇之门_16章_84案例_完整研究库.sqlite3` 实际大小3,248,128字节，SHA256 `a3573b3b147c24b2eb149fb43f6c6582d7a10a722c25f6c863571f4d4a29efb9`，Git Blob SHA `014358a97a219b76e26c01980a369736646e68a8`；独立压缩副本 `.sqlite3.xz` 大小302,428字节，SHA256 `da1e1c9346afe9bf33c3867fc883f714fcf5c235e4723dca19ddf9fde69e598d`。完整归档 manifest 在 `archives/sqlite/16chapters_84cases_manifest.json`，保留旧15章快照哈希 `44efe2ed11023c763558f3eabd4cc98f55c515482515d89a78a7641cdb1fde4e` 不变。
**本次真实数据库结果**：sections=16、完整历史事件=84、原书真实排盘=89、来源九宫=801、作者分析=376、研究语义候选=990，中宫干+寄坤二宫推导全89盘独立留存， `PRAGMA integrity_check=ok`、`foreign_key_check=[]`，历史15章原行逐表无损比对通过。新章7案、7有据九宫、32分析、11专题通法候选。因第6例预测克罗地亚胜但实际法国胜，书内**明确初断错误累计5案**（旧4案+本案），事后根据未土月令及天地盘干补断是独立负例复盘。用户要求每章公开生成新SQLite的规范已实际兑现；以后均以这个**已远端证实的完整16章版本**而非上一次15章继续增量。所有作者推理仍未全部经人工专业审查，词面候选不等于完整可信因果规则。GitHub CI对最新交接提交另行检验，不拿自动生成前的#196代替最终通过。

## 2026-10-20 第17章《军事事件预测》源稿与归档工作交接
原稿SHA256 `d8b369785de0110cc20376191332eef31b04e749d8ed764d7a1a155ae6c19c05`，183行22,467字节。2个完整事件，4张实际来源盘（1937事后研究一张+1998海湾危机三张），36来源宫，22条作者编号分析（9+13；第109—111行连续解释归同一步），32个有条件来源通法候选。本章共新增54条 `semantic_assertions` 草稿候选。原书事后回顾的二战案例不作为模型在未知历史上成功预测的证据；第31行有待外部史学核实的日期叙述另列 source caveat。案例二三个真实问时属于单个事件家族；三次新增已知、作者见盘和最终结果严格时间分层。所有源例未在现实战争预测领域获得独立验证，禁止向实际军事活动提供行动结论。
本章 GitHub source、builder、migration、tests、archive workflow 同时提交，**归档流程成功之前不得宣称17章完整数据库已经发布**。基库16章84案例/89盘/801宫/376分析/990语义研究候选；完整新版本目标17章86案例/93盘/837宫/398分析/1044候选，历史5个明确初断错误保持不变。中五寄二宫数据单列，不篡改原格。真正源码和SQLite的 hash、远端提交、最新CI必须以后续远端实测为准。UI和旧QimenLLM仍不触。

## 2026-10-20 第17章完整公开SQLite实际归档、二进制SHA及最终交接

本条为最新**实际 GitHub 远端核验状态**，覆盖前文只谈“待提交/目标”的阶段描述：GitHub Actions《Build and archive next military history chapter SQLite》Run #2 在提交 `0b7d569a6ac6041f30e111e6ab312690e29a7ccd` 已全部成功（Run #1 的脚本 ROOT 多取一层导致找不到 migration，已实际修复且 #2 通过），Action 生成了完整原始未加密数据库，并由机器人正式落在 GitHub `main` 提交 `262fc590966bd14abe8b7306d1a1f967b9337998`。文件：`archives/sqlite/WenguaApp_神奇之门_17章_86案例_完整研究库.sqlite3`，**3,516,416字节**、SHA256 **`d29cfc5cd0779cf0a334b168a48c07f7145d51f0fe1424c5c0954b76e1133867`**、Git Blob SHA **`fd6603a786128bfc840b3d63692f2321543a721f`**。`.sqlite3.xz` 压缩版本大小319,752字节、SHA256 **`bfa383f11c8c1a146d82faa0156df03b32924625a2a2041c7cc4babfe17c1394`**；完整 `archives/sqlite/17chapters_86cases_manifest.json` 与两份数据库同在远端。

从已归档16章源快照SHA256 `a3573b3b147c24b2eb149fb43f6c6582d7a10a722c25f6c863571f4d4a29efb9` **经sqlite3 backup()无损增量生成**17章真实库；实际数据 sections=17、whole events=86、real printed charts=93、palace records=837、author steps=398、semantic candidates=1044，`integrity_check=ok`、外键违规0，全旧16章原行逐表保留。原书军事新章2个事件、4张印盘、22步及32领域条件候选，第一例历史事后对照不得当独立预测，第二例同一危机3真实起盘不得拆3案，原文1937历史时序争议保留原字并独立警示。所有作者因果证据链人工专业完整核验仍为0；研究候选不能误报为真实可靠军事预测，原书明确初断错误累计仍为5。下一章**必须接续本次已验证的17章86案二进制快照**，绝不沿用16章或从索引重建。最新 handoff 的 Python 3.11/3.12 CI 必须另行在实际最新 HEAD 再核，不拿 #199（机器人提交前）冒充最终绿灯。

## 2026-10-20 第18处理章天时气象：源码提交状态与真实版本归档待验
原书完整19,857字节/156行，SHA256 `6093f9a89bd2eb889c392242892528a9022c6d9565f74be8912e2a8724663697`；五个完整事件、5张真正源书九宫45宫、13条作者分析及36条领域条件候选（总49新增研究候选），来源书内5个自述对应结果，但没有独立气象测量验证。本章特别保护例1同一行初断/事后回报、例2另外3个六爻起卦而非奇门盘、例3辰时雨巳时停后10点再下、例4球赛局跨问事重用、例5次日用事起局。新增真实源文、版本化 `18_from_17` builder、迁移013、回归测试、自动压缩归档工作流；**最终18章完整数据库/哈希以机器人实际上传并远端核实为准，不先写死**。目标累计18章91案98原书盘882宫411作者分析1093来源草稿，旧5条明确初断错误不变；已知前次17章基库hash `d29cfc5cd0779cf0a334b168a48c07f7145d51f0fe1424c5c0954b76e1133867`。所有历史86案细粒度证据链专业完整审核仍未完成，不拿机器来源索引当成可训练的已审断案。UI、旧QimenLLM冻结。

## 2026-10-20 第18章《天时气象预测》完整公开SQLite已归档：实测验证与下一章唯一基库

**此处是GitHub二进制归档成功后的实际状态，优先于本文件此前“目标/待验”描述。** 自动归档工作流 [Build and archive eighteenth weather source SQLite #1](https://github.com/turnupmason/WenguaApp/actions/runs/39451797786) 从来源提交 `fed9806811d25ec0eeb453428cc44a879f3468e4` 构建成功，已由 github-actions[bot] 写入 `main` 归档提交 `8dd8b384ac1d51548fc64979ac5f3acb0401462b`。未压缩原始SQLite独立新路径 `archives/sqlite/WenguaApp_神奇之门_18章_91案例_完整研究库.sqlite3`，Git Blob SHA `81ac96832000a598dda6db0ec207a6ef3997e780`，**实际3,692,544字节**，SHA256 **`c20edf3611a71d31a241f45d10f9b4a175212081659ac05908b980fd8854c31c`**。另存原始数据压缩 `.sqlite3.xz`，大小333,528字节，SHA256 **`574b5d502f315c2b74e6da2fd756f53aac14c337f0795795c447e2af5d6de4c0`**；校验清单 `archives/sqlite/18chapters_91cases_manifest.json` 已从GitHub远端读取并核对，与两份实际Git Blob路径一致。

**新库实际**：原始来源章节18、独立事件家族91、真实印出九宫盘98张、原字宫位882、作者分析步骤411、来源候选1,093；新章新增5案/5印盘/45宫/13步/36通法草稿=49新候选。继续保留历史明确初断错误5案。源稿准确SHA256 `6093f9a89bd2eb889c392242892528a9022c6d9565f74be8912e2a8724663697`，19,857字节、156行。此库由上一版 **17章86案的真实二进制快照** SHA256 `d29cfc5cd0779cf0a334b168a48c07f7145d51f0fe1424c5c0954b76e1133867` 用 SQLite backup() 衍生，**旧17章数据逐表源行不变**；远端构建结果 `PRAGMA integrity_check=ok`、`foreign_key_check=[]`；98个中心宫的原字及“寄坤二宫”独立推导保留，没有造中宫门星神。

例1源第42行初断和“结果”严格拆开；例2另有3次非奇门六爻卦，不新增奇门排盘、不用其已知结果污染初问；例3甲辰/乙巳两时条件只归同一来源盘，书内10点续雨隔离为反馈；例4同一球赛时间盘用于天气不同问事，不合并事件；例5按次日用事时辰而非询问时辰起局。所有气象对应成功只是作者文献陈述、尚无独立气象站验证；历史及新章人审的完整可迁移因果证据链仍未全部完成（目前自动抽取只为draft且禁止正向训练），不能据此宣称能可靠预测天气或洪水。下次必须以**本18章91案完整GitHub SQLite**作为唯一新起点，继续无损版本归档。UI/旧QimenLLM仍冻结。完成交接后需要检查最新handoff提交对应的Python3.11/3.12 CI，不能拿归档机器人写入前的#201冒充最终HEAD已测。

## 2026-10-20 第19处理章《地理环境预测》来源索引与待归档闸门
从用户实际提供原书 81行10,912字节 SHA256 `c755e3879432b2f84329e0b9491eabdb48b865fa2f1cad96a0187f1bb7a3f5c1`，保存2完整案例/2原印九宫（18宫）/6条无编号作者断词分析/23条件法源候选，新增加29条待审研究语义候选，来源全部保存在新版本SQLite而不压缩成单规则。第1案已有第三方案专家共识，不能作为作者独立取用预测；只确认计划8亿及资金未到位，2001年开业和14亿完工均未验证。第2案前段癸山丁向旧墓地根本没有印盘，后段吴先生辛山乙向墓地才有一张盘；只断“地很好但不能用、前辈占有”，没有作者详细宫位推理和地权实际证明，因此完整因果链状态仍不通过。不能根据后验为它编推理。新全量SQLite**待GitHub自动归档实际完成**，目标19章93事件、100来源盘、900宫位、417作者分析、1122候选；基库已确证18章91案二进制 SHA256 `c20edf3611a71d31a241f45d10f9b4a175212081659ac05908b980fd8854c31c`，禁止回到17章或索引重建。保留历史明确初断错误5案，全部未验因果链均draft。需检查新库实际上云、原表逐行、哈希/最新main CI后才能写成功。

## 2026-10-20 第19章实测归档完成：地理环境预测
GitHub远端机器人已提交 `4949b15d08036263dad37aa75f3fc3cf46705c68`，不是计划数字。完整版 `archives/sqlite/WenguaApp_神奇之门_19章_93案例_完整研究库.sqlite3` 3,807,232字节，SHA256 `9412c314a10827b34f6d2e1930124b672f389156d86692d58db1ffdff5ada4b0`，Git Blob `cdc7c852c460affaeccd3bbc7e826fb57278106f`；压缩 `.sqlite3.xz` 342,280字节，SHA256 `11f9808f88bbad35fdf153ecc8a549d073256a65067af1da3b816e34f9be15b4`。远端完整manifest `archives/sqlite/19chapters_93cases_manifest.json`；旧18章原始文件SHA256 `c20edf3611a71d31a241f45d10f9b4a175212081659ac05908b980fd8854c31c`，从其 `sqlite3.backup()` 增量、旧所有表源行不变，SQLite integrity=ok、外键违规=0。实际累计**19章/93事件/100盘/900来源宫/417分析/1,122候选**，新增本章2案2实际盘6段无编号断语和23条件来源草稿，旧作者明确初断错误5案不动。
来源上专家先选择第三建设方案，只有预算八亿与资金缺口获原书部分确认，2001开业/最终十四亿元无结果证据；第二案前一块墓地没有盘，后一块才有唯一原盘但没有真正作者宫位推理，缺口绝不能由AI编造。全库专业完整链仍未全人审，0个本章规则批准或科学验真。下一章**必须从19章93案完整二进制SHA `9412c314a10827b34f6d2e1930124b672f389156d86692d58db1ffdff5ada4b0` 继续**；本次归档前 CI#203通过，最终交接后须以最新main CI结果验收。

## 2026-10-20 第20处理章《神奇之门·人生机遇预测》永久交接及缺来源不得补造
此章原书标题为“第十六章”，项目真实累计顺序为**第20处理章**；原始TXT 37,761字节/273行/SHA256 `92de6590ebf88698d9bf0137e8ecdb780b8f1ff1f66765faf0a69eb3d7eac507`。原书确实5个整案、5张来源九宫45宫、作者分析/断词源行51条（第1案11条含未编号78；第2案15条是**同一完整事件中的15个子问题而不是15案**；第3案6编号+190行事后复盘；第4案4编号+221行作者结论限制；第5案13段逐轮断语但**没有逐条作者九宫证据链**）。专题方法从作者第10、11行及韵文13-25行按具体条件整理34条研究候选，51条来源分析索引均有源行、发生阶段、词面候选及反证/缺口，所有条目标注draft/`positive_training_eligible=0`；不要用古书的人格、疾病、死亡、年龄、灾祸断语当现实科学事实。

**三类最重要的反事实/后验防泄漏约束：** 例3赵某在第186、188行事前仅断“正月/七月注意车祸”，第189行结果正月初五发生撞人事故，第190行才事后据内盘、值使等推具体五天，不能把五天断法记成事前准确预测；例4第一段195行**女童死亡结果事先已知**，第217-221行出生盘分析全部属后验案例，不得做独立盲测、不得用术数预测儿童寿命；例5 第257行作者猜测丈夫于1994或1995年病故，第258行当事人明确纠正为1996年，**这一年份初断是书内明确错误**；第259行以后再用1930与1996干支解释是已知结果后的推理，不能倒灌。例5后面还有其他回答及反馈，必须保持同一event_family完整保存，不允许把整体其他正确说法冲掉这一错误。不允将用户“未来计划”当已经实现（例如例2最后新问办厂戌亥月）。

领域原则：**出生时间局**用于传统先天及长期机遇分析，**问时局**用于近期机遇，人物角色与年干父母/领导、月干兄弟/同事、时干子女/下属随问事切换，结合年命及坐宫；八门、九星、八神、格局必须条件化联合推理，原作者也明确说古籍绝对化不可拘泥。第二例15段分析中多人命年与官司、家庭、子女、出国及办厂必须按问答先后阶段隔离，严禁后披露信息偷跑到首轮输入。历史全部93案亦继续按相同作者真实逐步推理标准待逐案人工审查；本新章学员问答中的证据缺失处不能凭后来答案伪造中间论证。

**基库硬门槛：** 必须从已在GitHub归档的19章93事件全量 SQLite二进制 `archives/sqlite/WenguaApp_神奇之门_19章_93案例_完整研究库.sqlite3` 其 SHA256 `9412c314a10827b34f6d2e1930124b672f389156d86692d58db1ffdff5ada4b0` 开始，只能 `sqlite3.backup()` 无损增加，保持全部以前来源行不变，不能重新从索引构造，不能覆盖原19章快照。中宫单干照原书，寄坤二宫独立推导，绝不编门星神。新增 migration015、构建器20_from_19、来源和CI，并由专用Actions提交公开完整版 `20章98案例.sqlite3` 及 `.xz` 压缩版本、SHA256清单。构建前数字**仅为预期**：20章、98完整事件、105实际盘、945宫、468作者分析、1207候选、明确书内错误至少6件含新案#5；**远端归档未完成不能报完成**。所有历史/本章完整人审的作者因果链未完成，禁止自动批准或以命理替代医疗、交通安全、法律、现实职业规划。UI和旧QimenLLM继续冻结。

## 2026-10-20 第20处理章《人生机遇预测》完整SQLite实际远端归档与不可回退基线
GitHub Actions 第20章归档Run #2成功，机器人已在main提交 `e2136133783f3cb047ad969e246998ab499acfa0`。确实归档完整二进制 `archives/sqlite/WenguaApp_神奇之门_20章_98案例_完整研究库.sqlite3`，4,261,888字节，SHA256 `1332fe460c1e73bd74939760c59a376980c888bb8d9e41c3b7416fadd4bbdaa3`，Git Blob `98251e7a060219b6baecaef2e6b336615f2b7e83`；压缩 `.sqlite3.xz` 370,172字节、SHA256 `1f9afae4f3a8063ca76d79d4f006ef9f481036354c043b2b084f1fd0db2d3ce6`。远端清单 `archives/sqlite/20chapters_98cases_manifest.json` 已核对。来源TXT 37,761字节273行SHA256 `92de6590ebf88698d9bf0137e8ecdb780b8f1ff1f66765faf0a69eb3d7eac507`。实测累计**20章、98家族、105张真实九宫、945来源宫、468作者步骤、1,207候选**，本章新增5案、5盘、51个原书分析及断语步骤、34个条件法，明确初断错误案累计6（本章第5例丈夫死亡年份错断1994/1995而反馈1996）。第三例第190行精确应期是事后复盘，第四例回顾女童死亡已有结果不能盲测，第二例15子问题保留同一个完整家族。注意旧数据库 `historical_life_source_error_segments` 原先就有4行，加入本案错误后合计5条，禁止删改任何旧审计。新库由上版19章完整SQLite SHA256 `9412c314a10827b34f6d2e1930124b672f389156d86692d58db1ffdff5ada4b0` 经 sqlite3.backup()无损生成，旧19章所有表原始行逐表不变；`integrity_check=ok`、FK违规0，中五宫原字及寄坤推导仍独立保存。**以后唯一基库就是SHA256 `1332fe460c1e73bd74939760c59a376980c888bb8d9e41c3b7416fadd4bbdaa3` 的20章完整SQLite，必须创建新版本并完整上传GitHub，不重建、不覆盖旧数据库。** 所有古籍医学/死亡/命运说法只是作者陈述，未独立验证；作者证据链尚需逐案人工核对，不应据此正向训练。归档前源码CI#206已通过，最终handoff提交另需最新HEAD的3.11/3.12 CI通过。UI及旧QimenLLM冻结。
