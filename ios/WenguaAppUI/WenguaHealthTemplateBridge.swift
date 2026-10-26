import Foundation

// Stage 1 native iOS bridge: exact user-editable template + 81 ordered stem pairs.
// ONLY real chart facts and original table text. It does NOT infer patient roles,
// apply 200-cell strengths, decide void scores, or manufacture a final prognosis.
// The SAME two repo resources are bundled by project.yml; no network or frozen case.
struct WenguaHealthFormationBlock: Identifiable {
    let id: Int
    let palace: String
    let sentences: [String]
}

enum WenguaHealthTemplateError: Error, LocalizedError {
    case invalidTemplate, invalidCatalog, unavailableResource, unsupportedRealPair
    var errorDescription: String? {
        switch self {
        case .invalidTemplate: return "疾病断词JSON模板不完整或变量被改坏"
        case .invalidCatalog: return "81天地格目录必须恰有81个有序坐标与七个完整字段"
        case .unavailableResource: return "本机离线模板或81格资源未打包"
        case .unsupportedRealPair: return "本盘真实天盘/地盘组合缺少已核81格记录"
        }
    }
}

enum WenguaHealthTemplateBridge {
    static let stems = ["戊","己","庚","辛","壬","癸","丁","丙","乙"]
    static let fields = ["heaven","earth","name","polarity",
                         "classical_text","classical_meaning","imagery"]
    static let header = "天盘干|地盘干|格局名称|吉凶|古文（摘句）|古诀大意|天地盘取象"
    static let palaceOrder = [4,9,2,3,7,8,1,6]

    static func fromBundle(chart: WenguaNativeChart, bundle: Bundle = .main) throws
      -> [WenguaHealthFormationBlock] {
        guard let t = bundle.url(forResource:"reading_template",withExtension:"json"),
              let p = bundle.url(forResource:"81_pairs",withExtension:"tsv") else {
            throw WenguaHealthTemplateError.unavailableResource
        }
        return try fromText(chart:chart,
                            template:Data(contentsOf:t),
                            catalog:String(contentsOf:p,encoding:.utf8))
    }

    // Injectable input is used by Linux Swift parity tests and allows strict
    // validation before showing any user-customized source phrases.
    static func fromText(chart:WenguaNativeChart,template:Data,catalog:String) throws
      -> [WenguaHealthFormationBlock] {
        guard let json = try JSONSerialization.jsonObject(with:template) as? [String:Any],
              let format = json["formation"] as? String,
              fields.allSatisfy({format.contains("{"+$0+"}")}),
              let titles=json["section_titles"] as? [String:String],
              titles["illness"] != nil else {
            throw WenguaHealthTemplateError.invalidTemplate
        }
        let rows=catalog.split(whereSeparator: \.isNewline).map(String.init)
        guard rows.count == 82,rows.first == header else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        var pairs:[String:[String]] = [:]
        var positive=0
        for row in rows.dropFirst() {
            let cols=row.components(separatedBy:"|")
            guard cols.count==7,cols.allSatisfy({ !$0.trimmingCharacters(in:.whitespaces).isEmpty }),
                  stems.contains(cols[0]),stems.contains(cols[1]),
                  cols[3]=="吉" || cols[3]=="凶" else {
                throw WenguaHealthTemplateError.invalidCatalog
            }
            let key=cols[0]+"|"+cols[1]
            guard pairs.updateValue(cols,forKey:key)==nil else {
                throw WenguaHealthTemplateError.invalidCatalog
            }
            if cols[3]=="吉" {positive+=1}
        }
        guard pairs.count==81,positive==25,
              stems.allSatisfy({ h in stems.allSatisfy({ e in pairs[h+"|"+e] != nil }) }) else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        let byID=Dictionary(uniqueKeysWithValues:chart.palaces.map{($0.id,$0)})
        guard chart.palaces.count==9,
              byID[5]?.heavenStars.isEmpty==true,
              byID[5]?.door==nil,byID[5]?.deity==nil else {
            throw WenguaCastError.invalidChart
        }
        var blocks:[WenguaHealthFormationBlock]=[]
        for id in palaceOrder {
            guard let palace=byID[id], !palace.heavenStars.isEmpty else {
                throw WenguaCastError.invalidChart
            }
            var sentences:[String]=[]
            for item in palace.heavenStars {
                guard let cols=pairs[item.carriedStem+"|"+palace.earthStem] else {
                    throw WenguaHealthTemplateError.unsupportedRealPair
                }
                let values=[cols[0],cols[1],cols[2],cols[3],cols[4],cols[5],cols[6]]
                var line=format
                for (name,value) in zip(fields,values) {
                    line=line.replacingOccurrences(of:"{"+name+"}",with:value)
                }
                // Do not surface unknown placeholders as apparently finished prose.
                guard !line.contains("{"),!line.contains("}") else {
                    throw WenguaHealthTemplateError.invalidTemplate
                }
                sentences.append(line)
            }
            blocks.append(WenguaHealthFormationBlock(
                id:id,palace:palace.gua+String(id)+"宫",sentences:sentences))
        }
        return blocks
    }
}
