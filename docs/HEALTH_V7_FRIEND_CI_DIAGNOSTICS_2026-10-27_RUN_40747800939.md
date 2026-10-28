# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40747800939
Source: 8d9357b4e172be66a2db53218007b83c015407a5

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:206:13: warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
204 |         let doorPart=try signedSymbol("door",door,palace:p.id,
205 |                                       month:month,energy:energy)
206 |         let hasIllness=p.heavenStars.contains{$0.star=="天芮星"}
    |             `- warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
207 |         // Each actual sky carrier has a distinct 81 pattern; do not
208 |         // mis-attribute Tianqin's carried stem to Tianrui.

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:294:13: warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
292 |         // net +/- score of either resident physical palace.
293 |         let note=baseNote+targetPowerSentence
294 |         let outcome=edge.cell
    |             `- warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
295 |         let applicable=["strong","limited"].contains(edge.applicability)
296 |         let eligible:Bool

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:296:13: warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
294 |         let outcome=edge.cell
295 |         let applicable=["strong","limited"].contains(edge.applicability)
296 |         let eligible:Bool
    |             `- warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
297 |         if role=="chief" {
298 |             eligible=review.palaces[aid]?.void=="not_void" &&

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
```
## diff.md
```text
# STRICT GPT-Python versus iOS native literal reading parity

Both entire paragraphs and their headings, line breaks, punctuation must match.
No whitespace normalization or omitted sections is permitted.

## 1 2010-02-02T07:00:00-05:00: EXACT MATCH (text + all section IDs/titles/bodies)

Exact equality: 1 of 1
ISSUES: none
VERDICT: PASS
```
## regression.log
```text
No output from this stage
```
