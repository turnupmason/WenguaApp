# WenguaApp 章节处理账本（Append-only）

> 每次收到新章并完成处理后，**在表末追加一行**；不得删除已处理章记录，修订原章时增加版本并附原记录引用。总览计数另同步 `docs/PROJECT_STATUS.md`。

## 处理记录

| 日期 | Book ID | 章节标识 | 章节原题 | 原文 SHA256 | 来源状态 | 基础/起盘知识 | 候选规则 | 整体事件案例 | 候选断词 | 测试/审核 | GitHub Commit |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| — | — | — | 尚无已输入新章 | — | 待用户提供 | 0 | 0 | 0 | 0 | 尚未开始 | — |

### 必须记录的状态

- **原文来源状态**：`chat_only` / `local_original_backed_up` / `licensed_public` / `unavailable_for_recheck`，不要声称公开 GitHub 保存了原文。
- **每章的实际产物路径**：在对应行下方追加说明，可列 `data/knowledge/<book>/<chapter>` 的可公开结构化摘要、候选规则、案例索引、测试文件以及原文仅本地的相对路径（不含用户隐私路径）。
- **校对状态**：`extracted_draft` / `source_checked` / `needs_case_or_chart_review` / `approved`；不同类别可分开记录。
- **案例数量**：独立完整事件家族数（同案多题不得重算）。
- **断词数量**：候选与获批数量分开，不能以 GPT 生成数量代表已验收。
- **变更**：重审同章时增加同一 chapter 的新版本行，不编辑旧原文和旧事实结论。
