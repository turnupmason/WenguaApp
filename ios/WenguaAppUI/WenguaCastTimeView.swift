import SwiftUI

struct WenguaCastTimePicker: View {
    let mode: WenguaCastClockMode
    @Binding var candidates: [WenguaTimeCandidate]
    @Binding var timezone: String
    @State private var choosingTime = false
    @State private var draftClock = WenguaScheduledClock(date:Date(),timezone:TimeZone.current.identifier)
    @State private var occurrence = 0
    @State private var timeError = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("起局时间").font(.headline)
            if mode == .currentInquiry {
                Text("当前时辰问事").font(.headline)
                Text("直接使用确认起局时的当前时辰。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
            } else {
                Text("预定时辰起局").font(.headline)
                Text("请选择事项实际发生／约定的未来时刻。吉日专用评级仍在开发中，当前提供真实排盘。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Picker("事项发生地时区", selection: $timezone) {
                    ForEach(Array(Set(TimeZone.knownTimeZoneIdentifiers + [timezone])).sorted(), id: \.self) { zone in
                        Text(zone).tag(zone)
                    }
                }.pickerStyle(.menu)
                Button {
                    draftClock=WenguaScheduledClock(date:candidates.first?.date ?? Date(),timezone:timezone)
                    occurrence=0
                    timeError=""
                    choosingTime=true
                } label: {
                    HStack {
                        Label("选择时辰",systemImage:"calendar.badge.clock")
                        Spacer()
                        if candidates.first?.isConfirmed == true {Image(systemName:"checkmark.circle.fill")}
                        Image(systemName:"chevron.right").font(.caption)
                    }.padding(.vertical,10)
                }.buttonStyle(.plain)
                .accessibilityValue(candidates.first?.isConfirmed == true ? "已选择" : "尚未选择")
            }
        }
        .padding(14)
        .background(QStyle.surface, in: RoundedRectangle(cornerRadius: 14))
        .onChange(of:timezone) { _, _ in
            for index in candidates.indices {candidates[index].isConfirmed=false}
        }
        .navigationDestination(isPresented:$choosingTime) {
            VStack(spacing:20) {
                Text("选择事项发生的年月日与时间").font(.headline)
                WenguaCivilClockWheel(clock:$draftClock,timezone:timezone)
                if let choices=try? draftClock.instants(timezone:timezone),choices.count>1 {
                    Picker("该时间出现两次，请选择",selection:$occurrence) {
                        Text("较早一次").tag(0)
                        Text("较晚一次").tag(1)
                    }.pickerStyle(.segmented)
                }
                Text("发生地时区："+timezone).font(.caption).foregroundStyle(QStyle.secondary)
                if !timeError.isEmpty {Text(timeError).font(.footnote).foregroundStyle(QStyle.red)}
                Button("确认选择") {
                    do {
                        let dates=try draftClock.instants(timezone:timezone)
                        guard !dates.isEmpty,!candidates.isEmpty else {throw WenguaCastTimeError.invalidCivilTime}
                        let chosen=dates[min(occurrence,dates.count-1)]
                        _ = try WenguaCastTimePlan.resolve(mode:.plannedEvent,candidates:[chosen],
                            confirmedAt:Date(),timezone:timezone)
                        candidates[0].date=chosen
                        candidates[0].isConfirmed=true
                        choosingTime=false
                    } catch {timeError=error.localizedDescription}
                }.buttonStyle(.borderedProminent)
                Spacer(minLength:0)
            }
            .padding(20)
            .navigationTitle("选择时辰")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

}

struct WenguaTimeSourceBanner: View {
    let reading: WenguaNativeCustomerReading
    var body: some View {
        Text(QuestionCatalog.directionTitle(reading.topicID))
            .font(.system(size:17,weight:.semibold,design:.serif))
            .frame(maxWidth:.infinity,alignment:.center)
            .padding(.horizontal,16).padding(.vertical,10)
    }
}

struct WenguaCandidateComparison: View {
    let cases: [LocalNativeCase]
    let selectedISO: String
    let select: (LocalNativeCase) -> Void
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("同一事项 · 候选时辰对照").font(.headline)
            ForEach(cases.indices, id: \.self) { index in
                let item = cases[index]
                Button { select(item) } label: {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: selectedISO == item.chart.iso ? "checkmark.circle.fill" : "circle")
                        VStack(alignment: .leading, spacing: 4) {
                            Text("候选\(index + 1) · " + WenguaCastTimePlan.display(
                                item.chart.iso, timezone: item.reading?.castTimeZone))
                                .font(.subheadline)
                            Text(item.reading?.timingHeadline ?? "该时辰评级尚未核定")
                                .font(.caption.weight(.medium))
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(12).frame(maxWidth: .infinity, alignment: .leading)
                    .background(QStyle.surface, in: RoundedRectangle(cornerRadius: 12))
                }.buttonStyle(.plain)
            }
            Text("等级仅适用于所选事项的已接入规则，不代表整天所有事情的吉凶。")
                .font(.caption).foregroundStyle(QStyle.secondary)
        }.padding(16)
    }
}
