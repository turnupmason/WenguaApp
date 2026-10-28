# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40783200949
Source: 399ce7163e411636528dab396af5f82e3c08308d

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:209:13: warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
207 |         let doorPart=try signedSymbol("door",door,palace:p.id,
208 |                                       month:month,energy:energy)
209 |         let hasIllness=p.heavenStars.contains{$0.star=="天芮星"}
    |             `- warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
210 |         // Each actual sky carrier has a distinct 81 pattern; do not
211 |         // mis-attribute Tianqin's carried stem to Tianrui.

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
