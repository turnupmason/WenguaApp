# 2026-10-29：用户实机起盘失败 · 值使门行至中五未寄坤二

## 截图、原始根因、锁定边界
用户实机截图提示「本次未起局成功，也不会登记15天限制：值使门行至中五，除已校验例外外尚无可靠寄宫规则」。截图未附原始四柱，不能凭文件名编造时辰；采用可复现阳遁1戊辰、阴遁1己巳、阳遁2丁卯和真实日历新时辰验证。源代码 src/wengua/casting_shenqi.py 的 layout_from_explicit_bureau 和 ios/WenguaAppUI/WenguaNativeCore.swift 的 compute 先正确计算旬首起宫+所过时辰数×阴阳遁方向，若算到5仅允许 source5/steps0 已见例外，其余抛错，挡住完整九宫；App completeNativeCast 正确未写15天凭据。

## 证据等级
- 神奇之门源起盘规则 data/knowledge/shenqi/shijia_qiju/casting_rules.json 的 P10/P13/P14 原文行号分别60/64/96，68/72/102/184，102/143/184；原书整章 source_sha256=177f6ecba2bf4c165524a48adbdab8fdbd535cdb700dca12b5e5f29b1a75afb2，原来源状态并非新读扫描独立证明。
- 旧作者案例 1996-07-27 阴7 甲申中五，只有旬首0步原书旁证；非零数宫不能谎称原书已经逐案验明。
- 本次时家转盘同一寄宫口径参考：https://www.guyujian.cn/learn/qimen/07；https://exzh.net/96.html；https://bbscn-ly.luckerhome.com/article/webTopicPage/6/6016747.html。各资料表述值使逐时按1..9数、数到中五寄坤2、八门外圈继续随值使转。其它传承（例如奇门法窍随时令更使）存在差异，不将本项目当前时家转盘选择说成全流派公理。

## 此次修正精确范围
counted=((source_palace-1+elapsed*(阳+1/阴-1)) mod 9)+1，只有 counted==5，value_door_target=2；其他门位不变。随后由原来 host=(source==5?2:source) 到 target 作同一个外圈 [1,8,3,4,9,2,7,6] 8门旋转；中五仍无普通门/星/神，天禽随芮寄各自携干；原天盘星盘八神、真实四柱、节气局数均不改。失败起盘不会记15天，成功写完整九宫和断词且持久化成功后方登记15天。

## 验证及剩余
- 旧单盘 tests/test_casting_shenqi_chapter01.py 从「应阻挡中心」改为「实际寄坤」，历史原断言可从Git历史检索。
- 新tests/test_casting_centre_door_20261029.py 覆盖阴阳×九局×60时，共1080排列：实际数宫5应有120种，其他960不动；所有九宫正好8门/9星且中宫无普通门。
- 新tests/test_ios_centre_value_door_parity_20261029.py 在2026全年真实本地时辰抽取阴、阳各3个不同、非零值使数到5的实例，独立 Python 原盘与编译 Swift 真原生实际九宫各字段（天盘地盘、门神星、月令时支、空马墓、长生）完整比较，保存真实样本与失败日志。不能因模拟结构成功宣称预测准确。
- 原两书盘、此前四个完整盘、5盘随机、V8完整200格/81原文与冻结+3/+5/+1等疾病计分、V10.2客户模板全字没有更改。仍拒绝23点换日未核/节气±0.05°/1850..2150外，不为通关造旧盘或新原文。

**写入时未执行本轮Actions，不可预先宣称成功；在追加验收记录时以真实运行号为准，保留所有失败。**

## 实测 GitHub Actions 成败记录（2026-10-29）
- 最初完整修复源码提交 `eadacb00081d5fd51f9472274ee87eeca9ea273f`：真实 Python 3.11/3.12 主CI中新增的2遁×9局×60时=1080组合独立测试 **PASS**（120次直使数到中五，其余960无变化）；真正 macOS XcodeGen + Xcode iOS Simulator完整App编译及200/81/人物/V10.2模板包内资源 **PASS #40816857151**。首提交主CI #40816857169 FAIL、V8 native #40816857083 FAIL，是新修改的 `.github/workflows/ios_native_cast_parity.yml` 未同步 Python/Swift 两份 Important CI 镜像导致；全部原始失败已留存，非起盘算式失败。
- 第二次源码提交 `c909ebe988c72967cb04ef6606c5fc7beb4c5604` 补齐两份独立镜像（镜像SHA与canonical一致）和原生对照脚本中的可空horseBranch。真实当前 Python主CI #40817100051 PASS，V8原生Swift与Python的完整200格、人物、断词逐字比对 #40817100066 PASS，V7.7两个已见时辰原生回归 #40817100059 PASS。
- 此后小修对照脚本提交 `891de58f323fd2116fde2ff0b12196f98b767740`：Swift JSONEncoder不写入无值的马星、地盘墓星名；Python和Swift的真实字段按 `get(...)` 正常比较，无新源算法修改。Python3.11/3.12主CI #40817182166 PASS。真实 Linux Swift 编译 + Python独立生成的2026年非零中五时辰六盘（阳3+阴3）**完整九宫各字段、长生、空马墓、星门神等严格对照PASS**：GitHub Actions #40817182311 的 native_core 作业「Real center-valued door ... six actual Yin/Yang hours」步骤单项PASS，另「Five fresh reproducible random hours」原生源比较PASS，真Swift离线客户阅读检查PASS。全过程输出和两份九宫 JSON 已由工作流上传工件留存。
- **必须如实注明**：整个 iOS Offline Native Casting Parity 多作业 workflow #40817182311 整体仍FAIL。该native_core作业不是在新的中五对照失败，而是旧 `NativeActorProfileCheck.swift` 硬断 `idx.profiles.count==20`，当前正式包已按用户确认增加至22位含祖父母，抛 `WenguaCastError.invalidChart`（历史测试设计假设过时）；其它几个V7时期测试也硬断旧版长断词而FAIL。**不能因这项总体红灯声称新六盘原生对照失败，也不可把未跑的后续全部steps称为通过，更不该为旧测试改变冻结人物或V10.2断词。** 后续可在明确审计中修复这些旧版测试契约或拆出独立本版绿灯工作流。原失败工件/日志保留。
- 在此轮主用户问题中没有截图里的完整四柱及时间；上述6张实际测试盘对应该引擎缺口与阴阳双方，不捏造用户当时那一盘的九宫、分数或断词。本次修复不改变30秒静心、失败不登记15天、成功保存后登记的事务逻辑。重新安装最新App才能在手机看到修正。
