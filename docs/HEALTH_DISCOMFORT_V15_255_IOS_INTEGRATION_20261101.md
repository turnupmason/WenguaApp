# WenguaApp V15 · 255原始病位规则和iOS独立专题审计
2026-11-01 · 保留V8.0疾病轻重全部冻结规则、分数与模板。

## 来源
- 原始用户JSON完整实录：255 ID唯一，A142 B16 C16 D69 E12；12原书案例、20冲突、9来源。
- 原始255条上下干方向全部为空；多干合参需要真实符号身份、方向和原书明确成立条件。不得把庚癸无方向地改读庚加癸或癸加庚。
- 秘笈大全卷十三十干与三命通会卷七脏腑/体表三套异文各自保留；后二者同一命理书，不当作两项独立时家奇门证据。
- B历史案例已见反馈且有重复源，不当新盲测；C跨条文推导与D跨体系、E质量守则不作为实病诊断或者独立决定器官的规则。

## 实际修改
- data/knowledge/health_discomfort/complete_255_rules_v15_20261101.json：全部原始资料。
- src/wengua/health_discomfort_255_v15.py：对255条每条确定符合源条件或拒绝原因，真实八宫×阴阳遁×天芮携干与门神筛选；不可由宫净分臆测部位。
- data/templates/health_discomfort_v11/reading_template.json + health_discomfort_template_v11_draft.py：保留六段并在病星段明确三套来源，audit记录255逐条条件。
- data/templates/health_discomfort_v11/native_discomfort_v15.json + ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift：独立离线六段，逐盘从完整255、十干三套取主/异象；bundle路径真实加入project.yml。
- ios/WenguaAppUI/WenguaNativeReadingRouter.swift：独立 topicID 路由，不经过 V8 scoring。
- ios/WenguaAppUI/WenguaDesignPreviewApp.swift：现启用health.discomfort，30秒真实时辰与15天存档沿用但不同topic各自签名。
- tests/test_health_discomfort_full255_native_v15_20261101.py：全原始资料与条件匹配/排除/模板/UI路径回归。
- Important 双镜像及MANIFEST Git blob SHA跟随真实源更新；旧失败永不删除。

## 未完成
- Python V11+V15和Swift V15使用不同详略的六段辞，**不能宣称该专题逐字 parity**；先做独立同盘对照再验收。
- 原文多干方向/异文/原书反例条件继续待核；不能将255行直接全部作为已核客户规则。
- 还需最新macOS Xcode Simulator和包内资源实测结果、UI真机手工验收；CI失败时必须如实记录。无临床医学验证。

### 2026-11-01 V15 病位原生阴阳双时辰实际验收
- macOS GitHub Actions [#41327899200](https://github.com/turnupmason/WenguaApp/actions/runs/41327899200) 对 d9632f7d54ec84c4c3c55ba348eb67ba425491d4 完成：XcodeGen、真实 unsigned iOS Simulator app build、原V8模板/200格/81格/24人物，以及 App 包内新增255规则/三套十干/native六段模板**逐字节源一致性**，并在独立 Swift runner 真实算阴遁 2026-10-27 13:00 -04（艮八天芮、离九本人）与阳遁 2026-12-27 13:00 -05（离九天芮、艮八本人），均输出6段病位中文通过。新增的严格运行步骤成功，非仅 Swift 语法检查或静态源测试。不是签名真机或医学定位验收。
- 早前 [#41327564087](https://github.com/turnupmason/WenguaApp/actions/runs/41327564087) 曾出现 CLI 测试拼接语法失败，且存档只凭旧V8 bundle flag错记PASS；修为同时核实 native_site_validation.txt 后才可归档PASS。随后 [#41327734679](https://github.com/turnupmason/WenguaApp/actions/runs/41327734679) 发现 Swift 拼出“艮8”而原书数据用“艮八”，导致运行 missingRole，已固定全八宫中文宫名。旧失败和不严谨归档保留不改。
- 最近的主 Python 专项 [#41327928247](https://github.com/turnupmason/WenguaApp/actions/runs/41327928247) PASS，原V8 Python/Swift全文 native parity [#41327785507](https://github.com/turnupmason/WenguaApp/actions/runs/41327785507) PASS，旧V7.7固定盘 [#41327785563](https://github.com/turnupmason/WenguaApp/actions/runs/41327785563) PASS。V8.0冻结计分源/断词未改。
- **未完成**：病位专题目前 Python V11 六段与 Swift V15 六段非逐字同模板，尚未新专题 Python/Swift 相同真实时辰全文 parity；255完整归档不代表全部适用/核定，古籍严重病名类象不可作为医学诊断；无签名真机、无公众病位医学准确率测试。
