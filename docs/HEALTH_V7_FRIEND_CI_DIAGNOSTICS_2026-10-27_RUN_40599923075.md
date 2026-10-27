# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40599923075
Source: c91aa133ad6ca7420063b1700186888d6c41b431

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
ios/WenguaAppUI/WenguaNativeVNextEngine.swift:764:13: warning: initialization of immutable value 'scoreList' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
762 |         }
763 |         // One physical palace once, including accepted co-located roles.
764 |         let scoreList=physical.values.filter{enabled.contains($0.id)}
    |             `- warning: initialization of immutable value 'scoreList' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
765 |         let known=roleScores.values.reduce(0,+)
766 |         let pending=rolePending.sorted()

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

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:413:17: warning: initialization of immutable value 'marker' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
411 |                 extra=try phrase("illness",["name":t25.title,"explanation":t25.why])
412 |             }
413 |             let marker=String(pid)+":"+(review.roleEnergy[role]?.symbol ?? "")
    |                 `- warning: initialization of immutable value 'marker' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
414 |             let roleText:String
415 |             if role=="illness" {roleText=""}

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
```
## diff.md
```text
No output from this stage
```
## regression.log
```text
No output from this stage
```
