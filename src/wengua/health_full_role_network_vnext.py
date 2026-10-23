"""V-next review: full illness-domain palace/signifier strength network.

Every illness reading inspects both 乾六 and 坤二 as real palaces even when
neither has a verified personal role. Year-life exists only when user supplied
a genuine birth Ganzhi and the existing binder found its actual sky-stem cell.
No network edge contributes an independent verdict vote: one physical relation
can appear under several labels and must never be double-counted.
"""
from __future__ import annotations

from itertools import permutations
from .factor_energy_combinations import compare_full_factors
from .factor_energy_25_rules import inspect_strength_25


def attach_all_factor_strengths(palace_fact, month_branch):
    """Compute every physical deity, door, star, sky stem and earth stem."""
    observed = []
    seen = set()
    blockers = tuple(
        (["旬空待辨"] if palace_fact["void_branches"] else []) +
        (["天盘入墓"] if palace_fact["sky_tombs"] else []) +
        (["地盘入墓"] if palace_fact["earth_tombs"] else []) +
        (["六仪击刑"] if palace_fact["striking_stems"] else []) +
        (["门迫"] if palace_fact["door_pressure"] else [])
    )

    def include(kind, name, plane="heaven"):
        if not name or (kind, name, plane) in seen:
            return
        seen.add((kind, name, plane))
        observed.append(inspect_strength_25(
            kind, name, month_branch, palace_fact["palace"],
            plane=plane, restrictions=blockers))

    include("deity", palace_fact["deity"])
    include("door", palace_fact["door"])
    for sky in palace_fact["heaven"]:
        include("star", sky["star"])
        include("stem", sky["stem"])
    include("stem", palace_fact["earth_stem"], plane="earth")
    palace_fact["all_symbol_strength_25"] = observed
    primary_kind = "star" if palace_fact["star"] else "stem"
    primary_name = palace_fact["star"] or palace_fact["stem"]
    palace_fact["primary_strength_25"] = next(
        (f for f in observed if f["kind"] == primary_kind
         and f["symbol"] == primary_name), None)
    if palace_fact["primary_strength_25"] is None:
        raise ValueError("Role must match a real visible symbol in its palace")
    return palace_fact


def build_full_health_network(*, illness, doctor, medicine, patient, hour,
                              natal, qian, kun, extras, inquiry, actor):
    """Full directed role graph, with 乾坤 context and verifiable role gates.

    The pair graph is exhaustive over eligible physical nodes; it is NOT an
    exhaustive combinatorial fortune verdict. Its 20x20/25x25 lookups are
    delegated to the previously materialized universal tables.
    """
    for fact in (illness, doctor, medicine, patient, hour, qian, kun,
                 *([natal] if natal else []), *extras):
        if not fact["all_symbol_strength_25"] or not fact["primary_strength_25"]:
            raise ValueError("All role palaces must be energy-inspected")

    bound = {cell["palace"] for cell in actor.get("extra_cells", ()) if cell}
    sex = inquiry.get("patient_sex")
    if actor.get("relationship") == "wife":
        sex = "female"
    elif actor.get("relationship") == "husband":
        sex = "male"

    role_rows = [
        ("illness", illness, "source_illness_star"),
        ("doctor", doctor, "source_doctor_star"),
        ("medicine", medicine, "source_herbal_medicine_symbol"),
        ("patient", patient, actor.get("confidence", "unknown")),
        ("hour", hour, "time_affair_reference"),
    ]
    if natal:
        role_rows.append(("natal", natal, "birth_ganzhi_given_and_actual_sky_stem"))
    for label, palace, needed_sex in (
        ("qian", qian, "male"), ("kun", kun, "female")
    ):
        role_gate = ("role_bound_by_original_source_profile" if palace["palace"] in bound
                     else "sex_correspondence_candidate_unverified" if sex == needed_sex
                     else "physical_palace_observation_only")
        role_rows.append((label, palace, role_gate))
    # Other original-book role-bound auxiliary palaces, excluding repeated 乾坤.
    already = {qian["palace"], kun["palace"]}
    for n, extra in enumerate(extras, 1):
        if extra["palace"] not in already:
            role_rows.append(("extra_"+str(n), extra, "original_profile_auxiliary_candidate"))
            already.add(extra["palace"])

    nodes = {}
    for key, record, role_gate in role_rows:
        primary = record["primary_strength_25"]
        nodes[key] = {
            "id": key, "label": record["role"], "present": True,
            "role_status": role_gate, "palace": record["palace"],
            "palace_name": record["name"], "symbol": primary["symbol"],
            "symbol_kind": primary["kind"],
            "symbol_month_stage": primary["symbol_month_stage"],
            "symbol_palace_relation": primary["nominal_relation_from_symbol"],
            "symbol_strength": primary["strength_label"],
            "palace_month_stage": primary["palace_month_stage"],
            "palace_strength": primary["palace_strength_label"],
            "source_factor_id": primary["fact_id"],
            "all_factors": record["all_symbol_strength_25"],
            "life_stage_sky": record["heaven"],
            "life_stage_earth": record["earth_life"],
            "void_branches": record["void_branches"],
            "sky_tombs": record["sky_tombs"],
            "earth_tombs": record["earth_tombs"],
            "striking_stems": record["striking_stems"],
            "door_pressure": record["door_pressure"],
            "eligible_as_independent_verdict_vote": False,
        }
    if natal is None:
        nodes["natal"] = {
            "id": "natal", "label": "患者年命",
            "present": False, "role_status": "not_supplied_or_unbound",
            "note": "未提供真实完整出生干支，或天干没有按既有起盘法核定落宫，不造年命盘",
            "eligible_as_independent_verdict_vote": False,
        }
    else:
        nodes["natal"]["source_birth_ganzhi"] = (
            inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi"))

    facts = {key: record for key, record, _ in role_rows}
    edges = {}
    physical_first = {}
    for from_key, to_key in permutations(facts, 2):
        a, b = facts[from_key], facts[to_key]
        compared = compare_full_factors(
            a["primary_strength_25"], b["primary_strength_25"],
            actor_name=a["role"], target_name=b["role"])
        pid = (a["palace"], b["palace"])
        if pid not in physical_first:
            physical_first[pid] = from_key+"->"+to_key
        edge_id = from_key+"->"+to_key
        edges[edge_id] = {
            "id": edge_id, "actor": from_key, "target": to_key,
            "actor_palace": a["palace"], "target_palace": b["palace"],
            "same_physical_palace": a["palace"] == b["palace"],
            "physical_pair_id": str(a["palace"])+"->"+str(b["palace"]),
            "same_physical_pair_already_seen": physical_first[pid] != edge_id,
            "first_physical_pair_edge": physical_first[pid],
            "verdict_vote_added": False,
            **compared,
        }

    focus = {}
    # Every meaningful role must be compared against BOTH disease and person.
    for label in ("doctor", "medicine", "patient", "hour", "natal",
                  "qian", "kun", *(k for k in facts if k.startswith("extra_"))):
        if label not in facts:
            continue
        focus[label] = {
            target: edges[label+"->"+target]
            for target in ("illness", "patient")
            if target != label
        }
    return {
        "schema": "full_health_role_energy_network_vnext_1",
        "nodes": nodes, "directed_edges": edges,
        "focus_against_disease_and_patient": focus,
        "physical_palace_pair_count": len(physical_first),
        "role_pair_count": len(edges),
        "role_gating_applied": True,
        "all_9_palace_symbols_recomputed": False,
        "qian_and_kun_always_observed": True,
        "missing_natal_not_fabricated": natal is None,
        "strengths_are_research_hypotheses": True,
        "added_independent_verdict_votes": 0,
        "clinical_prediction": False,
    }


def format_health_network_summary(network):
    """Compact Chinese review sections; full directed graph remains in audit."""
    nodes = network["nodes"]
    links = network["focus_against_disease_and_patient"]

    def describe(key):
        node = nodes[key]
        head = (node["label"]+"落"+node["palace_name"]+
                "，主符号"+node["symbol"]+"月令"+
                (str(node["symbol_month_stage"]) if node["symbol_month_stage"] else "不单算")+
                "，力量"+node["symbol_strength"]+"，宫月令"+
                node["palace_month_stage"]+"、宫力"+node["palace_strength"]+
                "；门、星、神及天地干均已分别计算")
        endings = []
        for target, edge in links.get(key, {}).items():
            goal = "病宫" if target == "illness" else "患者宫"
            endings.append("对"+goal+edge["relation"]+
                           "（制约："+edge["ability_to_control"]+"）")
        if endings:
            head += "；"+"，".join(endings)
        return head+"。"

    parts = []
    if nodes["natal"]["present"]:
        parts.append(describe("natal"))
    else:
        parts.append("患者年命未提供或未能核定落宫，不补造年命，只依据真实已知用神。")
    parts.append(describe("hour"))
    for key, name in (("qian", "乾宫"), ("kun", "坤宫")):
        node = nodes[key]
        part = describe(key)
        if node["role_status"] == "physical_palace_observation_only":
            part += "此宫仅为真实盘面观察，尚不能当作患者个人用神。"
        elif node["role_status"] == "sex_correspondence_candidate_unverified":
            part += "按实际性别属于候选辅助宫，仍须结合该问事原书取用依据。"
        else:
            part += "已符合人物参考宫配置，但不单凭这一宫下病吉凶。"
        parts.append(part)
    return " ".join(parts)
