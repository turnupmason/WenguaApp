# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40767550267
Source: c1580732bb887080d148932d75e39f344657895b

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:207:13: warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
205 |         let doorPart=try signedSymbol("door",door,palace:p.id,
206 |                                       month:month,energy:energy)
207 |         let hasIllness=p.heavenStars.contains{$0.star=="天芮星"}
    |             `- warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
208 |         // Each actual sky carrier has a distinct 81 pattern; do not
209 |         // mis-attribute Tianqin's carried stem to Tianrui.

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:295:13: warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
293 |         // net +/- score of either resident physical palace.
294 |         let note=baseNote+targetPowerSentence
295 |         let outcome=edge.cell
    |             `- warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
296 |         let applicable=["strong","limited"].contains(edge.applicability)
297 |         let eligible:Bool

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:297:13: warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
295 |         let outcome=edge.cell
296 |         let applicable=["strong","limited"].contains(edge.applicability)
297 |         let eligible:Bool
    |             `- warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
298 |         if role=="chief" {
299 |             eligible=review.palaces[aid]?.void=="not_void" &&

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
