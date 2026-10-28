# 2026-10-28 · 用户两张实机截图：首屏固定继续按钮与整齐可辨的九宫

## 事实和范围
- 第1张上传截图底部金色「继续 · 填写问事信息」仅露上部，源于 `ios/WenguaAppUI/WenguaDomainJourneyScreen.swift` 将按钮放在 `ScrollView` 最末，顶部云境固定222pt、列表逐项34pt内边距，导致按钮被Home indicator/当前窗口截断。
- 第2张实际九宫截图，`ios/WenguaAppUI/WenguaDesignPreviewApp.swift::ProfessionalPalaceTile` 宫名字号11pt、没有「宫」，天芮+天禽病宫双携干使原 `Spacer` 弹性堆叠不整齐，用神竖排又挤主内容。不属于排盘错误、V8计分错误。
- 用户冻结 V8.0 起盘、模板、星门神干力量和200/81计分。**此次只修改上述两份 SwiftUI UI 源文件，Python/Swift engine/模板/数据源完全未改动**。

## 修复
- 已选领域时将头部云境压缩222→152pt，题行上下内边距17→12，节间空隙22→14；金色继续按钮移入ScrollView的 `safeAreaInset(edge:.bottom)` 固定54pt整高，保留不可用领域禁用与原跳转，完整位于设备安全区上方，用户无需把屏幕拖到底才找按钮。未选领域原222pt视觉保留。
- 3×3方盘的每个宫名从11pt改16pt粗体，并附「宫」字；空亡圆圈、驿马原宫状态保持。每格固定清晰位置：宫名→八神→九星（天芮／禽同一行）→天盘干（统一38pt承载轨，丁在戊左且每真实星携干对应可访问）→地盘干（统一38pt轨）→八门。长辈／患者／医药等本次用神标签换紧凑右侧横排上下分列，不再逐字拉长一整列；正常单星与病宫双星占完全相同的行槽。 `palaceBoard` viewport预算预留274pt以保证九宫及首屏标题不被底部遮挡。
- 所有文本仅 `real.heavenStars` 真星真携干、 `WenguaPalaceIdentity.labels` 真落宫身份和原 `QFive` 五行颜色；`middle 5` 不添加普通八门、八神、九星。未重新解释81格或新创分数。
- 静态与布局边界测试 `tests/test_ios_first_viewport_palace_layout_20261028.py` 及现行 V8 Python主CI、Swift parity、真实 macOS XcodeGen iPhone Simulator `xcodebuild`/bundle四源均必须本提交重新验收。不把旧版本 Xcode PASS 当本次新版成功；真机外观/手动UI录屏需要设备验收。失败Actions全部保留。

## 现行规则声明
本轮严格UI-only；没有修改 Python/Swift native 引擎、source 200 cells、81格、 V8固定断词模板、领域选用神取证、条件赋分或用户历史原盘。保留所有AGENTS/PROJECT_STATUS/LEDGER/失败日志原文。
