# WenguaApp 两书独立 RAG

本入口把已提供的《神奇之门》《开悟之门》原文、条件与案例来源做成独立检索库。原起盘程序、其他排盘变体、iOS 代码、旧研究结果和正在运行的 V5.1 教材/参数/恢复合同全部保留。本次不清理这些文件，也不向当前训练注入新资料。

## 来源与覆盖

来源为固定 SHA256 的双书194案例原库，结合已有逐字来源坐标、材料处置和案例角色复核。43章原文共577,780字字符、194个独立案例、1,008条原索引分析全部保留。原文非空行无遗漏，每个引用回查书目、章节版本、行号、字符范围及哈希。

独立索引5,320项：2,049项条件规则包、2,910项案例来源、361项参考材料。共同前提与例外保留在同一证据包；原表、标题和上下文仍可按章查看。检索正文来自原书，不收录微调答案、旧人工算分、吉凶等级教师或模型生成解释。检索提示词只帮助定位，不能当原书引文。

1,451项已有知识材料逐项关联：1,375项关联规则包；37项属于历史叙述、39项没有独立教学目标，均保留为来源参考。它们不是丢失的书稿。规则包数量也不是独立规则定理数。

知识问答和新盘分析只检索规则；历史学习使用 `study`，明确保留学生初断、作者按语、更正、后知反馈及原书抄盘，不将反馈当成当时已知信息。疾病A/B对照段关联两个原事件，保留各自案例身份；不合成一个事件、不修改原库。留出评测可以排除案例、事件家族和课程组；该路径不把已读案例冒充未见评测。

完整原文、索引审阅 Excel/HTML、回归问题及再构建定位材料用原有教材口令加密交付，公开 Git 只放代码、密文、来源哈希与验收摘要。口令不进入 Git、日志或 CI。

## Windows：训练期间可先用 CPU 检索

在 PowerShell 执行：

```powershell
Set-Location "$env:USERPROFILE\WenguaApp"
git pull --ff-only origin main
.\local\qwen_env\Scripts\python.exe -X utf8 unlock_wengua_rag.py
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py build
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py search --question "天芮和天心在疾病预测中的作用有什么区别？"
```

解密入口接受此前 V4/V5.1 的64位教材口令，输入可见。不要在聊天、GitHub或截图中公开口令。ZIP自动恢复到 Downloads；`build` 核对包及所有文件哈希后安装并生成索引，不加载 GPU。首次构建会激活索引，重复构建同一路径会拒绝覆盖；已有索引直接 `search` 即可。

本地文件：

- `local/wengua_rag/sources_v1/Wengua_两书RAG索引审阅.xlsx`：全部索引、194案、1,008分析、1,451材料处置、原文逐行。
- 同目录 `Wengua_两书RAG索引审阅.html`：浏览器本地搜索，不联网。
- `local/wengua_rag/index_v1.sqlite3`：不可变的 CPU FTS5 中文检索库，附完整性回执。
- `local/wengua_rag/active_index.json`：当前索引指针，切换时保留旧指针历史。

查看完整原章或案例：

```powershell
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py chapter --id shenqi/5 --output local/wengua_rag/chapter5.json
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py case --id kaiwu.health.19950219.brother_paralysis --output local/wengua_rag/case_review.json
```

解密后的来源目录可以复制到 Mac，使用相同 Python 检索代码；解密入口本身使用 Windows 内置 .NET。

## 训练完成后接模型

`ask` 只接受来源合同核对通过、正式阶段已经完成封存的 Qwen3-8B V4/V5/V5.1 适配器，不读取压力测试权重。默认读取 `local/course_v51/run1/phase_status.json` 中已完成的正式适配器。当前训练仍在运行时继续使用 `search` 或 `prompt`，不要另开第二套 GPU 模型。

```powershell
.\local\qwen_env\Scripts\python.exe -m pip install -r requirements-wengua-rag.txt
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py ask --question "天芮和天心在疾病预测中的作用有什么区别？"
```

新增依赖仅为 Windows 时区数据库 `tzdata`，不升级正在使用的 Torch/PEFT/Transformers。模型仍用现有离线缓存及融合注意力检查。加 `--base-only` 可以在同一份证据/提示下比较官方基模和适配器。每次回答保存完整原答、模型来源、来源引用、程序盘、实际预算及检查结果，输出使用直接中文，不要求旧 JSON 答案模板。

## 起盘仍由 WenguaApp 代码完成

独立适配器调用现有 `astro_calendar.solar_chart_clock → casting_shenqi.bureau_for_term → casting_shenqi.layout_from_explicit_bureau`，读取九宫、四柱、节气和局数。未改这三个函数，也未替换仓库内其他排盘算法；本入口明确登记当前转盘/拆补方法，其他流派不会自动混用。

时间必须包含正确 UTC 偏移和明确的原 App 时区；沿用现有程序的23点边界等校验，不由模型猜测。普通输出显示当地日期；时区留在可复核的技术回执中。

示例为明确指定北京时间的演示盘，不是原书历史盘的复原：

```powershell
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py ask --mode reading --time "2026-11-05T10:00:00+08:00" --zone Asia/Shanghai --question "本人问健康，请按原书方法分析，条件不足的应期不要补造。"
```

也可先 `cast --time ... --zone ... --output local/wengua_rag/chart.json`，再 `ask --mode reading --chart local/wengua_rag/chart.json ...`。回执会由原代码重算核对，修改后的盘面不能直接冒用。原书手抄盘和程序新盘分别保存。

## 后续八本逐章增加

目前实际收到并建索引的是两本；其余八本尚未收到，不预填书名或声称已处理。每章先保存原始上传、独立书目、章节、流派/方法、来源版本和哈希。`stage-chapter` 只归档为草稿；`reviewed-chapter` 需要明确完成的来源核对及原文选择范围，共用条件作为一组保留。原文全量保存，未归为通则的内容仍为参考，不能自动批准生成解释。

```powershell
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py stage-chapter --input local/new_book/chapter1.txt --book-id book03 --book-title "收到后的真实书名" --chapter-id 1 --title "原章标题" --method-id "核实后的方法标识" --revision 1 --output local/new_book/chapter1_draft.json
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py reviewed-chapter --draft local/new_book/chapter1_draft.json --review local/new_book/chapter1_review.json --output local/new_book/chapter1_library.json
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py build --library local/wengua_rag/sources_v1/sources.json.gz --library local/new_book/chapter1_library.json --output local/wengua_rag/index_v2.sqlite3 --activate
```

再次扩充时同时传入所有已核对增量库；有冲突的章节版本不能静默覆盖。资料更正需新版本和明确核对，旧库与旧索引保留。新资料更新 RAG 后即可用于检索，模型继续按版本集中微调，不需要每章重新训练。

## 验收的实际范围

完整原文及引用哈希、194案/1,008分析定位、非空行覆盖均已核对。46项有针对性的来源检索回归全部通过；官方 Qwen3-8B tokenizer 核对52份完整提示，最多3,327输入 token，加768输出不超过4,096，未截断问题、程序盘或共同条件。Excel保存后读回119,002个单元格一致。

另有46项软件测试、真实微型 Qwen+PEFT CPU 推理和 Windows FTS/内置.NET解密检查。本地全套1,202项测试0失败0错误、保留3项既有跳过。完整测试和远程同源码 CI 结果保存在 `docs/audits/wengua_book_rag_v1_20261105/`。微型测试只证明接口接线；当前没有本机8B/CUDA实答效果证明。

引用存在与机械盘位检查通过，仍不代表语义推理全部正确。专业效果需对完成的 V5.1 逐题实答核对，和基模在相同来源下比较；检索46/46不是事件预测准确率。不要把有出处、低loss或模板流畅当成现实验证。

本轮最终软件源码 `3e73107a` 的远端六项工作均成功（Python3.11/3.12、Windows来源与程序盘、真实微型Qwen+PEFT CPU、两项原生回归）。完整日志已存入上述审计目录。原文另做逐字符引用覆盖复查，43章无未覆盖非空白字。
