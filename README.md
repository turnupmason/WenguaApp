# 问卦 · WenguaApp

[![当前封存版本 CI](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml)

基于《神奇之门》《开悟之门》持续开发的原生离线 iPhone 应用，当前采用时家转盘。手机本地完成真实历法、完整九宫、人物取用与中文断词，不依赖云端 GPT；古籍象意不等于医学诊断或科学有效性证明。

## 当前正式封存版本 · 2026-11-02

以下两个健康主题已获用户确认封存，手机正式接口已接入并通过实际 App 包验收：

| 主题 | 计分与模板 | 正式模板 |
|---|---|---|
| 疾病健康 → 病情轻重 | **V9.0 计分＋V11 断词模板** | [轻重 V11](data/templates/health_severity_vnext/reading_template.json) |
| 疾病健康 → 奇门论疾 | **V27 病位规则与模板** | [病位 V27](data/templates/health_discomfort_v11/native_discomfort_v15.json) |

V9.0 保留 V8 基础计分，并包含按真实亲属条件成立的长幼辅助扩展；不能把基础 V8 的内部审计标签误认为加载旧版模板。病位 V27 的目录及文件名保留兼容命名，实际版本由 JSON schema 和封存清单确定。

- [正式封存与手机接口记录](docs/HEALTH_PRODUCTION_RELEASE_20261102.md)：版本、路由、清退、验收及剩余问题。
- [封存清单与 SHA256](data/releases/health_frozen_20261102.json)：锁定两份正式模板、规则资源及生产源码；未经授权不得暗改封存内容。
- **当前模板目录只保留两份正式模板。** 23 份旧模板、草稿及固定样例已清出原位，带原始 SHA [归档保留](archives/retired_health_templates_20261102/INDEX.json)，不参与手机打包或运行回退；38 项旧版自动构建/预览改为手动审计。
- 婚姻、工作、求财、出行、升学、刑事、失物等领域尚未完成正式验收，仍标开发中，不能套用疾病模板。

当前工程补丁 **p7** 按最新截图修正完整文字、等宽卡片、居中标题、明显下拉控件、公历值、两句轻重摘要与统一竖排角色。见[本轮记录](docs/IOS_POLISH_P7_20261102.md)，实际原生／Xcode验收结果完成后追加。此前工程补丁 **p6** 修正准备页、页内填写、普通／选吉日时间边界、五列日期滚轮、宫位对齐与解读分组，详见[本轮界面与验收记录](docs/IOS_SETUP_PALACE_UI_20261102.md)。本轮855项完整测试、真实原生、Xcode零Swift警告及App包验收均通过。此前 **p5** 整理领域内普通预定时刻／选吉日接口、共用等级基础、专业解盘分项排版和有效输入，详见[本轮接口与排版记录](docs/IOS_DOMAIN_LAYOUT_INPUTS_20261102.md)（本轮真实原生、Xcode零警告及App包资源验收通过）。此前p4记录见[手动事项时辰](docs/IOS_MANUAL_EVENT_TIME_20261102.md)。此前 **p1** 纠正地盘审计字段；**p2** 接入奇门论疾首页及统一名称；**p3** 将首页收为直接病位一句话、增加30秒小和尚敲木鱼与诵念文字动画，并清理Swift警告。两份模板和数值规则未变，旧封存清单已原样保留。[首页修复记录](docs/IOS_QIMEN_LUNJI_FRONTPAGE_20261102.md) · [简明摘要、动画与警告清理](docs/IOS_QIMEN_MEDITATION_WARNINGS_20261102.md)（正式Xcode与Swift零警告实测通过）。规则疑点和真机待验项见[本轮规则复核](docs/HEALTH_RULE_QUESTIONS_AUDIT_20261102.md)。

## 手机流程与正式接线

选领域与细项 → 居中准备页 → 点击填写问事信息 → 页内确认人物关系和事项 → 30 秒静心 → 普通问事按确认瞬间起局；领域内「选吉日」按所选未来事项时刻及发生地时区起局 → 真实九宫与已验收专题解读。

同一当事人同一专题按本机记录实行15天限制。旧多候选组记录继续兼容；新的选吉日专用比较流程后续开发。真实出生年命未提供则不补造；病位必须明确选择普通不适、意外受伤、骨肉受损、出血、剧痛或手术，未选择禁止起局。普通不适不额外启用远宫伤门，仍读取病宫本身的真实八门事实。

正式入口：[WenguaDesignPreviewApp.swift](ios/WenguaAppUI/WenguaDesignPreviewApp.swift) → [WenguaNativeCore](ios/WenguaAppUI/WenguaNativeCore.swift) → [WenguaNativeReadingRouter](ios/WenguaAppUI/WenguaNativeReadingRouter.swift)，随后按主题分流：

| 主题 | 引擎及断词链路 |
|---|---|
| 病情轻重 | NativeVNextEngine → PythonVNextVerbatim → NativeCustomerView |
| 奇门论疾 | NativeDiscomfortV15（实际 V27）→ NativeCustomerView |

病位不进入轻重计分。缺失、旧版或未封存模板会报错，不回退固定样例；未验收主题只提供真实排盘、标明解读开发中。200 格、81 格、人物规则、两份模板、255 来源、三源干象及封存清单均显式随 App 打包。`Important/` 是源码字节镜像，`archives/` 是历史审计资料，都不是 App 构建输入。

## 当前时辰、预定时刻与选吉日

- 普通专题只用当前问事时刻，在完整静心后按确认起局的真实瞬间计算，没有预定时间切换。
- 15领域各自的「选吉日」只选未来的事项发生／约定时刻：健康看病／手术、出行旅游／出行、婚姻约会／结婚等；独立择时评级仍在开发中，目前提供真实盘，不进入普通健康解读。
- 手动入口先只显示“选择时辰”；点击后进入独立选择页，五列明确标注**年／月／日／时／分**。确认才保存选择，取消不提交草稿，换时区须重新确认。闰日、夏令时不存在时刻／重复时刻及最终未来性均校验。
- 首页没有独立挑日子卡；旧候选组与旧预定健康记录继续兼容，既有时间、评级依据和15天回执保留。
- 共用最终吉凶尺度与领域模板接口，当前健康沿用V9/V11；其它普通专题可真实排盘，专用取用、吉凶和断词标开发中，不借疾病规则。
- 已移除无效的必填自由描述。人物与实际条件才进入专题取用；同一当事人同一专题实行本机15天限制，旧描述回执保守承接，不因删除输入框解锁。
- 专业解盘按伤损部位、星门神、星干、天地格、限制和结论旁证分组，相关短句合成段落；原始断词全文逐字保留。四柱标签在干支下方，方向替代重复时刻栏；宫位标题居中，身份标签放大，刑墓小标记不挤偏天干。

## 已完成的真实验收

| 验收 | 实测结果 |
|---|---|
| 正式 macOS Xcode Simulator 编译、零Swift源警告、包内资源SHA／白名单、两主题4次Bundle路由、Python／Swift逐字、六伤损及1080源盘、新五列时间与分组验收 | [#41502545254 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41502545254) |
| 独立iOS原生历法、断词回归及真实App编译（全部6 jobs） | [#41502545252 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41502545252) |
| 封存轻重Python／Swift逐字回归与奇门论疾首屏实际运行 | [#41503297213 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41503297213) |
| 工程补丁p6的Python 3.11／3.12主CI | [#41502544972 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41502544972) |

[本轮Xcode原始日志与断词](docs/IOS_V80_XCODE_PASS_RUN_41502545254_ATTEMPT_1.md)对应生产源`d594d5d6`；独立原生复验起点`5be81c80`只增加历史文档，生产源／资源pin完全相同。[结果与SHA总表](docs/audits/ios_setup_palace_ui_20261102/final_ci_results.json)记录855项本地完整回归（0失败／0错误／3原有skip）、真实时间模式双向拒绝、闰日／DST、12组伤损分项原文重组、旧回执／历史兼容。中途自动归档Git冲突的两次失败日志保留，独立复跑计算与归档均通过；未用旧结果替代新版验收。此前p5验收与原始日志见[历史记录](docs/IOS_DOMAIN_LAYOUT_INPUTS_20261102.md)。

本轮完成编译和接口验收，五列滚轮、动画与排版仍须在模拟器／真机操作查看，未声称已完成人工像素视觉或全套XCUITest验收。

**验收边界：**当前是未签名 iPhone Simulator App 和软件接口验收，尚非签名 iPhone 真机安装或 App Store 交付。手机上已经安装的旧 App 不会随 GitHub 更新，需使用本工程重新构建安装。

**最新全库Python测试：**855项，0 failures、0 errors、3项原有skip。原52条失败/错误已按证据逐项清账；最后2项手动时辰入口现已实现并通过，未删测试或增加skip。[本轮实际日志与SHA](docs/audits/ios_setup_palace_ui_20261102/local_results.json) · [旧失败逐项清账](docs/audits/health_cleanup_20261102/README.md)。全库程序通过不代表各领域择时规则已验收或现实预测有效；旧规则/配置/迁移/归档失败记录均保留。

## 在 Mac 用 Command＋R 打开并测试 UI

先安装完整 Xcode、一个 iOS Simulator Runtime 和 XcodeGen。这里使用现有工程，不需要新建 Xcode 项目。

### 1. 打开仓库并生成工程

**已经下载过仓库：**打开“终端”，输入 `cd `（后面有一个空格），把 Finder 中的 `WenguaApp` 文件夹拖进终端，再按回车。确认现在位于仓库根目录，然后运行：

```bash
git pull --ff-only origin main
cd ios/WenguaAppUI
xcodegen generate --spec project.yml
open WenguaApp.xcodeproj
```

若 `git pull` 提示本地修改或分支冲突，先保留现场处理，不要 reset 或覆盖文件。若提示 `xcodegen: command not found`，先运行 `brew install xcodegen`；这需要 Mac 已安装 Homebrew。

**第一次下载：**先在终端运行下面两行，再接上面的生成工程步骤：

```bash
git clone https://github.com/turnupmason/WenguaApp.git
cd WenguaApp
```

### 2. 在 Xcode 选择运行目标

工程打开后，在 Xcode 顶部选择：

- Scheme：**WenguaApp**。
- 设备：一个已经安装的 **iPhone 模拟器**，例如 iPhone 16；不要选择 My Mac。
- 若没有 iPhone 模拟器，在 **Xcode → Settings → Components／Platforms**（随 Xcode 版本不同）下载 iOS Simulator Runtime，再回来选设备。

### 3. 按 Command＋R

点击 Xcode 窗口，再按 **⌘R（Command＋R）**，或点击左上角 ▶。首次编译可能需要几分钟；完成后模拟器会启动“问卦”。修改 UI 后也在这里按 ⌘R 重新构建运行。

若构建失败，打开左侧错误列表或 Report Navigator，保留第一条实际错误及日志；不要把工程删掉重建。更多本机准备见 [Mac Xcode 本地开发](docs/MAC_XCODE_LOCAL_DEVELOPMENT.md)。

### 4. 本次手动 UI 测试顺序

使用“UI测试001”等明确的技术测试事项，不填私人病情或身份信息。

| 顺序 | 操作 | 检查内容 |
|---|---|---|
| 1 | 首页 → 领域 → 细项 → 准备页 | 方向与静心说明清楚；不自动弹表单，点击填写才进入 |
| 2 | 病情轻重 → 填写人物与实际条件 → 静心30秒 → 确认 | 小和尚敲木鱼与诵念文字随静心播放；未满30秒不能起局；确认后生成真实四柱、九宫和断词 |
| 3 | 点九宫与切换专业解卦／专业解盘 | 字是否清楚、详情能打开、完整断词可滚动阅读，无按钮遮挡 |
| 4 | 奇门论疾 | 未选伤损情况应阻断；首页只显示真实主位一句话，伤损直接说“先看某处”，完整旁证留专业解盘 |
| 5 | 领域内选吉日 → 选择时辰 | 只选未来时间，五列年／月／日／时／分；确认提交、返回不提交草稿，真实排盘且评级开发中 |
| 6 | 关闭再打开 App，再查看相同测试事项 | 本地记录保留；已完成的同一事项受15天限制 |
| 7 | 换小屏／大屏、深浅色和大字体，断网再运行 | 布局不截断，两个已验收健康主题能离线起盘和读取资源 |

**当前边界：**普通问事仅当前时刻，领域内选吉日仅未来时刻，滚轮明确五列年月日时分；“病愈应期”及旅游、婚礼、手术等专项择时吉凶评级仍开发中。⌘R 用于启动 App 后手动测试界面。⌘U 用于已配置测试 Target 的自动化测试，当前工程尚未接入整套 XCUITest，不能把编译成功当作全部按钮已测试。

### 可选：终端一键启动模拟器

在仓库根目录也可以运行：

```bash
./scripts/打开问卦模拟器.command
```

模拟器 App 不是真机 IPA，也不是可直接在普通 Mac Finder 打开的 Mac 应用。真正 iPhone 的签名安装与实测另见 [真机验收准备](docs/IOS_TRUE_DEVICE_ACCEPTANCE_PENDING_20261102.md)。

## 下一开发重点：病愈应期

用户已指定下一重点为“根据病情判断传统病愈应期”。继续保留轻重V9／V11、病位V27的封存版本，独立开发 `health.recovery`，通过来源与原生验收前不开放。先区分好转、康复、出院等目标，核对原书适用条件，再由真实历法计算有凭据的候选窗口；不能把吉凶分直接换成康复天数，也不能承诺现实医疗康复日期。现状与开发顺序见 [病愈应期启动审计](docs/HEALTH_RECOVERY_TIMING_KICKOFF_20261102.md)。

## 开发检查

在仓库根目录运行：

```bash
# 封存源码、资源 SHA、旧模板清退与无回退检查
python3 -m scripts.verify_frozen_health_release_20261102
python3 -m unittest tests.test_frozen_health_release_20261102 -v
# Important 字节镜像检查
python3 -m unittest tests.test_important_mirror_integrity_20261026 -v
# 真实病位及六种伤损条件
python3 -m unittest tests.test_health_discomfort_v27_ding_gods_hour_20261101 tests.test_health_discomfort_injury_gate_20261102 -v
# 完整单测：最新855项0失败、0错误、3项原有skip，保留历史失败日志
python3 -m unittest discover -s tests -v
```

检查实际构建的 App 包资源时，可使用：

```bash
python3 -m scripts.verify_frozen_health_release_20261102 --bundle /实际路径/问卦.app
```

Python 测试不能代替原生 Swift 逐字校验、真实 Xcode 编译或实际包内资源验收。修改核心文件必须同步 `Important/` 双镜像与 `MANIFEST.json`；封存内容须经用户授权另建版本。

## 续接与资料导航

- [AGENTS.md](AGENTS.md)：续接执行规范与当前封存入口。
- [项目状态](docs/PROJECT_STATUS.md) · [章节账本](docs/CHAPTER_LEDGER.md) · [逐章流程](docs/CHAPTER_WORKFLOW.md)。
- [中文分类导航](项目导航/README.md) · [规则能量与旧 Xcode 审计](docs/V80_RULE_ENERGY_AND_XCODE_AUDIT_20261027.md)。
- `src/wengua/`：Python 原始源位；`ios/WenguaAppUI/`：正式 Swift 源码及 XcodeGen 配置；`data/`：来源规则、正式模板与封存清单。
- `tests/`：当前与历史回归；`Important/`：现役源码镜像；`docs/`、`archives/`、`schema/`、`sources/`：来源、历史版本、案例、迁移及失败证据。

本 README 展示当前状态；旧 UI、计分和批处理进度保留于[更新前 README 原文](docs/history/README_BEFORE_HEALTH_SEAL_20261102.md)及对应历史文档。旧文件名、旧日志和旧导航不覆盖当前封存清单。
