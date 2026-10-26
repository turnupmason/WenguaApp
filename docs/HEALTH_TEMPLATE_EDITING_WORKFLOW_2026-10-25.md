# WenguaApp · 疾病严重程度断词模板在哪里、从哪抓数据、如何自行修改（2026-10-25）

**本文件是当前真正可运行 V-next 支线的编辑手册，不是重新设计的假想流程。** 老 V3.9.1 发布版本、iOS SwiftUI 画盘源码、旧81格局候选索引均不动。下面所有路径以公开仓库 `turnupmason/WenguaApp` 的 `main` 为准。

## 只需要改的两个地方

1. **断词话术（最建议自己改的模板）：** [`data/templates/health_severity_vnext/reading_template.json`](../data/templates/health_severity_vnext/reading_template.json)
   - `section_titles`：每节标题，例如「天芮病宫」「天心医生」「全部证据合断」。
   - `macros.role`：每一个用神段落怎么排列。 `{palace_detail}` 是本宫详细星神门天地干和Excel81古诀；`{palace_score}` 是用户当前±5研究宫分；`{extra_illness}` 是天芮源独立合断；`{role_relation}` 是该用神对病宫的真实生克和克制表，`{gender_note}` 是性别辅助提示。
   - `formation`：**每命中一个真实天盘干/地盘干有序对**的完整格局短句。可直接自行改为「{name}（{polarity}）：古文{classical_text}；释义{classical_meaning}；天地盘取象{imagery}」等；只要保留变量括号、不破坏JSON语法即可。
   - `macros.macro`、`overall_resolved`、`overall_pending`、`verdict`、`timing`：分别修改五不遇时伏反吟总纲、已核合断、确实缺盘事实合断、最终结论、应期。**不需要改计算逻辑**。
   - 不能把 `{name}` 等变量名任意改为别的词，除非同时在 [`health_reading_template_vnext.py`](../src/wengua/health_reading_template_vnext.py) 对应位置更新传入的占位名；不支持从网上任意抓取临时文本。

2. **81个天地盘有序格局的真实内容（本轮 Excel 一字不漏转换）：** [`data/knowledge/health_81_excel_20261025/81_pairs.tsv`](../data/knowledge/health_81_excel_20261025/81_pairs.tsv)
   - 文件第一行固定列：`天盘干|地盘干|格局名称|吉凶|古文（摘句）|古诀大意|天地盘取象`；之后恰好81行，逐行按 9×9 实际天地盘干排序。
   - 用户上传原Excel有**81条完整不重复有序组合**（25吉/56凶），工作表 `81格完整表`、区域 `B4:H85`。原Excel文件SHA256：`662c6ad43272367acf034e2c65758dffd783c815734e40ad76fdb58a77d95336`；当前GitHub TSV 按Excel提取内容逐字符检验一致（FNV UTF-16 `fea0e96e`）。`古文（摘句）`是原文件提供的摘句，程序**不虚构更长的原典全文**。
   - 日常直接在GitHub网页编辑这份 TSV 每行的**格局名称、古文、古诀大意、天地盘取象**即可；改`吉凶`会改变本次V-next研究宫分的来源极性，所以必须按你要的新版来源改，不能随口改。
   - 若你想在自己的 Excel 里修改，再用 [`scripts/import_user_81_excel_20261025.py`](../scripts/import_user_81_excel_20261025.py) 将Excel严格转成TSV；示例 `python scripts/import_user_81_excel_20261025.py "奇门遁甲_天地盘81格_古文吉凶化解取象.xlsx"`；此离线导入使用 `artifact_tool`（本地需安装），读取Excel B4:H85并校验81/81。有缺格、错列、重复、有竖线分隔符都拒绝覆盖，避免乱写。**只改自己本地Excel但不提交生成的新TSV，GitHub运行时不会自动更新。**

## 程序真实“抓取 → 替换 → 输出”调用链

```text
真实时辰 iso + 时区 + 人物关系
  └── src/wengua/health_text_pipeline_vnext_review.py
      auto_cast_health_review_text(...)
         ├── astro_calendar.solar_chart_clock             获取真实四柱/节气
         ├── casting_shenqi.layout_from_explicit_bureau   一次起盘九宫
         └── health_severity_vnext_review.analyze_health_severity_review
              ├── bind_patient(...)                      只取真实指定患者关系
              └── domain_selected_energy_vnext.selected_health_sequence
                   ├── health_macro_facts_vnext           五不遇时／伏吟／反吟
                   ├── health_palace_detailed_vnext.inspect_complete_selected_palace
                   │    ├── 真实天盘各携干+本宫地盘干
                   │    └── health_81_excel_catalog_vnext.for_real_palace
                   │         └── 【读取本地Git仓库81_pairs.tsv】
                   │              按「天盘干／地盘干」精确取：
                   │              格局名称、吉凶、古文、古诀大意、天地盘取象
                   ├── health_quant_overlay_vnext._quantize_one
                   │    └── health_81_excel_catalog_vnext.authoritative_score_source
                   │         Excel 81格明示吉凶（不是旧缺条件门控）
                   └── domain_selected_energy_vnext.selected_health_sections
                        ├── health_palace_detailed_vnext.render_complete_selected_palace
                        │    └── health_reading_template_vnext.formation_sentence
                        │         【读取本地Git仓库reading_template.json 的 formation】
                        │         .format_map({heaven,earth,name,polarity,
                        │                      classical_text,classical_meaning,imagery})
                        └── health_reading_template_vnext.render/title
                             【读取reading_template.json 的 macros + section_titles】
                             .format_map({palace_detail,palace_score,role_relation,...})
              └── reading_text = "\\n\\n".join(标题 + "：" + 填好字段的正文)
```

**关键澄清：程序不是用户点占卜时从 GitHub 网站联网抓文件。** 它读**随该版本一起 checkout／部署的 GitHub 仓库本地文件**，通过 Python `Path.read_text` 打开 TSV 和 JSON。GitHub 网页上的改动需成功 commit，并让运行环境切到包含该提交的新代码/资源；本地运行进程复用带缓存的 `catalog()`、`template()`，编辑后需要重启程序或清除缓存才生效。不存在自动从网页实时热更新的隐形链接。

**iOS 现有 SwiftUI 九宫预览并未直接从这个 Python JSON 模板在线抓数据**；本次生效的是 V-next Python 断案/预览调用链。正式 V3.9.1 冻结路径独立存在，不因修改 JSON 模板自动改变旧发布断词。

## 以后你自己改的最快步骤

1. 打开 `main` 中的 [断词模板 JSON](../data/templates/health_severity_vnext/reading_template.json)，用 GitHub 铅笔按钮修改文字／调整占位符排列 → **Commit changes**。
2. 若要改古文／格局名称／大意／天地取象，打开 [81格数据表 TSV](../data/knowledge/health_81_excel_20261025/81_pairs.tsv)，只改目标那一行 → **Commit changes**。
3. GitHub Actions 触发 [Health Conditional Evidence Review Preview](../.github/workflows/health_vnext_conditional_review.yml)：Python3.11/3.12检查 **全部81格、真盘、四个原字字段、文本模板占位符、老V3.9.1冻结读取**；全仓 `WenguaApp CI` 也必须为绿色。若编辑导致缺少占位符或错行，测试拒绝交付。
4. 新代码部署到实际服务后，`auto_cast_health_review_text(...)` 才会在实际起盘后按新模板排版；旧自动起盘规则、原书案例、其他领域数据不受影响。

## 你实际看到的一条格局示范（这里仅演示查表，不是测病）

当前Excel原句：
- 真实天盘 **戊**、地盘 **丙** → **青龙返首（吉）**
- 古文：**动作大利。**
- 古诀大意：**主动行动有利**
- 天地盘取象：**戊藏甲木为青龙，甲木生丙阳火，如青龙回首获得光明。**

这四项都从 TSV 相应 **戊|丙** 一行读取，而不是从上一代 82 行冲突数据集手工拼凑；Excel内另有「门吉事吉，门凶事凶」等古文条件词，这些会**完整保留为古文内容**，不再变成程序凭空宣称「81格局未满足条件」的全局拦截。五不遇时／伏反吟、旬空真假、200格和宫位分数作为**另外的真实盘事实**分析，不会把这81个原始格局覆盖。
