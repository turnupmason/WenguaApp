import SwiftUI

// Static native-gradient atmosphere; no loading, motion, or remote media.
struct WenguaCloudAtmosphere: View {

    var body: some View {
        GeometryReader { geo in
            ZStack {
                LinearGradient(
                    colors: [Color(red:0.025,green:0.08,blue:0.16),
                             Color(red:0.045,green:0.17,blue:0.28),
                             Color(red:0.09,green:0.24,blue:0.31)],
                    startPoint:.topLeading,endPoint:.bottomTrailing)
                RadialGradient(colors:[Color(red:0.54,green:0.78,blue:0.91).opacity(0.38),
                                       .clear],center:.init(x:0.72,y:0.35),
                               startRadius:12,endRadius:geo.size.width*0.75)
                Ellipse()
                    .fill(Color(red:0.63,green:0.82,blue:0.94).opacity(0.24))
                    .frame(width:geo.size.width*1.35,height:geo.size.height*0.23)
                    .blur(radius:48)
                    .offset(x:36,y:geo.size.height*0.27)
                Ellipse()
                    .fill(Color(red:0.80,green:0.91,blue:0.97).opacity(0.19))
                    .frame(width:geo.size.width*1.6,height:geo.size.height*0.20)
                    .blur(radius:52)
                    .offset(x:-22,y:geo.size.height*0.37)
                Ellipse()
                    .fill(Color(red:0.44,green:0.72,blue:0.92).opacity(0.19))
                    .frame(width:geo.size.width*1.3,height:geo.size.height*0.22)
                    .blur(radius:50)
                    .offset(x:-45,y:-geo.size.height*0.26)
                Circle()
                    .stroke(Color.white.opacity(0.16),lineWidth:0.6)
                    .frame(width:min(geo.size.width*0.82,350))
                    .overlay {
                        Circle().stroke(Color.white.opacity(0.08),lineWidth:0.7)
                            .padding(25)
                    }
                    .offset(y:-geo.size.height*0.10)
                ForEach(0..<20,id:\.self) { i in
                    Circle()
                        .fill(Color.white.opacity(i.isMultiple(of:3) ? 0.46:0.17))
                        .frame(width:i.isMultiple(of:4) ? 2.6:1.2)
                        .position(
                            x:geo.size.width*CGFloat((i*37+19)%100)/100,
                            y:geo.size.height*CGFloat((i*61+13)%100)/100)
                }
            }
            .frame(width:geo.size.width,height:geo.size.height)
            .clipped()
        }
        .accessibilityHidden(true)
        .allowsHitTesting(false)
    }
}

struct WenguaAppearanceMenu: View {
    @AppStorage("wengua:appearance") private var mode = "system"
    private let options:[(String,String,String)] = [
        ("system","跟随系统","circle.lefthalf.filled"),
        ("light","日间模式","sun.max"),
        ("dark","夜间模式","moon.stars")
    ]

    var body: some View {
        Menu {
            ForEach(0..<options.count,id:\.self) { index in
                let option=options[index]
                Button {
                    mode=option.0
                } label: {
                    Label(option.1,systemImage:mode==option.0 ?
                          "checkmark.circle.fill":option.2)
                }
            }
        } label: {
            Image(systemName:mode=="dark" ? "moon.stars.fill" :
                             mode=="light" ? "sun.max.fill" : "circle.lefthalf.filled")
                .font(.system(size:17,weight:.medium))
                .frame(width:38,height:38)
                .background(.thinMaterial,in:Circle())
                .accessibilityLabel("切换日间夜间模式")
        }
    }
}

struct WenguaCloudWelcomeScreen: View {
    let begin: () -> Void

    var body: some View {
        GeometryReader { geo in
            ZStack {
                WenguaCloudAtmosphere().ignoresSafeArea()
                ScrollView {
                    VStack(alignment:.leading,spacing:0) {
                        HStack {
                            WenguaMark(size:46)
                            Text("W E N G U A")
                                .font(.system(size:12,weight:.semibold,design:.rounded))
                                .tracking(2.5)
                                .foregroundStyle(Color.white.opacity(0.78))
                            Spacer()
                            WenguaAppearanceMenu().tint(.white)
                        }
                        .padding(.top,20)

                        Spacer(minLength:geo.size.height*0.14)
                        Text("借天地之势，成自己之事")
                            .font(.system(size:12,weight:.medium))
                            .tracking(4)
                            .foregroundStyle(Color(red:0.87,green:0.75,blue:0.54))
                        Text("欢迎来到问卦")
                            .font(.system(size:39,weight:.medium,design:.serif))
                            .tracking(3)
                            .foregroundStyle(.white)
                            .lineSpacing(11)
                            .padding(.top,20)
                            .accessibilityAddTraits(.isHeader)
                        Text("古籍为鉴 · 时势为引")
                            .font(.system(size:20,weight:.medium,design:.serif))
                            .foregroundStyle(Color.white.opacity(0.92))
                            .padding(.top,21)
                        Text("依托二十余部易学古籍的解图体系，历时数年人工搭建核心模型。严格以古籍规则助攻推演，深度还原事情发展趋势。助你洞察时局先机，破局当下迷茫。让千年的时间局密码，如今触手可及。")
                            .font(.system(size:15))
                            .lineSpacing(7)
                            .foregroundStyle(Color.white.opacity(0.72))
                            .fixedSize(horizontal:false,vertical:true)
                            .padding(.top,13)

                        Spacer(minLength:geo.size.height*0.11)
                        HStack(spacing:5) {
                            welcomeTag("古籍为本")
                            welcomeTag("规则推演")
                            welcomeTag("东方智慧")
                            welcomeTag("决策指引")
                            welcomeTag("破局迷茫")
                        }
                        .padding(.bottom,19)
                        Button(action:begin) {
                            HStack {
                                Spacer()
                                Text("开始问卦")
                                    .font(.system(size:18,weight:.semibold))
                                    .tracking(2)
                                Spacer()
                                Image(systemName:"arrow.up.right")
                                    .font(.system(size:15,weight:.bold))
                            }
                            .foregroundStyle(Color(red:0.09,green:0.17,blue:0.24))
                            .padding(.horizontal,23)
                            .frame(height:59)
                            .background(Color(red:0.92,green:0.82,blue:0.63),
                                        in:RoundedRectangle(cornerRadius:17))
                        }
                        .buttonStyle(.plain)
                        Text("30秒静心 · 实时起局 · 一事一占")
                            .font(.system(size:12))
                            .tracking(1)
                            .foregroundStyle(Color.white.opacity(0.74))
                            .frame(maxWidth:.infinity)
                            .padding(.top,16)
                            .padding(.bottom,23)
                    }
                    .padding(.horizontal,29)
                    .frame(minHeight:geo.size.height,alignment:.topLeading)
                }
                .scrollIndicators(.hidden)
            }
        }
        .preferredColorScheme(.dark) // The welcome cloud artwork is deliberately midnight.
    }

    private func welcomeTag(_ title:String)->some View {
        Text(title)
            .font(.system(size:10,weight:.medium))
            .tracking(0)
            .lineLimit(1)
            .minimumScaleFactor(0.72)
            .foregroundStyle(Color.white.opacity(0.82))
            .padding(.horizontal,4)
            .padding(.vertical,8)
            .frame(maxWidth:.infinity)
            .background(Color.white.opacity(0.09),in:Capsule())
            .overlay(Capsule().stroke(Color.white.opacity(0.13),lineWidth:0.6))
    }
}
