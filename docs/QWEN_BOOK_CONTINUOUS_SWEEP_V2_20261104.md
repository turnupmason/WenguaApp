# 纯古籍连续SFT与分阶段参数实验V2

用户已在4080启动：两步探测训练完成，随后生成遇到Float/BFloat16输出层冲突。修复版为独立生成补上CUDA autocast，与训练精度一致；CPU路径保持原精度。旧run1完整保留，因代码哈希合同变更，当前入口 `run_book_research_v2_windows.cmd` 使用新目录 `local/qwen_book_sweep_v2/run2_dtype_fix`，从官方基模重做探测。权重缓存继续复用，无需重装环境。此前V1逐教学轮重建优化器，保留复现；本版为**每个组合一个Trainer连续训练多个epoch**，同一个Adam和一条完整余弦学习率计划跨epoch继续。

## Windows CMD启动

使用已经装好CUDA依赖的 `local\qwen_env`，无需重装Python/torch。完整官方权重缓存存在时离线读取，缺文件才下载固定revision。

```bat
cd /d "%USERPROFILE%\WenguaApp"
git pull --ff-only origin main
run_book_research_v2_windows.cmd
```

等价CLI：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_book_sweep_v2.py run --output local\qwen_book_sweep_v2\run2_dtype_fix --hours 168 --resume
```

中断或到时后重复同一命令自动恢复。每次最多168小时，全部试验可能需要多日；关闭电脑时不会继续执行。普通中止优先一次Ctrl+C，最新未完整保存的一小段更新需重跑。Windows进程运行时请求系统保持唤醒。

只看计划，不开训：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_book_sweep_v2.py plan
```

PyCharm：解释器选 `local\qwen_env\Scripts\python.exe`，脚本 `run_qwen_book_sweep_v2.py`，参数 `run --output local\qwen_book_sweep_v2\run2_dtype_fix --hours 168 --resume`。根入口自动切到仓库。

## 训练条件与阶段

官方 `Qwen/Qwen3-14B` 固定revision `40c069824f4251a91eefaf281ebe4c544efd3e18`，NF4双重量化QLoRA；4080支持时用BF16计算，基础权重保持4bit，不是把14B全部BF16权重放进16GB。batch1×累积16；默认最多5个完整数据epoch，早停patience2、改善阈值0.001；初始LR3e-5、dropout0.05、warmup0.08、cosine。每25优化器步保存，最多保留5个Trainer检查点，epoch边界另保存并封存；每个完整epoch的适配器和验证结果保留。

| 阶段 | 默认候选 | 怎样选择 |
| --- | --- | --- |
| 覆盖与显存 | 下列4种结构×2048/4096，共8组 | 全部先做最长完整训练样本2步短测、验证前向和实际生成；仅CUDA OOM标不适合，其他错误停止 |
| 结构与上下文 | r8 q/v；r16 q/k/v/o；r16七模块；r32七模块；各2种上下文 | 可行组独立从官方基模正式训练；共同验证题的格式等权语言loss选候选 |
| 学习率 | 对上阶段结构比较2e-5、3e-5、5e-5 | 与已有组合完全相同则复用，不继续接训，不重复运行 |
| dropout/warmup | 对所选结构和LR比较dropout0.01/0.05×warmup0.03/0.08 | 共4个候选，其中已有组合复用 |
| 最终测试 | 冻结最后候选后，仅该模型与原模 | 测试答案不参与任何阶段决策 |

七模块指q_proj/k_proj/v_proj/o_proj/gate_proj/up_proj/down_proj。alpha固定2×r，r32即alpha64。这使用户提出的r32、七模块、4096进入结构候选；低dropout进入后续调参，不认为0.01会强迫模型遵守公式。默认最多13个不同正式训练配置，所有配置独立新建适配器、优化器和scheduler，短测适配器不用于正式训练。

这是预先声明的分阶段坐标搜索，不是所有参数的全组合穷举，不能保证全局最佳或覆盖全部参数相互作用。每次阶段选择写入decisions，恢复时须一致；同一验证集反复调参仍可能过拟合，下一轮不能看过测试答案后原地改选模型。

## 数据、完整案例与公平比较

固定双书原库SHA `21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405`，5250有出处核心任务；全部194案例目录、1008作者段、43章节原文保留。只用原书知识/领域流程/作者教学，不读人工计分、旧App断词、旧问答池、外部补充或旧适配器；不把模型回答回填成教材。

本版每个epoch遍历同一份、按每个assistant回合展开的核心训练视图，Trainer按固定seed打乱。百万改问候选池保留供审阅，没有在每个epoch重复训练百万同义问法。训练/验证/测试按原来源与事件分组隔离；194案不是全部拿去训练，保留案例不能被训练题改问泄漏。

实际完整token核对：

| 上下文 | 每epoch训练视图 | 整案视图 | 整案监督token占比 | 累积16时每epoch更新 | 5epoch最大更新 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2048 | 4815 | 115 | 约9.54% | 301 | 1505 |
| 4096 | 4876 | 172 | 约17.68% | 305 | 1525 |

两个长度均覆盖161个训练case_id、890来源分组；超长视图列排除记录、原文保留，不截断原盘/条件/答案。上表不是194个独立新事件被扩成4815个独立事件。每组全训练集遍历一次才叫一个epoch，不能按192/16=12步当一轮。

相同上下文的参数组共享同字节训练、mask和评测文件；不同上下文的训练覆盖允许不同，**共同验证loss、共同生成题和最后测试文件仍逐字节相同**，使用2048能完整容纳的来源留出题。每个epoch分别计算基础问答、条件对话、盘面应用、完整案例的语言NLL，按实际存在的格式等权平均选本组最佳epoch；默认真实数据有四种格式。这不是专业正确率，更不是旧人工奇门计分。

4096另外选最多4条只来自验证分组的较长整案/条件题，允许最多1536新token，记录完整提示和答案预算。原模与本组共同验证选中的适配器都回答，单独标extended_validation，**不参与跨长度或阶段排名**。短测也试该长生成预算；没有完整容纳的题则明确0条，不截答案。来源辅助作者复盘不是新盘盲测。

## 完整恢复与断电边界

每个组合内部连续训练，不在每个epoch重建Adam或重启cosine。`resume_from_checkpoint`恢复LoRA权重、optimizer、scheduler、Trainer步数、CPU/GPU随机状态和数据跳过进度；额外封存每epoch验证历史与早停状态。逐文件SHA、模型revision、依赖版本、源数据、配置和代码合同必须吻合。

程序自动选择最新完整封存检查点；损坏/半写目录会忽略，退回完整保存点。若已有训练进度却找不到完整状态，会停止并保留现场，不能悄悄新建优化器重来。

手动指定（将组合名和数字替换为本机真实目录）：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_book_sweep_v2.py run --output local\qwen_book_sweep_v2\run2_dtype_fix --hours 168 --resume --resume-from-checkpoint "local\qwen_book_sweep_v2\run2_dtype_fix\trials\r32_4096_实际哈希\cycle_01\trainer\checkpoint-250"
```

不同参数组、旧训练入口、非最新完整点和外来检查点拒绝。训练已完成只剩生成时用普通 `--resume`；已冻结最终选择不能回滚后换组。OOM组保留，释放显存后在新输出目录重试，不在已经比较完的实验里偷偷改变上下文。

实现专门处理：中途半个epoch暂停不误算完整epoch；完整epoch最后一步保存后、验证前断电会先恢复该轮验证，再继续下一epoch；最后更新已保存但状态尚未写完时只收尾，不能再多训练一步。验证缓存是否存在不改变新训练初始随机流，恢复训练再由Trainer加载原检查点随机状态。

## 查看结果和下一轮

双击 `local\qwen_book_sweep_v2\run2_dtype_fix\results.html`。总览含结构、上下文、LR/dropout/warmup、状态、训练视图和各格式监督token占比、最佳epoch、各格式loss、实际更新、显存、路径与阶段决策。点每组进入逐epoch/原模/长案例的原始回答、完整提问、作者参照和出处。各组有 `loss.svg`、全部 `training_steps.csv`；train loss与格式等权验证NLL并非同一统计口径，曲线只辅助看趋势。

`answer_review.json`按任务记录空答、输出到上限，以及原抄盘星位题中的宫位集合是否与参照相同；该机械诊断不理解否定语义，不能称专业准确率，也不参与选择。条件追问、用神关系、同宫不同符号、矛盾证据、领域切换和应期有无依据，继续看原始回答核对。

配置：`configs/qwen14b_book_sweep_v2.json`。开训前可调整限定的阶段候选和公共训练条件；改已开始实验的参数、代码、上下文、数据或总epoch须使用新目录，例如run2。保持旧run1、旧日志与适配器。最终候选仍须看专业回答，不能仅按最低loss宣称已经训练到位。

云端只做真实官方tokenizer、微型随机Qwen3 CPU训练、来源文件核对与控制流程验收；没有在云端加载14B权重或运行4080 NF4。真实显存、吞吐和回答能力以用户本地运行结果为准。

源码adcb2459的[远端Qwen验收](https://github.com/turnupmason/WenguaApp/actions/runs/41898463745)与[双Python主CI](https://github.com/turnupmason/WenguaApp/actions/runs/41898463885)已实际完成并通过；Windows43项、新连续训练CPU及长验证分支产物已下载核验。[远端审计](audits/qwen_book_sweep_v2_20261104/remote_source_ci.json)记录来源SHA、job、ZIP哈希和真实验收字段。初次失败日志保留。
