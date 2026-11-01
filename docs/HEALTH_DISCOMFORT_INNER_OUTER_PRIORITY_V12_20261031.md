# 2026-10-31 · health.discomfort 内外盘与优先级 V12 候选审计

## 结论与范围
用户给出的阴阳遁八宫表里映射已作为 **传统象意的确定性程序分支** 实现，不能等同于科学确认的真实部位、器官或病情。独立模块 `src/wengua/health_discomfort_inner_outer_v12_draft.py` 读取真实时家转盘九宫、唯一天芮、真实伤门、患者V11选中宫及时干宫；只允许8个外宫，中五不伪造神星门。程序主象由阴阳遁和天芮真实宫位决定，另一路表里候选完整保留，不改已经冻结的V8计分、81源表、疾病轻重断词。

## 原书中实际核到什么
- 《开悟之门》疾病章节原索引 `data/knowledge/kaiwu/health_prediction_ch02_section01/method_index.json`，章节源SHA256 `49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d`。第85行（单条来源SHA `c0ec0f318792a740ab74bfe2562991d6501267d7059428aa0ca0b40e7fdaf365`）明确对照阳遁坤二外盘与阴遁坤二内盘，并联合天芮携干、时干、伤门，而非仅凭一个符号断器官。第31行（SHA `7bd61f25f76160a6a1048bed8312c3226122875a5fa88713e65bd06258b97fb0`）写阴遁天芮离宫属内盘。两例均属于已知原书断案，不能充当独立盲测。
- 《神奇之门》人体疾病 `data/knowledge/shenqi/health_prediction_ch01/method_index.json` 原章SHA256 `3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a`，第5–7行包含8宫表/体内两个映射集；第9行是天芮与伤门、时干配合的候选规则。索引仍标draft，不能伪称两书每一处均已全面逐字再次核原本。
- **尚需原书条件核查**：用户给出的16种内外格是明示规则；书内已见案例可相互支持部分格，但尚未证明所有宫+所有流派都具有疾病定位实证能力。天盘显性/地盘隐性、单个门神必须取表/取里的所谓绝对规则、72干宫细病和固定生死门槛，不应写成已获原书批准的通用医学规则。

## 实现的优先级
1. 病星天芮唯一真实落宫，按阳遁1/8/3/4为内、9/2/7/6为外；阴遁相反。主导 **古籍体表/体内类象选择**，不是实际病灶诊断。
2. 天芮真实天盘携干独立读取，天禽携干仍独立；地盘干只作为另一个物理盘层/81格事实，绝不直接当病因或慢性损伤证据。干宫细象仍是未核外部资料。
3. 伤门、死门、杜门、白虎、玄武、螣蛇、戊己、壬癸各记录有条件的表里偏向，符合首层记印证，反向记冲突；**不把一个门或神一票否决首层内外盘**。特别保留内盘白虎或外盘死门/玄武这些冲突实盘。
4. 时干及伤门取各自真宫，人物按目前V11的实际亲友、长幼、年干/月干/时干和有条件乾坤绑定，不把代测者日干假作患者主用。多角色同实宫保留身份但不重复算一宫。
5. 医药克病、患者入墓、空亡和病势结论属于独立V8疾病轻重领域；不能以此在“难受部位”直接断“特效药必愈/必死/无生命危险”或任意诊断。

## 数据和测试
- 规则数据：`data/knowledge/health_discomfort/inner_outer_priority_policy_20261031.json`。
- 引擎：`src/wengua/health_discomfort_inner_outer_v12_draft.py`；读取旧研究原始候选的 `inspect_traditional_body_clues` 仍保留原字段，向前兼容。
- 组合器：`src/wengua/health_discomfort_template_v11_draft.py` 与 `data/templates/health_discomfort_v11/reading_template.json` 的6段书面断词只改该专题。原表里候选会出现在前文，但只按真实内外主象给方向性总结。
- 回归：`tests/test_health_discomfort_inner_outer_v12_20261031.py` 检验16种阴阳宫分类、实际阳/阴坤二相反、1080实盘及有相反象意时不覆盖、中心伪用神拒绝、iOS禁用。现行V11研究测试同步，Important Python/Swift JSON镜像与MANIFEST blob SHA同一版本。
- 发布门：`ios/WenguaAppUI/WenguaDesignPreviewApp.swift` 中 `health.discomfort` 保持 `enabled:false`，Swift独立专题断词未实现，不使用30秒/15日发布交互。

## 真实失败历史和后续门槛
开发中中间提交主CI因新模版「确诊」的否定句触及既有测试黑词，以及 Important 镜像尚未同步，发生过失败。已针对文本与镜像做后续修复，失败记录留在 GitHub Actions，不可声称这些旧run成功。最终Python、Swift native与macOS Xcode只能按实际已完成的对应SHA和运行ID报告；现行V8原生逐字一致测试**不等于**本新专题Swift和Python逐字通过。
下一步：两书更多原始反例、天盘/地盘门干由表转里的明确原书条件、数个不同人物的多证据定位对照、原书未见家族的事前验证，再完成正式Swift独立模块的相同输入逐字回归。来源无条件时不造唯一器官。新增古籍章节0、独立历史案例0。
