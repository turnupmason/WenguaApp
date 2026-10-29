# BigFish 518400 本地批量：已绑定人物主用神、可选真实年命、输出完整证据 · 2026-10-29

## 用户要解决的问题
单次每关系518400个60年干支×12月支×60日干支×12时支的**抽象合法四柱条件**；每月支两个不同可能节气独立由BigFish真实TypeScript生成并接入原Wengua V8.0量化/V10.2完整中文，供后续GPT+人工编辑。用户追加问「确保关系用神成功接入，然后我要写什么确保用神正确。如果后面有年命呢」。

## 原始正式源已实际核实（固定Git `0eae7d2b94742939e885938f8603e85c9452d1c3`）
`data/knowledge/phrase_library/health_v20/actor_profiles.json` 是真实22个 profile ID（包括合称、动物、其它亲属，并不等于用户口语中20个都已独立完整验收）。`health_dynamic_v21.bind_patient` 与 `domain_selected_energy_vnext.selected_health_sequence` 真实定义：
- father：问测**年干**为主，加男性长辈乾6宫；母亲、祖母对应长辈坤2宫，祖父乾6宫。主问测年干不等于患者出生年命。
- younger_sibling/older_sibling：问测**月干**为主；年轻的男性弟弟满足额外代码条件才增加艮8辅助，不可所有兄弟姐妹通加。
- 本人日干，晚辈/子女时干，妻子乙奇、丈夫庚金，配偶合称需要明确性别。孩子/儿子/女儿/侄子年龄排行仅在确实提供性别与eldest/middle/youngest时考虑相应辅助；**兄弟姐妹的BIRTH_ORDER不被当前原源使用，新增前置错误拒绝静默忽略**。
- `patient_birth_ganzhi` **真实出生年干支有才传**，无则不出现natal用神；如果出现而无法选中实际年命星干宫，必须保留失败而不是假称已审断案。出生年干支要求真实生日与立春界线核准，不能用户只写'1920'或'甲'就补造。特别 `甲` 当前旧绑定器在年/月/日或出生年可能借用**小时旬首**，本版拒绝跨来源自证，独立书源待核，不改冻结V8公式。

## 可下载修正版源码与输出
本轮生成可直接替换原Mac PyCharm同名文件 `/mnt/data/Wengua_BigFish_518400.py`，SHA256 `20c1cd0dd12a59d1a50d157872f50f6117bf6950ce41e90526b7e85937582693`，68188 bytes；含说明的ZIP `Wengua_BigFish_518400_关系用神与年命校验版.zip`，SHA256 `7303892141d18da9bff78c6fa39279e4c5739d7134984d88c7a90f4ba74e66b9`，CRC通过。完整 Python 实际同步 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` main；不需要任何 .command；沿用本机已有`local_batch.py`。
顶部填写示范**不是用户亲属的真实资料**：
```python
RELATIONSHIP = 'father' # 之后 mother、younger_sibling
PATIENT_SEX = None # 男性弟弟如真实可写'male'
PATIENT_AGE_BAND = None # 只有真实符合年轻弟弟时写'young'
BIRTH_ORDER = None # 仅子女/侄儿有明确排行时写 eldest/middle/youngest
PATIENT_BIRTH_GANZHI = None # 后来证实的某人真实年命才写完整六十甲子，如'乙丑'
CONSULTATION_CONTEXT = None # 自动self→direct_self，其它→direct_proxy；闻讯特殊另明确
MAX_NEW_ROWS = 20 # 小试；回0继续全部未记录条
```
运行会先读真源JSON并拒绝人物/性别/排行/年命/问事方式冲突。前3条**新算**的两节气分支打印实际主用神来源、干、宫、年命是否另参或不参与、具体失败；以后每条成功需 `verify_actual_role` 与V8量化角色 patient/natal/gender逐宫一致，输出 `人物用神与年命配置核对.json`、Excel末尾主用神/年命10列和JSONL `frozen_fact_lock.person_binding`（含来源/主宫/辅宫/真实年命/另宫）。
修改年命或其它可变参数时自动置于 `output/full_518400/<relationship>/年命_<干支>_<sha>/` 等新隔离子目录，不覆盖原无年命20行的SQLite/CSV/XLSX、已审稿、原失败；原出生年缺失时输出路径仍完全沿用旧版。年命改变的事实必须**重新运行全案评分**，不能给旧结果补一句年命。

## 实测与失败链
- 本地新Python py_compile PASS、新增7个隔离人工/mock测试 PASS（参数验证、关系/年命另存、已知甲来源拒绝、Excel扩列）；之前Node SSL安全初装合同保持，未在本环境Mac真正执行全518400。
- GitHub专项CI `#40941942424` PASS，实际读取主仓22人物原源并验证9个测试包括真实本源父亲/母亲/弟弟主用神取力、真实出生乙丑独立落宫、男女性别/排行输入阻断、旧甲来源不假成功。
- 初加真实4案BigFish集成CI `#40942273256` FAIL：**纯测试夹具误缺 `local_batch.normalize_bigfish`**，不是BigFish九宫或者V8错误，失败日志完整保留。将用户实际Mac包 `local_batch.py` 原封实现复制为仓库测试参考源 `scripts/bigfish_local_batch_reference_20261029.py`，源 SHA256 `bab8ad0e45a8ac1913e555a47030a3beccf745ddb493bbd58b0fb40bab591310`，测试夹具只复用其normalize函数，不发明新起盘。
- 经修复的 **真实原TypeScript 1080结构 + 2个真实时钟 + 4个实际BigFish→原V8/V10.2人物/年命** 专项CI `#40942647716` PASS：
  - father不报出生：丙午年/戊戌月/乙亥日/己卯时，霜降阴2局，年干丙患者真落巽4、乾6辅助，原始分-5（传统象意）、无年命。
  - father额外**模拟**患者出生年命乙丑：父亲主用神仍年干丙巽4、乾6；额外年命乙震3，原始分-5，但**全文SHA从9eba...变为ac1d...，证明独立年命被真实接入，不是简单增字段**。
  - mother模拟乙丑年命：年干丙巽4、坤2辅助、乙震3独立年命，-5，全文hash独立。
  - younger_sibling：月干戊坤2、没有乾坤长辈辅助、没有年命，-5。
  - 全部此4案为真实编译的BigFish TS原盘+Wengua现行冻结规则，不表示模拟的乙丑是用户家人的真实生日，也不表示科学有效医疗预后。4案未入App。
- 当前补触发正式Python/Swift native全文 parity和macOS XcodeGen Simulator bundle资源CI，**实际结果应从相应 Actions查看，没完成前不得说PASS**。本轮冻结V8/200格、81格、V10.2模板、人物源原JSON、Python真实判断函数、Swift正式核心、原著、Important双镜像与MANIFEST未修改；只加Mac batch核验/质量门槛、测试与审计。不删历史失败。

## 下一步
可本地爸爸 MAX_NEW_ROWS=20 核对启动打印及Excel新来源列，确认后改0跑剩余；后来真实年命出现单独新条件树重新跑。注意518400是组合索引、每行两节气候选不能冒充真实公历起盘事件。批量GPT/人工只润色、保留原结果/事实sha，审核放行后才可打包离线iOS。
