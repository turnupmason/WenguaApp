# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/40951533712\n\n\n## matrix_tests.log\n\n\`\`\`text\ntest_all_25_power_pairs_never_infer_strength_from_signed_grade (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_all_25_power_pairs_never_infer_strength_from_signed_grade) ... ok
test_both_real_clocks_account_for_actual_distinct_palaces (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_both_real_clocks_account_for_actual_distinct_palaces) ... ok
test_distinct_illness_host_allows_one_yi_ding_family (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_distinct_illness_host_allows_one_yi_ding_family) ... ok
test_independent_selected_host_any_role_or_any_order (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_independent_selected_host_any_role_or_any_order) ... ok
test_one_family_per_palace_and_complete_void_half_once (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_one_family_per_palace_and_complete_void_half_once) ... ok
test_same_physical_doctor_and_medicine_have_separate_energies (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_same_physical_doctor_and_medicine_have_separate_energies) ... ok
test_symbol_self_never_adds_once_or_under_different_role_alias (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_symbol_self_never_adds_once_or_under_different_role_alias) ... ok
test_yearstem_yi_is_not_yi_own_auspice (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_yearstem_yi_is_not_yi_own_auspice) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.067s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... 
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/scoring/health_quant_overlay_vnext.py') ... FAIL

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/scoring/health_quant_overlay_vnext.py')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'"""[30140 chars]     ground_restricted=_matching_restriction(\[19470 chars]")\n' != b'"""[30140 chars]     # earth_tombs from inspect_palace is BRAN[20007 chars]")\n' : src/wengua/health_quant_overlay_vnext.py does not match Important mirror

----------------------------------------------------------------------
Ran 1 test in 0.005s

FAILED (failures=1)
\n\`\`\`\n