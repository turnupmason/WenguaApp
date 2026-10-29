# V7 same-clock male friend standalone CI diagnostics

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40950715121
Source: e0e60755082c1c0d6a47f0be4de1d7c1796f2dfb

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
ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:159:65: error: expected ',' separator
157 |                 let extras=audit.auspiceBonusNotes.joined(separator:"|")
158 |                 FileHandle.standardError.write(Data(
159 |                   ("SIXJIA_2014_QIAN_NATIVE earth="+q.earthStem+
    |                                                                 `- error: expected ',' separator
160 |                    " stages="+stages+" tombs="+tombs+
161 |                    " god="+String(describing:q.deity)+

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:159:64: error: '+' is not a postfix unary operator
157 |                 let extras=audit.auspiceBonusNotes.joined(separator:"|")
158 |                 FileHandle.standardError.write(Data(
159 |                   ("SIXJIA_2014_QIAN_NATIVE earth="+q.earthStem+
    |                                                                `- error: '+' is not a postfix unary operator
160 |                    " stages="+stages+" tombs="+tombs+
161 |                    " god="+String(describing:q.deity)+

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:160:53: error: '+' is not a postfix unary operator
158 |                 FileHandle.standardError.write(Data(
159 |                   ("SIXJIA_2014_QIAN_NATIVE earth="+q.earthStem+
160 |                    " stages="+stages+" tombs="+tombs+
    |                                                     `- error: '+' is not a postfix unary operator
161 |                    " god="+String(describing:q.deity)+
162 |                    " auspice="+extras+"\n").utf8))

ios/WenguaAppUI/VNextThreeRandomNativeFullCheck.swift:162:45: error: value of tuple type '(AttributedString, String)' has no member 'utf8'
160 |                    " stages="+stages+" tombs="+tombs+
161 |                    " god="+String(describing:q.deity)+
162 |                    " auspice="+extras+"\n").utf8))
    |                                             `- error: value of tuple type '(AttributedString, String)' has no member 'utf8'
163 |             }
164 |             let debugItems:[String]=[
```
## diff.md
```text
No output from this stage
```
## regression.log
```text
No output from this stage
```
