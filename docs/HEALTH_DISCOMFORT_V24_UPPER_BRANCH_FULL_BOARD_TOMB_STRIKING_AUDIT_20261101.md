# V24 病位断词：双支能量向上取档与整盘墓刑跨宫核对 · 2026-11-01

## 变更来源与正确范围
用户对 V23 当前真盘追加规则，非 V21 回滚。此前原生/独立跨平台已通过的 V23 实测基线为 Xcode #41370186316，真实 SHA d39dc050c9ce50336ec0437f12e3a32a219223dc，见 `docs/HEALTH_DISCOMFORT_V23_INTEGRATED_PALACE_AND_TWO_BRANCH_ENERGY_AUDIT_20261101.md`。本轮新 V24 必须自己的 Python 测试、macOS Xcode Simulator 构建、离线 bundle、真 Swift、独立 Python 对照成功才可称通过。

## 真实 200 格 45 个双支冲突
- 原源：`data/mobile/health_vnext/health_energy_200.json`、`ios/WenguaAppUI/WenguaNativeCore.swift` 十干 × 十二长生。十干×八实宫×五种月令=400种，45种双支同宫的两项真实格得到不同档位。
- 新用户明文批准只在 **health.discomfort 病位象意** 中把每支原格单独核对并**按五档最大者取用于判断**，例如「丁巽四辰衰大、巳帝旺极大 → 取极大」「小和中等 → 取中等」。两支原资料、其中较弱者和所有组合测试完整保留，不覆盖原始200表，不用强弱冒充吉凶或现实病情轻重。
- Swift `ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift` 内 local `sourceStrength(kind:stem,...)` 双支逐格后最大档；Python `src/wengua/health_discomfort_v19_parity.py` 独立 `_discomfort_power` 及本地 `source_strength` 同规则，原全局 `WenguaVNextEngine.factor` 不改，因为 **V8疾病轻重冻结**，不得暗改任何全球评分解释。V23 「双支不可合并」旧预期必须改为用户最新明文规则。
- 关联测试 `tests/test_health_discomfort_v23_dual_branch_integrated_20261101.py` 对400组合、45差异、每条计算最大档、真实丁巽原格、大/极大、源表无改验收。

## 真九宫所有符号入墓/六仪击刑互证
- 已知 V23 隐患：只在 **天芮宫** 的干身上读 `badSigns`；其它七实宫的十干墓刑即便真实出现也不进入客户结论。典型错误：由于另一宫入墓的象意不与最后一个主病位词重合，直接漏掉源条件。
- 新 V24 逐张真实盘的全部八个实宫，排除中五虚造的普通门星神：遍历每实宫真实天盘携干与真实地盘干，命中 `palace.tombs` 原干及真实六仪击刑 `striking[stem]==palace.id` 时逐符号显示宫、干、所映身体部位、源200格强度、入墓/击刑原条件和实际五行宫对病宫方向。相同物理宫同符号只取一次，不把不同符号复用首个强度；不纳无真实干之宫。
- 方向按实际五行：此宫克病宫、此宫生病宫、病宫克此宫、病宫生此宫、比和分别言明，禁止生克倒置。优先列实际克病互证，但余实际墓刑也保留；宫位关系不能证明医学病因，不能将古籍象意「疼痛、潜伏」说成器官已经损坏、未检出并发症、肝火致胃病等已确证疾病。
- V24 把跨宫查核作为一行「全盘墓刑互证」并入病宫完整合断，结论最多取一条有真实条件的跨宫线索另释关系。仍有伤门独立门控，宫中实际任何门迫都按真实门克宫判断。
- Swift `crossEvents` 与 Python `crossEvents` 分别实现，不复用对方预先计算的断词。阴阳体内外、用神身份、真出生年命、八门神独立源强及81有序格均沿历史保真。
- 公众仅阅读传统文化解读。**墓刑不能作为实际医疗诊断、器质性损伤、潜伏期、因果关系的证据**；不是临床预后准确性测试。
- 原始来源、失败案及历史 CI 日志永久追加保存，Important Swift/Python 两套源镜像与 MANIFEST Git blob SHA 同步，手机未签名真机/App Store 交付。
