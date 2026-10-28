"""V8.0 read-only graph of independently selected real signifiers.

This is a domain-neutral, purely factual model. It NEVER replaces the
user-approved health V8.0 scoring engine, never assigns a bonus, and never
guesses a future domain's role, use-god or favorable relationship.

A signifier (kind, symbol_id, palace_id) is an actual occupant.
Several named roles can point to the very same signifier without multiplying
its source fact, physical palace grade, or a source-target action.
Different real signifiers in the same palace retain separate source powers.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Mapping

TIERS = ("极小", "小", "中等", "大", "极大")
ELEMENTS = {
    1: "水", 2: "土", 3: "木", 4: "木", 5: "土",
    6: "金", 7: "金", 8: "土", 9: "火",
}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
RESTRICTIONS = frozenset(("真空", "假空", "入墓", "击刑", "被宫克", "门迫"))
KINDS = frozenset(("star", "door", "deity", "stem", "palace", "other"))


@dataclass(frozen=True)
class SelectedSignifier:
    role_key: str
    kind: str
    symbol_id: str
    palace_id: int
    energy_fact_id: str
    strength: str | None
    restrictions: frozenset[str] = frozenset()

    @property
    def identity(self) -> tuple[str, str, int]:
        """Physical symbol identity, NOT the number of assigned use-god roles."""
        return (self.kind, self.symbol_id, self.palace_id)

    def __post_init__(self) -> None:
        if not self.role_key or not self.symbol_id or not self.energy_fact_id:
            raise ValueError("Actual role/symbol/source identifier required")
        if self.kind not in KINDS:
            raise ValueError("Unknown kind (cannot infer a different source table)")
        if self.palace_id not in ELEMENTS:
            raise ValueError("Only real nine-palace positions are accepted")
        if self.strength is not None and self.strength not in TIERS:
            raise ValueError("No signed palace grade or improvised strength")
        if not self.restrictions.issubset(RESTRICTIONS):
            raise ValueError("Unregistered restrictions must be source-reviewed")


# A chosen use-god obliges us to inspect ALL real residents of its palace.
ENVIRONMENT_KINDS = frozenset(("star", "door", "deity", "heaven_stem", "earth_stem", "ordered_81_pattern"))
PALACE_FLAGS = frozenset(("真空", "假空", "驿马", "天盘入墓", "地盘入墓", "六仪击刑", "门迫", "伏吟", "反吟"))

@dataclass(frozen=True)
class PalaceFactor:
    category: str
    symbol_id: str
    energy_fact_id: str
    strength: str | None = None
    signed_contribution: int | None = None
    restrictions: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if self.category not in ENVIRONMENT_KINDS or not self.symbol_id or not self.energy_fact_id:
            raise ValueError("Original symbol and kind-specific source required")
        if self.strength is not None and self.strength not in TIERS:
            raise ValueError("Source strength cannot be a signed palace grade")
        if (self.signed_contribution is not None and
                (type(self.signed_contribution) is not int or not -5 <= self.signed_contribution <= 5)):
            raise ValueError("Invalid auspiciousness contribution")
        if not self.restrictions.issubset(RESTRICTIONS):
            raise ValueError("Unreviewed resident restrictions")

@dataclass(frozen=True)
class PalaceEnvironment:
    palace_id: int
    stars: tuple[PalaceFactor, ...]
    door: PalaceFactor | None
    deity: PalaceFactor | None
    heaven_stems: tuple[PalaceFactor, ...]
    earth_stem: PalaceFactor | None
    ordered_81_patterns: tuple[PalaceFactor, ...]
    flags: frozenset[str]
    auspicious_grade: int

    def __post_init__(self) -> None:
        if self.palace_id not in ELEMENTS or type(self.auspicious_grade) is not int or not -5 <= self.auspicious_grade <= 5:
            raise ValueError("Real palace and signed V8 auspiciousness required")
        if not self.flags.issubset(PALACE_FLAGS):
            raise ValueError("Unreviewed real palace special condition")
        sets = ((self.stars, "star"), (self.heaven_stems, "heaven_stem"),
                (self.ordered_81_patterns, "ordered_81_pattern"))
        if any(x.category != category for items,category in sets for x in items):
            raise ValueError("Mixed sky/earth/81/star source category")
        for item,category in ((self.door,"door"),(self.deity,"deity"),(self.earth_stem,"earth_stem")):
            if item is not None and item.category != category:
                raise ValueError("Wrong source table or symbol plane")
        if self.palace_id != 5 and not (
            self.stars and self.door and self.deity and
            self.heaven_stems and self.earth_stem and self.ordered_81_patterns
        ):
            raise ValueError("Selected real palace must inspect ALL components")
        if self.palace_id == 5 and (
            self.stars or self.door or self.deity or self.heaven_stems or self.ordered_81_patterns
        ):
            raise ValueError("Middle five cannot be given invented ordinary doors/stars/deity")

    @property
    def residents(self) -> tuple[PalaceFactor, ...]:
        return (self.stars + ((self.door,) if self.door else ()) +
                ((self.deity,) if self.deity else ()) + self.heaven_stems +
                ((self.earth_stem,) if self.earth_stem else ()) +
                self.ordered_81_patterns)

    def report(self) -> dict:
        return {
            "palace_id": self.palace_id, "palace_element": ELEMENTS[self.palace_id],
            "auspicious_grade_once": self.auspicious_grade,
            "flags": sorted(self.flags), "source_complete": True,
            "factors": [
                {"category": f.category, "symbol_id": f.symbol_id,
                 "energy_fact_id": f.energy_fact_id, "strength": f.strength,
                 "signed_contribution_audit_only": f.signed_contribution,
                 "restrictions": sorted(f.restrictions)}
                for f in self.residents
            ],
            "no_extra_intrinsic_stem_vote": True,
        }


@dataclass(frozen=True)
class DomainCondition:
    condition_id: str
    domain_id: str
    host_roles: frozenset[str]
    helper_kind: str
    helper_symbol_id: str

    def __post_init__(self) -> None:
        if not all((self.condition_id, self.domain_id, self.host_roles,
                    self.helper_kind, self.helper_symbol_id)):
            raise ValueError("Provenanced domain-specific condition required")
        if self.helper_kind not in KINDS:
            raise ValueError("Invalid helper kind")


def relation_between(a: SelectedSignifier, b: SelectedSignifier) -> str:
    if a.identity == b.identity:
        return "同一符号"
    if a.palace_id == b.palace_id:
        return "同宫"
    first = ELEMENTS[a.palace_id]
    second = ELEMENTS[b.palace_id]
    if first == second:
        return "比和"
    if CONTROLS[first] == second:
        return "克"
    if CONTROLS[second] == first:
        return "被克"
    if GENERATES[first] == second:
        return "生"
    if GENERATES[second] == first:
        return "被生"
    raise ValueError("Unresolvable real palace relationship")


class SelectedSignifierGraph:
    """Canonical physical symbols + independent source powers; NO new scores."""

    def __init__(
        self, *, domain_id: str,
        roles: Iterable[SelectedSignifier],
        palace_grades: Mapping[int, int],
        environments: Mapping[int, PalaceEnvironment] | None = None,
    ) -> None:
        if not domain_id:
            raise ValueError("A domain profile must explicitly opt in")
        self.domain_id = domain_id
        bindings = tuple(roles)
        if not bindings:
            raise ValueError("Must select at least one actual use-god")
        if len({b.role_key for b in bindings}) != len(bindings):
            raise ValueError("A role must have one explicit binding")
        if not palace_grades or any(
            p not in ELEMENTS or type(grade) is not int or not -5 <= grade <= 5
            for p, grade in palace_grades.items()
        ):
            raise ValueError("Only already-computed, real signed palace grades")
        self.roles = {b.role_key: b for b in bindings}
        by_id: dict[tuple[str, str, int], SelectedSignifier] = {}
        aliases: dict[tuple[str, str, int], list[str]] = {}
        for b in bindings:
            if b.palace_id not in palace_grades:
                raise ValueError("Selected real palace grade was not supplied")
            old = by_id.get(b.identity)
            if old is not None and (
                old.energy_fact_id != b.energy_fact_id
                or old.strength != b.strength
                or old.restrictions != b.restrictions
            ):
                raise ValueError(
                    "Same actual symbol cannot secretly have two source powers"
                )
            by_id[b.identity] = b
            aliases.setdefault(b.identity, []).append(b.role_key)
        self.signifiers = by_id
        self.alias_roles = {
            ident: tuple(sorted(names)) for ident, names in aliases.items()
        }
        # A physical palace's signed grade is NEVER a signifier's power.
        self.palace_grades = {
            p: palace_grades[p] for p in sorted({b.palace_id for b in bindings})
        }
        self.environments = dict(environments or {})
        if self.environments:
            if set(self.environments) != set(self.palace_grades):
                raise ValueError("Every selected palace needs its COMPLETE environment")
            for pid, env in self.environments.items():
                if env.palace_id != pid or env.auspicious_grade != self.palace_grades[pid]:
                    raise ValueError("Real environment grade and palace location mismatch")

    @property
    def base_palace_total(self) -> int:
        """Once per selected physical palace, independent of alias counts."""
        return sum(self.palace_grades.values())

    def nodes(self) -> list[dict]:
        return [
            {
                "kind": b.kind,
                "symbol_id": b.symbol_id,
                "palace_id": b.palace_id,
                "energy_fact_id": b.energy_fact_id,
                "strength": b.strength,
                "roles": list(self.alias_roles[ident]),
                "restrictions": sorted(b.restrictions),
                "signed_palace_grade": self.palace_grades[b.palace_id],
                "palace_grade_is_not_power": True,
            }
            for ident, b in sorted(self.signifiers.items())
        ]

    def edges(self) -> list[dict]:
        """Directional actual graph edges, no invented result for 生/比和/克.

        For 克, a domain must separately read its original ordered 5x5;
        for 被克, reverse the actual source and target when looking it up.
        Even source+target both existing is NOT an authorized numerical bonus.
        """
        out: list[dict] = []
        for a, b in combinations(
            (self.signifiers[key] for key in sorted(self.signifiers)), 2
        ):
            for first, second in ((a, b), (b, a)):
                rel = relation_between(first, second)
                out.append({
                    "actor_symbol": list(first.identity),
                    "target_symbol": list(second.identity),
                    "actor_energy_fact_id": first.energy_fact_id,
                    "target_energy_fact_id": second.energy_fact_id,
                    "actor_strength": first.strength,
                    "target_strength": second.strength,
                    "relation": rel,
                    "actor_restrictions": sorted(first.restrictions),
                    "target_restrictions": sorted(second.restrictions),
                    "evidence_status": (
                        "ready_for_domain_rule"
                        if first.strength in TIERS and second.strength in TIERS
                        else "strength_pending"
                    ),
                    "effect": None,
                    "bonus_points": None,
                    "source_and_target_independent": True,
                })
        return out

    def resident_evidence(self) -> list[dict]:
        """Check every symbol and real condition for every selected use-god.

        No generic bonus is inferred. The user-approved V8 base remains
        one signed grade per physical palace; each selected role independently
        keeps its own source strength.
        """
        out = []
        for role, chosen in sorted(self.roles.items()):
            env = self.environments.get(chosen.palace_id)
            if env is None:
                continue
            for factor in env.residents:
                kind = "stem" if factor.category in ("heaven_stem","earth_stem") else factor.category
                self_ref = chosen.kind == kind and chosen.symbol_id == factor.symbol_id
                out.append({
                    "role_key": role, "palace_id": chosen.palace_id,
                    "selected_symbol": list(chosen.identity),
                    "selected_source_strength": chosen.strength,
                    "resident_category": factor.category,
                    "resident_symbol": factor.symbol_id,
                    "resident_energy_fact_id": factor.energy_fact_id,
                    "resident_strength": factor.strength,
                    "resident_restrictions": sorted(factor.restrictions),
                    "palace_flags": sorted(env.flags),
                    "is_selected_symbol_itself": self_ref,
                    "independent_cohost_candidate": not self_ref and factor.category != "ordered_81_pattern",
                    "signed_palace_grade_once": env.auspicious_grade,
                    "result_requires_domain_rule": True,
                    "awarded_points": None,
                })
        return out

    def independent_cohost_evidence(
        self, conditions: Iterable[DomainCondition],
    ) -> list[dict]:
        """Only proven *independent host and helper* matches, NO points.

        A condition belongs to ONE domain and must be opted into explicitly.
        A symbol cannot 'meet itself' via time/natal/patient role aliases.
        Tianxin, Yi, Ding, Chief can all coexist independently as real nodes;
        no generic +3 is inferred from their presence.
        """
        result: dict[tuple, dict] = {}
        for rule in conditions:
            if rule.domain_id != self.domain_id:
                raise ValueError("Cannot inherit another domain's special rule")
            for role_key in sorted(rule.host_roles):
                host = self.roles.get(role_key)
                if host is None:
                    continue
                for ident, helper in sorted(self.signifiers.items()):
                    if helper.palace_id != host.palace_id:
                        continue
                    if (helper.kind, helper.symbol_id) != (
                        rule.helper_kind, rule.helper_symbol_id
                    ):
                        continue
                    if helper.identity == host.identity:
                        continue
                    marker = (
                        rule.condition_id, host.identity, helper.identity
                    )
                    entry = result.setdefault(marker, {
                        "domain_id": self.domain_id,
                        "condition_id": rule.condition_id,
                        "host": list(host.identity),
                        "host_energy_fact_id": host.energy_fact_id,
                        "host_strength": host.strength,
                        "helper": list(helper.identity),
                        "helper_energy_fact_id": helper.energy_fact_id,
                        "helper_strength": helper.strength,
                        "palace_id": host.palace_id,
                        "host_roles": [],
                        "restrictions": sorted(host.restrictions | helper.restrictions),
                        "independent_real_symbols": True,
                        "authorized_effect": None,
                        "bonus_points": None,
                    })
                    entry["host_roles"].append(role_key)
        return list(result.values())

    def audit(self, conditions: Iterable[DomainCondition] = ()) -> dict:
        return {
            "version": "v8_0_observation_v8_next_candidate_no_new_score",
            "domain_id": self.domain_id,
            "nodes": self.nodes(),
            "palace_environments": [self.environments[p].report() for p in sorted(self.environments)],
            "palace_environment_completeness": "complete" if self.environments else "awaiting_fact_binding",
            "edges": self.edges(),
            "cohost_evidence": self.independent_cohost_evidence(conditions),
            "all_role_resident_evidence": self.resident_evidence(),
            "palace_grades_once": self.palace_grades,
            "base_palace_total_once": self.base_palace_total,
            "changes_authorized_v80_score": False,
            "unapproved_cross_domain_bonuses": False,
        }
