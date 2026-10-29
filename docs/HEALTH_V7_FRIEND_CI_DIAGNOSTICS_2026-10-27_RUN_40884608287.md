# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40884608287
Source: 19049373fed8dd7585bbf59424676ca39cb25956

## compiler.log
```text
ios/WenguaAppUI/WenguaNativeReadingRouter.swift:212:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
210 |         let fanyin=entire(actualStars,homeStars,true) ||
211 |                     entire(actualDoors,homeDoors,true)
212 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
213 |             fill(fiveNot ? "macro_five" : "macro_clear"),
214 |             fill(fuyin && fanyin ? "macro_mixed" :

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
