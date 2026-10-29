# 2026-10-28 V10.1客户断词去重与五个随机时辰技术审计

- `data/templates/health_severity_vnext/reading_template.json:macros.palace_compact` 的用户尾句由「全部因素推断后，此宫为{grade}」改成「宫象{grade}」，消除开发者解释口吻；原81古文和完整生命阶段事实仍不改。
- `src/wengua/domain_selected_energy_vnext.py:selected_health_sections` 与 `ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:sections` 只在公众合断用（物理实宫，实际符号）检测重复：乙奇同为患者/医药只叙一遍真强度与同一生克，第二身份仍显示「同在坎一宫」；不同真符号/真实强弱、跨宫方向继续独立叙述。冻结V8原200格、81格、病宫加减分、辅助条件全部保持。
- V10.1 schema `health_severity_user_editable_template_v20261028_v10_1_concise_cohost_dedup`，更新正式Xcode验包、Python/Swift模板加载及Important双镜像MANIFEST，增加Python自动实盘去重回归。
- 本次用新种子 `202610282259` 生成首次5个技术有效盘、严格顺序父亲/本人/本人/女儿/朋友，不按结局抽样。Ubuntu真正Swift源盘与Python每章节中文逐字对照、5份全文及拒绝技术盘保存在专用CI动作和成功归档，不能复用已见案例冒称新秘密盲测。
- 新脚本/文档进入main不等于宣称通过：应看当前Actions实际成功或失败并保留所有失败现场；未经过签名真机和医疗预后有效性验证。
