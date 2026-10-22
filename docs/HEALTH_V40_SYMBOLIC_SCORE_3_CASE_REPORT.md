# V4.0 实验性奇门病势象意评分（非健康指数/概率）

来源是用户提出的100分起始加减分方案和另列的病人、病宫、乾坤、旬空、刑墓、驿马冲墓研究候选。
**不能把分值解释成真实病情严重程度、病愈概率、死亡风险或医药疗效。**
既有 V3.9 文字未修改。这三份是固定旧问题的新模型回放，绝非新独立盲测。

每个总分保留未截断分和0—100显示分。分数超过100也不会让健康优于100%，它只暴露算分模型尚未校准的缺陷。

## 1. user_20261022_1200_EDT

四柱：丙午/戊戌/己巳/庚午
；患者4宫，天芮病宫6宫。
原始100＋调整-54＝46；区间显示：46（仅象意分，非百分比）。

| 项目 | 分值 | 真实宫位及规则 |
|---|---:|---|
| illness_controls_patient | -25 | 病宫克患者宫 |
| death_door_co_palace_patient | -8 | 患者本宫临死门 |
| patient_stem_month_vigorous | +6 | 患者主用干在月令旺 |
| patient_palace_month_weak | -4 | 患者宫五行在月令囚 |
| illness_tianrui_star_month_vigorous | -15 | 天芮月令相 |
| patient_good_deity | +8 | 患者宫乘六合 |
| patient_branch_month_break | -8 | 月支冲患者宫所辖地支 |
| double_adverse_distinct_chain_penalty | -8 | 疾病攻人或患者助病并见独立凶证，只扣一次协同项 |

缺失或不能自动加减分的条件：
- qian_kun_missing_patient_sex：未提供患者性别，不猜乾坤辅助宫
- illness_duration：未说明新病/久病，伏吟反吟/空亡条件评分不足
- natal_context：没有提供出生年命，年命只作为未取值辅助
- unverified_81_and_17_conditions：原书部分复合条件仍待逐条考证，未自动转成一票否决或加减分

墓库与马星：患者宫4，己墓支丑；入库宫位匹配=False，时支驿马在申（2宫），是否正对=False，真正四柱地支冲墓候选=False。开墓判别=not_in_tomb。

## 2. kaiwu.health.19950219.brother_paralysis

四柱：乙亥/戊寅/辛巳/癸巳
；患者9宫，天芮病宫2宫。
原始100＋调整-10＝90；区间显示：90（仅象意分，非百分比）。

| 项目 | 分值 | 真实宫位及规则 |
|---|---:|---|
| patient_generates_illness | -8 | 患者宫生病宫 |
| patient_stem_month_weak | -6 | 患者主用干在月令死 |
| patient_palace_month_vigorous | +4 | 患者宫五行在月令相 |
| illness_tianrui_star_month_weak | +10 | 天芮月令囚 |
| tianrui_geng_same_palace | -10 | 庚与天芮同宫 |

缺失或不能自动加减分的条件：
- patient_void_duration：患者宫旬空，但未提供新病或久病，不给固定吉凶分
- fuyin_duration：伏吟主迟，但未确认为久病，不机械扣轻重分
- illness_duration：未说明新病/久病，伏吟反吟/空亡条件评分不足
- unverified_81_and_17_conditions：原书部分复合条件仍待逐条考证，未自动转成一票否决或加减分

墓库与马星：患者宫9，戊墓支戌；入墓宫位匹配=False，时支驿马在亥（6宫），是否正对=False，真正四柱地支冲墓候选=False。开墓判别=not_in_tomb。

## 3. shenqi.health.19961102.on_site_health

四柱：丙子/戊戌/癸卯/庚申
；患者6宫，天芮病宫3宫。
原始100＋调整24＝124；区间显示：100（仅象意分，非百分比）。

| 项目 | 分值 | 真实宫位及规则 |
|---|---:|---|
| patient_controls_illness | +20 | 患者宫克病宫 |
| same_palace_event_or_illness_medicine_opportunity | +5 | 时干/病宫与医药宫同宫，古籍的医治机会辅助象 |
| patient_stem_month_weak | -6 | 患者主用干在月令死 |
| patient_palace_month_vigorous | +4 | 患者宫五行在月令相 |
| illness_tianrui_star_month_vigorous | -15 | 天芮月令相 |
| patient_good_deity | +8 | 患者宫乘值符 |
| double_suppression_distinct_chain_bonus | +8 | 患者制病并且病宫制天芮的独立两段关系，只加一次协同项 |

缺失或不能自动加减分的条件：
- qian_kun_missing_patient_sex：未提供患者性别，不猜乾坤辅助宫
- illness_duration：未说明新病/久病，伏吟反吟/空亡条件评分不足
- natal_context：没有提供出生年命，年命只作为未取值辅助
- unverified_81_and_17_conditions：原书部分复合条件仍待逐条考证，未自动转成一票否决或加减分

墓库与马星：患者宫6，癸墓支未；入墓宫位匹配=False，时支驿马在寅（8宫），是否正对=False，真正四柱地支冲墓候选=False。开墓判别=not_in_tomb。

## 研究限制

用户所提分值、交互加减权重和马星对宫开墓的退款比例都未用独立盲测校准。
大部分古籍案例有已知结局，不能直接用结局调参后当验证。
确定新旧病、病人性别、实际人物年命等之前，对应项目保持未评分。
原书组合全量81条、疾病补充42条、复合17条仍必须保留出处并逐条判断条件；这里不是声称所有项目可完全数值化。
