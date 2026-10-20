# 多书籍、多版本、多轨制结构化溯源协议（WenguaApp）

本协议永久约束《神奇之门》《开悟之门》及后续所有古籍。2026-10-20 用户确认：《开悟之门》是《神奇之门》的后续补充，新增材料不得覆盖历史原文、原 V1、旧书结论、作者证据和审核状态。

## 同一概念，多个来源轨道
- 全局 concept_id 是搜索概念标识，不是唯一权威断法；book_id + section_key + source_sha256 + source_line_span + excerpt_sha256 是不可替代的独立来源证据。
- 结构化去重仅合并检索键与语义上严格等价的显示结果；无论新旧书意见一致或重复，都必须在独立 source occurrence 中完整留存原文、作者条件和版本。
- 明确 source track_id：书名、章版本、流派/起盘变体、适用领域、人物关系、数理系统与信息时序。可标记 reaffirms / clarifies / extends / supplements / separate_context / potential_conflict，均只是草稿候选，未人工复核不能认定等价或矛盾。
- 《开悟之门》第一篇地支固定宫位与24节气平均每宫三节气是两种不同映射轨道，严禁混作一份映射；九宫所含多个数须结合用神、旺衰、门星神和实际情境选取，不能硬编码唯一值。

## 多版本不覆盖
- 每次从远端已真实归档、经 SHA256 验证的完整 SQLite 使用 sqlite3.backup() 无损增量，原书全文和全部旧表旧行完全保留，不得从元数据/索引重建整库或覆盖先前二进制快照。
- 相同 SHA 的重复原稿只记录别名；有变化则建新 section.content_version，旧 SHA、原文字节、来源版本、跨书引用和案例阶段全保留。
- 每个版本保存独立 SQLite 和 XZ 及 manifest：基库 SHA256、原书 SHA256、输出/压缩文件 SHA256、准确计数、全旧表行检验、integrity_check、foreign_key_check 和当前 HEAD Python3.11/3.12 CI。
- 用户允许按此前历史方案上传公开完整 SQLite；始终提示书籍原文可能有版权与二次分发风险，新增第三方作品的授权不可由旧授权推定。

## 交叉溯源和审核
- 已有 semantic_assertions 保存来源条目；新增跨书轨道在 cross_book_concept_tracks 独立追加来源、track、归一化值、适用条件与审核状态，不改早期条目。查询可联结多书，但 App 不得自动用新书替换 V1 文案。
- 新书引用《神奇之门》旧案例，只登记 cross_book_example_references 的当前行、旧书页码、版本和未核对标志；只有比对相同事件后才能指到同一 event_family，不能凭再引用新增案例、盘或独立事前成功。
- 新旧观点冲突必须同时保留、准确注明不同条件和出处，标为 unresolved，禁止偷偷裁决、删改失败案例、把作者后验修正放到事前输入。
- 原文文字和图/格表原貌保存；只有真正印出的问事九宫才计入实盘，太极、先后天八卦、河图、节气和宫位示意图不得冒充新盘。
- 数据四层：A作者原话、B经来源校验的原书可核事实、C模型候选、D经人工批准可发布。所有自动整理的新轨默认 draft / positive_training_eligible=0，来源忠实与现实科学有效性严格分离。
- 数量/日期/历法仅按书中实际陈述保存；书中节气的公历近似日期不是对任一年精确交节时刻的证明，未经专业数据核对不能用于精确自动起局。

## 逐章固定工作流
先读根 AGENTS.md、PROJECT_STATUS、CHAPTER_LEDGER、CHAPTER_WORKFLOW、本协议以及最新远端 DB manifest → 读全原文和 SHA 比对 → 先归类理论/专题方法，逐案保留作者真实分步推理和反馈 → 按已存在 concept_id 查重并追加独立轨道 → 增量 SQLite 和回归/旧行保护 → 生成版本化公共索引和完整原文归档 → 同步 AGENTS/STATUS/LEDGER → 推送 GitHub，检验真实远端二进制 SHA 与最新提交的 Python3.11/3.12 CI。UI 与旧 QimenLLM 冻结。所有未来新增书必须保留 V1 的既有来源、版本、验证和可调用能力。
