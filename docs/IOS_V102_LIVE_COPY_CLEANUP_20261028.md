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

## 实际Actions全量交付、镜像双副本失败与修复（绝不删日志）
- 本轮首提交 `01a5de34ada8af166bc95680845f7b0da17c64fa`：Python当前主CI #40810874530 FAIL，是旧测试 `tests/test_health_v80_concise_friend_20261028.py` 还访问已删除死宏 `summary_five_customer`；不能为过旧测试把该宏偷偷重新加入App。
- 同一首提交的V8实际native #40810874359 FAIL、V7.7 native #40810874473 FAIL、旧V7.4回归 #40810874404 FAIL，根因是双镜像中遗漏 `Important/python/templates/templates/health_severity_vnext/reading_template.json`，它仍含旧comment且字节不同；旧V-next preview #40810874546 也曾FAIL。各真实失败均保留于Actions及自动生成的追加失败报告；旧iOS Offline Native Casting Parity #40810874334 FAIL亦不声称全库无失败。
- 修复提交 `29509f71ef039d9c49e10bcb33b40604a2042ee5`：真实检查 MANIFEST 相同canonical有 **两份镜像记录**（Python与Swift），把两份资源均指向清理后的同一个Git blob SHA `f27aec394eb8c3fd3a952be763bee6fc0f9061e7`，更新 MANIFEST；将旧朋友测试仅改为验证当前真实 `macro_five_customer`。原冻结200/81/V8算分/有实际调用的V10.2断词宏未变。
- 修复后同一代码源 SHA `29509f71`：Python3.11/3.12正式主CI #40811025113 **PASS**（包括本轮新旧文字清库测试和 Important双镜像字节）；V8完整原生Swift ↔ Python 200格/五方向/同宫及全文 #40811024846 **PASS**；V7.7已见旧钟原生比对 #40811024502 **PASS**。首次提交 `01a5de34` 真macOS XcodeGen/Xcode iOS Simulator完整编译、包内200/81/人物/V10.2模板资源 #40810874316 **PASS**；该测试源码和App资源之后未再变，只修复 Important Python漏镜像与旧断言，故该实测构建与最终运行代码同版（但无需假称修复SHA另跑过Xcode）。
- 清理后核验的仍是冻结V8数值与V10.2实际生成断词逐字一致，不是签名真机或医学有效性。用户端此前安装的App需要重新编译更新才会看见旧标题及假未验收文案被清理。

## 最后一次旧用语扫尾与逐项真测
在清理后重新扫正式源代码时，另外找到 `src/wengua/health_palace_detailed_vnext.py:render_complete_selected_palace` 的**非compact历史路径**仍可能拼「全部因素推断后，此宫为」；按用户“不要留旧文字”将该唯一旧表达换成现行「宫象」，没有改变 score 或实际V10.2 customer macro。源码及 `Important/python/reading/health_palace_detailed_vnext.py` 同步，更新MANIFEST，提交 `245daf8caef5a6d478ae838958235dc9606a2ece`；新主CI增加严格无旧字样回归。
对这个最新实际源SHA的真实Python3.11/3.12主CI #40811469690 PASS、V8核心原生Swift和Python严格数据/中文比对 #40811469615 PASS、固定V7.7旧盘原生比对 #40811469635 PASS。另有非现行V7.4旧工作流 #40811469688 FAIL（历史期望旧阶段断词结构）和V-next旧preview #40811469642 FAIL（硬编码旧标题「起盘总纲：五不遇时、伏吟、反吟」，现行标题「时局总纲」），不为通过旧测试恢复废弃文字或改V8数值。两条失败按Actions保存。对应正式App源在前一提交实际Xcode Simulator #40810874316 PASS；这一步只变Python非compact历史句，未变iOS源码/包内App资源。