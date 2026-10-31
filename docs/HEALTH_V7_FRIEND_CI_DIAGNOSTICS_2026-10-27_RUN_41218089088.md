# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41218089088
Source: 4dd3edf17d33e2071f7f407e0312e22ae4ea8e26

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
No output from this stage
```
## regression.log
```text
No output from this stage
```
