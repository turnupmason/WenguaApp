# 问卦 iOS｜Mac 本地开发、模拟器与 App Store 准备

> 本文针对现有仓库 `turnupmason/WenguaApp`。**不要在 Xcode 中新建一个空项目去覆盖当前 Swift 引擎**；已有 `ios/WenguaAppUI/project.yml` 和 `WenguaNativeCore.swift`。
> 官方兼容表 https://developer.apple.com/xcode/system-requirements/ ，随本机 macOS 版本选择可运行的稳定 Xcode。Apple Developer Program 详情 https://developer.apple.com/programs/ 。

## 首次准备

1. Mac 苹果菜单 → 关于本机，确认 macOS 版本、可用存储和 Apple ID。
2. 从 Mac App Store 安装兼容的 **Xcode**（https://apps.apple.com/us/app/xcode/id497799835）；首次打开安装开发组件和 iOS 模拟器运行时（Xcode Settings → Components）。
3. 安装 **GitHub Desktop** https://desktop.github.com/ ，登录用户自己的账户，**Clone → URL** 输入 `https://github.com/turnupmason/WenguaApp`，选择 Mac 本地实际保存目录。不要仅从 GitHub 网站下载单个 Swift 文件，也不要丢弃 Python 源数据和历史失败记录。
4. 终端安装 Homebrew（若尚未安装）：https://brew.sh/ ，然后 `brew install xcodegen`。
5. 打开终端 `cd <你的本地 WenguaApp 路径>/ios/WenguaAppUI`，执行：
   ```sh
   xcode-select -p
   xcodebuild -version
   xcodegen generate --spec project.yml
   open WenguaApp.xcodeproj
   ```
   若尚未指向完整 Xcode，可执行 `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`，再重试。
6. Xcode 顶部 Scheme 选择 `WenguaApp`，运行目标选 iPhone Simulator，点击 ▶（或 Command-R）。若 iOS simulator 无设备，Xcode → Settings → Components 下载 simulator runtime，并在 Window → Devices and Simulators 创建模拟设备。
7. 生成的 `.xcodeproj` 是 XcodeGen 的派生产物；**修改 `project.yml` 及原 Swift 源码，不要新建平行项目替代它**。在 GitHub Desktop 查看 Diff 后 Commit，Push 到现有 main，或者先建 feature branch 经 CI 验证后合并。

## 真实 iPhone 与签名

用 USB 或无线配对连接 iPhone；手机首次开启 Developer Mode，并在 Xcode → Settings → Accounts 加入 Apple Account。Xcode 的 Signing & Capabilities 选择自己的开发 Team；免费 Apple Account 可做有限的自用设备测试。上架、TestFlight、App Store Connect 需要 Apple Developer Program（美国通常 $99/年）。正式发布前还需唯一 Bundle Identifier、正式 AppIcon、隐私政策、权限用途说明、商店截图、年龄分级、数据安全及传统文化/非医学诊断披露，Archive → Distribute App → App Store Connect → 审核。

## 两种真正的排盘时间（仅 iOS 原生）

- `按当前时间起局`：30 秒静心完整完成后，**按下最终确认** 时的本机 `Date()` 与 `TimeZone.current.identifier` 计算。不会偷偷使用之前显示的测试时刻。
- `手动选择年月日时分`：关掉“按当前时间”，滚轮选择真实日期和时间；静心后使用 `chosenTime` 按同一本机 Swift 历法和转盘算法计算。谨慎处理时区与夏令时。
- 对于仍未经古籍验证的节气近界、晚子时及中五门特殊情况，`WenguaNativeCore` **拒绝计算而不是猜测**；没有成功生成、保存收据就不能登记15天限制。

## 产品界面及规则进度

打开 iOS App **先选领域，再选具体事项**。当前只有 `health.severity`（疾病健康→病情轻重）允许进入起局；其余领域作为规划展示并禁用对外专业断词，绝不错误套用疾病轻重脚本。正式用户不会看到四张封存样例作默认九宫。这四张测试盘仍在 `FrozenReadingV391.json` / `chart-facts-v3.js` 作为版本保护及真实计算测试基线，不可删除。

九宫与双宫十二长生、星门神五行色、空马墓已在原生 SwiftUI；读取研究样例时完整文字连续排版、不需逐项点开。**实时新盘 V3.9.1 文字断案引擎尚待 Swift/离线 SQLite 完整移植与原书独立回归**，当前不得假造吉凶、应期、评分。15天限制是本机 SHA-256 具体事项锁，换设备/改写问题不能确保识别，发布前需加强事务性与隐私保护。

## 开发和测试命令

```sh
# 在仓库根目录
python3 -m unittest discover -s tests -v
node --test tests/ios_issue_policy_v2.test.cjs tests/ios_five_element_board_v3.test.cjs

# 在 ios/WenguaAppUI 目录
xcodegen generate --spec project.yml
xcodebuild -project WenguaApp.xcodeproj -scheme WenguaApp \
  -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build
```

XcodeGen 项目构建成功 != 真机运行 != 已签名的 IPA != App Store 已上架。CI 历史保留在 https://github.com/turnupmason/WenguaApp/actions 。

## 日常工作方法

用 Xcode 写 SwiftUI 页面、运行调试；用 VS Code 或其它编辑器维护 `src/wengua/`、`data/`、测试；用 GitHub Desktop 同步。每次开发先 `Pull` 再改，保留本地分支/失败实验，跑测试后再 `Push`；每次更新 AGENTS、项目状态、章节账本，确保换会话不会丢失项目状态。
