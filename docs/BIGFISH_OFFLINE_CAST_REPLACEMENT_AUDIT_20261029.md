# 2026-10-29 用户改用 BigFish 排盘 · 本地离线 V8 批处理与 Swift 迁移边界

## 用户新明确指令（高于先前 qfdk 方案）
弃用本轮才创建的 qfdk 起盘试验作为新生产方案，**选用** [perfhelf/bigfishmarquis-qimen/src/engines](https://github.com/perfhelf/bigfishmarquis-qimen/tree/main/src/engines) 为后续排盘的原始来源。原 qfdk 文档和历史失败留在 Git 审计轨迹，不删除历史。当前仍只做**时家转盘 + 拆补法**，不能把仓库同时存在年家、月家、日家、茅山、置闰几个文件视作当前已经全部验证/接线。对应产品冻结 V8.0 病情轻重和 V10.2 完整中文原断词、200格、81格、人物规则完全不修改。

## 上游实际代码审查
- 上游 `main` HEAD `6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c`，MIT（Copyright 2026 BigFishMarquis）；`src/engines/{shijia,shared,chaibuquju,maoshan,zhirun,rijia,yuejia,nianjia}.ts`。原仓README自述四层与三种时家起局、500+样本300年验证，**这只是作者声明，不等于本仓独立全部通过**。
- 真时家九宫原函数 `shiJiaGenerate(hourStem,hourBranch,juNumber,dun,fourPillars,solarTerm)`。拆补通过 `chaiBuJuByGanZhi(solarTerm,dayGan,dayZhi)` 获得局数后必须真调用 `shiJiaGenerate`。
- `src/engine.ts:handleShiJia` 茅山与置闰分支有基础盘时只覆盖 `juNumber/dun/yuan/juMethod` 字段，不重排九宫；本工程不能把它当完整重新起盘。没有核准交节精确参数前本地版拒绝触发这两分支，不默认套拆补。
- `shijia.ts` 组装字段**语义反转**：源码明确 `skyStem: eStem` 为实际**地盘干**，`earthStem: hStem` 为实际**天盘干**。适配器必须逆字面解读，否则将81有序格反过来。
- 天芮与天禽：`jiGanStem` 来自中五真实地干，寄在真实天芮的外宫，与天芮天盘携干**分别**组成有序天地格；不能把中五造普通九星门八神。
- `shijia.ts` 的门迫注释说“宫克门”，判定 `wxRestricts(dElem,pElem)` 实际是“门克宫”；原源 `marks` 不可无核便替换 V8 自己的门迫核算。源 `kongWang`、隐干支、地八神须独立对照现行所需事实。
- 真实节气/四柱不是从 `shiJiaGenerate` 内部自动生成：其必须作为外部可信输入。Mac 先复用冻结 Wengua 公历历算作为时间输入，不等于新 TypeScript 单独验证了全部历法/DST/节气交节秒差。

## 已经做的 GitHub 工程与验证
- `scripts/verify_bigfish_upstream_1080_20261029.cjs`：**实际原始 TS**（不是重写 JS 伪实现）的2阴阳×9局×60合法时柱=1080基础盘式结构逐盘核查；检查9宫唯一，中五无普通星门神，8个星/8门/8神及9地干唯一，天芮天禽携中五真干，不捏造月令年干。单独验证 `2026-10-23 庚午日/霜降` 的己巳符头为中元，拆补阴遁八局。上游茅山偏移122h的中元局数合同也单列。
- `.github/workflows/verify_bigfish_upstream_20261029.yml`：固定 `6112b39` clone 上游、TypeScript 5.8.3 编译原源码、执行上述1080真实 TS 测试；**第一轮正式 GitHub Action #40920402953 PASS**，相同 SHA 的现行 V8 主CI #40920402788 PASS。注意这是1080结构合法性，不是所有1080种四柱历法与 Swift 真实盘全字段同结论。
- `scripts/bigfish_shijia_cast_bridge_20261029.cjs`：真正 `shiJiaGenerate`+拆补起局 JS 调用；`scripts/verify_bigfish_frozen_v8_samples_20261029.py`：对2个真实公历时辰做 TypeScript九宫→源字段规范→**新物理盘作为唯一病情 V8 阅读输入**，旧 Shenqi 只在对照中记录，不偷换；自动化工作流已增加该步骤，未见独立运行结果前不可称通过。
- 本次对用户 Mac 提供新的 `WenguaBigFishLocal_20261029.zip`（SHA256 `22e23867e9424273109f8f7da1a1917151bff4fee7b35b360ab7f0453f09b2c7`），不是旧 qfdk ZIP 的原位改名；含首次联网 Git clone 固定上游并 tsc 编译的 install.command、Node TS实际调用 bigfish_cast.cjs、可本地持续 SQLite checkpoint 的 Python local_batch.py、中文说明和5个合成边界单测。冻结四源 JSON/TSV 首次下载并 SHA256 固定验证，后续本地无需互联网。原盘JSON/差异JSON/文本候选/SQLite均可保存；尚未用户 Mac 实跑真实全链，不自动批准上架。Python unittest 5/5 PASS、Node --check / py_compile / bash -n PASS、zip unzip -t PASS；这些**不是**真实上游 V8 全文对照。
- 本轮未改 `ios/WenguaAppUI/WenguaNativeCore.swift`，也未发布新的 Xcode 编译/资源/真机验收；**iOS 原生生产起盘还未替换**。要真正“把我们的换成它”必须将 BigFish 的真实时家算盘语义移植或确定性绑定至 Swift、充分验证、在用户批准新盘流派差异的边界内切换生产路由，再执行 macOS Xcode Simulator 全量实机编译/断词校验。不能把新 Mac 起盘成功混称 iPhone Swift 已切换。

## 后续严格操作
1. 先把新 TS 两真实钟 V8 合断的实测 Actions 结果归档；必须保留差异和失败。
2. 按实际新盘列举现有 Wengua 原始200/81/真假空/马墓刑迫/同宫双星/值使寄坤、伏反吟、天显五不遇、人物年命入口所有欠缺，逐条映射，绝不按宫净分替代独立用神力量。
3. 正式将新九宫数据进 Swift 之前，做全字段100%对照并对两冻结旧案严格标注新旧起盘变体。未经用户同意不追求旧病况分数结果而偷改 V8。
4. 用户所说的四柱直积518400为标签组合上限形式，不全是可达真实公历四柱；月干受年干、时干受日干约束。只对可实现的真时辰、真月令、人物条件批量生成并标明未审状态。


## 2026-10-29 实测失败与修复追记（保留全部原始证据）

**首次真实跨仓断词复核暴露旧来源保护门槛，不能把工作流绿灯当成真正的模板成功。** 在 #40920875955，1080个原始 TS 物理结构全部 PASS，但 Python 跨仓步骤失败：`health_severity_template.py:_validate_chart` 的真实策略首先要求 `status` 为旧 Shanqi 状态，并**重新调用** `layout_from_explicit_bureau` 对星门神和携干逐字段比较；BigFish 不同起盘来源不可能不经许可直接穿透它。该工作流最初使用 `python ... | tee`，没有 `pipefail`，造成该步骤 Python traceback 而 workflow 错报 success。#40921332503 改 `set -o pipefail`，**正确 FAIL** 并保存了原始失败；不删记录。

为真正让**BigFish 新盘**进入冻结规则而不把旧 Shenqi 盘偷偷喂给 V8，新建 `src/wengua/bigfish_source_gate_research.py`：
- 仅 Mac/CI **单线程研究候选**，具有 `source_key=perfhelf/bigfishmarquis-qimen@6112b393...`、`casting_variant=bigfish_shijia_chaibu_pilot`、状态 `bigfish_unapproved_candidate` 的实体盘才允许临时验证。
- 全宫独立检验 9真地干、天芮天禽双星携干、八星/八门/八神唯一、中心五不伪造门/神/天星、旬首六仪、局数/时干等。上下文作用域只临时替换 `health_severity_v22._validate_chart` 的**旧Shenqi来源身份核查**，退出后恢复原函数。它不修改正式冻结的原版脚本、V8计分公式、200/81、V10.2模板、Swift及Important镜像；不能作为并发 App 发布路径或对完整古籍来源准确性的批准。
- 正式真实 GitHub Action **#40921478524 PASS**：原上游TypeScript 1080结构逐个0 errors；将实际美东 `2026-10-28T06:00:00-04:00`（丙午戊戌乙亥己卯）和 `2026-10-28T10:00:00-04:00`（丙午戊戌乙亥辛巳）用 BigFish **原始实际九宫**传到**未修改计分 V8 Python**，双盘均阴遁2局、对照旧九宫星门神携干差异列表为 `[]`，输出内部传统符号等级 -5/-5，客户文案 SHA256 分别 `9eba5f30331013c50e9da5b454aa81b267a5c5c6b04f15b816591d16bea43a42`、`b187047c6895f691986c5b19f74c1c42b82cb9b2ad96bac8f4791c627d9ff568`。不以同分宣称医学预测有效性。
- 现行正式 V8 CI 同一 commit #40921478534 PASS；历史独立 V7.4 仍有 #40921438290 FAIL（保留，非V8变更引起）。Xcode macOS完整编译与新Swift原生 BigFish 重构**未跑**，不能宣称 App 真正换盘完成。
- 最新本轮 Mac 可下载 ZIP 更新版 SHA256 `f7cbe0156494e26873e526c139518f455881f3c7a0b487afa7cc3a88baebdfbe`；替代上方最初首稿 SHA `22e238...` 的下载建议（两份历史哈希都保留）。新增 `candidate_source_gate.py` 同源研究安全路径，并将 TypeScript 编译器固定为5.8.3。Mac 完整源码 clone/多日期跑批仍需真实本机测试，不能以 GitHub 的2时辰代替。

**结论**：现已可实证原 BigFish TS 时家拆补排盘与现有 V8 Python 独立来源门槛共同工作，但正式 iOS 原生并未切换，独立未知盘中可能出现新旧流派差异；应继续带真实边界条件逐例审核。用户今后本地首次安装只用更新版 BigFish ZIP，勿再用 qfdk 首稿。
