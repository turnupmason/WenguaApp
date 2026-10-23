# WenguaApp · iOS 专业九宫基础模板｜5 个全新随机时辰验收

- 状态：**计算及数据契约层验收完成 / BASE TEMPLATE ACCEPTED**
- 验收时间：2026-10-22（America/New_York；GitHub Actions 以 UTC 记录）
- 对应代码提交（测试运行）：`28d48e81edc1b6004824b6f10adfa8f96040f1ae`
- GitHub CI：https://github.com/turnupmason/WenguaApp/actions/runs/39886204311
- 五盘完整资料（原 Python 源结果、Swift 实时计算 JSON、结果报告和拒绝样本记录）：https://github.com/turnupmason/WenguaApp/actions/runs/39886204311/artifacts/12472846851
- 旧四张原书审计盘按原样保留，本次的五个时辰绝不来源于旧四盘。失败测试及历史 CI 不得删除。

## 选择原则

从 2027 年的 1、3、5、8、10 月五个不同月份，使用 `random.Random(20261022)` 对月内有效日期、奇数整点时辰抽样；采用 `America/New_York` IANA 时区与真实夏令时偏移。节气临界（原本未核准的近界）、23:00 晚子时、时门中五无可靠寄宫解法时，按照原书／既有引擎拒绝并记录原因，不猜测。五个样本均首次抽中有效时辰，**拒绝候选 0 个**。同一算法可重复再生成同一批测试输入，非人工指定阳遁／阴遁局。

## 五张新盘的真实计算事实

| # | 本地时刻及 UTC offset | 四柱（年 月 日 时） | 节气 | 遁局 | 旬首 | 值符／值使 | 空亡 | 时马 | 天地入墓 | 长生逐支事实 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| 1 | 2027-01-20 19:00 -05:00 | 丙午 辛丑 己亥 甲戌 | 大寒 | 阳遁9局 | 甲戌 | 天蓬星／休门 | 申酉 | 申 | 3 | 26 |
| 2 | 2027-03-18 05:00 -04:00 | 丁未 癸卯 丙申 辛卯 | 惊蛰 | 阳遁1局 | 甲申 | 天冲星／伤门 | 午未 | 巳 | 1 | 25 |
| 3 | 2027-05-10 07:00 -04:00 | 丁未 乙巳 己丑 戊辰 | 立夏 | 阳遁7局 | 甲子 | 天柱星／惊门 | 戌亥 | 寅 | 4 | 26 |
| 4 | 2027-08-16 07:00 -04:00 | 丁未 戊申 丁卯 甲辰 | 立秋 | 阴遁2局 | 甲辰 | 天柱星／惊门 | 寅卯 | 寅 | 0 | 26 |
| 5 | 2027-10-09 17:00 -04:00 | 丁未 庚戌 辛酉 丁酉 | 寒露 | 阴遁3局 | 甲午 | 天英星／景门 | 辰巳 | 亥 | 0 | 25 |

注意“天地入墓”记录真实触发数量，而不是评分；0 项必须显示为无已核定入墓，不能凭空补一个“墓”。

## 实际执行与验收结论

经 `.github/workflows/ios_native_cast_parity.yml` 自动执行：

1. 原有四张基准盘同时通过 Swift 与封存 Python 基准比对，未重写历史原书案例。
2. `tests/test_ios_five_random_live_casts.py` **当场生成** 五个新时辰及 Python 原算法期望值；不是硬编码四柱，更不是把固定 JSON 假装为 Swift 计算。
3. Swift `WenguaNativeCore.compute(at:timezone:)` 对五个 ISO 时刻重新起盘，CLI 逐项校验原 Python 的四柱、阴阳遁／局数／元／符头、节气、旬首、值符、值使、空亡、马支、值符值使落宫、天盘／地盘干、八门、九星、八神、天芮天禽双星寄宫、十二长生、分天地入墓。
4. 汇总：**5/5 新时辰成功、45/45 九宫字段一致（40 个外围八宫）、128 条真实天地盘逐支十二长生、8 条真实天地入墓标记一致**。中五宫未伪造普通八神门星，不将无入墓强行标注。五局横跨阳遁 3 例、阴遁 2 例。
5. 同一运行中的 Ubuntu Foundation 原生 Swift 编译及 macOS Xcode iOS Simulator **正式构建均成功**。这不是仅仅 `swiftc -frontend -parse` 的语法检查。
6. HTML 和 SwiftUI 原有契约测试覆盖标准九宫顺序 `巽4 离9 坤2 / 震3 中5 兑7 / 艮8 坎1 乾6`、四柱四等宽、节气与遁局独立显示、神星门天/地干、五行符号专属颜色、九宫内空马墓及长生可见、点击完整宫位详情。**本次五盘校验的是事实数据和源码/编译合同，不是用五张真机截图证明字号适配**。

### 验收边界 / 冻结决定

**基础专业九宫排盘模板的计算和数据契约可以结束本轮开发，后续所有问事领域复用同一套，不为每个领域重复发明排盘规则。** 

- 不变更 `src/wengua/astro_calendar.py`、`src/wengua/casting_shenqi.py`、`WenguaNativeCore.swift`、封存的四盘、194原书案例、43章账本、81原书有序天地干、42疾病补充、17复合格局或失败记录。
- 自动起盘不等于每个专题的**用神身份选择、正反证据、条件权重、成败/应期、古籍引用和完整自然中文断词**已经移植。iOS 新盘的 V3.9.1 专业离线断词仍未完成；不恢复 V4.2 健康分数或概率。
- Xcode Simulator 编译通过不等于用户的 iPhone 真机截图已核对、AppIcon / TestFlight / App Store 已交付。真实手机视觉可读性需在 Mac/Xcode 本地复看。
- 下一阶段：以领域 `domain` + 细分意图 `topic.id` 为独立脚本入口，搭建**同一九宫结构+多专题模板路由**；每个专题独立明确定义取用、条件、反证、应期、完整原书证据链，然后依照同样真实五盘/历史独立家族验收，最终逐个启用。未完成的专题保持禁用，不得借用疾病轻重模板。

## 可重复运行

```sh
# 仓库根目录，具备 swiftc、Python3
swiftc ios/WenguaAppUI/WenguaNativeCore.swift \
       ios/WenguaAppUI/NativeParityMain.swift -o /tmp/wengua-native
python3 tests/test_ios_five_random_live_casts.py \
    /tmp/wengua-native /tmp/wengua-five-report

# Mac 上还应做一次真实 Xcode iOS Simulator 编译
cd ios/WenguaAppUI
xcodegen generate --spec project.yml
xcodebuild -project WenguaApp.xcodeproj -scheme WenguaApp \
    -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build
```

本仓库所有文档须以当前 GitHub Actions 真实成功记录为依据，不能用“开发中/在验证”混淆已通过内容，亦不可将本次结论外推为占卜断词的现实准确性证明。
