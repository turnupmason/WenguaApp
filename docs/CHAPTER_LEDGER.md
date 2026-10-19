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
