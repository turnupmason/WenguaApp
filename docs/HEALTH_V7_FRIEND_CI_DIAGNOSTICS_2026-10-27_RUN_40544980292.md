# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40544980292
Source: c88c18e807176dab48b13321f28752b71140e1f1

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
ios/WenguaAppUI/WenguaNativeVNextEngine.swift:773:75: error: '+' is not a postfix unary operator
771 |                 let awarded=cohostPoints(chief:chiefPoints,stem:stemPoints,
772 |                                          void:isVoid)
773 |                 let tags=([chiefPoints>0 ? "值符" : nil].compactMap{$0})+
    |                                                                       `- error: '+' is not a postfix unary operator
774 |                     ([stemBest.map{$0.2+$0.1}].compactMap{$0})
775 |                 let note=isVoid ?

ios/WenguaAppUI/WenguaNativeVNextEngine.swift:774:48: warning: result of call to 'compactMap' is unused [#NoUsage]
772 |                                          void:isVoid)
773 |                 let tags=([chiefPoints>0 ? "值符" : nil].compactMap{$0})+
774 |                     ([stemBest.map{$0.2+$0.1}].compactMap{$0})
    |                                                `- warning: result of call to 'compactMap' is unused [#NoUsage]
775 |                 let note=isVoid ?
776 |                     place+"逢空，"+tags.joined(separator:"与")+"同宫的吉助减弱，尚有余气。" :

ios/WenguaAppUI/WenguaNativeVNextEngine.swift:775:26: error: the compiler is unable to type-check this expression in reasonable time; try breaking up the expression into distinct sub-expressions
773 |                 let tags=([chiefPoints>0 ? "值符" : nil].compactMap{$0})+
774 |                     ([stemBest.map{$0.2+$0.1}].compactMap{$0})
775 |                 let note=isVoid ?
    |                          `- error: the compiler is unable to type-check this expression in reasonable time; try breaking up the expression into distinct sub-expressions
776 |                     place+"逢空，"+tags.joined(separator:"与")+"同宫的吉助减弱，尚有余气。" :
777 |                     place+"得"+tags.joined(separator:"与")+"同宫扶助。"

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
