# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41245392771
Source: 8f23378e28de981a69e314109b625c4bce987e37

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

## 1 2010-02-02T07:00:00-05:00 (朋友): MISMATCH
Python sections 9, Swift sections 9; character lengths 853 and 843
Section records differ (including IDs, order or text):
{"ios_sections": [{"id": "01_macro", "text": "本时不犯五不遇。 星门无整盘伏吟反吟，应期须另参。", "title": "时局总纲"}, {"id": "02", "text": "落离九宫；九星天芮星极大凶，八门死门极大凶，八神白虎被宫克、小凶；天盘干乙势大、庚势极大，地盘干丁势大；天地格：乙加丁「奇仪相佐」（吉）、庚加丁「亭亭之格」（凶）；空亡不空、无特别刑墓迫。宫象极大凶。 病星格局「迅速恶化」。", "title": "天芮病宫"}, {"id": "03", "text": "落兑七宫；九星天心星极小吉，八门开门大吉，八神九地生宫、中凶；天盘干辛势极大，地盘干壬势中等；天地格：辛加壬「凶蛇入狱」（凶）；空亡不空、无特别刑墓迫。宫象中凶。 天心星势极小；受病宫克，制约轻重依双方实际力量。", "title": "天心医生"}, {"id": "04", "text": "与前述天芮病宫同在离九宫，合看该宫象。 乙势大；与病宫同宫，不另作跨宫克制。", "title": "乙奇医药"}, {"id": "05", "text": "落巽四宫；九星天英星极大凶，八门景门中平，八神六合比和、大吉；天盘干丁，地盘干己；天地格：丁加己「火入勾陈」（凶）；空亡不空、无特别刑墓迫。宫象极小凶。 丁势待核；生扶病宫，不作制病。", "title": "患者用神"}, {"id": "06", "text": "落乾六宫；九星天蓬星中凶，八门休门小吉，八神九天比和、大吉；天盘干丙势极小，地盘干辛势极大；天地格：丙加辛「奇神相合」（吉）；空亡不空、天盘入墓。宫象极大吉。 丙势极小；受病宫克，制约轻重依双方实际力量。", "title": "时干事体"}, {"id": "07", "text": "落坎一宫；九星天任星中吉，八门生门大吉，八神值符克宫、中吉；天盘干癸势中等，地盘干丙势中等；天地格：癸加丙「华盖孛师」（吉）；空亡真空、门破。宫象小吉。 值符势中等；逢空，护持受限。", "title": "值符护持宫"}, {"id": "90_review", "text": "病星天芮在离九宫，势极大，宫象极大凶；患者丁在巽四宫，势待核，宫象极小凶，生扶病宫。\n\n医药两端分别看：天心势极小，受病宫克，乙奇势大，与病宫同宫。\n\n另参时干事体丙在乾六宫，势极小，受病宫克；大吉神值符在坎一宫，势中等，克病未成；离九宫得天盘乙奇与地盘丁奇同宫扶助；值符逢空，护持受限。\n\n综上所述，此病为极小吉；以上仅作传统古籍象意参考，不作现实病情判断。", "title": "综合断语"}, {"id": "91_timing", "text": "驿马在寅；应期仍须参空、墓、冲合，证据不足不定日。", "title": "时空及应期"}], "python_sections": [{"id": "01_macro", "text": "本时不犯五不遇。 星门无整盘伏吟反吟，应期须另参。", "title": "时局总纲"}, {"id": "02", "text": "落离九宫；九星天芮星极大凶，八门死门极大凶，八神白虎被宫克、小凶；天盘干乙势大、庚势极大，地盘干丁势大；天地格：乙加丁「奇仪相佐」（吉）、庚加丁「亭亭之格」（凶）；空亡不空、无特别刑墓迫。宫象极大凶。 病星格局「迅速恶化」。", "title": "天芮病宫"}, {"id": "03", "text": "落兑七宫；九星天心星极小吉，八门开门大吉，八神九地生宫、中凶；天盘干辛势极大，地盘干壬势中等；天地格：辛加壬「凶蛇入狱」（凶）；空亡不空、无特别刑墓迫。宫象中凶。 天心星势极小；受病宫克，制约轻重依双方实际力量。", "title": "天心医生"}, {"id": "04", "text": "与前述天芮病宫同在离九宫，合看该宫象。 乙势大；与病宫同宫，不另作跨宫克制。", "title": "乙奇医药"}, {"id": "05", "text": "落巽四宫；九星天英星极大凶，八门景门中平，八神六合比和、大吉；天盘干丁，地盘干己；天地格：丁加己「火入勾陈」（凶）；空亡不空、无特别刑墓迫。宫象极小凶。 丁势待核（十二长生分支待辨）；生扶病宫，不作制病。", "title": "患者用神"}, {"id": "06", "text": "落乾六宫；九星天蓬星中凶，八门休门小吉，八神九天比和、大吉；天盘干丙势极小，地盘干辛势极大；天地格：丙加辛「奇神相合」（吉）；空亡不空、天盘入墓。宫象极大吉。 丙势极小；受病宫克，制约轻重依双方实际力量。", "title": "时干事体"}, {"id": "07", "text": "落坎一宫；九星天任星中吉，八门生门大吉，八神值符克宫、中吉；天盘干癸势中等，地盘干丙势中等；天地格：癸加丙「华盖孛师」（吉）；空亡真空、门破。宫象小吉。 值符势中等；逢空，护持受限。", "title": "值符护持宫"}, {"id": "90_review", "text": "病星天芮在离九宫，势极大，宫象极大凶；患者丁在巽四宫，势待核，宫象极小凶，生扶病宫。\n\n医药两端分别看：天心势极小，受病宫克，乙奇势大，与病宫同宫。\n\n另参时干事体丙在乾六宫，势极小，受病宫克；大吉神值符在坎一宫，势中等，克病未成；离九宫得天盘乙奇与地盘丁奇同宫扶助；值符逢空，护持受限。\n\n综上所述，此病为极小吉；以上仅作传统古籍象意参考，不作现实病情判断。", "title": "综合断语"}, {"id": "91_timing", "text": "驿马在寅；应期仍须参空、墓、冲合，证据不足不定日。", "title": "时空及应期"}]}

DIFF START
--- live_Python_GPT_Vnext
+++ native_iOS_Vnext
@@ -12,5 +12,5 @@
 
 患者用神：
-落巽四宫；九星天英星极大凶，八门景门中平，八神六合比和、大吉；天盘干丁，地盘干己；天地格：丁加己「火入勾陈」（凶）；空亡不空、无特别刑墓迫。宫象极小凶。 丁势待核（十二长生分支待辨）；生扶病宫，不作制病。
+落巽四宫；九星天英星极大凶，八门景门中平，八神六合比和、大吉；天盘干丁，地盘干己；天地格：丁加己「火入勾陈」（凶）；空亡不空、无特别刑墓迫。宫象极小凶。 丁势待核；生扶病宫，不作制病。
 
 时干事体：
DIFF END


Exact equality: 0 of 1
ISSUES: 2010-02-02T07:00:00-05:00 朋友 FULL_TEXT_MISMATCH 
VERDICT: FAIL - cannot claim complete iOS migration.
```
## regression.log
```text
No output from this stage
```
