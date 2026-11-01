# 2026-10-31 · 疾病「难受部位」V11 研究模板（未发布）

本次在现行 V8.0 病情轻重（原规则不改）、V11.2 真实人物/逐宫断词之外，独立新增 `health.discomfort` 候选模板。它不使用 V8 净宫分或十档吉凶代替身体部位，也不复制病情轻重原结论。

## 真实来源、对照与限制

- 《神奇之门》疾病章节结构索引 `data/knowledge/shenqi/health_prediction_ch01/method_index.json`，原章节 SHA256 `3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a`，原文5–7行八宫体表/体内候选、9行天芮/时干/伤门关联；原索引明确 `review_status=draft`，不伪称独立医学确认。
- 《开悟之门》 `data/knowledge/kaiwu/health_prediction_ch02_section01/method_index.json`，章节SHA256 `49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d`，王连明一案作者使用离宫、伤门/值符、诸宫组合。该历史案信息已见，不能冒充新盲测；不能将单一症例泛化为定位算法。
- 外部用户补充的8宫、10干、72干宫、8门、8神来源 `data/knowledge/health_discomfort/traditional_body_clue_candidates_20261029.json`，没有可核对的书章行号/来源hash，状态一直保持 `draft_unverified_external_notes`；仅显示为辅助传统候选，不把异常、肿瘤、手术类比当实际病名。
- 内外盘取舍、新旧病判断、独立复核、冲突优先级尚无全面通过的源条件，因此两路并存；不得伪造唯一诊断和精确应期。

## 可执行断词草稿

`data/templates/health_discomfort_v11/reading_template.json`：独立6段模板，先病位初象（两组候选），再天芮星本宫门神/携干/天禽/真实有序81格，再伤门和时干独立真实宫，V11人物主辅角色，最后合参与两句总结。`src/wengua/health_discomfort_template_v11_draft.py:compose_draft` 用真实九宫、中五无普通星门神、患者独立用神、实际时干和伤门；本地生成不触网。

模板是研究 draft：未纳入 `ios/WenguaAppUI/project.yml`、Swift iOS 发布 Router，`health.discomfort` 原本仍 `enabled:false`，不消耗用户30秒问卦后15天锁；未达到 Swift 和 Python 同盘逐字、原著条件及正式客户文案专业批准前不能开启。V8 200/81、天显/五不遇时、原断词、历史结果和用户反馈均未改。

## 测试及未决

`tests/test_health_discomfort_v11_draft_20261031.py` 检查双来源示例实盘（阳三丁巳天芮坎、阴八戊戌天芮艮）、朋友性别/年龄不影响月干、意图严格隔离、中心伪门拒绝、六段及双组、V8分数空、禁医学诊断和App关闭。以当前 main 最新提交 Actions 的真实运行结果为准；缺少 macOS 的执行环境不能宣称本轮已实际运行 Xcode。

下一步对两书定位规则逐条件和不同历史事件家族核查内外主客及天芮/伤门/时干多线索的优先级，明确可定/不可定门槛，再打包Swift逐字测试。本阶段新增原著章节0、历史事件0。

## 2026-10-31 · V11 难受部位模板 CI 与 Important 镜像验收
- 首轮主CI #41265404538 FAIL：新增字段校验将 Formatter.parse 的普通文字片段 None 误判为非法占位符，5项测试报错。保留历史失败，修复提交 d7a4cef6c4481e8d39c8ab860c09112fce7a9cf4 将检测改为仅判断真实字段名。
- 修复后的同一 V8 主CI #41265445681：Python 3.11、3.12 均 PASS（含新6段真实盘、双阴阳、朋友月干、缺中心拒绝、禁自动诊断）。这验证研究草稿可运行，不代表独立病位准确或正式 iOS/Swift parity。
- 新模板已加 Important 的 Python 和 Swift 双镜像，Python研究引擎与专项测试也留同字节快照，MANIFEST 的 Git blob SHA 同步。本模块仍 research_draft、iOS disabled，Xcode/macos 和手机对该新专题尚未实测，不冒称通过。

### 2026-10-31 · 新病位专题iOS安全门与构建核验
iOS `QuestionCatalog` 保持 `health.discomfort` 的 `enabled:false`，明确注释：定位模板仅draft、尚未Swift逐字以及源条件审核，不能消耗15天锁。Important Swift UI同字节镜像和MANIFEST SHA同步。本次仅更新UI的发布门说明，无新Swift病位断词引擎；本提交真实macOS Xcode模拟器CI结果须后验验证。#41265540427 主CI Python3.11/3.12 PASS；#41265540502 原V7.7 native PASS；V8 Native仍依本SHA实际结果。
