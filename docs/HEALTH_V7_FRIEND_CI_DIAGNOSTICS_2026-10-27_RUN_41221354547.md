# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41221354547
Source: fb0938965a84a428f3031c0d17e39a6db63fe896

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
