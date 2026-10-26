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
