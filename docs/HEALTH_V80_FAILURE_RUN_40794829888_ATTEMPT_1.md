# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/40794829888\n\n\n## compile.log\n\n\`\`\`text\nios/WenguaAppUI/WenguaNativeReadingRouter.swift:211:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |         let fanyin=entire(actualStars,homeStars,true) ||
210 |                     entire(actualDoors,homeDoors,true)
211 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
212 |             fill(fiveNot ? "macro_five" : "macro_clear"),
213 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:40: error: expected ',' separator
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                                      `- error: expected ',' separator
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:416:49: error: '+' is not a postfix unary operator
414 |             throw WenguaNativeReadingError.missingRole
415 |         }
416 |         var illnessText="在"+label(illnessCell)+
    |                                               `- error: '+' is not a postfix unary operator
417 |             "，势"+(review.roleEnergy["illness"]?.strength ?? "待核")+
418 |             "，宫象"+signed(review.roleScores["illness"])

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:417:74: error: '+' is not a postfix unary operator
415 |         }
416 |         var illnessText="在"+label(illnessCell)+
417 |             "，势"+(review.roleEnergy["illness"]?.strength ?? "待核")+
    |                                                                  `- error: '+' is not a postfix unary operator
418 |             "，宫象"+signed(review.roleScores["illness"])
419 |         let illVoid=review.palaces[illID]?.void ?? "not_void"

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:418:24: warning: result of operator '+' is unused [#NoUsage]
416 |         var illnessText="在"+label(illnessCell)+
417 |             "，势"+(review.roleEnergy["illness"]?.strength ?? "待核")+
418 |             "，宫象"+signed(review.roleScores["illness"])
    |                  `- warning: result of operator '+' is unused [#NoUsage]
419 |         let illVoid=review.palaces[illID]?.void ?? "not_void"
420 |         if illVoid != "not_void" {

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:424:63: error: '+' is not a postfix unary operator
422 |         }
423 |         let patientSymbol=review.roleEnergy["patient"]?.symbol ?? "未核"
424 |         var patientText=patientSymbol+"在"+label(patientCell)+
    |                                                             `- error: '+' is not a postfix unary operator
425 |             "，宫象"+signed(review.roleScores["patient"])
426 |         let patientVoid=review.palaces[patientID]?.void ?? "not_void"

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:425:24: warning: result of operator '+' is unused [#NoUsage]
423 |         let patientSymbol=review.roleEnergy["patient"]?.symbol ?? "未核"
424 |         var patientText=patientSymbol+"在"+label(patientCell)+
425 |             "，宫象"+signed(review.roleScores["patient"])
    |                  `- warning: result of operator '+' is unused [#NoUsage]
426 |         let patientVoid=review.palaces[patientID]?.void ?? "not_void"
427 |         if patientVoid != "not_void" {

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:39: error: '+' is not a postfix unary operator
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                                     `- error: '+' is not a postfix unary operator
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:437:63: error: '+' is not a postfix unary operator
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
    |                                                           `- error: '+' is not a postfix unary operator
438 |                 "，"+conciseRelation(key))
439 |         }

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:22: error: generic parameter 'E' could not be inferred
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                      `- error: generic parameter 'E' could not be inferred
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

Swift.Array.append:2:22: note: in call to function 'append(addingCapacity:initializingWith:)'
1 | generic struct Array {
2 | public mutating func append<E>(addingCapacity uninitializedCount: Int, initializingWith initializer: @_lifetime(span: copy span) (_ span: inout OutputSpan<Element>) throws(E) -> Void) throws(E) where E : Error}
  |                      `- note: in call to function 'append(addingCapacity:initializingWith:)'
3 | 

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:28: error: missing argument labels 'addingCapacity:initializingWith:' in call
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                            `- error: missing argument labels 'addingCapacity:initializingWith:' in call
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

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
Ran 8 tests in 0.080s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
\n\`\`\`\n