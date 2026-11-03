# 专业特征 V2 与 PyCharm 本地运行

本轮用户授权：接入所有已有专业特征，支持 Windows、RTX 4090 和 PyCharm。入口为仓库根目录 `run_professional_training.py`；旧 V1、旧模型和失败/早期运行目录保留。当前活动研究索引为 `data/knowledge/probability_research/active_research.json`。这是独立研究模块，不改已封存疾病轻重 V9/V11、病位 V27、应期 V4、App 页面和原始数据库。

## Windows / PyCharm 直接运行

先更新本地仓库：

```bat
cd /d "%USERPROFILE%\WenguaApp"
git pull --ff-only
```

用 PyCharm 打开 `WenguaApp` 文件夹，将项目解释器设为之前已安装好依赖的：

```text
C:\Users\wtmas\WenguaApp\local\probability_env\Scripts\python.exe
```

右键根目录 `run_professional_training.py` → Run。也可以选择仓库提供的 `Professional GPU` 运行配置。默认自动执行：

1. 全部194个事件、主宫表和19张真实补盘的只读来源核验。
2. 九宫、81有向关系、用神及专业特征导出，保留未知和不适用状态。
3. 逻辑回归 CPU 的五组对照。
4. CatBoost GPU 的相同五组对照。
5. 模型保存重载、逐分数核对、结果汇总和其他任务的真实状态报告。

不用设置 `QIMEN_PY`、`QIMEN_RUN`，不用激活环境；每次运行自动建立新目录。开头会打印实际 Python 路径和输出位置，每组模型、每个留出折都有即时进度。若选错旧 Python 3.8，会直接提示切换解释器。这里未远程控制或实际点击用户的 PyCharm。

终端等价命令：

```bat
local\probability_env\Scripts\python.exe run_professional_training.py --device GPU
```

仅跑 CatBoost、切换 CPU、只导出、单独使用原有训练器：

```bat
local\probability_env\Scripts\python.exe run_professional_training.py --backend catboost --device GPU
local\probability_env\Scripts\python.exe run_professional_training.py --device CPU
local\probability_env\Scripts\python.exe run_professional_training.py export
local\probability_env\Scripts\python.exe -m scripts.probability_research train --input <V2运行目录>\data\rows.jsonl --features professional --backend catboost --device GPU --progress --output <新训练目录>
```

已安装的 V1 训练环境可复用，依赖没有增加。首次没有环境时，使用 Python 3.11/3.12 创建 `local/probability_env` 并安装 `requirements-probability.txt`。GPU 请求失败时会记录失败，不暗中改成 CPU；无显卡机器须明确选 `--device CPU`。

## 实际接入的特征

V2 共 **4606个固定字段**。字段包括取值、上下文和未知/不适用状态，不表示4606条独立证据，也不增加历史案例数。

| 组 | 字段数 | 实际计算 |
| --- | ---: | --- |
| 原文历法 | 6 | 年月日时干支、阴阳遁、局数；只取可定位的原盘前文 |
| 问前人物背景 | 4 | 人物关系、性别、直接/代问/闻讯、人/动物；未知保留 |
| 全局 | 9 | 星/门/干伏吟反吟、五不遇、天显时等事实 |
| 宫位环境 | 360 | 实际门星神干、内外盘、旬空、日马/时马、门迫和不同月令方法 |
| 生命周期与隐甲 | 936 | 十干120长生表、双支原位、墓绝、六仪击刑、隐甲支的刑冲合与冲墓支 |
| 固定用户表/传统映射 | 320 | 既有力量表、真假空、制约矩阵、81格吉凶与分开的三系人体对应；单独消融 |
| 来源格局条件 | 1080 | 39组条件AST和81有序天地干组合，逐宫匹配；不是1080条训练样本 |
| 81有向宫间关系 | 1053 | 生克方向、空间、同宫/对宫、干合冲、支冲害合及刑/三合/三会组成关系 |
| 用神绑定与完整落宫环境 | 719 | 各柱、值符星/神、值使、天芮/天心/乙、日时/庚/六合/玄武等；宫关系与符号本体关系分开 |
| 同宫自指排重 | 36 | 真实选中角色与乙/丁/天心/值符的独立同宫条件；别名不变成第二个符号 |
| 四柱之间关系 | 80 | 不同实际柱的刑冲害合、自刑组成；不把同一对象复制一次来制造刑 |
| 明确未定规则 | 3 | 当前来源未定义的支破、合化成立、依目标选择应期等，保持未知 |

具体字段和逐项来源见生成的 `data/feature_catalog.json`，含已知适用、不适用、未知三类覆盖计数；完整规则文件依赖和字节哈希也在其中。CLI 另导出可读 TSV 和每个事件的来源核验结果。JSON 中的“天芮”“人体对应”“固定用户力量”均是传统符号/研究输入，不是观测到的医学诊断标签。

保真和边界：

- 门位/星位行在不同来源中不能统一当作天/地盘。适配器用原文明确阴阳遁与局数核对整列，可读外宫至少6处且全部吻合才采用一种层次约定；两列同值时保留重合情形。对不上就留下未知，不将单个错字替换成现代排盘结果。原字、原库均不改。
- 主宫表有160套九宫位置记录，不能据此说每格OCR都完整、每张原印图和历法均独立验证。151套主盘可完成本适配器的层次核验，其他字段按实际缺失程度保留。
- 中五只有原有地干，天禽随实际天芮、地盘中五寄坤二分别注明来源推导。中心不增加普通门星神。阴干长生和十干藏甲分层，癸落巽的辰养、巳胎不改成辰墓。
- 九星“旺相休囚废”、普通五行“旺相休囚死”、原书门令和八神无自身月令分别处理。双支/力量未定不擅自取最大值。六仪击刑只作为实际天盘仪的事实，地盘不凭同字另加击刑。
- 原书明确问本人、代问、闻讯采用既有人物绑定接口；年命仅在问前明确提供时使用，不从反馈、姓名或模糊公历生年补造。三系身体映射分开，不把它们作为三份独立医学证据。
- 合、刑、三合等组成关系不等于合化成功或完整格局。39组AST只记条件命中，原有未核条件仍是候选；未知从不映射成“没有”。

## 数据与评估隔离

194个原事件、19张原书补盘均已导出特征槽位：1917个节点、17253个有向位置。其中包含原盘缺损的未知槽位，不是213张完整验证盘。补盘仍属于原事件，不自动成为独立训练样本。1080个阴阳/局数/甲子时参数组合另作无标签软件穷举，不进入真实训练集。

本轮找回试验仍是12件物品、11个事件。公文包与包内现金始终同组、各半权重。两个案例最初是盲问或问出行，物品类别在后续才披露；V2将首盘输入类别改为未知，并保留后续披露行号、问题晚于起盘的标志。V1原记录/结果保留，不能把V2与旧V1的分数直接当成同输入消融。

每种算法自动比较同一份V2数据、同一事件划分：

- `prior`：事件加权平滑先验。
- `context`：仅问前物品背景。
- `chart`：相同背景加原九宫符号。
- `professional_facts`：再加来源事实与用神关系。
- `professional`：再加明确隔离的固定用户表/传统对应。

词表和恒定字段筛选只从该折训练集拟合，V2五组中所有需要拟合的模型使用相同的训练集零方差过滤；完整4606字段仍保留在审计导出中。原作者的结论、推理文本、后续反馈和真实结果日期均不进输入。代码从严格白名单的原盘/历法/问前人物数据重新计算特征，拒绝外部直接塞入一份预计算“专业分数”。预测时核对训练时的规则版本；规则在训练期间改变则报错保留该次运行。跨平台版本指纹只统一Git文本LF/CRLF，原字节收据保留，SQLite和原书不归一化、不重写。

先验与两种算法都保留；默认研究模型是预先指定的完整专业版本，不按留出成绩挑赢家或调参。小样本不拟合校准器，用户百分比始终为空，App生产开关仍为false。时间顺序/前瞻外部验证未完成，不以软件穷举或书内反馈证明真实预测有效。

## 输出位置和读取结果

所有本机工作文件默认在Git忽略的 `local/probability_v2/<本次运行编号>/`：

```text
run_status.json                 成功或失败、实际后端和设备
summary.tsv                     两种算法 × 五组比较
task_status.json                 各目标真实完成状态
data/inventory.json              原库、事件数、导出范围
data/feature_catalog.json        全字段及来源/缺失覆盖
data/case_features.jsonl          九宫、81关系、用神图和来源收据
data/flat_features.tsv           194个主记录固定宽表
data/rows.jsonl                  本次12件物品的训练输入/分隔的结果收据
data/case_quality.json           逐案核验、OCR/层次/人物来源
models/logistic/lost-recovery/   逻辑回归模型及逐事件结果
models/catboost/lost-recovery/   CatBoost模型及逐事件结果
```

模型目录含 `evaluation.json`、`heldout_predictions.json`、`ablation_predictions.json`、`feature_importance.json` 和模型。特征重要性只是训练模型的诊断信息，不能当因果、古籍证明或独立预测效度。一次训练失败和旧结果都不会被新运行覆盖。

本轮完成的是专业特征、数据导出、分类训练/推理和本地入口。疾病各部位真实阳性/阴性、统一轻重标准、实际位置/参照时刻、康复/失访/竞争事件日期仍需按目标抽取合格标签。删失/竞争风险拟合器尚未在本轮实现；任务报告会明确写出这一点，不称所有疾病/定位/应期模型已经训练完。V11原Excel schema没有改动，也没有将规则模板输出填作真实标签。

## 实测记录

本地专项与实际模型重载、1080参数遍历的结果、完整回归和新Linux/Windows工作流结果，会在本节及 `docs/audits/probability_professional_v2_20261103/` 据实追加。GPU仍需用户自己的4090执行；CI的Windows验证是CPU运行和启动器兼容，不是PyCharm人工点击或4090验收。

本地实际CPU终版：逻辑回归与CatBoost各五组、相同12物品/11事件，保存重载通过；完整运行约43秒。CatBoost原盘Brier 0.285914，来源专业事实0.252152，含固定用户表0.257795；先验0.275884。Log loss对应0.486435、0.462516、0.479280，先验0.469911。逻辑回归专业版Log loss约0.698，原盘约0.495，没有因加入字段而自动改善。两个最终专业模型仍全部判找回，准确率与先验相同约86.36%，不能据此宣布预测有效；不按测试成绩选择赢家。源规则、压缩全字典及小样本报告位于data/knowledge/probability_research/v2/和data/evaluation/probability_research/v2/。旧阶段完整运行目录仍在local，旧V1公开文件不动。

本地终版完整回归实际953 tests、0失败、0错误、3个既有skip，全部日志与结构化结果在 `docs/audits/probability_professional_v2_20261103/full_run/`。专项36项加镜像1项实际通过；两个后端的专业/纯事实保存重载与标签泄漏不变性、旧V1兼容检查均通过；新4606字段层实际遍历1080个无标签参数组合，新增真实训练事件0。公开TSV只统一LF换行，原始本地运行原样保留。GitHub Linux/Windows与最新main状态待推送后另据实追加。
