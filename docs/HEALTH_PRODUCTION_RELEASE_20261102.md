# 两个健康主题的正式封存与手机接口 · 2026-11-02

用户本轮明确确认：疾病轻重采用 **V9.0计分＋V11断词模板**；伤病在哪里采用 **V27**，两者均接受封存。今后以本文件和 `data/releases/health_frozen_20261102.json` 为当前发布入口，不再凭旧文件名或历史日志推测版本。

| 手机主题 | 正式规则/模板 | 实际源路径 | 正式接口 |
|---|---|---|---|
| health.severity 病情轻重 | V9.0计分，V11模板 | data/templates/health_severity_vnext/reading_template.json | NativeReadingRouter → NativeVNextEngine → PythonVNextVerbatim |
| health.discomfort 伤病在哪里 | V27 | data/templates/health_discomfort_v11/native_discomfort_v15.json | NativeReadingRouter → NativeDiscomfortV15 |

V9.0是保留原V8基础计分并增加有来源、按真实亲属条件取用的长幼辅助扩展。无该辅助角色时内部审计仍报告基础V8 policy；这不是落回旧客户模板。V11的JSON `version` 已标V9.0，schema标V11。V27的V11目录/V15文件名是兼容路径，不代表运行旧病位规则；不要为改名破坏历史工具。封存不等于临床有效性、签名真机或上架验收。

## 手机接线与版本阻断

- WenguaDesignPreviewApp真实入口采时 → NativeCore真历算 → NativeReadingRouter按两个主题分流 → 对应独立规则 → NativeCustomerView。病位不进入轻重计分。
- 手机现有两个主题启用，其余领域未验收仍开发中。人物关系、可选真实年命、亲属确认、伤损六条件、30秒静心、15天同一事项锁及本地保存沿原UI传递；本轮没有重构UI或改变规则。
- 轻重桥接在载入模板时严格核验V11 schema、V9.0 version及封存状态；病位Python/Swift严格核验V27 schema和封存状态；缺失/旧模板报错，不能回退固定样例。未支持主题先阻断，不能悄入轻重。
- 正式轻重DTO版本改为 `health_severity_v9_scoring_v11_template_frozen_20261102`；V27输出版本仍为 `discomfort_v27_ding_gods_inner_outer_hour_20261101`。旧本地历史记录保留原版本，不强行改写。
- project.yml显式打包200格、81格、24人物、轻重V11、病位V27、255来源、三源干象与封存清单；构建只读取现役源位，不从Important或archives导入。
- 封存清单记录正式资源与生产源码SHA256；Important双镜像仍以Git blob SHA逐字校验。之后变更封存内容须按用户授权建立新版本，不能偷偷改本封存版本。

## 旧模板清退

现役 `data/templates/` 只保留上述两份。23份旧模板、草稿、固定样例从原位清除，转入 `archives/retired_health_templates_20261102/`；INDEX.json逐一保存原位、归档位及原内容SHA256。原著、案例、已封存输出和全部失败日志未删除。旧历史模块显式读归档，仅供复现，不成为生产fallback；不删除旧测试、不批量skip。

Important内已退役模板的冗余镜像同时删除，MANIFEST删除对应条目；两份正式模板及新封存清单双镜像同步。旧设计文档与旧CI存档仅代表当时状态，不再作为当前版本导航。

## 验收与已知边界

新增：`verify_frozen_health_release_20261102.py` 验证封存SHA、23份归档SHA、原位已清退及App包JSON/TSV精确白名单；向模拟包放入旧模板应明确失败。新增Python错误schema/未封存拒绝回归。

新增原生 `NativeFrozenHealthBundleCheck.swift`：使用真正Xcode生成的问卦.app资源，真实历算哥哥/妻子各一盘，对两个正式Bundle路由执行4次调用，验证输出主题和封存版本；不拿直接调用数据函数冒充Bundle接口。保留已有Python/Swift逐字、六伤损条件及1080数据验收。

实际CI结果须在完成后追加，当前没有以旧run冒充本轮通过。

清退首轮全库835项实跑43 failures/88 errors/3 skipped，新增异常来自V20/V21用DATA目录拼接旧模板的两处读取遗漏；已改为显式归档文件，保留本段迁移失败记录。原始本轮日志 `/tmp/wengua-seal-full-tests.log`；修复后另跑全库，结果另记。更早基线831项41 failures/11 errors/3 skipped与旧V7.4失败仍保留，不能宣称全库全绿。

## 旧版自动任务退役

下列旧模板构建/预览工作流保留手动审计入口，清除push自动发布触发，防止已经退役的模板重新生成并回写main。这不是删除测试或抹去历史失败；当前Python、原生计分回归、Xcode与双路由验证继续自动运行。

- .github/workflows/build_self_gengshen_v25.yml
- .github/workflows/health_v31.yml
- .github/workflows/health_v38_customer_tomb_void_random2.yml
- .github/workflows/build_father_health_v24.yml
- .github/workflows/health_v40_symbolic_score_experiment.yml
- .github/workflows/health_v39_concise_presentation_random2.yml
- .github/workflows/health_v40_score_archive.yml
- .github/workflows/health_v37_all81_double_risk_noon.yml
- .github/workflows/health_v41_all81_full_archive.yml
- .github/workflows/health_v32_two_new_cases.yml
- .github/workflows/health_v78_conditional_palace_native_parity.yml
- .github/workflows/health_vnext_conditional_review.yml
- .github/workflows/build_health_v20.yml
- .github/workflows/health_v79_generalized_cohost_native_parity.yml
- .github/workflows/health_v42_full_unified_archive.yml
- .github/workflows/health_v77_unique_palace_native_parity.yml
- .github/workflows/health_v34_full_rules.yml
- .github/workflows/health_v33_all_cases.yml
- .github/workflows/build_health_severity_v19.yml
- .github/workflows/health_v28.yml
- .github/workflows/health_v74_colleague_natal_year_audit.yml
- .github/workflows/health_v35_patient_priority.yml
- .github/workflows/health_v42_unified_5_case_regression.yml
- .github/workflows/health_v75_two_fixed_clocks_parity.yml
- .github/workflows/build_health_v21.yml
- .github/workflows/health_v30.yml
- .github/workflows/build_father_health_v23.yml
- .github/workflows/build_self_gengshen_v26.yml
- .github/workflows/health_v76_real_native_parity.yml
- .github/workflows/health_v11_six_real_complete_preview_20261031.yml
- .github/workflows/health_v41_book_81_source_gates.yml
- .github/workflows/health_v36_actual_source_rules.yml
- .github/workflows/build_health_severity_v22.yml
- .github/workflows/health_v29.yml

本地最终完整测试：835 tests，41 failures、11 errors、3 skipped，与清退前相同52条历史失败/错误标识，新增封存4项均通过。迁移中曾有一份Important镜像尚未同步导致42 failures，已同步并复跑恢复41；历史算法断言不改、不隐藏。修复后旧V20/V21路径回归通过。当前CI名称也明确显示V9/V11与V27，现役parity不再向交接文件反复追加过时V10.1模板标识或未展开的run变量。

旧任务退役续审：共38项统一为单一workflow_dispatch。首提交旧V4.2工作流发生重复workflow_dispatch键的GitHub配置失败 #41452840714，现已修复并用拒绝重复键的YAML loader核查全目录；补退役V3.9.1及历史V2.7自动归档。该失败保留，不涉及封存模板或规则改变。

独立iOS Offline Native Casting #41452844599 的编译/逐字步骤通过，但两个归档写回步骤失败：生成的未提交测试文件阻止pull，以及多人工作流同时push争用main。新增只用于审计提交的autostash rebase＋5次push重试；不改产品规则、不隐藏真正冲突；保留原失败，后续以新run确认。


### 2026-11-02 · 两主题封存正式最终验收完成
- 用户指定并封存：疾病轻重 **V9.0计分＋V11模板**；伤病在哪里 **V27**。正式清单 `data/releases/health_frozen_20261102.json`，接口/清退记录 `docs/HEALTH_PRODUCTION_RELEASE_20261102.md`。V8基础计分及V9已有条件扩展均未改。
- **真正macOS Xcode #41454559739 success**（源码 `9094e763cac2a2ecb7ac1bdbd7773962592ca1c1`）：完整SwiftUI Simulator编译、200/81/人物/两模板/255/三源与封存清单实际包内字节白名单、两主题正式Bundle路由哥哥/妻子共4次调用、Python/Swift全文逐字、4时辰×6伤损条件、1080数据集全部通过。原样全文 `docs/IOS_V80_XCODE_PASS_RUN_41454559739_ATTEMPT_1.md`。原任务 #41452844633 长时间未分配runner，仅取消重复排队，不伪称该run执行通过。
- 独立 **iOS Offline Native Casting #41453149593 success**（含真实App Xcode构建及全部独立原生回归）；最新源码主CI **#41453149251 success**（Python3.11/3.12）、轻重原生逐字 **#41453149280 success**。审计提交的dirty生成文件＋并发远端变更，本地临时bare仓库真实复现修复通过。
- 23份旧模板/草稿/固定样例清出正式目录，原内容SHA无损归档；旧模板冗余Important镜像清除，当前两模板和封存清单双镜像/MANIFEST同步；38项旧版自动构建/预览改手动审计，原测试与历史记录不删。现役自动parity读取实际封存版本写交接，不再回写过时V10.1标识。
- 全库835 tests仍41 failures、11 errors、3 skipped，与此前相同52条历史失败标识；当前正式门槛全部通过但不能称全库零失败。迁移早期旧路径遗漏、镜像同步过程失败、旧workflow重复键 #41452840714/#41452954223 与归档写回 #41452844599 均保留记录，不以删除失败求全绿。
- 这是unsigned Simulator及软件接口验收；没有签名iPhone真机/App Store交付。用户已安装旧App不会随GitHub提交自动更新，需使用本封存工程重新构建安装。


### 2026-11-02 · 按序清账52项与规则复核，工程补丁p1
重新完整复现835项的41失败/11错误，原日志和每项断言/代码行/来源/复现命令写入 docs/audits/health_cleanup_20261102/；当前839项仅剩2个手动真实时辰功能失败，0错误、3原有skip，50条基线问题已验证处理，未删测试方法或增加skip/xfail。所有迁移测试原文件按SHA无损保存，不拿旧V7规则要求改当前评分。
真实缺陷：_quantize_one地盘本征审计误用循环末尾bottom，坤二戊地盘误记中五丁、空pairs崩溃；只改为ordinary_bottom，四张原时辰分数和完整中文SHA不变。两模板/200/81/人物/Swift与计分策略未改，原封存manifest归档，现行manifest明确engineering_p1。
第二阶段360真实时辰/1368物理关系组只读复核及1080物理组合清单已留证；同宫不同力量和实际奖励归因可正确区别，弱天芮泄耗/特殊宿主名单仍待来源核定，不自造量化表或改分。第三阶段真机清单 docs/IOS_TRUE_DEVICE_ACCEPTANCE_PENDING_20261102.md 均标未执行：当前无实际iPhone连接或Apple签名，已询问用户设备条件。手动入口缺口仍真实失败保留，按原顺序后续处理。新Swift/Xcode/包内资源CI待本提交实际结果，不拿旧run代替。


### 2026-11-02 · 清账与p1工程补丁正式验收完成
源码f8d1b1e0c0af5db51cadbcdcc3ab83fc3dd265d1：主CI #41460321192（Python3.11/3.12）、轻重原生逐字 #41460320478、独立iOS编译/原生回归 #41460320720、正式macOS Xcode/实际包资源SHA/四次Bundle路由/V27逐字/六伤损条件/1080数据 #41460320838 均success。新Xcode原始全文 docs/IOS_V80_XCODE_PASS_RUN_41460320838_ATTEMPT_1.md，未用旧run替代。
完整本地839 tests的2 failures/0 errors/3 skipped单独保留，不能声称全库全绿：两失败均为手动真实时辰入口缺失；三skip原已存在（可选Moshier软件交叉参考未安装，V7.7/V7.8两历史class版本门槛），本轮未增加skip或xfail。原52条逐项账、修改前测试原件/SHA和完整失败日志均可复现。四原时辰分数、完整中文SHA及两个模板/200/81/人物/Swift源码pin未变，唯一冻结源位改动是ordinary_bottom地盘审计字段，manifest明确engineering_p1并保留前版原件。
顺序进度：1）50条已验证解决，另2条功能缺口按第4步保留；2）360真时辰及1080物理组合复核完成，弱病泄耗/特殊宿主来源未核定不改分；3）真实iPhone无连接/签名/用户实测，验收清单已备、仍全部未执行；4）手动入口尚未实现，不越过真机条件伪报已交付。


### 2026-11-02 · 用户要求奇门论疾首页实际摘要与统一名称（p2）
实际根因：Premium卡仍读旧06_conclusion，V27真实结论是09_conclusion。现首页直接读取同一V27结论，首句金色突出主位，余下症候/旁证完整接入；不独立算分、不虚造次病位排序。产品入口、结果卡、历史统一“奇门论疾”，内部health.discomfort/存储/15天键不变，完整原始断词及已保存V27快照不改。用户截图仅UI回归文字，无时辰不补盘。详见 docs/IOS_QIMEN_LUNJI_FRONTPAGE_20261102.md。
工程manifest明确p2，原p1清单归档；只有3份生产UI源pin变化，V9/V11与V27模板/200/81/人物/规则源码逐字不变。专项25通过，全库841 tests仅原2个手动时辰失败/0错误/3原skip；新增真正Swift摘要适配器与两张native JSONL运行验证接入正式Xcode。Important镜像/SHA同步。实际新CI/Swift/Xcode结果待本提交完成后另记，不提前称通过；病愈应期仍后续重点，不因UI修复改变或开放未验收应期。


### 2026-11-02 · 奇门论疾p2首页接线正式验收完成
正式macOS Xcode #41469280778 success，源码9b9a2606934c32a68022bd1669d3556bea4202ad：完整双架构Simulator App构建、封存实际包内资源检查、哥哥/妻子两个主题共4次Bundle路由、Python/Swift全文逐字、六伤损条件及1080数据检查通过。真正首页适配器运行检查同时通过截图原文、错误06字段陷阱、缺失/空白/错误主题阻断和2份真实V27 native结论，日志 docs/IOS_V80_XCODE_PASS_RUN_41469280778_ATTEMPT_1.md。最新共享原生 #41470986685（含真实病位首页运行）、主CI #41470986700 success，源码5da7fc7e；独立iOS完整App编译 #41468305381 success。工作流/记录后续变更未改生产源码或资源pin。
早期 #41468305370 顶层failure、job cancelled、无任何执行步骤，GitHub原注释为“The job was not acquired by Runner of type hosted even after multiple attempts”，另报macOS arm64容量限制；不是代码编译失败，原记录保留。#41470986648/#41470987628为正式运行启动后取消的重复排队，不称通过。
本地841 tests仍2 failures/0 errors/3原有skip，保留手动真实时辰入口缺口；专项25项、封存SHA和Important镜像通过。此次仅改首页真实09结论展示及产品名“奇门论疾”，两模板/计分/详细断词不变；旧V27记录兼容。未作签名真机或全套XCUITest验收。更新代码后重新⌘R才能看到新UI；病愈应期仍待后续独立研究。


### 2026-11-02 · 用户要求简明病位、静心木鱼动画与Swift警告清理（p3）
奇门论疾首页只保留真实09结论的首句；“先从伤门落宫看”展示为“先看”，例如“本次因属伤损，先看右侧肋腰一带”。天禽伏吟、胃刑墓及检查核实等后续段落留在专业解盘；原始V27全文、人物、强度、分数和模板字节不变。新WenguaMeditationView以原生Canvas/Timeline绘制小和尚闭目敲木鱼、槌臂、声纹与诵念文字，无联网/外部素材或自动声音；尊重减少动态效果及后台暂停，倒计时和确认时刻起局/15天限制原守门不变。
按截图及前轮实际编译日志清理未用companion/witnesses/secondary/sourceSites/ending，macro仍保留try验证仅不绑定无用值；map/filter闭包显式括号、iOS17双参数onChange，正式Target启用SWIFT_TREAT_WARNINGS_AS_ERRORS=YES，CI增加实际生产Swift零警告验收，不关闭警告。原警告、封存p2清单、全库日志无损保留；现行manifest明确p3，所有7份规则/模板资源SHA及Python/评分源码不变，Important双镜像/MANIFEST同步。
本地专项8项通过；完整843 tests仅原2个手动真实时辰入口失败、0错误、3原skip，原日志 docs/audits/ios_meditation_p3_20261102/python_unittest_full.log.gz。实际Swift运行、macOS Xcode及bundle验收等待本提交Actions，不提前称通过。详见 docs/IOS_QIMEN_MEDITATION_WARNINGS_20261102.md；病愈应期继续待后续研究，未开放。


### 2026-11-02 · p3简明首页、静心动画及Swift零警告实测完成
生产源码f7c0ab453f3d295abf6db4cd1f946d93a09b4211：正式macOS Xcode #41474512486 success，Swift源码警告0，正式Target以警告即错误编译；实际App资源SHA/白名单、哥哥/妻子两主题4次Bundle调用、V27全文逐字、全部6伤损条件及1080数据集通过。完整原日志 docs/IOS_V80_XCODE_PASS_RUN_41474512486_ATTEMPT_1.md 含PASS SWIFT_PRODUCTION_WARNINGS_ZERO和PASS QIMEN_LUNJI_FRONT_PAGE。
共享原生 #41474512713 success：首页普通/伤损/剧痛简明文案、真实两张V27输出、保留完整原reading、木鱼周期/停止状态实际Swift运行通过；主CI #41474512568（Python3.11/3.12）与独立iOS真实App Xcode/全部原生回归 #41474512484 success。本轮这四个Actions均无失败；全库843 tests原2个手动时辰入口失败与3个原skip另行原样保留，不称全库全绿。
README、Important字节镜像/Git blob SHA及封存p3清单已同步。两个模板/7份规则资源/Python/评分源pin不变。没有进行真机签名、动画截图或整套XCUITest像素/按钮验收；动画为本地矢量与诵念文字，默认静音。Mac须按README pull后重新xcodegen generate并⌘R，将新增动画文件加入现有工程；历史V27结论直接使用新首页展示。病愈应期尚未开放。


### 2026-11-02 · 用户明确手动时辰为计划事项择时，候选合组（p4）
本轮用户授权当前问事/未来事项时辰两种模式，中文年月日时分滚轮、发生地IANA时区、1至6候选一组；用户答复确认“一次静心后并列比较，15天只登记整组”。按输入真实时刻逐一计算完整九宫，全部成功后一个编码值保存再登记一次15天回执，失败不保存半组。历史兼容旧单条，区分实际完成时间与未来事项时间，并支持组内切换。
首页手动健康盘显示“此时辰：”加同一真实盘V9/V11原文等级；V27病位原文不改，独立健康等级依据保留在专业解盘。新“挑日子·按事项时间排盘”仅提供旅游/约会/结婚/手术等真实候选盘，专项吉凶尚无验收规则，明确待核，不能套疾病分或声称手术更安全。出行章例1、6的计划起飞时局来源已复核，见 docs/IOS_MANUAL_EVENT_TIME_20261102.md。病愈应期未开放。
p3清单/原5份测试逐字归档；现manifest明确p4，7份已有展示/DTO/工程源pin与新增2时间源；两封存引擎、7份模板/规则资源及Python计分字节不变，Important双镜像/MANIFEST同步。专项32项通过；完整单测、真实Swift、Xcode零警告与bundle本提交新验收待实际完成追加，不引用旧run代替。此次无新原书章节/案例或临床有效性证明。


### 2026-11-02 · p4手动事项时辰、候选组与等级接口最终实测完成
正式macOS Xcode #41479754723 success（生产源4ee16bca3334b4203551218215fea2fee32a1c63）：完整App编译、Swift源警告0、实际包内SHA白名单、两健康主题4次Bundle路由、V27逐字/6伤损条件/1080源盘检查通过。新手动时辰真实执行通过当前/选中时刻区分、两张未来时辰完整历法与九宫复现、同盘同人物V11等级、跨时辰/人物/领域拒绝借分、DST重复时刻、无效候选、整组一个存储值、旧单条兼容；两盘健康章节/全文/用神宫位独立Python与Swift逐字相等。原始日志 docs/IOS_V80_XCODE_PASS_RUN_41479754723_ATTEMPT_1.md。
同一生产源码/资源pin、仅CI配置后续变化的7403dbbe：独立 iOS Offline Native Casting #41481224006（全部6 jobs，含完整真实App Xcode）、轻重与病位摘要原生 #41481223986、Python3.11/3.12主CI #41481223879 全success。完整本地846 tests 0 failures、0 errors、3既有skip；此前两项手动时辰真实缺口已交付，原测试与失败历史未删。Important双镜像/源pin/SHA验证通过。
中间真实编译超时失败 #41478402093及镜像同步前1条失败原日志保留，已修复后复验。排队重复/被最新源码替代的 #41478154115/#41478154090/#41479119490/#41479744446/#41479969232按实际cancelled保留，不冒称运行通过；#41479156312虽曾取消接口返回500，其实际后来success，亦按实际记录。没有签名真机或全套XCUITest/滚轮视觉手测；这次没有生成秘密盲测或医疗安全证据。
用户使用：普通问事选当前；有计划选事项时辰，通过滚轮和发生地时区填1至6候选，一次静心后同组切换，15天只登记一组，历史也可对照。健康等级仅为同一事项传统盘象，不代表全天万事吉凶；旅游/约会/婚礼/手术专项择时评级仍待核，只提供真实排盘，禁止借疾病分宣称手术安全。病愈应期仍未开放。README已更新入口、限制及本轮实测链接；Mac按其说明重新XcodeGen后⌘R查看。


### 2026-11-02 · p5各领域预定时刻/选吉日接口分离、分项排版与有效输入
用户要求已实际实现：首页独立挑日子入口删除；15领域各有elective预留子项（健康看病/手术、出行旅游/出行、婚姻约会/结婚等），选吉日后续独立开发不进普通全文。所有普通专题支持当前/已预定时刻真实排盘，健康两专题解读已接，其余清楚标开发中，不借疾病分。共用WenguaDomainContract及最终净分11级尺度，模板决定对象/条件；当前健康通过原封存引擎适配，不重写任何计分或定位。
长段落按病位/星门神/天干/天地格/本宫条件/另宫刑墓分块短行，源runs逐字可重组完整原文。选择时辰不再有默认预览/偏移行，显式打开、确认后才可起局；普通流程只选已定时间，多候选专用选吉日接口后续独立接。移除不参与引擎的必填描述及四字门槛，结构化专题/当事人摘要承接15天限制，旧记录/孤立回执保守保留剩余窗口，不清历史。
p4清单与6份测试原件/SHA归档，现行manifest明确p5：9个既有展示/DTO/时间/工程源pin及新增排版源；两专题schema、7份资源、评分/定位原生与Python源码不变。Important镜像/SHA同步。专项15通过；完整849 tests 0失败/0错误/3原skip。首轮1条旧CTA契约失败原日志保留后按本轮用户授权迁移，无删测试/新skip。新Swift实际运行、Xcode零警告与包内资源待本提交Actions结果，另追加，不拿p4旧通过充数。详见 docs/IOS_DOMAIN_LAYOUT_INPUTS_20261102.md。病愈应期与各域专用评级仍后续开发。


### 2026-11-02 · p5领域内接口、分项排版及真实输入最终验收完成
生产源0c8a668daee84a952f4f9696bb35dbed20591088：正式macOS Xcode #41494696931 success，完整App编译、Swift源警告0、实际包内资源SHA/白名单、两主题4次Bundle路由、V27逐字与6伤损条件/1080源盘通过。新增PASS DOMAIN_UI实测15领域普通预定时刻、15个electiveReserved阻断、共用最终净分等级、V27每节分项runs原文重组、旧描述和孤立回执限制；同盘同人物健康全文/用神宫位Python与Swift逐字相等。完整原日志 docs/IOS_V80_XCODE_PASS_RUN_41494696931_ATTEMPT_1.md。
同源主CI #41494641830（Python3.11/3.12）、原生轻重/病位摘要 #41494641874 success。独立iOS #41494641926 attempt2 success：原5项Foundation原生成功保留，独立完整App重跑成功，合计6 jobs均success。其attempt1长时间排队，在取消操作与刚分配runner之间发生竞态，中断了刚开始的App步骤；已如实重跑该job，原cancelled记录保留，不称attempt1通过。重复排队正式任务 #41494641971 cancelled，未虚报执行通过。
本地专项15项与完整849 tests 0失败/0错误/3原有skip；首轮旧CTA断言1条迁移失败原日志/原测试SHA继续保留，无删除测试或新skip。p4清单归档、p5源pin及Important镜像/MANIFEST同步通过。V9计分/V11、V27模板和原生/Python数学源码与7份规则资源未改；仅做UI/接口/输入与历史承接。没有新增章节/病例、签名真机、全套XCUITest或像素视觉手测，不将文化盘象说成科学预测有效性。
当前入口：首页仅领域；领域内普通问事可当前/一个已定时刻真实排盘，15领域各有选吉日预留项，暂不进普通完整解读；只有健康两专题已接评级/解读，其它模板逐步开发。专业解盘分块分短行，底层断词原文不删。手动入口只显示选择时辰，明确确认才使用；必填自由描述已移除、15天旧限制保守承接。README已同步。本轮可按README重新生成Xcode工程后⌘R检查实际UI。


### 2026-11-02 · p6准备页、普通／选吉日时间边界及截图排版修正
用户最新要求覆盖p4/p5普通双模式：普通问事仅当前确认时刻，15领域选吉日仅未来预定时刻，界面和原生resolveForTopic双重约束；选吉日现在可真实排盘，专项评级仍待开发，不借疾病分。准备页先显示，点击后页内填写，删除自动弹窗；表单统一容器、关系与下拉标题上置；年月日时分五列滚轮含闰日／DST与未来校验。坤二小标记overlay不挤偏天干；四柱标签下置、方向替代重复时刻栏；伤门／结论分组段落、源原文完整；宫位标题居中、清技术标签、放大角色。
p5清单和7份原测试／脚本及SHA归档，p6仅8份既有展示／DTO／时间／工程pin和新增准备页源，V9/V11、V27、Python数值与7份资源保持字节相同，Important镜像同步。完整回归首轮855项1条旧段落格式契约失败保留后迁移；最终全量及实际Swift／Xcode／bundle待执行结果追加，不拿p5旧通过充数。无删除原测试方法／新skip；无新增章节病例、签名真机或像素视觉验收。详见 docs/IOS_SETUP_PALACE_UI_20261102.md。

本地最终完整回归855 tests：0 failures、0 errors、3既有skip；专项33项通过。原失败和最终原日志／SHA已存docs/audits/ios_setup_palace_ui_20261102/，未删除旧测试或新加skip。实际Swift与Xcode仍待本提交Actions执行。


### 2026-11-02 · p6截图界面与独立时间模式最终验收完成
生产源d594d5d6a0423b04bbafe11318357018286b80cc：正式Xcode #41502545254 success，完整iPhone Simulator App、零Swift源警告、实际包SHA／资源白名单、两主题4次Bundle路由、V27逐字／六伤损／1080源盘通过。PASS SETUP_UI实际执行15领域普通仅当前、15领域选吉日仅未来的双向拒绝、五列公历对应的闰日／DST缺口／重复时刻、两张真盘×六伤损分支的逐节原文／段落重组；同盘同人物健康Python／Swift全文逐字相等，旧分组、孤立回执及15天限制保留。原日志 docs/IOS_V80_XCODE_PASS_RUN_41502545254_ATTEMPT_1.md。
同源独立iOS #41502545252 全部6 jobs success；主CI #41502544972 Python3.11／3.12 success。原生轻重／病位首页最终独立 #41503297213 success（5be81c80，仅历史文档后续变化，生产源码、资源、manifest与d594d5d6全部一致）。完整本地855 tests 0失败／0错误／3既有skip，专项33通过；旧测试与失败原日志／SHA保留，无删除测试或新增skip。结果总表 docs/audits/ios_setup_palace_ui_20261102/final_ci_results.json。
中途原生 #41502544938 attempt1／2的全部计算与逐字步骤成功，但自动审计文档尾部rebase冲突使workflow实际failure；两次完整原日志保留。由最新main独立dispatch #41503297213后完整计算及归档均success，未覆盖旧失败。旧源／冗余正式 #41502335031／#41502344251／#41502555446、旧独立iOS #41502334854在确认剩余App任务尚queued后取消，按实际cancelled保留，不称通过。
准备页先显示，按按钮进入页内表单；普通只当前、选吉日只未来；五列年／月／日／时／分，表单标题上置无重复；坤二刑墓overlay、四柱下置标签、方向栏、伤门／结论分组、宫位标题居中及角色放大均已编译接入。V9/V11、V27数学与模板及7份资源逐字未变。选吉日的专用吉凶评级／多候选筛选继续开发；当前只真实排盘。README及Important镜像同步。本轮无新原书章节／病例、签名真机、像素视觉手测或全套XCUITest；Mac须重新XcodeGen后⌘R查看实际界面。
