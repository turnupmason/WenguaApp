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

struct WenguaReadingTabStrip: View {
    @Binding var selection: Int
    private let labels = ["接卦", "专业解盘"]

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
        .background(.white, in: RoundedRectangle(cornerRadius: 15))
    }
}

struct WenguaPremiumVerdictCard: View {
    let reading: WenguaNativeCustomerReading
    private let ink = Color(red: 0.94, green: 0.94, blue: 0.89)
    private let muted = Color(red: 0.68, green: 0.76, blue: 0.76)
    private let gold = Color(red: 0.88, green: 0.73, blue: 0.45)

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 5) {
                    Text("接 卦 语")
                        .font(.system(size: 12, weight: .medium, design: .serif))
                        .tracking(4)
                        .foregroundStyle(gold)
                    Text("此刻之问 · 本卦之象")
                        .font(.system(size: 13))
                        .foregroundStyle(muted)
                }
                Spacer()
                Image(systemName: "seal")
                    .font(.system(size: 24, weight: .ultraLight))
                    .foregroundStyle(gold)
            }
            Rectangle().fill(gold.opacity(0.32)).frame(height: 1)

            if let verdict = WenguaVerdictPresentation.from(reading) {
                if let grade = verdict.grade {
                    Text(grade)
                        .font(.system(size: 36, weight: .semibold, design: .serif))
                        .foregroundStyle(gold)
                        .accessibilityLabel("传统盘象结论：" + grade)
                } else {
                    Text("结论待核")
                        .font(.system(size: 28, weight: .semibold, design: .serif))
                        .foregroundStyle(ink)
                }
                Text(verdict.conclusion)
                    .font(.system(size: 17, weight: .regular, design: .serif))
                    .foregroundStyle(ink)
                    .fixedSize(horizontal: false, vertical: true)
                    .textSelection(.enabled)
                if let timing = verdict.timing, !timing.isEmpty {
                    Rectangle().fill(gold.opacity(0.22)).frame(height: 1)
                    Text("应期提示")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(gold)
                    Text(timing)
                        .font(.system(size: 13))
                        .foregroundStyle(muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
            } else {
                Text("本次接卦结论尚无完整的原生核验依据。")
                    .font(.subheadline)
                    .foregroundStyle(ink)
            }
            Text("传统古籍象意参考 · 不作医学诊断或现实预后")
                .font(.system(size: 11))
                .foregroundStyle(muted)
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(red: 0.11, green: 0.19, blue: 0.24),
                    in: RoundedRectangle(cornerRadius: 22))
        .accessibilityElement(children: .contain)
    }
}
