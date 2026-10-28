# 2026-10-28 · V8原分冻结下客户V10文案精简与朋友用神事实审计

## 复现：先前已见随机一盘（不是未见盲测）
- 实际时辰2025-12-28 17:00美国纽约冬时；四柱乙巳/戊子/辛未/丁酉；阳遁7局。原生Swift/Python原始结果分档极大凶，完整原文在docs/HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40781030045_ATTEMPT_1.md；该盘已见，须只作版本对照。
- 原问题：health_dynamic_v21.bind_patient、WenguaNativeActorSource.bind均直接读actor_profiles.json；朋友当时kind=casting_month_stem正确，但JSON status=research_candidate_only错误地将用户确认的同辈月干标成待核。修正只改friend status/source/note，不动别的角色、实体或event_news下日干改用条件。
- 原公众文案：health_palace_detailed_vnext.render_complete_selected_palace及Swift palaceText直接把每个真实81格古文+古诀大意+天地取象整段贴给公众，天干长生字串长生/冠带/临官/帝旺/沐浴直接并列，五不遇明说每宫扣两分以及「按用户规则」等开发话术。用户明确要求全部改。
- 现在：新增template.macros.palace_compact，公开显示真实选定实宫星/门/神及天盘、地盘和每个有序81格名称与吉凶极性；后台完整书原文、十二长生分支和源格仍由200格和81格原始源保留。Python+Swift角色证据用实际独立用神strength和真实克/生/被克等关系短句，内计分过程只保存在研发审计。普通/伏吟天显模板仍按真条件查，不虚构。
- 严格不得变动：V8 200格、81格原数据字节、原跨宫/同宫分数、坤二寄地源宫、天显半分合计一次向下取整、五不遇逐实宫-2、星门神源能量角色不重算。
- 公众读本只说古籍传统象意，不声称医疗诊断、病情预后准确或真实个人疾病。下一轮必须真实运行当前源码Python单测、Swift同一时辰原生全文逐字对照与macOS Xcode模拟器资源检查，分别记录结果与任何失败。

### 2026-10-28 · V10第一次CI/Swift对照真实失败，独立修复记录
首轮主CI #40783200978 的 tests/test_health_v80_disease_dual_sky_20261028.py 静态契约仍断言旧客户原文实现`let chosen=formation.sentences`，实际现已在`let names=formation.sentences.map`只截取真实有序81格名、极性，原81分数和source pair不变；已据真实代码改旧静态断言，原失败日志照留。
首轮V8原生逐字专项 #40783200831 真实Swift可编译、200格/原分与Python一致，朋友同一2025-12-28 17:00仍双方score=-5，但Swift customer由于先以`phrase("palace_compact")`解析含占位符的**原始模板**，在实际字段尚未填入时触发`WenguaNativeReadingError.invalidPhrase`；修复是先从macros取raw字串并在palaceText绑定完整九宫源事实再检查占位符，不能放宽最终严格校验。失败原始Swift stderr和日志见docs/HEALTH_V80_FAILURE_RUN_40783200831_ATTEMPT_1.md。首轮真实macOS Xcode iOS simulator/四源资源验收 #40783200973 PASS，但对源码修复后的提交需重新验收。此次故障绝不以虚构汉字断词填补，完整Swift结果必须在后续CI真PASS后才交付。

### 2026-10-28 · V10最终同一时辰真Swift验收
最新commit 498cc54d 的 Python3.11/3.12正式V8 CI #40784209740 PASS，V8全源200/81真正原生Swift逐字核对 #40784209983 PASS，macOS XcodeGen真实iOS Simulator编译与完整App四资源/20261028 V10模板bundle验收 #40784209785 PASS。固定已见朋友盘2025-12-28 17:00 EST，四柱乙巳、戊子、辛未、丁酉，冬至阳遁七局；人物规则是已确认朋友用月干戊，艮八宫，年命未给不补，最终原V8 -5 极大凶不变。现在公众九宫只报星门神、真实天盘地盘、81有序格名吉凶与关键墓刑迫，去掉全部古文引号堆叠、多个十二长生并写、开发者口吻和每宫内部扣分；古书原文本/完整多支事实未改。原生Swift全文及对照归档docs/HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40784209983_ATTEMPT_1.md，1/1 EXACT MATCH，无差异。此前失败#40783200831/#40783200978的真实现场保留。不代表医疗有效性、签名真机或App Store上架。
