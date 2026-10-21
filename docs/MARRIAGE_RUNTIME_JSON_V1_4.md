# WenguaApp 婚姻 22 场景：实际盘面 JSON 接入 V1.4

本接口已经接上原书示例九宫计算、22个婚姻细分问题识别、书本原始证据读取和可直接计算的符号关系；它目前返回一份**可复查研究审计**，不是已形成结论及应期的最终断卦。对于没有核实年月节气、六亲年命或未实现原著综合证据规则的盘，不能让GPT补写确定日期。

## 完整输入结构与字段

建议在项目根目录运行下面的 Python 示例，它会**用原书起局样例生成一份符合现有引擎结构的可重复实验JSON**，而不是要求手写九宫或从古籍图像猜门星：

```python
import json
from src.wengua.casting_shenqi import layout_from_explicit_bureau

chart = layout_from_explicit_bureau(dun="yang", ju=3, hour_ganzhi="丁巳")
payload = {
  "chart": chart,
  "calendar_inputs": {
    "day_ganzhi": "癸酉",
    "solar_term": "芒种",
    "hour_ganzhi": "丁巳"
  },
  "original_casting_book_example_key": "shenqi_casting_example_1995_06_11",
  "inquiry": {
    "domain": "marriage",
    "scene_id": "marriage.scene.02",
    "question_text": "我们能否发展恋爱关系？",
    "relationship": "self",
    "querent": {"year_ganzhi": "癸酉"},
    "subject": {"year_ganzhi": "乙酉"},
    "partner": {"year_ganzhi": "庚寅"}
  }
}
with open("source_chart_study.json", "w", encoding="utf-8") as f:
  json.dump(payload, f, ensure_ascii=False, indent=2)
```

**注意：上面只用《神奇之门》的起盘练习盘加虚构关系问题验证软件逻辑，不是历史真实恋爱案例，也不是实际恋爱占断。** 1995年节气信息只按原书明确给定，尚未独立以现代历法数据库验证。若用户实际使用其它日期，需要已有引擎支持的真实年月日时、正确时区与经过认证的干支节气数据，不能套用这个例子。

## 调用命令

在项目根目录：

```bash
python -m scripts.run_marriage_json_study \
  --input source_chart_study.json \
  --database 'archives/sqlite/WenguaApp_双书194案例_婚姻真实排盘接入V1_4_完整研究库.sqlite3' \
  --output source_chart_audit.json
```

返回`source_chart_audit.json` 包括真实重算九宫`source_chart`、双方人员`actual_year_stem_candidate_binding`、24项`factor_audit`、`author_first_and_method_source_links`、`source_later_feedback_validation_only`以及`missing_to_publish`。例如两人年命用神候选都位于同宫时，计算出的纯宫五行“比和”只是事实关系，不足以据此断必成。当前真正`traditional_forecast_result/calculated_primary_timing/human_natural_phrase`均为null。

## 验收与安全边界

- 传入`chart.palaces`任一门、星、神、载干或宫位不符合源规则重排结果即拒绝。
- 仅设置`chart.status=engine_verified`无权证明起盘正确；需要独立的起盘/节气历法认证，未经接入不能绕过。
- 年命对照依据原书六十甲子与六甲遁六仪，但代测关系主辅用神尚必须经过领域和原著方法再选取，不能把人物年命落宫当最终结局。
- 把本书作者后来改局、书中结果反馈与首断严格隔离；后见成功日期绝对不能赋予新盘。
- 本轮2张已对照原著的起盘样本×22个场景生成44个技术回归记录；历史书案例总数仍194，0个新真实婚姻案例，0份经完整六层验收、带真实公历应期的正式断词。

后续顺序：先让`FACTORS_IDS`24项在有原书规则时能真实逐项计算，补齐真正节气历法和中五宫值使特殊路径；再做角色绑定与两书案例证据决策的正确性测试；最后才允许推出明确成败、具体应期和200字GPT中文。
