# Wengua 批量断词预生成与人机文学修订：正式意图澄清（2026-10-29）

## 用户本轮再次明确的唯一目标
不是重新设计奇门排盘，也不是重新调整冻结的 V8.0 疾病轻重判断，更不是为解决本地 Python 报错临时写一套人物用神。
**目的是先用已验收的 Wengua 正式起盘/疾病专题用神/冻结 V8.0 原始规则生成大量可追溯的原始断词，离线存本机，再由用户与 GPT 人工编辑，把僵硬、重复、内部术语过多的中文改成自然流畅有古籍风格的文案，供未来经审核后与 Swift 离线App相匹配。**
先父亲，之后母亲、弟弟和其他已确定人物，保留每个关系及有条件时的患者真实年命、情境和排行；未提供信息不补造。

## 已有代码，不必重复发明
- 当前正式 V8 主 CI、历史 Python/Swift 专项对齐记录仍作冻结基准，当前已有 200格、81格、actor_profiles.json、V10.2完整中文模板、原 iOS WenguaNativeVNextEngine/WenguaPythonVNextVerbatim 等源。
- `scripts/health_editorial_batch_v1.py` 与 `prompts/health_severity_gpt_editorial_v1_20261029.md`、`docs/HEALTH_GPT_EDITORIAL_BATCH_AUDIT_20261029.md` **已存在**，含事实锁/待润色/人工审校/不得改已知吉凶/全部细断章节必须保留的模型。应扩展/集成已有功能，不另建冲突模板。
- 严格审查现有 Mac `Wengua_BigFish_518400.py` 生成链；它通过研究型 `health_severity_vnext_review.analyze_health_severity_review` 运行，研究预览入口与生产正式 V8 Python/Swift 文字不可直接等同。**优先核对实际产出的冻结grade、同宫/用神/九宫事实/中文完整章节与正式引擎是否一致**，而不是仅凭存在文本或评分字段就视作已冻结V8正式结果。任何研究接口与正式入口差异先记录「批量适配器偏差」，不能未经确认说V8模型坏了、改已封存公式、删旧失败或把假盘当真盘。
- 现源人物库 `data/knowledge/phrase_library/health_v20/actor_profiles.json` 实际含22个 profile ID；用户说的20关系为正式已确认用神目标口径，更多 IDs（包含合称、动物等）并不能误称全部20已独立验收。读取现行源并逐类按条件查询，不复制简化名单。

## 批量输出必须分事实与文学两层
每条不可变事实包：`case_id, canonical_cast_id, base_chart_id, four_pillars, source_date_or_abstract_flag, solar_term, yin_yang_ju, true_nine_palaces, relationship_id, consultation_context, actual_patient_role_source, selected_symbol_ids, source_200_81_hashes, rule_version, real_strength_evidence, identical_physical_palace_dedup, exact_V8_score_or_grade, evidence_fact_ids, timing_triggers, original_full_reading, original_sha256, calculation_status/error`。
每条可变文学包：`original_case_sha256, prompt_version, candidate_version, first_screen_summary, full_section_texts, repetition_flags, style_notes, factual_check_status, human_approval, edited_at, editor_notes`。
- 原始判断不因 GPT 改字而漂移；首屏约200字概要 + 第二屏专业逐宫完整断词，不能把所有详细原证据删成200字，也不能重复出词/含内部计算泄露。
- 客户中文可以删模板的机械复述，不删盘面真实冲突或应期依据，不将传统象意变成现实诊断。
- 原始/每次候选/最终审稿三个版本并存，不能覆盖；单案的异议另写 `audit_issue` 而非悄悄改分数。
- 本地 SQLite 仅为断点进度，用户看 CSV/XLSX/JSONL/全文TXT。Excel 含原断词列、润色稿列、人工意见列、审核状态；未审核不能作为正式 App 资源。

## 对已失败20行的正确优先级
原Mac上传 `father_000001-000020.xlsx` 十八行空白根因可能发生在**批量研究预览适配调用**，事实确已查到甲角色定位策略的源限制，但现有产物本身未证明用户正式 Swift V8 医病规则不成立，亦不证明一定要修改封存模型。先比对真实 V8 正式链的同一输入是否有可正确输出的完整断词，发现差异则修**研究/批量接入层**；若正式模型自身也复现，再走原书来源、用户审批、独立审计的既有冻结规则。此前 expectedFailure审计继续保留，不撤销失败证据，也不凭第11行甲戌时疑似取己直接放行。
不要盲跑 518400×全部关系来积累无效文学稿；先20个样本正式链一致性小验收，过关后分段批量。518400是抽象合法标签的笛卡尔总数，不可宣称每条都有真实公历交节事实、可作为已知事件；存在真实时刻则以真实历法为主，抽象节气分支单独标注并隔离审稿。

## 当前本轮实际范围
本轮仅核对上述已有源码、文档与最近 GitHub Actions，并追加这一目的澄清/优先级交接；不对冻结评分、Swift正式入口、200/81、人物原源、Important镜像/MANIFEST或用户旧批量数据库作任何变更。没有实际运行新的Mac批量、Python/Swift parity或Xcode，不得声称通过。最新相关主V8 CI截至本轮查看仍是历史真实PASS（见实际run），不是本文件本身的规则验收。
