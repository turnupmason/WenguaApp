# 2026-10-28 · UI-only Xcode 编译修复与可打开的 iPhone Simulator

## 用户边界（最高优先级）
**软件展示/资源调用 ≠ V8.0 模板/起盘/计分算法修改。** 本轮只修编译器错误、拆分SwiftUI视图并提供本地Mac模拟器启动入口；不改源200格、81格、人物规则表、V8固定模板、疾病评分、九宫起局及古籍内容。屏幕力量只能查现有200格/原神五关系事实，不增加计算体系。

## 实际失败与复现
- 原UI版基准 SHA `8d9357b4`，macOS GitHub Action [#40747800998](https://github.com/turnupmason/WenguaApp/actions/runs/40747800998) 实际 FAIL：`ios/WenguaAppUI/WenguaPalacePowerDetail.swift:84` 原字符串两行拼接语法 `expected ',' separator`、`'+' is not a postfix unary operator`；同源 `line 51` 五张SwiftUI卡塞在同一表达式中触发 `compiler unable to type-check this expression in reasonable time`。失败日志已归档 `docs/IOS_V80_XCODE_FAIL_RUN_40747800998_ATTEMPT_1.md`，永久保留。
- 独立 UI-only 编译修正 commit [`a8dead6c`](https://github.com/turnupmason/WenguaApp/commit/a8dead6c3971e8491e311f9b34990768fab22417)：拆成 `doorCard/deityCard/starsCard/heavenStemsCard/earthStemCard`，单独拼出十二长生文字，不改任一 `sourcePower/doorMonth/starMonth/deityPower/stemPower` 数据调用。Swift源与 `Important/swift/ui/WenguaPalacePowerDetail.swift` 字节镜像+Manifest SHA一起提交。
- 新源实测 Xcode/macOS [#40749467216](https://github.com/turnupmason/WenguaApp/actions/runs/40749467216) **SUCCESS**：XcodeGen生成项目、真实 iOS Simulator xcodebuild、App可执行文件及随包 `health_energy_200.json` / `81_pairs.tsv` / `reading_template.json` / 22个人物 `actor_profiles.json` 全部 PASS，工作流自动添加 `docs/IOS_V80_XCODE_PASS_RUN_40749467216_ATTEMPT_1.md`。Simulator App artifact ID `12843257658`，构建日志artifact `12843402352`；**未签名模拟器App，不是真机签名或App Store包**。
- 同源 V8 Python3.11/3.12 主CI [#40749467530](https://github.com/turnupmason/WenguaApp/actions/runs/40749467530) PASS。iOS UI改动只是读取源事实的显示层，不能推断医学准确性。

## Mac用户打开
在已安装**完整Xcode、iOS Simulator Runtime和XcodeGen**的Mac上，在仓库根目录运行 `./scripts/打开问卦模拟器.command`（Finder也可运行脚本）。其生成本地 Xcode 工程、选可用 iPhone Simulator、独立构建、核查四个打包资源、安装并启动 `com.wengua.ios`。需要首次安装 XcodeGen 可运行 `brew install xcodegen`。没有Xcode/Simulator的机器不能将未签名 iOS .app 当macOS .app双击运行。脚本不访问云端规则、不覆盖用户个人历史、不修改Python/Swift计分源码。
