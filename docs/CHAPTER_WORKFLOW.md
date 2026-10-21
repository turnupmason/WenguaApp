# 每章完整处理流程 — WenguaApp V1

本文件是 root `AGENTS.md` 第4节的可操作清单。**输入顺序由用户决定**，从基础知识、起盘章节到专业预测案例均可以接收。

## 开始前
- [ ] 从 GitHub 读取 `AGENTS.md`、`docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`、`schema/schema.sql`、`src/wengua/database.py` 及相关已处理章节文件。
- [ ] 检查当前章在账本中是否已有相同 SHA256；完全重复则引用旧版本，不制造重复规则。
- [ ] 确认 `book_id=shenqi` 或 `book_id=kaiwu`、章节名、原文范围/完整性、排盘图是否可辨认。用户没有提供排盘元素时，记为**缺失**而非重新画一个假盘。
- [ ] 将聊天附件当作本次原始数据。如果因原书较长导致有截断，必须注明只处理可见部分，不能宣称整章完整。

## A. 原书保真、分区与索引
保留作者章节层级、条目、诗诀、定义、排盘、全部例子、注释、断句与反馈。原文不直接公开上传；作者句子的引用记录为 `book_id/section_key/section_version/sha256` 与字节或字符范围。没有真实原文字节时不编 SHA256。

每章都应区分：
- F 基础定义/九宫/门星神/天干/五行/格局/类象；
- P 历法定局/置闰拆补/节气/旬首/值符值使/排盘步骤；
- U 各专题的用神、问测人物关系、条件取用；
- J 断案推理、盘面条件、证据组合、冲突、吉凶、应期；
- C 作者一个完整问事事件（包括一个或多盘、原话推断及事后反馈）；必须保留上下文；
- N 例外、疑点、作者假设、勘误、未定义。
分类可多选；不准见一句“生门”就将其当作独立规则，更不能断章取义。

## B. 将知识转成可运行候选（没有充分证据就保持 draft）
每项候选有：稳定ID、书章版本、具体原书位置、分类、主题、适用关系及条件、取用方法、盘面事实选择器、作者的推断步骤、反证/边界、引用索引、置信理由、人工核对状态。关于“吉凶/疾病/财/官司”，要分传统方法解释与现实有效性。

**规则不能只写一段中文**：需要一个机器可评价的前提表达式 `conditions_json` 或等效的条件 AST，明确默认 unknown、冲突、不能适用和证据不足时的处理。尽量复用已有`rules`表，不直接改变/覆盖它的主键版本。

所有 AI 生成的规则和模板默认 `draft`。已找到原书位置但未做独立核验时为 `reviewed`候选也需要人工实际审核；**不能自动晋升到 `approved`**。

> **2026-10-19 最新用户强制修订：**下述章节须服从 [CASE_OUTCOME_POLICY.md](CASE_OUTCOME_POLICY.md)。**一件事一时辰一盘一完整解盘；作者未明确承认断错则默认书内断对；后续补充/反馈全部作为同一整案验证，不拆训练任务。App只交付一次完整断词，不开展多轮追问。**书内断对≠独立客观证实。

## C. 完整案例怎么处理
- 用一件独立问事的 `event_family_id` 为核心，不拆成伪独立成功案例。
- 保留【当时已知】与【盘式/输入】、【作者选用神与分步证据】、【作者断语】、【后来反馈】四个部分，不能把最后一块传入事前预测模拟。
- 严格按书对照原盘的每个宫位/符使/天干/神星门，不以文字大模型自由复现的盘作为真实数据。
- **默认一律记录 `book_outcome_label=author_book_success_default`，只有作者本人明确说明断错、复盘改断才记 `author_book_error_explicit`；后来补充的信息同样是该整案的书内验证。**独立现实验证另设字段，不得因无外部证据就否认作者书内成功标签。
- 如果没有完整盘、时刻或过程，则保存不完整案例的状态，阻止其作为完整独立验收样本。

## D. 从专业规则生成“断词”
**最终离线用户只收到一次完整解盘**，不得模拟作者多轮对话逐轮重写。研究用断词模板包含：
1. 问的是谁、哪件事、适用哪种流派/方法；
2. 选择的用神与条件理由；
3. 盘面原始事实（具体宫位、门、星、神、干）；
4. 有利证据 + 不利证据 + 冲突如何处理；
5. 传统预测/倾向性判断和必要限制；
6. 根据本章作者条件才能谈应期，未知则明确不能定；
7. 对照古籍作者步骤与引用；
8. 最后一句易懂、醒目的总结。

该文字先为候选、可版本化；审查通过并且可发布后才能进入 App 的运行数据。不能因为已经生成 1080 个状态，就自动生成 1080×15 个无条件断语。

## E. 测试与回归
- 数据库导入：相同 SHA 不重复；修订原文产生新版本而非覆盖。
- 有起盘章节：定义算法输入/输出与边界；原书每张真实盘作为 fixture，九宫事实逐格比对；用户未提供数据时报告缺口。
- 用神与领域：符合条件触发、条件不成立不触发、人物关系变化触发正确、同盘其他专题不滥用。
- 解读：每句引用真实、盘事实正确、禁止凭事后反馈编造预测、证据冲突安全阻断。
- `python3 -m unittest discover -s tests -v`；GitHub Actions 最新 commit 的结果须在用户报告中明确。
- 未有真正独立案例时不能称“盲测通过”，程序测试通过也不等于专业预测验收。

## F. GitHub 提交及会话交接（必做）
1. 保存原书在本地 Git-ignored `local/`，如果无法在用户 Mac 写入就清楚标记，并引导用户本地备份；只有可以公开的抽象规则、示例、元数据和少量合法引用进入 Public GitHub。
2. 结构化项目结果尽量采用一致目录 `data/knowledge/shenqi/<chapter_key>/` 或 `data/knowledge/kaiwu/<chapter_key>/`（确实有本章结果时再创建，勿生成空壳目录），包含 `chapter_manifest.json`、`foundation.json`、`casting.json`、`rule_candidates.json`、`case_index.json`、`reading_candidates.json` 中本章实际有数据的文件；其他缺项写在 manifest，而不是编造占位知识。
3. 文件的稳定ID与 schema 字段必须与实际现存代码兼容；如果目前还不能正式放进 SQLite `rules` 表，就明确标注知识候选状态、具体迁移任务。
4. 对照原文人工核对以后，写入必要代码/测试；确保可重复构建。
5. **同步根 `AGENTS.md` 的最新进度及本书内成功规则**，并追加 `docs/CHAPTER_LEDGER.md`（章、hash、类别计数、审查情况、commit及文件位置），更新 `docs/PROJECT_STATUS.md`（总进度、未决、本次结果、下一章）。
6. 推送 `turnupmason/WenguaApp` 并读取远端实际 commit；检查 GitHub CI 结果，不能复制以前旧仓库的成功记录。
7. 在当前用户对话报告真实成果与未完成项。**若用户已经给了下一章，不用再确认本条规则，直接进入下一章。**

## 新对话工作入口
只要当前用户发来的下一章可见，按以上流程立即处理；无需请求旧对话的记忆。但 GitHub 公开的抽象成果无法恢复未存的全文，逐字复核时仍需要对应的书稿原文附件或可访问的本地来源。


## 2026-10-19 新增：原书倒叙预测与结果的硬性防泄漏规则

求学考试第五例展示原书**先讲预测和后来结果，再补写完整九宫和全部解释**的特殊组织方式。因此今后案例即便文字顺序是“结果→盘面→复盘”，也必须区分：`initial_known_facts`、`original_cast`、`author_reasoning`、`author_judgment`、`same_event_validation_information`。这只是**同一整案的资料层次**，不是要App进行多轮对话。任何初始模拟只允许事件当时已经知道的资料以及实际原盘，绝不能从原文整段截取未来反馈当首断问题。作者书内没有明确断错一律仍按`author_book_success_default`记录，研究真实性独立标注。见 `docs/EDUCATION_CASE_REASONING_PROTOCOL.md` 第五例。


## 2026-10-19 补充：同一盘多人排名与书中未提供其他盘的强制流程

`employment_prediction_ch05` 原文SHA `b78ab538a090cc8f59474b49bac613318e130dd78a563929b097ac6922e7fa05`。一张盘中出现5名候选人时，保留**一个**`event_family_id`和一张完整原始九宫；用`historical_event_candidates`分别记五名候选人与所占宫、事前明确预测名次、后来反馈名次。**不得凭反馈后三四五名推定事前曾预测完整1至5名次。** 源书作者书内没有明确承认断错时依用户标准仍默认整体`author_book_success_default`，并不等于现实外部准确性证明。

如果作者说“一共算过五次”而只提供第一次起盘，**只录入第一张原文盘**，其他四次标`not_provided`，不可自动以不完整时间补起、不可断言四盘一样，也不能将四次当作额外完整历史实案。若同一事件后续问事明确翻出旧盘，就**只复用同一原盘**而不是第二次起盘。工作就业章案例二的11月25日与11月4日属于同一盘复看。除作者的编号分析，还须单独保存书中结果后编辑评注/老师复盘（如第五例张志春226–228行），不混到学生最初断案。



## 2026-10-19 永久追加：14事件可有16真实原盘，历史一案多时辰不等于App多轮聊天

经营求财原书 `c955d56bc7deb1b5c4a99f5b2594625d3d7f690e60063eed10f55864b514698c` 的慈善抽奖例12是完整连续抽奖活动一个事件家族，**但作者真实印有1997-01-25丙午、丁未和01-26丁巳三个不同时间盘**。必须逐盘保留真实源行号及完整九宫（第一盘在主表、后两盘在`historical_case_additional_cast_cells`），并与一个原书故事、七条学员推理及三条作者复盘关联；01-27/28仅文字判断，不推造不存在的源盘。最终用户问一个当前时辰则仍只有**当次起局一张盘和一次完整断词**，不模拟GPT多轮对话。

经营章节实例十未使用“（1）”编号，却按“第一种方法、第二种方法、第三种方法”写了三条完整推论，也必须录入`historical_case_reasoning`，不因无圆括号漏掉。案例七、九、十二的问事初始原文混入当时作者断语或之后结果；生成初断用的`known_before`必须从原文中裁剪掉断语与后来结果，同时保持完整版权源、分析和验证分栏。来源作者没明确承认某次断案错误，均按用户指定的`author_book_success_default`保存，独立外部真实性另列。具体见`docs/BUSINESS_CASE_REASONING_PROTOCOL.md`。


## 2026-10-19 最新第十一处理章：《出行出国预测》及#186失败提醒复核

本节为最新交接；前面十章的进度记录是历史快照。上一章Run **39343195782**（commit `c405993`）确实Failure，后续Run **39343304392**（commit `8af463e`）已success（Python3.11/3.12），不是失败未修复；失败的历史邮件不会自动撤回。

最新《神奇之门》累计**11章、48个完整事件家族、51张原书真实打印的九宫、459个原字宫位（主盘432＋附加时局27）、200组作者/学员编号分析、690条有出处的研究候选、48个默认书内判对标签**，《开悟之门》0章。新增原书文件`神奇之门_出行出国预测_精校完整版(2).txt`，**350行31026字节 SHA256 `c273c803eb78a02cfb3c6c00065da81312c1851a679a1e3bca4911acdbc3bc55`**，实际6故事7盘29编号分析38方法。原书首页标题只写“出行出国预测”，仓库`ch07`仅是顺序标识，不能伪造书内第七章原题。UI、旧QimenLLM/27B训练仍不启动。

**本章硬性例外**：例1于1月17咨询，但原作者依据1月20将起飞的计划时刻起局；例4 2月23出国一案10月25再联络母亲时仍使用二月**旧盘**，原作者3条初断+复看5条疾病及家属分析都在同一原事件，不新增十月盘；例6 6月21问时盘和6月24预计下午3点起飞机盘**两张确实打印的不同盘**属于一个出国考察故事，实际因雨拖延到6点属后验反馈，350行事后天气复盘不能提前当作者初断。任何书内叙述不构成航班安全、道路交通或疾病的独立可靠预测。详见`docs/TRAVEL_CASE_REASONING_PROTOCOL.md`。

公有`data/knowledge/shenqi/travel_abroad_prediction_ch07/`四索引、`src/wengua/compile_shenqi_travel.py`、`scripts/import_shenqi_travel.py`与`tests/test_travel_case_import.py`；**完整原书版权TXT与私有SQLite绝不自动上传公开Github**。私有新SQLite`WenguaApp_V1_神奇之门_十一章_出行出国四十八例_私有研究库.sqlite3`由十章库`backup()`无损增量生成，旧十章全部不变，实际计数`sections=11; cases=48; historical_chart_cells=432; historical_case_additional_casts=3; historical_case_additional_cast_cells=27; historical_case_reasoning=200; historical_case_book_verdicts=48; historical_case_disclosures=102; semantic_assertions=690`，integrity_check ok/无外键违规。上一理论第六章112公开规则、起局32结构条目仍有未全部入私有库事项，不宣称已物化。

下一章遵守`docs/CASE_OUTCOME_POLICY.md`：作者若未明确承认断错仍标`author_book_success_default`（不等于外部科学有效），事件后补同案验证，严格保留实际出现的每张不同时间盘，绝不造盘；问用户App仍一问一时一盘一次完整回答。远端逐文件重新读回+GitHub Actions**最新main对应的两Python任务都success**才宣称完成。减少重复推送通知，优先一个原子GitHub提交；禁止拿旧绿灯替代最新。
历史按计划起飞机时刻起局必须另记为cast_selection_strategy；同一事件真实两张时辰盘必须存实盘，后续旧盘复断绝不补造；不将后验答复和天气复盘作为首问事实。

## 2026-10-19 追加：先学领域解题方法，再用每个完整案例学习作者综合断盘

根 AGENTS.md 新增的“专题方法先行，每个历史案例必须学习作者整盘推理”是所有未来章节的硬性验收要求。先完整阅读该领域第一节，记录适用子问题、问者/当事人关系、主辅用神及理由、观察顺序、跨章知识、吉凶条件、反证、冲突、应期、限制，再逐案分析作者如何把前述方法和已经学习的基础知识落实在真实盘上。

每个完整历史案例必须保留一件事与一个 event_family，真正印出的不同时辰盘分别归档、实际观察的每个宫位及门星神干、所有原作者和学员的分析步骤、所调用的旧知识 concept_id、宫位与宫位之间如何形成条件证据链、作者如何取舍反证、为何形成断语或应期，以及书内后续反馈和老师纠错。即使没有编号的完整分析也不得漏；原文缺失的盘不得凭推测补造。来源未写明的理由属于 AI draft 推测，不可冒充作者原话。

案例是学习解题方法的演练，不是背诵结局。作者明确失误及修正属于负面教学证据，与原事件整体保存；后验信息严格隔离，不得偷看结果或在 train/test 跨事件家族泄漏。验收强调能否依据领域方法与跨章知识解释未见盘、主辅用神有无依关系切换、同宫证据和跨宫关系是否真实、反证是否考虑和应期是否确有来源。所有输出仍为 draft，未经人工审查与验盘不得作为正式预测。最终 App 只做一次完整解答，不是持续追问的对话。

本次重复来源的 SHA256 为 5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574，与现有 行人走失预测 精校完整版(1).txt 完全一致，禁止增加第13章或任何新案例数字。
## 全历史案例强制完整证据链（2026-10-19）
此流程回溯适用于现有58个历史整案及新增《钱物丢失预测》8案，未来所有新案亦同。逐领域精读取用方法；逐案从完整原书重建事前问题→用神选择理由→实际宫位证据→跨章已有概念ID→多因素组合和反证→条件应期→作者原话→后验验证与错误修正。旧库里的254条分析若尚未逐步对齐，不准称历史已完成；只有私有SQLite中的原书才可支持逐字补审。新建008迁移用于每一步机械候选记录，需人工复核才能提升状态，初始禁止正向训练。错漏如第6新案车位未断出、例7事后老师按语要明确隔离。所有计数、上传、最新CI核对规则不变。

## 从2026-10-19起：用户明确授权公开全量SQLite，每次新章必须有版本快照

每章工作闭环为：先读取GitHub根AGENTS、状态、账本及上个归档 `.sqlite3` → `sqlite3.backup()` 无损生成新文件（版本名含真实来源章数和事件数）→ 用新原书全文SHA严格校验后增量导入不覆盖旧案 → 所有实际印出的九宫严格9宫，中心宫只保留原字与“五宫寄坤二宫”来源推导的独立host字段，绝不伪造中五宫门星神 → 逐案记录所有步骤，后验事件和替代起局独立phase → 逐案历史全盘复查源行号与concept_id，仅审完才能approved → 提交GitHub公开原始完整 `.sqlite3` 二进制（用户授权）及 `.xz`、manifest、章索引、AGENTS/状态/账本/测试 → 核对本次主分支真实SHA及GitHub Actions Python 3.11/3.12均成功。不能仅生成本地SQLite声称已上传；不能覆盖以前历史快照。对外公开有二次分发风险，用户本次已经明确知悉仍要求公开。

## 第十五章官司诉讼新强化：隐含错误方法和结果先于分析的源章节仍须完整保留

按既有公开SQLite版本控制闭环推进；当原书学生做出最终正确判断但其**用神方法被后文作者明示否定**时，书内结果层与步骤级错误层必须分别保留，错误步骤永久不可提升正向训练。原书有**先断语/后反馈/再原印九宫/再详细分析**这种倒叙结构（官司例6）时，不按排版顺序判定信息可用性：必须明确截取第一次预测前的输入，新增信息后披露单独phase，真正源盘与事后解释虽然完整保存却不准当作未见新案首断依据。每张实际印出中宫保留字，无普通八神／门／星就标不适用并依旧起局法寄二宫单独追踪。用户已允许每新章将完整版原文字段SQLite（不是只有CSV/索引）公开上传GitHub独立归档，且需经远端Hash与本次HEAD的双CI验收。

## 第16处理章《体育竞赛预测》与每章完整公开SQLite闭环（2026-10-20）
所有历史和未来案例同一流程：专题条件化方法→所有原书案例整段阅读→事前问事事实及真实时辰→每张实际印盘九宫→完整作者步骤及方法试探→具体旧概念关联候选→支持证据/反证/时令与应期→原书反馈与错误修正分层→人审未完成则draft。此章特别区分第2例甲戌口头判断（无盘）与乙亥真实盘、第3例宫数/八门/九星三个尝试阶段、第5例点球决胜比分及“铺庚”未核OCR、第6例法国/克罗地亚胜者断错。每章必须从上一版GitHub实际`.sqlite3`以backup()生成新独立二进制和压缩副本，检查旧原文及盘面一字不变、完整性、哈希、公开归档路径、最新main对应的Python3.11/3.12 CI；不能让只存在本地的产物充当GitHub版本。

## 第17章军事历史源稿：2件事≠4案例；先据原文字段与问事时间划分层级（2026-10-20）
必须沿用 `AGENTS.md` 全量旧案与后续案例证据链政策；本章1个第二次世界大战事后对照、1个1998年海湾危机3次真实起盘。前者不得当独立预测，后者不得拆成3个独立成功案例；每次盘对应 source_cast、问事前背景、新事实和作者步骤。连写未编号解释（第111行）归第109行原作者同一个编号步骤。原文有争议的历史时序必须保留并另标人工史料校核，不自作修改。只有GitHub归档 `.sqlite3` `.xz` 和 manifest 真正到最新main、SQLite完整性/全旧表逐行核对、最新 Python3.11+3.12 两项均绿灯才声称完成。

## 第18来源章《天时气象预测》标准执行与案例阶段守门（2026-10-20）
延续根 AGENTS 所列**历史与未来所有案例**的完整作者解题链标准。本次天气书稿仅5个整体事件、5张真实九宫、13步；按九星天英晴/天辅风/天柱蓬雨、壬癸是否随星、所在宫及月令、门神生克反证统一建领域方法，再逐步源行号绑定作者观察与条件结论。尤其严格拆分例1第42行同列的初断和反馈；例2的三种**非奇门**六爻起卦绝不虚增盘/事件，旧卦的预先结果不作为独立未见输入；例3辰巳两时连贯判断、例4重复利用球赛问时并重定天气问事、例5未来用事时间起局均按原书分阶段保存。中五原字保留，派生寄坤不冒充作者原书星门神，历史所有旧行不改。每章按最新经SHA核实的17章完整SQLite backup()增量，GitHub Actions自动生成18章新版完整版原文SQLite、压缩版、manifest，并校验旧行逐表保真/CI。未经源书逐步人审不可为训练正例，古术数不能替代专业气象预报。

## 地理环境新章的无原文推理禁编和公开SQLite强制闭环（2026-10-20）
原书2案2真印盘；第1案三个方案是同一项目的设计候选，不是三张盘；第2案前面的癸山丁向只根据地形图口述，不能生成奇门盘或单独被训练为成功奇门断案。第2案虽有辛山乙向墓地真实盘，但作者仅给出结果未提供逐宫推理、应期，不可自行补完整断案理论，必须保持缺口和 draft。第1案专家已经先选择艮宫，且8亿资金计划的部分确认不证明2001开业与14亿最终成本。中五原字乙、壬分层，来源盘不改。继承全部旧18章原字及结构，并生成GitHub公开19章93案完整SQLite二进制+压缩归档+SHA256 manifest，验完真实最新main CI方称完成。

## 2026-10-20 第20处理章《神奇之门·人生机遇预测》永久交接及缺来源不得补造
此章原书标题为“第十六章”，项目真实累计顺序为**第20处理章**；原始TXT 37,761字节/273行/SHA256 `92de6590ebf88698d9bf0137e8ecdb780b8f1ff1f66765faf0a69eb3d7eac507`。原书确实5个整案、5张来源九宫45宫、作者分析/断词源行51条（第1案11条含未编号78；第2案15条是**同一完整事件中的15个子问题而不是15案**；第3案6编号+190行事后复盘；第4案4编号+221行作者结论限制；第5案13段逐轮断语但**没有逐条作者九宫证据链**）。专题方法从作者第10、11行及韵文13-25行按具体条件整理34条研究候选，51条来源分析索引均有源行、发生阶段、词面候选及反证/缺口，所有条目标注draft/`positive_training_eligible=0`；不要用古书的人格、疾病、死亡、年龄、灾祸断语当现实科学事实。

**三类最重要的反事实/后验防泄漏约束：** 例3赵某在第186、188行事前仅断“正月/七月注意车祸”，第189行结果正月初五发生撞人事故，第190行才事后据内盘、值使等推具体五天，不能把五天断法记成事前准确预测；例4第一段195行**女童死亡结果事先已知**，第217-221行出生盘分析全部属后验案例，不得做独立盲测、不得用术数预测儿童寿命；例5 第257行作者猜测丈夫于1994或1995年病故，第258行当事人明确纠正为1996年，**这一年份初断是书内明确错误**；第259行以后再用1930与1996干支解释是已知结果后的推理，不能倒灌。例5后面还有其他回答及反馈，必须保持同一event_family完整保存，不允许把整体其他正确说法冲掉这一错误。不允将用户“未来计划”当已经实现（例如例2最后新问办厂戌亥月）。

领域原则：**出生时间局**用于传统先天及长期机遇分析，**问时局**用于近期机遇，人物角色与年干父母/领导、月干兄弟/同事、时干子女/下属随问事切换，结合年命及坐宫；八门、九星、八神、格局必须条件化联合推理，原作者也明确说古籍绝对化不可拘泥。第二例15段分析中多人命年与官司、家庭、子女、出国及办厂必须按问答先后阶段隔离，严禁后披露信息偷跑到首轮输入。历史全部93案亦继续按相同作者真实逐步推理标准待逐案人工审查；本新章学员问答中的证据缺失处不能凭后来答案伪造中间论证。

**基库硬门槛：** 必须从已在GitHub归档的19章93事件全量 SQLite二进制 `archives/sqlite/WenguaApp_神奇之门_19章_93案例_完整研究库.sqlite3` 其 SHA256 `9412c314a10827b34f6d2e1930124b672f389156d86692d58db1ffdff5ada4b0` 开始，只能 `sqlite3.backup()` 无损增加，保持全部以前来源行不变，不能重新从索引构造，不能覆盖原19章快照。中宫单干照原书，寄坤二宫独立推导，绝不编门星神。新增 migration015、构建器20_from_19、来源和CI，并由专用Actions提交公开完整版 `20章98案例.sqlite3` 及 `.xz` 压缩版本、SHA256清单。构建前数字**仅为预期**：20章、98完整事件、105实际盘、945宫、468作者分析、1207候选、明确书内错误至少6件含新案#5；**远端归档未完成不能报完成**。所有历史/本章完整人审的作者因果链未完成，禁止自动批准或以命理替代医疗、交通安全、法律、现实职业规划。UI和旧QimenLLM继续冻结。

## 第21来源章《其他杂项预测》完整案例/异种预测/多盘/后验分层永久样例（2026-10-20）

新章原书五个完整故事，7张真正印出九宫（申奥同一事件3盘）。本章无单独“领域取用经验”，必须逐案归纳作者真实取用及证据，不得凭常识填补没有写下的推理。每条作者分析连同宫位源字、支持与反证、旧概念词面候选、已知/新披露/结果/老师按语阶段标draft，不自动审批。第一案信件为**六爻**、后书中三奇门盘，不能将三盘宣称同期已提前发布或一事拆三案；第三案110多人在第178行才获知、最终140在第180行；第四案临场先断再反馈、237-247行事后详细解释；第五案280行为老师已知结果按语。新四层九宫的中5只保存原单干并派生寄坤，不凭推断填原书空格。严格从20章98案完整SHA 1332fe460c1e73bd74939760c59a376980c888bb8d9e41c3b7416fadd4bbdaa3 生成独立21章103案公开二进制SQLite与压缩版，旧所有表源行不变；GitHub CI绿灯前不宣称完工。


## 所有未来新增古籍的跨书多版本强制步骤（2026-10-20）

开始逐章整理前必须读 [MULTIBOOK_PROVENANCE_PROTOCOL.md](MULTIBOOK_PROVENANCE_PROTOCOL.md)。统一概念 ID 只允许在查询层结构化去重，必须保留所有不同书、不同作者叙述、不同章版/来源原文、不同方法轨道；新书是补充，不是替换旧版本。若无实际问事起盘，原书中的空间/历法数字格、图例或对旧书的案例引用不得虚增新盘和事件。对同一书新修订用 content_version 和 SHA 管理。最近完整远端 SQLite 必须经 SHA 验证后 sqlite3.backup() 只追加，再产生独立的新库/.xz/manifest，旧版不改。每章更新 AGENTS/PROJECT_STATUS/CHAPTER_LEDGER，执行 migration 与回归，并验证当前 main 双 Python CI 和远端输出真实 hash。


## 后续新书必读：第二本第二章特别分轨经验（2026-10-20）

九星天时状态（我生最旺、同类相、我克休、生我废、克我囚）不能与一般地上五行的旺相休囚死混在同一表；九星落宫为主、月令兼看。十天干阳顺阴逆的十二长生与十二地支自身的五行长生法不能套用，戊己十干继承火干丙丁，地支土又有独立水土同宫逻辑。中五天禽寄坤是派生关系，不填伪造中心“平门”，不允许把中宫源单干改成外围多层格；墓与库需结合月令旺衰；八门凶吉要看领域/格局/宫门生克和月令。新书引用老书的两段“先断错后修正”仅作为原旧 event_family 的分析来源，不新增成功样本。上述各点以书、版本、原文SHA和行号独立可回溯；新来源不自动approved。不要将九星/12状态示例图当作历史实盘。任何新章都须在上一版全量SQLite的原始字节上backup增量、完整公开独立快照/压缩/manifest并验最新CI。


## 第三章纸上起局强制回归模式（2026-10-20）

凡以后遇到同书或新书排盘步骤，必须把**原书教学习题盘**与**历史预测案例实盘**分表：教习起盘和反事实示范不等于新的事件成功样本。七步的“地盘—值符/值使—天盘—人盘—神盘”有顺序依赖；值使随旬内每时辰按九宫数字阳顺阴逆跳宫定**唯一值使落宫**，其他七门再按外围八宫固定圆盘旋转，不能把9数字走法应用全门/九星。九星外围转动与天禽寄坤是另一轨，八神随星值符的落宫起点按阳顺阴逆方向布。中五原书仅单干/无门等，必须一字不多存下再另栏解释派生。只在明确阴阳遁、局数、时干支时用旧 `casting_shenqi` 逐宫对原文比较；精确公历转干支/节气/时区/日界单独校验。参考完整协议 docs/MULTIBOOK_PROVENANCE_PROTOCOL.md。归档必须12张图108原宫及4教习盘，103历史案不新增。


## 第四章来源判断与81有向十干克应回归规则

解析整个原章，保留81条有序天盘客/地盘主及反向组合各自原文和source line，不能用无序set消重、不能补造未见的19条；记录应期成功8项、失败6项、拦截寻回庚格3法及空亡/乙庚合排除和事后失准。来源符号相同不代表领域取用相同；年命及行年两种推法并存而作者优先本命。2幅原书图（旧银行案例再版九宫与宫位五行教学示意）单独增入资料性图表，不能新建案例/印盘。原书写的已知结果和后验决策与事前断语分层。构建必须从最新完整SQLite按SHA256检查父库，`sqlite3.backup()`扩展、全旧表逐行核对、SQLite integrity/FK、独立新版本、压缩/manifest/CI。严禁发布医学与金融实际有效性的误导性确认。

## 开悟第五章：古文/作者释义独立来源的强制流程（2026-10-20）

遇到古文第N段及其后“解说”，将原引用和后人解释拆开，逐段对应、分别保存完整原文字节、书章版本、行号、sha256，不得以现代解说改写古人语句、不得把同一概念去重到只剩一条原文。12古文+12作者解说是24份来源，不是12历史事件；全章无实际问事起盘。拆补与置闰分独立起局方法轨，日干生门四内外关系分开，戊丙与丙戊等有序上下配对不合并，九星/八门职业类象先验整体旺衰和语境；贫富、寿命、性格等书内断语为未经独立验证的古籍传统主张，候选draft不可用于用户现实判断。必须按SHA指定最新版SQLite backup增量，保持所有旧数据全行不变，实际Action归档及当前HEAD CI成功后再更新真实数字。


## 2026-10-20 《开悟之门》病例与《神奇之门》现有health域统一

医疗/疾病相关的案例必须重用 cases.domain_id='health'，新书和旧书只是不同的book/source/provenance，不允许再建另一套独立“kaiwu health cases”域，也不可把动物疾病放到没有统一检索的隔离案例表，animal_health只作为health内subdomain。遇到同一历史事件在两书各有完整盘，必须分别保留各自原文source witness和九宫原字，但cases/event_family_id只保留唯一事件、historical_chart_cells独立历史盘数量只计一次；重复来源不当独立盲测或两次成功。第一节例二B1996-07-27女问辛酉年父病原属 shenqi.health.19960727.father_illness；例二A1995-02-19弟病来自作者标“奇门学术论文之七”的第三方旧论文，没有完整初断，只可作为注明缺失事前断词的独立比较素材。案例前后阶段要分：known_before/原印盘/作者初断/书内事后反馈/编辑事后比较，不能倒置。死亡时间未实际观察则不声称精确命中；原始未知天干/异常星神符号保留缺陷并来源标注，不擅改。医学治疗只能由专业临床判断，这些古籍表述非临床证据或治疗建议。新版统一查询view health_cases_all_books用于复合检索，所有基础历史表和多书轨道不可覆盖。


## 2026-10-20 用户最高优先级：原书历史案例无需再逐例人工审核；跨书同域统一

凡用户主动提供的《神奇之门》《开悟之门》原书完整案例，书中问事、原书断语及后来反馈按用户认可的历史案例来源直接建库、使用、做书内结果对照。不得因先前脚本reviewed=0/draft或缺乏外部验证而强制用户批准每条案例；旧版原始行无需修改。始终如实保留源内第一次预测失败、书中作者后验纠正、信息何时出现、重复事件及多盘、无盘/无反馈事实；不得把用户认可书中记载误说成外部科学/临床证实或危险专业建议。跨书按 sports_competition、criminal_case、health、military_history_source、litigation 等统一domain_id和 event_family_id 索引；不同书只增加独立 source-witness/书内论证轨，不能按书名分裂业务案例库。新增复杂年度趋势可带多领域标签。用户认可规则对老书新书一体适用。原书2026-10-20提供《热门话题预测评析》13专题、20真正来源印盘；北京2008申奥第九/十三是同一event，台湾2000选举第543行原书作者明确认错不可假装事前命中。最新父库SHA 79b30135e42129f6596c66f09eec66496ae5d08afb8786f2831581f3fe7c6b05，仍须无损sqlite3.backup增量，全旧表保留。

## 2026-10-20 跨书恋爱婚姻案例领域归并、同人不同事与书内首次错断

《开悟之门》第二章第二节恋爱婚姻6例完整源sha256 4df9dfe432daec759df4f0e01449bc4a2381eb4251e1290a0d99d199e467fa01，305行/34960字节。六例都并入原《神奇之门》同一个marriage领域，不为Kaiwu另建业务案例库；6真印盘54原宫字及26分析步骤完整保留。第2/3例是同一个女性在不同时间提问不同婚事，建立同一人物关联而不合并历史独立事件；第4例兼就业及遗失钱物，第5例兼求财，用统一跨域facets查找。两件后续工作/复婚经营未来结果原书未给，不能补造。第6例原书作者初断单相思女性，被求测者明确回信“准确度极低，大相径庭”，新信才披露同性恋情，后出作者重释不能倒灌到首次推断，保留为新增书内明确初断错例。性取向本身不属于疾病或需治疗状态，古籍内旧时代叙述不可当作现代医疗诊断。第6例只有一张完整印出的盘；另外出生局及后信起局两盘作者自己省略，不补造成原书实盘。用户接受古籍案例无需逐例批准仍有效，但不能将用户认可书中事迹理解为每次首次断语均正确或经独立科学外证。下一版仅从当前28节全量SQLite sha 6dfe4337697e64a100f63de0b9d5144ad00e3b2e3fa818d9d314ea304a92a10d 无损备份追加，所有旧表原行保持。


## 2026-10-20 跨书工作就业同域、同局双事项、未知原盘和后验时间绝对保真

Kaiwu原书第四节工作就业3例来源SHA eeaaa79d23528dfc608282f6ab0b120620a7c44d67588145a9166a9bd03c733e，150行14577字节。三案例3真正来源印盘27原宫字、作者步骤13+后来编者评论4。与Shenqi现有employment业务领域共用case表，附组织任命/组织资格/交通事故标签。例三只一1997原局，对次日入党申请与1999农历二月车祸警告分两事项报告，却不能拆成两个事件两张盘；具体1999二月二十三日源书明说是在“前几天死了一个人”的事后消息以后才推算，禁止事后信息污染原始1997预警。原盘header甲午日与分析称日干辛有字面差异，保留二者而不改原书。例一原文阳5局当时采用置闰法，坎1门和星分别注明“原文未辨干”，两处天干不可推断补写。例二值使杜门中五宫寄坤二宫，原书中五不适用强行补普通星门。书内案例用户接受无需逐例人审，书内结果标签与外证仍区分。下一版严格从29节完整父SQLite SHA 64a01b16828dff326e1d0a2bd759147032fb8ef30869aa595be7aae04d492339 增量，全旧表行保留。


## 2026-10-20 Missing-person two-book event identity, unreadable source and same-event casts

Kaiwu seventh section 行人走失预测 original source SHA256 193e1eb8438a83e1408efa804daf66ea43e64f36155e221be23c9de53215ab71 has five original lost-person event families, six printed ASCII Qimen boards. The same niece is represented by a genuine inquiry-time board and a different genuine disappearance-time board; one family, two source casts. Two abducted hotel workers are distinct subject outcomes of one real inquiry and one real chart; do not count twice in performance or event families. The new male taxi homicide report references older Shenqi Ma Lande's female taxi-driver story as a similar *different* event: retain an explicit bibliographic reference, not a duplicate event and not an unverified hard-FK asserted same-case join. Another student predicted Aug16 home but the reported actual return was Aug17; preserve exact timing miss while keeping other source-reported aspects.

ASCII 3x3 palace grid may have 4 or 5 genuine per-band text rows. The special extra fifth row in new source chart six contains OCR text 原OCR：庚 辛 and MUST be kept in source witness; the conventional 4-row parser would silently lose it. Original unreadable OCR cells, gods, doors, stars and middle-center literal cannot be filled by recalculation; keep literal and missing-data flag, and omit uncertain standardized values, never overwrite source. The entire 200-line 27441-byte user text is preserved. The user directly accepts book historical cases with no case-by-case approval, but independent modern criminal or forensic evidence is not claimed. Next fully verified parent SQLite SHA256 9107e3e440a1448cce93fdef288a48c88a8440b3998c5adcf041e2f770172ae7 (32 source sections / 138 unique events / 155 real printed charts). All old rows must be immutable through sqlite3.backup.


## 2026-10-20 共领域业务/工业安全与书内明确错误的跨书来源纪律

开悟之门第五节经营求财11原书真实问事、11原书九宫，整章全文源SHA256 10d777fe514315c8e56dbef6d6a5152300b79c0ed041b92ee10f15cccef18fdf。既有Shenqi business_profit共领域新增十个求财项目；煤矿塌陷第五? 实为本节**第十例**，单一真实工业救援事件主域industrial_safety，附business_profit关联标签，不能以业务分类掩盖人命安全属性。第4/5科迪药业同一项目不同时间问资助与开工，第7/8太和日化城同一工程不同求测人的开发与独立购买问事，链接same_project但不是same_question，不合并event_family，也不算重复预测成功。第5例书作者原先6月21或22开工预测明确错，实际6月29取得证后开工，事后重解释不是初断成功，新全库整例明确错误9条。第8例只能证实预付三个月租金，不能宣称三年投资已验证；第11例其它大奖少年无独立来源九宫不能新增一盘一例。原书所有OCR缺损和原宫额外第四行raw不推算补字；中五宫只打印X干不可以填普通八神/门/星。原书问事项目直接接受无需再次逐例用户人审，但不称独立安全/财务/刑法科学核验。下一章父库必须是完整SHA256 cd1f9e1d4e352644b062bc048afb977dcc457c40bf76a5673a6e39ae93f21ac5（33来源节、149独立cases、166真实印盘）；旧行全部不可变。


## 2026-10-20 Kaiwu lost-property original source and temporal evidence discipline

Kaiwu second chapter eighth section complete 180-line original SHA256 fad699fbddf34f7bf4ff16849d4154d4633bce51c234db1cf0ecc4ff7eb8f554; four distinct historical lost-property cases and four genuine printed OCR-rearranged nine-palace boards (starts 16,57,97,156), 36 literal source cells, 25 original complete numbered/A-D reasoning units. All join original Shenqi domain_id=lost_property (8 older Shenqi cases+4 Kaiwu), not independent per-book category silos. Event1 recovered pouch but not 4300 cash: the finder denies having seen the cash, so NEVER infer that specific finder committed theft. Event2 is reported police/court motorbike theft, event3 earring was on bed and not criminal theft. Event4 on Aug20 1999 FIRST applied six-yao, bought Shenqi book Aug26, learned Qimen over next week and found motorbike Sep17; detailed Qimen analysis and exact-day reading are in later retrospective letter, not proven identical to the original Aug20 prediction. Other railway outgoing/incoming Qimen casts mentioned but not actually printed and must NOT be new fully documented real charts. Preserve raw OCR deficiency in original palace fields, mid5 only source stem, not invented deity/gate/star or rewritten evidence. All book cases user-accepted without per-case approval, no fabricated external forensic or empirical verification. Next ONLY verified SQLite parent: full 34-source/153-event/170-original-cast file SHA256 3e92bdf9a356edb0685bcb803122319ed56477ab97d0fd38b23a2f5c16fc2185; use sqlite3.backup, all preexisting rows immutable.

## 2026-10-20 Kaiwu travel book-accepted six cases / seven literal boards

原著第六节出行出国源SHA256 b561f1d0a216ab9da83955112752164c4bf6558be15a0a7017f350e423d37f67，230行28678字节；6个真实古书来源事件、7原印九宫、63来源宫、34编号步骤，共用既有Shenqi travel_abroad统一domain。一例1992航空事故是CCTV公布死亡消息后的事后反演，不是先验准确预测，不得加入预测成功样本。加拿大移民申请同一申请人1999年6月及10月两张真盘，但仅一个case；原有1998面试失败是求测前已知，10月第二盘日时与年命分析互相矛盾需保留，第132-135行考试后作者复盘单独分相位；原书只证实10月29日面试通过，不等于最终签发加拿大永久居民身份；六月16日11:40还有一处原书提到的未印问盘，不可增盘。香港永居+春节回家为同次问事不同事项，源书农历附注原样不改；法国护照被拒另案。佟安琪2000年8月10日去程、8月18日返程与前钱物丢失摩托车案是同一个人但不同事件，分别有真实九宫并增加明确跨章节关联，不可重复数，也不可纠正源书站名不一致。源九宫多行OCR缺损/中5无普通门星神/附加第五文本行一字不补。原书故事用户认可免逐例人工审核，书本报告不等于外部司法/科学核实。下次增量必须由35节159案例177真实盘完整SQLite SHA256 aa48d1f492e398c3216e7be15eb80653ab2bc57482c73f29a8d293d06b0ad47a 开始 sqlite3.backup，所有旧书旧行绝对保真。

## 2026-10-20 刑事案件跨书领域、课堂时序与错误初断绝对保真

Kaiwu第二章第九节源SHA256 f7e7dd3790e56bd43ed73e72d30ca9554609343c10640840b247b665d5b18b50，100行12565字节，2真实事件2确实印盘18原宫。复用《神奇之门》原有criminal_case业务域，旧5原专章刑事案及新2源案都必须包含，但同领域还可能含其它章的刑事相关案，不能断言总数仅7。第一个1996年现场研讨抢劫案，逐次先猜7000现金、两歹徒、女被害人等，然后由张局长现场逐条答复；不得将后说的回答偷换为先前就已知，第49行“能抓住一个”尚无后记抓获证据，不可冒充已被确认。第二案1999年11月14日求测11月9日已经发生的兰州命案，先一张未展示的案发局提及，完整印出的仅问测时间一张盘；不多造盘。第78行初断歹徒2-3、原书后来实际1；第86行初断破案丁丑月、实际11月21丁丑日，第90行本人承认这两方面错误；另初断遇害者约3实际4是书内近似偏差，但非作者明言第三处错误；随后第98/100行张志春知道答案后重解释不属于事前判断。保留原书巽4“庚；杜门 癸”、中五宫“庚（原OCR中宫字符）”和“壬（原OCR中宫字符）”、坤2“伤门 丙（壬）”、艮8“天芮 丙、天禽 壬”，不伪补普通中宫神门星。古书案例无须用户逐例审批，但原书刑案情节不是独立法庭证据或犯罪人鉴定。新真实完整父库 SHA256 70b31dbe6005aa1d24af5faf298796effe0d06a87b2c1faf0af55d461cb5a1b9（36来源节161独立案例179原印盘），下章只能以此全库sqlite3.backup且旧行全保真，错误整例总计10。
