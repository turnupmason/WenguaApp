import SwiftUI

// Exact source-power presentation: every value comes from the same native
// V8 200-cell tables used by production. No new scorer and no palace net
// auspice score can masquerade as a star, door, deity, or stem strength.
struct WenguaPalacePowerDetail: View {
    let palace: QPalace
    let monthBranch: String
    private var catalog: WenguaNativeEnergyCatalog? {
        try? WenguaNativeEnergyBundle.fromBundle()
    }
    private var monthElement: String? {
        try? WenguaVNextEngine.monthly(monthBranch)
    }
    private var real: WenguaNativePalace? {palace.computed}

    private func sourcePower(_ kind:String,_ symbol:String,
                             _ stages:[WenguaNativeStage]=[])->String {
        guard let catalog,let month=monthElement else {return "待核"}
        let factor=try? WenguaVNextEngine.factor(kind:kind,symbol:symbol,
            palace:palace.id,month:month,catalog:catalog,stages:stages)
        return factor?.strength ?? "待核"
    }
    private func stemPower(_ symbol:String,_ stages:[WenguaNativeStage])->String {
        let combined=sourcePower("stem",symbol,stages)
        if combined != "待核" {return combined}
        if stages.count>1 {
            // Branches can yield different legitimate 200-grid strengths.
            // Keep both instead of silently discarding them or averaging.
            return stages.map{$0.branch+"："+sourcePower("stem",symbol,[$0])}
                         .joined(separator:"／")
        }
        return "待核"
    }
    private func starMonth(_ star:String)->String {
        guard let element=WenguaVNextEngine.starElement[star],
              let month=monthElement else {return "待核"}
        return (try? WenguaVNextEngine.starMonth(element,month)) ?? "待核"
    }
    private func doorMonth(_ door:String)->String {
        guard let element=WenguaVNextEngine.doorElement[door],
              let month=monthElement else {return "待核"}
        return (try? WenguaVNextEngine.normalMonth(element,month)) ?? "待核"
    }
    private func deityPower(_ deity:String)->String {
        guard let element=WenguaVNextEngine.godElement[deity] else {return "待核"}
        let direction=try? WenguaVNextEngine.directed(element,palace.element)
        return direction.flatMap{WenguaVNextEngine.godTiers[$0]} ?? "待核"
    }

    // Small independent view builders avoid SwiftUI's expensive type-check
    // of the former five-card monolithic body; source calls are unchanged.
    var body: some View {
        VStack(spacing:10) {
            if let p=real,p.id != 5,catalog != nil,monthElement != nil {
                doorCard(p)
                deityCard(p)
                starsCard(p)
                heavenStemsCard(p)
                earthStemCard(p)
            } else {
                Text("真实九宫或源200格未核定，不能推定星门神干力量。")
                    .font(.subheadline)
                    .foregroundStyle(QStyle.secondary)
                    .frame(maxWidth:.infinity)
            }
        }
    }

    // Concise reader-facing symbol meanings. These are explanatory UI
    // labels only; they never participate in V8.0 scoring or verdicts.
    private static let godMeanings:[String:String]=[
        "值符":"统领、掌控与护持","螣蛇":"疑虑、反复与缠绕",
        "腾蛇":"疑虑、反复与缠绕","太阴":"隐情、谨慎与筹划",
        "六合":"合作、协调与关系","白虎":"激烈、损伤与决断",
        "玄武":"秘密、迂回与迷惑","九地":"稳守、积蓄与缓慢",
        "九天":"发展、视野与行动"]
    private static let starMeanings:[String:String]=[
        "天蓬星":"谋略、风险与流动","天芮星":"疾病、负担与问题",
        "天冲星":"行动、冲劲与速度","天辅星":"学习、文书与辅助",
        "天禽星":"中宫寄星，随天芮同宫","天心星":"医药、治理与谋划",
        "天柱星":"言语、阻力与冲突","天任星":"负责、稳定与守成",
        "天英星":"表现、名望与显露"]
    private static let doorMeanings:[String:String]=[
        "休门":"休养、交流与调息","生门":"生机、财源与发展",
        "伤门":"竞争、损伤与行动","杜门":"遮蔽、阻隔与封闭",
        "景门":"表现、形象与名声","死门":"停滞、结束与收藏",
        "惊门":"惊动、口舌与变化","开门":"开放、机会与事业"]
    private func meaning(_ symbol:String,kind:String)->String {
        if kind=="deity" {return Self.godMeanings[symbol] ?? "环境与人事"}
        if kind=="star" {return Self.starMeanings[symbol] ?? "事态动势"}
        return Self.doorMeanings[symbol] ?? "事情进退"
    }
    private func explain(_ symbol:String,kind:String)->some View {
        Text("象意："+meaning(symbol,kind:kind))
            .font(.caption).foregroundStyle(QStyle.secondary)
    }
    private func doorCard(_ p:WenguaNativePalace) -> some View {
        powerCard("八门") {
            symbolText(p.door ?? "待核",kind:"door")
            explain(p.door ?? "",kind:"door")
            Text("月令："+doorMonth(p.door ?? ""))
            Text("力量："+sourcePower("door",p.door ?? ""))
                .fontWeight(.semibold)
        }
    }

    private func deityCard(_ p:WenguaNativePalace) -> some View {
        powerCard("八神") {
            symbolText(p.deity ?? "待核",kind:"deity")
            explain(p.deity ?? "",kind:"deity")
            Text("八神不以月令取旺衰")
            Text("力量："+deityPower(p.deity ?? ""))
                .fontWeight(.semibold)
        }
    }

    private func starsCard(_ p:WenguaNativePalace) -> some View {
        powerCard("九星") {
            ForEach(Array(p.heavenStars.enumerated()),id:\.offset) { entry in
                starFact(entry.element)
                if entry.offset < p.heavenStars.count-1 {
                    Divider().padding(.vertical,4)
                }
            }
        }
    }

    private func starFact(_ star:WenguaNativeStar) -> some View {
        VStack(spacing:6) {
            symbolText(star.star,kind:"star")
            explain(star.star,kind:"star")
            Text("月令："+starMonth(star.star))
            Text("力量："+sourcePower("star",star.star))
                .fontWeight(.semibold)
        }
    }

    private func heavenStemsCard(_ p:WenguaNativePalace) -> some View {
        powerCard("天盘干") {
            // Two distinct sky carriers, shown individually in original
            // source order reversed solely for the left/right UI layout.
            ForEach(Array(p.heavenStars.reversed().enumerated()),id:\.offset) { entry in
                heavenStemFact(entry.element)
                if entry.offset < p.heavenStars.count-1 {
                    Divider().padding(.vertical,4)
                }
            }
        }
    }

    private func heavenStemFact(_ star:WenguaNativeStar) -> some View {
        let life = star.stages.map { $0.branch + $0.stage }.joined(separator:"、")
        return VStack(spacing:6) {
            symbolText(star.carriedStem,kind:"stem")
            Text(star.star+"携干 · "+life)
            Text("力量："+stemPower(star.carriedStem,star.stages))
                .fontWeight(.semibold)
        }
    }

    private func earthStemCard(_ p:WenguaNativePalace) -> some View {
        let life = p.earthStages.map { $0.branch + $0.stage }.joined(separator:"、")
        return powerCard("地盘干") {
            symbolText(p.earthStem,kind:"stem")
            Text(life)
            Text("力量："+stemPower(p.earthStem,p.earthStages))
                .fontWeight(.semibold)
            if let centre=palace.hostedCentreEarthStem {
                let stages=p.branches.compactMap { branch -> WenguaNativeStage? in
                    guard let stage=WenguaNativeCore.stages[centre]?[branch]
                    else {return nil}
                    return WenguaNativeStage(branch:branch,stage:stage)
                }
                Divider().padding(.vertical,4)
                Text("天禽寄宫地盘干").font(.caption)
                    .foregroundStyle(QStyle.secondary)
                symbolText(centre,kind:"stem")
                Text(stages.map{$0.branch+$0.stage}.joined(separator:"、"))
                Text("力量："+stemPower(centre,stages)).fontWeight(.semibold)
            }
        }
    }
    private func symbolText(_ symbol:String,kind:String)->some View {
        Text(symbol)
            .font(.system(size:24,weight:.semibold,design:.serif))
            .foregroundStyle(QFive.shade(kind,symbol.replacingOccurrences(of:"星",with:"")))
            .minimumScaleFactor(0.7)
    }
    private func powerCard<Content:View>(_ title:String,
                    @ViewBuilder content:()->Content)->some View {
        VStack(alignment:.center,spacing:6) {
            Text(title)
                .font(.system(size:14,weight:.semibold))
                .foregroundStyle(QStyle.secondary)
            content()
                .font(.system(size:14))
                .foregroundStyle(QStyle.text)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth:.infinity,alignment:.center)
        .padding(15)
        .background(QStyle.surface,in:RoundedRectangle(cornerRadius:15))
    }
}
