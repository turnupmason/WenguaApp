# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41222093963
Source: fa7749cf720c59e8d8d43bb0bd4197201d320c65

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:216:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
214 |         let fanyin=entire(actualStars,homeStars,true) ||
215 |                     entire(actualDoors,homeDoors,true)
216 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
217 |             fill(fiveNot ? "macro_five" : "macro_clear"),
218 |             fill(fuyin && fanyin ? "macro_mixed" :

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
.FFFF.F..F
======================================================================
FAIL: test_real_chief_under_illness_control_and_void_do_not_vote (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_real_chief_under_illness_control_and_void_do_not_vote) (instant='2022-07-19T11:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 80, in test_real_chief_under_illness_control_and_void_do_not_vote
    self.assertFalse(chief["score_eligible"])
AssertionError: True is not false

======================================================================
FAIL: test_real_chief_under_illness_control_and_void_do_not_vote (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_real_chief_under_illness_control_and_void_do_not_vote) (instant='2026-11-16T21:00:00-05:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 78, in test_real_chief_under_illness_control_and_void_do_not_vote
    self.assertIn("值符大吉神与天芮病宫同宫",r["reading_text"])
AssertionError: '值符大吉神与天芮病宫同宫' not found in '时局总纲：\n本时不犯五不遇。 星门无整盘伏吟反吟，应期须另参。\n\n天芮病宫：\n落兑七宫；九星天芮星小凶，八门休门极大吉，八神值符生宫、中吉；天盘干壬势极大、己势大，地盘干乙势小；天地格：壬加乙「小蛇」（吉）、己加乙「墓神不明」（凶）；空亡真空、无特别刑墓迫。宫象小吉。 病星格局「残存流逝」。\n\n天心医生：\n落坎一宫；九星天心星大吉，八门伤门极大凶，八神九地克宫、中凶；天盘干戊势中等，地盘干癸势极大；天地格：戊加癸「青龙华盖」（吉）；空亡不空、无特别刑墓迫。宫象中平。 天心星势大；受病宫生，非主动制病。\n\n乙奇医药：\n落乾六宫；九星天柱星极大凶，八门生门极小吉，八神九天比和、大吉；天盘干乙势小，地盘干戊势极小；天地格：乙加戊「利阴害阳」（凶）；空亡不空、天盘入墓、地盘入墓。宫象小凶。 乙势小；与病宫比和，不等于等力。\n\n患者用神：\n落震三宫；九星天任星极小吉，八门景门中平，八神白虎克宫、中凶；天盘干丙势中等，地盘干辛势极小；天地格：丙加辛「奇神相合」（吉）；空亡不空、无特别刑墓迫。宫象中吉。 丙势中等；受病宫克，制约轻重依双方实际力量。\n\n时干事体：\n与前述乙奇医药同在乾六宫，合看该宫象。\n\n值符护持宫：\n与前述天芮病宫同在兑七宫，合看该宫象。 值符势中等；逢空，护持受限。\n\n乾宫辅助（男）：\n与前述乙奇医药同在乾六宫，合看该宫象。 天柱星势极大；与病宫比和，不等于等力。\n\n综合断语：\n病星天芮在兑七宫，势小，宫象小吉，逢真空；患者丙在震三宫，势中等，宫象中吉，受病宫克。\n\n医药两端分别看：天心势大，受病宫生，乙奇势小，与病宫比和。\n\n另参长辈乾坤辅助天柱星在乾六宫，势极大，与病宫比和；大吉神值符在兑七宫，势中等，与病宫同宫；乾六宫得天盘乙奇同宫扶助；兑七宫逢空，值符同宫的吉助减弱，尚有余气；值符逢空，护持受限。\n\n综上所述，此病为极大吉；以上仅作传统古籍象意参考，不作现实病情判断。\n\n时空及应期：\n驿马在巳；应期仍须参空、墓、冲合，证据不足不定日。'

======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2021-10-03T03:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 42, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertIn("用神力量为",r["reading_text"])
AssertionError: '用神力量为' not found in '时局总纲：\n本时不犯五不遇。 星门无整盘伏吟反吟，应期须另参。\n\n天芮病宫：\n落乾六宫；九星天芮星大凶，八门惊门极大凶，八神六合被宫克、小吉；天盘干乙势极小、癸，地盘干壬势极大；天地格：乙加壬「日奇入地」（凶）、癸加壬「复见螣蛇」（凶）；空亡假空、天盘入墓。宫象小凶。 病星格局「疯狂消耗」。\n\n天心医生：\n落艮八宫；九星天心星极大吉，八门休门小吉，八神螣蛇生宫、中凶；天盘干壬势大，地盘干庚势极小；天地格：壬加庚「太白擒蛇」（吉）；空亡不空、地盘入墓、门迫。宫象极大吉。 天心星势极大；生扶病宫，不作制病。\n\n乙奇医药：\n与前述天芮病宫同在乾六宫，合看该宫象。 乙势极小；与病宫同宫，不另作跨宫克制。\n\n患者用神：\n与前述天芮病宫同在乾六宫，合看该宫象。\n\n时干事体：\n落离九宫；九星天冲星极小吉，八门杜门中平，八神九地被宫生、极大凶；天盘干丙势大，地盘干己势大；天地格：丙加己「火孛入刑」（凶）；空亡不空、无特别刑墓迫。宫象极大凶。 丙势大；虽有克向，效力未定。\n\n值符护持宫：\n落震三宫；九星天蓬星极小凶，八门生门极小吉，八神值符被宫克、小吉；天盘干戊势大，地盘干丙势大；天地格：戊加丙「青龙返首」（吉）；空亡不空、六仪击刑、门迫。宫象极大吉。 值符势小；受病宫克，制约轻重依双方实际力量。\n\n综合断语：\n病星天芮在乾六宫，势大，宫象小凶，逢假空；患者乙在乾六宫，势极小，宫象小凶，逢假空。\n\n医药两端分别看：天心势极大，生扶病宫，乙奇势极小，与病宫同宫。\n\n另参时干事体丙在离九宫，势大，虽克病，效力未明；大吉神值符在震三宫，势小，受病宫克；乾六宫逢空，天盘乙奇同宫的吉助减弱，尚有余气。\n\n综上所述，此病为中吉；以上仅作传统古籍象意参考，不作现实病情判断。\n\n时空及应期：\n驿马在申；应期仍须参空、墓、冲合，证据不足不定日。'

======================================================================
FAIL: test_same_two_actual_wife_clocks_use_current_role_strength_and_control (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_same_two_actual_wife_clocks_use_current_role_strength_and_control) (instant='2023-04-24T21:00:00-04:00')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 42, in test_same_two_actual_wife_clocks_use_current_role_strength_and_control
    self.assertIn("用神力量为",r["reading_text"])
AssertionError: '用神力量为' not found in '时局总纲：\n本时不犯五不遇。 星门无整盘伏吟反吟，应期须另参。\n\n天芮病宫：\n落震三宫；九星天芮星小凶，八门休门极小吉，八神螣蛇被宫生、极大凶；天盘干丁势小、戊势极大，地盘干丙势大；天地格：丁加丙「星随月转」（吉）、戊加丙「青龙返首」（吉）；空亡真空、六仪击刑。宫象小凶。 病星格局「萌芽被扼」。\n\n天心医生：\n落离九宫；九星天心星极小吉，八门伤门极小凶，八神六合生宫、中吉；天盘干己势极大，地盘干壬势小；天地格：己加壬「地网高张」（凶）；空亡不空、无特别刑墓迫。宫象小凶。 天心星势极小；受病宫生，非主动制病。\n\n乙奇医药：\n落坎一宫；九星天辅星大吉，八门惊门中凶，八神九天生宫、中吉；天盘干乙势小，地盘干癸势中等；天地格：乙加癸「华盖青龙」（吉）；空亡不空、无特别刑墓迫。宫象极大吉。 乙势小；生扶病宫，不作制病。\n\n患者用神：\n与前述乙奇医药同在坎一宫，合看该宫象。\n\n时干事体：\n落兑七宫；九星天任星中吉，八门景门中平，八神玄武被宫生、极大凶；天盘干辛势极大，地盘干庚势极大；天地格：辛加庚「白虎出力」（凶）；空亡不空、门破。宫象极大凶。 辛势极大；虽有克向，效力未定。\n\n值符护持宫：\n落艮八宫；九星天英星大凶，八门开门极大吉，八神值符比和、大吉；天盘干壬势极小，地盘干辛势极大；天地格：壬加辛「螣蛇相缠」（凶）；空亡假空、无特别刑墓迫。宫象极小凶。 值符势大；逢空，护持受限。\n\n综合断语：\n病星天芮在震三宫，势小，宫象小凶，逢真空；患者乙在坎一宫，势小，宫象极大吉。\n\n医药两端分别看：天心势极小，受病宫生，乙奇势小，生扶病宫。\n\n另参时干事体辛在兑七宫，势极大，虽克病，效力未明；大吉神值符在艮八宫，势大，受病宫克；震三宫逢空，天盘丁奇同宫的吉助减弱，尚有余气；值符逢空，护持受限。\n\n综上所述，此病为大凶；以上仅作传统古籍象意参考，不作现实病情判断。\n\n时空及应期：\n驿马在巳；应期仍须参空、墓、冲合，证据不足不定日。'

======================================================================
FAIL: test_v61_customer_prose_keeps_source_score_but_hides_internal_formulae (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_v61_customer_prose_keeps_source_score_but_hides_internal_formulae)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 121, in test_v61_customer_prose_keeps_source_score_but_hides_internal_formulae
    self.assertIn("天心医生宫克天芮病宫",public)
AssertionError: '天心医生宫克天芮病宫' not found in '时局总纲：\n本时不犯五不遇。 反吟主快。\n\n天芮病宫：\n落艮八宫；九星天芮星小凶，八门开门中吉，八神值符比和、大吉；天盘干庚势极小、癸势大，地盘干乙；天地格：庚加乙「太白蓬星」（凶）、癸加乙「华盖蓬星」（吉）；空亡真空、天盘入墓、六仪击刑。宫象小吉。 病星格局「潜伏菌群」。\n\n天心医生：\n落巽四宫；九星天心星小吉，八门生门极小吉，八神太阴克宫、中吉；天盘干丁，地盘干壬势极小；天地格：丁加壬「五神互合」（吉）；空亡不空、地盘入墓、门迫、本宫驿马。宫象极大吉。 天心星势小；虽有克向，效力未定。\n\n乙奇医药：\n落坤二宫；九星天任星小吉，八门杜门中平，八神白虎被宫生、极大凶；天盘干乙势大，地盘干庚势大、中五寄干癸；天地格：乙加庚「日奇被刑」（凶）、乙加癸「华盖青龙」（吉）；空亡不空、门破。宫象极大凶。 坤二承中五寄干，两重天地格并参，中五不另起宫象。 乙势大；与病宫比和，不等于等力。\n\n患者用神：\n与前述乙奇医药同在坤二宫，合看该宫象。\n\n时干事体：\n与前述乙奇医药同在坤二宫，合看该宫象。\n\n值符护持宫：\n与前述天芮病宫同在艮八宫，合看该宫象。 值符势大；逢空，护持受限。\n\n综合断语：\n病星天芮在艮八宫，势小，宫象小吉，逢真空；患者乙在坤二宫，势大，宫象极大凶。\n\n医药两端分别看：天心势小，虽克病，效力未明，乙奇势大，与病宫比和。\n\n另参大吉神值符在艮八宫，势大，与病宫同宫；艮八宫逢空，值符同宫的吉助减弱，尚有余气；值符逢空，护持受限。\n\n综上所述，此病为中吉；以上仅作传统古籍象意参考，不作现实病情判断。\n\n时空及应期：\n驿马在巳；应期仍须参空、墓、冲合，证据不足不定日。'

======================================================================
FAIL: test_very_weak_illness_generates_two_roles_in_one_physical_palace (test_health_vnext_exact_role_matrix_gate_20261026.ExactRoleMatrixGate.test_very_weak_illness_generates_two_roles_in_one_physical_palace)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_vnext_exact_role_matrix_gate_20261026.py", line 98, in test_very_weak_illness_generates_two_roles_in_one_physical_palace
    self.assertIn("病星本已极弱，反去生助",r["reading_text"])
AssertionError: '病星本已极弱，反去生助' not found in '时局总纲：\n本时不犯五不遇。 伏吟主慢。\n\n天芮病宫：\n落坤二宫；九星天芮星极小凶，八门杜门中平，八神太阴被宫生、极大吉；天盘干丙势中等、壬，地盘干丙势中等、中五寄干壬；天地格：丙加丙「月奇孛师」（凶）、壬加壬「蛇入地罗」（凶）；空亡不空、门破。宫象极小吉。 坤二承中五寄干，两重天地格并参，中五不另起宫象。 病星格局「无害残留」。\n\n天心医生：\n落乾六宫；九星天心星小吉，八门死门中凶，八神值符生宫、中吉；天盘干辛势中等，地盘干辛势中等；天地格：辛加辛「伏吟天庭」（凶）；空亡不空、本宫驿马。宫象中凶。 天心星势小；受病宫生，非主动制病。\n\n乙奇医药：\n落坎一宫；九星天蓬星中凶，八门惊门极小凶，八神九天生宫、中吉；天盘干乙势小，地盘干乙势小；天地格：乙加乙「日奇伏吟」（凶）；空亡不空、无特别刑墓迫。宫象大凶。 乙势小；受病宫克，制约轻重依双方实际力量。\n\n患者用神：\n与前述天芮病宫同在坤二宫，合看该宫象。 壬势待核；与病宫同宫，不另作跨宫克制。\n\n时干事体：\n与前述天心医生同在乾六宫，合看该宫象。 辛势中等；受病宫生，非主动制病。\n\n值符护持宫：\n与前述天心医生同在乾六宫，合看该宫象。 值符势中等；受病宫生，非主动制病。\n\n综合断语：\n病星天芮在坤二宫，势极小，宫象极小吉；患者壬在坤二宫，势待核，宫象极小吉，与病宫同宫。\n\n医药两端分别看：天心势小，受病宫生，乙奇势小，受病宫克。\n\n另参时干事体辛在乾六宫，势中等，受病宫生；大吉神值符在乾六宫，势中等，受病宫生；病星外泄，病气受耗；乾六宫得值符与天心星同宫扶助。\n\n综上所述，此病为中吉；以上仅作传统古籍象意参考，不作现实病情判断。\n\n时空及应期：\n驿马在亥；应期仍须参空、墓、冲合，证据不足不定日。'

----------------------------------------------------------------------
Ran 8 tests in 0.481s

FAILED (failures=6)
```
