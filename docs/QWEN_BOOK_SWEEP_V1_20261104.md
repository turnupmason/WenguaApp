> 当前默认已升级为[连续SFT＋分阶段调参V2](QWEN_BOOK_CONTINUOUS_SWEEP_V2_20261104.md)。用户此前尚未开训；本页9组逐轮重建优化器方案保留复现，勿与新目录混用。

# 纯古籍 Qwen3-14B 参数实验与完整检查点恢复

用户尚未启动上一版自动loop；本入口新增独立参数比较。默认在RTX4080/16GB上用NF4双重量化QLoRA，固定官方 `Qwen/Qwen3-14B` revision `40c069824f4251a91eefaf281ebe4c544efd3e18`。全精度/BF16的14B基础权重本身约28GiB，因此本轮不安排未经实测的全GPU普通LoRA。QLoRA仍能调整LoRA秩、alpha、作用层、dropout和学习率。

## Windows CMD启动

继续使用已经装好torch/transformers/peft/bitsandbytes的 `local\qwen_env`。不用重装Python，不用重复下载已完整缓存的官方权重。先保存任何尚未提交的本地代码；本命令不改用户数据或旧适配器。

```bat
cd /d "%USERPROFILE%\WenguaApp"
git pull --ff-only origin main
run_book_sweep_windows.cmd
```

启动器等价于：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_book_sweep.py run --output local\qwen_book_sweep_v1\run1 --hours 168 --resume
```

每次启动最多168小时，之后在安全步保存并暂停；再次执行同一命令接着完成剩余组合。9组各最多6轮，可能运行多日，不能以之前一轮40分钟推算本次总时间。Windows运行期间请求系统保持唤醒，不能保证断电、主动关机或合盖后继续执行。停止时尽量按一次Ctrl+C并等程序退出；最新未完整保存的一小段步数需重跑。

只查看计划、不开训：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_book_sweep.py plan
```

PyCharm的解释器选仓库 `local\qwen_env\Scripts\python.exe`，脚本 `run_qwen_book_sweep.py`，参数 `run --output local\qwen_book_sweep_v1\run1 --hours 168 --resume`；根入口自动切换到仓库目录。

## 默认9组比较

| 参数 | 值 |
| --- | --- |
| LoRA r | 8、16 |
| alpha | 2×r，即16或32 |
| 学习率 | 0.00002、0.00005 |
| 作用模块 | q/v，或q/k/v/o |
| dropout | 0.05 |
| 额外参考组 | r8、alpha16、q/v、学习率0.00003 |
| 公共条件 | 2048完整上下文、batch1×累积8、相同seed3407、同一套源分组与验证题 |
| 上限 | 每组合6轮；连续2轮验证loss改善不足0.001则早停 |
| 保存 | 每25个优化器步保存；每阶段最多保留3个Trainer检查点 |

8个笛卡尔积组合＋1个原默认参考组。每组先在最长完整样本上做2步显存短测，短测适配器不会作为正式训练初始适配器。CUDA OOM会记录为不适合本机并继续其他组合；本实验**不**给某一组偷偷降低上下文，以免比较失真。来源/配置/损坏文件/普通错误停止并保存错误现场。

同组下一轮继续本组上一轮适配器、重建该轮优化器与学习率计划；**同一轮中断恢复**则恢复该轮原优化器、调度器、随机状态及训练步数。不同组合之间从不传递权重或优化器。恢复的环境版本、源文件和配置须与创建检查点时一致。

## 明确的resume_from_checkpoint路径

通常重复原命令即可，程序自动选择当前阶段最新完整检查点，不需要人工找目录。恢复检查包含适配器、optimizer.pt、scheduler.pt、rng_state.pth、trainer_state.json、适配器配置及逐文件SHA；未封存/损坏的最新目录会忽略，自动退回完整保存点。

手工恢复时，将下面 `trial_XX_...` 替换为本机 `results.csv` / `sweep_status.json` 中的真实组合名，将数字替换为存在的检查点：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_book_sweep.py run --output local\qwen_book_sweep_v1\run1 --hours 168 --resume --resume-from-checkpoint "local\qwen_book_sweep_v1\run1\trials\trial_XX_...\cycle_01\trainer\checkpoint-250"
```

这是真正传给HuggingFace Trainer的 `resume_from_checkpoint`，不只是重新加载LoRA权重。显式路径必须属于当前实验当前组合、未完成的轮次，且是该轮最新完整检查点；外来、旧版本、另一组合、旧保存点、损坏和已完成轮次均拒绝，防止回滚或串训。训练已完成只剩评测时，使用普通 `--resume`，不要强行回滚。

先前的单配置入口仍可用。手动恢复它时，`run_qwen_book_loop.py run --fixed-context --output <实际training目录> --resume --resume-from-checkpoint <该目录内检查点>`；自动4096/2048探测控制目录不是实际training目录。新参数实验与旧单配置目录互不混用。

## 数据与选择

只从固定SHA的双书原库和原出处坐标生成5250核心任务，保留全部194案例目录、1008作者原段和四种教学格式。不读旧人工分数、旧App断词、旧问答池、旧适配器、非古籍补充。原书自己的吉凶措辞仍保留；它们不是旧人工打分。

百万改问是候选池，不等于百万独立知识。每轮对训练核心取一个确定改问版本、对每个assistant回合监督一次；每组使用**相同**改问和顺序。实际完整输入和目标逐条token检查，超长不截断原盘、作者分析或答案，原文另保留并列排除记录。共享准备缓存只生成一次，然后校验并复制到每组，所有数据、mask、验证和测试文件逐字节相同。

每组逐轮选最小的**固定验证集语言loss**，所有可行组合完成后，再按同一验证loss冻结全局候选。只有该候选和原模生成最终测试回答。测试答案不参与选择，已完成实验恢复不重测。不能看了测试结果后在同一次实验改选别组。

语言loss、字符相似度不是“奇门正确率”。源辅助作者复盘也不是未见盘预测；页面保留任务类型与source_mode。是否继续深入，应看条件变更、纠错、不同领域取用和未见案例的实际回答及依据，而不能只看loss下降或组合跑完。反复用同一验证集调参也会过拟合；下一轮针对已确认的验证错误调整，保留新的最终测试，不用模型输出自动回填教材。

## 看什么结果

总览：`local\qwen_book_sweep_v1\run1\results.html`，双击打开。CSV同目录，汇总参数、状态、最佳轮、验证loss、原模loss、训练耗时、显存峰值、适配器、最后优化器检查点。点每个实验进入逐轮原模/微调回答、完整问题、作者参照、出处和所有保存的步日志。最终选中组页面另显示最终测试原模与微调回答。

`selected_trial.json`冻结候选；`sweep_status.json`记录活动实验/进度；每组 `stage_status.json`、`failure.json`、`trainer\checkpoint-N`保存现场。来源正文、训练文件、适配器均在git忽略的local内，Public GitHub只存代码和不含书文的审计元数据。

## 后续调整

配置文件：`configs/qwen14b_book_sweep_v1.json`。启动前可改grid内rank/LR/dropout/作用模块，alpha随rank乘配置比例；shared_overrides只允许公共训练/评测条件。单次最多32组合，禁止外来适配器和旧teacher输入。已开始实验合同不可更改：修改grid、源文件、代码、上下文或轮次后必须使用新目录，例如 `--output local\qwen_book_sweep_v1\run2`，不能对旧run1强行resume。

若全部OOM，总状态为no_feasible_trial，不会虚构优胜者；释放显存后可在选择尚未冻结前用原配置加 `--retry-oom --resume` 再试。已冻结并做过最终测试的实验不能原地换组选；继续研究用新目录，旧结果全部保留。

本地已验证std契约、真实官方tokenizer上的微型随机Qwen3 CPU训练/Adam恢复/两组独立初始化/测试隔离；并核对真实原库准备后的两组数据SHA完全相同。云端没有加载14B权重或执行4080 NF4，真实显存及生成能力以用户本地结果为准。

源码51a48dd9的[远端Qwen验收](https://github.com/turnupmason/WenguaApp/actions/runs/41884207036)与[双Python主CI](https://github.com/turnupmason/WenguaApp/actions/runs/41884207344)均已实际通过；Windows29项及CPU两组合训练产物已取回核验。详见[远端审计](audits/qwen_book_sweep_v1_20261104/remote_source_ci.json)。首次Windows短路径断言失败保留，修正后未跳过任何新增测试。
