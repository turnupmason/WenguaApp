# V3.3 本轮十二个疾病历史事件：V3.1 原样全域回测与下一窗口 UI 交接（2026-10-22）

## 不要重置、不要回退
唯一已确认父库是 V3.2 全量 SQLite：`archives/sqlite/WenguaApp_双书194案例_两例新家族V31离线回测V3_2_完整研究库.sqlite3`，SHA256 `e4110828bbfb621e1bb7ed972284d4602d2ab361a12edc48d6f4750c965dddf9`。原194历史事件、43来源章、2次失败开发断语及过去版本全部不可变。当前还未通过 GitHub Actions 验收 V3.3 前，不得宣称新父库存在。新独立版只能通过迁移061从 V3.2 追加。禁止修改 V3.1 断案函数原样文本。

## 本轮用户明确任务
用 V3.1 固定离线模板对古籍全部疾病相关事件的原时辰研究回测；把用户再次直接提交的大段疾病取用、病宫、时干、值符值使、阴阳旺衰、医药、刑冲墓迫、星门、应期及危险格局加入可检索的11段模板条目，按已执行/仅索引分级，不把未执行当成通过。最终必须更新根 AGENTS、PROJECT_STATUS，并给下一窗口可以直接接UI和其他四个疾病模板的状态。当前窗口不开发 UI。

## 不重复计算的原书疾病事件全集
神奇之门专门人体疾病章节六个 event family。
开悟之门日常百事人体疾病节共六条源故事，其中父病一条与神奇之门完全同一个 family，因此仅新增五个（包括母鸡、公鸡）。
开悟之门末章同一时辰三问三人中另有“女婿术后康复”一个独立 health family，原九宫是 OCR 片段，尚不可核对原文九宫空间排列。因此 6+5+1=**12 个不重复疾病研究事件**。以 `data/knowledge/shenqi/health_prediction_ch01/case_index.json`、`data/knowledge/kaiwu/health_prediction_ch02_section01/case_index.json`、`data/knowledge/kaiwu/questions_answers_errors_and_methods_ch03/case_index.json` 为事件范围核对来源，不重启来源库、不拆分家族、不重复开悟父亲案。

`scripts/replay_all_historical_health_v31_v33.py` 的十二条清单固定：1996-03-16本人，1996-07-27父亲，1996-05-09侄儿出院，1996-05-23姨母，1996-11-02本人，1997-12-27妻子异地治疗，开悟1996-09-23工人、1995-02-19弟弟、1998-06-16母鸡、1998-06-21公鸡、1999-10-20当事人手术，末章2000-06-05女婿术后康复。每个完整可起盘且有V3.1真实用神的人物只调用 `analyze_health_severity_v31`，交回未修改的11/10段离线中文和 SHA256；无法验证的人物/缺宫不得假造“本人日干”来凑一个结论。
- 妻子角色：V3.1 `spouse` 还没有可核主用神；必须阻断而非擅用日干。
- 母鸡、公鸡：V3.1 尚没有 animal 对象的源书可执行角色，公鸡原盘巽宫另有2处OCR缺干；先阻断，不用动物死亡反馈反改盘。
- 女婿：没有 son_in_law 角色且末章共享盘的 OCR 宫位布局未验证；先阻断。
- 侄子问的是出院、1999问的是手术、妻子问异地治疗、女婿问恢复：即使同盘能够生成疾病轻重象，只是 **severity 分域候选**，不是这些其他问事已经可用；4个非 severity 意图仍待审。
- 同一“时辰”并不等于知晓某分钟：时间锚点只作时辰校验；对于原书没写分钟的案例绝不能伪造精确实际问测时刻。
- 对书中作者结果、初断错失、后续诊断/反馈一概只用于封存后单独比对，不输入渲染器；这不是秘密盲测，也不是现实医学病情效度证明。

## 本轮再次提供的疾病占方法如何进入模板
已有 `data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json` 与 `user_20261022_pair_catalog.json`（42条干组合、17组复合条件）。**新增** `data/knowledge/phrase_library/health_v33/user_disease_supplement_template_coverage.json` 把这次更完整的用户知识输入按 V3.1 11段顺序建立字段索引、实际执行状态、遗漏项和安全边界。未来继续开发必须使用此映射和旧V30真实索引，不能要求用户重贴古文。

目前 V3.1 已执行：天芮病宫及坤本位辅助、日干/年干及部分人物关系、时干病事对人的有向关系、五不遇、乾6坤2（已知性别）、医药星分月令、部分同宫就医机会、实际天盘刑墓与门迫、伏反吟和已满足条件的部分组合格局、部分未定具体日期的应期候选。
**仍未全部真算**：配偶日合与乙庚绑定、动物健康、多人分别取用、42组有序干格全部角色分歧及反例、17组全部复合条件、丧门吊客、马星完整触发与具体数日时、全套六亲独立验证、真实疗效、原书疾病诊断。原书古诀中“癌/必死”不是医学诊断，绝对不得拿去面向患者定疾病或建议停止看病。

## V3.3 工程路径与检验
- 批测：`scripts/replay_all_historical_health_v31_v33.py`
- 回归：`tests/test_health_all_historical_v33.py`
- 补充知识映射：`data/knowledge/phrase_library/health_v33/user_disease_supplement_template_coverage.json`
- 增量迁移：`schema/migrations/061_health_all_original_case_replay_v33.sql`
- 全数据库生成：`scripts/build_health_v33_all_case_archive.py`
- CI 工作流：`.github/workflows/health_v33_all_cases.yml`
- 只在真实 Actions 成功才写：`data/evaluation/health_v33/all_historical_health_V31_READOUTS_SEALED.json`、V3.3全量 SQLite/XZ、`archives/sqlite/wengua_health_v33_full_manifest.json`。旧V3.2、V3.1与任何旧实验都绝不能覆盖。

## 下一窗口唯一交接指令
先读最新 root AGENTS.md 底部、PROJECT_STATUS.md 底部、本文件与 `archives/sqlite/wengua_health_v33_full_manifest.json`（若存在）；核对最新 GitHub HEAD 和该提交CI。显示/比对本次十二条事件中已成功断词与明确阻断的全部真实结果，不得把成功 CI 直接等同用户专业通过。用户已说明下一个窗口希望处理 UI 和其它疾病模板；**用户下一窗口明确授权 UI 后可开始现有 iOS 产品 UI 设计，不能再因老版冻结备注一概拒绝**，但没有明确认可模板前不得宣布十一段医疗断词已经专业通过。UI需体现离线真盘、人物关系、用神、九宫、证据和古籍文化提示。其它四个疾病子题分别先出模板测试并等待用户确认，未通过前不在界面冒充已实现。真实 iOS app 仍需签名、Apple开发者账号与上架审核，不把静态设计称“已上架”。
