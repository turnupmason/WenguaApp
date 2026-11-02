import SwiftUI

// Display rhythm only. The existing calmEnds deadline controls the full
// thirty-second gate and the actual cast still captures its confirmation time.
struct WenguaMeditationBeat {
    let lift: Double
    let ripple: Double
    let chantIndex: Int

    static func at(elapsed: Double, active: Bool) -> WenguaMeditationBeat {
        guard active, elapsed.isFinite else {
            return .init(lift: 0, ripple: 1, chantIndex: 0)
        }
        let time = max(0, elapsed)
        let phase = time.truncatingRemainder(dividingBy: 1.6) / 1.6
        // Raise the mallet, then return to the wooden fish once each cycle.
        let lift = pow(sin(.pi * phase), 2)
        return .init(lift: lift, ripple: phase,
                     chantIndex: Int(time.truncatingRemainder(dividingBy: 6.4) / 1.6))
    }
}

struct WenguaMeditationScene: View {
    let startedAt: Date?
    let isActive: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.scenePhase) private var scenePhase

    private let ink = Color(red: 0.16, green: 0.25, blue: 0.24)
    private let gold = Color(red: 0.71, green: 0.51, blue: 0.25)
    private let chant = ["南无", "阿弥", "陀佛", "静心"]

    var body: some View {
        let animates = isActive && !reduceMotion && scenePhase == .active
        TimelineView(.animation(minimumInterval: 1.0 / 30, paused: !animates)) { frame in
            let beat = WenguaMeditationBeat.at(
                elapsed: startedAt.map { frame.date.timeIntervalSince($0) } ?? 0,
                active: animates)
            VStack(spacing: 8) {
                Canvas { context, size in
                    drawMonk(context: context, size: size, beat: beat)
                }
                .aspectRatio(360.0 / 250, contentMode: .fit)
                .frame(maxWidth: 340)
                .accessibilityHidden(true)
                HStack(spacing: 16) {
                    ForEach(chant.indices, id: \.self) { index in
                        Text(chant[index])
                            .foregroundStyle(isActive && index == beat.chantIndex ? ink : gold)
                            .opacity(!animates || index == beat.chantIndex ? 1 : 0.45)
                    }
                }
                .font(.system(size: 17, weight: .medium, design: .serif))
                .accessibilityHidden(true)
                Text(isActive ? "随木鱼轻叩，默念心中所问" : "安住此刻，静候心定")
                    .font(.footnote)
                    .foregroundStyle(QStyle.secondary)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(isActive ? "小和尚敲木鱼，静心默念中" : "小和尚静坐")
    }

    private func drawMonk(context original: GraphicsContext, size: CGSize,
                          beat: WenguaMeditationBeat) {
        var context = original
        context.scaleBy(x: size.width / 360, y: size.height / 250)
        let skin = Color(red: 0.94, green: 0.76, blue: 0.56)
        let robe = Color(red: 0.77, green: 0.42, blue: 0.20)
        let lightRobe = Color(red: 0.91, green: 0.63, blue: 0.30)
        let wood = Color(red: 0.49, green: 0.27, blue: 0.16)
        let bob = CGFloat(beat.lift * 1.5)

        func ellipse(_ rect: CGRect, _ color: Color) {
            context.fill(Path(ellipseIn: rect), with: .color(color))
        }
        func line(_ points: [CGPoint], color: Color, width: CGFloat = 2) {
            var path = Path()
            guard let first = points.first else { return }
            path.move(to: first)
            for point in points.dropFirst() { path.addLine(to: point) }
            context.stroke(path, with: .color(color),
                           style: StrokeStyle(lineWidth: width, lineCap: .round, lineJoin: .round))
        }

        // Warm halo, floor and a woven sitting cushion.
        ellipse(CGRect(x: 66, y: 12, width: 210, height: 210), gold.opacity(0.07))
        ellipse(CGRect(x: 82, y: 27, width: 178, height: 178), gold.opacity(0.07))
        ellipse(CGRect(x: 52, y: 221, width: 257, height: 13), ink.opacity(0.07))
        ellipse(CGRect(x: 72, y: 204, width: 165, height: 25), gold.opacity(0.30))
        ellipse(CGRect(x: 75, y: 200, width: 160, height: 23), gold.opacity(0.40))

        // Seated robe, crossed legs, sash and the resting left hand.
        var body = Path()
        body.move(to: CGPoint(x: 126, y: 115 - bob))
        body.addQuadCurve(to: CGPoint(x: 109, y: 186), control: CGPoint(x: 108, y: 139))
        body.addQuadCurve(to: CGPoint(x: 195, y: 189), control: CGPoint(x: 148, y: 213))
        body.addQuadCurve(to: CGPoint(x: 178, y: 115 - bob), control: CGPoint(x: 192, y: 139))
        body.closeSubpath()
        context.fill(body, with: .color(robe))
        ellipse(CGRect(x: 91, y: 178, width: 91, height: 33), lightRobe)
        ellipse(CGRect(x: 144, y: 178, width: 73, height: 33), robe)
        var sash = Path()
        sash.move(to: CGPoint(x: 171, y: 119))
        sash.addLine(to: CGPoint(x: 151, y: 126))
        sash.addLine(to: CGPoint(x: 116, y: 178))
        sash.addLine(to: CGPoint(x: 137, y: 187))
        sash.closeSubpath()
        context.fill(sash, with: .color(lightRobe))
        line([CGPoint(x: 150, y: 188), CGPoint(x: 186, y: 197)], color: wood.opacity(0.30))
        line([CGPoint(x: 121, y: 144), CGPoint(x: 119, y: 166), CGPoint(x: 137, y: 178)],
             color: lightRobe, width: 14)
        ellipse(CGRect(x: 128, y: 171, width: 22, height: 12), skin)

        // Round bald head, ears, six incense marks and gently closed eyes.
        ellipse(CGRect(x: 109, y: 72 - bob, width: 16, height: 23), skin)
        ellipse(CGRect(x: 181, y: 72 - bob, width: 16, height: 23), skin)
        ellipse(CGRect(x: 118, y: 36 - bob, width: 71, height: 84), skin)
        ellipse(CGRect(x: 132, y: 44 - bob, width: 26, height: 12), Color.white.opacity(0.16))
        for row in 0..<2 {
            for column in 0..<3 {
                ellipse(CGRect(x: 144 + CGFloat(column) * 8, y: 46 + CGFloat(row) * 8 - bob,
                               width: 2.6, height: 2.6), wood.opacity(0.40))
            }
        }
        for x in [CGFloat(132), CGFloat(163)] {
            var eye = Path()
            eye.move(to: CGPoint(x: x, y: 82 - bob))
            eye.addQuadCurve(to: CGPoint(x: x + 12, y: 82 - bob),
                             control: CGPoint(x: x + 6, y: 88 - bob))
            context.stroke(eye, with: .color(ink), style: StrokeStyle(lineWidth: 2, lineCap: .round))
        }
        ellipse(CGRect(x: 125, y: 89 - bob, width: 13, height: 7), robe.opacity(0.20))
        ellipse(CGRect(x: 171, y: 89 - bob, width: 13, height: 7), robe.opacity(0.20))
        var smile = Path()
        smile.move(to: CGPoint(x: 149, y: 101 - bob))
        smile.addQuadCurve(to: CGPoint(x: 159, y: 101 - bob), control: CGPoint(x: 154, y: 106 - bob))
        context.stroke(smile, with: .color(wood), style: StrokeStyle(lineWidth: 1.5, lineCap: .round))

        // Wooden fish on its own pad, with carved spiral and sound slit.
        ellipse(CGRect(x: 226, y: 209, width: 89, height: 17), robe.opacity(0.60))
        ellipse(CGRect(x: 230, y: 170, width: 78, height: 45), wood)
        ellipse(CGRect(x: 233, y: 168, width: 73, height: 34), gold)
        var grain = Path()
        grain.move(to: CGPoint(x: 253, y: 192))
        grain.addCurve(to: CGPoint(x: 291, y: 182), control1: CGPoint(x: 231, y: 171),
                       control2: CGPoint(x: 289, y: 163))
        grain.addCurve(to: CGPoint(x: 262, y: 185), control1: CGPoint(x: 291, y: 196),
                       control2: CGPoint(x: 252, y: 197))
        context.stroke(grain, with: .color(wood.opacity(0.65)),
                       style: StrokeStyle(lineWidth: 2, lineCap: .round))
        line([CGPoint(x: 283, y: 199), CGPoint(x: 306, y: 186)], color: ink.opacity(0.75), width: 4)

        // Right forearm and mallet rotate together around the elbow.
        var arm = context
        arm.translateBy(x: 182, y: 143)
        arm.rotate(by: .degrees(-38 * beat.lift))
        var sleeve = Path()
        sleeve.move(to: .zero)
        sleeve.addLine(to: CGPoint(x: 20, y: 13))
        arm.stroke(sleeve, with: .color(lightRobe), style: StrokeStyle(lineWidth: 18, lineCap: .round))
        arm.fill(Path(ellipseIn: CGRect(x: 15, y: 7, width: 18, height: 14)), with: .color(skin))
        var handle = Path()
        handle.move(to: CGPoint(x: 26, y: 12))
        handle.addLine(to: CGPoint(x: 77, y: 20))
        arm.stroke(handle, with: .color(wood), style: StrokeStyle(lineWidth: 5, lineCap: .round))
        arm.fill(Path(ellipseIn: CGRect(x: 68, y: 13, width: 19, height: 19)), with: .color(lightRobe))

        // A fading ring rises from the struck fish. Reduce Motion keeps a
        // still illustration and readable chant while the deadline continues.
        if isActive && !reduceMotion {
            let radius = 9 + CGFloat(beat.ripple) * 25
            let ring = Path(ellipseIn: CGRect(x: 274 - radius, y: 159 - radius,
                                             width: radius * 2, height: radius * 1.25))
            context.stroke(ring, with: .color(gold.opacity((1 - beat.ripple) * 0.55)), lineWidth: 1.5)
        }
    }
}
