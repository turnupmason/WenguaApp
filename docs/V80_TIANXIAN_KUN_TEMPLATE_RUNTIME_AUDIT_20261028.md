# V8 天显时/坤二寄干：真实运算与客户模板同源复核 · 2026-10-28

## 问题与验证位置
- **现有计分已实装**：Python `health_macro_facts_vnext.tianxian_palace_bonus` × `health_quant_overlay_vnext.inspect_selected_quantization`；Swift `WenguaNativeVNextEngine.compute` 中完整天显日干/时柱判定、真实星门伏吟与去重参与实宫。普通+2/实宫；伏吟+1.5/实宫，不逐宫取整。3宫→4分，5宫→7分；五不遇时每不同参与宫-2依旧。
- **坤二两格源数据**：Python `health_81_excel_catalog_vnext.for_real_palace`、`health_palace_detailed_vnext.inspect_complete_selected_palace`、`health_quant_overlay_vnext`；Swift `WenguaHealthTemplateBridge.fromText`、`WenguaVNextEngine.evaluate`。中五原生地盘保持，不生成星门神，始终寄坤二；两个有序81匹配皆从原Excel81表查。别宫不借中五地干；一个实宫的基础总分只纳入一次。
- **本轮查出的实际漏项**：旧 Python `render_first_stage_macro` 和 Swift `fullMacro` 均写死“全局得吉时之助”，忽略伏吟折助；合断也写死“整盘得吉时扶助”，与+2/实宫及伏吟+1.5不一致。坤二详情只写本地盘干，虽背后算两组真81格，却没解释第二组为何存在。
- **现行修复**：`reading_template.json` 模板新增 `tianxian_regular/tianxian_fuyin` 与 `tianxian_evidence_regular/tianxian_evidence_fuyin` 以及 `kun_host_note`。Python `render_first_stage_macro` 用真实星门伏吟标志按键读取，Python终论按同标志取证据句；Swift按原生实时星/门伏吟选择同键，最终段落和坤二详情亦取同JSON。文本不暴露内部加分数字。原作者81格七字段模板及原TSV保持不变。
- **回归**：新单测 `tests/test_tianxian_kun_template_narration_20261028.py` 验证选择条件、真实模板键及跨语言源调用，配合 `test_tianxian_tianqin_host_20261028.py` 与全部现行V8 Python/native parity。合成盘只算结构与文本测试，不是独立疾病预后验证。
- **过往版本**：2026-10-28 13:44同一实盘原0、暂行天禽随飞3、坤固定后0，属于已揭晓回归；原失败归档不删。新提交验收需读本轮GitHub Actions（尚待运行）。

## 2026-10-28 · 天显/坤二新模板最终实测（本轮可复核）
- 正式源码模板及Python/Swift客户断词由commit `24c5bbbdf7f1970279897bb35650a47d8912d7ea` 同步；当前模板版本 `health_severity_user_editable_template_v20261028_tianxian_kun_v9`。新模板区分普通天显/天显逢伏吟和对应终论语句，并由坤二真实参与时输出中五寄干两格说明；无客户分数泄露。
- 新独立V8 Python3.11及3.12 主CI **#40779886724 PASS**，含 25类原始克病矩阵、72组同宫特例、现行8角色宫图、3/5宫伏吟最后统一取整、新真实模板键路由、Important双镜像SHA与Xcode UI守卫。
- 真正 Python→原生 Swift V8 全文逐字专项 **#40779088908 PASS**（源码commit 24c5bbb 同一Python/Swift模板；25类矩阵/72同宫+两原盘+13:44四人物，通过，所见病例全部已揭晓非盲测）。
- 真正 macOS XcodeGen→Xcode16.4 iOS Simulator完整编译、在实际未签名`问卦.app`内核对200格JSON、81格TSV、22人物profiles、20261028新模板schema及五个新文案key及元信息 **#40779886908 PASS**（正式工作流修订commit cf05b666deef3c58b6f8b7d1ebdba96894479cf2）。构建、包内检查、artifact归档及自动PASS日志均实际完成。
- 旧版模板schema导致 #40779088950 的旧UI版本断言FAIL、#40779088892 的旧Xcode资源校验FAIL；第一次修复又因inline Python多一空格使 #40779534953 FAIL。这些失败均保留，不能删除或冒称从未发生。以前旧原生全库部分工作流另有 `invalidChart` 和V7断言错误，不属于本次现行V8模板验收成功范围，也不宣称全库全部通过。
- 本轮没有真机签名、TestFlight/App Store或用户手工界面验收；本次Xcode成功只确认真实Simulator编译和bundle资源。
