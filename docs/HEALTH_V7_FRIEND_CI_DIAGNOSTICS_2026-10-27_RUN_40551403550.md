# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40551403550
Source: 784fb3d51625afe604b451c6909d8d982a23bcce

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:291:13: warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
289 |         let rel=relation(aid,pid)
290 |         let note=try powerNote(role,p,own,chart:chart)
291 |         let outcome=edge.cell
    |             `- warning: initialization of immutable value 'outcome' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
292 |         let applicable=["strong","limited"].contains(edge.applicability)
293 |         let eligible:Bool

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:293:13: warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
291 |         let outcome=edge.cell
292 |         let applicable=["strong","limited"].contains(edge.applicability)
293 |         let eligible:Bool
    |             `- warning: immutable value 'eligible' was never used; consider removing it [#NoUsage]
294 |         if role=="chief" {
295 |             eligible=review.palaces[aid]?.void=="not_void" &&

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:438:13: error: invalid redeclaration of 'titles'
345 |         guard let root=try JSONSerialization.jsonObject(with:template) as? [String:Any],
346 |               let macros=root["macros"] as? [String:String],
347 |               let titles=root["section_titles"] as? [String:String] else {
    |                   `- note: 'titles' previously declared here
348 |             throw WenguaNativeReadingError.missingPhrases
349 |         }
    :
436 |         // V7.3: a dynamic two-sentence account of THIS chart, never a
437 |         // hardcoded success case or duplicated real-person/palace score.
438 |         let titles:[String:String]=[
    |             `- error: invalid redeclaration of 'titles'
439 |             "illness":"天芮病宫","doctor":"天心医生","medicine":"乙奇医药",
440 |             "patient":"患者用神","hour":"时干事体","chief":"值符",

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
