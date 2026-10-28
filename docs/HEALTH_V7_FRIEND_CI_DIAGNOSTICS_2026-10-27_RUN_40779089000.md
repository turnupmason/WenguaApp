# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40779089000
Source: 24c5bbbdf7f1970279897bb35650a47d8912d7ea

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:211:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |         let fanyin=entire(actualStars,homeStars,true) ||
210 |                     entire(actualDoors,homeDoors,true)
211 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
212 |             fill(fiveNot ? "macro_five" : "macro_clear"),
213 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:217:13: warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
215 |         let doorPart=try signedSymbol("door",door,palace:p.id,
216 |                                       month:month,energy:energy)
217 |         let hasIllness=p.heavenStars.contains{$0.star=="天芮星"}
    |             `- warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
218 |         // Each actual sky carrier has a distinct 81 pattern; do not
219 |         // mis-attribute Tianqin's carried stem to Tianrui.

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:314:13: warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
312 |         // net +/- score of either resident physical palace.
313 |         let note=baseNote+targetPowerSentence
314 |         let outcome=edge.cell
    |             `- warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
315 |         let applicable=["strong","limited"].contains(edge.applicability)
316 |         let eligible:Bool

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:316:13: warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
314 |         let outcome=edge.cell
315 |         let applicable=["strong","limited"].contains(edge.applicability)
316 |         let eligible:Bool
    |             `- warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
317 |         if role=="chief" {
318 |             eligible=review.palaces[aid]?.void=="not_void" &&

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
.FFF....F
======================================================================
FAIL: test_real_chief_under_illness_control_and_void_do_not_vote (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_real_chief_under_illness_control_and_void_do_not_vote) (instant='2022-07-19T11:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 80, in test_real_chief_under_illness_control_and_void_do_not_vote
    self.assertFalse(chief["score_eligible"])
AssertionError: True is not false

======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2021-10-03T03:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 56, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertEqual(q["summary"]["unique_palace_count"],len(selected))
AssertionError: 4 != 3

======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2023-04-24T21:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 56, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertEqual(q["summary"]["unique_palace_count"],len(selected))
AssertionError: 5 != 4

======================================================================
FAIL: test_very_weak_illness_generates_two_roles_in_one_physical_palace (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_very_weak_illness_generates_two_roles_in_one_physical_palace)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 98, in test_very_weak_illness_generates_two_roles_in_one_physical_palace
    self.assertIn("病星本已极弱，反去生助",r["reading_text"])
AssertionError: '病星本已极弱，反去生助' not found in '时辰总纲：\n不构成五不遇时（已按日干、时干五行克制及阴阳同类核对）。 九星伏吟、八门非伏吟反吟。伏吟主慢。 缓急不自动等于吉凶。\n\n天芮病宫：\n落坤二宫；九星天芮星极小凶；八神太阴被宫生、极大吉；八门杜门中平；天盘干丙势中等、壬、地盘干丙势中等、中五寄干壬；天地格：丙加丙「月奇孛师」（凶）。古文：文书逼迫，破耗遗失；古诀大意：急躁生乱，易有损耗；天地盘取象：两个丙阳火叠加，火势过烈，如荧惑扰乱军师；壬加壬「蛇入地罗」（凶）。古文：星门俱吉，庶免蹉跎；古诀大意：内外事务互相牵制，吉星吉门可缓；天地盘取象：两个甲辰壬重叠，蛇身相缠、罗网叠加，如蛇钻进自身织成的网；坤二承中五寄干，两重天地格并参，中五不另起宫象；空亡不空；门破。八门压制宫力量，吉事不吉，凶事更凶。全部因素推断后，此宫为极小吉。 传统病星格局「无害残留」。\n\n天心医生：\n落乾六宫；九星天心星小吉；八神值符生宫、中吉；八门死门中凶；天盘干辛势中等、地盘干辛势中等；天地格：辛加辛「伏吟天庭」（凶）。古文：公废私就，讼狱自罹罪名；古诀大意：公务不利，私务可能有成；天地盘取象：两个辛金同临天庭，刑责之气重叠，如两面刀刃互相伤害；空亡不空；本宫驿马。全部因素推断后，此宫为中凶。 天心星月令囚、比和，用神力量为小。天芮病星用神力量为极小。天心医生宫受天芮病宫生，方向上受病宫生扶，实际承受力量按双方用神判断，非主动克病。\n\n乙奇医药：\n落坎一宫；九星天蓬星中凶；八神九天生宫、中吉；八门惊门极小凶；天盘干乙势小、地盘干乙势小；天地格：乙加乙「日奇伏吟」（凶）。古文：只可安分守身；古诀大意：不利进取，宜守本分；天地盘取象：两个乙木、两个日奇重叠，形成原地重复之象；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为大凶。 乙天干十二长生衰 / 病、生月令，用神力量为小。天芮病星用神力量为极小。乙奇医药宫受天芮病宫克，病宫用神有力压制本方，制约较明显。\n\n患者用神：\n与前述天芮病宫同在坤二宫，合看该宫象。 壬天干与月令关系为克月令，其本宫力量仍待核实。天芮病星用神力量为极小。患者用神与天芮病宫同宫，意思为：双方同宫，不另论跨宫克制。\n\n时干事体：\n与前述天心医生同在乾六宫，合看该宫象。 辛天干十二长生长生/冠带/临官/帝旺/沐浴、被月令克，用神力量为中等。天芮病星用神力量为极小。时干事体宫受天芮病宫生，方向上受病宫生扶，实际承受力量按双方用神判断，非主动克病。\n\n值符护持宫：\n与前述天心医生同在乾六宫，合看该宫象。 值符按神宫生宫，用神力量为中等。天芮病星用神力量为极小。值符大吉神宫受天芮病宫生，方向上受病宫生扶，实际承受力量按双方用神判断，非主动克病。\n\n全部证据合断：\n伏吟主慢；天芮病宫落坤二宫，宫象极小吉，其中天芮星用神力量极小；天心医生落乾六宫，宫象中凶，其中天心星用神力量小，受病宫生；乙奇医药落坎一宫，宫象大凶，其中乙用神力量小，受病宫克；患者用神与天芮病宫同在坤二宫，其中壬用神力量待核，与病宫同宫；时干事体与天心医生同在乾六宫，其中辛用神力量中等，受病宫生；值符与天心医生同在乾六宫，其中值符用神力量中等，受病宫生；病星势弱而外泄，病气有耗损之象；乾六宫得值符与天心星同宫扶助。\n\n综上所述，此病为中吉；以上只作传统古籍象意参考，不能据此判断真实病情。\n\n时空及应期：\n时马在亥；应期须另有空、墓、冲合及问事情境支持，不能直接断定某一天。'

----------------------------------------------------------------------
Ran 8 tests in 0.469s

FAILED (failures=4)
```
