# V8 天显时/坤二寄干：真实运算与客户模板同源复核 · 2026-10-28

## 问题与验证位置
- **现有计分已实装**：Python `health_macro_facts_vnext.tianxian_palace_bonus` × `health_quant_overlay_vnext.inspect_selected_quantization`；Swift `WenguaNativeVNextEngine.compute` 中完整天显日干/时柱判定、真实星门伏吟与去重参与实宫。普通+2/实宫；伏吟+1.5/实宫，不逐宫取整。3宫→4分，5宫→7分；五不遇时每不同参与宫-2依旧。
- **坤二两格源数据**：Python `health_81_excel_catalog_vnext.for_real_palace`、`health_palace_detailed_vnext.inspect_complete_selected_palace`、`health_quant_overlay_vnext`；Swift `WenguaHealthTemplateBridge.fromText`、`WenguaVNextEngine.evaluate`。中五原生地盘保持，不生成星门神，始终寄坤二；两个有序81匹配皆从原Excel81表查。别宫不借中五地干；一个实宫的基础总分只纳入一次。
- **本轮查出的实际漏项**：旧 Python `render_first_stage_macro` 和 Swift `fullMacro` 均写死“全局得吉时之助”，忽略伏吟折助；合断也写死“整盘得吉时扶助”，与+2/实宫及伏吟+1.5不一致。坤二详情只写本地盘干，虽背后算两组真81格，却没解释第二组为何存在。
- **现行修复**：`reading_template.json` 模板新增 `tianxian_regular/tianxian_fuyin` 与 `tianxian_evidence_regular/tianxian_evidence_fuyin` 以及 `kun_host_note`。Python `render_first_stage_macro` 用真实星门伏吟标志按键读取，Python终论按同标志取证据句；Swift按原生实时星/门伏吟选择同键，最终段落和坤二详情亦取同JSON。文本不暴露内部加分数字。原作者81格七字段模板及原TSV保持不变。
- **回归**：新单测 `tests/test_tianxian_kun_template_narration_20261028.py` 验证选择条件、真实模板键及跨语言源调用，配合 `test_tianxian_tianqin_host_20261028.py` 与全部现行V8 Python/native parity。合成盘只算结构与文本测试，不是独立疾病预后验证。
- **过往版本**：2026-10-28 13:44同一实盘原0、暂行天禽随飞3、坤固定后0，属于已揭晓回归；原失败归档不删。新提交验收需读本轮GitHub Actions（尚待运行）。
