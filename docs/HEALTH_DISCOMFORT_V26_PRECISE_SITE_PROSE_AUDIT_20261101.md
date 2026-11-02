# V26 断词审稿 · 2026-11-01
女儿已见样本：巽四天芮、丁齿（两支大/极大最终极大）、乙胆极大、天禽所携戊脾中等；坤二己主胃，中等，真实六仪击刑。此前客户断词含“按较高一档取”“这一干象较突出”“可考虑此处受到病事牵连的象意”，缺失具体己胃伤痛归因。

V26分别修复 Python `src/wengua/health_discomfort_v19_parity.py` 和离线 Swift `ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift`，逐符号说真实部位/力量；击刑说对应部位的伤痛损伤象，入墓说受压隐伏象；宫与宫说木土生克等实际方向。45组原200双支仍各自取力并取较高档，V8病情轻重不改。保留全八宫真刑墓、81格、人物、伤门条件和先前失败记录。传统身体象意不是医学确诊、真实因果或临床预测。

已有V24 Xcode PASS #41377678550以及旧FAIL #41377648150等不是V26验收。待核V26真正 Python、Swift全文parity、macOS XcodeGen及unsigned Simulator离线bundle；未做签名真机与App Store；模板待用户批准。

### 2026-11-01 · V26 新提交测试门槛修复与失败留档
- V26源码SHA c425bc345e6a85cea21f132c89bb5228fb478ef8 的 CI #41380198105、Xcode #41380198099 在实际编译前失败：`tests/test_health_discomfort_v19_full_sequence_20261101.py:8` 仍断言V24 schema，与实际发布候选V26 schema不相等；对该测试及 Important 镜像只更新版本断言，不改源200/81、V8和失败案。两次失败真实链接保留，不算Xcode运行过。
- 同SHA V8关系图专项 #41380198072 成功，V7.7独立宫位专项 #41380198145 成功；旧V7.4案例审计 #41380198149 因独立断言失败，尚未归因为V26，不能伪称全绿。新提交后重新核实真正Xcode/Swift Python-parity/bundle。
