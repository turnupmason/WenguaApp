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

## 2026-10-31 实际 CI 追加记录（禁止覆盖旧失败）

- [主 Python CI #41222377904](https://github.com/turnupmason/WenguaApp/actions/runs/41222377904)：**成功**，包含 3.11/3.12 V11 朋友无性别/年龄、四类真实兄姐弟妹辅助、V8 25对源强及 Important 镜像回归。
- [BigFish #41222377667](https://github.com/turnupmason/WenguaApp/actions/runs/41222377667)：**成功**，原始 BigFish 24种身份源 / 26种实际条件配置；旧合称关系记录不被冒充当前实际人物。
- [真实 macOS Xcode Simulator #41222223461](https://github.com/turnupmason/WenguaApp/actions/runs/41222223461)：**成功**，Xcode 模拟器构建及应用包内 200格、81格、V11 模板与人物 JSON 资源验收；未做签名真机或 App Store 上架。
- [此前 Python/Swift 全文对照 #41222331008](https://github.com/turnupmason/WenguaApp/actions/runs/41222331008)：**失败留档**；该流程发现 2024-10-09 15:00 EDT 哥哥实盘辅助宫关系原字「受克」与 Swift「被克」不同。现已在 Swift 把辅助来源关系独立映射为原书用语「受克/受生/比和」，不改变五行克向、不改 V8 分数；纠正后须等新 Actions 真正通过再标完整一致。

## V11 最新复核追加

- [九盘真实甲干 Python/Swift 全文逐字一致 #41222507007](https://github.com/turnupmason/WenguaApp/actions/runs/41222507007)：**成功**。前次失败「受克」/「被克」原字已按原始 element_relation 统一；本次同时实测原始 25格施受力、同宫组合、Swift native 编译和 Important SHA。原失败报告仍保留。
- [新的 Swift 代码真实 Xcode Simulator #41222479925](https://github.com/turnupmason/WenguaApp/actions/runs/41222479925)：**成功**，包含最终关系名称修复。
- [六个 V11 完整实时时辰预览 #41222635966](https://github.com/turnupmason/WenguaApp/actions/runs/41222635966)：**成功**，新完整正文存于 `docs/HEALTH_V11_SIX_REAL_COMPLETE_PREVIEW_20261031.txt`。旧预览的错误是只筛选过期的 `02_illness/05_patient/09a_sibling` 标识，实际上章节编号为 `02/05/09a`，无意中丢弃病宫、天心、乙奇、患者、时干、值符、家属辅助的详细文字；已改为打印全部章节。
- 真实六盘第六例依然出现己干源强 `None`，新断词诚实地显为「待核」；该数据缺口未获源200格核准，不允许靠绝对宫分伪造五档力量。仍需专项追查（病宫自己宫天芮源强并不等于患者己干源强）。
