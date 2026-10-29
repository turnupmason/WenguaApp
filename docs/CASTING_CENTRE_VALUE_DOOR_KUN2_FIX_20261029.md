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
