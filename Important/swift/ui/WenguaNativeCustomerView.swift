import SwiftUI

// Customer-visible real native-chart evidence. Intentionally never accesses
// internal grade, score, +/-, or the sealed V3.9.1 historical example text.
struct WenguaNativeCustomerView: View {
    let reading: WenguaNativeCustomerReading

    var body: some View {
        VStack(alignment:.leading,spacing:12) {
            Text("本次时辰 · 传统盘象")
                .font(.title3.weight(.semibold))
            ForEach(reading.sections) { section in
                VStack(alignment:.leading,spacing:8) {
                    if section.id=="03classical" || section.id=="88subject" || section.id=="87vnext" {
                        DisclosureGroup(section.title) {
                            Text(section.text)
                                .font(.subheadline)
                                .fixedSize(horizontal:false,vertical:true)
                                .textSelection(.enabled)
                        }
                    } else {
                        Text(section.title).font(.headline)
                        Text(section.text)
                            .font(.subheadline)
                            .fixedSize(horizontal:false,vertical:true)
                            .textSelection(.enabled)
                    }
                }
                .frame(maxWidth:.infinity,alignment:.leading)
                .padding(14)
                .background(.white,in:RoundedRectangle(cornerRadius:12))
            }
        }
    }
}
