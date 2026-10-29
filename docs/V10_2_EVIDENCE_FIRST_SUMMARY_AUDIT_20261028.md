# V10.2 疾病综合断语精简与原生接入审计（2026-10-28）

## 复现问题
V10.1真实原生随机五盘存于 docs/HEALTH_V80_SELECTED_POWER_TWO_FIXED_CLOCKS_RUN_40793239030_ATTEMPT_1.md。综合段虽对同符号乙去重，仍把天芮、天心、乙、患者、时干、值符、长辈辅助各宫分和关系重复读一次。用户要求精简自然中文，不改V8真实事实或分数。

## 本次仅修改客户显示层
- Python src/wengua/domain_selected_energy_vnext.py:selected_health_sections、Swift ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:sections 同构重写编号90综合段；模板 data/templates/health_severity_vnext/reading_template.json 新增 macros.summary_concise，schema health_severity_user_editable_template_v20261028_v10_2_evidence_first。
- 顺序为「病星实际宫及200源力量/签名宫象→患者实际真符号落宫与强弱条件→天心和乙奇各自200源力量、真实对病宫方向及原5×5是否真正有效→已核同宫吉助、泄耗、值符空亡」。病星空亡/患者真假空明确；同一乙兼医药/患者不复制乙强度方向；不同真实符号同宫不可合并强度；受限、不能制病绝不可断有效。
- 五不遇、天显、伏吟反吟已经在编号01时局总纲动态展示，编号90不再复述。时干、年命、值符、乾坤等完整独立实际事实留在原编号02-09宫详情和完整内审，不会因精简而损失、重算、改净分。
- V8唯一冻结基础、源200格、81古文、双方5×5、天显取整、假空真空、墓刑门迫、中五坤二、十档吉凶、原著和历史失败均未修改。旧V10.1版本在git历史和原归档保留。

## 新增验收
tests/test_health_v102_summary_20261028.py 重用五张固定的真实随机开发盘校验原V8分[5,0,5,-1,-5]不变、总结长度、关键双方真正源符号及无内部运算；另检查已见妻子乙兼角色。正式 Python3.11/3.12 CI、原生Swift逐章节逐字对照（五盘及原已见案例）、macOS Xcode Simulator打包模板/200/81/人物资源各需读取本轮真实 GitHub Actions 结果，不能预先宣称通过。旧版iOS Offline Native Casting Parity #40793239166 FAIL继续留档。
