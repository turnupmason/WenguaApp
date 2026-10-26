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
