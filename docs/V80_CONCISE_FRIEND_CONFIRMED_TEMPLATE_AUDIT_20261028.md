# 2026-10-28 · V8原分冻结下客户V10文案精简与朋友用神事实审计

## 复现：先前已见随机一盘（不是未见盲测）
- 实际时辰2025-12-28 17:00美国纽约冬时；四柱乙巳/戊子/辛未/丁酉；阳遁7局。原生Swift/Python原始结果分档极大凶，完整原文在docs/HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40781030045_ATTEMPT_1.md；该盘已见，须只作版本对照。
- 原问题：health_dynamic_v21.bind_patient、WenguaNativeActorSource.bind均直接读actor_profiles.json；朋友当时kind=casting_month_stem正确，但JSON status=research_candidate_only错误地将用户确认的同辈月干标成待核。修正只改friend status/source/note，不动别的角色、实体或event_news下日干改用条件。
- 原公众文案：health_palace_detailed_vnext.render_complete_selected_palace及Swift palaceText直接把每个真实81格古文+古诀大意+天地取象整段贴给公众，天干长生字串长生/冠带/临官/帝旺/沐浴直接并列，五不遇明说每宫扣两分以及「按用户规则」等开发话术。用户明确要求全部改。
- 现在：新增template.macros.palace_compact，公开显示真实选定实宫星/门/神及天盘、地盘和每个有序81格名称与吉凶极性；后台完整书原文、十二长生分支和源格仍由200格和81格原始源保留。Python+Swift角色证据用实际独立用神strength和真实克/生/被克等关系短句，内计分过程只保存在研发审计。普通/伏吟天显模板仍按真条件查，不虚构。
- 严格不得变动：V8 200格、81格原数据字节、原跨宫/同宫分数、坤二寄地源宫、天显半分合计一次向下取整、五不遇逐实宫-2、星门神源能量角色不重算。
- 公众读本只说古籍传统象意，不声称医疗诊断、病情预后准确或真实个人疾病。下一轮必须真实运行当前源码Python单测、Swift同一时辰原生全文逐字对照与macOS Xcode模拟器资源检查，分别记录结果与任何失败。
