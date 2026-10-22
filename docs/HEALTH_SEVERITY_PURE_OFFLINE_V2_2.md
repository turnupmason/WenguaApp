# V2.2 人体疾病/病情轻重：纯离线程序直接生成21段断词

本版只改用户批准过的病情轻重21段，其他四种疾病问事尚未经用户审核，绝不开放或提前开发。用户发了丙午年、戊戌月、戊辰月、壬戌时，第三“月”暂读成“日”；2026-10-21 America/New_York 19:30 真正离线历法匹配四柱，寒露上元阴遁六局。用户没给患者关系，按self/direct_self仅作假定试验，正式问事还须患者选择；无出生年命则不加年命。

## 用户可见文字硬规则

生产断词只能由 src/wengua/health_severity_v22.py 的 analyze_health_severity_v22 读取真盘、用户角色、源码象意表及本地SQLite原书索引，按 data/knowledge/phrase_library/health_v22/severity_template.json 每项纯Python format_map填空直接产生21段中文。不得用任何GPT、联网API或本地LLM再润色；不得手工在单盘输出后续写。相同输入与本地数据库必须字节级相同。研发时修改代码和模板可以，但要版本化重新运行全部测试。

用户段落必须是“实际宫星门神干+简短意义+传统问事作用”，对外统一“依据古籍”。不得出现「程序、数据库、规则库、尚未编码、待审核、模型、工程、无法实现、书源摘句、出处SHA、还要核对、例如」等内部讲法；任何unknown内部审计可存，但不混入面向用户的正文。天盘和地盘有序，壬加辛实际查询古籍概念索引第661行、完整SQLite语义记录第161行均引用的干克应命名螣蛇相缠，直接简短给出「纠缠难安」；不能读出原文后向用户介绍检索来源。

这张盘真实天芮震三宫（壬加辛、六合、死门，震木克天芮土，戌月天芮相）；日干戊离九宫（天心、开门、螣蛇）；乙奇巽四宫（惊门、太阴）；巽4惊门迫而不是震3病宫门迫。第19/21段必须综合病星旺衰、死门、壬加辛、病星受宫制约、患者宫不空、开门、天心乙奇有向关系；不许只因死门而宣称「无有利证据」，不把凶象吉象简单投票加总。若应期源条件不足，第20段只用正常中文「不定具体应期」并无现实病患死亡或康复日期。

## 可运行工程和质量关口

21段真模板：data/knowledge/phrase_library/health_v22/severity_template.json
严格离线引擎：src/wengua/health_severity_v22.py
真实四柱重跑：scripts/run_health_severity_v22.py
独立单测：tests/test_offline_health_severity_v22.py
增量迁移：schema/migrations/050_health_severity_offline_customer_language_v22.sql
append-only完整SQLite：scripts/build_health_severity_v22_archive.py
官方CI归档：.github/workflows/build_health_severity_v22.yml

测试有socket拒绝全部联网、源码禁止GPT客户端、相同盘两次逐字节一致、整21段无内部研发措辞、原书壬加辛可追溯、巽宫门迫不冒充病星门迫、病星受制和患者门星神证据不漏、不同患者关系真正重新取用、其它四问事拒绝。保留已有24因子unknown于内部审计，不能说全24项都实际计算了；软件绿灯不意味着用户传统断案验收通过。

父库V2.1完整194案及历史错误、14个人物关系、其它四个未审问事模板、古籍索引均原行不动。父库SHA256 25d95ed8df42ed0739d82cc930fcd5127ba187740c0b871fc3ae488d69bc81f3。V2.2从父库完整备份迁移050并保存独立SQLite/XZ/manifest，不覆盖旧库与此前失败数据。归档经真实CI通过才确定SHA与交付完成状态。用户确认这张盘的原样21段之前，所有其他疾病问事与后续领域开发继续冻结。传统象意不可当医学诊断或真实疗效依据，UI仍不开发。


第一次GitHub V2.2专项测试发现并保留两项失败：有向五行文字主语指代含混，以及直接把概念索引第661行当成SQLite源段位置，实际SQLite semantic_assertions.source_start_line为161。已改为明确「病宫木生患者宫火，患者宫得病宫生扶」等实名方向判断，并把两个来源行分别审计；测试亦保留正反证及无内部措辞断言。原始失败工作流历史不得删除。