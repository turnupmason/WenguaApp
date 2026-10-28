# 问卦 iPhone · 接卦优先的专业阅读界面
日期：2026-10-28。只改 iOS 展示，不新建起盘引擎或计分口径。

## 主要信息层级
1. 选择领域与细项、问事人 → 真实时辰 → 30秒静心、同事项15天限制 → 离线起盘与V8断词。未验收其它领域仍标开发中。
2. 默认「接卦」：紧凑四柱、局数节气、真实九宫；金黄木绿水蓝火红土棕逐符赋色。每个真实宫右上角用🐎代表真实时马、用空心圆代表真实旬空；同时成立均显示。不伪造中五普通神星门。墓、角色、天地干与宫详情可查。
3. 九宫下深色大卡「接卦语」：只能从本次 `WenguaNativeCustomerReading.sections` 的 `90_review` 最后一段拿现有结论，从 `91_timing` 拿现有时空应期提示；不再次计分，不用历史案例替代。完整免责声明在专业解盘保留，简版在卡片底部。
4. 「专业解盘」：所有 `WenguaNativeCustomerView` V8完整正文、用神、克生证据、限制条件、应期及全九宫真实源事实一字不改。历史记录打开采用同样标签、可点宫详情。
5. 所有数据仍本地，无虚构订阅入口，不作医疗预后或临床建议。

## 工程与验收
- 主界面 `ios/WenguaAppUI/WenguaDesignPreviewApp.swift`。
- 只读展示 `ios/WenguaAppUI/WenguaPremiumReadingView.swift`。
- `ios/WenguaAppUI/project.yml` 已列入新Swift文件。
- `tests/test_ios_premium_result_ui_20261028.py` 静态UI源契约；主CI已添加。
- Important 的UI镜像/MANIFEST Git blob SHA 同步。
- 提交 iOS 源后 macOS 工作流 `.github/workflows/ios_v80_xcode_simulator_build.yml` 必须再实际通过XcodeGen、xcodebuild、4项打包资源验证；不拿旧成功代替新成功。

## 冻结与待核
时家排盘、200表、81格、V8评分、Python/Swift段落、关系绑定、两固定盘不变。旧失败留存；尚未签名真机、App Store、逐机型手工点击或订阅系统验收。
