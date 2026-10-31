# 2026-10-31 V11 朋友与家属用神分流、完整断语恢复审计

## 本次授权与冻结边界

用户明确更正：朋友与兄弟姐妹不是同一关系。朋友病情以**实际起卦月干**代表患者；性别及相对于求测人的长幼均不要求、不影响患者用神，不选择震三/巽四/艮八/兑七，也不选择乾坤亲属辅助宫。提供真实年命时可按既有年命规则另参，不提供不能捏造。哥哥/姐姐/弟弟/妹妹则是**确切家属身份**，月干为主，允许按关系审核确定的震三/巽四/艮八/兑七排行辅助。父母/祖父母严格按已核长辈乾坤选择，不拿普通朋友性别自动增宫。

本次**没有重写 V8 200格、81格、5×5 克病矩阵与加减分**。已有独立家属辅助成为真实选中角色时才参与对应物理宫计分；同一物理宫基础分仅计一次、不同真实符号力量必须分别查源、同符号多身份不得自己反复计票。生/被生/比和不得杜撰无源新分。旧 V9 4种朋友配置留在 Git 历史，不抹除旧失败或原书。

## 从原始六盘预览发现的复现问题（用户上传 v90_six_real_cast_previews.txt）

- 2026-12-03 17:30 EST、丙午 己亥 辛亥 丁酉、女性年长朋友：旧 V9.0 居然有 sibling 巽四宫天心星，为朋友增加亲属辅助；**预期**只有己月干患者宫，无兄弟姐妹辅助。新 V11 Python 绑定和 Swift 绑定都不再选此角色；BigFish 全人物循环只生成一个朋友配置。
- 2026-11-16 10:30 EST、丙午 己亥 甲午 己巳、男性年轻朋友：旧预览患者源强显示 None，不能使用宫位分数替代源力量；待单独核对200格与限制。旧例中“本时不犯五不遇”和“时局”等是传统象意，不能当医学证据。
- 2026-12-01 哥哥、2027-01-29 姐姐、2026-11-18 弟弟、2027-01-27 妹妹，已有真实月干+辅宫样本；四种关系辅助来源宫为震三、巽四、艮八、兑七。辅助有时与天芮、天心或其他已选符号同宫同符号，完整展示用神角色但基础宫分与同一符号不可重复叠加。
- 旧 V10.2 综合断语只有一段天芮、患者、天心/乙奇速记，缺时干/年命/值符/实选辅助的来源身份与对病宫真实作用；且未给患者独立源强。V11 在**保留 V10.1 逐用神完整宫位段、81格、空墓刑迫和真实宏观时局**的基础上，将以上真实独立角色按强度、落宫、作用恢复到综合断语，不将内部分数、条件矩阵、加分数字告诉客户。已见结局不能被当作盲测。

## 代码落点

- 朋友绑定：`src/wengua/health_dynamic_v21.py:bind_patient`、`data/knowledge/phrase_library/health_v20/actor_profiles.json` 的 friend；iOS `WenguaNativeActorBinding.swift:bind`、`WenguaDesignPreviewApp.swift` 朋友选择/校验；BigFish `scripts/wengua_bigfish_518400_offline_editorial_20261029.py:all_signifier_configs` 与 `build_inquiry`。
- 家属辅助实际落宫和完整200格/宫基础/克病独立作用：`src/wengua/domain_selected_energy_vnext.py:selected_health_sequence` 的 sibling；`src/wengua/health_quant_overlay_vnext.py:inspect_selected_quantization`；`ios/WenguaAppUI/WenguaNativeVNextEngine.swift` 的 sibling 选用、每个 physical 去重和控制条件。
- V11 模板与双端语序：`data/templates/health_severity_vnext/reading_template.json`、`src/wengua/health_reading_template_vnext.py`、`src/wengua/domain_selected_energy_vnext.py:selected_health_sections`、`ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:sections`。
- 本次专项真实时辰测试：`tests/test_health_v11_friend_family_aux_20261031.py`，已加入 main CI；BigFish 26组当前人物取用测试在 `tests/test_bigfish_all_22_signifiers_loop_20261031.py`；原著复核及早期失败记录不被覆盖。
- 源文件镜像：`Important/python`、`Important/swift` 与 `Important/MANIFEST.json` 依源码 Git blob SHA 同步。

## 验收门槛与未解决问题

1. 实盘朋友无性别/长幼与显式填写旧信息，必须在同一时辰同用月干、同宫、同结论、同全文且绝无 sibling/gender 辅助；真实兄姐弟妹需选择对应独立辅宫并只计一次物理宫分。
2. 检查 Python 源断词与 Swift iOS 同时辰**逐字一致**，不得用固定旧盘替换实际起盘；旧 V8 已见两例只能作为冻结回归，不得调整规则迎合结果。
3. Python 主 CI、BigFish 全人物循环、Swift native parity、macOS Xcode Simulator 编译与 bundle 资源必须分别提供实际 Actions 结果，不能因一项通过就声称全部通过。还须复核本审计记录的「患者力量 None」成因、某些弱天芮受生泄耗奖励是否有书源、同宫多角色的克病归因。
4. 软件仅作古籍象意研究，不作为临床诊断、医疗建议或康复预后。任何应期必须来自真实空墓冲合和时局条件，不能仅因马星定日期。

## 历史兼容

V9 friend 四分支、V10.1、V10.2 原叙述及相应失败测试仍留在 Git 提交历史；当前回归更新为 V11 目标是版本升级，不把历史运行结果涂改为当次通过。若新版 CI 失败，需保留失败链接与具体错误，再补独立修复记录。
