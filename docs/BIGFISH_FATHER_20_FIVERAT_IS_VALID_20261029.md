# 五鼠遁与父亲前20条失败：明确切分历法合法性与年甲取用绑定 · 2026-10-29

## 争议及精确判定
用户建议「根本原因：违反五鼠遁，甲子日乙亥时进入下一天」，但其列出的顺推恰好表明 **甲子日乙亥时为合法且位于甲子日 21:00–23:00 的最后亥时**。如果采取23点换日规则，只有 **亥时结束后的下一子时** 进入下一日乙丑、丙子时；甲子/乙亥本身没有违背日上起时。不同传统/软件对23:00换日、晚子时日柱可能存在异例；这个边界争论不影响任何 21:00–23:00 亥时有效性。

## 实际用户数据与本地验证
重新直接读取用户原始 `father_000001-000020.xlsx`（同前审计 SHA `0aa7118e856970b3ba5f617ce679ae5c52f2fca6113f281cb891eda99ca71857`），行1–12皆 `甲子日`，小时 `甲子 乙丑 丙寅 丁卯 戊辰 己巳 庚午 辛未 壬申 癸酉 甲戌 乙亥`；行13–20 `乙丑日`，小时 `丙子 丁丑 戊寅 己卯 庚辰 辛巳 壬午 癸未`。均满足原脚本 `Wengua_BigFish_518400.py::scenario/hour_ganzhi` 的自动五鼠遁，且日时本身是合法六十甲子，不曾任意手填不合法时干。月柱甲子年推成丙寅（月干五虎遁），也没有直接违背五虎遁。
在本次研究环境实际使用用户已下载的 **完整原 Python 脚本** `/mnt/data/Wengua_BigFish_518400.py` 在仅做导入与纯函数运算的方式测试：`scenario(0..19)` 原样给上面20对；`N_CASES==518400`；`hour_ganzhi(60日×12时支)` 共 **720/720** 所得均是合法60干支。该测试**没有调用BigFish线上下载或重跑V8**；与之前用户真正Mac生成20条、40/40上游九宫存在，是两个不同层面证据。
GitHub新增 `tests/test_five_rat_father_20_separate_from_signifier_20261029.py`，独立公式逐对对照仓库 `src.wengua.casting_shenqi.hour_ganzhi_from_day`，检查720对、前20对、甲子日乙亥→下一日乙丑丙子、六甲时遁干甲子戊甲戌己有别；独立Actions `.github/workflows/verify_five_rat_father_20_20261029.yml`。
引用传统五鼠遁依据：《千里命稿》原文与解读 https://libokang.com/classics/bazi/千里命稿/；另 https://wiki.openfate.ai/zh-hans/bazi/calendar/five-rats-method 。现代网页是一般术法说明，不替代用户本人指定的两书及其编码出处。

## 仍真实存在的独立错误（不改冻结V8）
前20行失败 **18行×2节气=36分支**：Python断词环节 `Patient signifier unresolved; do not force birth-year`。`health_dynamic_v21.py::_stem_cell` 对所有角色的 `甲`，除甲时之外始终返回None；甲时改走 `health_severity_template.py::_find_heaven_stem` 根据**时柱旬首**返回六仪。对于 `father` `actor_profiles.json` 指定的问测**年干甲**，时甲子→时遁戊、时甲戌→时遁己并不能证明年甲有了自己的独立落宫；第11行“成功”反而按时甲戌己误绑，不能视作可靠断案。故不能由日时合法性证明「整个模型毫无问题」；**起盘时柱合法**与**疾病用神能独立正确绑定**是两个完全不同的验收门槛。
518400条为四柱抽象组合标签，不说明所有年/月/日有真实公历交节时刻。二节气候选是条件支路，不可未经现实日期验证当真实发生时刻。
不得把失败转成成功，不得让乾6辅助宫替换年干主用神，不得根据甲子的样本回答硬改冻结V8及源200/81。之前的 `tests/test_father_jia_year_binding_known_gap_20261029.py` 两项明确expectedFailure继续保留，独立六甲角色的修复需先核对原书、建立新研究取用寻址版本和多盘回归，再重跑旧错算保留旧尝试与用户Excel。

## 执行与项目边界
没有本轮直接修改 `src/wengua` 的冻评分公式、BigFish TS / iOS Swift / 200/81 / V10.2 客户断词/Important双镜像/MANIFEST / 原古籍。已知失败与不一致记录不删。Python纯函数720/720本地通过，新增仓库测试的真实CI状态需以对应Actions完成为准。Mac Xcode没有实跑。