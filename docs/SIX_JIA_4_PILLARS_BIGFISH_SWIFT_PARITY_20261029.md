# 2026-10-29 · 用户明确批准四柱独立六甲遁仪，修复父亲1100行失败并核Python↔Swift↔BigFish

## 用户最新明确规则（覆盖此前“年/月/日甲不可独立寻址”的工程阻断）
领域疾病、关系父亲主用神仍为**问测年干**；不是患者出生年命。选中角色源柱为甲时必须用**其自身完整干支**寻找被遁六仪：
`甲子→戊、甲戌→己、甲申→庚、甲午→辛、甲辰→壬、甲寅→癸`。
年/月/日/时各自独立；绝不可将年甲子误绑当前时甲戌之己。角色真实名义用神仍是 **甲（木、200格自力）**，遁仪只用以寻找实际天盘符号所在宫；不能把甲的源力量复制为戊的，也不能把某个物理宫重复计基础分。
来源：用户本次显式批准；已有核心 `casting_shenqi.SIX_JIA` 六对映射，历史甲年已见失败案保留。对尚无真实出生年命的批量始终设置 `PATIENT_BIRTH_GANZHI=None`，以后真实年命为额外独立来源，不能用问测年柱补造。

## 修复代码与准确缺陷位置
- `src/wengua/health_severity_template.py::_find_heaven_stem` 增加 `source_ganzhi`；甲源有效且来自本人年/月/日/时柱才按原六仪定位真正天盘携干宫；`_role`按选中关系给真实源柱。
- `src/wengua/health_dynamic_v21.py::_stem_cell/bind_patient` 显式保留 `stem='甲'`、`source_ganzhi='甲子'`、`carrier_stem='戊'`，独立绑定问测来源，患者出生年命缺失不参与。
- `ios/WenguaAppUI/WenguaNativeActorBinding.swift` 新增 `sourceGanzhi`，`actualStem` 依自身六甲；`WenguaNativeReadingRouter.swift` 用实际时柱甲寻时干；`WenguaNativeVNextEngine.swift` 用原甲符号自身五档真力而不是“伪造一个普通甲天盘”，核对来源仪所携天盘并参原十二长生。
- `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 禁用旧 `DEFER_UNRESOLVED_JIA` 跳过策略，升级 `PIPELINE_VERSION=bigfish_518400_two_terms_sixjia_all_source_pillars_v3_earth_tomb_parity`，源仓固定 `a288d127883157cb2bea96b676d2c86a45c2ab12`，单独安装到 Mac `vendor/WenguaApp_sixjia_source_v2` / `frozen_sixjia_source_v2`，全新 `output/full_518400/<relation>/六甲全柱来源_20261029_v3_地盘墓核验/`；旧 SQLite、1100失败、人工Excel永久保留。新版默认 `MAX_NEW_ROWS=20` 首次逐分支核验，通过后用户自己改0继续。每行两种可能节气均真实BigFish TS原函数起盘，再用每行年/月/日时及人物源重新判，518400是抽象条件组合而非等量已证公历日期。
- 发现独立 **旧 Python/Swift 地盘乙入墓判断偏差**：2014-12-06 05:00 EST 父亲年甲午，乾6地盘乙十二长生戌墓/亥死，Swift实际将地盘乙入墓限制为+1，Python `health_quant_overlay_vnext.py` `_matching_restriction(detail['earth_tombs'],ground_stem)` 误以为 `earth_tombs` 列的是干名，实际上是墓支，漏认。修 `"墓" in ground_stages` 明确源全12中的地盘乙真实入墓，再按既有+1和一次逢空处理；**没有增设新量化奖励、更改源200/81或疾病V8加分系数**。新 `tests/test_six_jia_earth_tomb_cohost_parity_20261029.py` 锁定复现与事实；旧偏差和失败日志独立保留。

## 真实执行成果与失败完整链
- 历史父亲上传 `father_000001-001100.xlsx`：1100行×双节气=2200失败，全因 `casting_year_stem 甲` 未解析；原始错误Excel不覆写。不拿已见回顾测试当秘密盲测。
- **真实BigFish原TypeScript编译起盘→V8原始评分→V10.2完整中文**：GitHub Actions [#40949676143](https://github.com/turnupmason/WenguaApp/actions/runs/40949676143) 真PASS：原先甲子前20行×两节气40/40 + 乙丑后20行×两节气40/40，总80/80；每条核用神甲→戊、乾6辅助、无年命、源事实和文本hash。
- 第一轮 Python/Swift all-six-Jia strict real-date parity [#40950149606](https://github.com/turnupmason/WenguaApp/actions/runs/40950149606) **FAIL**：9组有8组逐字一致，2014甲午父亲最终V8分数同为-5，但 Swift 比 Python 多写“乾六宫得地盘乙奇同宫扶助。”，旧事实与日志完整保留。
- 检查真实墓支后修Python映射。第二轮 [#40951607416](https://github.com/turnupmason/WenguaApp/actions/runs/40951607416) **PASS**：正式Swift编译+**9个真实公历问事时辰**，6个不同甲年来源以及月甲、日甲、时甲，Python和Swift全部章节ID、标题、全文逐字相等；2014真实地盘乙入墓加分事实两端一致。不是 BigFish 新TS已移植成Swift。后续新完整CI [#40951701897](https://github.com/turnupmason/WenguaApp/actions/runs/40951701897) 亦 PASS。
- 更新 `Important/python/engine/health_severity_template.py`、`Important/python/scoring/health_quant_overlay_vnext.py`、`Important/swift/engine/WenguaNativeActorBinding.swift`、`WenguaNativeReadingRouter.swift`、`WenguaNativeVNextEngine.swift`、`Important/python/scripts/ios_vnext_three_random_20261026.py`、`Important/swift/tests/VNextThreeRandomNativeFullCheck.swift` 与 `Important/MANIFEST.json` 新Git blob SHA；严格镜像检测PASS。新增研究生成器仅用于真实测试，正式UI没有重构。
- 早期增量提交 CI 失败：未同步镜像、历史旧固定成绩不适用于新甲柱规则、临时开发审计打印 Swift 拼接语法错，均已在GitHub失败日志与 docs/HEALTH_V80_FAILURE_RUN_* 留档；不能删旧版V8已见预测回顾与原封证据。
- 真实Mac PyCharm没在此环境跑过；518400×2双节气全量与独立公历时刻集合的外部核验未完成。此前真XcodeGen iOS Simulator资源构建仍非签名真机或App Store。

## 下一步
从固定的最新Mac源 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 在用户电脑覆盖**仅Python启动文件**，不覆盖 `local_batch.py` / `vendor` / `frozen` / `output`。先父亲20条，确认旧数据库0重算但新v3前20条输出均有新角色源柱/遁仪宫/双节气完整中文；再运行其他来源柱年甲6种、月甲日甲时甲的批量；扩容到518400时段落检查失败分布并保留所有FAIL。年命最后作为额外用神单独条件版本开发。