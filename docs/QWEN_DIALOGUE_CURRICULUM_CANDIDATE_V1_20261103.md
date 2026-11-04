# Wengua ancient-source dialogue curriculum · candidate V1 · 2026-11-03

## Deliverable and reproducibility

A candidate, **not yet a released SFT gold dataset**, was generated from source-indexed records in WenguaApp at commit `cfb742db2fa98f6b3e72929dba0ab2405f6a16d5`. A locally delivered spreadsheet contains **11,952 unique question-and-answer training-style rows**, including **1,015 multi-turn conversations**.

| Group | Candidate dialogue rows |
| --- | ---: |
| 基础知识问答 | 4,428 |
| 领域用神及条件追问 | 5,196 |
| 独立九宫五行关系 | 1,536 |
| 原书历史案例**索引**教学（不是作者逐句分析） | 792 |
| **Total** | **11,952** |

There are **406 source-group IDs**, not 11,952 independently evidenced rules, and **65 unique historical event family keys** referenced across the sampled case indexes, not 65 newly validated full author cases. Source-group split: 316 train / 38 validation / 52 test, with common source IDs grouped rather than random row splits. Case variants must remain family-bound on any later full-source export.

Local deliverables transmitted to user (not published as original book content):

- Workbook: `Wengua_古籍指令问答与多轮对话_11952条_20261103.xlsx`, SHA256 `e9c6c964b0784caf31504ab2d4176b93aeb5a8f44d754c45e1bdefd78f5988a1`.
- Candidate JSONL: `Wengua_古籍指令对话_11952条_候选.jsonl`, SHA256 `82e924f908b9c0eef592b7488f57f8509fe3ad19351cbb557b3ff325fc42b59f`.
- Generator script snapshot: `build_wengua_curriculum.py`, SHA256 `05920c7592b6d28d9c27088e6f17b40db76b819da9125ce27ef29e93525a0535`.

Provenance metadata is separately recorded in `data/knowledge/qwen_curriculum_v2/candidate_11952_manifest.json` and its exact `Important/python/` mirror, with Git blob receipt in `Important/MANIFEST.json`.

## Source and safety boundaries

Verified public, source-referenced inputs include `data/knowledge/shenqi/shijia_symbols_ch04/symbol_index.json`, `.../shijia_judgments_ch05/concept_index.json`, `.../application_overview_ch06/method_index.json`, `.../health_prediction_ch01/method_index.json`, `.../marriage_prediction_ch02/method_index.json`, 81 ordered ten-stem names and multiple public case indexes. The original 194-case private SQLite was **not reopened in the current generator environment**. Prior separate V1 Qwen data export documented 793 tasks (602 de-duplicated foundation + 191 authored case reconstructions), not a verified count of rows in this new workbook. Do not merge those figures.

Status counts: **11,076** `candidate_requires_human_review`, **84** `needs_source_detail_and_human_review`, **792** `NOT_TRAIN_AS_AUTHOR_REASONING_until_full_source_checked`. The case-index section teaches only question/scope/method-topic identification; it **does not** reproduce verified original author palace-by-palace reasoning, timing judgments, or later outcomes. No generated case-index row is licensed as author-verbatim, sealed gold SFT, or a blind-test case. The generated JSONL explicitly marks all rows `training_eligible:false`. All samples need source-aware semantic and duplicate-family review before any training release.

Father health example is conditional: correctly resolve querent/subject, then historical subject year stem plus auxiliary 乾 palace; use a **real supplied** natal stem only when birth evidence exists. Do not fabricate natal year, double count one real marker or conflate subject stem with palace base score. Friend uses fixed month stem, no age/sex-dependent sibling mapping. A conditional source rule must not become unconditional diagnosis or real-world prognosis. Keep traditional medical symbolism separate from clinical diagnosis.

Existing V9 severity and V11 text, V27 body-site and Swift native app remain frozen. Existing `data/knowledge/qwen_curriculum_v2/overnight_release.json` **stays `preparing` / `checks_passed=false`**; no automated overnight job or Qwen3 14B/32B training has been started with this Excel. No original-source passages or private datasets were uploaded to public GitHub.

## Quality checks and limits

The workbook was exported using `artifact_tool`; exported file and JSONL hashes and row-count audit were checked. Source text embedding in references, user-provided semantic scope and source-aware review remain manual audit tasks. **No released 10k authoritative dialogue gold set is claimed**. Qwen model answer quality, complete 194-case source reconstruction, tokenizer length audits, actual GPU fit, Swift parity and macOS/Xcode compilation have **not** been tested by this workbook-only change.

The new manifest regression checks **only** that the mirrored candidate manifest is exact, row totals and hashes are immutable, and training release remains disabled. Do not mistake that test for end-to-end model training or author reasoning review. All historical failures and prior training snapshots remain unchanged.
