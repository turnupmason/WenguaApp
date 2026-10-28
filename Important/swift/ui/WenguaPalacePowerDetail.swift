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

    var body: some View {
        VStack(spacing:10) {
            if let p=real,p.id != 5,catalog != nil,monthElement != nil {
                powerCard("八门") {
                    symbolText(p.door ?? "待核",kind:"door")
                    Text("月令："+doorMonth(p.door ?? ""))
                    Text("力量："+sourcePower("door",p.door ?? ""))
                        .fontWeight(.semibold)
                }
                powerCard("八神") {
                    symbolText(p.deity ?? "待核",kind:"deity")
                    Text("八神不以月令取旺衰")
                    Text("力量："+deityPower(p.deity ?? ""))
                        .fontWeight(.semibold)
                }
                powerCard("九星") {
                    ForEach(Array(p.heavenStars.enumerated()),id:\.offset) { entry in
                        let star=entry.element
                        symbolText(star.star,kind:"star")
                        Text("月令："+starMonth(star.star))
                        Text("力量："+sourcePower("star",star.star))
                            .fontWeight(.semibold)
                        if entry.offset != p.heavenStars.count-1 {
                            Divider().padding(.vertical,4)
                        }
                    }
                }
                powerCard("天盘干") {
                    // Preserve star->carrier identity even when the visual
                    // order puts Tianqin 丁 to the left of Tianrui 戊.
                    ForEach(Array(p.heavenStars.reversed().enumerated()),id:\.offset) { entry in
                        let star=entry.element
                        symbolText(star.carriedStem,kind:"stem")
                        Text(star.star+"携干 · "+
                             star.stages.map{$0.branch+$0.stage}.joined(separator:"、"))
                        Text("力量："+stemPower(star.carriedStem,star.stages))
                            .fontWeight(.semibold)
                        if entry.offset != p.heavenStars.count-1 {
                            Divider().padding(.vertical,4)
                        }
                    }
                }
                powerCard("地盘干") {
                    symbolText(p.earthStem,kind:"stem")
                    Text(p.earthStages.map{$0.branch+$0.stage}.joined(separator:"、"))
                    Text("力量："+stemPower(p.earthStem,p.earthStages))
                        .fontWeight(.semibold)
                }
            } else {
                Text("真实九宫或源200格未核定，不能推定星门神干力量。")
                    .font(.subheadline)
                    .foregroundStyle(QStyle.secondary)
                    .frame(maxWidth:.infinity)
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
