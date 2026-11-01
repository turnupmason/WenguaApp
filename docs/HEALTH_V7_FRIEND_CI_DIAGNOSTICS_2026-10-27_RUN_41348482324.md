# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41348482324
Source: 6183ae23f1a325f41b8a529db8e6b30b1df4ee1a

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:237:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
235 |         let fanyin=entire(actualStars,homeStars,true) ||
236 |                     entire(actualDoors,homeDoors,true)
237 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
238 |             fill(fiveNot ? "macro_five" : "macro_clear"),
239 |             fill(fuyin && fanyin ? "macro_mixed" :

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
........
----------------------------------------------------------------------
Ran 8 tests in 0.490s

OK
```
