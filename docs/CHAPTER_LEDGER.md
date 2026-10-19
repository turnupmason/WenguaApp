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
