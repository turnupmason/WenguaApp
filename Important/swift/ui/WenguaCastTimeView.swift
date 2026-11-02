import SwiftUI

struct WenguaCastTimePicker: View {
    @Binding var mode: WenguaCastClockMode
    @Binding var candidates: [WenguaTimeCandidate]
    @Binding var timezone: String
    @State private var choosingTime = false
    @State private var draftDate = Date()

    private var calendar: Calendar {
        var value = Calendar(identifier: .gregorian)
        value.timeZone = TimeZone(identifier: timezone) ?? .current
        return value
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("起局时间").font(.headline)
            Picker("起局方式", selection: $mode) {
                ForEach(WenguaCastClockMode.allCases, id: \.self) { item in
                    Text(item.title).tag(item)
                }
            }.pickerStyle(.segmented)
            if mode == .currentInquiry {
                Text("不测不占，不动不占。普通问事按静心结束后确认的当下时辰起局。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
            } else {
                Text("已有预定出发或办事时间，可按那个时刻起局。选吉日为领域内的独立功能，后续接入。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Picker("事项发生地时区", selection: $timezone) {
                    ForEach(Array(Set(TimeZone.knownTimeZoneIdentifiers + [timezone])).sorted(), id: \.self) { zone in
                        Text(zone).tag(zone)
                    }
                }.pickerStyle(.menu)
                Button {
                    draftDate=candidates.first?.date ?? Date()
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
        .sheet(isPresented:$choosingTime) {
            NavigationStack {
                VStack(spacing:18) {
                    Text("选择事项发生的年月日与时间").font(.headline)
                    DatePicker("手动选择年月日时分", selection: $draftDate,
                                   displayedComponents: [.date, .hourAndMinute])
                            .datePickerStyle(.wheel)
                            .environment(\.locale, Locale(identifier: "zh_CN"))
                            .environment(\.calendar, calendar)
                            .environment(\.timeZone, calendar.timeZone)
                            .labelsHidden()
                    Text("发生地时区："+timezone).font(.caption).foregroundStyle(QStyle.secondary)
                    Button("确认选择") {
                        if !candidates.isEmpty {
                            candidates[0].date=draftDate
                            candidates[0].isConfirmed=true
                        }
                        choosingTime=false
                    }.buttonStyle(.borderedProminent)
                }
                .padding(20)
                .navigationTitle("选择时辰")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {ToolbarItem(placement:.cancellationAction) {Button("取消") {choosingTime=false}}}
            }.presentationDetents([.medium,.large])
        }
    }
}

struct WenguaTimeSourceBanner: View {
    let reading: WenguaNativeCustomerReading
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(reading.castMode == "planned_event" ? "预定时辰 · 问事起局" : "当前时辰 · 问事起局")
                .font(.subheadline.weight(.semibold))
            Text(WenguaCastTimePlan.display(reading.iso, timezone: reading.castTimeZone))
                .font(.caption.monospacedDigit())
            if let zone = reading.castTimeZone { Text(zone).font(.caption2) }
        }
        .foregroundStyle(QStyle.secondary)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 16).padding(.vertical, 8)
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
