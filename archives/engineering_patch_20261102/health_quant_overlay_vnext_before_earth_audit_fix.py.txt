"""2026-10-24 current user classification: signed real palace star/door/god/pattern.

Every real resident star contributes; god follows five palace relationships
WITHOUT month, and neutral Du/Jing doors contribute explicit zero. Exact
source-specific 81 stem-pair exceptions, two-branch life uncertainty and
unknown final >5 grade bands are audit-gated. Frozen V3.9.1 is untouched.
"""
from __future__ import annotations

from .health_five_level_quant_vnext import (
    points,palace_tally,multi_palace_tally,pattern_grade,VERSION,
    door_break_penalty_policy)

from .health_intrinsic_scoring_vnext import (
    star_score,door_score,god_score,resolve_ordered_pair,
    stem_intrinsic_score,catalog_validation,VERSION as INTRINSIC_VERSION)
from .health_five_level_quant_vnext import label as grade_label, saturate, adverse_shift, void_shift_three
from .health_81_excel_catalog_vnext import (
    authoritative_score_source,catalog,VERSION as EXCEL_VERSION)

def _matching_restriction(entries,stem):
    """Only a genuinely explicit stem-labelled source fact matches."""
    for item in entries:
        if isinstance(item,dict):
            label=item.get("stem") or item.get("heaven_stem") or item.get("earth_stem")
            if label==stem:return True
        elif item==stem:return True
    return False


def _quantize_one(role,detail,*,five_not_encounter,xun_shou=None):
    """Score the four categories using user's latest exact symbolic rules.

    Four categories can contain multiple REAL stars or 81 pairs, but not
    multiple invented votes for a single chart source. Per factor baseline
    remains visible beside actual 200-cell strength.
    """
    if detail["palace"]==5:
        raise ValueError("No invented middle-five star/door/god")
    star_entries=[]
    for entry in detail["stars"]:
        st=entry["strength"]
        # User's 2026-10-24 strict illness rule: 天芮 and its piggyback
        # 天禽 appear together in real chart, but only 天芮 contributes to
        # illness-severity points. Keep Tianqin as a raw chart fact.
        if role=="illness" and entry["name"]!="天芮星":
            star_entries.append({
                "symbol":entry["name"],"baseline":None,"score":None,
                "status":"real_cohost_not_health_signifier",
                "not_scored_in_illness":True,
                "carried_stem":entry.get("carried_stem")})
        else:
            star_entries.append(star_score(entry["name"],st.get("strength_label")))
    scored_stars=[x for x in star_entries if not x.get("not_scored_in_illness")]
    valid_stars=[x["score"] for x in scored_stars if x.get("score") is not None]
    star_values=(valid_stars[0] if len(valid_stars)==1
                 else valid_stars if len(valid_stars)>1 else None)
    if len(valid_stars)!=len(scored_stars):star_values=None
    star_audit={
        "status":"calculated" if star_values is not None else "some_real_star_strength_pending",
        "per_star":star_entries,
        "score":sum(valid_stars) if star_values is not None else None,
        "intrinsic_baselines":[v.get("baseline") for v in star_entries],
        "co_palace_source_stars_not_silenced":True,
        "illness_tianrui_only":role=="illness",
        "excluded_real_stars":[x["symbol"] for x in star_entries
                               if x.get("not_scored_in_illness")],
        "user_rule_version":INTRINSIC_VERSION,
        "polarity":next((x["polarity"] for x in star_entries if
                         x.get("polarity") is not None),None),
    }
    door=detail["door"]
    door_policy=(door_break_penalty_policy(
        door_name=door["symbol"],palace=detail["palace"],
        door_relation=door["user_cell_col"])
        if door else None)
    door_out=(door_score(door["symbol"],door.get("strength_label"))
              if door else {"status":"no_real_door","score":None})
    door_audit={**door_out,"symbol":door["symbol"] if door else None,
        "strength":door.get("strength_label") if door else None,
        "symbol_palace_relation":door.get("user_cell_col") if door else None,
        "penalty_policy":door_policy,
        "applied_door_break_shift":door_policy["two_level_shift"] if door_policy else 0,
        "strength_lookup_unchanged":True,
        "neutral_door_is_known_zero":door_out.get("score")==0}
    deity=detail["deity"]
    god_audit=god_score(deity["name"],deity.get("nominal_relation"))
    god_audit.update({"auspice":deity["polarity"],"relation":deity["relation"],
        "month_stage_is_not_used":True,
        "intrinsic_polarity_is_user_explicit":True})
    earth=detail["earth_stem"]
    ordinary_bottom=earth["symbol"] if earth else None
    hosted_bottom=detail.get("hosted_centre_earth_stem")
    heaven={x["symbol"]:x for x in detail["heaven_stems"]}
    # Explicitly approved disease-only Tianrui+Tianqin exception:
    # Tianqin star itself is NOT a second illness source, but EACH distinct
    # real carrier forms its own ordered heaven/earth 81 pattern.
    illness_top_stems={
        e["carried_stem"] for e in detail["stars"] if e.get("carried_stem")}
    skipped_health_cohosts=[]
    origin={(p["heaven"],p["earth"]):p
            for p in detail["ordered_book_81_pairs"]}
    pairs=[]
    # Kun-2 may have two real source-81 pairs for one real sky stem.
    # Never collapse by a dict keyed only on the heavenly stem.
    for source_pair in detail["ordered_book_81_pairs"]:
        top,bottom=source_pair["heaven"],source_pair["earth"]
        stem_fact=heaven.get(top)
        if stem_fact is None:continue
        if role=="illness" and top not in illness_top_stems:
            skipped_health_cohosts.append(top)
            continue
        if not bottom:continue
        # Current 81 classification is user Excel, NOT the older 82-record
        # condition-gated book/health conflict corpus. Old records remain
        # separately auditable but no longer silence known Excel 吉/凶.
        candidate=authoritative_score_source(top,bottom)
        stages=[s["stage"] for s in stem_fact.get("palace_twelve_life_facts",())
                if s.get("stage")]
        if not stages: stages=None
        # Restriction facts must identify the SPECIFIC original stem; don't
        # charge another cohost's tomb twice.
        heavenly_tomb=_matching_restriction(detail.get("sky_tombs",()),top)
        earthly_tomb=_matching_restriction(detail.get("earth_tombs",()),bottom)
        heaven_penalty=_matching_restriction(detail.get("striking_stems",()),top)
        earth_penalty=_matching_restriction(detail.get("striking_stems",()),bottom)
        actual_source=origin.get((top,bottom))
        polarity=candidate.get("polarity")
        gate_ok=candidate["status"]=="user_excel_exact_81"
        if polarity in ("吉","凶"):
            graded=pattern_grade(
                polarity=polarity,heaven_stage=stages,
                heaven_tomb=heavenly_tomb,earth_tomb=earthly_tomb,
                heaven_punishment=heaven_penalty,earth_punishment=earth_penalty,
                source_gate_verified=gate_ok)
        else:
            graded={"status":"source_polarity_or_context_pending","score":None}
        pairs.append({
            "key":candidate["key"],"name":candidate["excel_original"]["name"],
            "polarity":candidate["polarity"],
            "classical_text":candidate["excel_original"]["classical_text"],
            "classical_meaning":candidate["excel_original"]["classical_meaning"],
            "imagery":candidate["excel_original"]["imagery"],
            "excel_version":EXCEL_VERSION,
            "excel_row":candidate["excel_original"]["source_excel_row"],
            "source_rule":candidate,
            "actual_book_source":actual_source,
            "heaven_lifecycle":stages,
            "grade":graded,
            "score":graded.get("score"),
            "status":graded.get("status"),
            "book_illness_conflict":False,
            "user_excel_authoritative":True,
            "no_invented_author_outcome":True,
        })
    applied=[p["score"] for p in pairs if p["score"] is not None]
    # All 81 user declarations remain visible. A non-triggered additional
    # pattern condition is not a reason to withhold already measured star,
    # door, god and other *qualified* patterns: this one contributes zero.
    # Keep the original candidates, gates and provenance for source audit.
    # Retain each actual ordered sky/earth pattern's +/-1..5 component.
    # Several real cohost stems may produce an aggregate >5, which is
    # legitimate raw palace arithmetic but NOT a single five-tier factor.
    pattern_score=(applied if len(applied)>1 else
                   applied[0] if len(applied)==1 else 0)
    pattern_audit={
        "status":("calculated" if len(applied)==len(pairs)
                  else "nontriggered_patterns_excluded_from_current_score"),
        "matches":pairs,
        "score":sum(applied),
        "excluded_patterns_not_assumed_true":len(pairs)-len(applied),
        "pending":[p["key"] for p in pairs if p["score"] is None],
        "explicit_81_coverage":{
            "expected_pair_positions":81,
            "distinct_declared_pairs":len(catalog()),
            "source_version":EXCEL_VERSION,
            "classification":"Excel user explicit all 81",
            "previous_82_row_source_historical_only":True},
        "default_tier":"中等","base_per_user_pattern":3,
        "preserve_book_source_conditions":"historical_archive_only",
        "latest_user_excel_is_authoritative":True,
        "disease_dual_carrier_81_exception":role=="illness",
        "only_tianrui_carried_stem_if_illness":False,
        "skipped_cohost_heaven_stems":skipped_health_cohosts}
    summary=palace_tally(
        factors={"star":star_values,
                 "door":door_out["score"],
                 "deity":god_audit.get("score"),
                 "pattern":pattern_score},
        door_break=bool(door_policy and door_policy["apply_extra_two_level_shift"]),
        five_not_encounter=bool(five_not_encounter),
        void_state=detail["void"]["classification"],
        horse_cleared_void=bool(detail["void"].get("horse_cleared_void")))
    stem_audit={
        "heaven":[stem_intrinsic_score(x["symbol"]) for x in detail["heaven_stems"]],
        "earth":stem_intrinsic_score(bottom) if bottom else None,
        "jia_hidden_cycle":stem_intrinsic_score("甲",xun_shou=xun_shou)
                            if xun_shou else None,
        "not_doubled_on_four_categories":True}
    return {"role":role,"palace":detail["palace"],
            "star":star_audit,"door":door_audit,
            "deity":god_audit,"pattern":pattern_audit,
            "ten_stem_intrinsic":stem_audit,
            "real_heaven_stem_facts":detail["heaven_stems"],
            "real_earth_stem_fact":detail["earth_stem"],
            "palace_score":summary,
            "intrinsic_user_baselines_applied":True,
            "source_coverage":catalog_validation(),
            "scope":"user_candidate_health_severity_not_clinical"}


def independent_special_host(hosts,auspice_kind,auspice_symbol):
    """True only if at least one actual selected host is a DIFFERENT symbol.

    Physical identity is (kind, symbol), never the number of role aliases.
    A time stem 乙 is NOT its own 乙奇 host; if a different patient or
    illness signifier shares that seat, the same 乙 may qualify ONCE.
    """
    return any((host["kind"],host["symbol"]) !=
               (auspice_kind,auspice_symbol) for host in hosts)


def disease_dual_sky_bonus(star_carriers,stem_candidates,illness_host):
    """Only an ACTUAL Tianrui illness palace with two distinct qualifying
    sky-star carriers may sum two independently powered 乙/丁 auspice effects.
    A single symbol repeated through roles, or a sky+earth copy, cannot.
    Input carriers: [(star_name, carried_stem)], candidates:
    [(source_points, '<stem>奇', '天盘'|'地盘')].
    This is NOT a second physical-palace baseline or an 81 formation score.
    """
    if not illness_host:
        return None
    source_by_stem={}
    for star,stem in star_carriers:
        if star and stem:
            source_by_stem[stem]=star
    eligible={}
    for points,name,plane in stem_candidates:
        stem=name.removesuffix("奇")
        if plane!="天盘" or stem not in ("乙","丁"):
            continue
        star=source_by_stem.get(stem)
        if star:
            eligible[(star,stem)]=points
    if len({star for star,stem in eligible})<2:
        return None
    return sum(eligible.values())


def special_cohost_total(chief_points,stem_points,*,tianxin_points=0,
                         void=False,disease_dual_sky=False):
    """V7.2 real one-palace chief + earth/sky 奇: halve TOTAL, floor once."""
    stem_tiers=(0,1,2,3,4,5,6) if disease_dual_sky else (0,1,2,3)
    if chief_points not in (0,2,3) or stem_points not in stem_tiers:
        raise ValueError("Unknown same-palace auspice tier")
    if tianxin_points not in (0,2,3):
        raise ValueError("Unknown independent Tianxin bonus")
    total=chief_points+stem_points+tianxin_points
    return total//2 if void else total


# All inter-palace relations use the actually selected signifier's power;
# palace signed auspiciousness is never an actor or target strength.
from .selected_duel_table_vnext import CONTROL_CONFIDENT, CONTROL_LIMITED
_REAL_CONTROL_RESULTS=CONTROL_CONFIDENT | CONTROL_LIMITED

def special_disease_control_points(*,attacker_strength=None,target_strength=None,
                                   control_result=None,control_status=None,
                                   control_ability=None,attacker_void=False,
                                   attacker_controlled=False,illness_void=False,
                                   attacker_score=None):
    """Verified real user 5x5 strengths determine a qualified directed 克.

    The historical attacker_score argument is intentionally ignored; legacy
    callers cannot authorize credit by using abs(signed_palace_grade).
    """
    from .factor_energy_25_rules import TIERS
    if (attacker_strength not in TIERS or target_strength not in TIERS
            or control_status!="matched"
            or control_ability not in ("能","艰难")
            or control_result not in _REAL_CONTROL_RESULTS):
        return 0
    if attacker_void or attacker_controlled:
        return 1
    return 5 if illness_void else 3


def _role_score(item,primary,xun_shou):
    """Per-role signifier (source polarity x 200-cell) plus palace environment."""
    out=dict(item)
    p=item["palace_score"]
    kind=primary["kind"]
    info={"symbol":primary["symbol"],"kind":kind,
          "tier":primary.get("strength_label"),"included_in_resident":kind!="stem"}
    if kind=="stem":
        baseline=stem_intrinsic_score(primary["symbol"],xun_shou=xun_shou).get("baseline")
        tier=primary.get("strength_label")
        own=(None if baseline is None or (baseline and tier is None)
             else 0 if baseline==0 else points(tier,"吉" if baseline>0 else "凶"))
        # V7.9: 81 天地格 strength already depends on the real sky stem.
        # Keep its own 200-cell strength in audit, but do NOT add it to the
        # same palace again; nor count it once per hour/natal/medicine alias.
        info.update(score=own,baseline=baseline,
                    audit_only_not_added_on_top_of_81=True)
    else:
        info["score"]=(item["deity"]["score"] if kind=="deity" else next(
            (x["score"] for x in item["star"]["per_star"]
             if x["symbol"]==primary["symbol"]),None))
    out["primary_signifier_score"]=info
    return out


def inspect_selected_quantization(*,selected_roles,
                                  qian_kun_observations,first_stage_macro,
                                  xun_shou=None,selected_gender_palace=None,directed_edges=None):
    """Do not count same real palace twice in numeric summary."""
    five=first_stage_macro["five_not_encounter_triggered"]
    roles={}
    aggregate={}
    physical_cache={}
    for key,row in selected_roles.items():
        if key in (
                "illness","doctor","medicine","patient",
                "hour","natal","gender","chief","sibling"):
            detail=row["complete_palace"]
            palace=detail["palace"]
            item=_role_score(_quantize_one(
                key,detail,five_not_encounter=False,xun_shou=xun_shou),
                row["primary_strength_25"],xun_shou)
            if palace not in physical_cache:
                physical_cache[palace]={"role":key,"item":item}
            roles[key]=item
            # User: ONLY the exact selected health roles. No unrelated extra
            # palace inferred through a generic family/profile traversal.
            # Shared physical palaces are collapsed by multi_palace_tally.
            aggregate[key]={"palace":item["palace"],
                            "score":item["palace_score"]["score"],
                            "raw_sum":item["palace_score"]["raw_sum"],
                            "known_subtotal":item["palace_score"]["known_subtotal"]}
    qian_kun={}
    for k,row in qian_kun_observations.items():
        palace=row["palace"]
        if palace in physical_cache:
            canonical=physical_cache[palace]
            qian_kun[k]={**canonical["item"],"role":k,
                          "score_shared_with_role":canonical["role"],
                          "same_real_palace_same_score":True}
        else:
            qian_kun[k]=_quantize_one(
                k,row["complete_palace"],five_not_encounter=False,
                xun_shou=xun_shou)
            physical_cache[palace]={"role":k,"item":qian_kun[k]}
        qian_kun[k]["auxiliary_only_not_auto_counted"]=True
        qian_kun[k]["selected_if_patient_gender_known"]=(
            row["palace"]==selected_gender_palace)
    # Do not add the unselected Qian/Kun auxiliary to the final aggregate.
    # When gender is supplied, its one real selected palace is already
    # counted under the "gender" role. No sex means neither is added.
    # Both unselected technical observations remain in audit for provenance.
    # Existing authoritative source-grid control result is the permission
    # gate, not a second invented energy table. The illness palace remains.
    # A nominal 克 with a failed/unknown real 5x5 source cell does not count
    # as independently effective assistance. 值符 is stricter: it is zero
    # unless it truly 克病, is not void, and its actual control is effective.
    # When another legitimate role occupies the same palace, that role can
    # still bring the single physical palace into the total exactly once.
    accepted={"能","艰难"}
    gates={}
    effective={}
    for key,row in selected_roles.items():
        if key not in roles:continue
        pid=row["palace"]
        edge=(directed_edges or {}).get(key+"->illness")
        rel=edge.get("relation") if edge else ("病宫本体" if key=="illness" else None)
        void=row["complete_palace"]["void"]["classification"]
        ability=edge.get("ability") if edge else None
        scenario=edge.get("control_scenario") if edge else None
        outcome=edge.get("control_result") if edge else None
        is_control=rel=="克"
        chief=key=="chief"
        chief_cohost=(chief and pid==selected_roles["illness"]["palace"])
        # Every role keeps its OWN selected power and original source edge.
        active=(key=="illness" or chief_cohost or not is_control or
                (edge is not None and edge.get("control_status")=="matched"
                 and ability in accepted and outcome in _REAL_CONTROL_RESULTS))
        reason=("病宫自身"
                if key=="illness" else
                "值符与天芮同宫，大吉神护持在同宫起作用"
                if chief_cohost else
                "值符空亡，不提供护持" if chief and void!="not_void" else
                "值符受病宫克，不能压制病宫" if chief and rel=="被克" else
                "值符没有克病方向，不作为制病护持" if chief and not is_control else
                "克制矩阵"+str(outcome or "未核定")+"，未形成有效克制"
                if not active and is_control else
                "克病能力："+str(outcome) if is_control else
                "非克制方向，按原宫位象意计入")
        gates[key]={"palace":pid,"relation":rel,
                    "actor_strength":row["primary_strength_25"].get("strength_label"),
                    "disease_strength":selected_roles["illness"]["primary_strength_25"].get("strength_label"),
                    "control_result":outcome,
                    "control_status":edge.get("control_status") if edge else None,
                    "control_scenario":scenario,
                    "control_ability":ability,"void":void,
                    "score_eligible":active,"reason":reason,
                    "chief_zero_score":chief and not active}
        # All selected real palaces contribute intrinsic state once; only
        # extra *control assistance* is gated by effective suppression.
        effective[key]=aggregate[key]
    # V7.7: every physical palace and every distinct selected stem ONE time.
    grouped={}
    for key,item in roles.items():
        pid=item["palace"]
        group=grouped.setdefault(pid,{"roles":[],"stems":{}})
        group["roles"].append(key)
        own=item["primary_signifier_score"]
        if own["kind"]=="stem":
            group["stems"].setdefault(own["symbol"],own["score"])
    for pid,group in grouped.items():
        first=group["roles"][0]
        canonical=_quantize_one(first,selected_roles[first]["complete_palace"],
                                five_not_encounter=False,xun_shou=xun_shou)
        base=canonical["palace_score"]
        # Every source 81格 already uses its REAL heaven stem strength.
        # Do not add those selected stem intrinsic scores a second time.
        merged={**base,
                "unique_stem_scores":{stem:0 for stem in group["stems"]},
                "excluded_duplicate_stem_audit":dict(group["stems"]),
                "heaven_stem_strength_applied_in_81_only":True}
        for key in group["roles"]:
            # The first role's resident source facts define the physical
            # palace, not a second cohost interpretation of the same seat.
            for factor in ("star","door","deity","pattern"):
                roles[key][factor]=canonical[factor]
            roles[key]["palace_score"]=merged
            roles[key]["shared_palace_roles"]=group["roles"]
            effective[key]={"palace":pid,"score":merged["score"],
                            "raw_sum":merged["raw_sum"],
                            "known_subtotal":merged["known_subtotal"]}
    summary=multi_palace_tally(palaces=effective)
    role_scores={key:record["palace_score"]["score"] for key,record in roles.items()}
    pending_roles=[key for key,value in role_scores.items() if value is None]
    role_sum=sum(value for value in role_scores.values() if value is not None)
    previous_physical=dict(summary)
    # V7 USER CONDITIONAL RULES, private-only points. Source 200/81 table
    # scores and every real palace remain unchanged. Distinct physical
    # control palaces and distinct auspicious symbols are counted once each.
    # A weak/void attacker does not get a normal +3 just for nominal 克.
    illness_pid=selected_roles["illness"]["palace"]
    illness_detail=selected_roles["illness"]["complete_palace"]
    illness_void=illness_detail["void"]["classification"]!="not_void"
    weak_disease=(selected_roles["illness"]["primary_strength_25"]
                  .get("strength_label")=="极小")
    control_roles={"doctor","medicine","patient","hour","natal","chief","gender","sibling"}
    control={}
    control_points={}
    drain={}
    for key,row in selected_roles.items():
        if key=="illness":continue
        gate=gates.get(key)
        if gate is None:continue
        pid=gate["palace"]
        if pid==illness_pid:continue
        if key in control_roles and gate["relation"]=="克":
            # Actual primary factor per role, not the signed palace grade.
            nominal=row["primary_strength_25"].get("user_cell_col")
            symbol_controlled=nominal in ("宫克符号","被宫克")
            edge=(directed_edges or {}).get(key+"->illness") or {}
            points=special_disease_control_points(
                attacker_strength=gate["actor_strength"],
                target_strength=gate["disease_strength"],
                control_result=edge.get("control_result"),
                control_status=edge.get("control_status"),
                control_ability=gate["control_ability"],
                attacker_void=gate["void"]!="not_void",
                attacker_controlled=symbol_controlled,
                illness_void=illness_void)
            if points:
                control.setdefault(pid,[]).append(key)
                control_points[str(pid)]=max(control_points.get(str(pid),0),points)
        # Preserve prior V6 weak illness actively draining into other roles.
        if (weak_disease and gate["relation"]=="被生"
                and gate["actor_strength"] in ("极小","小","中等","大","极大")
                and gate["disease_strength"] in ("极小","小","中等","大","极大")):
            # Previously recorded weak-Tianrui drain condition; require BOTH
            # independently selected 200-cell strengths to be resolved.
            # Do not invent a 生 matrix or use signed palace auspiciousness.
            if key!="chief" or gate["void"]=="not_void":
                drain.setdefault(pid,[]).append(key)

    # V7.2 co-palace rule: one physical palace once; sky/earth 乙/丁 are ONE
    # auspicious stem family per palace. A chief-deity and that family are
    # separate eligible components. Void halves their COMBINED subtotal,
    # flooring only once (6->3, 5->2, 4->2, 3->1).
    # Independent sky/door/star/deity/81 factors remain untouched.
    # V7.9: a selected physical host must be a DIFFERENT actual symbol
    # from the source of the auspice. Same 乙 used as time/natal/medicine
    # is only one symbol, not an independent host that meets itself.
    auspice_hosts={"illness","patient","hour","natal","gender","sibling"}
    host_palaces={}
    host_signifiers={}
    for key,row in selected_roles.items():
        if key in auspice_hosts:
            pid=row["palace"]
            host_palaces.setdefault(pid,row["complete_palace"])
            primary=row["primary_strength_25"]
            host_signifiers.setdefault(pid,[]).append({
                "role":key,"kind":primary["kind"],
                "symbol":primary["symbol"]})
    auspice={}
    cohost_audit={}
    high_ground_stages={"长生","沐浴","冠带","临官","帝旺"}
    from .health_intrinsic_scoring_vnext import GOD_RELATIONS
    for pid,detail in sorted(host_palaces.items()):
        label=detail["palace_name"]
        hosts=host_signifiers[pid]
        is_void=detail["void"]["classification"]!="not_void"
        sky_tombs={x["stem"] for x in detail.get("sky_tombs",())}
        strikes=set(detail.get("striking_stems",()))
        sky_candidates=[]
        for x in detail["heaven_stems"]:
            stem=x["symbol"]
            if (stem in ("乙","丁") and
                    independent_special_host(hosts,"stem",stem)):
                sky_candidates.append((stem,x.get("strength_label"),
                                       stem in sky_tombs or stem in strikes))
        ground=detail.get("earth_stem") or {}
        ground_stem=ground.get("symbol")
        ground_stages=[x.get("stage") for x in
            ground.get("palace_twelve_life_facts",()) if x.get("stage")]
        # earth_tombs from inspect_palace is BRANCHES (e.g. 戌), whereas
        # _matching_restriction requires an explicit STEM label. The actual
        # earth-stem full12 lifecycle already records 墓 at this palace.
        # Match that real fact rather than treating a branch as a stem.
        # Swift p.tombs has plane='地盘', stem='乙' for the same event.
        ground_restricted=("墓" in ground_stages or
                           _matching_restriction(
                               detail.get("earth_tombs",()),ground_stem) or
                           ground_stem in strikes)
        stem_candidates=[]
        for stem,strength,restricted in sky_candidates:
            if not strength and not restricted:continue
            tier=1 if restricted else 2 if strength=="极小" else 3
            stem_candidates.append((tier,stem+"奇","天盘"))
        if (ground_stem in ("乙","丁") and
                independent_special_host(hosts,"stem",ground_stem)):
            gstrength=ground.get("strength_label")
            if ground_restricted:
                tier=1
            elif not ground_stages or not gstrength:
                tier=0
            elif all(x in high_ground_stages for x in ground_stages):
                tier=2 if gstrength=="极小" else 3
            else:
                tier=0
            if tier:
                stem_candidates.append((tier,ground_stem+"奇","地盘"))
        stem_best=(max(stem_candidates,key=lambda x:x[0])
                   if stem_candidates else None)
        # Only physical illness Tianrui+Tianqin can have TWO independently
        # eligible 乙/丁 carriers. Ordinary palaces still take best ONE
        # special-stem family. Same Yi/Ding on earth is not a second carrier.
        independent_stem_sum=disease_dual_sky_bonus(
            [(x["name"],x.get("carried_stem")) for x in detail["stars"]],
            stem_candidates,
            illness_host=any(h["role"]=="illness" for h in hosts))
        separate_sky=independent_stem_sum is not None
        chief_points=0
        if (detail["deity"]["name"]=="值符" and
                independent_special_host(hosts,"deity","值符")):
            god=detail["deity"]
            if GOD_RELATIONS.get(god["nominal_relation"]):
                chief_points=2 if god["nominal_relation"]=="宫克符号" else 3
        tianxin_points=0
        for star in detail["stars"]:
            if (star["name"]!="天心星" or
                    not independent_special_host(hosts,"star","天心星")):
                continue
            power=star["strength"].get("strength_label")
            if power:
                tianxin_points=2 if power=="极小" else 3
                break
        raw_stem=(independent_stem_sum if independent_stem_sum is not None
                  else stem_best[0] if stem_best else 0)
        raw=raw_stem+chief_points+tianxin_points
        if not raw:continue
        # Void acts ONCE on the SUM of every different qualified blessing,
        # including Tianxin, not separately on chief/stem and doctor-star.
        applied=raw//2 if is_void else raw
        # One actual Yi or Ding only gets ONE label even when both sky and
        # earth candidates carry that same character; preserve source order.
        stem_name_by_identity={}
        for _,stem,plane in stem_candidates:
            stem_name_by_identity.setdefault(stem,plane+stem)
        stem_names=list(stem_name_by_identity.values())
        tags=([ "值符" ] if chief_points else [])+stem_names
        if tianxin_points:tags.append("天心星")
        if is_void:
            note=label+"逢空，"+"与".join(tags)+"同宫的吉助减弱，尚有余气。"
        else:
            note=label+"得"+"与".join(tags)+"同宫扶助。"
        token=str(pid)+":同宫吉助"
        auspice[token]={"palace":pid,"symbol":"、".join(tags),
                         "points":applied,"before_void":raw,
                         "note":note,"cohost":True}
        cohost_audit[str(pid)]={
            "hosts":hosts,"chief":chief_points,"stem_family":raw_stem,
            "tianxin":tianxin_points,
            "stem_candidates":[{"points":q,"stem":stem,"plane":plane}
                               for q,stem,plane in stem_candidates],
            "ground_stages":ground_stages,
            "ground_restricted":ground_restricted,
            "disease_two_independent_sky_stars":separate_sky,
            "independent_sky_bonus":independent_stem_sum,
            "empty":is_void,"pre_void":raw,"after_void":applied,
            "self_signifier_excluded":True,
            "void_after_all_bonuses":True}
    lucky_points=sum(v["points"] for v in auspice.values())
    total_bonus=sum(control_points.values())+3*len(drain)+lucky_points
    # V7.8: special illness auspice is an independent CONDITION overlay.
    # The unique physical palace base (stars/door/god/pattern/stems) counts
    # ONCE; two distinct eligible Tianrui/Tianqin sky carriers are
    # the ONLY disease exception to the one-stem-family bonus cap.
    # Never repeat this extra per role in the same actual palace.
    qualified_bonus=sum(control_points.values())+3*len(drain)+lucky_points
    macro_penalty=2*summary["unique_palace_count"] if five else 0
    historical_stacked_total=role_sum+total_bonus-(2*len(roles) if five else 0)
    from .health_macro_facts_vnext import tianxian_palace_bonus
    tianxian_bonus=tianxian_palace_bonus(
        summary["unique_palace_count"],
        triggered=bool(first_stage_macro.get("tianxian_hour_triggered")),
        fuyin=bool(first_stage_macro.get("star_fuyin") or first_stage_macro.get("door_fuyin")))
    final_raw=summary["post_void_known_sum"]+qualified_bonus-macro_penalty+tianxian_bonus
    original=summary["score"]
    summary["physical_palace_v75_audit"]=previous_physical
    summary["effective_role_scores"]=role_scores
    summary["role_count"]=len(roles)
    summary["pending_roles"]=pending_roles
    summary["v76_role_score_sum_if_repeated"]=role_sum
    summary.update({
        "pre_relationship_bonus_score":original,
        "control_bonus_palaces":{str(k):v for k,v in sorted(control.items())},
        "control_bonus_points":control_points,
        "signed_palace_grades_never_actor_strength":True,
        "actual_role_strengths":{
            role:{"palace":record["palace"],
                  "kind":record["primary_strength_25"]["kind"],
                  "symbol":record["primary_strength_25"]["symbol"],
                  "tier":record["primary_strength_25"].get("strength_label"),
                  "relation":gates.get(role,{}).get("relation"),
                  "control_cell":gates.get(role,{}).get("control_result"),
                  "control_status":gates.get(role,{}).get("control_status")}
            for role,record in selected_roles.items()},
        "control_power_provenance":"selected_primary_200x200_5x5_source_never_abs_palace_score",
        "non_control_pair_policy":"all_selected_role_and_target_200_strengths_independent_no_invented_matrix",
        "drain_bonus_palaces":{str(k):v for k,v in sorted(drain.items())},
        "control_bonus_score":sum(control_points.values()),
        "weak_illness_drain_bonus_score":3*len(drain),
        "auspice_bonus_details":auspice,
        "auspice_cohost_audit":cohost_audit,
        "auspice_bonus_notes":[auspice[k]["note"] for k in sorted(auspice)],
        "auspice_bonus_score":lucky_points,
        "auspice_applied_extra_score":lucky_points,
        "auspice_merged_into_physical_palace":False,
        "relationship_bonus_score":qualified_bonus,
        "historical_role_stacked_bonus_score":total_bonus,
        "unique_palace_score_details":{str(pid):roles[g["roles"][0]]["palace_score"] for pid,g in grouped.items()},
        "repeated_signifier_merged":True,
        "five_not_global_penalty":macro_penalty,
        "tianxian_global_final_bonus":tianxian_bonus,
        "tianxian_applied_once_after_all_palaces":False,
        "tianxian_total_floor_once":True,
        "tianxian_selected_unique_palaces":summary["unique_palace_count"],
        "five_not_penalty_per_palace":2 if five else 0,
        "five_not_penalized_unique_palace_count":summary["unique_palace_count"] if five else 0,
        "five_not_per_distinct_palace":True,
        "five_not_per_selected_role_occurrence":False,
        "five_not_penalized_role_count":len(roles) if five else 0,
        "historical_overlay_total_if_stacked":historical_stacked_total,
        "relationship_overlays_audit_only":False,
        "final_scoring_policy":("V9.0_SOURCE_CONDITIONED_SIBLING_AUXILIARY"
            if "sibling" in selected_roles else "V8.0_SELECTED_SIGNIFIER_STRENGTH_ALL_INTERPALACE"),
        "raw_final_before_saturation":final_raw,
        "five_not_deducted_once_at_end":False,
        "weak_illness_drain_eligible":weak_disease,
        "score":(saturate(final_raw) if not summary["pending_palaces"] else None)})
    summary["grade"]=grade_label(summary["score"]) if summary["score"] is not None else None
    return {"version":VERSION,"roles":roles,
            "auxiliary_qian_kun":qian_kun,
            "selected_gender_palace":selected_gender_palace,
            "role_effectiveness_gates":gates,
            "summary":summary,
            "incomplete_conversion_not_silently_scored":True,
            "source_condition_gate_required":True,
            "not_a_medical_diagnosis":True}


def render_palace_signed_score(item):
    """Report EVERY known star/door/god and ordered stem pair, no fake final."""
    star=item["star"]
    descriptions=[]
    for st in star["per_star"]:
        if st.get("not_scored_in_illness"):
            descriptions.append(st["symbol"]+"真实同宫但疾病不另计分")
            continue
        descriptions.append(
            st["symbol"]+"基准"+str(st.get("baseline","待核"))+
            "，200格现值"+str(st.get("tier") or "待核")+
            ("→"+st["label"]+"（"+str(st["score"])+"）" if
             st.get("label") else "→待核"))
    door=item["door"]
    descriptions.append(
        str(door.get("symbol"))+"门基准"+str(door.get("baseline","待核"))+
        "，200格"+str(door.get("strength") or "待核")+
        ("→"+str(door.get("label"))+"（"+str(door["score"])+"）"
         if door.get("score") is not None else "→待核"))
    god=item["deity"]
    descriptions.append(
        str(god.get("symbol"))+"神基准"+str(god.get("baseline","待核"))+
        "，对宫"+str(god.get("nominal_relation"))+
        "→"+str(god.get("tier") or "待核")+
        ("、"+str(god.get("label"))+"（"+str(god["score"])+"）"
         if god.get("score") is not None else "→待核"))
    ten=item.get("ten_stem_intrinsic",{})
    for x in ten.get("heaven",()):
        descriptions.append("天盘"+x["stem"]+"本体默认"+
                            ("%+d"%x["baseline"])+"（宫内四项不重复加）")
    if ten.get("earth"):
        x=ten["earth"]
        descriptions.append("地盘"+x["stem"]+"本体默认"+
                            ("%+d"%x["baseline"])+"（宫内四项不重复加）")
    if ten.get("jia_hidden_cycle") and ten["jia_hidden_cycle"]["baseline"] is not None:
        x=ten["jia_hidden_cycle"]
        descriptions.append(x["xun_shou"]+"遁甲本体默认"+
                            ("%+d"%x["baseline"])+"（不造可见甲）")
    pattern=item["pattern"]
    if not pattern["matches"]:
        descriptions.append("天地有序格无核定本次候选")
    for pair in pattern["matches"]:
        sub=pair["name"]+"（"+pair["key"]+"）"
        sc=pair["score"]
        descriptions.append(
            sub+(("→"+grade_label(sc)+"（"+str(sc)+"）")
                 if sc is not None else
                 "→"+str(pair["source_rule"]["status"])+"待核"))
    palace=item["palace_score"]
    if palace["grade"] is not None:
        final=("本宫原始净分"+str(palace["raw_sum"])+
               "，空亡调整前"+str(palace["score_before_void"])+
               "分，实际"+str(palace["score"])+"分："+ 
               ("不凶不吉" if palace["score"]==0 else palace["grade"]))
    elif palace["score"] is not None:
        final="本宫当前"+str(palace["score"])+"分（"+str(palace["status"])+"）"
    else:
        final=("本宫已核分项小计"+str(palace["known_subtotal"])+
               "，尚缺"+"/".join(palace["unresolved_categories"])+
               "；最终五级待核（"+palace["status"]+"）")
    return "；".join(descriptions)+"；"+final+"。"


def render_palace_compact_score(item):
    """Customer-facing concise four-category points, no duplicated facts.

    Full provenance remains available under the exact raw JSON and
    render_palace_signed_score() for developer audits.
    """
    def signed(x):
        return "%+d"%x if isinstance(x,int) else "待核"
    stars="、".join(x["symbol"]+signed(x.get("score"))
                   for x in item["star"]["per_star"]
                   if not x.get("not_scored_in_illness"))
    door=item["door"]
    deity=item["deity"]
    patterns=item["pattern"]["matches"]
    pq="、".join(x["name"]+signed(x.get("score")) for x in patterns) or "无已核格局"
    parts=[
        "星"+(stars or "待核"),
        "门"+str(door.get("symbol") or "无")+signed(door.get("score")),
        "神"+str(deity.get("symbol") or "无")+signed(deity.get("score")),
        "格"+pq,
    ]
    pal=item["palace_score"]
    if pal["score"] is not None:
        if pal["void_state"] in ("fake_void","true_void"):
            kind="假空" if pal["void_state"]=="fake_void" else "真空"
            tail=(kind+"宫空前"+str(pal["score_before_void"])+"分，"+
                  "按正减3／负加3／零不变→"+str(pal["score"])+
                  "分（"+("不凶不吉" if pal["score"]==0 else pal["grade"])+
                  "）；只在后续填实冲开应期上区分真假空")
        else:
            tail=("原始净分"+str(pal["raw_sum"])+
                  "，五档"+str(pal["score"])+
                  ("不凶不吉" if pal["score"]==0 else pal["grade"]))
    else:
        tail=("已核小计"+str(pal["known_subtotal"])+
              "，待核"+"/".join(pal["unresolved_categories"]))
    return "、".join(parts)+"；"+tail+"。"


def render_quant_review(report):
    summary=report["summary"]
    score=summary["score"]
    if score is not None:
        return ("本次相关实宫空亡调整前原分合计"+str(summary["raw_known_sum"])+
                "，空亡调整后各宫实际净分合计"+str(summary["post_void_known_sum"])+
                "，最后按±5截断为"+str(score)+"分（"+
                ("不凶不吉" if score==0 else summary["grade"])+"）；共"+
                str(summary["unique_palace_count"])+"个不重复相关宫。"+
                "四类星门神格原分独立保存；时干、值符、性别辅助若与"+
                "其他用神同宫不重复加总；仅为术数研究。")
    return ("已知相关宫当前原始小计"+
            str(summary["raw_known_sum"])+"分，暂示"+
            str(summary["provisional_known_grade"])+"；另有"+
            str(len(summary["pending_palaces"]))+"个宫的格局触发、"+
            "十二长生分支或人物条件未核，不能当最终断案净分。"+
            "最终档位只有证据齐备后按±5上限确定。")
