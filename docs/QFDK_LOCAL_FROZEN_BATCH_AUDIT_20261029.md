# qfdk/qimen 本地冻结 V8 批量工厂阶段一交接与失败门控 · 2026-10-29

## 用户新目标（本轮不得曲解）
Mac 本地先准备 Wengua V8.0 疾病轻重计算规则 + V10.2 中文正式模板、源200格、81格、人物规则，后续使用 [qfdk/qimen](https://github.com/qfdk/qimen) 起盘，一个真实时辰、一个真实人物条件逐条生成中文并存 SQLite/JSON/TXT；每条有完整四柱/真实月令/日干/空亡/天显五不遇/角色，不以物理盘唯一ID代替原日期条件。用户提出 60×12×60×12=518400 理论状态；这不是已被证实的518400个独立合法公历四柱组合。每个合法时柱时干受日干、月柱受年干和节气约束。物理1080键和实例断词不能混称。

## 核对的两仓版本
- 唯一产品源仓：turnupmason/WenguaApp main，在本轮读取时 HEAD `0eae7d2b94742939e885938f8603e85c9452d1c3`；版本冻结 V8.0 计分、V10.2 断词，不做写改。
- 新引擎：qfdk/qimen master HEAD `1d0d1c5b39755e67525a11e68bab9b73baae1937`。README 明示**茅山派转盘**，入口 `lib/qimen.js:calculate(date)`、安装 `npm ci`；并非自动等同《神奇之门》现行排盘。源码保留 MIT LICENSE，package.json 中另标 ISC，发行许可需复核。
- 现有 Wengua 主入口 `src/wengua/health_text_pipeline_vnext_review.py:auto_cast_health_review_text` 与 `src/wengua/health_severity_vnext_review.py:analyze_health_severity_review`；重要数据源 `data/templates/health_severity_vnext/reading_template.json`、`data/mobile/health_vnext/health_energy_200.json`、`data/knowledge/health_81_excel_20261025/81_pairs.tsv` 和人物 profiles。
- 既有 1080 可见布局 1032；Python 1080 索引完整指纹与 Swift 真实生产盘面不能混说成全数通过。该提交前最后专项 GitHub Actions #40905670829 全盘 Swift/Python **FAIL**；同提交主 V8 CI #40905671173 PASS。保留失败不改源算法。

## 本轮 Mac 可下载包（由当前会话交付）
`WenguaLocalBatch_20261029.zip`，ZIP SHA256 `c0fa1ea5a0e56acb0c3b10a2198270422e19b0dadc104daeafe126974616e8bc`。
包内有 `install.command`、`qimen_cast.cjs`、`local_batch.py`、`tests/test_local_batch.py`、`README_使用说明.md`、`RUN_ONE.command` 和 `RUN_BATCH.command`。当前 ZIP 是**离线处理工具的首次安装包**，不是已携带完整 77MB 源仓的 air-gapped 完整数据包；首次安装必须从两公开仓固定 SHA clone，复制原字节冻结四源资源并建立 SHA256 manifest；此后运行不需要联网。下载路径保存在当次聊天交付，不伪造永久 GitHub ZIP URL。

执行逻辑：qfdk 原始盘 `qfdk_original.json` → 严格九宫天干门星神/四柱/局数/节气/旬首/旬空/马等对比 → 无差异时将 qfdk 结构化盘送原 V8 Python 合成，校验与冻结参考路径中文字逐字一致 → `reading.txt` / `frozen_result.json`；不一致只有 `audit.json`，阻止伪造文本。所有逐条状态写 `output/progress.sqlite3`，重复运行跳过已记录事务。真实用户年命未提供不补造；23:00 日界暂拒绝；DST 不存在时刻跳过。

## 本轮真正测试与未验收
- 当前隔离环境真实运行 `python -m unittest discover -s tests -v`：3/3 PASS（中心空白/天芮天禽真实双携干、差异拒绝、时区与晚子拒绝）。
- `node --check qimen_cast.cjs`、`python -m py_compile local_batch.py`、`bash -n install.command`：PASS（语法）。
- ZIP `unzip -t`：PASS。
- 无公网 Git clone、npm 安装、完整 qfdk `calculate` 实盘测试、原 Wengua 全量 Python suite、真实 Swift/Xcode macOS 编译或人审结果；不得冒充完成。此期因执行环境不支持 GitHub 直接拉源码到容器，Mac 首装/完整跨仓样本仍必须执行。
- qfdk 可能与冻结《神奇之门》算法不等：专项 parity fail 不是“断词缺失”，而是流派/源码差异的真实审计信息。未经用户批准不得为求成功静默改 V8、V10.2、200、81、源书、Important 镜像或已知失败。
- 未来推进：在 Mac 用同钟 ≥20 真实时辰、8类含坤寄中五/双星/空马/跨节气/阴阳遁以及父母/祖父母等做两仓九宫 + V8/V10.2 全字对照；对每个失败记位置、预期/实际、来源、回归测试。确认差异后才决定是否采用 qfdk 新规范替换盘源；用户已明确将 qfdk 设为未来起盘来源，但**不能替换后仍使用旧盘断词冒充新盘**。

## 其它规范
这不是新古籍章节，`docs/CHAPTER_LEDGER.md` 没有新增伪章节。冻结模板/200/81/人物及原 Swift 工程没有改动，因此 Important 镜像/MANIFEST 原有 SHA 保持不变；不应人为触碰造成包资源漂移。此文档及 AGENTS/STATUS 追加是本轮主仓交接。传统医学象意不等于实际疾病诊断/预后。
