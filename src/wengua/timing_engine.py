"""Deterministic traditional timing candidate search over calendar-engine periods.

Source method is selected from a real book reasoning trace. Calendar periods and
their branch labels MUST originate from separately verified calendar/casting
engine records. This validates shape & computes exact windows but cannot
cryptographically attest the caller's 'verified' flag or scientifically predict
external events. GPT cannot invent calendar rows, date windows or method choice.
"""
from __future__ import annotations
from datetime import datetime
from .phrase_pipeline import canonical_sha

BRANCHES="子丑寅卯辰巳午未申酉戌亥"
CLASH={"子":"午","午":"子","丑":"未","未":"丑",
       "寅":"申","申":"寅","卯":"酉","酉":"卯",
       "辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
GRANULARITIES=("day","month","year")
METHODS=("fill_empty","clash_empty")
ALLOWED_OUTCOMES=("success","failure","delayed","mixed","unresolved")

def _parse_local_iso(s):
    if not isinstance(s,str):
        raise ValueError("period datetime must use ISO-8601 with timezone")
    try: obj=datetime.fromisoformat(s)
    except (ValueError,TypeError) as exc:
        raise ValueError("invalid Gregorian ISO-8601 calendar period") from exc
    if obj.tzinfo is None or obj.utcoffset() is None:
        raise ValueError("timezone-offset-aware periods mandatory")
    return obj

def derive_timing_candidates(*, empty_branches, periods, granularity, method,
                             reference_iso, calendar_method_version,
                             calendar_receipt, source_method_ref):
    """Find explicit first upcoming 空亡填实 / 冲实 windows, never invent dates.

    'periods' must already contain method-versioned sexagenary Gregorian day or
    solar-term-defined Chinese month/year intervals from the casting calendar
    engine. We do not convert Gregorian calendar month numbers into 干支月.
    """
    if (granularity not in GRANULARITIES or method not in METHODS
        or not calendar_method_version or not calendar_receipt or not source_method_ref):
        raise ValueError("Need resolution, source rule and versioned calendar proof")
    if (not isinstance(empty_branches,list) or not empty_branches
        or len(set(empty_branches))!=len(empty_branches)
        or any(b not in BRANCHES for b in empty_branches)):
        raise ValueError("Complete source-observed XunKong branches required")
    if not isinstance(periods,list) or not periods:
        raise ValueError("Verified calendar periods not supplied")
    reference=_parse_local_iso(reference_iso)
    target={b if method=="fill_empty" else CLASH[b]:b for b in empty_branches}
    candidates=[]
    seen=set()
    for period in periods:
        if not isinstance(period,dict) or set(("start_iso","end_iso","branch"))-set(period):
            raise ValueError("calendar period missing start, end, or branch")
        start=_parse_local_iso(period["start_iso"])
        end=_parse_local_iso(period["end_iso"])
        if end<=start:
            raise ValueError("calendar period must have positive chronological length")
        if period["branch"] not in BRANCHES:
            raise ValueError("Unrecognized sexagenary period branch")
        if start<reference:continue
        if period.get("granularity")!=granularity or period.get("calendar_method_version")!=calendar_method_version:
            raise ValueError("Mixed calendar methods or scales cannot be searched")
        key=(period["start_iso"],period["end_iso"],period["branch"])
        if key in seen:raise ValueError("duplicate calendar period")
        seen.add(key)
        if period["branch"] in target:
            candidates.append({
                "method":method,"source_empty_branch":target[period["branch"]],
                "trigger_branch":period["branch"],"granularity":granularity,
                "window_start_iso":period["start_iso"],"window_end_iso":period["end_iso"],
                "source_method_ref":source_method_ref,
                "calendar_method_version":calendar_method_version,
                "calendar_receipt":calendar_receipt,
                "traditional_symbolic_condition_only":True})
    return sorted(candidates,key=lambda c:c["window_start_iso"])

def finalize_traditional_decision(*, outcome, reasoned_support, reasoned_counter,
                                  chosen_timing, known_timing_candidates,
                                  timing_choice_rule_ref, confidence_boundary):
    """Fail-closed contract: no vague 'need to check when X is filled' final answer.

    A resolved judgment MUST say what the traditional method forecasts and
    specify a computed event period, or explicitly report which missing fact
    prevents timing. 'unresolved' is allowed only when decisive evidence is
    actually missing. No outcome is factually or scientifically certified here.
    """
    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError("Outcome must be a bounded traditional interpretation")
    if not isinstance(reasoned_support,list) or not reasoned_support or any(not x for x in reasoned_support):
        raise ValueError("Judgment must show nonempty concrete supporting evidence")
    if not isinstance(reasoned_counter,list):
        raise ValueError("Must account for counterevidence even when empty")
    if not confidence_boundary:
        raise ValueError("Must distinguish book tradition from reality")
    if not isinstance(known_timing_candidates,list):
        raise ValueError("Timing candidate audit required")
    if outcome!="unresolved":
        if not isinstance(chosen_timing,dict) or chosen_timing not in known_timing_candidates:
            raise ValueError("Concrete chosen window must be one of actually computed windows")
        if not timing_choice_rule_ref:
            raise ValueError("Explain why this window/method was chosen, not just '填实再说'")
        return {"status":"conditional_concrete_traditional_forecast",
                "outcome":outcome,"window_start_iso":chosen_timing["window_start_iso"],
                "window_end_iso":chosen_timing["window_end_iso"],
                "timing_granularity":chosen_timing["granularity"],
                "timing_calculation":chosen_timing,
                "selection_rule_ref":timing_choice_rule_ref,
                "support":reasoned_support,"counterevidence":reasoned_counter,
                "confidence_limit":confidence_boundary,
                "this_is_not_verified_external_event_prediction":True,
                "decision_trace_sha256":canonical_sha({
                    "o":outcome,"timing":chosen_timing,"ref":timing_choice_rule_ref,
                    "support":reasoned_support,"counterevidence":reasoned_counter})}
    if chosen_timing is not None:
        raise ValueError("Cannot present a concrete window for unresolved event")
    return {"status":"unresolved_missing_decisive_evidence",
            "outcome":outcome,"missing_decisive_evidence":reasoned_support,
            "counterevidence":reasoned_counter,
            "confidence_limit":confidence_boundary,
            "no_concrete_window_can_be_defended":True}
