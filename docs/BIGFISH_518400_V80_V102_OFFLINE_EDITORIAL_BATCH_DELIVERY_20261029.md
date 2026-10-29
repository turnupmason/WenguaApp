# BigFish 每人物518400条：封存V8.0/V10.2原始中文预生成与离线审校工作件（2026-10-29）

## 用户需求（本轮明确）
只用 Python 在本机 PyCharm 挂机，按用户一次选一个人物的原则先父亲、后母亲、弟弟等，枚举 60年干支×12月支×60日干支×12时支＝518400个**抽象合法四柱组合**，按五虎遁/五鼠遁推月干/时干。各月支有两种真实可能节气，**分别计算两支断词**，不能任意选一个说是实际公历时间。BigFish 固定原始 TypeScript 负责九宫物理排盘（18阴阳局×60甲子时=1080源物理状态），缓存同一物理盘而对每条条件独立重算人物/真实月令与冻结Wengua V8.0判级以及V10.2完整中文。只是在本机预生成和后续人工/GPT修改中文，**不改封存模型、书源、Swift**。

## 本轮实际代码与路径
- 完整脚本真实提交 main：`scripts/wengua_bigfish_518400_offline_editorial_20261029.py`，1050行左右。与用户旧 PyCharm 项目里已有 `local_batch.py` 同级，覆盖为 `Wengua_BigFish_518400.py` 即可；脚本内置之前的 pinned BigFish/Git/npm/Node官方SHA与SSL安全下载安装及冻结四资源 SHA 检查，不需.command。
- 本轮最新用户下载单 Python `/mnt/data/Wengua_BigFish_518400.py` SHA256 `4108e479ee1194f6b5da9bf03eac7f12aabdcbcf67d64d95cae81f3f530f5ea8`；ZIP `/mnt/data/Wengua_BigFish_518400_V80_V102_批量润色版.zip` SHA256 `a77cd48f3119fe78e38a0337b6dbb04775890de66a91401e4348e845d21b82f6`；ZIP中的PY与单独PY字节一致，CRC通过。
- **默认 `RELATIONSHIP='father'`、`MAX_NEW_ROWS=0` 表示对当前人物继续所有剩余518400条；`=20` 用于可选试跑。爸爸结束仅修改 relationship 为 `mother`、`younger_sibling` 等；动态读现行冻结人物 profiles（JSON实际22 ID，用户正式20关系与较多辅助ID仍要按源区分），无生日/性别/排行不补造。
- 源 TypeScript 调用 `shiJiaGenerate` + `chaiBuJuByGanZhi`，本机worker常驻Node一进程，并缓存最多1080九宫。原 BigFish 为唯一正式九宫输入，严禁拿 Wengua Shenqi 对照版替代。
- 断词保持已有与 `scripts/preview_20261028_twoclocks_six_relatives_v80.py` 相同的 `src.wengua.health_severity_vnext_review.analyze_health_severity_review` 入口，并使用 `full_health_role_strength_network.candidate_five_grade_quantization.summary.score` 与原 `reading_text/sections`，**没有第二套打分函数、没有GPT改写或改V8正式公式**。注意这仍是仓库现存 Python review/candidate 分支，不能仅因此宣称518400盘均已经Swift全字段逐字对齐或当前App在线实际切BigFish；在专业书源选择不足时照实失败保留，不为凑断词填假用神。
- 本机持久库为 `output/full_518400/<relationship>/<relationship>_断点进度.sqlite3`，每10条事务提交；已记录旧20条（包括18失败）照原状跳过，不自动覆盖/篡改已经编辑的Excel。输出 `Excel_CSV_可直接打开/<role>_000001-005000.csv`、`<role>_000001-005000.xlsx`，以及对应 `*_待审事实包.jsonl`。每条两个节气分支原文/身份/局/盘式、V8内部等级与分数/原始正文/全文分节/角色事实锁/应期/源哈希/失败原因。另留空的人工修改/GPT修订/人工审核栏，不自动发布App。
- 本轮重要修正：旧脚本第一行双失败会停止，本版 `STOP_IF_FIRST_ROW_FAILS=False`；若某时刻源角色不能定位只记录 `失败_保留原样`，其余合法行继续批量。**不是**放宽核心证据/偷偷补造年命。已导出CSV/XLSX/JSONL不覆盖，防止丢用户人工修稿；JSONL原始身份 SHA、事实 SHA、`editorial.approved_for_app=false` 供下一步对照润色。

## 本轮真实测试
- 本轮容器中 Python `py_compile` PASS；本地真实 518400/720五鼠遁枚举、临时SQLite2行含“成功原文+源用神失败”双支、CSV+实际XLSX ZIP结构、JSONL 4条（每行2节气）、保留错误、可编辑字段、SHA身份、不覆盖导出与断点配置冲突均 PASS，未调用互联网AI/真实Node原TS。
- 已有用户 `father_000001-000020.xlsx` 使用 artifact_tool 成功打开，旧18行空白来自真正 Python `Patient signifier unresolved`；本版**不解决旧跨柱甲取用疑点**、不抹去已见失败，先大规模生成可用稿/保留有问题的行供后续单独事实审核。
- GitHub新增专用测试 `tests/test_bigfish_518400_offline_editorial_20261029.py`（4项Python合同）及 `.github/workflows/bigfish_518400_offline_editorial_20261029.yml`，**真实 Actions Run #40938996134 PASS**，确切验证完整主代码Python语法、SQLite/CSV/XLSX/JSONL、原稿不覆盖和源失败保留。此前BigFish原始TS全1080结构 #40920402953 PASS；实际两个2026-10-28时钟的BigFish转Wengua Python入口 #40921478524 PASS。这些不等于本轮518400×2真打全、也不等于最后iOS Swift BigFish当前切换/Xcode真机已通过。
- 目前只做本地代码交付＋GitHub Python合同，**未在本环境真实联网安装或跑满518400、未做本轮 native Swift、macOS Xcode编译、bundle资源新验收**，要如实报告。V8冻结模型/200/81/V10.2/人物源/Swift/Important双镜像/MANIFEST和原著/历史FAIL未修改。

## 后续审稿纪律
用户要的是把生硬机械的中文改成自然、连贯、不重复的优美古籍风格，绝不可让人工/GPT把原盘事实、用神强弱、判级、应期触发条件或缺失信息改错。首页约200汉字，第二屏完整逐角色章节；`scripts/health_editorial_batch_v1.py` 和固定 `prompts/health_severity_gpt_editorial_v1_20261029.md` 已存在，后续应复用。原文、修稿、人工批准分版本保存，审后才能离线打包，未批准不进入手机App。
