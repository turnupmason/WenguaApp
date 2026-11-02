import SwiftUI

struct WenguaCastTimePicker: View {
    @Binding var mode: WenguaCastClockMode
    @Binding var candidates: [WenguaTimeCandidate]
    @Binding var timezone: String

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
                Text("时区：" + TimeZone.current.identifier)
                    .font(.caption).foregroundStyle(QStyle.secondary)
            } else {
                Text("已有计划或几个备选时间时，按事项实际发生的时刻排盘。多个备选属于同一事项，一次静心后并列查看。")
                    .font(.subheadline).foregroundStyle(QStyle.secondary)
                Picker("事项发生地时区", selection: $timezone) {
                    ForEach(Array(Set(TimeZone.knownTimeZoneIdentifiers + [timezone])).sorted(), id: \.self) { zone in
                        Text(zone).tag(zone)
                    }
                }.pickerStyle(.menu)
                ForEach($candidates) { $candidate in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("候选时辰").font(.subheadline.weight(.medium))
                            Spacer()
                            if candidates.count > 1 {
                                Button("移除", role: .destructive) {
                                    candidates.removeAll { $0.id == candidate.id }
                                }.font(.caption)
                            }
                        }
                        DatePicker("手动选择年月日时分", selection: $candidate.date,
                                   displayedComponents: [.date, .hourAndMinute])
                            .datePickerStyle(.wheel)
                            .environment(\.locale, Locale(identifier: "zh_CN"))
                            .environment(\.calendar, calendar)
                            .environment(\.timeZone, calendar.timeZone)
                            .labelsHidden()
                            .frame(height: 175)
                            .clipped()
                        Text(WenguaCastTimePlan.display(
                            WenguaCastTimePlan.iso(candidate.date, timezone: timezone), timezone: timezone))
                            .font(.caption.monospacedDigit()).foregroundStyle(QStyle.secondary)
                    }
                    .padding(10)
                    .background(QStyle.backing, in: RoundedRectangle(cornerRadius: 12))
                }
                if candidates.count < 6 {
                    Button {
                        let next = (candidates.last?.date ?? Date()).addingTimeInterval(2 * 60 * 60)
                        candidates.append(WenguaTimeCandidate(date: next))
                    } label: { Label("再加一个候选时间", systemImage: "plus.circle") }
                }
                Text("请选未来时间，最多6个。23点子初及未核定的节气边界仍会阻断，不擅自改成其它时辰。")
                    .font(.caption).foregroundStyle(QStyle.secondary)
            }
        }
        .padding(14)
        .background(QStyle.surface, in: RoundedRectangle(cornerRadius: 14))
    }
}

struct WenguaTimeSourceBanner: View {
    let reading: WenguaNativeCustomerReading
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(reading.castMode == "planned_event" ? "事项时辰 · 候选排盘" : "当前时辰 · 问事起局")
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
