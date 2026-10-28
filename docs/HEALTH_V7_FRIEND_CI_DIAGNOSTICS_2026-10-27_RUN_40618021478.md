# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40618021478
Source: 6e340ab6f3d738dba8874bdf571dc5cfc9824777

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:293:56: error: '+' is not a postfix unary operator
291 |         // Each edge compares THIS selected signifier with Tianrui, not the
292 |         // net +/- score of either resident physical palace.
293 |         let note=baseNote+"天芮病星用神力量为"+
    |                                      `- error: '+' is not a postfix unary operator
294 |             (review.roleEnergy["illness"]?.strength ?? "待核")+"。"
295 |         let outcome=edge.cell

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:294:65: warning: result of operator '+' is unused [#NoUsage]
292 |         // net +/- score of either resident physical palace.
293 |         let note=baseNote+"天芮病星用神力量为"+
294 |             (review.roleEnergy["illness"]?.strength ?? "待核")+"。"
    |                                                             `- warning: result of operator '+' is unused [#NoUsage]
295 |         let outcome=edge.cell
296 |         let applicable=["strong","limited"].contains(edge.applicability)

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:475:59: error: '+' is not a postfix unary operator
473 |             let power=review.roleEnergy[key]?.strength ?? "待核"
474 |             if let existing=seenPalaces[pid] {
475 |                 head=name+"与"+existing+"同在"+label(p)+
    |                                                     `- error: '+' is not a postfix unary operator
476 |                     "，其中"+symbol+"用神力量"+power
477 |             } else {

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:476:54: warning: result of operator '+' is unused [#NoUsage]
474 |             if let existing=seenPalaces[pid] {
475 |                 head=name+"与"+existing+"同在"+label(p)+
476 |                     "，其中"+symbol+"用神力量"+power
    |                                        `- warning: result of operator '+' is unused [#NoUsage]
477 |             } else {
478 |                 head=name+"落"+label(p)+"，宫象"+quality+

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:478:61: error: '+' is not a postfix unary operator
476 |                     "，其中"+symbol+"用神力量"+power
477 |             } else {
478 |                 head=name+"落"+label(p)+"，宫象"+quality+
    |                                                     `- error: '+' is not a postfix unary operator
479 |                     "，其中"+symbol+"用神力量"+power
480 |                 if state != "not_void" && key != "chief" {

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:479:54: warning: result of operator '+' is unused [#NoUsage]
477 |             } else {
478 |                 head=name+"落"+label(p)+"，宫象"+quality+
479 |                     "，其中"+symbol+"用神力量"+power
    |                                        `- warning: result of operator '+' is unused [#NoUsage]
480 |                 if state != "not_void" && key != "chief" {
481 |                     head+="且逢"+(state=="true_void" ? "真空":"假空")

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
