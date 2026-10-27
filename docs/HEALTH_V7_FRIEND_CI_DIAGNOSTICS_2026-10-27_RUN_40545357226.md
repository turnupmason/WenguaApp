# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40545357226
Source: f07562a4af1d0feee9c3101d2917167fc037439e

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
ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:115:64: error: expected ',' separator
113 |                 relationship:test.relationship,energy:energy,
114 |                 catalog:pairs,actor:actor)
115 |             print("V7_FULL_SOURCE_BONUS_COMPARE "+test.instant+
    |                                                                `- error: expected ',' separator
116 |                   " Swift base="+String(audit.postVoidKnownSum)+
117 |                   " result="+String(describing:audit.score)+

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:115:63: error: '+' is not a postfix unary operator
113 |                 relationship:test.relationship,energy:energy,
114 |                 catalog:pairs,actor:actor)
115 |             print("V7_FULL_SOURCE_BONUS_COMPARE "+test.instant+
    |                                                               `- error: '+' is not a postfix unary operator
116 |                   " Swift base="+String(audit.postVoidKnownSum)+
117 |                   " result="+String(describing:audit.score)+

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:116:64: error: '+' is not a postfix unary operator
114 |                 catalog:pairs,actor:actor)
115 |             print("V7_FULL_SOURCE_BONUS_COMPARE "+test.instant+
116 |                   " Swift base="+String(audit.postVoidKnownSum)+
    |                                                                `- error: '+' is not a postfix unary operator
117 |                   " result="+String(describing:audit.score)+
118 |                   " controls="+String(describing:audit.controlBonusPoints)+
```
## diff.md
```text
No output from this stage
```
## regression.log
```text
No output from this stage
```
