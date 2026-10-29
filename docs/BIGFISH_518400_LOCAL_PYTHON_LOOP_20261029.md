# BigFish 60×12×60×12 四柱条件批量离线生成器（爸爸→妈妈→弟弟）· 2026-10-29

## 本轮用户明确要求（覆盖前次逐日批量方案）
只需要 **Python 源代码**，不再要 .command 脚本。默认父亲 `RELATIONSHIP='father'`，以后改为 `mother`、`younger_sibling` 等分别一次跑完。对每个人物枚举 **60个年干支×12个月支×60个日干支×12个时支＝518400个逻辑四柱标签组合**。月柱干必须用五虎遁从年干推，时柱干必须用五鼠遁从日干推；不能做非法的60×60×60×60干支随意笛卡尔积。当前冻结 `data/knowledge/phrase_library/health_v20/actor_profiles.json` **实际22个**关系 profile，并非旧本地脚本写死的11个，也不是恰好20个。本轮代码动态读源22个 profile ID。

**历法诚实边界**：518400是组合索引数量，不等于这518400条都存在可验证的实际公历起盘时刻。某一月支内有两个可能生效的24节气（例如戌支寒露/霜降，子支大雪/冬至），它们的局数与真实盘可能不同；没有准确公历日期不能选一个作为唯一真实节气。为忠实保持518400行、又不遗漏两个时令，**每行分别计算两个节气分支与两个V8断词**，标注 `抽象四柱条件候选、未绑定真实公历时刻`；并不将其暗指为现实已证盘。若用户以后要按真实公历批量，仍用 `local_batch.py run` 的真实时区日期枚举。

## 用户可下载代码
本轮已在对话沙盒生成 `/mnt/data/wengua_518400.py`，SHA256 `b761a0705007e2275fa24781788f7271fe4b195b0c7ab3497b7949c3cef99a52`，代码542+行，需放在先前 `WenguaBigFishLocal_20261029` 安装文件夹、`local_batch.py` 同层（其 `vendor/`、`frozen/`、`bigfish-compiled` 由首次 `install.command` 联网安装得到，**此新代码不会调用在线GPT**）。代码本身作为本次会话单独可下载 .py，不能假称 GitHub 本次已提交其原始源码的完整文本；本仓这份独立文档是交接/源哈希。普通终端直接 `python3 wengua_518400.py`；顶端 `MAX_NEW_ROWS=0` 默认把该关系未做完的所有组合继续循环、`MAX_NEW_ROWS=20` 可先生成20行；每5000行一个独立Excel兼容 `.csv`和真正`.xlsx`文件。中途 Ctrl+C/终端断开后重跑自动续跑 SQLite，不要求用户打开/懂 SQL。最终输出目录 `output/full_518400/father/Excel_CSV_可直接打开/` 等，切换人物生成不同数据库及输出目录。已导出的CSV和XLSX**不覆盖**，可人工/GPT独立修订（改动不会自动反写原数据库）。

## 算法与资源保护
- BigFish 真原始 `shiJiaGenerate`+原 `chaiBuJuByGanZhi` 在一个**常驻Node进程**中真实执行。按 `(yin/yang,1..9局,时干支60)` 缓存最多1080实际九宫布局及原始TS JSON（物理缓存不是随意代替单案月令）；节气/真实日柱的三元局数继续按原BigFish函数查出，每条四柱组合与每个节气分支都单独交给冻结 V8 `analyze_health_severity_review`。
- 仅允许现有 `candidate_source_gate.py` 在本机单进程验证新BigFish物理九宫来源，绝不将旧Shenqi重排盘冒充新源；冻结V8.0计分、200格/81格、V10.2客户断词、人物源、Swift、Important双镜像/MANIFEST未修改。公开的原本符号等级不是临床预后或医学确诊。
- 中五不冒普通星门神；坤寄天芮/天禽独立携干，源字段反转 skyStem=实际地干、earthStem=实际天干依旧由原 `local_batch.normalize_bigfish` 正确处理；原BigFish 24节气拆补局与两个可能节气均保留；出生年命不存在绝不捏造，人物排行/年龄/性别可在代码顶部**真实已知时**给定。
- 结果按行储存完整两支 `节气、局、V8等级、文本、原物理盘指针、证据哈希、失败原因`，每5千行一个Excel友好的独立档，供未来人工/LLM改写，但原候选文本从不自动晋升为已验证的App结果。

## 本轮实际测试与未验收
- 当前会话实际 `python -m py_compile` PASS；
- 518400公式与四柱枚举索引、五虎遁/五鼠遁（丙午年戌月→戊戌、乙亥日卯时→己卯）、24节气两分支、前10000组合唯一键 PASS；
- 构造临时SQLite两条记录后，真实生成CSV+XLSX：读回中文、BOM、公式注入防御、Excel行数、无覆盖 PASS；额外使用 `artifact_tool.SpreadsheetFile.import_xlsx` **真实读取自写XLSX成功**，标签为 `逐时辰条件候选`、A1:AG2；
- 动态长连接Node的生成脚本 `node --check` PASS；
- 本会话容器无法解析github.com，**未运行真正安装/BigFish 518400条/Python V8 1036800个分支**；不能称这些批量盘已全验收。先前原始BigFish实际TypeScript1080结构 #40920402953 PASS 和2个真实钟接V8 #40921478524 PASS，不等于本轮大循环整体通过。
- 本轮只交付新的独立Mac Python生成器及源哈希交接，**不宣称 iOS Swift已经替换成BigFish**。既有真实Swift全盘失败 #40905670829、BigFish首轮来源门槛失败 #40921332503等仍在历史保留。