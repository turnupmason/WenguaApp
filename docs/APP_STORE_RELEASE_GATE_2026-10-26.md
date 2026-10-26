# 问卦 / WenguaApp · iOS App Store 发布关卡（2026-10-26）

> 这是上架工程交接，不是宣称已经发布。仅在用户自己的 Apple Developer/App Store Connect 账户授权后才能创建发行记录、签名并实际向 Apple 提交。现有 GitHub Xcode Simulator 的 CODE_SIGNING_ALLOWED=NO 构建不是可安装发行 IPA。

## 已开发并经 CI 核验的技术基础

- 继承现有 `WenguaNativeCore.compute(at:timezone:)`：确定性本地时家转盘，节气不确定或中五值使寄宫不明一律报错，不发假盘；仍有原书/天文边界等待补核。
- 领域→细分 ID → 原生模板入口：`health.severity`，主取用目前限定本人（日干）和父亲（年干）；其它领域/人物关系在 UI 可见但未过离线验收，不得冒用健康本人模板。
- 真九宫直接定位天芮、天心、乙奇、时干、值符与真患者用神；检查五不遇时与整盘伏吟反吟，分别以真实宫位关系拼接 `reading_template.json/native_customer` 的人工可编辑话术，精确读取同一Git仓库 TSV 81/81 真有序干古诀。
- **正式顾客文本绝不显示内部数值**：研究评分继续由 Python V-next 的200格、真假空+/-3、宫位去重、五级原始量化等内层计算，留结构化 DTO；iOS 用户只看到核定的原生盘面及目前来源已接通的传统证据。Python顾客模板移除评分节与数字，老模板归档 `data/templates/health_severity_vnext/internal_audit_template_20261025.json`。目前双运行时的最终完整 V-next **没有完成逐盘一致性**，因此 iPhone 尚不能给出已经验证的综合吉凶、应期或诊疗结论。新版自然语气还可由用户在 GitHub 人工改。
- 30秒静心 + 同一具体事项15天内真实成功起局限制继续保留；现在在 `WenguaNativeReadingRouter.compose` 可成功生成该项真盘与原生证据 **之后** 才持久化并计入15天。若未知人物关系或缺盘失败，严格不记锁。
- 本地记录页面、逐项删除、明确确认的全量删除及隐私说明 `ios/WenguaAppUI/WenguaLocalHistoryView.swift`，不误承诺跨设备同步；用户仍需实际 iPhone 手工测试。

## 尚不可宣称已经上架或可直接送审的项目

1. **最关键：完整健康 V-next parity**。200格矩阵、81格所有源条件、十二长生、患者关系全部分支、真假空±3、宫内签名计算、物理宫去重、真病宫克制方向、旧/新证据冲突优先级、详细应期尚须移植到原生或经过可分发的共享引擎，并与Python在跨年、节气、夏令时、同宫、空墓刑迫、各种人物关系真盘逐字段比较。其它14大领域独立模板继续排队，用户可按领域逐一批准。
2. 设备层：Mac Xcode 打开 XcodeGen生成工程、真实 iPhone（iOS17+）安装点击、后台中断30秒、离线、断网、时区变化和 DST、本地记录恢复/删除、VoiceOver、大字体、UI截图及资源实机测试。
3. 发行物：用户 Apple Developer Program 账号及证书、真实的 Team ID；Bundle ID `com.wengua.ios` 需在 Apple Developer 检查唯一性后确定，不能假定当前占位ID已注册；App Store Connect 建App条目、签名归档、上传构建、TestFlight内外测、版本/build编号、隐私问卷、分级、截图、描述/关键词/分类、本地化和可访问的支持页面。
4. 隐私政策必须有公开可访问的 URL（App Store Connect + App 内）；仓库 `docs/app-store/privacy-policy.html` 是可公开部署的原稿，**需真正用 GitHub Pages 或授权域名托管并从外网验证可访问**，不能将 GitHub 文件地址冒称为正式官网。
5. Apple 2026 规则需复核：`https://developer.apple.com/app-store/review/guidelines/` 的 4.3（占卜/fortune telling 分类要求具有显著差异化）、4.2（minimum functionality）、1.4.1（诊断治疗软件高审查）、5.1.1（隐私政策与清除方式）、5.1.3（健康隐私敏感）。上架主定位「可复核的传统时家转盘 + 古籍来源 + 离线本地研究」，不应声称能够科学地判疾病轻重、死亡或实际疗效。
6. 版权：用户原书和194案例版本保留研究库；发行时只附有授权可公开的少量古诀及原创说明，原书全文不要无授权嵌入可发行 app。用户81格TSV的古文摘句亦需要确认公开发行权。

## 每次改动的 GitHub人工文字流程

- 修改 `data/templates/health_severity_vnext/reading_template.json` 里的 `native_customer` 各句即可调整原生客户文字。保留 `{palace}` / `{relation}` / `{names}` 等占位符名字，不改真实干、门、星神算法。
- 改Excel的格局解释则按原流程更新 `data/knowledge/health_81_excel_20261025/81_pairs.tsv`，严格81行7列；历史原版和所有失败 Actions 仍保留。
- **GitHub Commit 并不会更改已安装用户手机App**，必须下载/构建带新Bundle资源的App并重装/经App Store发布新的版本。真正可在设备上实时下载远程断案规则属新的网络/隐私/审核架构，不在现有离线V1中擅自开启。

## 发布主线下一交付

研究层 V-next 与 iOS 原生共享事实契约、完整推理层 parity → 至少多个人物/多种时辰稳定无内部评分的自然断词 → 真人设备测试/版权和隐私审查 → TestFlight → 提交Apple审核。**此轮未提交App Store、未生成签名IPA，不能宣称已上架。**

## 2026-10-26 200格离线资源补档

新版另增 `data/mobile/health_vnext/health_energy_200.json` 作为八张25格用户权威表的**全部真实单元格**静态 Bundle；`WenguaNativeEnergyBundle.swift` 校验本地资源，且 `scripts/export_ios_health_energy_200.py --check` / `tests/test_ios_energy_200_source_parity.py` 比对 Python 8×25。注意只是**数据已搬入iOS应用**，尚不是 Python `health_quant_overlay_vnext.py` 的全套推理和结论已经 Swift 等价执行；上架门槛仍要求全链数值内部一致、客户输出不得展示任何分数。

## 2026-10-26 发行资源补充
- `ios/WenguaAppUI/PrivacyInfo.xcprivacy` 声明 UserDefaults 只访问当前App本机偏好（Apple已确认理由 `CA92.1`）、没有声明第三方跟踪/收集；需在正式发行前按实际 SDK 与网络行为重新审查，不能只靠此文件解决全部隐私义务。来源：Apple `https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitypereasons`。
- `.github/workflows/ios_native_cast_parity.yml` 完整Xcode Simulator构建成功时产**未签名模拟器调试App artifact**（30天），不是iPhone可安装IPA或App Store签名包。真实开发者账号、Team ID和App Store Connect仍须本人处理。


### 2026-10-26 原生 iOS 离线接线／模拟器工件最终已验证（本轮实测）
- 本轮真实源码构建提交 `073078cef6ff16349fc30289928a3ebfaa571e9f`；其对应 [iOS Offline Native Casting Parity #40350794158](https://github.com/turnupmason/WenguaApp/actions/runs/40350794158) 的 `native_core=success`、`real_ios_xcode_build=success`，两者是实际 Swift 核心运行及 macOS XcodeGen + iOS Simulator `xcodebuild` 全工程编译，不是只做 syntax parse。已真实导出 GitHub Actions artifact `wengua-unsigned-simulator-debug-app`（artifact ID **12663004530**，下载从该 run 的 Artifacts 区域进入）；另有五盘审计 `five-new-true-charts-and-pillar-template-audit`（ID **12662799274**）。
- 同源码 [WenguaApp CI #40350794314](https://github.com/turnupmason/WenguaApp/actions/runs/40350794314) 的 Python 3.11/3.12 全仓 success；[iOS V1 Design Contract #40350794872](https://github.com/turnupmason/WenguaApp/actions/runs/40350794872) success。此轮此前 SwiftUI 历史页语法/类型检查失败、CLI 忘带200格依赖、Python tuples/list 数组转换失败等旧Run 全部保留，不覆盖、不删除。未来一旦再次提交代码，仍需以最新 HEAD 对应CI重验。
- **产品可用性界线**：生成的 `.app` 是 **unsigned Simulator Debug**，不适用于用户直接安装 iPhone、不代表 TestFlight、Apple Connect 上传或 App Store审核通过。手机现在已有真盘、明确支持的本人/父亲两条用神、81格、200格静态资源、真实宏观条件和简明中文证据、本地存储与隐私，但**未完成跨语言 V-next 核心200格运行推理／真假空规则／内部评分合断的完整逐盘一致性**，所以原生综合吉凶仍明确为待核而非假冒真断。用户后续人工改模板靠 `reading_template.json/native_customer` 并重新编译发版本；既有V3.9.1、81来源、全部194古籍案例和失败数据保留。


## 2026-10-26 最新用户反馈：旧 Frozen391 仍是本机界面；客户端改为 V-next 真盘、20类关系源索引，古籍保留仓库不打包

- 用户打开 Xcode 实测仍只看到 `FrozenReadingV391`，证明**“GitHub 上 Swift V-next 真盘数学对照已通过”≠“用户的 Mac 已重新 pull/generate/build 且入口展示新版”**。此前称完整接入不严谨。已将 `FrozenPreview` 用户 UI 分支和 `project.yml` 的 `FrozenReadingV391.json` 资源移除，**原冻结文件及其历史签名/测试仍保留Git**；真盘九宫下显著增加 `WenguaVNextInlineReading`，用户无需跳转旧 Sample。历史测试中错误假设旧冻结 UI 必须保留的断言已改为“源文件不删除、商用包不打包”。
- Python 原 `data/knowledge/phrase_library/health_v20/actor_profiles.json` **真实20个角色**（先前口头19是计数错误）。新增 `WenguaNativeActorBinding.swift` 在 iOS Bundle 中读取**这一个来源索引**并用真实年/月/日/时干、夫庚妻乙、真实日干五合、父母乾坤、性别/出生顺序、完整出生年命干支可选、代问/闻讯区别按源条件逐条绑定。没有原书验证的类推（同辈、母亲及晚辈等）按 `roleStatus=source_conditional_candidate` 对客户使用独立 `native_customer.vnext_role_candidate` 模板，不得输出肯定结论。已确证自测若日干适合等，可维持经过验证的路径；遇未解决的甲、出生年命、真实宫缺失则拒绝，不计成功起局锁。
- 新 `ios/WenguaAppUI/NativeActorProfileCheck.swift` 用真实2025-07-18 03:00 EDT盘逐个检查本人、父母辅助、妻乙夫庚和日干五合、朋友月干、侄子甲时六仪遁干及闻讯日干；同时检查不合法关系/情境强制拒绝。`tests/test_ios_vnext_production_entry_20261026.py` 检查完整20来源、旧V3.9归档存在但非Bundle、Swift源码实际展示新版且不打包SQLite。原全网研究评分只能内部用，客户 JSON / local history不显示数值。
- **明确不转码 GitHub 全部 Python 文件**：仅 App 离线执行需要的确定性起局/断事算法移植Swift与打包其小型规则索引，古籍原书、全部历史案例、SQLite全存现有GitHub/研究本地备份便于以后查阅和人工修正规则，不将仓库改成古籍阅读App，不删除既有书数据。
- 本轮依旧只有健康病情轻重子领域已移植；其他14大领域及细分并未因 UI 出现而冒称可断。对健康已经覆盖的核心200格/81格/生克/评分，真实五盘 Python vs Swift 的宫分和克制方向结论回归见现行 Actions；更广泛已知来源分支、同宫角色、多样时辰仍需追加实盘验收。Xcode 更新不用建新项目，步骤 `docs/IOS_VNEXT_MAC_XCODE_UPDATE_2026-10-26.md`，必须 `git pull --ff-only origin main` 后 xcodegen generate，再 Clean Build Folder + ⌘R；用户本地 Mac 不会随远端 push 自动更新。
- 本轮原著新章0、原书事件家族新0，累计两书43章194事件不变；旧所有CI失败保留，最终是否绿以对应 HEAD 工作流实时结果为准，未签 IPA/未 Apple 上架。
