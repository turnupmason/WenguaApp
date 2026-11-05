# V19 病位完整序列、独立用神强度与真实家属身份审计 · 2026-11-01

## 本轮变更范围

health.discomfort 独立专题从 V18 压缩六节改为九段真实盘证据：01 天芮病星与阴阳遁内外定位、02 伤门、03 病宫及其他辅助门、04 时干事体、05 根据人物关系所选主用神、06 符合亲属排行/长辈乾坤/真实年命条件的辅助宫、07 天地盘真实81格、08 逐符号入墓/六仪击刑/真空假空/门迫、09 综合传统病位优先次序。部位象意是古籍文化表达，不是现代医学诊断，也不可断言实际疼痛程度。

V18 已复现的真实缺陷：`ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift` 即使计算多种门/干强度，最终只显示天芮宫两处部位与少量同部位交叉提示，伤门/辅助门、时干、人物和81格被省去，源符号的墓刑没有参与独立部位排序。V19 在同一个离线 Swift 文件新增全顺序，真实200源格中每个符号独立取五档力量，81天地盘格只作格局而非源力量。遇墓或六仪击刑，只给**真实指向相应位置的符号**增加传统病位关注权重（内部排序+5，非真正源力等级、非病情轻重净分），同符号同宫不重复计。真假空调整本宫证据显现的优先级，门迫只作为本门的限制条件；两书冲突及255行原始 source inventory 完整保留，不让未经证实的外书候选直接改写确定器官。

## 跨专题人物关系约束

`WenguaNativeActorBinding.swift` 为病位与疾病轻重共同使用的人物绑定门槛：哥哥、姐姐、弟弟、妹妹必须由用户主动确认**真实家庭亲属关系**，非亲属一律走“朋友”。本轮 iOS 里的“姐姐”明确为家中**大姐**，巽四长女辅宫需确认 family + eldest，不能把普通年长朋友推为大姐；哥哥震三、弟弟艮八、妹妹兑七的辅宫遵原资料保留独立类象及来源不确定性，条件不符拒绝套宫。朋友必须填写性别与比求测者大/小，但仍取真实月干，不增加排行或乾坤等家庭辅宫。人物状态变化时清除上一个身份的旧勾选。年命始终可选且须源于真实提供，不能冒充起局年干。共享门槛对V8生效，但原V8病情轻重评分引擎、两张能量表、81格、矩阵、净分及十档断语**完全未修改**。

## 失败与复现及修复

- 旧基线 main SHA `312ba59`，主CI run #41337733981 PASS。
- 人物 guard 提交 `2b5f818`；扩九节 `3155ace`。CI run #41339353432 的 Xcode 真 macOS 编译 FAILED：`WenguaNativeDiscomfortV15.swift` 多处多行字符串尾部 `+` 拼接语法错误，原始失败记录 `https://github.com/turnupmason/WenguaApp/blob/course-v4-before-cleanup-20261105/docs/IOS_V80_XCODE_FAIL_RUN_41339353432_ATTEMPT_1.md` 不得删除。
- run #41339353399 六甲来源V8原生一致性 FAILED：测试旧“哥哥”案例未显式确认亲属，原生 `unsupportedRelationship` 被拒；先修复测试输入而非放松生产人物 guard。失败记录 `https://github.com/turnupmason/WenguaApp/blob/course-v4-before-cleanup-20261105/docs/HEALTH_V80_FAILURE_RUN_41339353399_ATTEMPT_1.md` 保留。
- `03d85b6` 修复新增Swift文本拼接、V8夹具上“哥哥”等真亲属关系输入，并在iOS切换人物时清理先前亲属确认。必须**以后续同SHA CI结果为准**；当前阶段不能把旧V18的Xcode PASS冒充V19已经验收。
- 本轮不新增原书章节、原书案例或所谓独立盲测。V8旧已揭晓回顾固定案例不改历史结论；V19 Python研究稿和Swift客户九节的**逐字同盘 parity 仍是单独验收项**。真机签名/App Store未验收。

## 代码和测试

Swift: `ios/WenguaAppUI/{WenguaNativeActorBinding,WenguaNativeDiscomfortV15,WenguaDesignPreviewApp,VNextThreeRandomNativeFullCheck,NativeDiscomfortV15Smoke,NativeActorProfileCheck}.swift`。
模板及索引: `data/templates/health_discomfort_v11/native_discomfort_v15.json`, `data/knowledge/phrase_library/health_v20/actor_profiles.json`。
测试: `tests/test_health_discomfort_power_v17_20261101.py` (延续原有断言), `tests/test_health_discomfort_v19_full_sequence_20261101.py` (本轮严格九节及身份门槛)。Xcode Actions `.github/workflows/ios_v80_xcode_simulator_build.yml` 仍要求真实 simulator build，bundle 200/81/255 资源和随机父亲/大姐双盘。 `Important/python`、`Important/swift` 与 `Important/MANIFEST.json` 每次改代码同步镜像及 Git blob SHA。

## V19 补充：独立多宫候选阈值

新九节原本只排序天芮本宫的原始位置，对旁宫的完全不同位置仍然排除。进一步增加额外候选准入：旁宫实际用神／时干／伤门／亲属辅宫／真实八门源200强度必须达大或极大，且符号自身有真实入墓或击刑，或至少另一**不同物理宫**中等及以上的独立证据支持该同一部位，才可加入异宫候选（最多4项，最终显示主次仍控制篇幅）。同一宫的患者与伤门不得冒充两个物理宫交叉。此为传统部位类象候选的审慎排序，不是新增来源规则，也不代表医学上的疼痛或病灶。

## 真实验收补充（2026-11-01）

- `c0b10d67`：真正macOS XcodeGen/iOS Simulator unsigned build、包内200格/81格/255源表/三系干象/9段模板验收、随机父亲和家中大姐真实双盘 Swift 离线全文输出，GitHub Actions [#41340149493](https://github.com/turnupmason/WenguaApp/actions/runs/41340149493) **PASS**。这不是签名真机或App Store验收。
- 同版原V8 Python与Swift人物源力专项 parity [#41340149539](https://github.com/turnupmason/WenguaApp/actions/runs/41340149539) **PASS**；V7.7 独立两时辰 [#41340149586](https://github.com/turnupmason/WenguaApp/actions/runs/41340149586) **PASS**。
- 最新 V19 新增九段顺序/身份校验测试正式进入 Python 3.11/3.12 主 CI，`4d61b3a5` 的 [#41340256039](https://github.com/turnupmason/WenguaApp/actions/runs/41340256039) **PASS**。本轮曾有 Xcode [#41339915786](https://github.com/turnupmason/WenguaApp/actions/runs/41339915786) 拼接语法失败，随后已修复，失败源码记录继续保留。
- 独立病位专题 Python V11 与 Swift V19 同盘逐字 parity **仍未通过单独验收**；较旧 `iOS Offline Native Casting Parity` 总工作流还存在原版言词断言冲突与其他失败，不借本次两个专项PASS冒充全库通过。传统身体取象不是医疗验证。

## 六甲载干与时干本力修正

实际V19随机姐姐盘出现甲时干，旧 `stemPower(hourStem,hourPalace)` 用甲字面寻找携干（盘中甲实际遁六仪）会落入待核；本轮在病位独立专题补 `actualRolePower`，先用完整甲干支确认六仪载干真实物理宫，再从现有 `WenguaNativeCore.stages["甲"]` 及源200天干表按甲本身实际宫支/月令取力；主用神为甲同理。入墓/六仪击刑仍针对真实物理携干身份，不对同宫两个角色重复算宫位净分。不能直接把六仪戊己庚辛壬癸自身的源力假冒甲的源力，未有有效完整干支则保留待核。原V8计分不变。

## 家中四种关系 UI 与双新角色原生随机盘

Picker 四个直接写：哥哥（家里的哥哥）、姐姐（家里的大姐）、弟弟（家里的弟弟）、妹妹（家里的妹妹）。四个对应不同文本的确认 Toggle，非家庭朋友必须改走朋友。新原生 smoke 添加随机弟弟、妻子各一时辰（保留原父亲、大姐两时辰），验证弟弟月干与艮八、妻子乙奇无兄妹辅助，九段客户原句逐节输出，V8评分不动。


## 2026-11-01 V19 真家属四类及病位 Python/Swift 同盘逐字验收

iOS Picker 对「哥哥（家里的哥哥）」「姐姐（家里的大姐）」「弟弟（家里的弟弟）」「妹妹（家里的妹妹）」逐项明确；每一关系拥有独立真实家庭亲属确认文字，Swift fail-closed；姐姐=家中大姐（需长女条件），朋友永不借家族辅助宫。NativeActorProfileCheck 新增四类未确认不得绑定回归。V8评分冻结不改。

真 macOS Xcode Simulator #41341637870 PASS，随机弟弟2026-11-14 11:00 -05、妻子2027-02-14 05:00 -05 各9段原生客户文字在 https://github.com/turnupmason/WenguaApp/blob/course-v4-before-cleanup-20261105/docs/IOS_V80_XCODE_PASS_RUN_41341637870_ATTEMPT_1.md。独立 Python V19读取同一张 Swift 物理盘的原始事实、自行用200格、81格和255源/人物用神求部位及重组九段中文；实际另随机弟弟2026-11-15 05:00 -05、妻子2027-02-12 21:00 -05 各9/9段文字、标题与落宫严格一致，真 macOS Xcode #41342466896 PASS。此 parity 验的是跨语言断词和源表，原盘排盘在别的既有专项验证；不是医学有效性证明。

历史 Xcode失败 #41341934448 因独立Python读取中五宫 p['door'] 错误：中五无普通门，已改为 get() 后 #41342466896 PASS，记录保留。旧综合 iOS Offline Native Casting Parity 仍有 V7过时文案断言及 unresolvedRole，不能冒称全库通过；继续逐案审查。未签名真机/App Store 验收。


## 2026-11-01 本轮后续：旧综合原生回归真正审查（保留失败）

1. 用户要求家里的四种亲属必须逐一明确。Swift UI `WenguaDesignPreviewApp.swift` Picker + 每项确认分别为「哥哥（家里的哥哥）」「姐姐（家里的大姐）」「弟弟（家里的弟弟）」「妹妹（家里的妹妹）」，四者均必选亲属确认；历史 `哥哥或姐姐` / `弟弟或妹妹` 复合档案仍存但已经从面向用户的 Picker 隐去。真正朋友仍走独立朋友性别/相对长幼，绝不借亲属排行辅助宫。4种未经确认拒绝真实 Swift actor binding 的 `NativeActorProfileCheck.swift` 及 Python 源静态回归已加。
2. 旧 `iOS Offline Native Casting Parity` V5/V7回归和现行V8的冲突：旧测试把 `chief.score_eligible` 当作物理宫是否计数，错把不克病或逢空的值符所在实宫完全剔除。现行 V8 源 `src/wengua/health_quant_overlay_vnext.py` 360–406节说明独立物理宫基础事实只计一次，克病**条件奖励**另外门控。修正旧 `tests/test_health_vnext_exact_role_matrix_gate_20261026.py`，断言按真正 `unique_palace_count` 去重，逢空优先反证，原生产打分一行未改。旧【原先预写断词】只测试真实用神/方向/四段结果和保密，不再强制已废弃的V5句子。
3. 原生 `VNextNativeParityCheck.swift` 旧 `qian` / `kun` 与 V8 `gender` 其实共用一个物理乾六/坤二宫。只在实际性别辅助宫吻合时把旧测试名映射至一个真实宫，不新造克病条件/奖励；错误日时、用神及首个不一致角色打印日志。旧流程 #41343697589 的五盘 native_core Swift/Python 实际计算、原生朋友真盘和长辈/同事专项已经运行通过。
4. 多个历史测试工作流会同时在 main 修改同名固定归档，导致旧 #41342824942、#41343697589、#41343840162 出现 `git pull --rebase` 文件冲突，并不等于 Python Swift 模型错。为了防止覆盖原著及长期失败，新归档改成 `RUN_${GITHUB_RUN_ID}` 唯一文件，旧归档原样保留；同时修复相同文件无需commit时误报失败。并未隐藏旧失败记录。
5. 原 V19 独立 Python/Swift 九节逐字一致、源200/81和六甲时干落宫已由 #41342466896 真 macOS 编译、随机弟弟/妻子两盘 PASS；四亲属 Picker、病位九段资源也经 #41343697671 Xcode PASS。本轮最新归档防冲突改动需要**新的 Actions 自身结果**，不能挪用旧版PASS。
6. 当前仍需持续跟踪旧综合流程最终归档成功与 iOS 真实签名设备/App Store。真实古籍文化部位不构成医学病灶、疼痛强度、预后验证；V8疾病轻重原始规则矩阵/源数据、10档分层以及已见结局历史家族没有变动。
