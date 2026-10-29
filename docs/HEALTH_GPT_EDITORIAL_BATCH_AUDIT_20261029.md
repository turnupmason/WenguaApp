# Health V8 GPT Editorial V1 — 批量生产与联网质检审计（2026-10-29）

## 正式决议
用户选择方案1：**真实时家转盘 + 确认人物及专题用神 + V8.0冻结评分 + V10.2完整原文证据 → GPT联网审核候选 → GPT润色 → 人工审核 → 离线iOS。**
首页目标约200个汉字：传统象意吉凶必须明确给一个结果且与V8得分对应，但不在公众文字宣读「极大凶/大凶」这种内部档位，不把结果当实际医疗预后、病名、治疗保证。专业解盘必须逐宫提供可追溯、细致润色的完整章节，不能拿200字摘要替代。两屏吉凶与证据不可矛盾。

冻结Prompt：
- `prompts/health_severity_gpt_editorial_v1_20261029.md` 是主审稿、润色、输出JSON合同；改 Prompt 必须换版本、重算hash、新批号，绝不覆写旧稿。
- `prompts/health_severity_online_rule_audit_v1_20261029.md` 是可联网研究候选审计；涉及原书章节/source hash、精确人物条件、同宫去重和方向，发现疑点排入待审队列；**不能联网查到不同说法就默改V8或古籍原文**。
- `scripts/health_editorial_batch_v1.py` 批量准备真实资料、索引、符合 OpenAI Batch API `/v1/responses` 的 `JSONL`，及候选强制身份/原章节/评分校验。
- `tests/test_health_editorial_batch_v1_20261029.py` 检查基础1080状态不能装成已完成断词、12真实盘不补年命及保持原始+/-5/0等级、GPT返回必须逐章节且不得修改case/grade。
- `.github/workflows/health_editorial_prebatch_v1.yml` 真实GitHub runner 测试+生成 **1080基础拓扑索引** 与 **12真实时辰人物完整事实输入**，存Action artifact和追加run报告；**只生产GPT任务，不向外部API发送，也没有12篇已审批GPT成品**。

## 实际 GitHub Actions
首轮真实运行 **#40901654390 PASS**，source commit `9fa86ceef50548306d9dc0be1cff80ef18cdb58d`：1080完整索引 / 12个既有真实时辰人物原始事实准备成功；Python专用测试已通过。
存档 `docs/HEALTH_EDITORIAL_PREBATCH_RUN_40901654390_ATTEMPT_1.md`；artifact 名 `health-v80-editorial-v1-topology1080-and-12-real-source-jobs`。最新确认Action随后的docs归档提交 SHA `29ef7ac1bbf26939fdfde962901823682a7692c6`。
本次GPT API调用=0；联网审核作为Prompt与工作程序准则建立，不声称已逐12篇自动做完联网比对；人工最终批准=0；新iOS JSON loader尚未接入。代码未改正式疾病V8计分、原始两本书、200/81、已接受模板或 iOS 界面。已有2026-10-28真实12篇文学候选仍与这批结构化新工作项不同，不要声称重新生成并审过12篇。

## 为什么1080不等于1080篇父亲断词
`2阴阳遁×9局×60时` = **1080基础时家转盘状态**，不包含真实月令、年月日、患者出生年命和人物条件；同一基础盘若源200格旺衰、真假空等不同就不能共用一篇断词。后续应以 `case_fingerprint` 哈希九宫、四柱、月令、选择用神及全部专题条件与V8判级，并关联 prompt_sha 与版本；审核后才允许精确命中本地资源。若未命中，则回退到冻结原生V10.2实时断词，不伪造缓存匹配。不能保证“1080父亲=1080全覆盖”。

## 特别审计：月干兄弟姐妹辅助宫还应看身份条件
外部《神奇之门》第六章网络转录（**只作为待核异文来源，不代替仓库原书原文**）
`https://www.zhaosir.online/Books/BookChapterDetail.aspx?did=1167`
提到同辈月干的同时，**大姐兼巽四／小弟兼艮八**作为条件象。与当前 `data/knowledge/phrase_library/health_v20/actor_profiles.json` 的 `older_sibling.palaces=[]`、`younger_sibling.palaces=[]`，以及 `src/wengua/health_dynamic_v21.py:182-207` 的年轻男性小弟才加艮8相比，待审区别是“大姐”是否需要明确排行信息才能加巽，以及弟弟是否属于“小弟”。2026-10-28 10:00已见姐姐和弟弟都取月干戊兑7并得到冻结V8=0；若擅自加巽/艮会改变参与宫和V8得分。**绝不凭已见0分追溯调参**。记录预期：只有得到实证排行条件和核准原书判据时才增条件宫；实际：程序目前不自动加入姐姐巽，弟弟年龄/性别条件未提供也不加入艮；需回归：父母/祖辈/兄弟/同宫重合/未提供出生年，及两固定回归与随机Swift parity。现只记审计疑点，不改V8。
此外网络其他流派对生门、死门、空亡新旧病有不同用法，不得混入既定轻重领域，必须注明流派和适用条件。

## 后续执行前提
1. 由可用并获授权的GPT API模型按已固定prompt从每一 `case_facts` 生成约200字首页与全部详细章节，结果只写新候选，原本事实只读；网络研究阶段另存有URL/版次/证据的audit_flags。
2. 上传 Batch API JSONL 需真实 `OPENAI_API_KEY`、核实有效模型、明确费用授权；本仓库不含密钥，CI仅准备事实任务。请求规范可查 `https://developers.openai.com/api/docs/guides/batch`；结构化输出 `https://developers.openai.com/api/docs/guides/structured-outputs`。API Batch 可能异步耗时，不能说此对话已生成全部稿件。
3. GPT返回后运行 `--mode validate` 严格保留所有section ID和冻结分档；规则错漏转待审，不自动修正；同源全文对照与人工签核后更新offline资源，再做正式Python/Swift native parity、macOS Xcode和iPhone bundle资源验收。
4. 古籍断词不是医学诊断或真实生命预测；无实际病历不能把「命悬一线」写成病逝，吉局也不能承诺临床治愈。需要现实诊疗时不以盘代医。
