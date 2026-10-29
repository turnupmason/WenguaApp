# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/40950868839\n\n\n## compile.log\n\n\`\`\`text\nios/WenguaAppUI/WenguaNativeReadingRouter.swift:216:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
214 |         let fanyin=entire(actualStars,homeStars,true) ||
215 |                     entire(actualDoors,homeDoors,true)
216 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
217 |             fill(fiveNot ? "macro_five" : "macro_clear"),
218 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:159:65: error: expected ',' separator
157 |                 let extras=audit.auspiceBonusNotes.joined(separator:"|")
158 |                 FileHandle.standardError.write(Data(
159 |                   ("SIXJIA_2014_QIAN_NATIVE earth="+q.earthStem+
    |                                                                 `- error: expected ',' separator
160 |                    " stages="+stages+" tombs="+tombs+
161 |                    " god="+String(describing:q.deity)+

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:159:64: error: '+' is not a postfix unary operator
157 |                 let extras=audit.auspiceBonusNotes.joined(separator:"|")
158 |                 FileHandle.standardError.write(Data(
159 |                   ("SIXJIA_2014_QIAN_NATIVE earth="+q.earthStem+
    |                                                                `- error: '+' is not a postfix unary operator
160 |                    " stages="+stages+" tombs="+tombs+
161 |                    " god="+String(describing:q.deity)+

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:160:53: error: '+' is not a postfix unary operator
158 |                 FileHandle.standardError.write(Data(
159 |                   ("SIXJIA_2014_QIAN_NATIVE earth="+q.earthStem+
160 |                    " stages="+stages+" tombs="+tombs+
    |                                                     `- error: '+' is not a postfix unary operator
161 |                    " god="+String(describing:q.deity)+
162 |                    " auspice="+extras+"\n").utf8))

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:162:45: error: value of tuple type '(AttributedString, String)' has no member 'utf8'
160 |                    " stages="+stages+" tombs="+tombs+
161 |                    " god="+String(describing:q.deity)+
162 |                    " auspice="+extras+"\n").utf8))
    |                                             `- error: value of tuple type '(AttributedString, String)' has no member 'utf8'
163 |             }
164 |             let debugItems:[String]=[
\n\`\`\`\n\n## matrix_tests.log\n\n\`\`\`text\ntest_all_25_power_pairs_never_infer_strength_from_signed_grade (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_all_25_power_pairs_never_infer_strength_from_signed_grade) ... ok
test_both_real_clocks_account_for_actual_distinct_palaces (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_both_real_clocks_account_for_actual_distinct_palaces) ... ok
test_distinct_illness_host_allows_one_yi_ding_family (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_distinct_illness_host_allows_one_yi_ding_family) ... ok
test_independent_selected_host_any_role_or_any_order (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_independent_selected_host_any_role_or_any_order) ... ok
test_one_family_per_palace_and_complete_void_half_once (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_one_family_per_palace_and_complete_void_half_once) ... ok
test_same_physical_doctor_and_medicine_have_separate_energies (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_same_physical_doctor_and_medicine_have_separate_energies) ... ok
test_symbol_self_never_adds_once_or_under_different_role_alias (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_symbol_self_never_adds_once_or_under_different_role_alias) ... ok
test_yearstem_yi_is_not_yi_own_auspice (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_yearstem_yi_is_not_yi_own_auspice) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.107s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
\n\`\`\`\n