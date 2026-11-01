# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41342773278
Source: 9b3366b1b427d27da208ab863cd97a300e510e8a

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:232:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
230 |         let fanyin=entire(actualStars,homeStars,true) ||
231 |                     entire(actualDoors,homeDoors,true)
232 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
233 |             fill(fiveNot ? "macro_five" : "macro_clear"),
234 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
```
## diff.md
```text
# STRICT GPT-Python versus iOS native literal reading parity

Both entire paragraphs and their headings, line breaks, punctuation must match.
No whitespace normalization or omitted sections is permitted.

## 1 2010-02-02T07:00:00-05:00: EXACT MATCH (text + all section IDs/titles/bodies)

Exact equality: 1 of 1
ISSUES: none
VERDICT: PASS
```
## regression.log
```text
.FFF.....
======================================================================
FAIL: test_real_chief_under_illness_control_and_void_do_not_vote (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_real_chief_under_illness_control_and_void_do_not_vote) (instant='2022-07-19T11:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 82, in test_real_chief_under_illness_control_and_void_do_not_vote
    self.assertFalse(chief["score_eligible"])
AssertionError: True is not false

======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2021-10-03T03:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 57, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertEqual(q["summary"]["unique_palace_count"],len(selected))
AssertionError: 4 != 3

======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2023-04-24T21:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 57, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertEqual(q["summary"]["unique_palace_count"],len(selected))
AssertionError: 5 != 4

----------------------------------------------------------------------
Ran 8 tests in 0.485s

FAILED (failures=3)
```
