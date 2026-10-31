# 2026-10-31 · 用户决定直接改原 Wengua BigFish 批量代码，只预审未来四个月真实时辰

## 直接用户指令与产品含义

用户明确：问卦是**按手机当前时间、用户实际情况和领域人物专业解盘**，不是展示一张预先算好的固定卦盘。现阶段无须为518400个抽象条件组合或1930–2040年逐一文学润色；新预生成窗口只做 **2026-11-15 到 2027-03-15（含两端）**。用户随后特别纠正：**不是另建一套新工具，要直接修改原 Wengua BigFish 的 Python 脚本**。

旧版 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 的518400理论组合研究循环完全保留为显式 `BATCH_MODE='abstract_518400_legacy'`；当前同一文件默认 `BATCH_MODE='real_clock'`，不是继续用原 `60×12×60×12` 的抽象四柱枚举，也不会从旧518400库挑一个伪造的真实日期。

## 已实现的真实范围和排盘路径

新参数：`REAL_DATE_START='2026-11-15'`、`REAL_DATE_END='2027-03-15'`（含边界）、`REAL_TIMEZONE='America/New_York'`，`MAX_NEW_ROWS=20` 供首次本机小样本核对，修改成0才生成该真实窗口全部代表时刻。窗口121天，每日选择12个**真正本地带UTC偏移**的代表时刻，00:30/01:30/03:30/.../21:30，共 **1452 条真实日期时辰样本/每人物+时区**。每条调用 `src.wengua.astro_calendar.solar_chart_clock` 得真实四柱、唯一**当下生效的节气**、时间戳和历算SHA；与原书 `bureau_for_term` 的局数、阴阳遁和真正 BigFish 编译 TypeScript 的 `chaiBuJuByGanZhi` 对照，不一致拒绝。继续调用同一原BigFish `shiJiaGenerate` 的物理九宫，再经现行 `compute_variant` → 完整人物用神（独立六甲遁仪、乾坤条件） → V8.0 → V10.2中文；用真实日期事实锁而不是假的双节气条件。**严禁将12个样本误称已覆盖每天所有秒**：节气在时辰内部交节、23:00子初流派争议、DST缺失/重复时间仍需要手机按实际秒数现场起盘，不能从附近时辰复用预生成的文字。面对尚未通过术数来源/算法校验的输入，不以同宫旧词冒充当前结论。

输出新目录：`output/real_calendar_20261115_20270315/<relationship>/<IANA_zone> /source_v1`（zone路径实际把`/`改`_`，无空格），每人独立源配置封印+SQLite `real_cases` + 分卷 XLSX/CSV/完整章节 JSONL。真实日期、时区/偏移、四柱、实际节气、局、九宫物理ID、用神源柱及遁仪、原分/等级/断词、失效原因、原始事实SHA、用户人工与GPT编辑空栏全部保留。SQLite与已导出的审核稿不覆写，源配置发生改变必须独立版本目录。旧 `full_518400` SQLite、失败、Excel、人工修改及古籍原著保留。保留原导出器默认5000行一卷；新真实时辰审核卷另设200行。

本次完全不改 iOS Swift 时间实时起盘、15天同事限制、200/81及V8数学或固定模板，Python正式`PATIENT_BIRTH_GANZHI=None` 的无年命阶段保持不变。未来的用户手机仍以设备真实秒数和当地IANA时区直接离线起局、重新选用神和断词，**不以这四个月候选文字预审库作为运行时唯一查询源，也不将范围用作App功能限制**。前期1930–2040仅是历史计划，保留见 `docs/REAL_CALENDAR_WINDOW_1930_2040_20261029.md`，本轮新的预生成范围优先。

## 真实测试与风险

- `tests/test_bigfish_real_clock_nov2026_mar2027_20261031.py`：新默认模式、1452个带时区真实日期样本、两端边界、春季DST前后真实UTC偏移、23点拒绝盲算、拒绝矛盾局数、不重复覆盖旧SQLite/人工Excel、真实xlsx非双节气列、原生历算仅当下一个节气；在 BigFish batch 专项运行。专项 GitHub [#41205752755](https://github.com/turnupmason/WenguaApp/actions/runs/41205752755) **PASS**，原旧单测也通过。
- 初轮 `#41205636586` 与 `#41205718837` **FAIL**：新函数一个Python `dict.update` 关键字写成字符串赋值导致SyntaxError，未跑进真实历算。已更正并保留失败历史，不对用户称第一次通过。
- 真正原BigFish上游固定TS编译/1080结构及真实6条公历日期 Wengua V8/V10.2完整断词端到端 [#41205792872](https://github.com/turnupmason/WenguaApp/actions/runs/41205792872) **PASS**：2026-11-15零时和亥时、2026-11-25零时、2026-12-29零时、2027-03-15零时和亥时；每条检查真正年/月/日/时、单一真实节气、局数、真实用神、六宫条件、中文原文SHA，无出生年命。**6条成功不代表1452条或iPhone本地安装已跑完**。
- 原真Swift V8 parity [#41205752883](https://github.com/turnupmason/WenguaApp/actions/runs/41205752883) 的当前最终状态需实时确认；本轮没有改Swift生产代码。Xcode Simulator [#41205752793](https://github.com/turnupmason/WenguaApp/actions/runs/41205752793) 的真实状态也须另查；不得说真机/IPA验收。

## 用户本机操作

仅替换 Mac `/Users/masonliu/PycharmProjects/Wengua/Wengua_BigFish_518400.py` 为仓库最新 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py`，先备份原.py，别清 `local_batch.py` / `vendor` / `frozen` / `output`。不再主动跑完整518400抽象库；首次运行只处理新窗口前20条真实时刻（配置 `MAX_NEW_ROWS=20`），人工检查实际当地日历/节气/四柱/角色/中文后改0继续剩余新窗口。**未实际跑用户Mac；网络首次安装Node及TS编译状况需以本地Traceback为准。**
