# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40794829881
Source: c62a5437649519030174bb882d44d2d43e43bf4a

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:40: error: expected ',' separator
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                                      `- error: expected ',' separator
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:416:49: error: '+' is not a postfix unary operator
414 |             throw WenguaNativeReadingError.missingRole
415 |         }
416 |         var illnessText="在"+label(illnessCell)+
    |                                               `- error: '+' is not a postfix unary operator
417 |             "，势"+(review.roleEnergy["illness"]?.strength ?? "待核")+
418 |             "，宫象"+signed(review.roleScores["illness"])

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:417:74: error: '+' is not a postfix unary operator
415 |         }
416 |         var illnessText="在"+label(illnessCell)+
417 |             "，势"+(review.roleEnergy["illness"]?.strength ?? "待核")+
    |                                                                  `- error: '+' is not a postfix unary operator
418 |             "，宫象"+signed(review.roleScores["illness"])
419 |         let illVoid=review.palaces[illID]?.void ?? "not_void"

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:418:24: warning: result of operator '+' is unused [#NoUsage]
416 |         var illnessText="在"+label(illnessCell)+
417 |             "，势"+(review.roleEnergy["illness"]?.strength ?? "待核")+
418 |             "，宫象"+signed(review.roleScores["illness"])
    |                  `- warning: result of operator '+' is unused [#NoUsage]
419 |         let illVoid=review.palaces[illID]?.void ?? "not_void"
420 |         if illVoid != "not_void" {

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:424:63: error: '+' is not a postfix unary operator
422 |         }
423 |         let patientSymbol=review.roleEnergy["patient"]?.symbol ?? "未核"
424 |         var patientText=patientSymbol+"在"+label(patientCell)+
    |                                                             `- error: '+' is not a postfix unary operator
425 |             "，宫象"+signed(review.roleScores["patient"])
426 |         let patientVoid=review.palaces[patientID]?.void ?? "not_void"

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:425:24: warning: result of operator '+' is unused [#NoUsage]
423 |         let patientSymbol=review.roleEnergy["patient"]?.symbol ?? "未核"
424 |         var patientText=patientSymbol+"在"+label(patientCell)+
425 |             "，宫象"+signed(review.roleScores["patient"])
    |                  `- warning: result of operator '+' is unused [#NoUsage]
426 |         let patientVoid=review.palaces[patientID]?.void ?? "not_void"
427 |         if patientVoid != "not_void" {

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:39: error: '+' is not a postfix unary operator
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                                     `- error: '+' is not a postfix unary operator
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:437:63: error: '+' is not a postfix unary operator
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
    |                                                           `- error: '+' is not a postfix unary operator
438 |                 "，"+conciseRelation(key))
439 |         }

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:22: error: generic parameter 'E' could not be inferred
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                      `- error: generic parameter 'E' could not be inferred
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

Swift.Array.append:2:22: note: in call to function 'append(addingCapacity:initializingWith:)'
1 | generic struct Array {
2 | public mutating func append<E>(addingCapacity uninitializedCount: Int, initializingWith initializer: @_lifetime(span: copy span) (_ span: inout OutputSpan<Element>) throws(E) -> Void) throws(E) where E : Error}
  |                      `- note: in call to function 'append(addingCapacity:initializingWith:)'
3 | 

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:436:28: error: missing argument labels 'addingCapacity:initializingWith:' in call
434 |         var medicine:[String]=[]
435 |         for (key,name) in [("doctor","天心"),("medicine","乙奇")] {
436 |             medicine.append(name+"势"+
    |                            `- error: missing argument labels 'addingCapacity:initializingWith:' in call
437 |                 (review.roleEnergy[key]?.strength ?? "待核")+
438 |                 "，"+conciseRelation(key))

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
