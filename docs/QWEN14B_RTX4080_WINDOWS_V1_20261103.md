# Qwen3-14B：RTX4080／Windows本地首版

用户本机doctor实报：Windows、Python3.12.10、RTX4080、总显存15.99GiB、空闲14.72GiB、CUDA可用；torch2.8.0+cu128及其余固定依赖均已安装。该记录取代此前将用户当前机器称为4090的假设。用户已明确选择“先做14B本地版本，之后再升级32B”。

## 当前默认和复用范围

根入口仍为`run_qwen_research.py`，不再重装现有环境。默认配置改为`configs/qwen14b_v1.json`：官方[Qwen/Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B)，revision `40c069824f4251a91eefaf281ebe4c544efd3e18`，Apache-2.0；实际读取官方API/config确认。NF4双重量化、q/v LoRA-r8、batch1、累积8、1536 tokens、冻结大矩阵半精度、梯度检查点。目标是先验证本机训练能运行，不承诺已经在4080上测过。

原`configs/qwen32b_v1.json`逐字保留，使用时显式`--config configs/qwen32b_v1.json`。旧PyCharm4090训练配置也固定指定32B，避免名称与实际基座错位；新增三个4080/14B配置。以后可继续使用相同源材料，但14B适配器不能直接加载到32B；升级需要用相同数据另训32B适配器。

语料格式仍使用既有`wengua_qwen32b_v1`历史schema名，表示同一版源学习数据协议，不表示当前模型规模。源库194案/43章、793条教学记录与按事件/段落分组完全复用，没有新增事件、伪造问前监督或重新切分来挑成绩。当前训练仍以作者书内复盘/基础资料阅读为主，不代表已经学会对新事件作可靠预测。

## 按顺序在Windows CMD执行

先更新代码并检查当前14B配置。安装已经成功，无需再次pip安装：

```bat
cd /d "%USERPROFILE%\WenguaApp" && git pull --ff-only origin main
local\qwen_env\Scripts\python.exe run_qwen_research.py doctor
```

新的`training_route`应显示`Qwen/Qwen3-14B`；`training_preflight.status`在所报14.72GiB空闲状态下应为`ready_for_smoke_test`。它只是启动筛查，`actual_training_fit_verified`仍为false；不能据此宣称训练通过。对14B采用12GiB总量/空闲保守筛查，对32B采用20GiB筛查；不是实验测得的精确最低显存。实际选中的CUDA卡不满足时，会在读取数据、建立运行目录及下载模型权重前拒绝。它不自动换模型，也不声称所有其他卸载框架均不可用。

准备资料（不下载模型权重）：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py prepare --output local\qwen14b_v1\run1\data
```

检查1536长度能保留哪些完整案例，只获取tokenizer：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py audit-tokens --data local\qwen14b_v1\run1\data --output local\qwen14b_v1\run1\token_audit_1536.json
```

先执行两步真实GPU试跑：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py train --data local\qwen14b_v1\run1\data --output local\qwen14b_v1\run1\smoke --max-steps 2
```

这一步才首次下载原始基座（约30GB）并在加载时量化，建议磁盘至少预留60GB用于缓存、环境和输出。基座默认缓存在`%USERPROFILE%\.cache\huggingface`（可被HF_HOME覆盖），需检查缓存所在盘的可用空间；自己的训练适配器保存在项目`local/`。首次下载可能耗时较长。不要把下载进度当训练进度；`run_status.json`显示`complete`、实际走完两个优化步骤且没有OOM后，才算该短跑完成。其结果会记录分配/保留显存峰值，不是问卦准确率。

确认短跑完成后，用新目录正式训练，配置与短跑一致：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py train --data local\qwen14b_v1\run1\data --output local\qwen14b_v1\run1\full
```

1536长度会排除部分长案，原始整案仍保留，不自动截断教师答案。要扩大到2048，需先以新输出目录加`--max-seq-length 2048 --max-steps 2`重新验证显存，再在正式训练中使用同样长度；只通过1536短跑不能宣称2048可用。不覆盖原运行目录或删除失败记录。

实际14B tokenizer覆盖检查：1536训练可用587条（479基础+108整案），排除52条；验证71/排除7，测试72/排除4。2048可增加训练完整案到142，但需重新实测显存。最初1024仅保留20个训练整案，因此没有把1024设为最终默认。全部793条教学记录仍完整保留，训练时排除记录逐一列出。若1536仍OOM，可在新运行目录加`--max-seq-length 1024`诊断，但不能把这项结果冒充所有案例都已训练。

PyCharm解释器使用`local\qwen_env\Scripts\python.exe`，依次运行`Qwen 4080 Prepare`、`Qwen 4080 Smoke`、`Qwen 4080 Train`；三项共用`local/qwen14b_v1/pycharm_run1/`，与上述CMD的run1分开。直接GPU适配器提问仍使用`chat --adapter-run ...`，从运行记录读取基座，保留模型一致性。

## 验收边界

本机用户已验证的是CUDA可用和依赖版本；新代码的纯函数显存筛查测试使用明确标注的硬件夹具，不能写成实际操作了用户4080。微型随机Qwen3 CPU训练只验证tokenizer/遮罩/LoRA/保存重载接口。真实14B权重下载、NF4训练显存与生成回答质量均待用户本机短跑和后续留出评测。病位/严重性/日期/百分比不是因为切换到14B就获得医学或统计有效性。

原量化V2、封存疾病App、原始数据库、原Excel与全部旧32B运行/收据保留；新增原书章0/历史事件0。
