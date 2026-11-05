# 52条全库失败/错误清账 · 2026-11-02

基线源码94edb647，835 tests：41 failures、11 errors、3 skipped。补丁后839 tests：2 failures、0 errors、3 skipped；50条基线记录已验证解决，剩2条是手动时辰功能缺口。没有删除测试方法或增加skip/xfail；4项新回归验证补丁边界。

原始失败、断言原文、实际异常、代码行与复现命令见 [failure_ledger.json](failure_ledger.json)、[baseline/results.json](baseline/results.json)。完整输出以gzip原样保留，SHA在对应results.json。所有迁移测试原文件与SHA见 [original_test_index.json](../../../archives/engineering_patch_20261102/original_test_index.json)。旧V7数字断言不是当前V9预期；原件可独立审计，不拿来改写封存评分。

## 真正实现缺陷与修复边界

`health_quant_overlay_vnext.py:_quantize_one` 地盘本征审计错误取循环末尾bottom。真实2025-07-18 03:00纽约盘：坤二普通地盘戊，中五寄干丁，旧审计误写丁；空格局测试fixture则UnboundLocalError。现取已保存ordinary_bottom；原型审计源与原封存manifest均无损保存。新的工程补丁p1仅变该源文件SHA，不变两模板、200/81、人物源、Swift和任何计分策略。四张原有真实盘分数与完整中文SHA逐字不变；该测试不是盲测或临床有效性。

## 逐项账目

| 编号 | 测试/子测试 | 分类 | 当前状态 |
|---|---|---|---|
| HC001 | `test_casting_chai_bu_user_process_vnext.CastingUserFlow.test_centre_door_zero_step_only_original_confirmed` | center_host_extension | verified_resolved |
| HC002 | `test_domain_selected_energy_vnext.CompactTables.test_only_registered_subtype_is_eligible` | registered_eight_roles | verified_resolved |
| HC003 | `test_domain_selected_energy_vnext.SelectedRealCases.test_gender_selection_male_qian_female_kun` | elder_identity | verified_resolved |
| HC004 | `test_domain_selected_energy_vnext.SelectedRealCases.test_template_order_and_one_disease_matrix_evidence` | v11_customer_contract | verified_resolved |
| HC005 | `test_factor_energy_25_rules.UniversalTwentyFive.test_actual_control_vs_inverse_vs_blocker` | inverse_control_direction | verified_resolved |
| HC006 | `test_health_81_excel_live_template_20261025.Excel81.test_real_chart_displays_all_four_excel_fields_every_selected_palace` | v11_customer_contract | verified_resolved |
| HC007 | `test_health_complete_palace_vnext.RealSelectedPalacePipeline.test_avoids_double_voting_multiple_symbols_of_same_palace` | v11_customer_contract | verified_resolved |
| HC008 | `test_health_complete_palace_vnext.RealSelectedPalacePipeline.test_qian_and_kun_are_always_real_auxiliaries_not_two_patients` | elder_identity | verified_resolved |
| HC009 | `test_health_complete_palace_vnext.RealSelectedPalacePipeline.test_role_bindings_no_fabricated_year_or_both_gender_palaces` | elder_identity | verified_resolved |
| HC010 | `test_health_customer_unscored_20261026.CustomerOnlyUnscored.test_template_has_no_visible_score_words` | v11_customer_contract | verified_resolved |
| HC011 | `test_health_customer_unscored_20261026.CustomerOnlyUnscored.test_two_actual_casts_keep_private_quant_but_customer_unscored` | v11_customer_contract | verified_resolved |
| HC012 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_actual_other_door_break_uses_two_level_shift (door='景门', palace=7)` | runtime_earth_audit | verified_resolved |
| HC013 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_actual_other_door_break_uses_two_level_shift (door='死门', palace=1)` | runtime_earth_audit | verified_resolved |
| HC014 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_actual_other_door_break_uses_two_level_shift (door='休门', palace=9)` | runtime_earth_audit | verified_resolved |
| HC015 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_actual_other_door_break_uses_two_level_shift (door='开门', palace=3)` | runtime_earth_audit | verified_resolved |
| HC016 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_exact_two_are_still_door_break_but_skip_shift (door='生门', palace=1)` | runtime_earth_audit | verified_resolved |
| HC017 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_exact_two_are_still_door_break_but_skip_shift (door='景门', palace=6)` | runtime_earth_audit | verified_resolved |
| HC018 | `test_health_door_break_exception_vnext.DoorBreakNoExtraPenalty.test_user_now_defines_door_intrinsic_polarity` | runtime_earth_audit | verified_resolved |
| HC019 | `test_health_first_macro_vnext.FirstStageMacroFacts.test_fuyin_and_fanyin_tempo_do_not_cast_good_or_bad_vote` | v11_customer_contract | verified_resolved |
| HC020 | `test_health_first_macro_vnext.FirstStageMacroFacts.test_live_cast_macro_before_selected_palace_sections` | v11_customer_contract | verified_resolved |
| HC021 | `test_health_first_macro_vnext.FirstStageMacroFacts.test_real_not_encounter_hour_counts_exactly_one_global_bad_fact` | v11_customer_contract | verified_resolved |
| HC022 | `test_health_quant_overlay_vnext.CurrentQuantReview.test_selected_roles_real_tier_not_imaginary_god_door_case` | elder_identity | verified_resolved |
| HC023 | `test_health_relationship_language_vnext.NaturalDiseaseRoleInterpretation.test_illness_attacks_others_must_not_be_reversed` | v11_customer_contract | verified_resolved |
| HC024 | `test_health_relationship_language_vnext.NaturalDiseaseRoleInterpretation.test_real_caster_selected_roles_have_grounded_prose` | v11_customer_contract | verified_resolved |
| HC025 | `test_health_two_random_template_20261026.TwoUnbiasedLiveTemplateCases.test_two_new_real_hour_customer_readings` | v11_customer_contract | verified_resolved |
| HC026 | `test_health_user_final_signed_template_vnext.UserSignedFinalScore.test_real_2025_chart_tianqin_fact_not_second_illness_star` | disease_dual_carrier | verified_resolved |
| HC027 | `test_health_user_final_signed_template_vnext.UserSignedFinalScore.test_user_requires_both_real_qian_and_kun_auxiliary_palaces (sex='male')` | elder_identity | verified_resolved |
| HC028 | `test_health_user_final_signed_template_vnext.UserSignedFinalScore.test_user_requires_both_real_qian_and_kun_auxiliary_palaces (sex='female')` | elder_identity | verified_resolved |
| HC029 | `test_health_v32_fresh_two_families.SourceFamilyV32HistoricalCheck.test_original_centre_5_head_hour_uses_only_source_attested_kun_host` | center_host_extension | verified_resolved |
| HC030 | `test_health_v74_colleague_natal_yi_and_macro_penalty_20261027.FixedColleagueNatalYi.test_all_adverse_and_good_actual_palaces_counted_once` | historical_role_stacking | verified_resolved |
| HC031 | `test_health_v74_colleague_natal_yi_and_macro_penalty_20261027.FixedColleagueNatalYi.test_two_paragraphs_include_both_global_conditions` | v11_customer_contract | verified_resolved |
| HC032 | `test_health_v75_unique_palace_five_not_20261027.FinalUniquePalaceV75.test_1920_elder_without_five_not` | historical_role_stacking | verified_resolved |
| HC033 | `test_health_v75_unique_palace_five_not_20261027.FinalUniquePalaceV75.test_colleague_five_not_each_real_palace` | historical_role_stacking | verified_resolved |
| HC034 | `test_health_v75_unique_palace_five_not_20261027.FinalUniquePalaceV75.test_cultural_not_clinical` | v11_customer_contract | verified_resolved |
| HC035 | `test_health_v76_three_stage_20261027.V76ThreeStage.test_1920_same_yi_twice` | historical_role_stacking | verified_resolved |
| HC036 | `test_health_v76_three_stage_20261027.V76ThreeStage.test_colleague` | historical_role_stacking | verified_resolved |
| HC037 | `test_health_vnext_conditional_review.FullRealChartPreview.test_different_logic_is_preview_only_not_clinically_validated` | v11_customer_contract | verified_resolved |
| HC038 | `test_health_vnext_conditional_review.FullRealChartPreview.test_new_readings_complete_and_no_scores_or_unverified_claims` | v11_customer_contract | verified_resolved |
| HC039 | `test_health_vnext_conditional_review.OldBookQuestionOnlySmoke.test_two_source_historical_roles_are_not_forced_to_self` | v11_customer_contract | verified_resolved |
| HC040 | `test_health_vnext_signed_customer_20261026.SignedHealthCustomerVerbatim.test_five_band_grade_wording_and_no_veto_for_completed_total (instant='2021-10-03T03:00:00-04:00')` | v11_customer_contract | verified_resolved |
| HC041 | `test_health_vnext_signed_customer_20261026.SignedHealthCustomerVerbatim.test_five_band_grade_wording_and_no_veto_for_completed_total (instant='2023-04-24T21:00:00-04:00')` | v11_customer_contract | verified_resolved |
| HC042 | `test_health_void_signed_scope_20261025.Real2024SelectedChart.test_real_2024_chart_and_only_selected_relevance_closure` | elder_identity | verified_resolved |
| HC043 | `test_health_void_signed_scope_20261025.Real2024SelectedChart.test_same_palace_same_current_score_even_if_different_roles` | elder_identity | verified_resolved |
| HC044 | `test_ios_design_v1_contract.V3SourceUI.test_all_screen_elements_and_no_fake_live_cast` | manual_clock_gap | open_feature_gap |
| HC045 | `test_ios_design_v1_contract.V3SourceUI.test_consumer_entry_has_fifteen_domains_one_explicitly_supported_topic` | manual_clock_gap | open_feature_gap |
| HC046 | `test_ios_design_v1_contract.V3SourceUI.test_native_launch_uses_domain_route_and_preserves_frozen_source_audit_offline` | current_ui_contract | verified_resolved |
| HC047 | `test_ios_design_v1_contract.V3SourceUI.test_true_five_element_color_map_not_category_colors` | current_ui_contract | verified_resolved |
| HC048 | `test_ios_health_template_bridge_20261026.NativeTemplateBundleContract.test_exact_live_sources_are_bundled_and_looked_up_in_real_chart` | current_ui_contract | verified_resolved |
| HC049 | `test_ios_health_template_bridge_20261026.NativeTemplateBundleContract.test_full_clinical_or_vnext_score_is_not_claimed_on_phone` | current_ui_contract | verified_resolved |
| HC050 | `test_ios_store_history_release_gate.LocalHistoryAndPrivacy.test_history_and_user_initiated_full_delete` | current_ui_contract | verified_resolved |
| HC051 | `test_ios_vnext_production_entry_20261026.NativeVNextAppContract.test_main_is_not_frozen_v391_and_book_sqlite_is_not_bundled` | current_ui_contract | verified_resolved |
| HC052 | `test_user_exact_energy_duel_grids_vnext.UserAuthoredCells.test_raw_user_labels_flow_into_real_selected_health_reading` | v11_customer_contract | verified_resolved |

## 尚未结案

HC044/HC045继续明确失败：当前手机只有实时Date()，没有用户要求的手动真实时辰DatePicker。按原计划先核定规则疑点、完成真机验收准备，随后补功能；不靠删断言/skip制造全绿。

真机验收与App Store不在本账本中被标为通过，需真实设备、签名与实际操作证据。


### 2026-11-02 · 清账与p1工程补丁正式验收完成
源码f8d1b1e0c0af5db51cadbcdcc3ab83fc3dd265d1：主CI #41460321192（Python3.11/3.12）、轻重原生逐字 #41460320478、独立iOS编译/原生回归 #41460320720、正式macOS Xcode/实际包资源SHA/四次Bundle路由/V27逐字/六伤损条件/1080数据 #41460320838 均success。新Xcode原始全文 https://github.com/turnupmason/WenguaApp/blob/course-v4-before-cleanup-20261105/docs/IOS_V80_XCODE_PASS_RUN_41460320838_ATTEMPT_1.md，未用旧run替代。
完整本地839 tests的2 failures/0 errors/3 skipped单独保留，不能声称全库全绿：两失败均为手动真实时辰入口缺失；三skip原已存在（可选Moshier软件交叉参考未安装，V7.7/V7.8两历史class版本门槛），本轮未增加skip或xfail。原52条逐项账、修改前测试原件/SHA和完整失败日志均可复现。四原时辰分数、完整中文SHA及两个模板/200/81/人物/Swift源码pin未变，唯一冻结源位改动是ordinary_bottom地盘审计字段，manifest明确engineering_p1并保留前版原件。
顺序进度：1）50条已验证解决，另2条功能缺口按第4步保留；2）360真时辰及1080物理组合复核完成，弱病泄耗/特殊宿主来源未核定不改分；3）真实iPhone无连接/签名/用户实测，验收清单已备、仍全部未执行；4）手动入口尚未实现，不越过真机条件伪报已交付。
