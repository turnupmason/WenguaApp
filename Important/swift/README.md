# Important/swift · 真实 iOS 原生执行索引

本目录分类快照数量 **30**。实际 Xcode 项目配置在原仓 `ios/WenguaAppUI/project.yml`；**不要直接编译 Important 镜像目录**。

- `engine/WenguaNativeCore.swift`：真实 iOS 离线起盘。
- `engine/WenguaNativeActorBinding.swift`：20种关系资料映射；取用条件未核仍在内部审计留痕，年命没有就不虚构。
- `engine/WenguaNativeVNextEngine.swift`：同源八神/星门/81格/200格、十二长生、空墓刑迫、真实宫位去重评分与跨宫计算。
- `engine/WenguaPythonVNextVerbatim.swift` + `engine/WenguaNativeReadingRouter.swift`：**现在手机真实入口**，与 Python 使用同源 `reading_template.json` 严格生成断词。
- `engine/WenguaNativeEnergyBundle.swift`、`engine/WenguaHealthTemplateBridge.swift`：同源数值与古籍有序81格桥接。
- `ui/`：SwiftUI 页面，含 `WenguaDesignPreviewApp.swift`、离线历史与客户展示；另外独立 `WenguaVNextReasoner.swift` 为研究旧层，不能当最终客户全文入口。
- `data/`、`templates/`：与 Python **完全相同的原始 TSV/JSON blob**，不是 Swift 另造一套。
- `tests/` 和 `ci/`：真 Swift CLI、Xcode iPhone Simulator、随机时辰 Python 整篇中文逐字/逐节/人物/时间一致性硬门槛。旧成功失败记录继续留 GitHub。

***所有真实业务文件仍在原位运行。*** `Important/MANIFEST.json` 标准化其对应镜像，并由 Python CI 字节校验防止失同步。
