# Qwen3-8B：Windows融合注意力兼容修复

> 用户第一组完整5epoch已完成，第二组曾无回执退出。现原CMD在不更改冻结训练文件/合同的前提下增加诊断包装，仍续同一run3；见[无回执诊断与恢复](QWEN8B_NATIVE_EXIT_DIAGNOSTICS_20261105.md)。不要为此新建run4或重跑已完成组。

当前默认入口仍为run_qwen8b_research_windows.cmd，输出改为local/qwen8b_book_v1/run3_attention_fix。run1、run2_loss_fix原日志/检查点保留；不沿用它们的压力/OOM结论或适配器。已下载的官方8B缓存复用，不重装环境、不重新下载基模。

旧运行窗口按一次Ctrl+C，等子进程退出后，在PowerShell执行：

```powershell
cd "$env:USERPROFILE\WenguaApp"
git pull --ff-only origin main
.\run_qwen8b_research_windows.cmd
```

## 证据与尚未确认的部分

用户实际PyTorch为2.8.0+cu128；flash_compiled=False，flash_enabled/efficient_enabled/math_enabled均True。开关True不代表内核已编译或真正选中。修复损失接线后，GPU验证/训练均已打印bounded_loss_verified，但r8/4096仍在44次更新后反向传播申请1.78GiB失败。

同教材压力数据、Trainer/Accelerate版本及seed3407在CPU重放：更新44之后的第712个微批次长3866 tokens；32头FP32完整注意力矩阵为1.782GiB。此结果依赖相同缓存/采样设置，未取得用户失败批次的直接shape日志，不能将CPU重放写成GPU运行追踪。

Transformers4.57.1的sdpa_attention在Torch>=2.5且无mask时开启enable_gqa；Torch2.8文档说明CUDA GQA只支持Flash与math内核。因此无Flash编译时存在绕过Efficient、落入math大矩阵的明确风险；旧运行没有直接内核追踪，不能仅凭开关声称已经观察到具体旧算子。参考[PyTorch SDPA](https://docs.pytorch.org/docs/2.8/generated/torch.nn.functional.scaled_dot_product_attention.html)、[HF固定版本实现](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/integrations/sdpa_attention.py)。

## 新执行路径

保留HF原有mask、因果位置、scale、dropout与缓存处理，显式按组重复K/V头，以同样的分组注意力语义调用SDPA；没有截断上下文、窗口近似或改变label。每个GPU worker加载8B前，用随机小张量实际测试Flash（编译可用时）、Efficient、CuDNN，选择首个通过的融合内核：32 query头/8 KV头/head_dim128，64、3866、4096长度及单token缓存查询均做前向与反向，检查梯度有限，并记录真实autograd算子名与探测峰值显存。

实际SDPA调用只允许所选单一融合内核，禁止math回退。没有内核通过则在加载8B前明确停止并保存报告，不将环境不兼容伪称某一配置OOM。若真实模型本身仍OOM，保留原异常并继续既有配置筛选。融合内核通过不保证完整模型一定装下。

首个worker固定attention_backend.json，后续worker必须保持相同后端/设备/dtype。压力证明包含此合同哈希，不能把一种后端的显存证明用于另一种后端。首次合同建立后再按实际合同封存证明。

控制台核对：

- qwen8b_fused_attention_probe_passed：小型GPU前后向探测已通过，显示实际所选后端。
- qwen8b_attention_verified：实际模型的训练/验证确实调用新路径。
- qwen8b_bounded_loss_verified：上一版修复的128位置分块损失仍实际调用。

worker_calls/*.attention_probe.json记录GPU探测算子/形状；*.attention_path.json记录实际调用次数与最近/最大Q/K长度，异常也保留最后输入形状；*.loss_path.json记录损失调用。Torch全局math开关在作用域退出后恢复，不能拿另一个进程的全局开关代替这些运行收据。

单独检查GPU注意力而不加载模型：

```powershell
.\local\qwen_env\Scripts\python.exe -X utf8 run_qwen8b_research.py attention-doctor
```

此命令也会实际使用GPU，建议在旧训练退出后执行。无需额外安装Flash Attention或从源码编译Torch；是否有可用融合内核由本机测试决定。PyCharm脚本run_qwen8b_research.py，解释器local/qwen_env/Scripts/python.exe，参数run --output local/qwen8b_book_v1/run3_attention_fix --hours 168 --resume。

## 验证边界

CPU核对原生GQA与显式KV重复的输出及Q/K/V梯度，覆盖完整因果、单token缓存、显式掩码；真实微型Qwen3训练及缓存生成调用已检查，生成token一致，绕过/错误math策略被拒绝，异常后全局绑定恢复。CPU软件夹具允许CPU数学内核，并明确不认证CUDA。

既有分块loss数学等价、实际worker调用、100步压力流程、连续Adam与跨进程优化器恢复保留。课程仍仅两书/194事件/1008作者段/5250核心任务，参数搜索仍最多9组，原14B源文件不变。含书源文本的数据仅在local私有目录，公开证据只有程序、计数、哈希和软件日志。真实8B/NF4/4080融合内核和完整训练容量须以用户新run3日志为准，不以CPU测试宣称已跑通GPU或具备真实预测能力。
