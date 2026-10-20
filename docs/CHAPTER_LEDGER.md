# WenguaApp 章节处理账本（Append-only）

> 每次收到新章并完成处理后，**在表末追加一行**；不得删除已处理章记录，修订原章时增加版本并附原记录引用。总览计数另同步 `docs/PROJECT_STATUS.md`。

## 处理记录

| 日期 | Book ID | 章节标识 | 章节原题 | 原文 SHA256 | 来源状态 | 基础/起盘知识 | 候选规则 | 整体事件案例 | 候选断词 | 测试/审核 | GitHub Commit |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| — | — | — | 尚无已输入新章 | — | 待用户提供 | 0 | 0 | 0 | 0 | 尚未开始 | — |

### 必须记录的状态

- **原文来源状态**：`chat_only` / `local_original_backed_up` / `licensed_public` / `unavailable_for_recheck`，不要声称公开 GitHub 保存了原文。
- **每章的实际产物路径**：在对应行下方追加说明，可列 `data/knowledge/<book>/<chapter>` 的可公开结构化摘要、候选规则、案例索引、测试文件以及原文仅本地的相对路径（不含用户隐私路径）。
- **校对状态**：`extracted_draft` / `source_checked` / `needs_case_or_chart_review` / `approved`；不同类别可分开记录。
- **案例数量**：独立完整事件家族数（同案多题不得重算）。
- **断词数量**：候选与获批数量分开，不能以 GPT 生成数量代表已验收。
- **变更**：重审同章时增加同一 chapter 的新版本行，不编辑旧原文和旧事实结论。


## 2026-10-19 · 第一个正式处理章节

| 日期 | Book ID | 章节标识 | 章节原题 | 原文 SHA256 | 来源状态 | 基础/起盘知识 | 候选规则 | 整体事件案例 | 候选断词 | 测试/审核 | GitHub Commit |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026-10-19 | shenqi | shijia_qiju | 时家奇门的起局方法 | `177f6ecba2bf4c165524a48adbdab8fdbd535cdb700dca12b5e5f29b1a75afb2` | `chat_original; assistant-created_private_SQLite_download` | 12 | 17（全部draft） | **0**（另有2完整起局盘+1局部起局示例） | **0** | 已按整章整理；两例逐宫与用户提供的文字表对照；原印刷图/历法未独立复核；Python 3.11/3.12 CI通过 | `c991093` |

**新增知识库**：`data/knowledge/shenqi/shijia_qiju/{chapter_manifest,foundation,casting_rules,casting_examples}.json`。这四份公开文件不包含原书全文。原文字节已由本次用户附件实读，长26691字节、191行，SHA256如表；私有原文数据库下载件 `WenguaApp_chapter01_source_only.sqlite3` 已在本轮生成，**但还未部署到用户自己的 Mac**，不能因为提供下载就声称已本地永久备份。

**代码实现**：`src/wengua/casting_shenqi.py` 从已知阴/阳局、局数和时干支排地盘、天盘、门盘、神盘，并有24节气三元局表、日干支符头/上中下元、五鼠遁日上起时、六甲旬首、值符值使计算；`tests/test_casting_shenqi_chapter01.py` 对1995-06-11阳遁三局与1995-08-13阴遁八局逐个九宫字段及附加局部例进行文本一致性验证。输出状态是 `source_text_consistency_only`，不是全流程 `engine_verified`。

**数据库**：`schema/migrations/001_chapter_knowledge.sql`、`src/wengua/chapter_ingest.py`、`scripts/import_casting_chapter01.py` 支持将32条结构化资料（12+17+3）入本地 SQLite，并允许用户提供精确 SHA256 匹配的私有原文入库。当前公共规则获批数0，真实预测案例家族0。

**未解决**：公历时间/节气精确瞬时换算与子时日界；书中使用的定局细则与置闰/拆补边界；值使逐宫计数落中五宫的明确处理；原始印刷九宫图复核。图三是邻近正文的恢复表，绝不能声称对印刷原图/第三方历法已经独立验算。

**下一步**：接受用户的下一章原文，按同一目录/来源规范逐章增量；如后续章节提供历法与排盘变体详情，再解除起盘引擎相应阻断。**UI继续暂停。**


## 2026-10-19 · 《神奇之门》第四、第五章（同一上传原文，分别入库）

两章均来自用户本次重新提供的原文文件 `神奇之门_第四章与第五章_完整纯文字精校版(1).txt`（1261行、UTF-8 86324字节）。**合并文件**SHA256：`8b8d7f57fa539785f5613cb6f8fdbdc27090da559d6d2fe5ce0ffd03953c9147`。不把一份附件误计为两个不同来源文件。

| 日期 | Book ID | 章节标识 | 章节原题 | 分章 SHA256 | 来源状态 | 基础/起盘知识 | 组合与候选规则 | 整体事件案例 | 候选断词 | 测试/审核 | GitHub Commit |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026-10-19 | shenqi | shijia_symbols_ch04 | 奇门预测符号的象数理含义 | `15ce23c3fff0c9d3a48b595ee3bbf115d0c1e98a64ce1efc88bdb27e67eab22a` | `chat_source + assistant_private_SQLite_download` | **55符号主档＋87八卦象意分条** | 门宫五行与九星季节公式及作者例外待核 | 0 | 0 | 全章已提取，全部draft，源文需用户私有保留；单元测试与CI | `ba36da9` |
| 2026-10-19 | shenqi | shijia_judgments_ch05 | 奇门预测的判断依据 | `e153de133f4c5b6c325361ff30a572e782becbb245bb471599d678bb6349679d` | `chat_source + assistant_private_SQLite_download` | 结构化书中组合判断依据 | **81十干克应＋64门门＋72门奇仪＋13吉格＋27凶格**（其中有39种复合候选表达式供进一步审查） | 0 | 0 | 全章已提取，完整条件仍未专业批准；程序对前述矩阵完整性及幂等导入测试 | `e92251e` |

**本次来源断言合计411条**：55符号、87八卦细分象意、81＋64＋72有序组合、13＋27吉凶格顶层标题、12条方法、条件/例外。39条子变体为对上述吉凶格的进一步结构化，不是另有39条原书完整案例。**真实历史预测事件家族仍为0**：这两章是知识及判断体系，不含完整“问事—起盘—作者逐步断案—反馈”的独立实案。

**代码/数据目录**：
- `data/knowledge/shenqi/shijia_symbols_ch04/{chapter_manifest,symbol_index}.json`
- `data/knowledge/shenqi/shijia_judgments_ch05/{chapter_manifest,concept_index,formation_variants_draft}.json`
- `schema/migrations/002_semantic_assertions.sql`、`src/wengua/compile_shenqi_ch45.py`、`src/wengua/semantic_lookup.py`、`src/wengua/formation_candidates.py`
- `scripts/import_shenqi_ch45.py`、`tests/test_shenqi_ch45_semantics.py`、`tests/test_formation_candidates.py`
- `docs/SEMANTIC_KNOWLEDGE_MODEL.md`

**配合旧第一章的互调用法**：真实九宫盘内每个已知天盘携带干与地盘干映射 `heaven_over_earth:天干:地干`；八卦、门、星、神映射共享ID查各章出处；门生克宫与九星月令采用专门公式；进一步验证39个“同宫 AND/OR”复合吉凶格候选。不允许把上/下门盘未定的八门×八门64项或门×仪72项直接当已判吉凶，也不能把未专业审核的GPT话术当正式断词。

**原书争议与方法边界**：九星旺相休囚废与地上五行不同；作者只取天盘八神；“三奇得使”冲突解释作者明确待实践；“天网四张”作者坚持只癸加癸并保留网高网低争议；五不遇时需要综合星门格局；本书第五章的 `9720/8640` 为宫位格局计数，既不同于局态目录 `1080`，也未证明最终用户问事种类被穷尽。

**本地原文**：本次合并私有数据库输出为 `WenguaApp_V1_神奇之门_起局_第四章_第五章_私有知识库.sqlite3`，含第一章旧原文以及第四、第五章原文和411条来源关联断言；新会话不能通过公开GitHub直接恢复版权原文。第一章额外32条结构化概念可以通过原仓库 `python3 -m scripts.import_casting_chapter01 --db local/wengua.sqlite3` 填入个人SQLite，不重置原文。用户需要保存私有下载件。

**下一步**：继续用户下一章的完整原书、按相同ID和来源/审核机制加入；跨书同概念可复用ID但要独立保留作者/章节说明。UI仍然暂停。


**第四章/第五章补充归档（2026-10-19，保留以上旧记录）**：在 `data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json` 新建42条天干地支原书组合关系、10条天干生命周期记录、8条八门季节规则，与已有第四章87类象及55主档共享原书出处。 `formation_variants_draft.json` 的39条格局子候选已加入 `formation_concept_id`，能映射第五章257个公开索引；新 `src/wengua/symbol_relations.py`/测试为这种可调用条件提供程序入口。所有项目仍为来源草稿，非审核合格解词。此处不是新增另一份原书或新案例。

## 2026-10-19 · 第六章《奇门遁甲应用概述》（完整新章节，不能重复算前章）

| 日期 | Book ID | 章节标识 | 章节原题 | 原文 SHA256 | 来源状态 | 基础/方法候选 | 用神/应期候选 | 完整历史案例 | 获批断词 | 审核状态 |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-10-19 | shenqi | application_overview_ch06 | 第六章 奇门遁甲应用概述 | `50c76ce5354d3378a842d6117f06c239bcdfe2f04786663c2e89f606d98c402e` | 用户新上传TXT；完整原文仅私有 | 20组解释方法 + 10项五不遇时 | **68条条件用神候选 + 14种应期方法** | **0**（另登记1个不完整历史实例） | **0** | 提取draft，未获专业审批 |

- 原始文件：`奇门遁甲应用概述.txt`，**240行、31549字节**，上述真实SHA256；五节跨度：4–132、134–152、154–184、186–204、206–240。
- **累计《神奇之门》处理章节现在是4章**：第一章时家起局、第四章象数理、第五章判断依据、第六章应用概述；《开悟之门》仍0章。
- 公共数据：`data/knowledge/shenqi/application_overview_ch06/{chapter_manifest,method_index,historical_cases_index}.json`；其中 **112** 是20+68+14+10个源中不同粒度的候选，不是112个已审核吉凶规则。
- 代码：`src/wengua/ch06_knowledge.py`（主客、横看竖看、内外近远、用神取用、五不遇时、应期条件）；`src/wengua/compile_shenqi_ch06.py`＋`scripts/import_shenqi_ch06.py`（核对原书哈希、追加原文与112条来源断言到现有私有库）；`schema/migrations/003_incomplete_historical_case_parts.sql`（隔离历史个案事前已知、作者断语、事后反馈）；`tests/test_shenqi_ch06.py`（验证来源/关系分支/完整度/幂等）。详情 `docs/CH06_LINKED_REASONING_PROTOCOL.md`。
- **1995年1月26日卫星发射事件**：文中包括已知时间与局部盘面、作者判断及后来报道，但**缺完整九宫排盘**，结果并未在此独立外部核实，故只登记1个**不完整**事件，禁止作为独立正式测试样本，事后反馈另存不泄漏。
- **主客原书结构**：文中说“大致四条原则”却实际列了五项——按动静、先后、主动性、天地盘、远近，保存五项而不漏第五项。
- **1080/8640的关键核对**：1080＝18×60个基本局态索引；第五章8640＝8个外宫×1080个局态的宫位条目，不能把8640当成8640张盘或推导7560张完整重复盘。真实重复要按实际起盘输出做hash去重。
- **技术/验收边界**：阶段仍draft，公历完整起盘和中五宫问题未解决；最终回答需经过问事人关系→所取用神→同宫/跨宫证据→时令及主客→应期条件再审核。UI继续冻结。
- 后续章节继续严格更新 `AGENTS.md`、`docs/PROJECT_STATUS.md`、本账本、增量源码/测试，并核对对应最新GitHub SHA及CI。


## 2026-10-19 · 第一份专题完整实战章：《神奇之门》人体疾病预测

| 日期 | Book ID | 章节ID | 原书章节 | SHA256 | 原文字节/行 | 源中完整九宫案例 | 作者编号推理 | 用神/方法抽象 | 后续反馈 | 专业审批 |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| 2026-10-19 | shenqi | health_prediction_ch01 | 第一章 人体疾病预测 | `3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a` | 34,625 / 298 | **6事件家族、54原字宫位** | **29步** | 8体表/体内映射＋14条件用神＋8判断流程 | 六例书内反馈，含4次中途披露分离 | draft，approved=0 |

### 本章新增文档与程序

- 原文由用户本轮提供 `神奇之门_人体疾病预测_精校完整版(1).txt`。原书正文行1–290；**293–298是整理者附注，不是作者自述**；源校九宫按原字保留，不能用模型盘覆盖。
- 公开资料：`data/knowledge/shenqi/health_prediction_ch01/{chapter_manifest,method_index,case_index,source_audit}.json`；完整29步作者原文以及姓名/谈话/反馈在**私有**SQLite，不上传版权全文。
- 工程：`schema/migrations/004_health_case_evidence.sql`、`src/wengua/compile_shenqi_health_cases.py`、`scripts/import_shenqi_health.py`、`src/wengua/health_research.py`；具体用法与安全限制在 `docs/HEALTH_CASE_REASONING_PROTOCOL.md`。
- 自动测试：`tests/test_health_case_import.py` 使用合成而非版权原文的六案九宫数据，验证6事件、54宫、29步骤、30方法条目、4次披露隔离、旧库保留、幂等与错误SHA拒绝。
- 从此前四章私有下载数据库制作新的五章**私有 SQLite**，实际验证：`sections=5`，`chapter_knowledge=5`，`cases=6`，`historical_chart_cells=54`，`historical_case_reasoning=29`，`historical_case_disclosures=4`，`semantic_assertions=441`（之前411＋本章30），`PRAGMA integrity_check=ok`、`foreign_key_check`空。**此前第六章112条公共方法索引尚未在此私有下载版完成导入**；它们在公开GitHub可检索，若要进入私有SQLite按 `scripts.import_shenqi_ch06` 另做。已保存的源文本不等于已全部导入每项抽象数据。
- **案例1和3中间新披露**绝不泄漏到最初问题；案例2/4/5/6的作者报告后续也不构成独立真实有效性证据；6个家族整体保留，29步不得拆分成29个独立训练样本。
- 跨章核对：第四例庚申日丙戌时被原作者标为“五不遇时”，第六章列举表为庚日丙子时，时干一样、时支不同。记录 `source_audit.json` 待澄清范围，不擅自修书。
- **累计《神奇之门》按新项目处理5章**（时家起局、第四/第五/第六章理论及本疾病预测章）；已收6个完整原书预测事件家族，**0个独立已验证现实预测、0条获批专业断词**。《开悟之门》仍0章，UI继续冻结。
- 用户明确后续《神奇之门》主要进入各专题的“取用规则＋实际案例”阶段。每次先理解关系与作者分析顺序，再把方法和原始案例存为一整家族，并同步根 `AGENTS.md`、`docs/PROJECT_STATUS.md`、本账本及最新CI，拒绝任意省略字段或恢复旧模型训练路线。


## 2026-10-19 · 第二份专题案例章：恋爱婚姻预测

| 日期 | Book | chapter_key | 原文字节/行 | SHA256 | 独立事件家族 | 原始九宫宫位 | 作者编号步骤 | 取用方法索引 | 案例原书标签 |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-10-19 | 神奇之门 | `marriage_prediction_ch02` | **35777字节 / 367行** | `64c7e9c1c0e646814c11644809277f71587d21736bdbd49679e6ad65611303c9` | **6** | **54** | **23** | **18候选、7步解释流程** | **6个author_book_success_default** |

这章有【母问子恋爱】【母问女婚姻】【男青年离婚财产】【已婚女离婚及第三者】【第三者问婚】【妻子问丈夫外遇】六个完整事件家族。**本章结束于原书第367行实例六第4条分析末尾，没有后来更远的文字或结局可读，不许补造。** 原书例三第175行、例五第284行编辑标记个别天干位置与盘面原字相互矛盾；保留原文与冲突，而不是认定作者明确断错。例六1997年无九宫的电话问事与1998-04-22有九宫的再次问事属于同一个持续婚姻问题的不同来源时间层；可据以排盘的仅1998年盘，不能把1998盘倒填到1997年。

**用户最新强制政策已启用并追溯旧病案六例**：[CASE_OUTCOME_POLICY.md](CASE_OUTCOME_POLICY.md) 规定“一个事情、一个时辰、一张盘、一个完整解盘，用户V1一次提供答案；作者未亲自明确改断/认错则默认书内判对；后来补充事实与回访都是该整案的书内验证信息”。因此目前疾病6例+本章婚姻6例，**共12例全部 `author_book_success_default`**。这不等于12例经独立外部验证，`independent_external_verification=not_verified` 分列保存。与旧“中途补充拆任务/未验证即失败”口径冲突之处，统一以新强制政策为准；研究原始来源语序依旧保留，绝不允许把后验结果当成新独立案例。

新数据/代码：
- `data/knowledge/shenqi/marriage_prediction_ch02/{chapter_manifest,case_index,method_index,source_audit}.json`；
- `src/wengua/compile_shenqi_marriage.py`、`scripts/import_shenqi_marriage.py`、`src/wengua/book_case_retrieval.py`；
- `schema/migrations/005_book_case_verdicts.sql`、`src/wengua/book_verdict_sync.py`、`scripts/sync_author_book_verdicts.py`；
- `tests/test_marriage_case_import.py`、`docs/MARRIAGE_CASE_REASONING_PROTOCOL.md`、`docs/CASE_OUTCOME_POLICY.md`。

新私有 SQLite 下载：`WenguaApp_V1_神奇之门_六章_健康婚姻十二例_私有研究库.sqlite3`，由前五章数据库复制、追加完整原文及婚姻六案后验核 `sections=6, chapter_knowledge=6, cases=12, historical_chart_cells=108, historical_case_reasoning=52, historical_case_disclosures=22, historical_case_book_verdicts=12`，`integrity_check=ok`、外键检查无问题。当前下载副本仍为 `semantic_assertions=441`，婚姻18条方法候选在**公开GitHub**，通过完整婚姻章节导入器可补录；旧第六章112条公开方法候选此前亦尚未写入此私有文件。不可把已公开的源码索引等同于私有库已导入的数据。

**累计**《神奇之门》按新WenguaApp流程处理6章（起局、第四、第五、第六、人体疾病预测、恋爱婚姻预测），两专题合计12事件、108个九宫原字单元、52条作者编号分析；《开悟之门》0章。后续各预测领域仍严格同一标准，root `AGENTS.md`＋`PROJECT_STATUS.md`＋本账本每章同步，并核对最新远程CI，UI继续暂停。

**2026-10-19 私有六章数据库最终复核（比上述中间导出更新）**：婚姻专题18条公开的方法候选现已**按同一规范写入本轮私有 SQLite**，故该最终下载件的 `semantic_assertions=459`（原有441＋婚姻18）。`sections=6`、`cases=12`、`historical_chart_cells=108`、`historical_case_reasoning=52`、`historical_case_book_verdicts=12`，`integrity_check=ok`、外键无违规。旧第六章112条方法和起局章32个结构化记录仍有独立导入事项，不能说已入最终下载件。文件名继续为 `WenguaApp_V1_神奇之门_六章_健康婚姻十二例_私有研究库.sqlite3`。此前正文对本下载件“只有441/婚姻18未同步”的表述只描述**中间阶段**，以后以本段最新验证状态为准。


## 2026-10-19 · 第三预测专题：《神奇之门》怀孕分娩预测＋旧病案补漏

| 日期 | 书 | 新章 | 原书 SHA256 | 字节/行 | 独立起盘案例 | 九宫原字单元 | 作者编号分析 | 专题条件候选 | 作者原书成败标签 |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-10-19 | 神奇之门 | pregnancy_prediction_ch03 | `51af5117a1390f8af44e27c70fde83722d5df98d9c517e303a1dde7d433b5b9e` | 28082 / 313 | 6 | 54 | 23 | 24 | 6个author_book_success_default |

**案例编排**：1.女儿何时怀孕（1996-01-13阳3）；2.同一女儿分娩预产期（1996-11-08阴6）；3.叶姓孕妇临产（1996-09-24阴7）；4.电话代问早产（1997-03-25阳3）；5.王立忠妻生育（1997-02-07阳8）；6.丈夫因产检B超疑虑问胎儿与分娩（1998-03-24阳9）。前两例为同一个家庭不同时间、不同问题、不同盘，关联但不合并盘。全章元数据、作者23步行号、54条原字盘、结果来源分别登记 `data/knowledge/shenqi/pregnancy_prediction_ch03/{chapter_manifest,case_index,method_index,source_audit}.json`。

**用户要求的旧病案必须补漏，已真正更新七章私有下载件**：六个原`shenqi.health.`案全部保留书内成功标签与一个事件/盘/解读，之前在中途出现的人物年龄/后续反馈按真实原文字段补入或重分类为**同一案的`validation_information`**，而非仅修改公共索引文字。原有29条作者分析与54个宫位没有删除、分割、重置。公开 `health_prediction_ch01/case_index.json` 同步增加各案 `validation_information_lines`；同一增量处理逻辑永久保留在 `src/wengua/compile_shenqi_pregnancy.py:retroactively_sync_health_book_validation`。六个疾病例默认 `author_book_success_default`；独立医学确认依旧 `not_verified`。详见 `docs/CASE_OUTCOME_POLICY.md`。

**原书例外**：第2例作者“拿不准胎儿性别”，且在已经知道医院11月21日预产期后重选应期；第4、5例学员的原断法经过张志春修改加工；第5例特别警告五不遇时并不必然不利；第6例B超异常疑虑在起盘之前已知，复查与分娩是后来反馈。**不因这些叙述把整案改成书内失败；也不伪装每项子预测独立正确。** 第307–313行精校附注不是作者正文。

**本次下载七章私有SQLite真实检查**：`WenguaApp_V1_神奇之门_七章_健康婚姻孕产十八例_私有研究库.sqlite3`，从六章旧版本 SQLite `backup()` 后增量新增整章和六案，`sections=7`、`chapter_knowledge=7`、`cases=18`、`historical_chart_cells=162`、`historical_case_reasoning=75`、`historical_case_book_verdicts=18`、`historical_case_disclosures=38`、`semantic_assertions=483`（原459＋新孕产24），`PRAGMA integrity_check=ok`、`foreign_key_check=[]`。新生儿健康/诊疗仅做古籍研究，禁止在现实用于产前诊断、胎儿性别认定、是否终止妊娠或分娩治疗。

**累计 WenguaApp**：《神奇之门》7章（起局、第四、第五、第六、人体疾病、恋爱婚姻、怀孕分娩）；《开悟之门》0章。完整原书历史案例家族18，原文盘18、宫162、作者编号步骤75；18案书内默认成功，专业验收和独立预言有效性仍未建立。公开 GitHub 只储存可追溯抽象，不提交原书。七章私有库中之前第六章112方法候选、起局章32结构项仍有单独导入事项，切勿称已全部加载。每章必须同步 `AGENTS.md`、本账本及`PROJECT_STATUS.md`，检查最新HEAD CI。


## 2026-10-19 · 《神奇之门》第四预测专题《求学考试预测》

| 日期 | 章ID | 原书来源 SHA256 | 原文字节 / 行数 | 完整原书起盘事件 | 原字九宫 | 编号作者分析 | 研究方法索引 | 整案书内标签 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-10-19 | `education_prediction_ch04` | `88d641e3b2ba541e5ea2acce40cd73af28c362befbff7cbc39fb558f3d84eb43` | 30539 / 349 | **5** | **45宫** | **17组**（最后一例5组多段解释） | **35条** | **5例默认书内判对** |

五案分别：1996-07-12父问儿子高考分数及志愿；1996-04-22母问儿子高考录取；1996-07-04父问儿子成绩及自费入学；1996-11-03本人问1997年考北大心理学博士（书称1997未中，1998再考录取不能拿来否认前一年的整案判断）；1997-08-23父代女儿问美国行医执照考试成绩受质疑的申诉/诉讼与最后通知（**原书先讲10月结果，再贴8月原盘和完整复盘，初始问事仅第264行，不能让书内结果提前泄漏**）。

**案例5的5段分析不是5个新问题或5张盘**，也不是单行大标题：完整原文行号 `325–329, 331–335, 337–339, 341–343, 345–349` 各段均整体保留。该案第268行是起初作者断语，后续第270–280行是同案反馈与第276行作者后来重申；初始已知第264行不含未来结局。其他案例后补考生年命、估分、结果均是原案`validation_information`。

**书内五例全部标为 `author_book_success_default`**，来源认为断对不等于外部真实准确性经独立核查。每案一时一盘、一份完整解盘、App V1一次显示；第五例跨考试/申诉/诉讼/证据，但仍属于一个考试录取事件家族。三类历史领域规则还有“旧武试/拜师学艺”，只记录为对应主题方法，不误用为高考的一般固定算法。

公开新增：`data/knowledge/shenqi/education_prediction_ch04/{chapter_manifest,case_index,method_index,source_audit}.json`；`src/wengua/compile_shenqi_education.py`、`scripts/import_shenqi_education.py`、`tests/test_education_case_import.py`、`tests/test_education_handoff_consistency.py`、`docs/EDUCATION_CASE_REASONING_PROTOCOL.md`。原书全文和个人信息仅存私有 SQLite，源转写九宫未独立排盘验校。

**当前私有八章库已在当前回合用上一七章库备份增量构建并检查**：`WenguaApp_V1_神奇之门_八章_求学考试二十三例_私有研究库.sqlite3`，`sections=8`、`chapter_knowledge=8`、`cases=23`、`historical_chart_cells=207`、`historical_case_reasoning=92`、`historical_case_disclosures=53`、`historical_case_book_verdicts=23`、`semantic_assertions=518`，SQLite `integrity_check=ok`、`foreign_key_check=[]`。先前七章和18个完整案例保留。**5例原文均入库、最后一例known_before按第264行修正，不含10月录取结果**。

**现总进度**：《神奇之门》8章，3个专题疾病/婚姻/孕产加本次求学考试4个专题，**23个历史整案/207宫位/92组原文分析/23默认书内判对**；《开悟之门》0章。此前理论应用第六章112条公开方法及起局章32条结构草稿还未全部物化在本导出 SQLite，不能报称已完成。GitHub root `AGENTS.md`、`PROJECT_STATUS.md`、本账本均要随章同步，要求最新HEAD两项CI成功且真正从远端读到更新文件。


## 2026-10-19 · 第五预测专题《神奇之门·工作就业预测》

| 源章 | 文件大小/行 | 原文 SHA256 | 独立整案 | 完整九宫 | 编号分析 | 候选研究方法 | 源书结果标签 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `employment_prediction_ch05` | **25748字节/228行** | `b78ab538a090cc8f59474b49bac613318e130dd78a563929b097ac6922e7fa05` | **5** | **5盘/45宫** | **20组** | **53条** | **5个默认书内判对** |

原书五个事件：毕业分配（1996-02-09阳2）、母代子选部委工作（1996-11-04阴2，11月25日重新询问但用的仍是11月4日原盘，**不是两个事件或第二张盘**）、军官免职（1996-01-02阳2）、杜新会自测调任联通（1997-04-15阳1，书中自述共预测5次，但**仅第一次的完整盘存在**；后4盘不得伪造）、五名村党支部书记候选同盘比较（1996-10-27阴5，**一个卦、五个候选人、五组分析，而非五件事情**）。

竞争排名唯一已预测前两名为**乾6尚耀坤第一、坤2尚明吉第二**；第五例事后原书报告震3张相如第三、巽4尚文才第四、坎1尚用成第五。独立`historical_event_candidates`把**事前预测名次仅两条**与书内事后报告完整五名排序分开；张志春第226–228行的点评独立作为`historical_case_source_segments`保存，主张先比月令旺相休囚、日时克泄，再考虑其它繁琐格局，不能回填成学员最初分析。案例一实际签约时间甲午日己巳时也保留，与事前辰巳日候选不同但整案依用户政策仍默认书内判对。全部结论尚无独立外部验证。

新增公开目录`data/knowledge/shenqi/employment_prediction_ch05/`中`chapter_manifest.json`、`case_index.json`、`method_index.json`、`source_audit.json`，代码`schema/migrations/006_employment_ranked_candidates.sql`、`src/wengua/compile_shenqi_employment.py`、`scripts/import_shenqi_employment.py`、`tests/test_employment_case_import.py`，规范`docs/EMPLOYMENT_CASE_REASONING_PROTOCOL.md`。原书原文只保留用户私有 SQLite，不能提交公开库。

本轮已从上一八章私有文件 `backup()` 无损创建新私有 `WenguaApp_V1_神奇之门_九章_工作就业二十八例_私有研究库.sqlite3`。**数据库实际核验**：`sections=9`、`chapter_knowledge=9`、`cases=28`、`historical_chart_cells=252`、`historical_case_reasoning=112`、`historical_case_disclosures=65`、`historical_case_book_verdicts=28`、`semantic_assertions=571`、`historical_case_source_segments=5`、`historical_event_candidates=5`，`integrity_check=ok`、`foreign_key_check=[]`；前8章和23个整案没有修改或删除。新53候选在私有库按原文、ID和公共方法索引链接保留，详细`ref_concept_id/scenario/summary`在公开`method_index.json`可查；第六章旧112条方法及起局32条元数据尚未全部入此私有版。

**累计按新规则《神奇之门》9章、28个整案、252宫、112作者编号分析，默认书内判对28，外部独立验证0，《开悟之门》0章**。严格 `docs/CASE_OUTCOME_POLICY.md` 一事一盘一次解读、后补同案验证。每次同步根`AGENTS.md`、`docs/PROJECT_STATUS.md`、本账本，远端取回关键文件并验证当前HEAD对应两套Python CI都成功。职业人格、革职、竞选等只是古籍研究，不当作独立事实判断。


## 2026-10-19 · 第六预测专题《神奇之门·经营求财预测》完整十四案

| 章节 | 来源SHA256 | 字节/行 | 整体问事家族 | 真实原盘 | 宫位 | 作者/学员分析组 | 来源取用方法 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `business_profit_prediction_ch06` | `c955d56bc7deb1b5c4a99f5b2594625d3d7f690e60063eed10f55864b514698c` | **67599字节/717行** | **14** | **16** | **144** | **59**（56编号＋贷款3条无编号） | **81** |

十个基线方法类别：交易、投资、买货、卖货、房地产、开店、合伙、借钱、放贷、讨债。十四事件依原书：①租赁酒店②引资商城③商城开业④投资买商位⑤合资办厂⑥直销传销保健品⑦出租商场⑧齐白石画卷购售⑨化肥厂经营策略⑩申请银行贷款⑪煤矿中介⑫慈善抽奖汽车⑬上门讨债获还⑭寻找欠债人无获。案例十虽无“（1）”序号，但第一、二、三种贷款预测方法必须算3组。第十二例**同一连续四日抽奖故事仅一个event_family，实际出现3张不同时辰完整文字盘**（555、585、614行），其余第三四日只有641、643行判断而无完整盘，不得补造。老师582/610/639行不同解释独立来源段归同案。

全部14案例按用户约定`author_book_success_default`书内判对，后补事实/奖品领取/追债结果统一同案验证；无外部准确率证明。例7第308行和例9第420行早期作者判断与起问混写、例12第550行已含未来开奖结果必须保证`known_before`防泄漏。原书最后717行句子未结束，保留原文，不能虚构收尾。

公开新增`data/knowledge/shenqi/business_profit_prediction_ch06/{chapter_manifest,case_index,method_index,source_audit}.json`、`schema/migrations/007_business_multi_casts.sql`、`src/wengua/compile_shenqi_business.py`、`src/wengua/business_case_retrieval.py`、`scripts/import_shenqi_business.py`、`tests/test_business_case_import.py`及交接测试、`docs/BUSINESS_CASE_REASONING_PROTOCOL.md`；私有原文仍仅本地保留。**私有库十章** `WenguaApp_V1_神奇之门_十章_经营求财四十二例_私有研究库.sqlite3` 从九章备份增量创建，库实际记录`sections=10, cases=42, historical_chart_cells=378, historical_case_additional_casts=2, historical_case_additional_cast_cells=18, historical_case_reasoning=171, historical_case_disclosures=89, historical_case_book_verdicts=42, semantic_assertions=652`，完整性与外键检查通过；此前九章28案例不删除。**累计10章、42个原书事件、44张有来源的真实盘、396宫、171组作者分析、652条知识候选**。以前理论第六章112条和起局32条结构素材仍有未完全物化部分。

必须同步根`AGENTS.md`、`PROJECT_STATUS.md`和本账本；测试最新main SHA的Python3.11/3.12均通过，不拿旧CI替代本次工作。


## 2026-10-19 最新第十一处理章：《出行出国预测》及#186失败提醒复核

本节为最新交接；前面十章的进度记录是历史快照。上一章Run **39343195782**（commit `c405993`）确实Failure，后续Run **39343304392**（commit `8af463e`）已success（Python3.11/3.12），不是失败未修复；失败的历史邮件不会自动撤回。

最新《神奇之门》累计**11章、48个完整事件家族、51张原书真实打印的九宫、459个原字宫位（主盘432＋附加时局27）、200组作者/学员编号分析、690条有出处的研究候选、48个默认书内判对标签**，《开悟之门》0章。新增原书文件`神奇之门_出行出国预测_精校完整版(2).txt`，**350行31026字节 SHA256 `c273c803eb78a02cfb3c6c00065da81312c1851a679a1e3bca4911acdbc3bc55`**，实际6故事7盘29编号分析38方法。原书首页标题只写“出行出国预测”，仓库`ch07`仅是顺序标识，不能伪造书内第七章原题。UI、旧QimenLLM/27B训练仍不启动。

**本章硬性例外**：例1于1月17咨询，但原作者依据1月20将起飞的计划时刻起局；例4 2月23出国一案10月25再联络母亲时仍使用二月**旧盘**，原作者3条初断+复看5条疾病及家属分析都在同一原事件，不新增十月盘；例6 6月21问时盘和6月24预计下午3点起飞机盘**两张确实打印的不同盘**属于一个出国考察故事，实际因雨拖延到6点属后验反馈，350行事后天气复盘不能提前当作者初断。任何书内叙述不构成航班安全、道路交通或疾病的独立可靠预测。详见`docs/TRAVEL_CASE_REASONING_PROTOCOL.md`。

公有`data/knowledge/shenqi/travel_abroad_prediction_ch07/`四索引、`src/wengua/compile_shenqi_travel.py`、`scripts/import_shenqi_travel.py`与`tests/test_travel_case_import.py`；**完整原书版权TXT与私有SQLite绝不自动上传公开Github**。私有新SQLite`WenguaApp_V1_神奇之门_十一章_出行出国四十八例_私有研究库.sqlite3`由十章库`backup()`无损增量生成，旧十章全部不变，实际计数`sections=11; cases=48; historical_chart_cells=432; historical_case_additional_casts=3; historical_case_additional_cast_cells=27; historical_case_reasoning=200; historical_case_book_verdicts=48; historical_case_disclosures=102; semantic_assertions=690`，integrity_check ok/无外键违规。上一理论第六章112公开规则、起局32结构条目仍有未全部入私有库事项，不宣称已物化。

下一章遵守`docs/CASE_OUTCOME_POLICY.md`：作者若未明确承认断错仍标`author_book_success_default`（不等于外部科学有效），事件后补同案验证，严格保留实际出现的每张不同时间盘，绝不造盘；问用户App仍一问一时一盘一次完整回答。远端逐文件重新读回+GitHub Actions**最新main对应的两Python任务都success**才宣称完成。减少重复推送通知，优先一个原子GitHub提交；禁止拿旧绿灯替代最新。
本章来源：原书350行、6整案、7盘、29组分析、38条方法；其中例6一事两盘，例4半年后旧盘复断。

## 2026-10-19 最新第十二处理章：《行人走失预测》及之前多次CI失败的归档原则

**本段为最新事实；早期3–11章小节属于历史过程。** 用户提供原书`神奇之门_行人走失预测_精校完整版(1).txt` **477行、49372字节、SHA256 `5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574`**。新增**10完整案例家族、11真正来源盘、99九宫、54编号作者步骤、81条来源条件候选**。本章例二在同一孩子失踪事件中同时给出问时和走失时两张盘，另外提及六次占测**没有原盘**；旧规则同一事件不因多次交流另增事件家族。

**强制不能遗漏书里明说断错**：例5第239行明确“此例断错”、后面241自复盘；例9第401行明确“此例断错”、403-413修订推理；例10学员前4组误断归来后第455行未验、第457行找老师复核、老师第459-475行重新判断（包括7组修正证据）。这三例保留`author_book_error_explicit`的初始错误标签，原断错证据与后来的新逻辑均在同一个案例，**初始错误不可当正面断词训练**。其他7例按用户政策书内默认成功；但**不是独立现实预测验证**。全库累计**12章、58案、62张有据原盘、558宫（522主表+36额外宫）、254条来源作者分析、771条知识候选，55默认书内成功+3有明确初断错误**。《开悟之门》依旧0章。

**本章与准确性特别相关**：原书第一节的日干/时干/月干/年干依实际走失时或问时取用、不同人物关系；六合初始去向/杜门躲藏/用神落宫最终地点，阴阳内外盘远近、空亡冲宫、旺相制凶、庚格和马星归期均为*条件化来源规则*，不允许凭一个凶门直接断死亡。实例3的源叙述在复盘前就已有后来结果，盲测的`known_before`必须裁断后验。实例10最后第477行仅称另用出行时盘可见恶兆、**没有印出该盘，不得自动捏造**。个人失踪或刑事指控只能依警方和实际证据，术数文献不可作为现实断定依据。

**真正创建的私有SQLite**：`WenguaApp_V1_神奇之门_十二章_行人走失五十八例_私有研究库.sqlite3`，从用户十一章库`backup()`只增量写本章，先前48案与十一章原文不改。经实际检查`sections=12,cases=58,historical_chart_cells=522,historical_case_additional_casts=4,historical_case_additional_cast_cells=36,historical_case_reasoning=254,historical_case_book_verdicts=58,historical_case_disclosures=113,semantic_assertions=771`，SQLite`integrity_check=ok`且`foreign_key_check=[]`。第六章老112理论知识候选与起局章32结构记录仍有部分待补私有物化，勿说771已完全包含。

公开`data/knowledge/shenqi/missing_person_prediction_ch08/{chapter_manifest,case_index,method_index,source_audit}.json`与`src/wengua/compile_shenqi_missing.py`、`scripts/import_shenqi_missing.py`、`tests/test_missing_case_import.py`、`docs/MISSING_PERSON_CASE_REASONING_PROTOCOL.md`、本交接文档仅含非版权原文的抽象索引及来源行号。**私有原文、未加密原书SQLite不上传公开repo**。上一批CI通知中的失败属历史旧commit；本轮必须一次合并提交、核对远端每个文件、验证当前main HEAD的Python3.11和3.12两个job均success才标成功。旧QimenLLM和App UI保持不动。

## 2026-10-19 同一来源别名去重（非新章、非原章修订）

新上传的 神奇之门_行人走失预测_精校完整版(2).txt 已读取为477行、49372字节、SHA256 5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574，与既有 missing_person_prediction_ch08/v1 原书的 SHA 完全一致。仅作为同源附件文件名别名记录，严格不增加章节行数、完整事件、九宫盘、分析步骤、候选或 SQLite 原书版本。当前实际进度12章、58案、62盘、558宫、254分析、771候选不变。

本次同时在根AGENTS和逐章流程正式强化：每章先学领域取用判断的完整方法，再把每个历史案例当整盘学习作者如何调用之前知识、组合盘事实与正反证据并得出判断或纠错的真实示范；验证今后新盘方法迁移的能力而非背原书反馈。不能把这一更新冒充额外知识或新历史实案入库。
## 2026-10-19 · 第十三个实际处理章：《钱物丢失预测》
| 章节 | SHA256 | 字节/行 | 完整事件 | 原书实盘/宫位 | 作者分析 | 通法候选 | 案例候选 | 公开状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lost_money_property_prediction_ch09` | `ed3c80f32c213563bf35d9f9790e330ea04e4def404f6e6ca904006a94a9eaf9` | 34197/362 | 8 | 8 / 72 | 36（34编号、例3无编号2条） | 18 | 36 | 全draft、外部验证0 |
特殊追溯：第3例初问实际失物至115行才披露；第6例有问事中披露和253行原作者明确遗漏具体车位；第7例先问妻子出行，293才转身份证，307作者按语属后验；第356–362行是整理者校字，不能将“乙休庚”视为原印书独立验对。公开仅原书哈希/源行号/方法摘要，原书正文留私有。全历史58案各在 `case_reasoning_retroaudit.json` 追踪缺失的人审证据链，后续从用户现有私有SQLite安全补录；**本轮无旧私有库，不能谎称改造已完成**。总进度13章、66家族、70盘、630宫、290作者分析、825研究候选。
