# 2026-10-29 · 难受部位外部候选规则 / iOS 标题实际验收与历史失败

## 原则与变更范围
源提交 `19f95b658db1df01d5c292d4f9d66fa87dec7966`：已将 iOS 客户细项「身体哪里不舒服」改为「难受部位」；稳定ID health.discomfort，`enabled:false`。新增外部用户笔记的8宫+10干（乙至癸72细分）+8门双角色+8神+条件链为未核准草稿，仅Python研究引擎读取真实病星主天干、天禽次天干与芮宫门神。没有改变V8评分、V10.2病情轻重模板、分数来源200/81、原著文本或真实客户结果；新模块**未**有Swift独立解词，没有医疗诊断批准。

外部材料来源未给出版次、书章和可校验原文SHA，故与原有《神奇之门》《开悟之门》来源索引隔离；「王」疑「壬」、「自虎」疑「白虎」，以及癌症、鬼神致病等说法只能做来源争议记录，不能直接展示为诊断或病因。患者门与天芮门独立；新旧、体表体内需真实可证规则，否则均标unknown。

## 本次真实GitHub Actions（均针对源提交19f95b6）
- **PASS** Python 3.11/3.12当前V8主CI、包括新增外部注释集与真实九宫3例专项回归：#40886848712，https://github.com/turnupmason/WenguaApp/actions/runs/40886848712 。
- **PASS** 原有V8真实Swift↔Python及客户中文、200/81原生对照：#40886848622，https://github.com/turnupmason/WenguaApp/actions/runs/40886848622 。不能误称新病位模块Swift全文已完成。
- **PASS** V7.7两原时辰既有冻结回归：#40886848887，https://github.com/turnupmason/WenguaApp/actions/runs/40886848887 。
- **PASS** 真实macOS XcodeGen/Xcode iPhone Simulator App编译、11档UI文字、历史5份V10.2结论及App打包的200/81/人物/模板资源检查：#40886848727，https://github.com/turnupmason/WenguaApp/actions/runs/40886848727 。**非签名真机/App Store**。
- **FAIL（旧契约）** V7.4源表/人物/固定分数专项：#40886848564，失败步骤`User fixed pillars, natal Yi physical cohost, exact signed scoring ledger`，https://github.com/turnupmason/WenguaApp/actions/runs/40886848564 。
- **FAIL（旧契约）** 综合iOS Offline Native Casting Parity：#40886848616，旧V7.2/朋友/1920老人/同事固定断词及原20人物测试步骤失败，Xcode子Job因此skipped；**不可**把本次另行成功的正式Xcode #40886848727算作此旧工作流成功。https://github.com/turnupmason/WenguaApp/actions/runs/40886848616 。

独立Python完整历史全库`python -m unittest discover -s tests -v`、用户新增规则的Swift病位解词一致性及专业病位准确性**本轮未完成**，不得称其通过。失败历史照存，不为迁就旧断词改冻结评分。

## 下一验收门槛
核实外部资料原书版次和具体条文，尤其内外盘新旧疾病、天干每宫候选、八门八神各自施于病星或患者的前提及相反证据。建立可判定的患者角色、时干/伤门实宫冲突与非诊断断词，使用非后验案例回归和Python-Swift逐字一致后方可评估是否启用health.discomfort；未启用不得登记15天限制。
