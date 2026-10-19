# WenguaApp V1 — 跨章可调用的符号、组合与证据知识图（2026-10-19）

## 设计目标
把《神奇之门》重新提供的三部分资料接成**同一张图**：

- 第一章 `shijia_qiju`：时家转盘的**地盘、天盘、门盘、神盘事实**，起盘程序 `src/wengua/casting_shenqi.py`。
- 第四章 `shijia_symbols_ch04`：乾坤震巽坎离艮兑八卦、十天干、十二地支、八门、九星、八神的**象数理、五行和条件化性质**。
- 第五章 `shijia_judgments_ch05`：有序的三套组合矩阵、吉凶格名称、条件组合、作者解释、不同说法、例外。

**核心关系不是一本书=一个答案表，而是多个书/章共同指向同一个稳定 `concept_id`。** 新增《开悟之门》或 V2 古籍时，若确实在谈同一概念就使用相同 `concept_id`，同时保留它独立的来源条目与原本观点；不将多书解释直接合并为一个确定“吉凶结论”。

## 当前已核实的来源边界
用户上传整份 UTF-8 文件共 1261 行、86,324 字节，SHA256：
`8b8d7f57fa539785f5613cb6f8fdbdc27090da559d6d2fe5ce0ffd03953c9147`。

- 第四章：行1–500，章节 SHA256 `15ce23c3fff0c9d3a48b595ee3bbf115d0c1e98a64ce1efc88bdb27e67eab22a`。
- 第五章：行501–1261，章节 SHA256 `e153de133f4c5b6c325361ff30a572e782becbb245bb471599d678bb6349679d`。
- **公开 GitHub 只保存原创抽象索引、编译代码、测试和审校状态。完整原书只在下载的私有SQLite/用户设备中。**

## 统一概念 ID 的格式
- `trigram:乾`、`stem:乙`、`branch:亥`、`door:生`、`star:天任星`、`deity:六合`。
- `heaven_over_earth:癸:丁` 表示天盘癸加地盘丁，**不可反过来**。
- `door_over_door:开:休` 是开加休，**不是休加开**，其上下门盘层仍待原书进一步定义。
- `door_over_stem:休:癸` 是休门加癸；休门加壬和加癸共用同一原文字句，但数据库是**两个 concept_id，同一 source_line**。
- `formation:good_formation:01`、`formation:bad_formation:26` 为吉格、凶格一级标题；`formation_variants_draft.json` 是部分小类严格按 AND/OR 保存的**候选**条件。

稳定 ID 仅表示“概念是否相同”，并不表示来自不同书的术数说法天然一致。记录还要保留 `chapter_key`、行号、文本哈希、原书局法、`review_status` 和条件。

## 第一轮完整结构化计数

| 分类 | 数据条数 | 说明 |
| --- | ---: | --- |
| 符号主档 | 55 | 八卦8＋天干10＋地支12＋八门8＋九星9＋八神8 |
| 八卦象意分条 | 87 | 按来源原文行/语义方向索引；文字仅私人本地 |
| 十干克应 | 81 | 九个有效天盘奇仪×九个地盘奇仪，甲按六仪隐藏 |
| 八门加八门 | 64 | 顺序敏感，不能交换 |
| 八门加三奇六仪 | 72 | 八门×九仪；休门加壬、癸同源双索引 |
| 吉格一级标题 | 13 | 其中九遁、三诈五假等含多个独立子变体 |
| 凶格一级标题 | 27 | 包含伏吟、反吟、六仪击刑、三奇入墓、时干入墓、门迫 |
| 条件/流派观点及例外 | 12 | 8条审查限定＋天干关系＋地支关系＋出行歌诀例外＋天芮星用神候选 |
| **原文来源索引合计** | **411** | 全部 `draft`，不得当已审核断词 |

另外公开 `formation_variants_draft.json` 提供 **39 条复合条件候选**，是从上述吉凶格的一级条目展开的交叉索引，不在 411 条基础来源记录之外再算成 39 条新的原书条目。

## 源码与查询路径

- `schema/migrations/002_semantic_assertions.sql` 增加 `semantic_assertions` 表；由 `src/wengua/database.py` 迁移旧 SQLite，**不能重置第一章**。
- `scripts/import_shenqi_ch45.py` 从用户本地原书 TXT、严格哈希后导入两个原书章节，以及全部411条有行号、类别、谓词、草稿状态的本地来源断言；再次运行幂等，不会重复写入。
- `data/knowledge/shenqi/shijia_symbols_ch04/symbol_index.json` 提供可公开的55个符号 ID、五行、原始宫位/来源行。
- `data/knowledge/shenqi/shijia_judgments_ch05/concept_index.json` 提供257项有序组合/吉凶格基础索引和行号。
- `src/wengua/semantic_lookup.py` 接收第一章真实起盘结果的九宫事实：对每一宫的**实际**天盘携带干与地盘干形成对应 `heaven_over_earth`，同时查询八卦、天干、门、星、神的本地来源；不会跨宫混配。
- `src/wengua/formation_candidates.py` 用 AND、OR 在同一宫验证39个可审查的复合条件候选，绝不能把它们直接升级为正式解读或真实预测。
- 每条查到的来源仍保留原 `concept_id + chapter_key + source_lines`，供以后写断词时核查，而不是让 GPT 靠印象瞎编。

## 关键例子（只演示机械查找）
第一章1995年6月11日阳遁三局的文字盘，离九宫为天盘癸、地盘丁；由程序映射出 `heaven_over_earth:癸:丁`。本章第五章能找到相应克应与“螣蛇夭矫”格名；若休门落离九宫，`door_palace_relation('休门',9)` 分类为“迫”（门克宫）。**必须保留三者属于不同证据，及其他全宫、用神、季节和反证；不能单凭该组合发布吉凶断词。**

## 必须严格保留的原书差异与作者限定

1. 八门性质不是简单“开休生必吉、死惊伤必凶”；八门的实际落宫、季节和门宫生克是必要限定。门克宫=迫，宫克门=制，门生宫=和，宫生门=义；同类为比和。
2. 九星的**旺相休囚废**和地上五行的**旺相休囚死**是不同系统。作者要求“我生之月旺、同我为相、月生我为废、我克月休、月克我囚”；不能偷换。
3. 作者本章明确采用**天盘八神**，不让另一流派的地盘八神默认掺入。
4. “三奇得使”作者认为冲突时配合值使门可用，**但自己注明还需实践验证**；这不是已证实的自动覆盖条件。
5. “天网四张”作者明确取**癸加癸**。网高/网低两种说法相反，原书也未认定统一答案。
6. 五不遇时按原书十个日干/时干支的精确组合理解，作者末句强调还需综合星门格局；不能直接判现实必凶。
7. 本书第五章提到“9×18×60=9720种”或“五宫寄二宫后8×18×60=8640种”，它们是宫位格局计数；原项目1080是“18局×60时辰”的**局态索引数**，不能互相替代。
8. **门加门及门加三奇六仪的具体层绑定仍需专业核实**：只有一种门盘的信息时，不能虚构第二层门来匹配64项；部分术数用语未明示究竟采用哪个三奇六仪层时，也必须保留 `layer_binding=unresolved`。避免为了得到任何结果而强行匹配。
9. 这两个章节主要是基础象意和传统格局规则，**并非真实历史完整问事案例**；因此完整事件预测家族数仍是0。

## 在 Mac 的正确本地操作

```bash
git clone https://github.com/turnupmason/WenguaApp.git
cd WenguaApp
mkdir -p local/books
# 把用户保存的精校原书放在 local/books/，不提交到公开Git
python3 -m scripts.import_shenqi_ch45 \
  --db local/wengua.sqlite3 \
  --source-file 'local/books/神奇之门_第四章与第五章_完整纯文字精校版(1).txt'
python3 -m scripts.import_casting_chapter01 --db local/wengua.sqlite3
python3 -m unittest discover -s tests -v
```

**如果已经下载含前三个章的私有 SQLite，不要覆盖它；只需放在 `local/wengua.sqlite3` 并运行第一章32项结构化入库命令。** 完整原文仍由用户自行保管；公开 GitHub 无法提供版权原文的字节级恢复。

## 专业准入
现在 `semantic_assertions.review_status` 全为 `draft`。符号和组合识别可作研究参考；正式断词必须以后根据问事类型和问测人关系识别用神，再对完整、可靠的九宫/星门神/旺衰/格局进行证据推导及人工审查。**Python CI通过不等于古籍断案通过，更不等于现实预测准确率。** 


## 2026-10-19 增量：第四章刑冲害合及旺衰结构查询

另增 `data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json` 与 `src/wengua/symbol_relations.py`：提供 **42条组合关系**（天干合5/冲4，地支冲6/害6/六合6/三会4/三合4/刑3/自刑4）、**10条天干长生/帝旺/死/墓/绝表**，以及**8门的季节旺相休囚死表**。这些是对第四章原文的进一步结构化索引，**不能当作411条之外新发现了42件断案**。

查询示例：`related('stem_combine',['己','甲'])` 仍关联甲己合；`related('branch_punishment',['巳','申','寅'])` 保留作者相刑的方向循环，而随意倒序不满足；`stem_stage('乙','墓')` 给戌；`door_season('死门','四季月')` 在原书未明确状态时返回 `unspecified_in_original`。九星特殊旺相休囚废仍应通过 `semantic_lookup.nine_star_month_status` 读取，不与八门状态共用算法。新增 `tests/test_symbol_relations.py` 保护这些条件。

以后逐章归一化的新五行、生克、刑冲、用神专题依然先检索并复用已有语义ID，但每一本书的文字及作者意见另留来源，不得静默合并冲突。
