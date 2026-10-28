# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40619777581
Source: af9b7b3d45ab94e6bdcc7bdba96216bacb3b39fa

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
ios/WenguaAppUI/WenguaVNextReasoner.swift:195:80: error: '+' is not a postfix unary operator
193 |             // in that environment have DIFFERENT selected powers.
194 |             let symbol=audit.roleEnergy[role]?.symbol ?? role
195 |             let pair=[id,illID].sorted().map(String.init).joined(separator:":")+
    |                                                                                `- error: '+' is not a postfix unary operator
196 |                       ":"+symbol
197 |             if !usedPairs.insert(pair).inserted {

ios/WenguaAppUI/WenguaVNextReasoner.swift:196:26: warning: result of operator '+' is unused [#NoUsage]
194 |             let symbol=audit.roleEnergy[role]?.symbol ?? role
195 |             let pair=[id,illID].sorted().map(String.init).joined(separator:":")+
196 |                       ":"+symbol
    |                          `- warning: result of operator '+' is unused [#NoUsage]
197 |             if !usedPairs.insert(pair).inserted {
198 |                 relations.append(try fill("reason_shared",[

ios/WenguaAppUI/WenguaVNextReasoner.swift:204:72: error: '+' is not a postfix unary operator
202 |             let control=audit.controls.first{$0.role==role}
203 |             let direction=control?.direction ?? relation(id,illID)
204 |             let strength=(audit.roleEnergy[role]?.strength ?? "待核")+
    |                                                                    `- error: '+' is not a postfix unary operator
205 |                 "；天芮病星"+(audit.roleEnergy["illness"]?.strength ?? "待核")
206 |             let effect:String

ios/WenguaAppUI/WenguaVNextReasoner.swift:205:34: warning: result of operator '+' is unused [#NoUsage]
203 |             let direction=control?.direction ?? relation(id,illID)
204 |             let strength=(audit.roleEnergy[role]?.strength ?? "待核")+
205 |                 "；天芮病星"+(audit.roleEnergy["illness"]?.strength ?? "待核")
    |                        `- warning: result of operator '+' is unused [#NoUsage]
206 |             let effect:String
207 |             if let control, direction=="克" || direction=="被克" {

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
