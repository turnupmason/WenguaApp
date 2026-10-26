"""Wengua illness severity research v-next: full facts *inside* selected palaces.

Nine-palace casting is upstream and immutable. All factor strengths are exact
user 8x25 v3 table lookups (apart from god, whose user rule deliberately has
no month stage). This module adds no V4.2 score, no invented clinical validity,
no new five-elements or undisclosed additional 'palace power duel'.
"""
from __future__ import annotations

from .factor_energy_review import DEITY_ELEMENTS, _directed_relation
from .health_severity_template import MONTH_ELEMENTS
from .health_severity_v34 import HORSE
from .marriage_runtime import PALACE_BRANCHES
from .semantic_lookup import GENERATES
from .selected_duel_table_vnext import table_one
from .health_five_level_quant_vnext import door_break_penalty_policy
from .health_81_excel_catalog_vnext import for_real_palace

GOOD_GODS=frozenset(("值符","六合","太阴","九天"))
BAD_GODS=frozenset(("白虎","玄武","螣蛇","腾蛇","九地"))
# Normalize aliases without altering the source term in the chart.
GOD_DISPLAY_REL={
    "宫生符号":"被宫生","宫克符号":"被宫克",
    "符号克宫":"克宫","符号生宫":"生宫","比和":"比和",
}
# Only the first two are user-specified strengthening, other three weaken;
# not all favourable signs become unlucky and vice versa.
GOD_SUPPORTED=frozenset(("宫生符号","比和"))
# Opposing branch-pairs are a complete involutive 6-冲, not a text guess.
BRANCH_CLASH={"子":"午","午":"子","丑":"未","未":"丑",
              "寅":"申","申":"寅","卯":"酉","酉":"卯",
              "辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
assert all(BRANCH_CLASH[BRANCH_CLASH[x]]==x for x in BRANCH_CLASH)


def inspect_role_void(*,palace,occupied_void_branches,month_branch,hour_ganzhi):
    """Latest user: 空宫马星同宫为假空；对宫冲空旧法可冲开；月令生/比假空，其余真空.

    The horse must have an actual mapped branch/palace. Opposite position is
    checked by *actual* branch clash; geometric diagonal alone is insufficient
    when the stem/branch relationship is not evidenced.
    """
    from .marriage_runtime import ELEMENTS
    empties=tuple(occupied_void_branches)
    horse_branch=HORSE[hour_ganzhi[1]]
    horse_palaces=tuple(p for p,branches in PALACE_BRANCHES.items()
                        if horse_branch in branches)
    if len(horse_palaces)!=1:raise AssertionError("Actual horse branch needs one palace")
    if not empties:
        return {"classification":"not_void","void_branches":[],
                "horse_branch":horse_branch,"horse_palace":horse_palaces[0],
                "month_support":False,"horse_clashes_void":False,
                "had_xun_void":False,"horse_cleared_void":False,
                "horse_same_palace_void":False,
                "reasons":[],"rule":"user_20261025_void_horse_same_palace_fake_v3"}
    pe=ELEMENTS[palace]
    me=MONTH_ELEMENTS[month_branch]
    from_month=(me==pe or GENERATES[me]==pe)
    opposite=any(BRANCH_CLASH[b]==horse_branch for b in empties)
    same_palace=horse_palaces[0]==palace
    # Latest user amendment supersedes earlier "horse makes fake void":
    # a verified opposite horse breaks/cancels the void first; ONLY if
    # there is no horse can month support make the remaining void 假空.
    if same_palace:
        klass="fake_void"
        flags=["马星与旬空处于同一真实宫：假空"]
    elif opposite:
        klass="not_void"
        flags=["马星与逢空宫实际地支相冲：冲空后不按逢空处理"]
    elif from_month:
        klass="fake_void"
        flags=["逢空且落宫受月令生扶或比和：假空"]
    else:
        klass="true_void"
        flags=["逢空且无同宫马星、对宫冲空或月令生扶：真空"]
    return {"classification":klass,"void_branches":list(empties),
            "had_xun_void":True,"horse_cleared_void":opposite,
            "horse_branch":horse_branch,"horse_palace":horse_palaces[0],
            "month_support":from_month,"horse_clashes_void":opposite,
            "horse_same_palace_void":same_palace,
            "reasons":flags,
            "rule":"user_20261024_void_horse_cancels_first_v2"}


def inspect_god(*,deity,palace_element):
    """Five intrinsic god-to-palace relations; NO fabricated monthly stage."""
    if not deity:
        return {"status":"no_god","name":None,"month_stage":None,
                "relation":None,"polarity":"pending","strength_effect":"未核"}
    if deity not in DEITY_ELEMENTS:
        return {"status":"unknown","name":deity,"month_stage":None,
                "relation":None,"polarity":"pending","strength_effect":"未核"}
    nominal=_directed_relation(DEITY_ELEMENTS[deity],palace_element)
    strength="增强" if nominal in GOD_SUPPORTED else "减弱"
    auspicious=deity in GOOD_GODS
    inauspicious=deity in BAD_GODS
    polarity=(("更吉" if strength=="增强" else "微吉") if auspicious else
              ("更凶" if strength=="增强" else "微凶") if inauspicious else
              "待核")
    return {
        "status":"calculated","name":deity,"symbol_element":DEITY_ELEMENTS[deity],
        "month_stage":None,"nominal_relation":nominal,
        "relation":GOD_DISPLAY_REL[nominal],
        "strength_effect":strength,"polarity":polarity,
        "auspicious":auspicious,"inauspicious":inauspicious,
        "kind":"deity_no_month_stage_five_relation",
        "not_independent_outcome_vote":True,
    }


def normalize_new_door_relation(*,record,cell,month_branch):
    """Only V-next: remap old source's `迫=门克宫` to NEW USER two columns.

    The original source fact remains `legacy_door_pressure` for audit.
    The user defined 宫迫 as 宫克门, 门破 as 门克宫; do not let legacy
    `门迫` accidentally create a second adverse restriction on the two
    explicitly exempted special real palace/door combinations.
    Never change inspect_palace or frozen V3.9.1 semantics.
    """
    door=cell["door"]
    if door is None:return record
    basic=table_one("door",door,month_branch,cell["palace"])
    relation=basic["user_cell_col"]
    return {**record,
            "legacy_door_pressure":record.get("legacy_door_pressure",record["door_pressure"]),
            "door_pressure":relation=="宫迫",
            "door_break":relation=="门破",
            "door_relation_user_200_cells":relation,
            "door_relation_normalized_to_user":True}


def inspect_complete_selected_palace(*,chart,cell,record,month_branch,
                                     matched_pairs=(),primary_factor=None):
    """All real resident chart objects in one chosen outer palace.

    One palace can contain Tianrui + Tianqin and several carried stems.
    Include BOTH sky and earth; keep exact 81-source matches with source gates.
    Role-specific primary strength is not double-counted against occupants.
    """
    record=normalize_new_door_relation(
        record=record,cell=cell,month_branch=month_branch)
    palace=cell["palace"]
    if palace==5:
        raise ValueError("Middle five needs book-specific method, no fake symbols")
    restrictions=tuple(dict.fromkeys(
        (["六仪击刑"] if record["striking_stems"] else [])+
        (["天盘入墓"] if record["sky_tombs"] else [])+
        (["地盘入墓"] if record["earth_tombs"] else [])+
        (["门迫"] if record["door_pressure"] else [])))
    void=inspect_role_void(
        palace=palace,occupied_void_branches=record["void_branches"],
        month_branch=month_branch,hour_ganzhi=chart["hour_ganzhi"])
    god=inspect_god(deity=cell["deity"],palace_element=record["element"])
    star_factors=[]
    for entry in cell["heaven_stars"]:
        star=entry["star"]
        star_factors.append({
            "name":star,"carried_stem":entry["carried_stem"],
            "strength":table_one("star",star,month_branch,palace,
                                 restrictions=restrictions)})
    door_factor=(table_one("door",cell["door"],month_branch,palace,
                           restrictions=restrictions) if cell["door"] else None)
    door_break=(door_break_penalty_policy(
        door_name=cell["door"],palace=palace,
        door_relation=door_factor["user_cell_col"])
        if door_factor else None)
    heaven=[]
    for entry in cell["heaven_stars"]:
        stem=entry["carried_stem"]
        heaven.append(table_one("stem",stem,month_branch,palace,
                                plane="heaven",restrictions=restrictions))
    earth=table_one("stem",cell["earth_stem"],month_branch,palace,
                    plane="earth",restrictions=restrictions)
    # The user's latest complete Excel has exactly one definitive name,
    # 81-pair 吉凶 and FOUR requested interpretations for each real pair.
    # Keep the historical review pairs in a separate audit field, never
    # overwrite source history or let its old gates silence the Excel result.
    pairs=for_real_palace(cell)
    historical_pairs=[
        {"fact_id":pair["fact_id"],"name":pair["book_title"],
         "heaven":pair["heaven"],"earth":pair["earth"],
         "source_state":pair["source_state"],
         "source_conditions":pair.get("source_gate_flags",()),
         "source_line_internal":pair.get("source_line_internal"),
         "source_sha256_internal":pair.get("source_sha256_internal")}
        for pair in matched_pairs
        if pair["palace"]==palace and
           any(entry["star"]==pair["star"] and
               entry["carried_stem"]==pair["heaven"] and
               cell["earth_stem"]==pair["earth"]
               for entry in cell["heaven_stars"])
    ]
    historical_by_pair={(x["heaven"],x["earth"]):x
                        for x in historical_pairs}
    for excel_pair in pairs:
        historical=historical_by_pair.get(
            (excel_pair["heaven"],excel_pair["earth"]),{})
        # Compatibility-only provenance: Excel still defines the FOUR
        # current user-facing descriptions and 吉凶; previous book SHA
        # remains available for archival scripts, not conditional gating.
        excel_pair["source_line_internal"]=historical.get(
            "source_line_internal",excel_pair["source_excel_row"])
        excel_pair["source_sha256_internal"]=historical.get(
            "source_sha256_internal",
            "662c6ad43272367acf034e2c65758dffd783c815734e40ad76fdb58a77d95336")
        excel_pair["historical_source_state"]=historical.get("source_state")

    return {
        "schema":"health_complete_selected_palace_v1",
        "palace":palace,"role":record["role"],"palace_name":record["name"],
        "palace_element":record["element"],
        "palace_month_stage":record["palace_month_stage"],
        "stars":star_factors,"deity":god,"door":door_factor,
        "door_break_penalty_policy":door_break,
        "heaven_stems":heaven,"earth_stem":earth,
        "primary_strength":primary_factor,
        "ordered_book_81_pairs":pairs,
        "historical_book_81_audit":historical_pairs,
        "user_excel_81_is_authoritative":True,
        "void":void,"horse_branch":void["horse_branch"],
        "horse_in_this_palace":void["horse_palace"]==palace,
        "sky_tombs":record["sky_tombs"],
        "earth_tombs":record["earth_tombs"],
        "striking_stems":record["striking_stems"],
        "door_pressure":record["door_pressure"],
        "five_levels_are_source_hypotheses":True,
        "medical_diagnosis":False,
    }


def void_kwargs(actor_detail,target_detail):
    """Exactly one source/target fake/true selection for an actual 克 edge."""
    a=actor_detail["void"]["classification"]
    b=target_detail["void"]["classification"]
    return {"attacker_fake_void":a=="fake_void",
            "target_fake_void":b=="fake_void",
            "attacker_true_void":a=="true_void",
            "target_true_void":b=="true_void"}


def render_complete_selected_palace(detail, *, quantified=None):
    """Output signed current star/door/god/palace tiers from real scoring audit.

    Heavenly and earthly stem 200-cell grades express strength, not automatically
    auspiciousness. No invented score for an unresolved source/lifecycle branch.
    """
    from .health_five_level_quant_vnext import label as signed_grade
    from .health_intrinsic_scoring_vnext import star_score

    def signed(score):
        if score is None:
            return "吉凶待核"
        return ("中平" if score == 0 else signed_grade(score).replace("中等吉","中吉").replace("中等凶","中凶"))

    def stem_strength(x):
        if x is None:
            return "无"
        if x["strength_label"] is not None:
            return str(x["symbol"])+"势"+str(x["strength_label"])
        choices=x.get("stem_life_candidate_cells",())
        return (str(x["symbol"])+"长生分支待核（"+
                "／".join(str(y["row"])+"势"+str(y["strength"])
                         for y in choices)+"）")

    stars="、".join(
        x["name"]+signed(star_score(
            x["name"],x["strength"].get("strength_label"))["score"])
        for x in detail["stars"] if x["name"]!="天禽星") or "无已核星"
    d=detail["deity"]
    deity=(d["name"]+d["relation"]+"、"+
           signed(quantified["deity"].get("score"))
           if quantified is not None and d["status"]=="calculated"
           else "未核")
    door=detail["door"]
    door_text=(door["symbol"]+signed(quantified["door"].get("score"))
               if door and quantified is not None else "门势待核")
    # In the real Tianrui + Tianqin co-hosted palace, Tianqin and the
    # carried stem/order-81 pair belonging to Tianqin are not illness evidence.
    disease_star=next((x for x in detail["stars"]
                       if x["name"]=="天芮星"),None)
    disease_stem=(disease_star.get("carried_stem")
                  if disease_star else None)
    kept_stems=([x for x in detail["heaven_stems"]
                 if x["symbol"]==disease_stem]
                if disease_stem else detail["heaven_stems"])
    top="、".join(stem_strength(x) for x in kept_stems) or "无"
    bottom=stem_strength(detail["earth_stem"])
    book=detail["ordered_book_81_pairs"]
    if disease_stem:
        book=[p for p in book if p["heaven"]==disease_stem]
    from .health_reading_template_vnext import formation_sentence
    booktext=("；天地格："+ "；".join(formation_sentence(pair)
        for pair in book) if book else "；本宫没有实际天地盘有序格")
    v=detail["void"]
    vt=("不空" if v["classification"]=="not_void" else
        "假空" if v["classification"]=="fake_void" else "真空")
    door_break=detail.get("door_break_penalty_policy")
    conditions="、".join(
        x for x,active in (("门破",bool(
                                door_break and door_break["has_door_break"])),
                           ("天盘入墓",bool(detail["sky_tombs"])),
                           ("地盘入墓",bool(detail["earth_tombs"])),
                           ("六仪击刑",bool(detail["striking_stems"])),
                           ("门迫",bool(detail["door_pressure"])),
                           ("本宫驿马",detail["horse_in_this_palace"]))
        if active) or "无已核特殊刑墓迫"
    palace=quantified["palace_score"] if quantified is not None else None
    final=("全部因素推断后，此宫为"+signed(palace.get("score"))+"。"
           if palace is not None else "")
    if door_break and door_break.get("has_door_break"):
        conditions+="。八门压制宫力量，吉事不吉，凶事更凶"
    return ("落"+detail["palace_name"]+"；九星"+stars+"；八神"+deity+
            "；八门"+door_text+"；天盘干"+top+
            "、地盘干"+bottom+booktext+"；空亡"+vt+
            "；"+conditions+"。"+final)
