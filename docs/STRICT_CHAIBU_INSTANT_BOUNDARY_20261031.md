# 2026-10-31 严格交节时刻拆补法：审计记录

用户最终确认：严格以真实交节 UTC 瞬间为界；未到为旧节气，交节时刻（含）以后是新节气。**同一两小时辰不提前换新节气，也不采用双局互参**。每15°节气按时刻切换；仅“节”（每30°，如立春、惊蛰）改变月柱。

代码提交 f4580970f762c704bebb3067355b46389e58498d：修改原 scripts/wengua_bigfish_518400_offline_editorial_20261029.py、src/wengua/astro_calendar.py、iOS WenguaNativeCore.swift及两个Important源镜像/MANIFEST。用户Mac原脚本固定旧Wengua源码a288d127883157cb2bea96b676d2c86a45c2ab12，故**只修改仓库当前历算源不生效**；原单文件已经内嵌离线交节时间表，避免旧版本0.05°保护误拒算。新的原BigFish脚本仍保留TS真正起盘、年/月/日/时真实四柱、原V8+200/81+人物绑定及V10断词。新版本独立路径 source_v2_strict_jieqi，原source_v1 SQLite失败、旧人工Excel与旧日志不得覆盖。

离线计算依据 Swiss Ephemeris 2.10.03 Moshier太阳视黄经15°交界（2025—2028共96条），以整数UTC毫秒记录于 data/calendar/strict_jieqi_moshier_2025_2028.json，并以同一序列接入Python、Swift、原BigFish单文件。时间精度为历算模型结果与毫秒舍入，不能称绝对无误差。表外年份仍采用原近界0.05°拒算保护；23时子初换日流派未确认仍拒算。

原前600四条旧拒算现在应该分别为：
- #86 2026-11-22 01:30 EST → 立冬，小雪在02:23:21.139交节。
- #87 2026-11-22 03:30 EST → 小雪。
- #264 2026-12-06 21:30 EST → 小雪，大雪在21:52:32.429交节。
- #441 2026-12-21 15:30 EST → 大雪，冬至在15:50:14.539交节。

旧0.05°规则在该1452样本窗口曾产生12条拒算，留作历史失败的只读断言，不重新标为旧版PASS。提交7ca81b26c03bff1fbd9ce793bcde475fb47de695补充交节毫秒及原BigFish/Python严格判定测试，保留旧Meeus历法方法版本供历史归档。

实测：当前 V8 主CI #41212456846 PASS；BigFish 全窗口回归 #41212456902 PASS；Book Astronomy #41212456877 PASS；较前Xcode Simulator #41212201619 PASS。其它历史任务不一律PASS：旧婚姻归档 #41212456827 因已有归档目标拒绝覆盖，独立1080 Swift全实盘 #41212201702 KeyError horseBranch，旧Native端到端 #41212201662 invalidChart。须对上述失败和签名真机单独验收。用户Mac全24×1452未在本次会话实际运行，不能冒充完成。V8疾病计分与原著未更改。

## 最终追加：月度应期边界与真 Swift 实盘专项

提交 `97315316918fcfb63c49084d794a47a7c6abc46e` 进一步将 `src/wengua/astro_calendar.py::branch_periods(granularity='month')` 的2025—2028年每30°节月边界改为同一份真实UTC交节表，不再让应期月份区间另走旧Meeus秒数；历史1998等窗口仍保留原来源方法。Python镜像与Important/MANIFEST blob SHA同步。2026年11月亥月→子月严格换界为纽约2026-12-06 21:52:32.429。

**真实新提交回归**：BigFish全窗口专项 [#41213021533](https://github.com/turnupmason/WenguaApp/actions/runs/41213021533) PASS；Book Astronomy [#41213021592](https://github.com/turnupmason/WenguaApp/actions/runs/41213021592) PASS；V8现行主CI [#41213021575](https://github.com/turnupmason/WenguaApp/actions/runs/41213021575) PASS。**真实 Swift 编译与Python 10个UTC小雪/大雪/冬至/DST时刻全盘节气/四柱/局数逐项对照 [#41213021562](https://github.com/turnupmason/WenguaApp/actions/runs/41213021562) PASS。** 之前 Swift 专项第一次仅因Python脚本导入路径失败，已在第二次提交修正并真实复测，失败历史保留。Xcode iOS Simulator真实build对应源码修改SHA的旧run #41212201619 PASS，后续只改Python、测试、文档；仍未做iPhone签名真机手工验收。

历史独立失败工作流没有隐藏或改标为成功，旧V7.4/婚姻历史归档仍须另行审计。
