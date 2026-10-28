import SwiftUI

// Three distinct moments: welcoming, category discovery and a verified topic.
// No casting, scores or domain heuristics live inside this screen.
struct WenguaDomainJourneyScreen: View {
    let select:(QuestionTopic)->Void
    let goHome:()->Void
    @State private var chosenDomain:String?
    @State private var chosenTopic:String?
    @State private var revealed=false

    private var domain:QuestionDomain? {
        QuestionCatalog.domains.first(where:{$0.id==chosenDomain})
    }
    private var selected:QuestionTopic? {
        domain?.topics.first(where:{$0.id==chosenTopic})
    }
    private let columns=[GridItem(.flexible(),spacing:12),
                         GridItem(.flexible(),spacing:12)]

    var body:some View {
        NavigationStack {
            ScrollView {
                VStack(alignment:.leading,spacing:22) {
                    ZStack(alignment:.bottomLeading) {
                        WenguaCloudAtmosphere()
                        VStack(alignment:.leading,spacing:11) {
                            Text("QUESTION · "+(domain == nil ? "01" : "02"))
                                .font(.system(size:11,weight:.medium))
                                .tracking(2.8)
                                .foregroundStyle(Color(red:0.9,green:0.78,blue:0.57))
                            Text(domain == nil ? "请问有什么疑惑？" : "这一次想问什么？")
                                .font(.system(size:27,weight:.medium,design:.serif))
                                .foregroundStyle(.white)
                            Text(domain == nil ?
                                 "选择一个方向，让古籍规则为你逐层解读。" :
                                 domain!.title+" · 先确定具体事项")
                                .font(.system(size:13))
                                .foregroundStyle(Color.white.opacity(0.78))
                        }
                        .padding(23)
                    }
                    .frame(height:222)
                    .clipShape(RoundedRectangle(cornerRadius:22))

                    if let domain {
                        Button {
                            withAnimation(.easeInOut(duration:0.22)) {
                                chosenDomain=nil
                                chosenTopic=nil
                            }
                        } label: {
                            Label("全部问事领域",systemImage:"arrow.left")
                                .font(.system(size:13,weight:.medium))
                                .foregroundStyle(QStyle.secondary)
                        }
                        .buttonStyle(.plain)
                        VStack(alignment:.leading,spacing:14) {
                            Text(domain.title)
                                .font(.system(size:24,weight:.semibold,design:.serif))
                                .foregroundStyle(QStyle.text)
                            Text("请只选择本次所问的一件事")
                                .font(.subheadline).foregroundStyle(QStyle.secondary)
                            ForEach(domain.topics) { topic in
                                topicRow(topic)
                            }
                        }
                        if let selected {
                            Button {
                                if selected.enabled { select(selected) }
                            } label: {
                                HStack {
                                    Text(selected.enabled ? "继续 · 填写问事信息" : "此专题开发中")
                                    Spacer()
                                    Image(systemName:selected.enabled ?
                                          "arrow.right":"lock")
                                }
                                .font(.system(size:16,weight:.semibold))
                                .padding(18)
                                .foregroundStyle(Color(red:0.11,green:0.19,blue:0.24))
                                .background(Color(red:0.91,green:0.79,blue:0.57),
                                            in:RoundedRectangle(cornerRadius:16))
                            }
                            .disabled(!selected.enabled)
                            .opacity(selected.enabled ? 1 : 0.48)
                            .buttonStyle(.plain)
                            Text(selected.enabled ?
                                 "之后填写人物信息，静心30秒，按手机确认时刻离线起盘。" :
                                 "每个领域使用独立用神与断案模板；未验收时不套用疾病规则。")
                                .font(.caption).foregroundStyle(QStyle.secondary)
                        }
                    } else {
                        VStack(alignment:.leading,spacing:6) {
                            Text("探索问事领域")
                                .font(.system(size:24,weight:.semibold,design:.serif))
                            Text("从疑惑开始，逐层明晰。")
                                .font(.subheadline).foregroundStyle(QStyle.secondary)
                        }
                        LazyVGrid(columns:columns,spacing:12) {
                            ForEach(QuestionCatalog.domains.indices,id:\.self) { index in
                                let item=QuestionCatalog.domains[index]
                                Button {
                                    withAnimation(.easeInOut(duration:0.24)) {
                                        chosenDomain=item.id
                                        chosenTopic=nil
                                    }
                                } label: {
                                    VStack(alignment:.leading,spacing:14) {
                                        HStack {
                                            Image(systemName:item.symbol)
                                                .font(.system(size:23,weight:.light))
                                                .foregroundStyle(Color(red:0.66,green:0.57,blue:0.35))
                                            Spacer()
                                            Image(systemName:"arrow.up.right")
                                                .font(.system(size:10,weight:.medium))
                                                .foregroundStyle(QStyle.secondary)
                                        }
                                        Text(item.title)
                                            .font(.system(size:16,weight:.semibold,design:.serif))
                                            .foregroundStyle(QStyle.text)
                                        Text(item.id=="health" ?
                                             "病情轻重 · 已接入" : "专题开发中")
                                            .font(.system(size:11))
                                            .foregroundStyle(QStyle.secondary)
                                    }
                                    .frame(maxWidth:.infinity,minHeight:108,alignment:.leading)
                                    .padding(17)
                                    .background(QStyle.surface,
                                                in:RoundedRectangle(cornerRadius:18))
                                    .overlay(RoundedRectangle(cornerRadius:18)
                                        .stroke(QStyle.line.opacity(0.55),lineWidth:0.7))
                                }
                                .buttonStyle(.plain)
                                .opacity(revealed ? 1:0)
                                .offset(y:revealed ? 0:20)
                                .animation(.easeOut(duration:0.55)
                                    .delay(Double(index)*0.045),value:revealed)
                            }
                        }
                        Text("只有已完成独立规则与离线验收的专题可以正式问卦。")
                            .font(.system(size:12))
                            .foregroundStyle(QStyle.secondary)
                    }
                }
                .padding(.horizontal,18)
                .padding(.top,16)
                .padding(.bottom,40)
            }
            .background(QStyle.backing)
            .navigationTitle("问卦")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement:.topBarLeading) {
                    Button(action:goHome) {
                        Image(systemName:"house")
                            .accessibilityLabel("返回欢迎页")
                    }
                }
                ToolbarItemGroup(placement:.topBarTrailing) {
                    NavigationLink {
                        WenguaLocalHistoryView()
                    } label: {
                        Image(systemName:"clock.arrow.circlepath")
                            .accessibilityLabel("本地问卦记录")
                    }
                    WenguaAppearanceMenu()
                }
            }
            .onAppear { revealed=true }
        }
    }

    private func topicRow(_ item:QuestionTopic)->some View {
        let chosen=chosenTopic==item.id
        return Button {
            withAnimation(.easeInOut(duration:0.15)) { chosenTopic=item.id }
        } label: {
            HStack(spacing:12) {
                Image(systemName:chosen ? "checkmark.circle.fill" : "circle")
                    .font(.system(size:21))
                    .foregroundStyle(chosen ? Color(red:0.67,green:0.51,blue:0.24)
                                              : QStyle.secondary)
                VStack(alignment:.leading,spacing:5) {
                    Text(item.title)
                        .font(.system(size:16,weight:.semibold))
                        .foregroundStyle(QStyle.text)
                    Text(item.enabled ? "已接入本机离线规则解盘" : "独立模板校验中")
                        .font(.caption).foregroundStyle(QStyle.secondary)
                }
                Spacer()
                if !item.enabled {
                    Image(systemName:"lock")
                        .font(.caption)
                        .foregroundStyle(QStyle.secondary)
                }
            }
            .padding(17)
            .background(chosen ? Color(red:0.76,green:0.63,blue:0.38).opacity(0.10)
                               : QStyle.surface,
                        in:RoundedRectangle(cornerRadius:16))
            .overlay(RoundedRectangle(cornerRadius:16)
                .stroke(chosen ? Color(red:0.76,green:0.63,blue:0.38)
                               : QStyle.line.opacity(0.5),lineWidth:chosen ? 1.1:0.6))
        }
        .buttonStyle(.plain)
    }
}
