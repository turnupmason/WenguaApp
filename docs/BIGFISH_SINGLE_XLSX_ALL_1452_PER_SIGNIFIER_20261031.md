# 2026-10-31 · 用户最新确定：全部用神直接全跑，每用神一个完整Excel，不拆卷

## 用户明确要求与覆盖旧计划

用户问：“ROWS_PER_EXCEL=5000 / REAL_ROWS_PER_EXCEL=200 这两个啥意思，我要一个用神在一个excel里，因为一个才1300多”，再明确“**不用，直接全跑，东西很少**”。这是对刚才预审20条/每200行导出一份Excel的直接修订。现行最新脚本 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 已实际修改：
- `BATCH_MODE='real_clock'`、`RELATIONSHIP='all'`、`MAX_NEW_ROWS=0`：默认不设人工分批上限，按人物源22个ID + 配偶/父母合称男女各一支，共24个独立上下文，真实日期2026-11-15至2027-03-15，含首尾121天×每天12个独立代表时刻=1452条/配置；总最多34848个代表时刻。用户所说1300多是近似，实际严格算是1452。
- 旧 `ROWS_PER_EXCEL=5000` 只服务明确选择的旧518400抽象研究模式；**移除 `REAL_ROWS_PER_EXCEL=200`**，真实时辰模式再无按行拆卷：每种人物/男女单独配置完成全部1452条，严格查SQLite记录0..1451及逐条真实ISO时刻匹配后，只导出**一份完整1452行的XLSX**（附同一完整数据的CSV和不可改原始事实JSONL），目录 `output/real_calendar_20261115_20270315/<actor>/<zone>/source_v1/[optional_sex_specific]/每个用神一个完整Excel/`。合称配偶/父母男、女必须分别一个Excel，不混同患者主用神或自造年命。
- 为保护人工修改和保存断点，运行中每10条提交SQLite；中途停止或遇错误，**只保存SQLite** 不生成零散的20/200行正式Excel，下一次同样命令能续跑。全部完成后检查整段真实clock的完整性、Excel/CSV/JSONL存在性与非空、源数据签名；已导出并存在的文件只返回原路径，绝不重写人工修改稿。若历史200行Excel已生成，**按不删历史原则保留在旧 `Excel_CSV_可直接打开/` 子目录**，新的单文件另放 `每个用神一个完整Excel/`，避免用户把过去手动修改旧稿与最新正式单文件混淆。
- 本次没有修改BigFish原TypeScript算法、V8冻结加减分、81格、200格、Swift UI、人物来源、原书数据/旧失败记录。特殊真实节气交界的未知仍按原真日历保留错误，不能拿一条代表时刻替代整个2小时时辰；预生成不是临床判断或原书验证。连续三组未知错误停该人物并保留日志，避免空白万条被误作成功，其余人物继续而总状态保持FAIL。

## 实测

- 实际专项单测 `tests/test_bigfish_real_clock_nov2026_mar2027_20261031.py::test_one_full_1452_row_excel_per_actor_then_no_rerun_overwrite` 新增验证：先提交20条但不导出分卷，全部1452条才导出1份XLSX+CSV+JSONL，xlsx XML正好1453行（含表头），首末真实时刻、人工修改稿保留、同一批重复运行无覆盖。原有真实时区/DST/148?（准确1452）日期枚举、人物循环、518400旧库合同测试不变。GitHub [#41209416239](https://github.com/turnupmason/WenguaApp/actions/runs/41209416239) **PASS**。第一轮仅将默认20改为0时，旧测试断言仍要求20导致 [#41209286670](https://github.com/turnupmason/WenguaApp/actions/runs/41209286670) **FAIL**，后更新测试后 [#41209340380](https://github.com/turnupmason/WenguaApp/actions/runs/41209340380) PASS，前失败记录保持。
- 原BigFish TS真实启动与全部22人物24条件 [#41208505466](https://github.com/turnupmason/WenguaApp/actions/runs/41208505466) 24/24 单时辰PASS；未在用户的Mac全量完成34848条，也没有声称全部断词已人工审核。旧人名/性别与原书标research_candidate_only状态不因技术生成升级为已证规则。真Swift Python parity/XcodeSimulator旧专项 PASS，但本次未改Swift业务引擎。
