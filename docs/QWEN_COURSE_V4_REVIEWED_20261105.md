# 纯两书短答课程 V4

当前入口为 `run_qwen_course_v4_windows.cmd`。旧 bookv3 默认入口继续暂停，旧检查点仅供复现。新教材建立新适配器，禁止把旧适配器或旧优化器接进来。

本轮阅读批注覆盖 1,451 项基础知识材料、194 个案例、1,008 条登记作者分析，并回读有关原文续段、教师点评和短表。私有包保留全部原文、逐项批注、使用覆盖表和 Excel。不是每段都进入正向监督：重复容器、编者附注、识别疑字、未核推测和原书明确承认的错误分别保留、排除或变成纠错题，不把“原书说过”自动等同“结论正确”。

最终 3,129 个核心任务：知识短答 961、条件追问及纠错 413、字面读盘与明确规则运用 1,561、原书案例复盘 194。其中含 10 条实际多轮对话；训练使用每次助手回复的前缀视图。不是百万条重复改问。全部答案最长 189 字；简单题直接答，案例先结果，再原因和证据，避免复述同一结论。

原书两种旺衰、不同书名下的格名、主客天地盘方向、病神与医药身份、天禽寄宫和所带干、十二长生各支状态分别处理。三刑异说与作者后改的出生年、错误起盘、学生初断、作者纠正均明确区分。无旧人工分数或评分教师。

事件、跨书同案、补盘、共享原盘、同一封来信及相应反馈按组隔离。696 组，训练 2,571、验证 296、测试 262。原书案例属于回顾性教学；有作者原分析辅助的题标明 source review，字面查宫题单独标记。复盘 NLL 和字面读盘不能宣称独立预测能力、现实正确率或医学概率；最终仍需看模型实答。已看过的旧 20 道模型题不充当全新盲测。

## 下载与启动

聊天中的工作区文件路径不是有效附件，现已改成加密数据随 Git 同步，无需从聊天下载 ZIP。公开仓库只有 AES256-CBC＋HMAC-SHA256 密文，实际解密码仅在私有对话交付，不进入 Git。此方式不依赖 GitHub 附件上传权限。

在 **PowerShell** 当前 WenguaApp 目录运行（把“本对话中的解密码”替换为收到的64位十六进制码）：

```powershell
git pull --ff-only origin main
.\local\qwen_env\Scripts\python.exe -X utf8 unlock_qwen_course_v4.py --key "本对话中的解密码"
.\run_qwen_course_v4_windows.cmd
```

解密入口使用 Windows 内置 .NET AES，无需安装新包；先认证 HMAC，解密后核对原 ZIP SHA256 `e704510f43c20fc87ca636e39107450313215ea1add0f25a60ffd58de0bf21c8`，再自动保存到 `Downloads/Wengua_course_v4_reviewed_20261105.zip`，不用解压。旧有不同文件会保留并报告错误；不会覆盖。密文分发与解密器不在原训练合同文件列表中，原教材、配置、所有训练源码逐字未改。

ZIP 内含完整 Excel，可以在自动保存后从 Downloads 解压查看。明文不提交到 Git。

仍使用现有 `local\qwen_env` 和官方 8B 缓存。需要手动指定 ZIP 时：

```bat
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_course_v4.py install --archive "C:\完整路径\Wengua_course_v4_reviewed_20261105.zip"
run_qwen_course_v4_windows.cmd
```

新输出 `local/qwen_course_v4/run1/results.html`。最多六种不同正式参数：4096 上下文、r8/r16 四个注意力投影；先 100 更新的实际长度压力测试，通过后正式训练；再比较学习率与 dropout/预热。每组最多三轮，同一优化器持续。保存频率 25 更新，完整轮末也保存；中断后重复同一 CMD，恢复完整优化器、调度器、随机状态和 Trainer 状态。显式路径仅允许该实验最近完整检查点：

```bat
run_qwen_course_v4_windows.cmd --resume-from-checkpoint "C:\Users\wtmas\WenguaApp\local\qwen_course_v4\run1\trials\实际组名\cycle_01\trainer\checkpoint-实际步数"
```

新训练停用逐微批 FLOP 参数遍历统计，另在开始、每 25 更新及结束核查真实参数名称、身份、形状和可训练性，遇异常保留诊断并停止。每组仍用独立进程、原来实测通过的分块损失和融合注意力，并保留 stderr、退出码及心跳。并未据此宣布之前 Windows 原生访问违规已定位或一定消失。

## 本轮验证范围

发布 ZIP 安装、逐文件摘要、全部回答与 Excel 读回已检查。官方 8B tokenizer 下，训练 2,579 个助手前缀视图全部完整装入 4096，无截断；这是实际教材长度覆盖，不是最大 4096 长度任意批次的 GPU 容量承诺。

新入口做真实微型 Qwen3 CPU 训练与跨进程优化器恢复，检查多轮助手掩码、40 更新、重复恢复不重训、参数图及遥测恢复。该检查不加载 8B 权重，也不验证本机 CUDA 容量或断案水平。软件全套与远端源码一致 CI 证据另见 `docs/audits/qwen_course_v4_20261105/`。

公开仓库仅含编译代码、运行代码、测试、摘要和说明。私有 ZIP 含原书材料和训练问答，不上传公共 CI。

源码 `908d8ecf5556a08205bf956e50d9f20da23e1164` 的主CI `42051657768` 双Python、Qwen CI `42051657846` 三job均success。已逐job读取完整日志并核对checkout源码、无error标记及cleanup完成。Windows真实venv/实际HF参数图、Trainer loss及注意力路径通过；Linux新入口40更新和优化器恢复通过。证据 `docs/audits/qwen_course_v4_20261105/remote_source_ci.json`。这些是软件验收，不是本机GPU或预测正确率验收。
