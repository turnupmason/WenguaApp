> **当前默认已改为14B：** 用户实测RTX4080/16GB，并选择先做14B本地版本。请从[4080 Windows指南](QWEN14B_RTX4080_WINDOWS_V1_20261103.md)继续。本页保留32B路线；以下训练/doctor/长度检查均显式指定旧32B配置，不会自动换模型。

# 问卦 Qwen32B：本地知识库与领域适配器 V1

用户在2026-11-03明确选择：在Qwen 32B基础上加入自己的古籍和案例，建立自己的问卦模型。该授权新增独立LLM研究路线，取代此前“本项目不开发27B路线”对本轮新工作的限制；没有复用旧QimenLLM训练集，也没有删除现有CatBoost对照。

## 首版结构和真实状态

确定性排盘程序提供宫位；带来源的本地检索提供资料；Qwen3-32B负责理解问题、学习作者分析和组织回答；4位NF4 QLoRA只保存小型领域适配器。不是从零训练328亿参数，也不是把全文塞进提示词后就称为已训练的自有模型。

基座：官方 [Qwen/Qwen3-32B](https://huggingface.co/Qwen/Qwen3-32B)，固定revision `9216db5781bf21249d130ec9da846c4624c16137`。2026-11-03实际读取官方API、config与模型卡：32.8B，Apache-2.0，支持非思考模式。配置见 `configs/qwen32b_v1.json`。基座许可不自动授予任何书稿发行权。

当前交付代码：私有语料准备、固定分组、中文双字检索、程序排盘提示、结构/引用成员检查、CUDA QLoRA训练、适配器直接推理、兼容OpenAI接口的RAG提问、PyCharm入口和环境/长度检查。32B权重没有在云端下载，4090的实际NF4训练和领域回答质量仍待用户本机验证。CPU微型随机Qwen3测试只能证明训练接口、标签遮罩和适配器保存重载能工作。

现阶段新问题只检索**无登记案例章节中的白名单基础知识**。全43章原文与领域/案例资料保留在私有语料中，`reference`可显式阅读；默认问事检索不会把章节里混杂的历史结局带进来。疾病、工作、婚姻、失物等完整条件规则与问前多轮监督仍需按来源阶段审计，不能称“所有专业断案已经学会”。

## 数据与训练目的

只读源库：`archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3`，SHA256 `21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405`。源库不迁移、不修改。43章、194事件、1008条作者分析，原图缺损与分层疑点继续保留。

首轮实际导出793条SFT记录：602条去重基础资料问答、191条整案作者分析重建。另3案没有专门分析行，仍保留在194案登记及检索库，不编造教师答案。拆分639训练/78验证/76测试；事件登记161/18/15。3513条检索文档中842条可用于新问事。793条不等于793个独立事件，1008条分析也不是1008个事件。

`source_study`明确训练“作者在书里怎样说”，答案可以包含作者断语和后来反馈；它们不是已验证的事前监督。`cases.known_before`本身存在后续披露混入，因此训练中明确标为书内摘要，不标成严格问前事实。没有把“作者判对”当现实成功标签。规则段落按内容去重和固定分组；案例按事件整体分组，真实补盘仍属于原事件。测试、验证案例及原始整章不进入默认检索；评估应继续排除被测事件的全部材料。

SFT只计算assistant答案的loss，system/user被遮罩；使用官方Qwen3聊天模板并关闭thinking，不训练虚构的内部思考。原作者可见分析作为来源证据保存。超长整案保留在数据文件，但不静默截断进训练；`token_audit.json`明确列出未能训练的记录。2048长度并不保证覆盖所有长案例。

## RTX4090安装与运行

先根据当前终端选择下面的命令。提示符为`C:\Users\...>`是Windows CMD；它不能直接执行`cd ~/WenguaApp`、`python3.12`或`local/qwen_env/bin/python`。这些分别要改为Windows项目路径、`py -3.12`和`local\qwen_env\Scripts\python.exe`。此前只有Linux命令的说明不适用于CMD。

### Windows CMD：先检查环境

使用之前已克隆的项目，执行：

```bat
cd /d "%USERPROFILE%\WenguaApp" && git pull --ff-only origin main && dir requirements-qwen.txt
py -3.12 --version
nvidia-smi
```

如果项目目录不存在，先执行`git clone https://github.com/turnupmason/WenguaApp.git "%USERPROFILE%\WenguaApp"`，再重新执行上面第一行。不要在用户主目录直接`git pull`。如果项目有未提交修改/无法快进，保留修改，先查看具体错误，不使用reset强行覆盖。

如果`py -3.12`提示未安装或找不到命令，先安装Python，完成后重新打开CMD，再运行上述检查：

```bat
winget install -e --id Python.Python.3.12 --source winget
```

指定`--source winget`避开此前msstore源的证书错误。每行是独立命令，不要把`py`和`winget`拼成同一条。

确认Python显示3.12、项目目录正确后，执行下面这一整段。CMD续行符`^`必须保留在行末；`&&`确保前一步失败时不继续安装。仅创建独立环境和检查，不下载32B权重、不启动训练：

```bat
py -3.12 -m venv local\qwen_env && ^
local\qwen_env\Scripts\python.exe -m pip install --upgrade pip && ^
local\qwen_env\Scripts\python.exe -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128 && ^
local\qwen_env\Scripts\python.exe -m pip install -r requirements-qwen.txt && ^
local\qwen_env\Scripts\python.exe run_qwen_research.py doctor --config configs/qwen32b_v1.json
```

原生Windows的CUDA/bitsandbytes组合需要在用户机器核验；当前Qwen微型训练CI是Linux CPU，不代表Windows32B训练已测过。以doctor实际输出的依赖版本、`cuda_available`、显卡名称和`total_gib/free_gib`为准，不凭“4090”型号假定可用显存。不需要仅为了修正路径就先重装系统或安装WSL。若原生依赖/CUDA仍不兼容，再根据实际报错使用下方Linux/WSL2路线。

doctor正常后，Windows CMD的数据准备、长度检查和两步训练命令为：

```bat
local\qwen_env\Scripts\python.exe run_qwen_research.py prepare --output local\qwen32b_v1\run1\data
local\qwen_env\Scripts\python.exe run_qwen_research.py audit-tokens --config configs/qwen32b_v1.json --data local\qwen32b_v1\run1\data --output local\qwen32b_v1\run1\token_audit_before_training.json
local\qwen_env\Scripts\python.exe run_qwen_research.py train --config configs/qwen32b_v1.json --data local\qwen32b_v1\run1\data --output local\qwen32b_v1\run1\smoke --max-steps 2
```

逐条执行并检查结果，已有输出目录会拒绝覆盖。最后一条才会首次获取大模型权重并尝试GPU训练；前两条不证明显存足够。Windows PyCharm解释器为项目下`local\qwen_env\Scripts\python.exe`。

### Linux／WSL2：Bash命令

推荐GPU训练在4090电脑的Linux或WSL2中运行；先确认该环境执行`nvidia-smi`能看见GPU。Mac可以执行数据准备、检索，或连接已运行的模型接口。此CUDA训练入口不支持Mac/MPS；不用把CatBoost环境改成LLM环境。

在项目根目录执行（已有项目先pull，不覆盖本地修改）：

```bash
cd ~/WenguaApp
git pull --ff-only origin main
python3.12 -m venv local/qwen_env
local/qwen_env/bin/python -m pip install --upgrade pip
local/qwen_env/bin/python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
local/qwen_env/bin/python -m pip install -r requirements-qwen.txt
local/qwen_env/bin/python run_qwen_research.py doctor --config configs/qwen32b_v1.json
```

PyTorch CUDA12.8轮子需要兼容的NVIDIA驱动；以doctor的`cuda_available=true`与本机显存报告为准。不能靠“pip安装成功”认定CUDA可用。首次获取原始BF16基座文件需约66GB下载和相应磁盘空间，运行时才量化为NF4；建议给环境、缓存、适配器留100GB以上可用磁盘，训练前自行查看剩余空间。4位权重仍有量化元数据、激活、优化器与缓存开销，24GB显存能否容纳该配置必须实际试跑。

准备材料不用GPU或torch，仅需Python3.11/3.12：

```bash
python3.12 run_qwen_research.py prepare --output local/qwen32b_v1/run1/data
```

检查长度只下载tokenizer，不下载32B权重：

```bash
local/qwen_env/bin/python run_qwen_research.py audit-tokens --config configs/qwen32b_v1.json \
  --data local/qwen32b_v1/run1/data \
  --output local/qwen32b_v1/run1/token_audit_before_training.json
```

先做**两步真实显存验证**，不是直接长时间训练。默认2048 tokens、batch1、梯度累积8、q/v投影LoRA-r8、梯度检查点、NF4双重量化。冻结基座准备只将一维归一化参数保留FP32，保留大词嵌入/输出矩阵的BF16/FP16，避免PEFT默认整批上转FP32造成额外数GB开销。CUDA混合精度仍由Trainer管理，运行结束记录实际显存峰值。它是保守候选配置，不是已实测的4090显存承诺：

```bash
local/qwen_env/bin/python run_qwen_research.py train --config configs/qwen32b_v1.json \
  --data local/qwen32b_v1/run1/data \
  --output local/qwen32b_v1/run1/smoke \
  --max-steps 2
```

确实完成且显存稳定后，使用新目录正式训练：

```bash
local/qwen_env/bin/python run_qwen_research.py train --config configs/qwen32b_v1.json \
  --data local/qwen32b_v1/run1/data \
  --output local/qwen32b_v1/run1/full
```

若OOM，先释放其他GPU进程；可用新输出目录加`--max-seq-length 1024`验证较短上下文，但会排除更多长案例，必须读token_audit，不能再称全部案例训练完毕。不做32B全参数微调。更长上下文/更多LoRA模块应在有实际显存余量时再测。4090若始终不足，需要更省显存的训练实现或更大显存机器；不自动改成别的参数规模、不偷偷CPU卸载后声称4090成功。

PyCharm：项目选择此独立环境，运行根入口 `run_qwen_research.py`。共享配置`Qwen Prepare`、`Qwen 4090 Smoke`、`Qwen 4090 Train`共用`local/qwen32b_v1/pycharm_run1/`，依序准备→两步短跑→正式训练；已有输出会拒绝覆盖，重跑请更改三个配置的目录。工作目录为项目根目录。WSL GPU训练使用PyCharm的WSL解释器。

## 检索、排盘与提问

不用模型即可检查检索和实际传入提示：

```bash
python3.12 run_qwen_research.py retrieve --data local/qwen32b_v1/run1/data --question '天芮星与天心星是什么'
python3.12 run_qwen_research.py prompt --data local/qwen32b_v1/run1/data --question '失物应当怎样取用神'
```

可选`--chart local/本次盘参数.json`内容为`{"dun":"yin","ju":8,"hour_ganzhi":"己巳"}`。由现有程序生成盘，模型不能改宫位。当前入口只接显式局数和时柱，不新增自动历法判断；没有提供年月日与人物信息时，不得假造四柱/年命/旺衰。自然语言取用步骤仍需模型评测，此入口不等于已经自动接通全部4606字段。

正式适配器训练完成后，在4090本机直接提问：

```bash
local/qwen_env/bin/python run_qwen_research.py chat \
  --data local/qwen32b_v1/run1/data \
  --adapter-run local/qwen32b_v1/run1/full \
  --question '天芮星与天心星在传统疾病分析中如何区分'
```

此命令加载固定原基座和自己的LoRA；推理总上下文预算4096，超预算明确拒绝，不自动截断盘面。若模型生成了非JSON、无效引用或概率，入口会拒绝并报错；这可能说明微调/格式还未学好，需要继续评估。

如果用户已经用Ollama运行官方`qwen3:32b`，也可从Mac执行：

```bash
python3.12 run_qwen_research.py ask \
  --data local/qwen32b_v1/run1/data \
  --base-url http://127.0.0.1:11434/v1 \
  --model qwen3:32b --question '天芮星是什么'
```

这是“基础Qwen加检索”，不是已经加载自己的适配器。本程序不自动下载Ollama模型、不自动导出/合并GGUF、不自动开放4090网络服务。若已有可信模型服务，base-url和model可改为其真实地址与名称；不要将含书稿/私人问题的请求发送到不可信服务。

## 如何判断是否有用

先按完全相同的留出事件比较：基础Qwen、基础Qwen+检索、LoRA、LoRA+检索。核查人物与物品取用、宫位事实、条件和反证、引文支持、来源矛盾、未知条件披露、应期是否有依据及是否编造结局。现有源重建测试与微型训练测试不等于已经做过这些32B回答评测。

保存的验证语言loss仅衡量对书内文本的拟合，不是问卦准确率。案例含出版选择偏差与回顾性整理，训练集中的死亡或病愈叙述不能变成新患者的医学预后。接口`event_probability=null`；以后如需百分比，必须基于明确定义的真实结果、随访和独立留出数据校准。保留量化对照的目的正在于此。

当前所有长原文、SFT、RAG语料和模型权重位于被git忽略的`local/`。公开仓库只增加代码、配置、文档、统计和无原文验收收据。v11 Excel、封存疾病引擎/手机页面、原始数据库均未修改。新增原书章0，新增真实历史事件0。
