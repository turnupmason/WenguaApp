# V8.0 疾病计分 + V10.2 疾病断词正式双冻结基线（2026-10-28）

## 用户明示冻结
2026-10-28 用户明确说：“现在目前封存这两个，以后就使用了。不变了。如果以后再需要修改再说。”解释为两个当前正式软件基线：
1. 疾病轻重 V8.0 的真实起盘事实、人物用神、200格力量、81格、五行生克、宫位净吉凶、空亡真/假、天显/五不遇时、独立克制5×5、特殊同宫吉助及原±5总结，不作推断性调参。
2. 疾病轻重 V10.2 的最新客户断词模板与 Python/Swift 原生一致性，包括时局、完整九宫详情、短综合断语、独立应期文本。schema `health_severity_user_editable_template_v20261028_v10_2_evidence_first`。

**往后所有日常开发不得擅自修改这两套基线；如将来用户明确提出改动，要先获得用户对具体规则/模板的批准，另开显式版本，保留当前冻结文件原貌与独立逐字回归，不在当前用户审查计分规则期间私自修复。** 用户让审查/指出疑点不等于批准修改。可以继续开发其它领域/界面，但不得暗改 V8 与 V10.2。

## 实际源码 Git Blob SHA 冻结快照
基于本次审查时 GitHub main SHA `f0c3584d1f32d64898ff72dda21787574300b4b1`。以下是仓库文件本身的 SHA（Git blob，不是普通 SHA256）：

| canonical path | Git blob SHA |
|---|---|
| src/wengua/health_quant_overlay_vnext.py | `9e064a9d16e6061a88d433c206549244b527c3c9` |
| src/wengua/health_five_level_quant_vnext.py | `1e2fdd89ae8327336e51f9327dcd3b2a45cbac65` |
| src/wengua/user_domain_matrices_20261023.py | `b99b28562ac87c3e8210232255db97b6e79b9453` |
| src/wengua/health_intrinsic_scoring_vnext.py | `da392b140f8d95e86ad3f6f506c34738d6c4ad0f` |
| src/wengua/health_macro_facts_vnext.py | `2f619a2a18256eec432b07d904d4b409e1dcae11` |
| src/wengua/domain_selected_energy_vnext.py | `8be9a8723788e4324551bf7aef49e20f7732a752` |
| src/wengua/health_palace_detailed_vnext.py | `0be6c308bea6355d1f85a2d66723e68ea4374730` |
| ios/WenguaAppUI/WenguaNativeVNextEngine.swift | `5f7f7925606c7f3dc755cd947f841c7720093a13` |
| ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift | `ee691c98607cd83e2e3c0dfe6ef85cfe56be1007` |
| data/templates/health_severity_vnext/reading_template.json | `33f844566b8ac10e47aee69f7ea8c05909779c5d` |
| data/mobile/health_vnext/health_energy_200.json | `1d9f75c913bcba2c607f327beda18bfba9fab84a` |
| data/knowledge/health_81_excel_20261025/81_pairs.tsv | `10338e0433a25140e8749f574e504320ada7e831` |
| data/knowledge/phrase_library/health_v20/actor_profiles.json | `943d74dfb05f00d1be2f4e44dc9ae44ab6ae3e29` |

Important双镜像和MANIFEST依原canonical按此前已验版本保存，不能因此次文档冻结而擅自变动。

## 本次看到的冻结规则审查疑点（仅记录，不改源，不宣称BUG已定）
- `src/wengua/health_quant_overlay_vnext.py` 的 weak_disease 分支：当病星200源强为「极小」、对方角色关系判为「被生」时，每一个独立外宫给疾病“泄耗”+3；是否有核准古籍来源和应否将「病星弱」与「对方真实被生」等同于疾病受到有效泄耗，需用户下一次专门确认，不能凭猜测删改。
- `src/wengua/user_domain_matrices_20261023.py` 真空受力病宫表大多数格为「完全失控」；控制附加分须通过原真实5×5，故「病宫逢真空」**不保证**自动+5。其语义是否符合冻结规则，需对照用户授权原表逐格审查。假空/真空/双方同时空亡条件不能混用。
- `src/wengua/health_five_level_quant_vnext.py` 中真、假空的宫位净分均使用「吉-3／凶+3」，只有克制矩阵与填冲应期区分；若未来用户要改变，请明确授权，不得现在偷偷替换。
- `src/wengua/health_quant_overlay_vnext.py` 中间阶段的历史注释提到旧V7、部分historical开关，**现行以 final_raw 真实计算**为准；不能拿注释里的旧示例代替现有正式逻辑。
- `src/wengua/health_full_role_network_vnext.py` 对真实独立符号图的某些跨宫生/被生/比和未提供新奖励矩阵，因此这些方向只保留事实；若未来开发域扩展，不得从疾病+3套用。
- 长辈选用与同辈朋友 status 依原用户确认表分别保留源书已验证、用户明确确认、书源类比和研究候选等级；不要把标记 `research_candidate_only` 的同事自动当作书源完整核准。
- 未单独提供出生年命不能推造；1920立春以前/以后与庚申年命不能据模糊年龄倒推。
- 这些仅为冻结代码阅读时的审计观察，没有在本轮通过新的数值变化测试，也不是科学医疗有效性证据。

## 冻结对应的真实验证（此前已完成，不以本次只读报告冒称新运行）
- V8 Python主CI #40794999872 PASS，原生Swift↔Python完整中文段落和V8现实宫计分 #40794999535 PASS，5个**已见**开发时辰5/5 EXACT MATCH，Xcode iOS Simulator实际编译与四源bundle验收 #40794999563 PASS；对应源码SHA `232c9f5c21eb9eb35a3bb8104ba02f5374b3c75c`。之后仅追加文档与审计，冻结文件blob SHA未更改。
- 旧独立 iOS Offline Native Casting Parity #40794999554 FAIL 仍须保留；不能宣称全项目无失败。签名真机/App Store、科学医疗预测准确性尚未验收。
- 完整逐字原版存档 `docs/HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40794999535_ATTEMPT_1.md`。
