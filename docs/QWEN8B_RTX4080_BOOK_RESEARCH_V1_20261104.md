# Qwen3-8B：RTX4080纯古籍连续训练

> 当前默认输出已更新为run3_attention_fix，见[Windows融合注意力修复](QWEN8B_WINDOWS_FUSED_ATTENTION_V1_20261104.md)。下方run2_loss_fix为上一版损失接线修复记录，原样保留，不能继续用于新代码恢复。

> **当前入口已修复损失接线，输出改为run2_loss_fix。** 用户run1的两组4096均约44/100步OOM；完整栈显示进入原生Trainer.compute_loss和整段CE。首次读取Trainer会更换Transformers根LazyModule，原来的根属性替换可能落在旧对象上。此前独立损失/梯度数学核对仍有效，但旧微型loop没有证明实际Trainer使用该函数，现补足该缺口。这两次OOM不能证明正确分块路径下4096必定装不下。

修复直接绑定规范transformers.trainer.Trainer.compute_loss，既有别名与后续导入均生效，worker退出/异常时恢复；不改教材、label、训练参数或原14B文件。实际训练和验证回调逐次检查调用计数及最大投影位置≤128；走错路径即报普通错误停机，不冒充OOM跳过。控制台先显示qwen8b_bounded_loss_installed，实际算过loss后分别显示qwen8b_bounded_loss_verified（validation/train），worker_calls/*.loss_path.json保留实测计数。

更新前在旧窗口按一次Ctrl+C，等待子进程退出；更新后重复同一个CMD入口。默认新目录local/qwen8b_book_v1/run2_loss_fix，不复用旧run1的OOM状态、压力证明或适配器；run1原日志/检查点保留。官方8B下载缓存直接复用，无需重新下载。新目录也必须重新压力测试，正确接通并不保证实际4096一定够显存。

用户已明确转做8B。此前14B八个配置均OOM，两组2048正式训练在约37/1505步的反向传播中申请560MiB失败，最终no_feasible_trial；两步短测不能证明全程稳定。14B目录、权重缓存、日志、检查点与内核原文件全部保留。8B使用独立输出，不加载14B适配器。

## PowerShell启动

复用已经装好CUDA依赖的`local/qwen_env`，不需要另建环境：

```powershell
cd "$env:USERPROFILE\WenguaApp"
git pull --ff-only origin main
.\run_qwen8b_research_windows.cmd
```

首次自动下载官方`Qwen/Qwen3-8B`固定revision `b968826d9c46dd6066d109eabc6255188de91218`，原始权重约16GB，缓存和14B分开。完整下载后训练worker离线读取，PEFT保存阶段不会再联网探测；下载中断后重复入口复用缓存。保持此前对实际Python主程序设置的NVIDIA `Prefer No Sysmem Fallback`。

下载连接重置10054与Hub的LocalEntryNotFoundError表示网络中断且缓存未齐，发生在训练前，不代表显存不足。下载入口现默认单文件并发；元数据超时60秒、文件读取超时120秒（保留用户已有环境覆盖），对连接中断/超时、408/429/5xx最多5次尝试，间隔5/10/20/40秒。每次仍为同一固定revision及标准Hub缓存，已完成文件复用、未完文件由Hub续传，不清缓存/不强制重下；权限、仓库或revision错误不盲重试。5次网络失败明确报告训练尚未开始。持续10054仍须修复到huggingface.co的网络/代理；重试不是连通性保证，未禁用TLS校验。

新报告：`local/qwen8b_book_v1/run2_loss_fix/results.html`。同一命令恢复，不改已经启动的配置、数据或总epoch；旧14B入口不用于新8B。PyCharm脚本`run_qwen8b_research.py`，解释器`local/qwen_env/Scripts/python.exe`，参数`run --output local/qwen8b_book_v1/run2_loss_fix --hours 168 --resume`。每次最多168小时，到时同入口继续。

单独下载或查看计划：

```powershell
.\local\qwen_env\Scripts\python.exe -X utf8 run_qwen8b_research.py download
.\local\qwen_env\Scripts\python.exe -X utf8 run_qwen8b_research.py plan
```

缓存已完整时可给run加`--offline`；首次无缓存不要加。GPU启动筛查是12GiB total/free的保守门槛，不是测得的最低需求，更不是4096保证装下。

## 数据与训练目标

仍只用两书原知识、原书领域流程、194原事件、1008作者段和原盘。固定原库SHA256 `21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405`；不读旧人工评分、非古籍补充、旧QA或旧适配器。5250核心任务的固定来源分组不变，百万改问不作为百万独立知识反复训练。

已用官方8B tokenizer实际重算：2048每epoch4815监督视图，4096为4876；训练case_id161，其余来源留出。整案视图115→172，整案监督token占比9.54%→17.68%。输入/答案超长时保留原文并排除该视图，不截掉条件。各配置共用同一共同验证/最终测试字节，最终测试仍不选模型。原书材料辅助复盘不冒充独立新盘或实际预测验证。

8B专用损失保留完整输入供decoder注意力计算，只对原来labels!=-100的下一词位置投影词表，按128位置分块，并在反向传播时重算这一小块CE，避免保留整段巨大词表张量。标签、因果位移、token归一化和LoRA目标不变；CPU真实微型Qwen3已比较原生/分块loss及全部可训练参数梯度，在记录容差内匹配。训练/验证只需要loss；自然语言生成沿用原模型generate。仅支持该单GPU、冻结lm_head的Qwen3 LoRA路径，不声称适用于任意模型/分布式损失。

allocator在Torch导入前固定`backend:native,max_split_size_mb:128`；不启用Windows兼容性未知的expandable_segments。它是碎片化控制策略，不保证消除OOM。

## 先压力测试，再连续训练

默认4个结构/上下文：4096与2048各测r8注意力四模块、r16全部七模块。每个独立内存结构先做**100次优化器更新**，即累计16时最多1600个训练视图；包含最长输入、最多监督位置和各长度分位混合，四种任务都覆盖。实数据2048压力样本99～2045 tokens，4096为99～4088 tokens，避免只测相同长度的前两步。压力后还有长验证前向与真实生成。

日志`probe:true`与`updates:100`表示压力测试；压力LoRA不作为正式训练起点。每30秒左右打印微批次进度，更新一次参数仍需累积16个微批次。worker心跳/输出10分钟无变化会停止保留诊断，不把停滞伪称CUDA OOM。

相同模型、结构、上下文、数据、seed、loss和依赖环境的显存证明可被LR/dropout/warmup变体复用，`pressure_reuse.json`明确记录；只复用内存证明，不载入压力权重、不用压力loss选模型。换rank、模块或上下文必须重新100步。真正CUDA OOM由既有控制器记录并跳过，全部无可行配置时入口返回非零；其他异常停止保留。

正式组从官方8B新建LoRA，一个worker/Trainer持续最多5epoch，同一Adam和完整cosine调度跨epoch继续；不是每轮重置。累积16，保存间隔25，最多5个完整检查点，按四格式等权验证NLL早停（patience2、min_delta0.001）。2048最多1505更新，4096最多1525；这些是更新步数而非epoch数。

分阶段最多9个不同正式配置：4个结构/上下文，再最多2个新学习率，再最多3个新dropout/warmup。重复配置复用；不是完整网格或全局最优保证。raw回答、来源、loss曲线和人工复核应一起看，NLL不是专业正确率。

## 隔离、恢复与边界

每个压力、整组正式训练、最终测试在独立Python子进程运行，父进程不加载模型权重；等worker退出再下一组。回执按请求SHA与nonce关联，允许Windows venv启动器PID不同。Ctrl+C一次转发给worker并等待，之后原入口恢复；不结束无关进程。

完整优化器/调度器/RNG、早停历史和数据/代码哈希随检查点封存。必要时明确指定当前实验的最新完整点：

```powershell
.\local\qwen_env\Scripts\python.exe -X utf8 run_qwen8b_research.py run --output local/qwen8b_book_v1/run2_loss_fix --hours 168 --resume --resume-from-checkpoint "local/qwen8b_book_v1/run2_loss_fix/trials/实际ID/cycle_01/trainer/checkpoint-25"
```

阶段名仍为cycle_01，但组内包含全部连续epoch。已完成训练而仅生成待继续时用普通--resume。跨模型、参数、数据、source schema或旧14B检查点均拒绝，不把8B适配器直接加载14B。

通过隔离函数命名空间复用既有书源/检查点/分阶段控制源码，各训练合同固定全部依赖文件哈希；旧14B模块对象与源码不改。8B仅在自己的worker生命周期内使用分块损失Trainer。CPU软件夹具有独立标记，不能当作真实8B权重或CUDA实测。

目前云端实测范围：官方8B tokenizer与真实教材预算、微型随机Qwen3的原生/分块梯度、进程控制、optimizer恢复、跨epoch同Adam、恢复/不中断LoRA张量匹配。实际8B NF4/4080/4096能否完整稳定运行、专业解盘是否改善，仍须以用户本机压力测试和后续留出答题为准；100步压力也不是全程稳定性证明。8B效果好不自动证明14B必更好，后续可复用教材/流程/评测另开更大模型实验。
