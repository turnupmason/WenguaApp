# 8B第二组无回执退出：保留run3继续并采集诊断

用户日志中第一组完成1525更新/5epoch，train_runtime14065.5181秒、train_loss1.1770542628330285；后续验证/生成完成，03:21:04 worker以exit_code0退出。随后r16_4096_3987e4a0e627正式训练到第3步，启动器返回而没有result.json。原错误没有打印退出码，也没有Python训练异常栈；不能据此称CUDA OOM、驱动故障或已定位某原生库错误。

用户随后回传Windows事件：2026-11-05 03:22:02 Event1000，python.exe发生0xC0000005访问违规，故障模块unknown、offset0，PID0xA730（42800）。随后03:22:16两条Event1001/BEX64共享相同Report ID，与Event1000是同一故障报告，不计三次崩溃。事件时间与第二组退出吻合；尚未直接核对旧heartbeat的真实PID，也未分析minidump。已确认该时间段Python原生访问违规，具体组件仍未知，StackHash/BEX64不能定位某DLL或证明具体漏洞/硬件损坏。

本次仅增加独立诊断包装。原8B训练/损失/注意力/调参/数据/配置及它们的代码哈希逐项不变，不迁移或重写旧合同，不换GPU内核，不改参数，不自动重试崩溃，也不把未知退出标成OOM。原CMD入口转到run_qwen8b_diagnostic.py，再调用原CLI；仍为local/qwen8b_book_v1/run3_attention_fix和--resume。

```powershell
cd "$env:USERPROFILE\WenguaApp"
git pull --ff-only origin main
.\run_qwen8b_research_windows.cmd
```

如果旧运行已经结束，可直接更新并执行；仍在运行的实验不要同时再启动一份。完整压力证明和第一组已完成状态由原控制器读取，已完成组仅核对适配器后跳过。第二组使用已有最新完整检查点恢复；只有第3步且每25步保存时，可能还没有完整检查点，此时仅第二组重来，不重做第一组。保留全部原目录，不删除/手工改状态、不拿压力权重代替正式权重。

新包装仅对run_qwen8b_worker.py进程增加PYTHONFAULTHANDLER=1、PYTHONUNBUFFERED=1，stderr实时显示并同步写文件。正常nonce/SHA回执验证、GPU锁、poll/wait/超时、Ctrl+C与原调度均保留；非worker子进程不改变。异常继续按原流程停止，等待用户检查，不掩盖失败。

每次实际worker对应：

- worker_calls/请求ID.native_stderr.log：tqdm、Python栈和可捕获的原生崩溃信息；外部强制结束可能没有栈。
- worker_calls/请求ID.exit_diagnostic.json：原始退出码及32位十六进制、Windows状态提示、启动器PID、心跳中真实worker PID/阶段/step、请求字节校验、回执是否存在、stderr是否读完、诊断包装源码SHA。
- 控制台[qwen8b_exit_diagnostic]：即使原回执缺失也先打印上述退出信息，再保留原错误。

Windows venv的启动器PID与实际Python PID可能不同，不能强行按同PID解释故障；若退出码0却无回执且stderr尚未读完，也需核对真实worker是否仍在运行。0xC0000005等状态提示只描述Windows状态，不自动认定具体GPU库或硬件原因。

可另开PowerShell读过去12小时Python的Windows错误记录（没有输出不代表排除原生问题）：

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000,1001; StartTime=(Get-Date).AddHours(-12)} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'python.exe' } | Select-Object -First 3 TimeCreated,Id,Message | Format-List
```

此诊断无法补回此前未记录的退出码。它为再次出现问题提供证据，不等于已经修复或确认用户原生崩溃根因。第一组训练/验证NLL是书源语言任务指标，不是专业解盘正确率或临床预测验证。

验证：真实子进程硬退出且无回执/实时stderr、正常退出和重复wait、非worker管道、超时/终止、Windows退出状态解码；原微型Qwen3数学、实际attention/loss调用、检查点恢复与不中断权重一致、完成后无新worker的断言均在诊断包装下保留。真实GPU native问题仍需本机退出码/栈或Windows事件记录。
