# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41343617893
Source: d4e51b794808ee483c008ec5d8a443cdb3154258

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
..F.....
======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2023-04-24T21:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 64, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertIn("不能压制病宫",chief["reason"])
AssertionError: '不能压制病宫' not found in '值符空亡，不提供护持'

----------------------------------------------------------------------
Ran 8 tests in 0.290s

FAILED (failures=1)
```
