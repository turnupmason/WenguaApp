import SwiftUI

// Professional presentation of the exact offline V8 sections. Display-only:
// original section IDs, titles and customer paragraphs remain unchanged.
struct WenguaNativeCustomerView: View {
    let reading: WenguaNativeCustomerReading

    private let gold = Color(red:0.72,green:0.56,blue:0.31)

    var body: some View {
        VStack(alignment:.leading,spacing:15) {
            VStack(alignment:.leading,spacing:9) {
                HStack(spacing:9) {
                    Image(systemName:"text.book.closed")
                        .font(.system(size:20,weight:.light))
                        .foregroundStyle(gold)
                    Text("专业解盘")
                        .font(.system(size:23,weight:.semibold,design:.serif))
                        .foregroundStyle(QStyle.text)
                }
                Text("据本次真实九宫，逐层呈现古籍条件、用神落宫、吉凶及应期依据。")
                    .font(.system(size:13))
                    .foregroundStyle(QStyle.secondary)
                    .fixedSize(horizontal:false,vertical:true)
            }
            .padding(.bottom,6)

            ForEach(reading.sections.indices,id:\.self) { index in
                let section=reading.sections[index]
                VStack(alignment:.leading,spacing:12) {
                    HStack(alignment:.center,spacing:10) {
                        Text(String(format:"%02d",index+1))
                            .font(.system(size:12,weight:.medium,design:.monospaced))
                            .foregroundStyle(gold)
                        Rectangle()
                            .fill(gold.opacity(0.5))
                            .frame(width:2,height:19)
                        Text(section.title)
                            .font(.system(size:17,weight:.semibold,design:.serif))
                            .foregroundStyle(QStyle.text)
                        Spacer(minLength:0)
                    }
                    if ["03classical","88subject","87vnext"].contains(section.id) {
                        DisclosureGroup("展开原文依据") {
                            customerParagraph(section.text)
                                .padding(.top,9)
                        }
                        .font(.system(size:13))
                        .tint(gold)
                    } else {
                        customerParagraph(section.text)
                    }
                }
                .padding(18)
                .frame(maxWidth:.infinity,alignment:.leading)
                .background(QStyle.surface,
                            in:RoundedRectangle(cornerRadius:18))
                .overlay(RoundedRectangle(cornerRadius:18)
                    .stroke(QStyle.line.opacity(0.65),lineWidth:0.6))
            }
        }
    }

    private func customerParagraph(_ text:String)->some View {
        Text(text)
            .font(.system(size:15,weight:.regular,design:.serif))
            .lineSpacing(6)
            .foregroundStyle(QStyle.text)
            .fixedSize(horizontal:false,vertical:true)
            .textSelection(.enabled)
    }
}
