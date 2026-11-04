# 14B首版完整训练后的回答检查

## 已经观察到的结果

用户回传完整run_status：Qwen3-14B、1536长度、两轮结束、state=complete，训练1794.7307秒，平均训练loss0.9354345；71条验证的eval_loss0.2643812，验证35.518秒。587条训练包含479条基础阅读、108个整案复盘；验证包含59条基础阅读、12个整案。52条超长训练记录仍排除且保留原文。

这是用户本机终端证据，见`docs/audits/qwen14b_rtx4080_v1_20261103/user_reported_full_training.json`；未读取用户适配器文件，也不是代理云端GPU复现。环境内fit_verified=false是训练前快照，不能据此否定后面的state=complete/epoch=2。真实完成的是领域LoRA训练，不是所有模型参数全量更新。

验证loss低于训练期平均loss不证明泛化良好或没有过拟合：两者分别是最终模型验证值和全过程训练平均，任务构成也不同；多数是带资料的基础阅读。尚无相同设置的原模型对照，也未完成独立事件预测验证。继续增加轮数前应先看实际回答。

用户报告峰值allocated13.161GiB、reserved24.490GiB，而显卡总量15.99GiB。这里只保留原始数值；Windows驱动/共享内存/记账的具体原因没有独立诊断，不将reserved当成24GB物理显存或可用余量，不据此扩大上下文。

## 当前提问入口修正

原入口会将4段参考全部放入提示，某些基础问题已超过2048上下文，尚未加载GPU就会报错。现在使用实际官方tokenizer计算预算，优先按检索顺序选择能放入的完整参考；过长参考跳过，不截断问题、系统要求或程序盘面。只有真正传入的引用ID能通过回答检查。没有任何参考能放入时明确记录no_references，不伪造资料。

原模型和LoRA使用相同数据、提示构建方式、采样参数与seed=3407；`--base-only`只关闭适配器。它是逐题交互对照入口，不是已完成全测试集评测，也不保证不同硬件逐位确定性。接口只检查JSON、模式、引用成员与概率空值，是否真正支持结论仍须对照来源。

每次chat的原始回答、实际发送的完整提示、引用ID、预算、模型类型和解析结果，自动保存到`full/inference/`下的唯一时间戳JSON。原始资料/问题可能包含私有内容，这些文件只保存在git忽略的local中。无效JSON或引用会保存原文后拒绝，不自动改写成貌似正确的答案；报错时把相应trace文件交给后续审查。成功解析也不等于语义或预测有效。

## Windows CMD：先做一个相同问题的交互对照

不重训、不重装依赖；更新入口，已训练的full/adapter继续保留：

```bat
cd /d "%USERPROFILE%\WenguaApp" && git pull --ff-only origin main
```

先看自己的适配器：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py chat --data local\qwen14b_v1\run1\data --adapter-run local\qwen14b_v1\run1\full --mode source_study --max-new-tokens 768 --question "古籍中天芮星与天心星的作用有什么区别？"
```

再用相同问题/资料测原始Qwen：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py chat --data local\qwen14b_v1\run1\data --adapter-run local\qwen14b_v1\run1\full --mode source_study --max-new-tokens 768 --base-only --question "古籍中天芮星与天心星的作用有什么区别？"
```

两次分别加载、退出，复用已有基座缓存。768是回答上限，程序从2048总量中为它保留预算，不是扩大训练上下文；按当前资料与tokenizer，这题可保留一段完整来源，输入约909 tokens，总预算1677，长度检查已实际执行，不等于已在代理侧运行14B生成。

检查：是否回答了问题、来源是否支持、有没有擅自补盘/出生信息、相反条件是否保留、JSON是否完整、引用是否真实。先区分格式/引用失败和专业推理错误，不能拿一条基础题就宣布模型比原版强。真正的留出评测应按事件隔离、排除同案资料，验证集用于选择版本，测试集不反复用于调参；目前尚未完成该生成评测程序及分任务人工审校。

旧训练代码、模型配置、数据划分、原始库与封存App不变。续训和中途checkpoint仍未实现，本次没有偷偷增加训练轮数或覆盖模型。
