# WenguaApp V3.0 下一会话交接（2026-10-22）

## 权限与仓库状态

仓库 turnupmason/WenguaApp 的 main 分支继续历史所有工作，不重开、不改写、不覆盖旧版本。194个古籍真实事件家族、43个源章节、旧开发失败记录和所有历史 SQLite 必须保留。用户在本对话亲自提供巨量疾病占方法，不能让用户下一会话再粘贴。最新完整已绿的V2.9数据库为 archives/sqlite/WenguaApp_双书194案例_精简医药旺衰应期V2_9_完整研究库.sqlite3，SHA256 511f3b18404d72d185d1e01c79258ac53d5f3aab66235092d9fd7c2e03c27f19。V3.0新增方法库及增量库如果通过CI，则最新父库以V3.0实际manifest为准，不得由V2.9重新开始。

## 本次高价值疾病方法入库

全部重点已归类入 data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json（总方法与争议）及同目录 user_20261022_pair_catalog.json（42个有序天地干格局，17类复合规则）。用户原句为个人提供的重要术数材料，不等同于已经逐行校对完成的古书文本；保留source=user message，不虚构原著hash/行号。部分OCR王可能为壬，门追可能为门迫； raw 与 normalized 分轨，不抹除异文。双书真实原文及其独立来源继续原样保存。

患者用神优先：本人日干；妻子日合干与乙；丈夫日合干与庚；父母年干并父乾6母坤2；兄弟姐妹月干；子女晚辈时干；动物无用神取时干。一个问事同时涉及多人的健康，则各人分别绑定，不能机械用一张天芮归因。已提供年命时以人物本身状态优先综合，没提供绝不猜。患者用神决定传统生命力权重；天芮主疾病现状部位并参考地盘天芮本位坤2；时干主病情发展趋势，日时及病宫五行有向生克要断传统偏吉或偏凶；值符值使有实际用神关联时纲领作用提升。新旧病/年龄/性别缺少信息不得假定。

病星五行：离火生天芮土旺，艮坤比助主拖延，震巽木克土制病但辰月土旺可能仍凶，坎病土克水久拖，乾兑土生金传统也有难治象。关键是病星、人物、时干、值使、奇门神、月令和格局共同判断，不机械数证据。天芮所在宫与坤二宫本位不可混写两个真实天芮，后者为辅助参照。医药：天心西医、乙奇中医的古籍符号；时干同天心或乙奇宫，或者病宫同天心或乙奇宫，都象征有及时医治机会，不直接代表治疗见效。天心的九星月令旺相休囚废、乙奇木干月令旺相休囚死须分别计算；开休生/死惊伤景、太阴、白虎、螣蛇、玄武、杜门、值符及其空、门迫、刑墓条件须逐宫真算。医生/药能克病宫为传统有利，反过来病克医药不利，但不能建议现实停止看病。

新病空亡或反吟在古籍可视转愈，久病空亡或反吟偏凶；伏吟慢，反吟快，缺新旧病事实不写。时干所见疾病现状、马星动冲、墓库出墓/冲墓、旬空填实冲实、六仪击刑逢冲转合、伏吟冲为应、反吟合为应、内外盘远近以及值使门数，只在足够证据时才算应期。无事实不造日期。六仪击刑：戊震3己坤2庚艮8辛离9壬巽4癸巽4，三奇入墓乙丙乾6丁艮8；一切都必须来自真天盘落宫，墓库需月令再辨。

《诸葛武侯千金决》古句所涉及戊丙/丙戊、辛乙/乙辛、丙庚/庚丙等顺序干克应，病宫与患者宫可能相反，辛乙原古诀和实践判断相互冲突应多轨保留。地遁、鬼遁、人遁、鬼假、人假、三诈、三奇得使、玉女守门、三门四户、丧门吊客、马星、六仪击刑、入墓、天网罗网、伏干飞干、荧白反转、大格小格、五不遇、新旧病逢空等，规则已索引但并不是全部已完成条件引擎，按完整图层实际成立才触发。庚辛颗粒/肿瘤、己囊肿、戊良性、癌症候选以及病部位九星类象，仅保留为古代象征，不可当现代确诊。书中“必死”“必癌症”的表达属于被记录的古语，用户端不得直接预测某人必死、确患癌，也不能给停药建议。古籍占断吉凶不是医疗预后。

## 工程交接

V2.7既有五不遇时、性别乾坤、内外盘、真正伏吟反吟、吉凶关系；历史1996-05-23庚申日丙戌时女性姨母例，仅V2.7那个原断词用户说“第二个对的”，不代表V2.8、V2.9、V3.0新版文字获批准。1996-11-02癸卯日庚申时例仍待审核。V2.8已有及时医治两种同宫、天心乙奇分月令、入墓/六仪击刑，V2.9删除同一段月令重复，均已归档。V3.0基于V2.9新增病星地盘本位坤宫、时干与患者关系、真实有序干克应的角色敏感取断、有限已全部满足的遁/假、新病久病才出现的条件应期，并采用原有静态离线11段为基本结构，不再造第二套LLM。新增文件：src/wengua/health_severity_v30.py，data/knowledge/phrase_library/health_v30/severity_fixed_template.json及两个方法知识JSON，scripts/run_two_historical_health_v30.py、scripts/build_health_v30_archive.py，schema/migrations/058_health_user_disease_supplement_v30.sql，tests/test_health_supplement_v30.py；请检查实际工作流和新版本manifest再宣称完成。把用户提供的所有规则可检索是知识整理完成，不等于42个组合、17个复合格局已经全部回归证明；未实现项必须留在status。

每次最终断词严格由本地Python读取九宫+本地SQLite+固定JSON模板生成，不准GPT或联网二次润色。简洁、不重复、用户只见“依据古籍”及实际宫门星神干、明示吉凶和最后传统主判；原书line/hash/工程日志放后台审计。历史样本预测封存SHA后方可看原著断语，不能回头按答案修改预测。病例虽来自真实书籍，不可冒充新秘密盲测。必须保留194个原始家族/43节和所有失败实验。

## 用户下一对话要做UI以及其他四种健康子模板

此前UI冻结只是之前阶段没有用户明确授权；用户已经说下一会话将处理UI与其他模板，因此下一会话如果明确要求UI开发就可以开始，但**本轮不要提前建UI**。其他四个意图 treatment/discharge/surgery/travel_for_treatment 目前历史草稿没有用户专业验收，不得自动解冻和宣称批准。新对话如指名哪一类，先展示简洁11段以内纯静态中文替换字段模板供用户审，再真实起盘测试，保留失败及用户审批。下一会话先核对根AGENTS最新段落、PROJECT_STATUS末尾、V3.0 CI和数据库SHA，再沿现有代码继续；不要重开工程、复写旧档，且不必要求用户重复提供这些规则。


## V3.1 FINAL verified next-conversation superseding checkpoint — 2026-10-22

**USE THIS INSTEAD OF EARLIER V2.9 OR V3.0 HANDOFF LATEST-PARENT CLAIMS.**
WenguaApp latest immutable COMPLETE SQLite: archives/sqlite/WenguaApp_双书194案例_患者时干病事有向修正V3_1_完整研究库.sqlite3
SHA256 **3a72dbb798d73413c2ebb994e232b83039a483d91cfa8a8f60f246d4ad84b529**.
XZ SHA256 **6652672be87874aa194a82e0669799760a0e12934bbfb3465d0f2f9382d46f16**.
Parent full V3.0 SHA **713081aed68bb38172ae506d78c1cf59a1853f64daf14be360507e6670baf27b**; V3.0 parent was V2.9 SHA 511f3b18404d72d185d1e01c79258ac53d5f3aab66235092d9fd7c2e03c27f19. Latest archive manifest archives/sqlite/wengua_health_v31_manifest.json. No old database, historic experiments, original 194 events, 43 original chapters or 2 previously failed developer predictions were overwritten. V3.1 versioned migration is schema/migrations/059_health_patient_hour_direction_v31.sql. Its full-source regressions Python 3.11/3.12 SUCCESS GitHub Actions #39789491358; full WenguaApp CI both Python versions SUCCESS #39789491067. Original V3.0 was initially CI-green after fixing a brittle test but post-seal manual evidence review revealed a genuine invalid subject/sign: had reused 时干-病宫的健康标签 as 时干-患者宫, giving “时干病事宫克患者宫” 偏吉 when it must be 患者受克、偏凶. **Retain the V3.0 actual wrong readouts as a real failed research iteration**, not delete it or silently rewrite original source. V3.1 codes: src/wengua/health_severity_v31.py and new fixed slot data/knowledge/phrase_library/health_v31/severity_fixed_template.json, which independently computes patient compared with real 时干病事宫, applies 古籍人克病为吉、病克人不利, and preserves all other V3.0 output/audit. Two updated readouts newly sealed data/evaluation/health_v31/two_historical_patient_hour_V31_SEALED.json SHA256 **0f84c309524b7de8c7aa38e235a6db7837cf898753504f1a555c657305fa062e**; 1996-11-02 self corrected SHA **36b386e3c9be334aa3b367265c2aec76cad4850fa6faea397371ea7b681065c6** and 1996-05-23 aunt corrected SHA **4e4763a5c92b88cdd66eb3f3cee752b42fa105d89c74cbbd2832762ef3071b10**. Previous book cases not independent new secret blind tests; output review for new version still PENDING. User's previous positive feedback ("第二个对的") applies only to original V2.7 female aunt readout, not these new versions.

User-provided long supplemental method and all extracted catalog items available in data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json, user_20261022_pair_catalog.json (42 ordered stem pairs+17 composites) and docs/HEALTH_V30_NEXT_CHAT_HANDOFF.md. The catalog has SOURCE TYPE user message; don't fabricate original book chapter/line/hash. Only a subset of conditions is truly calculated; remaining rows are indexed for future tests, not certified fully coded. No GPT, no online per-chart generation, customer prose from local fixed template, and no real medical diagnosis or mortality claims.

**Next user chat authorized goal: UI and other disease templates.** UI was frozen under OLD instructions because not authorized then; user now plans to explicitly request UI in next chat, so follow the next explicit request and can build UI as instructed. Do not proactively add UI before instruction. Four other health intents treatment/discharge/surgery/travel_for_treatment are still UNAPPROVED drafts and require user to view concise fully-dynamic source-driven template, see real offline test, then explicitly accept. Don't misreport that user approved the other four. For future full SQLite use exact current V3.1 SHA above, append migration060; NEVER reset repo or overwrite previously sealed V27-V31.
