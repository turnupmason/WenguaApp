# 问卦 · WenguaApp

[![当前封存版本 CI](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml)

基于《神奇之门》《开悟之门》持续开发的原生离线 iPhone 应用，当前采用时家转盘。手机本地完成真实历法、完整九宫、人物取用与中文断词，不依赖云端 GPT；古籍象意不等于医学诊断或科学有效性证明。

## 当前正式封存版本 · 2026-11-02

以下两个健康主题已获用户确认封存，手机正式接口已接入并通过实际 App 包验收：

| 主题 | 计分与模板 | 正式模板 |
|---|---|---|
| 疾病健康 → 病情轻重 | **V9.0 计分＋V11 断词模板** | [轻重 V11](data/templates/health_severity_vnext/reading_template.json) |
| 疾病健康 → 伤病在哪里 | **V27 病位规则与模板** | [病位 V27](data/templates/health_discomfort_v11/native_discomfort_v15.json) |

V9.0 保留 V8 基础计分，并包含按真实亲属条件成立的长幼辅助扩展；不能把基础 V8 的内部审计标签误认为加载旧版模板。病位 V27 的目录及文件名保留兼容命名，实际版本由 JSON schema 和封存清单确定。

- [正式封存与手机接口记录](docs/HEALTH_PRODUCTION_RELEASE_20261102.md)：版本、路由、清退、验收及剩余问题。
- [封存清单与 SHA256](data/releases/health_frozen_20261102.json)：锁定两份正式模板、规则资源及生产源码；未经授权不得暗改封存内容。
- **当前模板目录只保留两份正式模板。** 23 份旧模板、草稿及固定样例已清出原位，带原始 SHA [归档保留](archives/retired_health_templates_20261102/INDEX.json)，不参与手机打包或运行回退；38 项旧版自动构建/预览改为手动审计。
- 婚姻、工作、求财、出行、升学、刑事、失物等领域尚未完成正式验收，仍标开发中，不能套用疾病模板。

工程补丁 **p1** 仅纠正地盘本征审计字段及空格局审计崩溃；两份模板和数值规则未变，旧封存清单已原样保留。规则疑点和真机待验项见[本轮规则复核](docs/HEALTH_RULE_QUESTIONS_AUDIT_20261102.md)。

## 手机流程与正式接线

选领域与细项 → 确认人物关系和事项 → 30 秒静心 → 点击确认瞬间采集手机真实时刻及 IANA 时区 → 本地历法与九宫 → 用神与条件推断 → 九宫、自然中文结论及有依据的应期。

同一事项按本机记录实行 15 天起局限制。真实出生年命未提供则不补造；病位必须明确选择普通不适、意外受伤、骨肉受损、出血、剧痛或手术，未选择禁止起局。普通不适不额外启用远宫伤门，仍读取病宫本身的真实八门事实。

正式入口：[WenguaDesignPreviewApp.swift](ios/WenguaAppUI/WenguaDesignPreviewApp.swift) → [WenguaNativeCore](ios/WenguaAppUI/WenguaNativeCore.swift) → [WenguaNativeReadingRouter](ios/WenguaAppUI/WenguaNativeReadingRouter.swift)，随后按主题分流：

| 主题 | 引擎及断词链路 |
|---|---|
| 病情轻重 | NativeVNextEngine → PythonVNextVerbatim → NativeCustomerView |
| 伤病在哪里 | NativeDiscomfortV15（实际 V27）→ NativeCustomerView |

病位不进入轻重计分。缺失、旧版或未封存模板会报错，不回退固定样例；未支持的主题先阻断。200 格、81 格、人物规则、两份模板、255 来源、三源干象及封存清单均显式随 App 打包。`Important/` 是源码字节镜像，`archives/` 是历史审计资料，都不是 App 构建输入。

## 已完成的真实验收

| 验收 | 实测结果 |
|---|---|
| 正式 macOS Xcode Simulator 编译、实际包内资源 SHA/白名单、两个 Bundle 路由 4 次调用、Python/Swift 完整中文逐字、六伤损条件及 1080 数据检查 | [#41460320838 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41460320838) |
| 独立 iOS 原生历法、断词回归及真实 App 编译 | [#41460320720 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41460320720) |
| 封存轻重 Python/Swift 原生逐字回归 | [#41460320478 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41460320478) |
| 工程补丁 p1 的 Python 3.11/3.12 主 CI | [#41460321192 · PASS](https://github.com/turnupmason/WenguaApp/actions/runs/41460321192) |

[本轮 Xcode 完整原始日志与断词](docs/IOS_V80_XCODE_PASS_RUN_41460320838_ATTEMPT_1.md)保留了实际源码 SHA 和四次正式路由返回版本。上述通过记录各自绑定其源码提交，最新分支状态见页首 CI。

**验收边界：**当前是未签名 iPhone Simulator App 和软件接口验收，尚非签名 iPhone 真机安装或 App Store 交付。手机上已经安装的旧 App 不会随 GitHub 更新，需使用本工程重新构建安装。

**全库历史测试仍未全绿：**最新工程清账运行 839 项，2 failures、0 errors、3 skipped。原52条失败/错误中50条已修复或完成有证据的契约迁移，原断言与失败日志仍保留；剩2条明确指向手动真实时辰入口缺失。[逐项清账](docs/audits/health_cleanup_20261102/README.md)。正式封存门槛通过不等于全库通过，不能删除失败或改冻结规则迎合旧断言。迁移失败、配置失败与归档失败及其修复见[封存审计记录](docs/HEALTH_PRODUCTION_RELEASE_20261102.md)。已揭晓案例仅作回归，不能冒充秘密盲测。

## 在 Mac 上运行

需安装 Xcode、iOS Simulator Runtime 和 XcodeGen。首次获取仓库：

```bash
git clone https://github.com/turnupmason/WenguaApp.git
cd WenguaApp
brew install xcodegen  # 已安装可跳过
./scripts/打开问卦模拟器.command
```

已有仓库请先确认本地修改，再同步 `main`。也可在现有工程中手动运行：

```bash
cd ios/WenguaAppUI
xcodegen generate --spec project.yml
open WenguaApp.xcodeproj
```

选择 `WenguaApp` Scheme 与 iPhone Simulator。模拟器 App 不是可直接在普通 Mac Finder 打开的 Mac 应用，也不是真机 IPA。更多说明见 [Mac Xcode 本地开发](docs/MAC_XCODE_LOCAL_DEVELOPMENT.md)。

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
# 全库历史审计：包含上文已知失败，不能当作全部已通过
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
