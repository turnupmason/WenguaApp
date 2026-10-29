# 2026-10-28 · 正式App文字清库，删除废弃显示文案与旧试验备注
用户明确要求“把所有扰乱我们，不用的旧文字全部删除，不要留”。此需求是针对活跃产物和App可见断词的文本清库，不授权删除古籍原文、历史Git提交、已揭晓案例、失败日志、以前版本完整证据，亦不授权修改V8.0计分或V10.2客户实际断案话术。保留用户前一轮锁定的十档吉凶四字诀以及中平「微恙／病势平缓」。

本轮清理范围：
- `ios/WenguaAppUI/WenguaPremiumReadingView.swift` 移除曾导致误判的硬编码「尚未定局」旧标题及旧「只作/仅作」版本说明；真正无可解析结论时只显示准确的「结论依据待核」，仍拒绝给未知值造吉凶。
- `ios/WenguaAppUI/WenguaNativeReadingRouter.swift` 废弃无200格时伪造「专业合断尚未接通」的阶段一伪断词分支；缺本地真实能量数据改为显式抛 `missingEnergy`，生产有资源的唯一路径依旧经过同一真实 `WenguaVNextEngine.compute` 和 `WenguaPythonVNextVerbatim.sections`。之前故障描述“200格未完成与Python验收”现已失实，不再打包。
- `data/templates/health_severity_vnext/reading_template.json` 只移除不参与客户真实输出或冻结计分的冗长旧 V7.2..V7.9 comment/试验说明、历史阶段版本元数据，以及已无消费者的早期 summary_five_customer 和 native_customer.pending；**不改任何 V10.2 实际展示宏、当前 schema、源81原文、V8 final_scoring_v80 或人选及八张200格**。旧原文字节始终保留于清库前Git提交和归档，不能清除历史。
- `src/wengua/health_reading_template_vnext.py` 只接受 V10.2 实际 schema，弃用历史版本白名单、无用宏的存在性断言；所有正式 live V10.2 断词段仍通过相同 Python/Swift 模板输出。
- 主 iPhone board 注释删除旧 V3.9 误导说明，用户看不到任何过时状态；真实非疾病领域仍保留诚实「开发中」。同步 Important 双镜像与 MANIFEST Git blob SHA。
- 新 test_ios_live_copy_cleanup_20261028.py 进入当前主CI，检查无旧标题、虚假未验收提示、V7旧配置和伪结果分支，且十档与当前断词存在。Xcode bundle现改验 current summary_concise，必须跑macOS实际SwiftUI iOS Simulator与bundle200/81/人物资源；原生Python↔Swift全字验收须实际确认。本提交不宣称未执行的结果。

历史记录一律只追加。因用户显式本次批准清理旧文字，此次 live JSON 文件blob SHA变动是冻结V10.2模板的一次“**仅清理死字段，不改实际输出字面**”例外；原始冻结源SHA及断词全文仍长期留存，恢复须新获用户批准。
