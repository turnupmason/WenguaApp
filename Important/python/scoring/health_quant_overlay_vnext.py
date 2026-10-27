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
from .health_five_level_quant_vnext import label as grade_label
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
    bottom=earth["symbol"] if earth else None
    heaven={x["symbol"]:x for x in detail["heaven_stems"]}
    illness_top_stems={
        e["carried_stem"] for e in detail["stars"]
        if e["name"]=="天芮星" and e.get("carried_stem")}
    skipped_health_cohosts=[]
    origin={(p["heaven"],p["earth"]):p
            for p in detail["ordered_book_81_pairs"]}
    pairs=[]
    for top,stem_fact in heaven.items():
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
        "only_tianrui_carried_stem_if_illness":role=="illness",
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


def special_cohost_total(chief_points,stem_points,*,void=False):
    """V7.2 real one-palace chief + earth/sky 奇: halve TOTAL, floor once."""
    if chief_points not in (0,2,3) or stem_points not in (0,1,2,3):
        raise ValueError("Unknown same-palace auspice tier")
    total=chief_points+stem_points
    return total//2 if void else total


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
                "hour","natal","gender","chief"):
            detail=row["complete_palace"]
            palace=detail["palace"]
            if palace in physical_cache:
                canonical=physical_cache[palace]
                item={**canonical["item"],"role":key,
                      "score_shared_with_role":canonical["role"],
                      "same_real_palace_same_score":True}
            else:
                item=_quantize_one(key,detail,five_not_encounter=False,
                                   xun_shou=xun_shou)
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
        active=(key=="illness" or chief_cohost or
                (not chief and not is_control) or
                (is_control and ability in accepted and
                 (not chief or void=="not_void")))
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
                    "control_result":outcome,"control_scenario":scenario,
                    "control_ability":ability,"void":void,
                    "score_eligible":active,"reason":reason,
                    "chief_zero_score":chief and not active}
        # All selected real palaces contribute intrinsic state once; only
        # extra *control assistance* is gated by effective suppression.
        effective[key]=aggregate[key]
    summary=multi_palace_tally(palaces=effective)
    # V7 USER CONDITIONAL RULES, private-only points. Source 200/81 table
    # scores and every real palace remain unchanged. Distinct physical
    # control palaces and distinct auspicious symbols are counted once each.
    # A weak/void attacker does not get a normal +3 just for nominal 克.
    illness_pid=selected_roles["illness"]["palace"]
    illness_detail=selected_roles["illness"]["complete_palace"]
    illness_void=illness_detail["void"]["classification"]!="not_void"
    weak_disease=(selected_roles["illness"]["primary_strength_25"]
                  .get("strength_label")=="极小")
    control_roles={"doctor","medicine","patient","hour","natal","chief","gender"}
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
            strength=gate["actor_strength"]
            if strength and strength!="极小":
                # The actor is weakened if it is empty or its OWN resident
                # primary symbol is克 by its palace, not because a 5×5 text
                # label says "完全失控". This never reverses real 五行方向.
                nominal=row["primary_strength_25"].get("user_cell_col")
                symbol_controlled=nominal in ("宫克符号","被宫克")
                points=(1 if gate["void"]!="not_void" or symbol_controlled
                        else 5 if illness_void else 3)
                control.setdefault(pid,[]).append(key)
                control_points[str(pid)]=max(control_points.get(str(pid),0),points)
        # Preserve prior V6 weak illness actively draining into other roles.
        if weak_disease and gate["relation"]=="被生":
            if key!="chief" or gate["void"]=="not_void":
                drain.setdefault(pid,[]).append(key)

    # V7.2 co-palace rule: one physical palace once; sky/earth 乙/丁 are ONE
    # auspicious stem family per palace. A chief-deity and that family are
    # separate eligible components. Void halves their COMBINED subtotal,
    # flooring only once (6->3, 5->2, 4->2, 3->1).
    # Independent sky/door/star/deity/81 factors remain untouched.
    auspice_hosts={"illness","patient","hour","natal","gender"}
    host_palaces={}
    host_roles={}
    for key,row in selected_roles.items():
        if key in auspice_hosts:
            host_palaces.setdefault(row["palace"],row["complete_palace"])
            host_roles.setdefault(row["palace"],set()).add(key)
    auspice={}
    cohost_audit={}
    high_ground_stages={"长生","沐浴","冠带","临官","帝旺"}
    from .health_intrinsic_scoring_vnext import GOD_RELATIONS
    for pid,detail in sorted(host_palaces.items()):
        label=detail["palace_name"]
        is_void=detail["void"]["classification"]!="not_void"
        sky_tombs={x["stem"] for x in detail.get("sky_tombs",())}
        strikes=set(detail.get("striking_stems",()))
        # The underlying earth twelve-life facts come from the original
        # stem atlas at THIS real seat; do not use the sky stem stages.
        sky_candidates=[]
        for x in detail["heaven_stems"]:
            if x["symbol"] in ("乙","丁") and (
                pid==illness_pid or
                any(selected_roles[k]["primary_strength_25"].get("symbol")==x["symbol"]
                    for k in host_roles[pid])):
                sky_candidates.append((x["symbol"],x.get("strength_label"),
                                       x["symbol"] in sky_tombs or x["symbol"] in strikes))
        ground=detail.get("earth_stem") or {}
        ground_stem=ground.get("symbol")
        ground_stages=[x.get("stage") for x in
            ground.get("palace_twelve_life_facts",()) if x.get("stage")]
        ground_restricted=bool(detail.get("earth_tombs")) or ground_stem in strikes
        stem_candidates=[]
        for stem,strength,restricted in sky_candidates:
            if not strength:continue
            points=1 if restricted else 2 if strength=="极小" else 3
            stem_candidates.append((points,stem+"奇","天盘"))
        if ground_stem in ("乙","丁"):
            gstrength=ground.get("strength_label")
            if ground_restricted:
                points=1
            elif not ground_stages or not gstrength:
                points=0  # Do not invent a 200-cell strength for split seats.
            elif all(x in high_ground_stages for x in ground_stages):
                points=2 if gstrength=="极小" else 3
            else:
                points=0  # Off-five life stages cannot claim an invented partial bonus.
            if points:
                stem_candidates.append((points,ground_stem+"奇","地盘"))
        # Same actual palace + 乙/丁 family is ONE bonus even if the selected
        # hour/year itself is 乙 and the earth is 丁.
        stem_best=(max(stem_candidates,key=lambda x:x[0])
                   if stem_candidates else None)
        chief_points=None
        if detail["deity"]["name"]=="值符":
            god=detail["deity"]
            if GOD_RELATIONS.get(god["nominal_relation"]):
                chief_points=2 if god["nominal_relation"]=="宫克符号" else 3
        if stem_best or chief_points:
            raw_stem=stem_best[0] if stem_best else 0
            raw_chief=chief_points or 0
            raw=raw_stem+raw_chief
            applied=special_cohost_total(raw_chief,raw_stem,void=is_void)
            # Show every real qualifying sky/earth symbol in prose,
            # although they share ONE stem-family score.
            stem_names=list(dict.fromkeys(plane+stem
                for _,stem,plane in stem_candidates))
            tags=(["值符"] if chief_points else [])+stem_names
            if is_void:
                note=label+"逢空，"+"与".join(tags)+"同宫的吉助减弱，尚有余气。"
            else:
                note=label+"得"+"与".join(tags)+"同宫扶助。"
            token=str(pid)+":同宫吉助"
            auspice[token]={"palace":pid,"symbol":"、".join(tags),
                            "points":applied,"before_void":raw,
                            "note":note,"cohost":True}
            cohost_audit[str(pid)]={
                "roles":sorted(host_roles[pid]),"chief":raw_chief,
                "stem_family":raw_stem,
                "stem_candidates":[{"points":q,"stem":stem,"plane":plane}
                                   for q,stem,plane in stem_candidates],
                "ground_stages":ground_stages,
                "ground_restricted":ground_restricted,
                "empty":is_void,"pre_void":raw,"after_void":applied}
        # Tianxin is separately a real star signifier: its own auspice is
        # not a second deity nor another 乙/丁 bonus.
        for star in detail["stars"]:
            if star["name"]!="天心星":continue
            power=star["strength"].get("strength_label")
            if not power:continue
            points=1 if is_void else 2 if power=="极小" else 3
            note=(label+"逢空，天心星吉助余气尚存。" if is_void else
                  label+"天心星势极小，吉助有限。" if power=="极小" else
                  label+"得天心星医者吉助。")
            auspice[str(pid)+":天心星"]={
                "palace":pid,"symbol":"天心星","points":points,"note":note}
    lucky_points=sum(v["points"] for v in auspice.values())
    total_bonus=sum(control_points.values())+3*len(drain)+lucky_points
    # Apply 五不遇时 ONCE to the aggregate, after role dedup and bonuses.
    macro_penalty=2 if five else 0
    final_raw=summary["post_void_known_sum"]+total_bonus-macro_penalty
    original=summary["score"]
    summary.update({
        "pre_relationship_bonus_score":original,
        "control_bonus_palaces":{str(k):v for k,v in sorted(control.items())},
        "control_bonus_points":control_points,
        "drain_bonus_palaces":{str(k):v for k,v in sorted(drain.items())},
        "control_bonus_score":sum(control_points.values()),
        "weak_illness_drain_bonus_score":3*len(drain),
        "auspice_bonus_details":auspice,
        "auspice_cohost_audit":cohost_audit,
        "auspice_bonus_notes":[auspice[k]["note"] for k in sorted(auspice)],
        "auspice_bonus_score":lucky_points,
        "relationship_bonus_score":total_bonus,
        "five_not_global_penalty":macro_penalty,
        "raw_final_before_saturation":final_raw,
        "five_not_deducted_once_at_end":True,
        "weak_illness_drain_eligible":weak_disease,
        "score":(max(-5,min(5,final_raw))
                 if original is not None else None)})
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
