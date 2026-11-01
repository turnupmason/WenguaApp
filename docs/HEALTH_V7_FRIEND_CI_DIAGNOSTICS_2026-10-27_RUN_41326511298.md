# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41326511298
Source: a427dcf6caea2198dac97762778792e088c54f1a

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:73:24: error: cannot find 'WenguaNativeDiscomfortV15' in scope
 71 |             let actor=try WenguaNativeActorSource.bind(
 72 |                 chart:chart,inquiry:request,index:profile)
 73 |             return try WenguaNativeDiscomfortV15.compose(
    |                        `- error: cannot find 'WenguaNativeDiscomfortV15' in scope
 74 |                 chart:chart,relationship:relationship,actor:actor,bundle:bundle)
 75 |         }

ios/WenguaAppUI/WenguaNativeReadingRouter.swift:228:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
226 |         let fanyin=entire(actualStars,homeStars,true) ||
227 |                     entire(actualDoors,homeDoors,true)
228 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
229 |             fill(fiveNot ? "macro_five" : "macro_clear"),
230 |             fill(fuyin && fanyin ? "macro_mixed" :

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
