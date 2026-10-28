# 2026-10-28 · 九宫天芮／禽单行、源200格宫位力量、乾坤长辈门槛

## 用户截图及原问题
用户2026-10-28 13:44阴遁2局（丙午／戊戌／乙亥／癸未）在手机图上发现：原九宫天芮与天禽被分两行，天盘星携干挤在星行，底盘干挤在门行；宫位详情仍留下「同宫同事实不得...」内部句，缺八门/神/星/天盘干/地盘干的月令和独立源力量。乾坤两宫应只有长辈且依实际性别条件才作辅助，不能因单纯性别给孩子、同事、本人追加长辈用神。

## 现行正式代码位置、修正及约束
- `ios/WenguaAppUI/WenguaDesignPreviewApp.swift::ProfessionalPalaceTile`：将所有真实九星压缩**同一行**；天芮／天禽单行「天芮／禽」，天盘两携干独立一行、次星丁置左，天芮戊居右、真实单地盘庚再下一行，八门/八神完整不被用神竖排遮盖。独立`star→carriedStem`映射及无改动的两条真实81格源计算仍保存，绝不凭截图创造干。
- 同源 `ProfessionalPalaceDetail`：详情顶部「宫位属性 · 用神角色」仅列实际宫名、五行、宫支、已选角色（`rolePalaces`），去掉内部同宫防重复打分句。新 `WenguaPalacePowerDetail.swift` 为**只读**，实际八门→八神→九星→天盘干→地盘干顺序展示，并单独居中。每颗星专用九星旺相休囚废、每门普通旺相休囚死、八神仅本神五关系（不借星与月令）、星门和每干力量均调用`WenguaVNextEngine.factor`及实际200格Bundle；不同宫支干强度不同逐支列出，不从最终±5宫分反推。未知显示待核。十二长生「天盘干：」「地盘干：」冒号固定。
- 原Python `src/wengua/domain_selected_energy_vnext.py::selected_health_sequence` 曾在已选`gender`以外**无条件观察两宫**，`src/wengua/health_text_pipeline_vnext_review.py` 又无条件把2/6列为源审计相关宫；Swift `WenguaNativeVNextEngine.swift` 原来亦无条件`allSelected.append(qian/kun)`。现只依22种原人物Profile（原20+单独爷爷奶奶）选中真实长辈性别宫一次：男乾6、女坤2；未提供性别的其他长辈暂不补选；非长辈`qian_kun_auxiliary_observations={}`。完整九宫仍始终可见，可点查真实原盘，不意味着把6/2宫从排盘中删除。
- 原生专项`VNextThreeRandomNativeFullCheck.swift` 对新`gender`选中宫进行核对，非长辈不得多角色隐选乾坤。未改变V8.0疾病计分表、月令算法、跨宫奖励、天芮+天禽双格、原书、已见两例基线或原断词模板。较老专用V7测试可能因其原始无条件观察口径出现冲突，失败仍永久保留，不借机调算法。
- 回归：`tests/test_ios_palace_source_power_20261028.py`包括本人/同事/父母/祖辈真时辰与选中辅助观测、五类源力量及单星行结构；现行主CI、Swift真原盘及20随机、XcodeGen macOS实际Simulator构建和资源验收必须基于此次最新提交重新运行，不能沿用上一版成功。工程保留30秒静心、15天同事禁重复、所有未验收领域开发中。此处仅传统文化数值展示，不是临床病情判断。


## 2026-10-28 真实运行记录与旧UI测试口径隔离

- 本次新规则真 Python/Swift 原始两历史盘、13:44多人物与20真实时刻完整全文逐字一致：GitHub V8专项 `#40747800929` **PASS**；两侧源计分/中文模板保持一致，Python/Swift没有新分数表。旧历史V7专项若报告失败不得伪称V8正式验证失败或删除旧记录。
- 最初V8主CI `#40747800957` **FAIL**：旧UI结构静态测试 `tests/test_ios_health_grade_copy_20261028.py`仍要求`String(star.0.dropFirst())`逐星第二行，已按用户新「天芮／禽单行」修改该测试（commit `ed88fe6`）。下一轮 `#40747944601` 仍 **FAIL**：另一旧`tests/test_health_v80_disease_dual_sky_20261028.py`硬要求`symbolRow(star.0,kind:"star",stem:star.1)`，亦是旧行布局断言而非81格错；按真实新UI的「同星行、独立天盘行、独立地盘行且逐星归属」重新设静态合约（commit `19f58c6`）。两个失败Actions与代码历史都保留；不得通过回滚合法双星排列令假旧测通过。
- 现行新UI含真实13:44人物门槛、25/72组合/双天盘及全源200力量渲染结构、Important所有镜像、数据smoke：V8主CI `#40748081165` Python3.11/3.12 **PASS**。真实 macOS XcodeGen iOS Simulator 与 bundle 资源工作流 `#40747800998` 已因本轮SwiftUI源变更触发，但查看时处于**queued**，未返回真实编译、包验收，故暂不能给此次源码标记Xcode PASS；之前的 `#40745274121` 是改前版本，仅作历史成功证据。实际状态以本轮 run 页面和新日志为准。
