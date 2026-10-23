"""Cross-domain, source-conscious symbol/palace energy FACTS; review only.

No invented score, medical outcome, market return or fortune verdict.
A nominal element relation does not by itself establish its effectiveness.
The same per-symbol facts may be used by any domain's separate reasoning rules.
"""
from __future__ import annotations

from .semantic_lookup import GUAS, DOORS, STAR_ELEMENT, GENERATES, CONTROLS, nine_star_month_status
from .health_severity_template import MONTH_ELEMENTS, STEM_ELEMENTS
from .symbol_relations import door_season
from .health_lifecycle_v391 import stage_for_stem_at_actual_palace

# Matches existing JS and native SwiftUI mappings; 本流派值符固定为土.
DEITY_ELEMENTS = {
    "值符": "土", "螣蛇": "火", "腾蛇": "火", "太阴": "金",
    "六合": "木", "白虎": "金", "玄武": "水", "九地": "土", "九天": "金",
}
SEASON_BY_BRANCH = {
    "寅": "春", "卯": "春", "辰": "四季月", "巳": "夏", "午": "夏",
    "未": "四季月", "申": "秋", "酉": "秋", "戌": "四季月",
    "亥": "冬", "子": "冬", "丑": "四季月",
}
KIND_ALIASES = {"八神": "deity", "九星": "star", "八门": "door", "天干": "stem"}


def ordinary_month_stage(element: str, month_element: str) -> str:
    """Earthly 五行旺相休囚死; never use in place of 九星旺相休囚废."""
    if element not in GENERATES or month_element not in GENERATES:
        raise ValueError("Known five elements required")
    if element == month_element:
        return "旺"
    if GENERATES[month_element] == element:
        return "相"
    if GENERATES[element] == month_element:
        return "休"
    if CONTROLS[element] == month_element:
        return "囚"
    if CONTROLS[month_element] == element:
        return "死"
    raise AssertionError("Five elements relation incomplete")


def _directed_relation(symbol_element: str, palace_element: str) -> str:
    if symbol_element == palace_element:
        return "比和"
    if GENERATES[symbol_element] == palace_element:
        return "符号生宫"
    if GENERATES[palace_element] == symbol_element:
        return "宫生符号"
    if CONTROLS[symbol_element] == palace_element:
        return "符号克宫"
    if CONTROLS[palace_element] == symbol_element:
        return "宫克符号"
    raise AssertionError("Five elements relation incomplete")


def inspect_symbol_energy(kind: str, symbol: str, month_branch: str, palace: int) -> dict:
    """Return auditable, directional facts for any domain; NOT a verdict.

    Month is the verified *solar-term month branch*, not a Gregorian month.
    A centre-5 cell has no ordinary eight deity/gate/star, and is blocked here
    until its own source-specific placement method is explicitly selected.
    """
    kind = KIND_ALIASES.get(kind, kind)
    if kind not in ("deity", "star", "door", "stem"):
        raise ValueError("Unsupported symbolic factor")
    if month_branch not in MONTH_ELEMENTS:
        raise ValueError("Require a source-verified seasonal month branch")
    if palace not in GUAS or palace == 5:
        raise ValueError("Centre five and unknown palaces need a separate source method")
    if kind == "deity":
        elements = DEITY_ELEMENTS
    elif kind == "star":
        elements = STAR_ELEMENT
    elif kind == "door":
        elements = {name + "门": el for name, el in DOORS.items()}
        if symbol in DOORS:
            symbol += "门"
    else:
        elements = STEM_ELEMENTS
    if symbol not in elements:
        raise ValueError("Symbol has no defined element in this method version")
    element = elements[symbol]
    month_element = MONTH_ELEMENTS[month_branch]
    palace_element = GUAS[palace][1]
    result = {
        "kind": kind, "symbol": symbol, "symbol_element": element,
        "month_branch": month_branch, "month_element": month_element,
        "palace": palace, "palace_element": palace_element,
        "palace_month_stage": ordinary_month_stage(palace_element, month_element),
        "nominal_relation_from_symbol": _directed_relation(element, palace_element),
        "effective_control": "unverified_needs_both_sides_and_palace_conditions",
        "source_level": "source_method_fact_review_only",
        "numeric_score": None, "usable_as_final_verdict": False,
    }
    if kind == "deity":
        result["symbol_month_stage"] = None
        result["month_method"] = "八神自身不单独套月令旺衰"
    elif kind == "star":
        result["symbol_month_stage"] = nine_star_month_status(symbol, month_element)["value"]
        result["month_method"] = "九星旺相休囚废"
    else:
        result["symbol_month_stage"] = ordinary_month_stage(element, month_element)
        result["month_method"] = "普通五行旺相休囚死"
    if kind == "door":
        seasonal = SEASON_BY_BRANCH[month_branch]
        book = door_season(symbol, seasonal)
        result["book_door_season"] = seasonal
        result["book_door_month_stage"] = book["stage"]
        result["book_door_source_lines"] = book["source_lines"]
        result["month_views_must_remain_distinct"] = True
    if kind == "stem":
        lifecycle = stage_for_stem_at_actual_palace(symbol, palace)
        result["palace_twelve_life_facts"] = lifecycle["actual_stage_facts"]
        result["palace_has_tomb"] = lifecycle["has_tomb"]
        result["palace_has_extinction"] = lifecycle["has_extinction"]
        result["twelve_life_independent_of_month"] = True
    return result


def illustrate_user_tianrui_scores(month_branch: str, palace: int = 3) -> dict:
    """Exactly reproduce user-supplied arithmetic, without endorsing weights.

    The illustrative fixed -4 is a *nominal* palace relation constant and does
    NOT reflect that 震木宫 is 死 in 申月 but 相 in 亥月.
    No score for other months is fabricated.
    """
    if month_branch not in ("申", "亥") or palace != 3:
        raise ValueError("User supplied arithmetic only for 申/亥月震三宫")
    fact = inspect_symbol_energy("star", "天芮星", month_branch, palace)
    if fact["nominal_relation_from_symbol"] != "宫克符号":
        raise AssertionError("Illustration requires 宫克星")
    proposed_base = {"申": 10, "亥": 3}[month_branch]
    proposed_palace_adjustment = -4
    return {
        "month_branch": month_branch,
        "star_month_stage": fact["symbol_month_stage"],
        "palace_month_stage": fact["palace_month_stage"],
        "proposed_star_base": proposed_base,
        "proposed_nominal_palace_adjustment": proposed_palace_adjustment,
        "arithmetic_only_total": proposed_base + proposed_palace_adjustment,
        "effective_palace_control": "unverified: palace strength differs by month",
        "weights_status": "user_hypothesis_not_book_calibrated",
        "usable_as_verdict": False,
        "usable_for_medical_guidance": False,
    }
