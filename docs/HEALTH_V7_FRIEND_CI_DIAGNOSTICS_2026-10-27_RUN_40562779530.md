# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40562779530
Source: e9721d58d044c986e8623ea4c6c332db92aa7c5e

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:208:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
206 |         let fanyin=entire(actualStars,homeStars,true) ||
207 |                     entire(actualDoors,homeDoors,true)
208 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |             fill(fiveNot ? "macro_five" : "macro_clear"),
210 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:291:13: warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
289 |         let rel=relation(aid,pid)
290 |         let note=try powerNote(role,p,own,chart:chart)
291 |         let outcome=edge.cell
    |             `- warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
292 |         let applicable=["strong","limited"].contains(edge.applicability)
293 |         let eligible:Bool

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:293:13: warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
291 |         let outcome=edge.cell
292 |         let applicable=["strong","limited"].contains(edge.applicability)
293 |         let eligible:Bool
    |             `- warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
294 |         if role=="chief" {
295 |             eligible=review.palaces[aid]?.void=="not_void" &&

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
```
## diff.md
```text
# STRICT GPT-Python versus iOS native literal reading parity

Both entire paragraphs and their headings, line breaks, punctuation must match.
No whitespace normalization or omitted sections is permitted.

## 1 2010-02-02T07:00:00-05:00 (朋友): MISMATCH
Python sections 9, Swift sections 9; character lengths 1461 and 1448
Section records differ (including IDs, order or text):
{"ios_sections": [{"id": "01_macro", "text": "不构成五不遇时（已按日干、时干五行克制及阴阳同类核对）。 九星非伏吟反吟、八门非伏吟反吟。本盘无整盘伏吟反吟，不凭此三项擅断缓急。 缓急不自动等于吉凶。", "title": "起盘总纲：五不遇时、伏吟、反吟"}, {"id": "02", "text": "落离九宫；九星天芮星极大凶；八神白虎被宫克、小凶；八门死门极大凶；天盘干乙势大、地盘干丁势大；天地格：乙加丁「奇仪相佐」（吉）。古文：文书事吉，百事可为；古诀大意：文书和合作事务顺利；天地盘取象：乙木生丁火，日奇扶助星奇，如两位助手彼此协作；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为极大凶。 传统病星格局「迅速恶化」。", "title": "天芮病宫"}, {"id": "03", "text": "落兑七宫；九星天心星极小吉；八神九地生宫、中凶；八门开门大吉；天盘干辛势极大、地盘干壬势中等；天地格：辛加壬「凶蛇入狱」（凶）。古文：两男争女，讼事不息；古诀大意：多方争执，难以停止；天地盘取象：辛为白虎及牢狱，壬为甲辰螣蛇，蛇落白虎牢笼，如被纠缠拘禁；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为中凶。 天心星月令废、比和，用神力量为极小。天心医生宫受天芮病宫克，意思为：天心医生受病宫压制，无法制病。", "title": "天心医生"}, {"id": "04", "text": "与前述天芮病宫同在离九宫。全部因素推断后，此宫为极大凶。 乙天干十二长生长生/冠带/临官/帝旺/沐浴、克月令，用神力量为大。乙奇与天芮病宫同宫，表示正在接受治疗，医药与病象同宫发挥作用。", "title": "乙奇医药"}, {"id": "05", "text": "落巽四宫；九星天英星极大凶；八神六合比和、大吉；八门景门中平；天盘干丁、地盘干己；天地格：丁加己「火入勾陈」（凶）。古文：奸私雠冤，事因女人；古诀大意：私情、仇怨产生麻烦；天地盘取象：丁为朱雀阴火，己为勾陈土及甲戌火墓，朱雀之火陷入纠缠之土；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为极小凶。 丁天干与月令关系为生月令，其本宫力量仍待核实。患者用神宫生天芮病宫，意思为：疾病得不到患者用神的压制，反受其生扶。", "title": "患者用神"}, {"id": "06", "text": "落乾六宫；九星天蓬星中凶；八神九天比和、大吉；八门休门小吉；天盘干丙势极小、地盘干辛势极大；天地格：丙加辛「奇神相合」（吉）。古文：谋事成就，病人不凶；古诀大意：谋划可能成功；天地盘取象：丙阳火与辛阴金为天干相合，如两方虽异性却能够结合；空亡不空；天盘入墓。全部因素推断后，此宫为极大吉。 丙天干十二长生死 / 墓 / 绝、生月令，用神力量为极小。时干事体宫受天芮病宫克，意思为：时干事体受病宫压制，无法制病。", "title": "时干事体"}, {"id": "07", "text": "落坎一宫；九星天任星中吉；八神值符克宫、中吉；八门生门大吉；天盘干癸势中等、地盘干丙势中等；天地格：癸加丙「华盖孛师」（吉）。古文：贵贱逢之，上人见喜；古诀大意：受到上位者认可；天地盘取象：癸为华盖阴水，丙为月奇荧惑火，华盖罩临火光，取上位者接纳之象；空亡真空；门破。八门压制宫力量，吉事不吉，凶事更凶。全部因素推断后，此宫为小吉。 值符按神宫克宫，用神力量为中等。因值符空亡，护持力明显减弱，尚存少许余气。", "title": "值符护持宫"}, {"id": "90_review", "text": "天芮病宫落离九宫，宫象极大凶；天心医生落兑七宫，宫象中凶，受病宫克；乙奇医药与天芮病宫同在离九宫；患者用神落巽四宫，宫象极小凶，生扶病宫；时干事体落乾六宫，宫象极大吉，受病宫克；值符落坎一宫，宫象小吉，克病宫，虽逢空仍有余气克制病宫；离九宫得天盘乙奇与地盘丁奇同宫扶助。\n\n综上所述，此病为不凶不吉；以上只作传统古籍象意参考，不能据此判断真实病情。", "title": "全部证据合断"}, {"id": "91_timing", "text": "时马在寅；应期须另有空、墓、冲合及问事情境支持，不能直接断定某一天。", "title": "时空及应期"}], "python_sections": [{"id": "01_macro", "text": "不构成五不遇时（已按日干、时干五行克制及阴阳同类核对）。 九星非伏吟反吟、八门非伏吟反吟。本盘无整盘伏吟反吟，不凭此三项擅断缓急。 缓急不自动等于吉凶。", "title": "起盘总纲：五不遇时、伏吟、反吟"}, {"id": "02", "text": "落离九宫；九星天芮星极大凶；八神白虎被宫克、小凶；八门死门极大凶；天盘干乙势大、地盘干丁势大；天地格：乙加丁「奇仪相佐」（吉）。古文：文书事吉，百事可为；古诀大意：文书和合作事务顺利；天地盘取象：乙木生丁火，日奇扶助星奇，如两位助手彼此协作；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为极大凶。 传统病星格局「迅速恶化」。", "title": "天芮病宫"}, {"id": "03", "text": "落兑七宫；九星天心星极小吉；八神九地生宫、中凶；八门开门大吉；天盘干辛势极大、地盘干壬势中等；天地格：辛加壬「凶蛇入狱」（凶）。古文：两男争女，讼事不息；古诀大意：多方争执，难以停止；天地盘取象：辛为白虎及牢狱，壬为甲辰螣蛇，蛇落白虎牢笼，如被纠缠拘禁；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为中凶。 天心星月令废、比和，用神力量为极小。天心医生宫受天芮病宫克，意思为：天心医生受病宫压制，无法制病。", "title": "天心医生"}, {"id": "04", "text": "与前述天芮病宫同在离九宫。全部因素推断后，此宫为极大凶。 乙天干十二长生长生/冠带/临官/帝旺/沐浴、克月令，用神力量为大。乙奇与天芮病宫同宫，表示正在接受治疗，医药与病象同宫发挥作用。", "title": "乙奇医药"}, {"id": "05", "text": "落巽四宫；九星天英星极大凶；八神六合比和、大吉；八门景门中平；天盘干丁、地盘干己；天地格：丁加己「火入勾陈」（凶）。古文：奸私雠冤，事因女人；古诀大意：私情、仇怨产生麻烦；天地盘取象：丁为朱雀阴火，己为勾陈土及甲戌火墓，朱雀之火陷入纠缠之土；空亡不空；无已核特殊刑墓迫。全部因素推断后，此宫为极小凶。 丁天干与月令关系为生月令，其本宫力量仍待核实。患者用神宫生天芮病宫，意思为：疾病得不到患者用神的压制，反受其生扶。", "title": "患者用神"}, {"id": "06", "text": "落乾六宫；九星天蓬星中凶；八神九天比和、大吉；八门休门小吉；天盘干丙势极小、地盘干辛势极大；天地格：丙加辛「奇神相合」（吉）。古文：谋事成就，病人不凶；古诀大意：谋划可能成功；天地盘取象：丙阳火与辛阴金为天干相合，如两方虽异性却能够结合；空亡不空；天盘入墓。全部因素推断后，此宫为极大吉。 丙天干十二长生死 / 墓 / 绝、生月令，用神力量为极小。时干事体宫受天芮病宫克，意思为：时干事体受病宫压制，无法制病。", "title": "时干事体"}, {"id": "07", "text": "落坎一宫；九星天任星中吉；八神值符克宫、中吉；八门生门大吉；天盘干癸势中等、地盘干丙势中等；天地格：癸加丙「华盖孛师」（吉）。古文：贵贱逢之，上人见喜；古诀大意：受到上位者认可；天地盘取象：癸为华盖阴水，丙为月奇荧惑火，华盖罩临火光，取上位者接纳之象；空亡真空；门破。八门压制宫力量，吉事不吉，凶事更凶。全部因素推断后，此宫为小吉。 值符按神宫克宫，用神力量为中等。因值符空亡，护持力明显减弱，尚存少许余气。", "title": "值符护持宫"}, {"id": "90_review", "text": "无整盘伏吟反吟，缓急另核；天芮病宫落离九宫，宫象极大凶；天心医生落兑七宫，宫象中凶，受病宫克；乙奇医药与天芮病宫同在离九宫；患者用神落巽四宫，宫象极小凶，生扶病宫；时干事体落乾六宫，宫象极大吉，受病宫克；值符落坎一宫，宫象小吉，克病宫，虽逢空仍有余气克制病宫；离九宫得天盘乙奇与地盘丁奇同宫扶助。\n\n综上所述，此病为不凶不吉；以上只作传统古籍象意参考，不能据此判断真实病情。", "title": "全部证据合断"}, {"id": "91_timing", "text": "时马在寅；应期须另有空、墓、冲合及问事情境支持，不能直接断定某一天。", "title": "时空及应期"}]}

DIFF START
--- live_Python_GPT_Vnext
+++ native_iOS_Vnext
@@ -21,5 +21,5 @@
 
 全部证据合断：
-无整盘伏吟反吟，缓急另核；天芮病宫落离九宫，宫象极大凶；天心医生落兑七宫，宫象中凶，受病宫克；乙奇医药与天芮病宫同在离九宫；患者用神落巽四宫，宫象极小凶，生扶病宫；时干事体落乾六宫，宫象极大吉，受病宫克；值符落坎一宫，宫象小吉，克病宫，虽逢空仍有余气克制病宫；离九宫得天盘乙奇与地盘丁奇同宫扶助。
+天芮病宫落离九宫，宫象极大凶；天心医生落兑七宫，宫象中凶，受病宫克；乙奇医药与天芮病宫同在离九宫；患者用神落巽四宫，宫象极小凶，生扶病宫；时干事体落乾六宫，宫象极大吉，受病宫克；值符落坎一宫，宫象小吉，克病宫，虽逢空仍有余气克制病宫；离九宫得天盘乙奇与地盘丁奇同宫扶助。
 
 综上所述，此病为不凶不吉；以上只作传统古籍象意参考，不能据此判断真实病情。
DIFF END


Exact equality: 0 of 1
ISSUES: 2010-02-02T07:00:00-05:00 朋友 FULL_TEXT_MISMATCH 
VERDICT: FAIL - cannot claim complete iOS migration.
```
## regression.log
```text
No output from this stage
```
