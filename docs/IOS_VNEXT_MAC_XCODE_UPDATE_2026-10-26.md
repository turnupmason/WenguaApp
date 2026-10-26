# 本机更新 WenguaApp iOS V-next（2026-10-26）

> 仅更新原有 `turnupmason/WenguaApp`，不能重建仓库、reset、force pull 或覆盖本机未提交的改动。

## 为什么之前只看到 FrozenReadingV391？

过去 Xcode 工程还把冻结的 `FrozenReadingV391.json` 当成 App Bundle 样例。它是 V3.9.1 的旧历史测试，不是新版 V-next 真盘断案；GitHub 远端提交不会自动更新 Mac 本地工程，也不会自动更新已经装好的模拟器 App。现在 GitHub 的正式 `ios/WenguaAppUI/project.yml` 已经撤下这份旧样例资源，正式用户入口 `WenguaDesignPreviewApp.swift` 已改为起局后在九宫下直接展示实时生成的 `WenguaVNextInlineReading`。旧文件没有从 GitHub 删除，仍可作为历史查阅。

## 已有克制与资源的边界

- iPhone 计算：`WenguaNativeCore.swift` 真实本机起局；`WenguaNativeVNextEngine.swift` 与现行 Python 对照的九星/八门/八神/81格/200格、真正干支十二长生、病宫医药医者人物宫、真假空±3、五不遇时、门破、实宫去重与克制格；`WenguaVNextCustomerComposer.swift` 将内部计算结果转换为无评分的可编辑中文。评分仅内存研究运算，不会写进客户断词或本地历史。
- 人物关系：`data/knowledge/phrase_library/health_v20/actor_profiles.json` 共20个**已有来源**身份作为轻量 iOS Bundle 规则索引，`WenguaNativeActorBinding.swift` 选择实际日/月/年/时干或妻乙夫庚、日干五合，核对问事是本人/专门代问/闻讯事件。出生完整干支、真实病人性别及排行只在适用时参考；未验证条件不得靠类推硬写成确切用神，不能看作20个都已做完独立实盘验收。没有甲盘普通显干时拒绝而非造假。
- 正式 iOS 包不包括整个 `src/wengua/*.py`、古籍全文、案例 SQLite 或训练资料；完整 Python 和历史 SQLite 留仓库作为研发、审校及更新依据，只有真正离线执行所需的轻量数据和 Swift 计算内置。
- **目前只开放**`疾病健康→病情轻重` 的详细 V-next。其它领域需按其独立领域+细分用神规则单独接线，不能直接复用测病模板；本阶段不宣称15领域已完成。
- 现行研究性定向证据在有些时辰与宫内分值可能冲突，App 不能为了输出“吉凶”假装已经解决；仅原书条件满足且两条路线一致才可给传统象意倾向。属于传统文化研究，不是实际医学诊断或预后。
- 你之后修改客户文字只改 `data/templates/health_severity_vnext/reading_template.json` 的 `native_customer` 文字。修改后需重新拉 GitHub/重新构建 App 才会生效；在线文字更新不会自动推送到已安装的 iPhone。

## 在你**已经打开过** Xcode 的 Mac 上更新（只操作现有工程）

1. **在 Xcode 先关闭当前工程**（File → Close Project）。不要删除工程或新建项目。
2. 在 Terminal 进入你已存在的 **WenguaApp 仓库根目录**。不确定路径可在 Finder 找到 WenguaApp 文件夹，打开 Terminal 输入 `cd `，再把该文件夹拖进 Terminal 并按回车。例如如果放在用户主目录：

   ```bash
   cd ~/WenguaApp
   ```

3. 确认当前文件是否有你自己没提交的修改，然后以 **快进模式**拉取 GitHub main，绝不强制覆盖：

   ```bash
   git status --short
   git branch --show-current
   git pull --ff-only origin main
   git log -1 --oneline
   ```

   如果 `git status` 显示你有自己要保留的改动、或 `--ff-only` 拒绝，不执行 `reset --hard`、`clean -fd` 或 force；先保存你的改动并核实分支再继续。上面命令不会自动启动 Python/安装数据库。

4. 从 **同一仓库**重新生成已配置的新 Xcode 目标（不要点 Create New Project）：

   ```bash
   cd ios/WenguaAppUI
   xcodegen generate --spec project.yml
   open WenguaApp.xcodeproj
   ```

   如果显示 `xcodegen: command not found`，先运行 `brew install xcodegen`（需 Mac 已有 Homebrew）；再运行 `xcodegen generate --spec project.yml`。

5. Xcode 顶部 Scheme 选 **WenguaApp**，运行设备选择一台 **iPhone Simulator**（不是 `Any iOS Device (arm64)`）；Product → Clean Build Folder（Shift+⌘+K），然后 ⌘+R。
6. **验收新版**：选择“疾病健康”→“病情轻重”→选择人物与情境 → 输入真实或手动时间、完成30秒静心、确认起局。九宫下应直接出现标题 **“本次 V-next 断案”**，有宏观缓急、相关宫位、人物关系、综合判断、应期；古诀文字可展开。主界面**不应再出现 FrozenReadingV391**。其它领域仍标记开发中。
7. 若仍看到旧版，请在 Terminal 的同一仓库运行：

   ```bash
   git rev-parse --short HEAD
   grep -n 'WenguaVNextInlineReading' ios/WenguaAppUI/WenguaDesignPreviewApp.swift
   grep -n 'actor_profiles.json' ios/WenguaAppUI/project.yml
   ```

   两个 grep 都应查到内容，且 `project.yml` 不应包含 `FrozenReadingV391.json`。若本地有更旧工程的并行副本，确认 Xcode 顶部打开的 `WenguaApp.xcodeproj` 就是当前那个仓库下的路径。代码更新后记得重新运行并清理旧 Simulator 缓存。

## 发行门槛

真正 App Store 发行还需官方开发者证书、真机和 TestFlight、公众隐私政策 URL、App Store Connect 信息和 Apple 审核。这里的 Xcode Simulator 成功并不等于已上架。


### 2026-10-26 20关系原书附证进入新版断词主流程（UI简洁）
- 从已保存的 `health_v20/actor_profiles.json` 源索引执行配偶妻乙/夫庚的真实日干五合辅助、乾坤及排行补充、实际年命独立实宫；**不把辅助宫直接充当患者主用神，也不当成第二独立分数**。`WenguaVNextCustomerComposer.swift` 已在主断案的角色解释里显示经核实际 `natal` / `gender` 角色，其他人物取用来源说明和五合补充仅在折叠的「人物取用的额外依据」中，避免啰嗦。所有新增话术都归现行 `reading_template.json` 的 `native_customer.vnext_actor_*`，客户看不到数值。
- 原 `native_core` 对照门槛继续要求同一真实时辰的五盘 Python/Swift 完整星门神/格/实宫签名后得分一致；新的20档案是取用**来源索引及条件性实现**，不是所有来源已通过足量原著未见家族案例判对；其他专题不可挪用疾病模板。任何后续新 Xcode build 都要在改动代码的同一SHA Actions验证。旧UI与失败记录不删除。


### 2026-10-26 最终定向全链验收：3新随机真盘 + 5原有对照，性别辅宫源错误已修复

- 固定新随机种子 **202610263311**，按纽约本地真实钟表 `2020..2025年 / 1..12月 / 1..28日 / 奇数时1..21` 先抽得技术有效的三个时辰，没有依据输出吉凶挑选：① `2024-09-02T05:00:00-04:00` 本人，甲辰 壬申 己巳 丁卯，阴遁4局；② `2022-04-05T17:00:00-04:00` 父亲，壬寅 甲辰 戊子 辛酉，阳遁1局；③ `2024-10-13T15:00:00-04:00` 妻子，甲辰 甲戌 庚戌 甲申，阴遁6局。Python 当期真盘 `scripts/ios_vnext_three_random_20261026.py` 先跑，Swift `ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift` 独立调用**和生产同一个** `WenguaNativeVNextEngine.compute` ＋ `WenguaNativeReadingRouter.compose`，逐宫比九星、八门、无月令八神、81格十二长生/墓刑、有序地盘、月令、门破、五不遇时、真假空后值、同宫去重、乾坤辅助、五张定向克制表当前实际单元及 Python 证据方向，并禁止内部评分流入读词。这三盘及此前五盘**8次实际钟点样本**通过，并非穷举所有组合。
- 真实失败保留：首轮 `iOS Offline Native Casting Parity #40374860791` 因新Swift测试命令跨行 `+` 语法错，修复后在第三张妻子盘抓到 `WenguaVNextReadingGate.unresolvedRole` 真问题：性别辅助`gender`被误当成需要天盘携干的`stem`而不是实宫九星，这是前五盘完全未覆盖的交叉角落；已在 `WenguaNativeVNextEngine.swift`修正性别归类，保留旧run，**最终完整** [iOS Offline Native Casting Parity #40375225758](https://github.com/turnupmason/WenguaApp/actions/runs/40375225758) 的 `native_core=success` 与 `real_ios_xcode_build=success`（真 XcodeGen + iOS Simulator `xcodebuild`），三个独立真盘都打印 `VNEXT_IOS_RANDOM_PARITY_PASS` 和 `VNEXT_IOS_3_RANDOM_ALL_PASSED 202610263311`。当次原生 App Store debug simulator artifact 是未签名模拟器构建，不是 iPhone IPA/Apple 已审核。
- 本轮用户可见三套**真 Swift 最新客户模板原始读稿**以不可静默覆盖的新名称存储在 `docs/HEALTH_VNEXT_THREE_RANDOM_REAL_IOS_READINGS_2026-10-26.md` 和 `data/evaluation/health_vnext/three_random_20261026_ios_vnext_customer_reports.json`，其中完整详文含8段用户显示原样，与 Python研究内部数值分离；GitHub Actions artifact 保留独立源Python金标及 Swift stdout（默认90天）。书籍章节/原著案例不新增，历史43章194案例家族不改变。用户的未来人工修改模板**只影响重新编译后的后续读稿**，不会修改封存的本次历史测试原样输出。
- 用户询问“所有东西已接入”：**就目前唯一可运行的「疾病健康 → 病情轻重 V-next」在真实盘触发的列举确定性计算步骤、三盘 Swift↔Python 值、三盘原生客户模板断词而言，证据成立**；**不代表**所有20类人物取用的独立来源与条件均已完全确认，也不代表81格所有墓刑分支/全年节气边界/值使中宫未经原书核实的寄宫/全部五张克制表所有条件组合都已穷举；尤其**其它14大领域和健康其它细分尚未移植**。早前用户人工确认的 81 Excel 与200表资源都在本机包内，不把整库古籍SQLite或所有Python放手机。
- 本轮三个实际结论是传统象意候选：本人甲辰壬申己巳丁卯 `偏凶`；父亲壬寅甲辰戊子辛酉宏局 `反吟主快`，按年干候选与病宫独立门槛`尚不强断`；妻子甲辰甲戌庚戌甲申宏局`伏吟主慢`，妻乙夫庚加庚日干五合辅助，同样`用神来源条件性待核`。**不是医学诊断、病情预测或实际预后**。
