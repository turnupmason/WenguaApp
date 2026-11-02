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
                Text(WenguaDomainContract.lookup(reading.topicID)?.interpretationReady == true ?
                     "分项查看盘面、人物用神与条件依据。" :
                     "真实历法与九宫事实；专题取用与断词仍在开发中。")
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
                            customerParagraph(section.text,sectionID:section.id)
                                .padding(.top,9)
                        }
                        .font(.system(size:13))
                        .tint(gold)
                    } else {
                        customerParagraph(section.text,sectionID:section.id)
                    }
                }
                .padding(18)
                .frame(maxWidth:.infinity,alignment:.leading)
                .background(QStyle.surface,
                            in:RoundedRectangle(cornerRadius:18))
                .overlay(RoundedRectangle(cornerRadius:18)
                    .stroke(QStyle.line.opacity(0.65),lineWidth:0.6))
            }
            if let reference=reading.timingReferenceSections,!reference.isEmpty {
                DisclosureGroup("所选时辰 · 健康盘象等级依据") {
                    ForEach(reference) { section in
                        VStack(alignment:.leading,spacing:8) {
                            Text(section.title).font(.headline)
                            customerParagraph(section.text,sectionID:section.id)
                        }.padding(.vertical,8)
                    }
                }
                .padding(18)
                .background(QStyle.surface,in:RoundedRectangle(cornerRadius:18))
            }
        }
    }

    private func customerParagraph(_ text:String,sectionID:String)->some View {
        let blocks=WenguaReadingLayout.blocks(text,sectionID:sectionID)
        return VStack(alignment:.leading,spacing:18) {
            ForEach(blocks.indices,id:\.self) { index in
                let block=blocks[index]
                VStack(alignment:.leading,spacing:10) {
                    if let heading=block.heading {
                        Text(heading).font(.subheadline.weight(.semibold)).foregroundStyle(gold)
                    }
                    let paragraphs=WenguaReadingLayout.paragraphs(block)
                    ForEach(paragraphs.indices,id:\.self) { row in
                        let raw=paragraphs[row]
                        let prefix=(block.heading ?? "")+"："
                        let visible=(row==0 && block.heading != nil && raw.hasPrefix(prefix)) ?
                            String(raw.dropFirst(prefix.count)) : raw
                        let paragraph=visible.trimmingCharacters(in:.whitespacesAndNewlines)
                        if !paragraph.isEmpty {
                            Text(paragraph)
                                .font(.system(.body,design:.serif))
                                .lineSpacing(5)
                                .foregroundStyle(QStyle.text)
                                .fixedSize(horizontal:false,vertical:true)
                                .textSelection(.enabled)
                                .frame(maxWidth:.infinity,alignment:.leading)
                        }
                    }
                }
            }
        }
    }
}
