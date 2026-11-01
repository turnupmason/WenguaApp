# 2026-11-01 · 健康难受部位 V14：255条综合古籍证据表归因与反例审计（独立研究未发布）

## 实际读取范围与源指纹

用户本轮上传 Excel「奇门古籍测病规则证据总库_255条_20261101.xlsx」。已用 artifact_tool 实读其四个工作表，原文件 54,678 bytes、SHA256 `19d199a42f306d2855709a8f19979bea22e24443053e2d79e75fe89fddb6d00c`：

| Sheet | 行（不含标题） |
| --- | ---: |
| 古籍规则总库 | 255（HLT-0001～HLT-0255，无重复编号） |
| 组合精选 | 62（主库摘录索引，不能再算62条新规则） |
| 实战与反例 | 12（S01～S06、K01、K02A/B、K03A/B、K04；S02=K02B同一事件） |
| 异文与冲突 | 20（C01～C20） |

255主行证据标签：A原书明确142、B原书案例16、C跨条文推导16、D跨体系引用69、E整理推论12。标签是**用户Excel自述来源等级**，不是代码已经逐条校对原本、原书所有卷章或影印校勘。43主行来源链接为空，255行「上下干方向」列实际全空；因此对有 `庚癸`、`癸庚`、`壬丙` 之类连字组合，不允许自动认定天空加地盘、地盘加天盘或双天盘携干。真实上下干仍必须以现有 `for_real_palace` 有序81格及实际宿主恒定原盘为准。

这次**没有声称已把255行全部结构化上传至GitHub**：完整原表在本次上传文件及同字节源哈希索引；在对话交付另外生成保持四表原17/14/9/6列内容的JSONL ZIP供独立验收。GitHub现存 `workbook_255_v14_ingest_manifest_20261101.json` 为总表元数据、`cross_text_16_location_candidates_v14_20261101.json` 为16条风险隔离候选、`book_cases_12_conflicts_20_v14_20261101.json` 为12例/20冲突索引，而非伪造全量255已批准来源。

## 读了此前有哪些，新增哪些

- `data/knowledge/shenqi/health_prediction_ch01/method_index.json` 先前已经有8宫体表/体内主图，原章SHA256 `3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a`。
- `data/knowledge/kaiwu/health_prediction_ch02_section01/method_index.json` 原章SHA256 `49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d`，例二A/B论病原文第85、87、89行对应 source_sha `c0ec0f318792a740ab74bfe2562991d6501267d7059428aa0ca0b40e7fdaf365`、`94acd3cdcbdb4db20d92209f912cbaf497815d60db3e413d0e67905c5cd511a0`、`e8110fd62252f520744c626980017f4555f956feb8fe0df23ac17d80edd74c0b`。其中A：阳遁坤二外盘，病芮携庚、时干癸；B：阴遁坤二内盘，病芮携癸、时干庚。各自用月令、人物与条件年命/乾艮辅宫作传统解释，不是相同病名。
- `data/knowledge/health_discomfort/traditional_body_clue_candidates_20261029.json` 已含八宫、十干及72干宫、八门和八神；V12阴阳内外和V13上中下/主辅干角色原来已实现，不能再次重复录入成并列的多个独立证据。
- 新补强：**文本家族隔离与跨体系异文、十六个跨条文候选严格查真实方向、同一物理象意只算一条独立线索、缺页码hash阻断自动批准、原书对照事件家族去重、已知诊断和书后反馈不可倒灌**。病位的多候选未排除时必须分叉，不能因为凶门/宫分极大改判唯一器官。

## 已外部实际核对的两处典型原句

1. 《三命通会》卷七「论疾病先知五脏六腑所属干支」两段已在 ctext、识典古籍、维基文库互证。天干脏腑对应、另套体表部位歌和五行左右上下皆为**命理体系**资料，不是时家转盘的独立评分源。链接：https://ctext.org/wiki.pl?chapter=548506&if=gb&remap=gb
2. 《奇门法窍》卷二干支星门问答中，兑金克伤门、兑金克杜门的文本，以及木旺金衰/金衰木旺在同段互相冲突的「凶吉」表述，已实际查到公开原文。冲突 C13 **不可把相反判断吞掉或随意调V8**，只能等待版本比对。链接：https://shuyuan.zhiming.life/read/奇门法窍/10
其余如《奇门遁甲秘笈大全》《统宗》《新述》《元灵经》《医宗金鉴》表内A等级不因为这两处抽核就升级源审核状态；先保留为带来源待核候选。不同古籍同文转抄不算独立校验。

## 关键反例与操作界限

- K02A阳九局坤二外 vs K02B阴七局坤二内：**真实宫位、门神可相同而遁别、携干、天地盘有序格、月令、人物和年命不同**；不能以「病星坤二＋死门＋值符＋午未空」推同一病位与预后。B案同S02为1996年7月27日父亲同一事件，应同一event_family计一次；两例均已知反馈，不是真实盲测。
- K04已知视力下降及医院怀疑头部问题，作者使用离/乾等多宫解释，不可用结局反推「坤死门空亡无肿瘤」的普适医疗公式。
- K01在起盘前已知相关鼻部病史，作者原书相应断法可做文化规则演绎，但不能宣称独立预知病名。
- S06壬与丙或K02及其他多干同宫：不同独立天芮/天禽携干必须分记；即使不同体系同名五行给出两组，也不能按同一符号重复计票。真正`heaven`/`earth`有序顺序或`tianrui`/`tianqin`身份不详时必须等待明确源证。
- 12已见案例的「起盘前已知信息」和「反馈」单独存，所有资料由Excel归纳，未把任何案例提升到新独立盲测集。
- 传统疾病、死生、妖灵、择药和手术象意仅留文献研究，不诊断癌症、不能指导临床治疗，也不将古籍生死断法与用户现实健康结果等价。

## 新代码与回归边界

- `data/knowledge/health_discomfort/workbook_255_v14_ingest_manifest_20261101.json` 源指纹+四表结构+标签数+缺失记录。
- `data/knowledge/health_discomfort/cross_text_16_location_candidates_v14_20261101.json` HLT-0240～HLT-0255，16条C跨条文推导保持不同身份。其中只有六条单一确定天芮携干+同实宫唯一门的组合可以生成 **research_only** 匹配；多干/门神同时出现且上下干方向没核的，`unresolved_ordered_two_stems` 不执行。
- `src/wengua/health_discomfort_cross_text_v14_draft.py` 和原 `health_discomfort_template_v11_draft.py` 相接，输出审计字段 `v14_cross_text_research`，原六段中文结论不受未核候选更改。`distinct_independent_confirmations=0`，禁止多票当医学确定。
- `data/knowledge/health_discomfort/book_cases_12_conflicts_20_v14_20261101.json` 留历史案例/重复家族/20类冲突；不是新病例，案号不能全部当独立家族。
- `tests/test_health_discomfort_cross_text_v14_20261101.py` 测源数、双天地干顺序、完整1080真实布局、历史反馈挡闸、独立证据不能重复、旧版不改；CI `.github/workflows/ci.yml` Python3.11/3.12。
- Important Python真源/引擎/测试镜像与 Swift research JSON镜像、MANIFEST SHA同步；V8病情轻重正式Python/Swift保持冻结。iOS `health.discomfort` 仍 disabled；没有V14新专题原生Swift逐字交付，不消耗15日锁。

## 失败历史和未完成

初次主CI有 V12、V11 Python源镜像未同步及早期 V14 研究测试变更阶段的失败，历史run不删；所有文件与重要双镜像修复后须以相同commit的真实Actions结果为准。旧综合V7离线原生Parity尚有历史失败，不同于此次V14对客验收。

下一步按照用户Excel本身的来源链接，分批逐条核原书的逐版原文段、成立/反条件、方向事实（必须确认天地顺序及天芮/天禽身份）、来源家族重复关系；跨体系命理不自动移植到起盘领域。来源和病例未核时保留多候选，不追求每张盘唯一器官。未添加新原书章节或可用秘密盲测例，任何古籍历史断语不能作临床医学证据。
