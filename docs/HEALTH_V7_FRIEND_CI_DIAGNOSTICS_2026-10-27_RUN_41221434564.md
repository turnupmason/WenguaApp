# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41221434564
Source: e94834a8a3beccb4c2dd297d5bf87f00393bbf19

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
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:476:66: error: expected ',' separator
474 |             if documented.contains(identity){continue}
475 |             documented.insert(identity)
476 |             support.append(name+f.symbol+"在"+label(p)+"，势"+
    |                                                            `- error: expected ',' separator
477 |                 (f.strength ?? "待核")+"，"+conciseRelation(key))
478 |         }

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:465:52: error: value of type 'WenguaVNextFactor' has no member 'kind'
463 |         for k in ["illness","patient","doctor","medicine"] {
464 |             if let id=review.roles[k],let f=review.roleEnergy[k] {
465 |                 documented.insert(String(id)+":"+f.kind+":"+f.symbol)
    |                                                    `- error: value of type 'WenguaVNextFactor' has no member 'kind'
466 |             }
467 |         }

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:473:43: error: value of type 'WenguaVNextFactor' has no member 'kind'
471 |             guard let id=review.roles[key],let f=review.roleEnergy[key],
472 |                   let p=cells[id] else {continue}
473 |             let identity=String(id)+":"+f.kind+":"+f.symbol
    |                                           `- error: value of type 'WenguaVNextFactor' has no member 'kind'
474 |             if documented.contains(identity){continue}
475 |             documented.insert(identity)

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:476:65: error: '+' is not a postfix unary operator
474 |             if documented.contains(identity){continue}
475 |             documented.insert(identity)
476 |             support.append(name+f.symbol+"在"+label(p)+"，势"+
    |                                                           `- error: '+' is not a postfix unary operator
477 |                 (f.strength ?? "待核")+"，"+conciseRelation(key))
478 |         }

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:476:21: error: generic parameter 'E' could not be inferred
474 |             if documented.contains(identity){continue}
475 |             documented.insert(identity)
476 |             support.append(name+f.symbol+"在"+label(p)+"，势"+
    |                     `- error: generic parameter 'E' could not be inferred
477 |                 (f.strength ?? "待核")+"，"+conciseRelation(key))
478 |         }

Swift.Array.append:2:22: note: in call to function 'append(addingCapacity:initializingWith:)'
1 | generic struct Array {
2 | public mutating func append<E>(addingCapacity uninitializedCount: Int, initializingWith initializer: @_lifetime(span: copy span) (_ span: inout OutputSpan<Element>) throws(E) -> Void) throws(E) where E : Error}
  |                      `- note: in call to function 'append(addingCapacity:initializingWith:)'
3 | 

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:476:27: error: missing argument labels 'addingCapacity:initializingWith:' in call
474 |             if documented.contains(identity){continue}
475 |             documented.insert(identity)
476 |             support.append(name+f.symbol+"在"+label(p)+"，势"+
    |                           `- error: missing argument labels 'addingCapacity:initializingWith:' in call
477 |                 (f.strength ?? "待核")+"，"+conciseRelation(key))
478 |         }

ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:477:47: error: cannot convert value of type 'String' to expected argument type '@_lifetime(span: copy span) (inout OutputSpan<String>) throws(E) -> Void'
475 |             documented.insert(identity)
476 |             support.append(name+f.symbol+"在"+label(p)+"，势"+
477 |                 (f.strength ?? "待核")+"，"+conciseRelation(key))
    |                                         `- error: cannot convert value of type 'String' to expected argument type '@_lifetime(span: copy span) (inout OutputSpan<String>) throws(E) -> Void'
478 |         }
479 |         let supportText="另参"+(support.isEmpty ? "无独立附加用神" :
```
## diff.md
```text
No output from this stage
```
## regression.log
```text
No output from this stage
```
