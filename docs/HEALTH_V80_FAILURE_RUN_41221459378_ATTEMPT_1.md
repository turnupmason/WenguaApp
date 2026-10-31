# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/41221459378\n\n\n## matrix_tests.log\n\n\`\`\`text\ntest_all_25_power_pairs_never_infer_strength_from_signed_grade (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_all_25_power_pairs_never_infer_strength_from_signed_grade) ... ok
test_both_real_clocks_account_for_actual_distinct_palaces (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_both_real_clocks_account_for_actual_distinct_palaces) ... ok
test_distinct_illness_host_allows_one_yi_ding_family (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_distinct_illness_host_allows_one_yi_ding_family) ... ok
test_independent_selected_host_any_role_or_any_order (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_independent_selected_host_any_role_or_any_order) ... ok
test_one_family_per_palace_and_complete_void_half_once (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_one_family_per_palace_and_complete_void_half_once) ... ok
test_same_physical_doctor_and_medicine_have_separate_energies (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_same_physical_doctor_and_medicine_have_separate_energies) ... ok
test_symbol_self_never_adds_once_or_under_different_role_alias (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_symbol_self_never_adds_once_or_under_different_role_alias) ... ok
test_yearstem_yi_is_not_yi_own_auspice (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_yearstem_yi_is_not_yi_own_auspice) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.062s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... 
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/data/knowledge/phrase_library/health_v20/actor_profiles.json') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/templates/templates/health_severity_vnext/reading_template.json') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/engine/domain_selected_energy_vnext.py') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/reading/health_reading_template_vnext.py') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/data/knowledge/phrase_library/health_v20/actor_profiles.json') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/templates/templates/health_severity_vnext/reading_template.json') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/ui/WenguaDesignPreviewApp.swift') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/engine/WenguaNativeActorBinding.swift') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/engine/WenguaPythonVNextVerbatim.swift') ... FAIL
  test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/engine/health_dynamic_v21.py') ... FAIL

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/data/knowledge/phrase_library/health_v20/actor_profiles.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'{\n[39 chars]es_v90_friends_20261031",\n  "domain": "health[31554 chars]n}\n' != b'{\n[39 chars]es_v91_friend_month_only_20261031",\n  "domain[30886 chars]n}\n' : data/knowledge/phrase_library/health_v20/actor_profiles.json does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/templates/templates/health_severity_vnext/reading_template.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'{\n[54 chars]0261028_v10_2_evidence_first",\n  "formation":[32805 chars]n}\n' != b'{\n[54 chars]0261031_v11_full_evidence",\n  "formation": "{[33497 chars]n}\n' : data/templates/health_severity_vnext/reading_template.json does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/engine/domain_selected_energy_vnext.py')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'"""[34443 chars] # V10.2: audience conclusion selects only dec[4750 chars]ns\n' != b'"""[34443 chars] # V11: preserve V10.1 evidence depth, clarify[6231 chars]ns\n' : src/wengua/domain_selected_energy_vnext.py does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/reading/health_reading_template_vnext.py')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'"""[206 chars]es.\nOnly current V10.2 wording is accepted; f[2456 chars]s)\n' != b'"""[206 chars]es.\nV11 detailed role evidence; frozen V8 sou[2458 chars]s)\n' : src/wengua/health_reading_template_vnext.py does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/data/knowledge/phrase_library/health_v20/actor_profiles.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'{\n[39 chars]es_v90_friends_20261031",\n  "domain": "health[31554 chars]n}\n' != b'{\n[39 chars]es_v91_friend_month_only_20261031",\n  "domain[30886 chars]n}\n' : data/knowledge/phrase_library/health_v20/actor_profiles.json does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/templates/templates/health_severity_vnext/reading_template.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'{\n[54 chars]0261028_v10_2_evidence_first",\n  "formation":[32805 chars]n}\n' != b'{\n[54 chars]0261031_v11_full_evidence",\n  "formation": "{[33497 chars]n}\n' : data/templates/health_severity_vnext/reading_template.json does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/ui/WenguaDesignPreviewApp.swift')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'imp[68145 chars]="\xe6\x9c\x8b\xe5\x8f\x8b" || subject=="\xe7\[32094 chars]n}\n' != b'imp[68145 chars]="\xe7\x88\xb6\xe6\xaf\x8d" ||\n              [30738 chars]n}\n' : ios/WenguaAppUI/WenguaDesignPreviewApp.swift does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/engine/WenguaNativeActorBinding.swift')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'imp[7138 chars]     if profile.id=="friend" {\n            gu[5995 chars]n}\n' != b'imp[7138 chars]     // Friends always use the true casting mo[5569 chars]n}\n' : ios/WenguaAppUI/WenguaNativeActorBinding.swift does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/swift/engine/WenguaPythonVNextVerbatim.swift')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'imp[25003 chars]der")\n        ] {\n            guard let pid=[7708 chars]n}\n' != b'imp[25003 chars]der"),\n            ("sibling","09a","sibling"[9893 chars]n}\n' : ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift does not match Important mirror

======================================================================
FAIL: test_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) (snapshot='Important/python/engine/health_dynamic_v21.py')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_important_mirror_integrity_20261026.py", line 29, in test_all_selected_important_snapshots_match_canonical_bytes
    self.assertEqual(copied.read_bytes(), source.read_bytes(),
AssertionError: b'"""[10836 chars]  # V9: \xe6\x9c\x8b\xe5\x8f\x8b\xe6\x9c\xac\x[43211 chars] }\n' != b'"""[10836 chars]  # V11: friend is a peer, not a family siblin[41602 chars] }\n' : src/wengua/health_dynamic_v21.py does not match Important mirror

----------------------------------------------------------------------
Ran 1 test in 0.010s

FAILED (failures=10)
\n\`\`\`\n