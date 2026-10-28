# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40765865438
Source: ffcfcb86446b013767b6699676676023568a89c4

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:211:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |         let fanyin=entire(actualStars,homeStars,true) ||
210 |                     entire(actualDoors,homeDoors,true)
211 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
212 |             fill(fiveNot ? "macro_five" : "macro_clear"),
213 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/WenguaNativeVNextEngine.swift:363:66: error: cannot find 'actualEarth' in scope
361 |             patternNames.append(fields[2])
362 |             let polarity=fields[3]=="吉" ? 1 : -1
363 |             let score=pattern(star,p,polarity:polarity,earthStem:actualEarth)
    |                                                                  `- error: cannot find 'actualEarth' in scope
364 |             if let score {patternPoints.append(score)}
365 |             let relevantTombs=p.tombs.filter{$0.plane=="天盘" &&
```
## diff.md
```text
No output from this stage
```
## regression.log
```text
No output from this stage
```
