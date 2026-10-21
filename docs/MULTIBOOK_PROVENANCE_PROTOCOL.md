# 多书籍、多版本、多轨制结构化溯源协议（WenguaApp）

本协议永久约束《神奇之门》《开悟之门》及后续所有古籍。2026-10-20 用户确认：《开悟之门》是《神奇之门》的后续补充，新增材料不得覆盖历史原文、原 V1、旧书结论、作者证据和审核状态。

## 同一概念，多个来源轨道
- 全局 concept_id 是搜索概念标识，不是唯一权威断法；book_id + section_key + source_sha256 + source_line_span + excerpt_sha256 是不可替代的独立来源证据。
- 结构化去重仅合并检索键与语义上严格等价的显示结果；无论新旧书意见一致或重复，都必须在独立 source occurrence 中完整留存原文、作者条件和版本。
- 明确 source track_id：书名、章版本、流派/起盘变体、适用领域、人物关系、数理系统与信息时序。可标记 reaffirms / clarifies / extends / supplements / separate_context / potential_conflict，均只是草稿候选，未人工复核不能认定等价或矛盾。
- 《开悟之门》第一篇地支固定宫位与24节气平均每宫三节气是两种不同映射轨道，严禁混作一份映射；九宫所含多个数须结合用神、旺衰、门星神和实际情境选取，不能硬编码唯一值。

## 多版本不覆盖
- 每次从远端已真实归档、经 SHA256 验证的完整 SQLite 使用 sqlite3.backup() 无损增量，原书全文和全部旧表旧行完全保留，不得从元数据/索引重建整库或覆盖先前二进制快照。
- 相同 SHA 的重复原稿只记录别名；有变化则建新 section.content_version，旧 SHA、原文字节、来源版本、跨书引用和案例阶段全保留。
- 每个版本保存独立 SQLite 和 XZ 及 manifest：基库 SHA256、原书 SHA256、输出/压缩文件 SHA256、准确计数、全旧表行检验、integrity_check、foreign_key_check 和当前 HEAD Python3.11/3.12 CI。
- 用户允许按此前历史方案上传公开完整 SQLite；始终提示书籍原文可能有版权与二次分发风险，新增第三方作品的授权不可由旧授权推定。

## 交叉溯源和审核
- 已有 semantic_assertions 保存来源条目；新增跨书轨道在 cross_book_concept_tracks 独立追加来源、track、归一化值、适用条件与审核状态，不改早期条目。查询可联结多书，但 App 不得自动用新书替换 V1 文案。
- 新书引用《神奇之门》旧案例，只登记 cross_book_example_references 的当前行、旧书页码、版本和未核对标志；只有比对相同事件后才能指到同一 event_family，不能凭再引用新增案例、盘或独立事前成功。
- 新旧观点冲突必须同时保留、准确注明不同条件和出处，标为 unresolved，禁止偷偷裁决、删改失败案例、把作者后验修正放到事前输入。
- 原文文字和图/格表原貌保存；只有真正印出的问事九宫才计入实盘，太极、先后天八卦、河图、节气和宫位示意图不得冒充新盘。
- 数据四层：A作者原话、B经来源校验的原书可核事实、C模型候选、D经人工批准可发布。所有自动整理的新轨默认 draft / positive_training_eligible=0，来源忠实与现实科学有效性严格分离。
- 数量/日期/历法仅按书中实际陈述保存；书中节气的公历近似日期不是对任一年精确交节时刻的证明，未经专业数据核对不能用于精确自动起局。

## 逐章固定工作流
先读根 AGENTS.md、PROJECT_STATUS、CHAPTER_LEDGER、CHAPTER_WORKFLOW、本协议以及最新远端 DB manifest → 读全原文和 SHA 比对 → 先归类理论/专题方法，逐案保留作者真实分步推理和反馈 → 按已存在 concept_id 查重并追加独立轨道 → 增量 SQLite 和回归/旧行保护 → 生成版本化公共索引和完整原文归档 → 同步 AGENTS/STATUS/LEDGER → 推送 GitHub，检验真实远端二进制 SHA 与最新提交的 Python3.11/3.12 CI。UI 与旧 QimenLLM 冻结。所有未来新增书必须保留 V1 的既有来源、版本、验证和可调用能力。


## 第二维度案例：开悟第二章要求显式区分的概念轨道

- nine_star_energy_vs_ordinary_element：九星旺相休囚废、地上五行旺相休囚死属于不同作用模型；九星以宫为主以月令为辅，不可因同一个“旺”标签覆盖彼此。
- heavenly_stem_life_cycle_vs_earthly_branch_cycle：十干阳顺阴逆、戊/己循丙/丁；地支五行不按天干阴逆、地支土循水。旧书与新书各自全源保存，不以同名长生合并周期或任意增加状态。
- center_host_derived_vs_book_printed_center：中五天禽与天芮同飞寄坤，是额外来源标注/算法派生；原著印盘中五若仅一字就只存一字，不设“平门”或伪中宫神星门。
- grave_vs_storehouse：月令旺相且落墓位在书的解释中称入库、休囚称入墓；保存相反条件和原书错误复盘（第二章180及199行），不可盲贴一个“入墓”凶断。
- domain_conditional_doors_and_deities：八门与八神具有同一符号的多种问事含义，不支持从词面吉/凶标签直接硬生成临床结论、刑事指控或寿命；至少考虑门宫生克、月令、人物关系、星神及格局。
- 本章图23–33教学九星、十干和八门，不计实印起盘。新书9次引用旧书的页码是引用而非新 event、外部验真或独立准确率；读者必须再核对应事件，旧案明确首错不得被后验正解覆盖。


## 第三章新增规则轨道：完整教学起盘与历史预测严格分离（2026-10-20）

原书七步中，值使门先按**九宫1..9数序**随旬内时辰以阴逆阳顺决定目标宫，再按外围**八宫圆形顺时针**布其余七门，分别是 `value_door_nine_numeric_count` / `peripheral_eight_door_ring` 两轨，不能因同是门盘就用一个算法。九星外围按其固定顺序旋转，天禽寄坤2与芮同走但原宫源字永远不伪造中心门神。八神随值符星而非值使门、阴阳顺逆旋转；不同流派转盘/飞盘算法不得硬合并。

凡教学图，无论是否已展示完整九宫，独立入 `kaiwu_didactic_figures` + `kaiwu_didactic_figure_cells` 保存每宫实际文字；不混原来的103完整历史案例/112源盘。在作者仅显示简化门星盘时，没给出的八神字段必须留空，不能用确定性算法偷偷填为“原书来源”。反事实阳遁演示等也作为未实际问事的教学示范。已有源本的同概念/新书差异始终多轨保留；全部研究候选draft、正向训练资格0。排盘算法与两本书源文字一致不等于天文时间验证，更不代表现实预测成功。


## 《开悟之门》第四章：主客方向、条件化应期与旧案例再分析的新增永续约束

十干克应为**有序天盘/地盘符号配对**：原书81个，不是完整笛卡儿积100个；缺失的组合不得凭倒序补造。每个独立来源键必须保留天盘客、地盘主、作者各自比类取象及能逆转吉凶的限定（问事领域、门迫/入墓/击刑、月令旺衰、上下身份）；跨书同名格仅共享索引，不覆盖原始古籍断词。应期必须先区分“成功”“失败”“破获/找寻/阻拦”三种**先决判断轨**；庚格需验证空亡或乙庚合是否使格无效，作者事后解释和未能初断不许转为事前命中。内外盘阴阳遁反转、值使宫数候选与具体尺度、旬空和驿马地支都需单独条件，不能机械全局吉凶。2026-10-20新章第228行作者坦言银行案具体应期当时未断出、第232行找发票实到日比断日提前一天，这些来源阶段永远保真。重印旧书历史九宫及教学五行格应单独存来源引用/图字，不新建历史事件、不复制旧实盘为新盘。

## 古文与后出作者解说双声音保真轨（2026-10-20）

同一本书中的“古文第N段”与“解说”不应当视为一个原作者一体化命题。逐句保存古文原文和后著作者解说原文的不同sha、不同source_line、不同source track，任何现代解释不能反向覆盖古文。复用既有概念ID只能追加独立跨书/跨时代来源，不合并原文字节或断案历史。书中的置闰、拆补、职业命运、健康与家庭结论属于传统作者表述，不能直接当作现代科学证据或个体安全建议。古文+解说不等于新问事/新盘/独立命中。


## 2026-10-20 《开悟之门》病例与《神奇之门》现有health域统一

医疗/疾病相关的案例必须重用 cases.domain_id='health'，新书和旧书只是不同的book/source/provenance，不允许再建另一套独立“kaiwu health cases”域，也不可把动物疾病放到没有统一检索的隔离案例表，animal_health只作为health内subdomain。遇到同一历史事件在两书各有完整盘，必须分别保留各自原文source witness和九宫原字，但cases/event_family_id只保留唯一事件、historical_chart_cells独立历史盘数量只计一次；重复来源不当独立盲测或两次成功。第一节例二B1996-07-27女问辛酉年父病原属 shenqi.health.19960727.father_illness；例二A1995-02-19弟病来自作者标“奇门学术论文之七”的第三方旧论文，没有完整初断，只可作为注明缺失事前断词的独立比较素材。案例前后阶段要分：known_before/原印盘/作者初断/书内事后反馈/编辑事后比较，不能倒置。死亡时间未实际观察则不声称精确命中；原始未知天干/异常星神符号保留缺陷并来源标注，不擅改。医学治疗只能由专业临床判断，这些古籍表述非临床证据或治疗建议。新版统一查询view health_cases_all_books用于复合检索，所有基础历史表和多书轨道不可覆盖。


## 2026-10-20 跨书人体疾病同领域事件归并的真实归档例

2026-10-20 《开悟之门》第二章日常百事第一节人体疾病预测原文SHA 49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d，实际书内六个场景六张印盘。和《神奇之门》统一cases.domain_id='health'且统一查询视图health_cases_all_books，重复同一1996-07-27父病只存一个event family（shenqi.health.19960727.father_illness），新书第二份原印盘保留为健康跨书来源witness及9个逐字原宫，但不新增历史盘/案例的独立计数。新增五件新历史事件、五张新独立起盘、21个作者步骤。另存AB事后比较不能代替原事前预测，完整原文和章/书/时序/证据多轨共存。当前新版父SQLite SHA256 79b30135e42129f6596c66f09eec66496ae5d08afb8786f2831581f3fe7c6b05，从前完整版本SHA 1c445680fa5bb4ea928b5154f7cc8c1f0957681cd94dc062e02ffb601461ba9e使用sqlite3.backup生成、旧数据逐行不变。今后跨书同案默认事件维度去重、source witness维度不去重。对人体/动物健康的传统来源断词不是经验证医疗判断；所有新增规则draft、正向训练0。严禁倒灌后验或填造原始宫位缺失。


## 2026-10-20 用户最高优先级：原书历史案例无需再逐例人工审核；跨书同域统一

凡用户主动提供的《神奇之门》《开悟之门》原书完整案例，书中问事、原书断语及后来反馈按用户认可的历史案例来源直接建库、使用、做书内结果对照。不得因先前脚本reviewed=0/draft或缺乏外部验证而强制用户批准每条案例；旧版原始行无需修改。始终如实保留源内第一次预测失败、书中作者后验纠正、信息何时出现、重复事件及多盘、无盘/无反馈事实；不得把用户认可书中记载误说成外部科学/临床证实或危险专业建议。跨书按 sports_competition、criminal_case、health、military_history_source、litigation 等统一domain_id和 event_family_id 索引；不同书只增加独立 source-witness/书内论证轨，不能按书名分裂业务案例库。新增复杂年度趋势可带多领域标签。用户认可规则对老书新书一体适用。原书2026-10-20提供《热门话题预测评析》13专题、20真正来源印盘；北京2008申奥第九/十三是同一event，台湾2000选举第543行原书作者明确认错不可假装事前命中。最新父库SHA 79b30135e42129f6596c66f09eec66496ae5d08afb8786f2831581f3fe7c6b05，仍须无损sqlite3.backup增量，全旧表保留。

## 2026-10-20 跨书恋爱婚姻案例领域归并、同人不同事与书内首次错断

《开悟之门》第二章第二节恋爱婚姻6例完整源sha256 4df9dfe432daec759df4f0e01449bc4a2381eb4251e1290a0d99d199e467fa01，305行/34960字节。六例都并入原《神奇之门》同一个marriage领域，不为Kaiwu另建业务案例库；6真印盘54原宫字及26分析步骤完整保留。第2/3例是同一个女性在不同时间提问不同婚事，建立同一人物关联而不合并历史独立事件；第4例兼就业及遗失钱物，第5例兼求财，用统一跨域facets查找。两件后续工作/复婚经营未来结果原书未给，不能补造。第6例原书作者初断单相思女性，被求测者明确回信“准确度极低，大相径庭”，新信才披露同性恋情，后出作者重释不能倒灌到首次推断，保留为新增书内明确初断错例。性取向本身不属于疾病或需治疗状态，古籍内旧时代叙述不可当作现代医疗诊断。第6例只有一张完整印出的盘；另外出生局及后信起局两盘作者自己省略，不补造成原书实盘。用户接受古籍案例无需逐例批准仍有效，但不能将用户认可书中事迹理解为每次首次断语均正确或经独立科学外证。下一版仅从当前28节全量SQLite sha 6dfe4337697e64a100f63de0b9d5144ad00e3b2e3fa818d9d314ea304a92a10d 无损备份追加，所有旧表原行保持。


## 2026-10-20 跨书工作就业同域、同局双事项、未知原盘和后验时间绝对保真

Kaiwu原书第四节工作就业3例来源SHA eeaaa79d23528dfc608282f6ab0b120620a7c44d67588145a9166a9bd03c733e，150行14577字节。三案例3真正来源印盘27原宫字、作者步骤13+后来编者评论4。与Shenqi现有employment业务领域共用case表，附组织任命/组织资格/交通事故标签。例三只一1997原局，对次日入党申请与1999农历二月车祸警告分两事项报告，却不能拆成两个事件两张盘；具体1999二月二十三日源书明说是在“前几天死了一个人”的事后消息以后才推算，禁止事后信息污染原始1997预警。原盘header甲午日与分析称日干辛有字面差异，保留二者而不改原书。例一原文阳5局当时采用置闰法，坎1门和星分别注明“原文未辨干”，两处天干不可推断补写。例二值使杜门中五宫寄坤二宫，原书中五不适用强行补普通星门。书内案例用户接受无需逐例人审，书内结果标签与外证仍区分。下一版严格从29节完整父SQLite SHA 64a01b16828dff326e1d0a2bd759147032fb8ef30869aa595be7aae04d492339 增量，全旧表行保留。


## 2026-10-20 Missing-person two-book event identity, unreadable source and same-event casts

Kaiwu seventh section 行人走失预测 original source SHA256 193e1eb8438a83e1408efa804daf66ea43e64f36155e221be23c9de53215ab71 has five original lost-person event families, six printed ASCII Qimen boards. The same niece is represented by a genuine inquiry-time board and a different genuine disappearance-time board; one family, two source casts. Two abducted hotel workers are distinct subject outcomes of one real inquiry and one real chart; do not count twice in performance or event families. The new male taxi homicide report references older Shenqi Ma Lande's female taxi-driver story as a similar *different* event: retain an explicit bibliographic reference, not a duplicate event and not an unverified hard-FK asserted same-case join. Another student predicted Aug16 home but the reported actual return was Aug17; preserve exact timing miss while keeping other source-reported aspects.

ASCII 3x3 palace grid may have 4 or 5 genuine per-band text rows. The special extra fifth row in new source chart six contains OCR text 原OCR：庚 辛 and MUST be kept in source witness; the conventional 4-row parser would silently lose it. Original unreadable OCR cells, gods, doors, stars and middle-center literal cannot be filled by recalculation; keep literal and missing-data flag, and omit uncertain standardized values, never overwrite source. The entire 200-line 27441-byte user text is preserved. The user directly accepts book historical cases with no case-by-case approval, but independent modern criminal or forensic evidence is not claimed. Next fully verified parent SQLite SHA256 9107e3e440a1448cce93fdef288a48c88a8440b3998c5adcf041e2f770172ae7 (32 source sections / 138 unique events / 155 real printed charts). All old rows must be immutable through sqlite3.backup.


## 2026-10-20 共领域业务/工业安全与书内明确错误的跨书来源纪律

开悟之门第五节经营求财11原书真实问事、11原书九宫，整章全文源SHA256 10d777fe514315c8e56dbef6d6a5152300b79c0ed041b92ee10f15cccef18fdf。既有Shenqi business_profit共领域新增十个求财项目；煤矿塌陷第五? 实为本节**第十例**，单一真实工业救援事件主域industrial_safety，附business_profit关联标签，不能以业务分类掩盖人命安全属性。第4/5科迪药业同一项目不同时间问资助与开工，第7/8太和日化城同一工程不同求测人的开发与独立购买问事，链接same_project但不是same_question，不合并event_family，也不算重复预测成功。第5例书作者原先6月21或22开工预测明确错，实际6月29取得证后开工，事后重解释不是初断成功，新全库整例明确错误9条。第8例只能证实预付三个月租金，不能宣称三年投资已验证；第11例其它大奖少年无独立来源九宫不能新增一盘一例。原书所有OCR缺损和原宫额外第四行raw不推算补字；中五宫只打印X干不可以填普通八神/门/星。原书问事项目直接接受无需再次逐例用户人审，但不称独立安全/财务/刑法科学核验。下一章父库必须是完整SHA256 cd1f9e1d4e352644b062bc048afb977dcc457c40bf76a5673a6e39ae93f21ac5（33来源节、149独立cases、166真实印盘）；旧行全部不可变。
