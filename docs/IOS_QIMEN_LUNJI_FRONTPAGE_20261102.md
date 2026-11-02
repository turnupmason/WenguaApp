# 奇门论疾 · V27 首页摘要接线修复 · 2026-11-02

用户截图显示第一页空提示、第二页已有完整病位结论；用户要求第一页总结，并将当前产品“伤病在哪里/病情在哪里”统一命名为“奇门论疾”。本轮是经用户明确授权的展示补丁p2，不修改V27规则或断词模板，不改轻重V9/V11。

## 根因与修复

- `WenguaPremiumReadingView.swift` 的旧首页在health.discomfort分支读取 `06_conclusion`，但V27真实最后一节是 `09_conclusion`。因此已有完整结论也落入“当前无足够实际盘面依据”的错误占位提示。不是实际盘面缺证据。
- 新的纯展示适配器 `WenguaDiscomfortVerdictPresentation` 只读取同份reading的 `09_conclusion`，首句提为醒目金色摘要，余下真实症候和旁证显示在下方。仅去掉首句已知的“综上，人物”开头，不创造病位、排序、强弱、吉凶或康复日期。
- 用户截图文字作为明确标注的UI回归样本：标题应显示“本次病位先看大肠”，下方保留胃的伤痛/损伤线索。截图未给时辰，不补造一张起盘，不把UI样本冒充实盘。原文只有“另见胃”时不擅改为已核准的第二病位排序。
- 原始reading、完整专业解盘和已保存快照不变。V27旧记录也可通过同一适配器显示摘要，无需重新起局。真正缺少有效09结论才显示结论缺失提示；不从旧06字段、轻重等级或固定样例拼造结论。

## 名称统一与兼容

- 选领域/细项、起局填写页及本次事项标题沿QuestionCatalog统一显示“奇门论疾”。
- 专业解卦卡显示“奇门论疾 · 古籍类象”，不再用“可能关注的身体区域”替代实际结论。
- 历史列表按既有topicID映射“健康 · 奇门论疾”，修复原先显示技术ID的问题。
- 内部 `health.discomfort`、V27版本标识及存储/15天限制键保持兼容；不改原书题名或历史审计原文。

## 封存与测试范围

原p1清单原样保存在 `archives/engineering_patch_20261102/health_frozen_20261102_before_frontpage.json`。当前清单明确标注engineering_p2，仅3份生产UI源pin变化（主入口、首页卡、历史页）；全部模板、200/81、人物、V27/Python/Swift内核的源pin逐字不变。p1旧补丁边界仍对归档p1清单验，不放宽成无范围的任意改动。

新增实际Swift源码运行检查 `tests/verify_ios_discomfort_frontpage_runtime_20261102.py`：编译真正首页适配器，核对截图摘要、错误旧ID陷阱、缺失/空白/错误主题阻断，以及本轮实际V27 native JSONL中至少两张真实时辰。该检查接入正式Xcode workflow，并将日志归档。它验证真实摘要接线，不冒充全部按钮的XCUITest或真机视觉验收。

本地专项25项全通过；完整841 tests仍2个手动时辰功能失败、0错误、3个原有skip，无新增失败。封存资源SHA与镜像检查同步通过。新Swift运行、正式Xcode和包内资源结果以本提交真实Actions完成后追加，不引用旧run充数。

病愈应期仍是下一研发重点，health.recovery未开放；本展示修复不添加应期规则或康复承诺。

补充：同一实际源码摘要适配器与两份真实V27 native输出也接入Ubuntu Swift快速回归，并保存完整artifact。它补足旧检查只验轻重首页而漏验病位首页的覆盖缺口，不依赖macOS排队；实际App的Apple编译/资源验收仍由正式Xcode完成。

快速Swift实际运行 #41470201781 已success，截图与两张实际V27 native摘要均通过；独立App真Xcode编译 #41468305381 success。专用macos-15队列长时间未分配runner，增加手动可选macos-latest备用，仍完整执行相同验收，不改变或跳过步骤；App/资源pin不变。共享原生工作流补齐Important双镜像。


### 2026-11-02 · 奇门论疾p2首页接线正式验收完成
正式macOS Xcode #41469280778 success，源码9b9a2606934c32a68022bd1669d3556bea4202ad：完整双架构Simulator App构建、封存实际包内资源检查、哥哥/妻子两个主题共4次Bundle路由、Python/Swift全文逐字、六伤损条件及1080数据检查通过。真正首页适配器运行检查同时通过截图原文、错误06字段陷阱、缺失/空白/错误主题阻断和2份真实V27 native结论，日志 docs/IOS_V80_XCODE_PASS_RUN_41469280778_ATTEMPT_1.md。最新共享原生 #41470986685（含真实病位首页运行）、主CI #41470986700 success，源码5da7fc7e；独立iOS完整App编译 #41468305381 success。工作流/记录后续变更未改生产源码或资源pin。
早期 #41468305370 顶层failure、job cancelled、无任何执行步骤，GitHub原注释为“The job was not acquired by Runner of type hosted even after multiple attempts”，另报macOS arm64容量限制；不是代码编译失败，原记录保留。#41470986648/#41470987628为正式运行启动后取消的重复排队，不称通过。
本地841 tests仍2 failures/0 errors/3原有skip，保留手动真实时辰入口缺口；专项25项、封存SHA和Important镜像通过。此次仅改首页真实09结论展示及产品名“奇门论疾”，两模板/计分/详细断词不变；旧V27记录兼容。未作签名真机或全套XCUITest验收。更新代码后重新⌘R才能看到新UI；病愈应期仍待后续独立研究。
