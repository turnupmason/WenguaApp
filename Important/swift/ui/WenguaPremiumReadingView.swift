import SwiftUI

// Presentation only. The sole source of the verdict and timing remains the
// real V8 native reading's exact, parity-checked customer sections.
// Never compute a grade or alter a Python/Swift narration section in the UI.
struct WenguaVerdictPresentation {
    let conclusion: String
    let grade: String?
    let timing: String?

    static func from(_ reading: WenguaNativeCustomerReading) -> WenguaVerdictPresentation? {
        guard let original = reading.sections.first(where: { $0.id == "90_review" })?.text,
              let finalParagraph = original.components(separatedBy: "\n\n").last else {
            return nil
        }
        // Remove the *existing* cultural disclaimer from the prominent line;
        // the full original text remains intact on the professional tab.
        let conclusion = String(finalParagraph.components(separatedBy: "；以上只作").first ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !conclusion.isEmpty else { return nil }
        let grade: String?
        if let range = conclusion.range(of: "此病为") {
            let tail = conclusion[range.upperBound...]
            let word = String(tail.split(separator: "。", maxSplits: 1,
                                         omittingEmptySubsequences: true).first ?? "")
            grade = word.isEmpty ? nil : word
        } else {
            grade = nil
        }
        let timing = reading.sections.first(where: { $0.id == "91_timing" })?.text
        return WenguaVerdictPresentation(conclusion: conclusion, grade: grade,
                                         timing: timing)
    }
}

// Health-only literary captions for a V8 grade already decided by the engine.
// Not clinical diagnoses, treatment instructions or a second scoring model.
// The same grade always renders exactly the same copy, with no user inputs.
struct WenguaHealthGradeCaption {
    let category: String
    let epithet: String
    let interpretation: String

    static func forGrade(_ grade: String) -> WenguaHealthGradeCaption? {
        switch grade {
        case "极大吉":
            return .init(category:"吉局",epithet:"沉疴顿愈",
                         interpretation:"沉重顽疾迎刃而解，元气彻底恢复")
        case "大吉":
            return .init(category:"吉局",epithet:"邪退正复",
                         interpretation:"治疗手段极为对症，病情迅速好转")
        case "中吉":
            return .init(category:"吉局",epithet:"身心渐安",
                         interpretation:"病情发展得到控制，正逐步走向康复")
        case "小吉":
            return .init(category:"吉局",epithet:"转危为安",
                         interpretation:"虽有波折但无大碍，危险期已经过去")
        case "极小吉":
            return .init(category:"吉局",epithet:"正邪相持",
                         interpretation:"虽未根治但病情稳定，需长期精细调养")
        case "极小凶":
            return .init(category:"凶局",epithet:"风寒微染",
                         interpretation:"只是皮毛表证小疾，日常多加注意即可")
        case "小凶":
            return .init(category:"凶局",epithet:"沉疴隐现",
                         interpretation:"体内已有小病变，切勿拖延需及时就医")
        case "中凶":
            return .init(category:"凶局",epithet:"病势缠绵",
                         interpretation:"病情较为顽固反复，治疗过程面临阻力")
        case "大凶":
            return .init(category:"凶局",epithet:"元气大伤",
                         interpretation:"病情极其危重凶险，必须全力介入救治")
        case "极大凶":
            return .init(category:"凶局",epithet:"命悬一线",
                         interpretation:"运势陷入至暗绝境，急需寻求破局生机")
        default: return nil // An unknown V8 outcome must never be guessed.
        }
    }
}

// UI-only labels, projected from the exact V8 role binding that produced
// the customer's reading. Independent roles sharing one actual palace are
// composed with ／. No role is reverse-engineered from a pretty chart tile.
enum WenguaPalaceIdentity {
    static let displayOrder:[(String,String)]=[
        ("illness","病"),("doctor","西医"),("medicine","中医"),
        ("chief","大吉神"),("hour","病事"),("patient","被测人"),
        ("natal","年命"),("gender","长辈辅助")
    ]
    static func labels(_ reading:WenguaNativeCustomerReading?,
                       palaceID:Int)->[String] {
        guard let roles=reading?.rolePalaces else { return [] }
        var labels:[String]=[]
        for (key,text) in displayOrder where roles[key]==palaceID {
            if !labels.contains(text) { labels.append(text) }
        }
        return labels
    }
}

struct WenguaReturnToTop: View {
    let action:()->Void
    var body:some View {
        Button(action:action) {
            Label("回到顶部",systemImage:"arrow.up.to.line")
                .font(.system(size:14,weight:.semibold))
                .frame(maxWidth:.infinity)
                .padding(16)
                .foregroundStyle(QStyle.text)
                .background(QStyle.surface,
                            in:RoundedRectangle(cornerRadius:15))
                .overlay(RoundedRectangle(cornerRadius:15)
                    .stroke(QStyle.line.opacity(0.7),lineWidth:0.7))
        }
        .buttonStyle(.plain)
        .accessibilityHint("滚动到本次解盘的最上方")
    }
}

struct WenguaReadingTabStrip: View {
    @Binding var selection: Int
    private let labels = ["专业解卦", "专业解盘"]

    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<2, id: \.self) { index in
                Button {
                    withAnimation(.easeInOut(duration: 0.18)) { selection = index }
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: index == 0 ? "sparkle" : "text.book.closed")
                        Text(labels[index])
                    }
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundStyle(selection == index ? Color.white : QStyle.text)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(selection == index
                        ? Color(red: 0.13, green: 0.22, blue: 0.28)
                        : Color.clear, in: RoundedRectangle(cornerRadius: 11))
                }
                .buttonStyle(.plain)
                .accessibilityAddTraits(selection == index ? .isSelected : [])
            }
        }
        .padding(4)
        .background(QStyle.surface, in: RoundedRectangle(cornerRadius: 15))
    }
}

struct WenguaPremiumVerdictCard: View {
    let reading: WenguaNativeCustomerReading
    private let ink = Color(red:0.94,green:0.94,blue:0.89)
    private let muted = Color(red:0.78,green:0.83,blue:0.81)
    private let gold = Color(red:0.88,green:0.73,blue:0.45)
    private let notice = "本模型基于古籍规则算法进行时空走向推演，相关结论仅作为传统文化研究与决策视角参考，不构成任何医疗诊断或医学建议。身体不适请务必及时前往医院就医。"

    var body: some View {
        VStack(alignment:.leading,spacing:17) {
            HStack {
                Text("专 业 解 卦")
                    .font(.system(size:13,weight:.medium,design:.serif))
                    .tracking(3)
                    .foregroundStyle(gold)
                Spacer()
                Image(systemName:"seal")
                    .font(.system(size:23,weight:.ultraLight))
                    .foregroundStyle(gold)
            }
            Rectangle().fill(gold.opacity(0.32)).frame(height:1)

            if let verdict=WenguaVerdictPresentation.from(reading) {
                if let grade=verdict.grade,
                   let caption=WenguaHealthGradeCaption.forGrade(grade) {
                    Text(caption.category)
                        .font(.system(size:16,weight:.semibold,design:.serif))
                        .tracking(3)
                        .foregroundStyle(muted)
                        .accessibilityAddTraits(.isHeader)
                    Text(grade + "：" + caption.epithet)
                        .font(.system(size:29,weight:.semibold,design:.serif))
                        .foregroundStyle(gold)
                        .minimumScaleFactor(0.72)
                        .lineLimit(2)
                        .accessibilityLabel("传统古籍等级：" + grade)
                    Text(caption.interpretation)
                        .font(.system(size:17,weight:.regular,design:.serif))
                        .lineSpacing(6)
                        .foregroundStyle(ink)
                        .fixedSize(horizontal:false,vertical:true)
                } else {
                    // Unknown, pending or unsupported grades remain fail-closed.
                    Text("断词待核")
                        .font(.system(size:23,weight:.semibold,design:.serif))
                        .foregroundStyle(gold)
                    Text(verdict.conclusion)
                        .font(.system(size:15,design:.serif))
                        .foregroundStyle(ink)
                        .fixedSize(horizontal:false,vertical:true)
                }
            } else {
                Text("本次解卦结论尚无完整的原生核验依据。")
                    .font(.subheadline).foregroundStyle(ink)
            }

            Rectangle().fill(gold.opacity(0.22)).frame(height:1)
            Text(notice)
                .font(.system(size:11))
                .lineSpacing(4)
                .foregroundStyle(muted)
                .fixedSize(horizontal:false,vertical:true)
        }
        .padding(21)
        .frame(maxWidth:.infinity,alignment:.leading)
        .background(Color(red:0.11,green:0.19,blue:0.24),
                    in:RoundedRectangle(cornerRadius:22))
        .accessibilityElement(children:.contain)
    }
}
