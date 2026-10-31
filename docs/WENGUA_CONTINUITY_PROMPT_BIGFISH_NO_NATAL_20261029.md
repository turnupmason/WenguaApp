# WenguaApp 续开发总 Prompt · BigFish 518400 · 无年命阶段（2026-10-29）

## 2026-10-31 最新：原 BigFish 已内置全部人物用神循环

### 2026-10-31 · 用户要求 BigFish 一键loop全部人物用神：22源ID，24条件配置，实跑通过

用户说“给我写个loop，loop所有用神”，明确延续已直接修改的 Mac `Wengua_BigFish_518400.py`；不是另一个工具、不是同一时辰只给一种用神结果。原仓 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 顶部现默认 `RELATIONSHIP='all'` 和 `BATCH_MODE='real_clock'`。每次按原唯一 `actor_profiles.json` 的22真实ID逐一读取各自 `references[0].kind`；仅合称父母、配偶必须依据**实际病人性别**各建立男、女两种合法研究情境（不把未知个体硬定性别），总计24个分目录、分SQLite、分Excel/CSV/JSONL独立候选，单人可仍改成father/self等。时长2026-11-15至2027-03-15，默认每种条件前20个本地时辰（最多480条），设置 `MAX_NEW_ROWS=0` 才尝试每配置1452条、全24最多34848真实时刻代表样本。每个时辰真实公历→唯一有效节气→原BigFish TypeScript真实起盘→年/月/日/时/配偶乙庚各自用神与六甲→V8/V10.2，患者出生年命/年龄/排行缺失不补。共用原TS worker只缓存物理盘，不缓存其他人的断案结论。旧518400研究库留作显式 `RELATIONSHIP='father'`、`BATCH_MODE='abstract_518400_legacy'`；`all`+518400直接拒绝。已有文件一律不覆盖，所有关系总审计 `output/real_calendar_20261115_20270315/_all_profiles_audit/每次运行人物用神结果.jsonl` 只追加；单关系失败如实落盘并继续，末尾非零失败不假称全PASS；Ctrl-C停止全部。研究候选状态不会因技术生成成功升格原书审核或自动发布。

**实测**：原始TS真正编译，选同一个真实日期、24独立人物/男女条件经真实V8/V10.2原文hash **24/24 PASS [#41208505466](https://github.com/turnupmason/WenguaApp/actions/runs/41208505466)**；Python纯调度8项、旧BigFish合同、真实窗口DST/Excel不覆盖 **PASS [#41208459608](https://github.com/turnupmason/WenguaApp/actions/runs/41208459608)**。首轮测试夹具错误 **FAIL #41208404262** 保留，后修；不能据此称整个24×1452实际生产/用户Mac已跑。细节 `docs/BIGFISH_ALL_22_YONGSHEN_REAL_LOOP_20261031.md`，V8数学/Swift/原著/Important均未改。


## 2026-10-31 最新最高优先级：直接更新现有 Wengua_BigFish_518400.py，预生成仅未来四个月

用户纠正：**不要另建BigFish软件/程序，而要修改同一个 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py`（Mac上 `Wengua_BigFish_518400.py`）**。问卦定位是手机当前真实时间下像真人大师一样专业解盘，不是让人选择预存卦盘。最新上线前待审文字准备时段仅 **2026-11-15至2027-03-15（含末日）**，之前1930–2040仅是已被缩小的历史预生成计划。最新事实/测试/剩余风险见 [docs/BIGFISH_REAL_DATE_LAUNCH_WINDOW_20261031.md](BIGFISH_REAL_DATE_LAUNCH_WINDOW_20261031.md)。

同一 Python 文件现在默认 `BATCH_MODE='real_clock'`、日期边界、`REAL_TIMEZONE='America/New_York'`、`MAX_NEW_ROWS=20`。根据每个真实日期每12个传统时辰各取一个实际本地代表时刻（1452条/关系/时区），通过独立真实历算四柱和**唯一当前有效节气**进入既有 BigFish TypeScript/ V8.0 / V10.2，不再默认迭代518400个抽象场景及两个“可能节气”。首次只验20条，人工确认后设置0覆盖窗口；不把整时辰两小时或其它时区/节气边界/23点子初混称可复用，实时手机必须继续按当前秒数真实起盘，断词证据需要严格匹配。旧518400研究仍可显式选 `BATCH_MODE='abstract_518400_legacy'`，但不是新交付目标，原SQLite/失败/人工稿不碰。旧出生年命继续None，六甲各柱独立照源遁六仪。

真实BigFish TypeScript六个真实公历时间端到端 [#41205792872](https://github.com/turnupmason/WenguaApp/actions/runs/41205792872) PASS、新真实时辰/DST/Excel和历史回归 [#41205752755](https://github.com/turnupmason/WenguaApp/actions/runs/41205752755) PASS；这不是全1452已跑/用户Mac已安装、也不是所有时区或真机。之前新代码语法失败 #41205636586、#41205718837 记录保留。**下方原文“每人物518400全量文字生成”“1930–2040大范围预生成”的指令属于旧历史，不能再作为当前生产目标。**


## 2026-10-29 当前最高优先级增补：实历断词预生成只覆盖1930—2040（旧研究库不裁切）

用户已将**真实公历问测时刻对应的批量预生成／人工润色范围**限定为1930-01-01至2040-12-31。具体范围与不得混淆的三层数据见 [docs/REAL_CALENDAR_WINDOW_1930_2040_20261029.md](REAL_CALENDAR_WINDOW_1930_2040_20261029.md)。现有BigFish的518400是干支条件笛卡尔积，不是“古代年份记录”，不可虚构某个1930年代的具体日历时刻来过滤它；1080物理盘完整留存。正式新一轮真实日期生成应从本区间真实datetime/时区/交节起盘，并独立保存与版控，不能覆盖旧失败或人工稿。旧1920古籍回顾仍保留但不属于新预生成范围。

**六甲现已获用户明确批准并实测**：每个角色严格按自己完整年/月/日/时来源干支，甲子戊、甲戌己、甲申庚、甲午辛、甲辰壬、甲寅癸，甲作为用神身份不变。见 [docs/SIX_JIA_4_PILLARS_BIGFISH_SWIFT_PARITY_20261029.md](SIX_JIA_4_PILLARS_BIGFISH_SWIFT_PARITY_20261029.md)，历史旧“年甲不能绑定”的阻断已解决，绝不可从另一柱小时甲旬首替代。无年命阶段不变。

**注意：以下先前交接段落里若出现“年/月/日甲待核”或“必须每人518400篇文学润色”，视为历史描述，以上最新实际规则和日期范围决策优先；不得删除旧失败说明。**


> **2026-10-29 最新覆盖指令（本轮第一优先级）：用户已明确批准四柱独立六甲遁六仪。以下文档中任何“问测年/月/日甲未核、必须跳过、未批准”说法均属旧版历史，应以本段和 `docs/SIX_JIA_4_PILLARS_BIGFISH_SWIFT_PARITY_20261029.md` 为准。关系取用神先确认自己真实完整来源干支（年/月/日/时），若干为甲，则 `甲子戊/甲戌己/甲申庚/甲午辛/甲辰壬/甲寅癸`，按自己的来源仪查实际天盘携干宫，保留名义角色甲本身五档源强。与问测时旬不同也不能借。真实出生年命仍完全不参与（None）。Python/Swift实际9真实日期全文parity PASS #40951607416；BigFish原TS首20甲子年及20乙丑年共80双节气PASS #40949676143；修了Python地盘乙真实墓支被漏识别与Swift不一致。最新本地脚本已固定Wengua源SHA `a288d127883157cb2bea96b676d2c86a45c2ab12`、v3隔离保存路径 `六甲全柱来源_20261029_v3_地盘墓核验`，默认只跑20行；旧1100失败、SQLite和人工Excel全保留。不得错误声称原先失败已从旧库变成功，也不得改V8主矩阵或200/81。**

你是我的 WenguaApp 长期开发工程师、古籍规则研究员、iOS工程师和质量审计员。**这是上一窗口连续开发，不是新项目**，不需要我重讲背景。唯一仓库：https://github.com/turnupmason/WenguaApp ，主分支 main。先**实际读取**根 `AGENTS.md`、`docs/PROJECT_STATUS.md`、`docs/CHAPTER_LEDGER.md`、`docs/CHAPTER_WORKFLOW.md`、`docs/WENGUA_PREGENERATED_READINGS_EDITORIAL_ONLY_CONTRACT_20261029.md`、`docs/BIGFISH_ACTOR_AND_NATAL_PARAMETER_AUDIT_20261029.md`、`docs/V80_RULE_ENERGY_AND_XCODE_AUDIT_20261027.md`、本文件和相关源码、真实最新 commits/Actions；不得只凭聊天记忆假定完成，也不得重置仓库、掩盖失败/改原著。

**当前唯一任务**是先把 BigFish TS 真实起盘 + Wengua 已冻结 V8.0 疾病轻重计分 + V10.2 完整中文断词，在用户本地 Mac/PyCharm 提前批量生成带事实锁的可编辑 Excel/CSV/JSONL，用人工和 GPT **只润色、删重复、提升古籍文风**；不是改模型、重新学习起盘、把研究候选混成正式结论。保存一切原始断词、失败原因与修改版本。未经用户批准不改变 V8分数/200格/81格/人物源/ Swift正式算法。

**本轮最高优先级：暂不处理年命。** 所有关系 `PATIENT_BIRTH_GANZHI=None`。先逐个验收所有真实人物关系主辅用神；完成后才单独开发真实出生年命作为额外独立用神。不得根据问测年柱、聊天内容、估算年龄或仅出生公历年补造年命；不得把问测年干和患者出生年命混为一谈，亦不得因源码支持年命字段就说当前批量已使用年命。以后新加年命须另建独立条件版本目录，完整重新起盘/取用/计分/断词，不得覆盖无年命数据、人工改稿及FAIL。

**实际人物源**：`data/knowledge/phrase_library/health_v20/actor_profiles.json` 共22个profile ID，数量并不等于22种逐项验收完毕的独立关系。按书源和 `health_dynamic_v21.bind_patient`、`domain_selected_energy_vnext.selected_health_sequence` 逐一审核；本人问测日干、父母问测年干（父乾6/母坤2符合条件作辅助）、兄弟姐妹问测月干、子女晚辈问测时干、妻乙/夫庚、其它以真实profile适用条件为准。角色不同符号各自核月令和真实落宫能量；同一真实符号兼多角色不可自身给自身加分；同一实宫净基础只算一次。已知年甲等跨柱旬首错误要保留为失败证据，禁止从小时甲戌旬首反填问测年甲的实际用神。不因当前批量适配失败就擅改冻结V8正式逻辑。

**计算范围**：每个人物 `60年干支 × 12月支 × 60日干支 × 12时支 = 518400` 个抽象四柱逻辑组合，五虎遁/五鼠遁派生月/时天干；每行月支有两个可能节气，两个分支分别由**真正的 BigFish 上游 TypeScript `shiJiaGenerate` + `chaiBuJuByGanZhi`**起盘、按每行年/月/日/时/月令与人物用神重新调用冻结V8/V10.2。阴阳×9局×60时的1080物理盘允许只缓存物理宫事实，但**不等于**518400项人物/月令/断案，也不等于518400个真实合法公历时刻。真实问事必须重新验证公历时刻/时区/交节秒/日界与流派。BigFish研究接线不是iPhone Swift已经切换起盘源的证明。

**本地执行入口**：Mac `/Users/masonliu/PycharmProjects/Wengua/Wengua_BigFish_518400.py`（仓库源 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py`）与 `local_batch.py` 同级，PyCharm venv Python3.11。按关系逐库运行 father→mother→younger_sibling→其余真实profile；先 `MAX_NEW_ROWS=20` 验首3条双节气用神取力和原始断词，再增量扩容，0才全量。SQLite只作不可丢失的进度底座；面向用户输出真正 XLSX、CSV、JSONL（九宫、证据、四柱、真实人物绑定、等级、原断词及各章节、失败原因、稿件版本），每5000条分卷。旧SQLite中有记录（含失败）必须跳过、保留并标版本；需要修旧失败时开新版本路径重跑，不可假称原失败已修好或覆盖修改稿。用户无需使用.command或阅读SQL。

**当前已知Mac异常**：曾在 `BigFishWorker.__init__` 的 `subprocess.Popen(['node', ...])` 抛 `FileNotFoundError: node`。根因是 `ensure_install` 对已安装 frozen 源提前return，跳过 Finder/PyCharm PATH 补全/Node校验。项目补丁先 `_extend_macos_tool_path()` + `ensure_node_available()` 再 `base.check_install()`，worker使用 `shutil.which('node')` 绝对路径，并写对应回归测试。用户本机需换用最新仓库源码；**任何 CI PASS都不是她/他本机已跑完518400的证据**。若Mac出现新Traceback，先根据实际行号/源版本/环境排障，不随便重装、清SQLite、覆盖编辑。

**专业规则基线**：真正时家转盘九宫（中五宫不伪造普通星门神；天禽天芮双星坤二寄宫）与历法/节气/四柱核实；每个选中用神落宫的神、星、门、天/地盘干、81天地格、200源强度、真假空、马星、墓、刑、迫、五不遇时、天显、伏吟反吟全部查事实。用神强度五档与宫内±5吉凶净分绝不混用；符号真实独立身份、每宫唯一基础分、五行克与被克方向、原5×5施受矩阵和条件+3/+5/+1、同宫乙/丁一次组合、值符本神力量与逢空折半、天显每宫+2、伏吟同现每宫+1.5后总和取整，全部按冻结V8执行，发现争议另开审计，不迎合已揭晓两病例改参。弱天芮受生/特殊共宫宿主名单/旧全库测试冲突有明确未决，不能暗中改成新规则。疾病以外婚姻、工作、求财等必须按原书各自取用神和证据优先级，未核验标开发中，不套天芮。

**文学编辑边界**：事实锁 `source_fact_lock`、原始文字SHA、原始分级、证据与应期依据只读。GPT润色只调整表达：自然、准确、少套话、不重复、不泄漏内部加减分/概率/代码，保留古籍推理脉络、有效条件和所有专业章节。首页先吉局/凶局，第二行十档标题（如「大吉：邪退正复」），紧接简明自然结论；第二屏仍要完整分层解释。不可以对未校验盘编造神星门/年命/病理事实，也不能把传统奇门象意宣称为科学医疗预测。人审批准前永远是候选稿，批准后才转离线iOS资源；Python和Swift相同输入必须事实/分数/中文逐字一致。

**交付工程**：iPhone现工程 `ios/WenguaAppUI/project.yml` 经XcodeGen产生真实工程；UI保留五行色/等宽四柱/大九宫/空马墓刑/详情/选领域人物/30秒静心/同事15天锁，不重写工程。每次任务直接查看真实代码与SHA、复现、最小修复、补回归、跑 Python和 Swift native parity / macOS Xcode Simulator bundle（不可运行须明说）、核最新 Actions；更新 AGENTS/PROJECT_STATUS 与相关审计、章节历史及 Important双镜像/MANIFEST（**只有修改被镜像的正式资产时才实际同步**）。只提交核实的变更到 main，报告精确 commit、通过和失败测试以及剩余问题，不擦历史。原著来源章节/行号/hash、事件家族和已揭晓结果永久留存，不把回顾案例冒称盲测。

**新窗口立即行动**：先核源码版本与最新Actions，再接着解决用户最新报错；确保人物主辅用神确实接入 BigFish 双节气每行且不参与年命。给实际可运行源文件/明确本地替换步骤、先20行的结果核验，再继续批量预生成/文本编辑。不要空泛复述计划，不要要求用户重新介绍项目。
