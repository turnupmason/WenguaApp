# 首次回答的乱码、字段类型和检索修正

## 已定位的三个问题

用户第一次chat已加载完8个权重分片并生成249 tokens，未到768上限，返回可解析JSON，但被字段类型校验拒绝。终端粘贴副本中的σ/τ/Φ等字符可通过CP437→UTF-8无损反向还原；还原后发送提示的SHA256与trace记录的`3f0fd2d30147413b491603add404ba1b9254336c19ea60cba955e6d0dd8d2ad9`完全一致。这是显示代码页错解的证据，不能据此说训练文件已损坏。只在代理私有分析副本还原，不改用户原文件、语料或权重。

先前让用户直接`type` UTF-8文件时，没有同时设置CMD代码页，查看方式不完整。Windows查看先执行`chcp 65001`，优先用Python按UTF-8读取。根Python入口也明确使用UTF-8输出，避免重定向文件再次按旧代码页编码；这不永久修改Windows注册表或系统区域。

还原后的实际格式问题是`missing_information`为字符串，接口要求数组。其余基础字段类型正常。校验不把字符串偷偷转换成列表；报错会明确显示`missing_information expected array, got string`。新的chat遇拒绝会打印标记为rejected的原始回答和诊断，保留完整私有trace，以退出码2结束，而非只给泛化堆栈。旧失败记录保持原样。

内容也不合格：模型复制了“转动天盘、确定九星落宫”的排盘步骤，没有回答天芮/天心的作用。原检索仅允许无登记案例章节的基础段落，未放行疾病章通则，导致该题选错来源。修正的重点不是降低校验标准或把语言loss当能力。

## 检索修正的来源边界

新增`data/knowledge/qwen_research/v1/safe_general_rule_scopes.json`，只允许《神奇之门》疾病章原文第9行、第11行的health_yongshen通则（分别139和50字符）。两段均在登记案例开始前，章节SHA、具体行范围、原字段内容SHA必须全部匹配。一般疾病/医生用神问题优先这些作用说明，排盘问题不加此优先级；明确工作/婚姻/考试等其他领域也不加疾病优先级。相同书章同一段落按内容排重，避免重复段落占满检索槽位。

第64/67/105行等病例/披露阶段角色不放行，没有把整章或所有历史推理加入新问事。来源仍为draft，不自动升格approved。此适配器仅在检索时作用于已有corpus，训练SFT、分组、旧manifest、模型配置和已训练权重不变，无需重新prepare或重训。

资料学习不再强制附上“缺新盘”的缺失条目；新事件解读仍保留缺盘约束。输入额外明确数组类型和按问题解释的要求。这里只增强指令，不能保证模型必然遵守；新回答仍要逐条复核。

## 先读旧回答，不占GPU

更新代码后，在CMD中执行：

```bat
cd /d "%USERPROFILE%\WenguaApp" && git pull --ff-only origin main
chcp 65001
local\qwen_env\Scripts\python.exe -X utf8 run_qwen_research.py review --trace local\qwen14b_v1\run1\full\inference\20261104T041245995264Z_adapter.json
```

review只读取原UTF-8文件，输出原始/解析回答、具体类型问题与按所存提示复查的结果；不加载模型、不联网、不重写旧trace。旧回答的recheck_passed仍为false，这是保留失败证据，并不是修复没生效。

仅为查看原文、尚未更新时也可：

```bat
chcp 65001
local\qwen_env\Scripts\python.exe -X utf8 -c "import json; p=r'local\qwen14b_v1\run1\full\inference\20261104T041245995264Z_adapter.json'; print(json.load(open(p,encoding='utf-8'))['raw_output'])"
```

## 再用新检索提问

按`docs/QWEN14B_FIRST_ANSWER_REVIEW_20261103.md`重新运行同一题的adapter与base-only。两者都要使用这次更新后的提示，比较`prompt_sha256`，不能拿旧错源提示下的adapter回答与新提示下的base回答混作对照。仍使用旧full/adapter，不再训练。

chat默认只使用本机已缓存的固定基座、适配器tokenizer与权重，避免为了可选custom_generate文件发HEAD查询；确实缺缓存且希望下载时才加`--allow-model-download`。该开关只控制基座文件获取，不上传私有提示。加载器使用固定版本支持的`dtype`参数，去除torch_dtype弃用提示。读取旧trace不受任何网络状态影响。

此修复没有在代理侧执行用户14B的真实GPU生成。CPU测试只能验证检索来源、类型校验、UTF-8只读复查、预算和缓存加载接口；实际内容是否改善仍待用户新trace。旧训练报告、974项完整回归及失败原始副本继续保留，不以修显示来宣称模型已经答对。
