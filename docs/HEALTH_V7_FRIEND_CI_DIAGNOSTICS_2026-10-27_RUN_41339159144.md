# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41339159144
Source: 2b5f818cb4a70511e209c3463aedcc3bb3d82a85

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:232:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
230 |         let fanyin=entire(actualStars,homeStars,true) ||
231 |                     entire(actualDoors,homeDoors,true)
232 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
233 |             fill(fiveNot ? "macro_five" : "macro_clear"),
234 |             fill(fuyin && fanyin ? "macro_mixed" :

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
