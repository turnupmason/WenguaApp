# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40533730619
Source: 9d20ea2f35224aee0e3f1ae421b0c1e6c6ef2172

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
ios/WenguaAppUI/WenguaNativeVNextEngine.swift:775:63: error: '+' is not a postfix unary operator
773 |         let auspiceNotes=auspices.keys.sorted().compactMap{auspices[$0]?.1}
774 |         let auspicePoints=auspices.values.reduce(0){$0+$1.0}
775 |         let relationshipBonus=controlPoints.values.reduce(0,+)+
    |                                                               `- error: '+' is not a postfix unary operator
776 |                               3*drainBonus.count+auspicePoints
777 |         let result=pending.isEmpty ?

ios/WenguaAppUI/WenguaNativeVNextEngine.swift:776:49: warning: result of operator '+' is unused [#NoUsage]
774 |         let auspicePoints=auspices.values.reduce(0){$0+$1.0}
775 |         let relationshipBonus=controlPoints.values.reduce(0,+)+
776 |                               3*drainBonus.count+auspicePoints
    |                                                 `- warning: result of operator '+' is unused [#NoUsage]
777 |         let result=pending.isEmpty ?
778 |             Optional(saturation(known+relationshipBonus)) : nil

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
