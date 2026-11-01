# V19 病位完整序列、独立用神强度与真实家属身份审计 · 2026-11-01

## 本轮变更范围

health.discomfort 独立专题从 V18 压缩六节改为九段真实盘证据：01 天芮病星与阴阳遁内外定位、02 伤门、03 病宫及其他辅助门、04 时干事体、05 根据人物关系所选主用神、06 符合亲属排行/长辈乾坤/真实年命条件的辅助宫、07 天地盘真实81格、08 逐符号入墓/六仪击刑/真空假空/门迫、09 综合传统病位优先次序。部位象意是古籍文化表达，不是现代医学诊断，也不可断言实际疼痛程度。

V18 已复现的真实缺陷：`ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift` 即使计算多种门/干强度，最终只显示天芮宫两处部位与少量同部位交叉提示，伤门/辅助门、时干、人物和81格被省去，源符号的墓刑没有参与独立部位排序。V19 在同一个离线 Swift 文件新增全顺序，真实200源格中每个符号独立取五档力量，81天地盘格只作格局而非源力量。遇墓或六仪击刑，只给**真实指向相应位置的符号**增加传统病位关注权重（内部排序+5，非真正源力等级、非病情轻重净分），同符号同宫不重复计。真假空调整本宫证据显现的优先级，门迫只作为本门的限制条件；两书冲突及255行原始 source inventory 完整保留，不让未经证实的外书候选直接改写确定器官。

## 跨专题人物关系约束

`WenguaNativeActorBinding.swift` 为病位与疾病轻重共同使用的人物绑定门槛：哥哥、姐姐、弟弟、妹妹必须由用户主动确认**真实家庭亲属关系**，非亲属一律走“朋友”。本轮 iOS 里的“姐姐”明确为家中**大姐**，巽四长女辅宫需确认 family + eldest，不能把普通年长朋友推为大姐；哥哥震三、弟弟艮八、妹妹兑七的辅宫遵原资料保留独立类象及来源不确定性，条件不符拒绝套宫。朋友必须填写性别与比求测者大/小，但仍取真实月干，不增加排行或乾坤等家庭辅宫。人物状态变化时清除上一个身份的旧勾选。年命始终可选且须源于真实提供，不能冒充起局年干。共享门槛对V8生效，但原V8病情轻重评分引擎、两张能量表、81格、矩阵、净分及十档断语**完全未修改**。

## 失败与复现及修复

- 旧基线 main SHA `312ba59`，主CI run #41337733981 PASS。
- 人物 guard 提交 `2b5f818`；扩九节 `3155ace`。CI run #41339353432 的 Xcode 真 macOS 编译 FAILED：`WenguaNativeDiscomfortV15.swift` 多处多行字符串尾部 `+` 拼接语法错误，原始失败记录 `docs/IOS_V80_XCODE_FAIL_RUN_41339353432_ATTEMPT_1.md` 不得删除。
- run #41339353399 六甲来源V8原生一致性 FAILED：测试旧“哥哥”案例未显式确认亲属，原生 `unsupportedRelationship` 被拒；先修复测试输入而非放松生产人物 guard。失败记录 `docs/HEALTH_V80_FAILURE_RUN_41339353399_ATTEMPT_1.md` 保留。
- `03d85b6` 修复新增Swift文本拼接、V8夹具上“哥哥”等真亲属关系输入，并在iOS切换人物时清理先前亲属确认。必须**以后续同SHA CI结果为准**；当前阶段不能把旧V18的Xcode PASS冒充V19已经验收。
- 本轮不新增原书章节、原书案例或所谓独立盲测。V8旧已揭晓回顾固定案例不改历史结论；V19 Python研究稿和Swift客户九节的**逐字同盘 parity 仍是单独验收项**。真机签名/App Store未验收。

## 代码和测试

Swift: `ios/WenguaAppUI/{WenguaNativeActorBinding,WenguaNativeDiscomfortV15,WenguaDesignPreviewApp,VNextThreeRandomNativeFullCheck,NativeDiscomfortV15Smoke,NativeActorProfileCheck}.swift`。
模板及索引: `data/templates/health_discomfort_v11/native_discomfort_v15.json`, `data/knowledge/phrase_library/health_v20/actor_profiles.json`。
测试: `tests/test_health_discomfort_power_v17_20261101.py` (延续原有断言), `tests/test_health_discomfort_v19_full_sequence_20261101.py` (本轮严格九节及身份门槛)。Xcode Actions `.github/workflows/ios_v80_xcode_simulator_build.yml` 仍要求真实 simulator build，bundle 200/81/255 资源和随机父亲/大姐双盘。 `Important/python`、`Important/swift` 与 `Important/MANIFEST.json` 每次改代码同步镜像及 Git blob SHA。
