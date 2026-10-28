# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/40619938658\n\n\n## compile.log\n\n\`\`\`text\nios/WenguaAppUI/WenguaNativeReadingRouter.swift:208:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
206 |         let fanyin=entire(actualStars,homeStars,true) ||
207 |                     entire(actualDoors,homeDoors,true)
208 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |             fill(fiveNot ? "macro_five" : "macro_clear"),
210 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/WenguaVNextReasoner.swift:195:80: error: '+' is not a postfix unary operator
193 |             // in that environment have DIFFERENT selected powers.
194 |             let symbol=audit.roleEnergy[role]?.symbol ?? role
195 |             let pair=[id,illID].sorted().map(String.init).joined(separator:":")+
    |                                                                                `- error: '+' is not a postfix unary operator
196 |                       ":"+symbol
197 |             if !usedPairs.insert(pair).inserted {

ios/WenguaAppUI/WenguaVNextReasoner.swift:196:26: warning: result of operator '+' is unused [#NoUsage]
194 |             let symbol=audit.roleEnergy[role]?.symbol ?? role
195 |             let pair=[id,illID].sorted().map(String.init).joined(separator:":")+
196 |                       ":"+symbol
    |                          `- warning: result of operator '+' is unused [#NoUsage]
197 |             if !usedPairs.insert(pair).inserted {
198 |                 relations.append(try fill("reason_shared",[

ios/WenguaAppUI/WenguaVNextReasoner.swift:204:72: error: '+' is not a postfix unary operator
202 |             let control=audit.controls.first{$0.role==role}
203 |             let direction=control?.direction ?? relation(id,illID)
204 |             let strength=(audit.roleEnergy[role]?.strength ?? "待核")+
    |                                                                    `- error: '+' is not a postfix unary operator
205 |                 "；天芮病星"+(audit.roleEnergy["illness"]?.strength ?? "待核")
206 |             let effect:String

ios/WenguaAppUI/WenguaVNextReasoner.swift:205:34: warning: result of operator '+' is unused [#NoUsage]
203 |             let direction=control?.direction ?? relation(id,illID)
204 |             let strength=(audit.roleEnergy[role]?.strength ?? "待核")+
205 |                 "；天芮病星"+(audit.roleEnergy["illness"]?.strength ?? "待核")
    |                        `- warning: result of operator '+' is unused [#NoUsage]
206 |             let effect:String
207 |             if let control, direction=="克" || direction=="被克" {

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
\n\`\`\`\n\n## matrix_tests.log\n\n\`\`\`text\ntest_all_25_power_pairs_never_infer_strength_from_signed_grade (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_all_25_power_pairs_never_infer_strength_from_signed_grade) ... ok
test_both_real_clocks_account_for_actual_distinct_palaces (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_both_real_clocks_account_for_actual_distinct_palaces) ... ok
test_distinct_illness_host_allows_one_yi_ding_family (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_distinct_illness_host_allows_one_yi_ding_family) ... ok
test_independent_selected_host_any_role_or_any_order (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_independent_selected_host_any_role_or_any_order) ... ok
test_one_family_per_palace_and_complete_void_half_once (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_one_family_per_palace_and_complete_void_half_once) ... ok
test_same_physical_doctor_and_medicine_have_separate_energies (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_same_physical_doctor_and_medicine_have_separate_energies) ... ok
test_symbol_self_never_adds_once_or_under_different_role_alias (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_symbol_self_never_adds_once_or_under_different_role_alias) ... ok
test_yearstem_yi_is_not_yi_own_auspice (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_yearstem_yi_is_not_yi_own_auspice) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.121s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
\n\`\`\`\n