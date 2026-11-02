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
