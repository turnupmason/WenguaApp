# 2026-11-02 · 伤门调用与iOS病位开放审计

## 实际缺口与复现
- 当前main f25a2807。`WenguaDesignPreviewApp.swift` 原已有未选/none/accident/bone/bleeding/severe_pain/surgery选择，且病位enabled=true，不能宣称以前完全没做。
- `WenguaNativeDiscomfortV15.swift` candidateSites及独立Python对剧痛只作旁证，未按用户所问最痛位置优先伤门；injuryFull遗漏门自身及无部位交集的宫内符号实际力量；手术段只写开门宫克伤门宫，白虎没有手术专用分支。
- 原CI #41386393773 Xcode与bundle成功、独立parity CLI因第86行跨行+编译失败。本次改joined拼接，保留历史失败。
- 已见2027-02-07 11:00女儿固定案，不是盲测。旧守门要求时干外盘；改以源盘真正时干落宫判断，不能根据旧聊天填庚或外盘；Python原起盘为丁巳日丙午时，本次未改历法/五鼠遁。

## 本次规则与接线
| 选择 | 独立伤门 | 病位输出 |
|---|---|---|
| 未选、未知 | 阻断 | 不起局、不消耗15天次数 |
| 普通不适 | 关闭 | 天芮本宫事实；若本宫恰临伤门，仍读本宫八门 |
| 意外受伤、骨肉受损、出血 | 开启、主用神 | 先看实际伤门宫的体表伤损部位，天芮辅助 |
| 剧烈疼痛 | 开启、主用神 | 先看实际伤门宫的痛处，按实际内外盘选候选 |
| 已做/拟做手术 | 开启 | 分列天芮病位与伤门所示手术部位；查开门宫克伤门宫与同宫白虎 |

未选择在静心前、最终compute前、路由与compose多层拒绝；本地已存旧记录缺injuryContext仍可解码。伤门启用后段落置顶，真实星、门、神、天盘/地盘干各读自身源力量，检查81格、墓刑迫、空亡与马。强弱只作定位主次，不能混入V8轻重。优先级是独立排序层，不用任意分数覆盖伤门主位，也不因门弱或真空跳过伤门。

骨折/肌肉伤损先读同宫既有体表映射，避免阴遁离九内盘心脏被误当骨折部位；实际宫与内外盘事实不改。手术/剧痛不根据门象断定真实骨折、临床病因或必须手术。

## 文件
- Swift/UI：WenguaNativeDiscomfortV15、WenguaDesignPreviewApp、WenguaPremiumReadingView、WenguaNativeReadingRouter。
- Python：health_discomfort_v19_parity.py；同一个native_discomfort_v15.json离线模板附injury_policy。
- NativeInjuryContextAcceptance.swift：四独立真实时辰×六选择共24次原生运行，另拒绝12次空/未选/未知条件。
- tests/test_health_discomfort_injury_gate_20261102.py：四盘六选择、未选阻断、伤损/剧痛真实主位、手术两个独立条件正反例。
- Important双镜像与MANIFEST Git blob SHA同提交，README和状态追加，V8和原书未改。

## 验证
本地结果及新源码SHA对应的真实macOS Xcode/Swift逐字比较将在运行完成后追加。当前没有签名iPhone真机或App Store交付，不可把GitHub提交称为用户手机自动更新。

- 本地已实际通过22项现行病位专项，包含新伤门运行检查。全病位初跑有1处旧测试强制断言首段必须为病宫；改为按01_location角色ID查天地格，保留伤门首段要求。旧测试失败未改任何盘面或V8。macOS仍待运行。
