"""Deterministic state catalog and guarded source-based interpretation.

A state index is NOT a calculated, verified nine-palace chart.
"""
from dataclasses import dataclass
from itertools import product

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
SCHOOL = "shijia_zhuanpan"

def cycle60():
    return tuple(STEMS[i % 10] + BRANCHES[i % 12] for i in range(60))

@dataclass(frozen=True)
class State:
    dun: str
    ju: int
    hour: int

    def __post_init__(self):
        if self.dun not in ("yang", "yin") or type(self.ju) is not int or not 1 <= self.ju <= 9 or type(self.hour) is not int or not 0 <= self.hour < 60:
            raise ValueError("Invalid state index; valid: yin/yang, ju 1..9, hour 0..59")

    def as_dict(self):
        return {"state_id": f"{self.dun}-{self.ju:02d}-{self.hour:02d}",
                "school_id": SCHOOL, "dun": self.dun, "ju": self.ju,
                "hour_index": self.hour, "hour_ganzhi": cycle60()[self.hour],
                "status": "index_only_unverified_chart"}

def state_index():
    return [State(d, j, h).as_dict() for d, j, h
            in product(("yang", "yin"), range(1, 10), range(60))]

def _get(chart, path):
    item = chart
    for part in path.split("."):
        if not isinstance(item, dict) or part not in item:
            return False, None
        item = item[part]
    return True, item

def _conditions_match(chart, when):
    if not isinstance(when, dict) or not when:
        return False
    for path, expected in when.items():
        found, actual = _get(chart, path)
        if not isinstance(path, str) or not found or actual != expected:
            return False
    return True

def compose_reading(chart, domain, relationship, rules):
    """Only approved source-linked rules AND verified charts may generate a reading.

    Rule records are provided by a separately authenticated, locally audited
    rule release. This function doesn't approve GPT prose or validate astronomy.
    """
    if (not isinstance(chart, dict) or chart.get("status") != "engine_verified"
        or chart.get("school_id") != SCHOOL
        or not all(chart.get(x) for x in ("chart_id", "method_version", "verification_receipt"))):
        return {"status": "blocked_unverified_chart", "text": None, "summary": None, "evidence": []}
    matches = []
    for r in rules:
        if (r.get("status") == "approved"
            and r.get("school_id") == SCHOOL
            and r.get("domain_id") == domain
            and r.get("relationship_id") in ("any", relationship)
            and all(isinstance(r.get(k), str) and r[k].strip() for k in
                    ("rule_id", "source_ref", "interpretation", "summary"))
            and _conditions_match(chart, r.get("when"))):
            matches.append(r)
    if not matches:
        return {"status": "blocked_no_applicable_reviewed_rule", "text": None, "summary": None, "evidence": []}
    conclusions = {r["summary"] for r in matches}
    if len(conclusions) != 1:
        return {"status": "blocked_conflicting_conclusions", "text": None,
                "summary": None, "evidence": [{"rule_id": r["rule_id"], "source_ref": r["source_ref"]} for r in matches]}
    return {"status": "rule_based_traditional_explanation",
            "text": "\n".join(r["interpretation"] for r in matches),
            "summary": next(iter(conclusions)),
            "evidence": [{"rule_id": r["rule_id"], "source_ref": r["source_ref"]} for r in matches],
            "limitations": "仅是核实过的传统古籍解读，不证明预测现实事件的有效性。"}
