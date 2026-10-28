# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40617644117
Source: 7224aff491f9303731defcf8370845b75cc2acda

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
ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:106:26: error: extra argument 'attacker' in call
104 |         ] {
105 |             try require(WenguaVNextEngine.conditionalDiseaseControl(
106 |                 attacker:attacker,attackerVoid:empty,
    |                          `- error: extra argument 'attacker' in call
107 |                 attackerControlled:controlled,illnessVoid:illEmpty)==expected,
108 |                 "V7.8 3/5/1 illness control gate mismatch")

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:105:68: error: missing arguments for parameters 'attackerPower', 'targetPower', 'actualCell', 'applicability' in call
103 |             (-5,true,false,false,1)
104 |         ] {
105 |             try require(WenguaVNextEngine.conditionalDiseaseControl(
    |                                                                    `- error: missing arguments for parameters 'attackerPower', 'targetPower', 'actualCell', 'applicability' in call
106 |                 attacker:attacker,attackerVoid:empty,
107 |                 attackerControlled:controlled,illnessVoid:illEmpty)==expected,

ios/WenguaAppUI/WenguaNativeVNextEngine.swift:82:17: note: 'conditionalDiseaseControl(attackerPower:targetPower:actualCell:applicability:attackerVoid:attackerControlled:illnessVoid:)' declared here
 80 |         "微弱克制","减力克制","断续克制","效力递减"
 81 |     ]
 82 |     static func conditionalDiseaseControl(
    |                 `- note: 'conditionalDiseaseControl(attackerPower:targetPower:actualCell:applicability:attackerVoid:attackerControlled:illnessVoid:)' declared here
 83 |          attackerPower:String?,targetPower:String?,
 84 |          actualCell:String?,applicability:String,
```
## diff.md
```text
No output from this stage
```
## regression.log
```text
No output from this stage
```
