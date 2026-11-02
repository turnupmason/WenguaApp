import Foundation

enum WenguaCastClockMode: String, CaseIterable {
    case currentInquiry = "current_inquiry"
    case plannedEvent = "planned_event"
    var title: String { self == .currentInquiry ? "当前时辰问事" : "事项时辰择时" }
}

struct WenguaTimeCandidate: Identifiable {
    let id = UUID()
    var date: Date
}

enum WenguaCastTimeError: Error, LocalizedError {
    case invalidZone, invalidCandidates, pastCandidate, duplicateCandidate
    var errorDescription: String? {
        switch self {
        case .invalidZone: return "请选择事项发生地的有效时区。"
        case .invalidCandidates: return "请提供1至6个1850至2150年范围内的候选时辰。"
        case .pastCandidate: return "择时用于尚未发生的事项，请选择确认时刻之后的候选时间。"
        case .duplicateCandidate: return "候选时间重复，请保留不同的事项时间。"
        }
    }
}

enum WenguaCastTimePlan {
    static let plannedTopicID = "timing.planned"
    static let eventKinds = ["旅游出发", "约会", "结婚", "手术", "其它计划事项"]

    static func supports(_ topic: String) -> Bool {
        ["health.severity", "health.discomfort", plannedTopicID].contains(topic)
    }

    static func resolve(mode: WenguaCastClockMode, candidates: [Date],
                        confirmedAt: Date, timezone: String) throws -> [Date] {
        guard let zone = TimeZone(identifier: timezone) else { throw WenguaCastTimeError.invalidZone }
        // The question's actual confirmation instant is captured once, after
        // the full calm interval; opening a picker must never freeze "now".
        if mode == .currentInquiry { return [confirmedAt] }
        guard (1...6).contains(candidates.count) else { throw WenguaCastTimeError.invalidCandidates }
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = zone
        var seen = Set<Date>()
        return try candidates.map { candidate in
            guard candidate.timeIntervalSince1970.isFinite,
                  let minute = calendar.dateInterval(of: .minute, for: candidate)?.start,
                  (1850...2150).contains(calendar.component(.year, from: minute)) else {
                throw WenguaCastTimeError.invalidCandidates
            }
            guard minute > confirmedAt else { throw WenguaCastTimeError.pastCandidate }
            guard seen.insert(minute).inserted else { throw WenguaCastTimeError.duplicateCandidate }
            return minute
        }
    }

    static func iso(_ date: Date, timezone: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.timeZone = TimeZone(identifier: timezone)
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.string(from: date)
    }

    static func display(_ iso: String, timezone: String?) -> String {
        let parser = ISO8601DateFormatter()
        guard let date = parser.date(from: iso) else { return iso }
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "zh_CN")
        formatter.timeZone = timezone.flatMap { TimeZone(identifier: $0) } ?? TimeZone.current
        formatter.dateFormat = "yyyy年M月d日 HH:mm ZZZZZ"
        return formatter.string(from: date)
    }

    static func chartOnlyReading(chart: WenguaNativeChart, eventKind: String) -> WenguaNativeCustomerReading {
        let pillars = [chart.pillars.year, chart.pillars.month, chart.pillars.day, chart.pillars.hour]
        return WenguaNativeCustomerReading(
            version: "planned_event_chart_only_v1_20261102", topicID: plannedTopicID,
            relationship: "本人", iso: chart.iso,
            evidenceStatus: "actual_chart_only_domain_timing_grade_pending",
            sections: [
                .init(id: "time_basis", title: "所选事项与时间",
                      text: eventKind + "；按本盘注明的实际时刻、时区计算历法与九宫。"),
                .init(id: "chart_facts", title: "历法与盘面",
                      text: "四柱：" + pillars.joined(separator: " / ") + "。节气：" + chart.solarTerm + "。完整九宫可逐宫查看。"),
                .init(id: "timing_pending", title: "择时评级",
                      text: "本事项的主辅用神、证据优先级和吉凶等级仍在开发中。当前提供候选时刻的真实排盘，不以疾病分数代替本事项的择时判断。")])
    }

    static func annotate(_ reading: WenguaNativeCustomerReading, mode: WenguaCastClockMode,
                         timezone: String, confirmedAt: Date, groupID: String, index: Int,
                         eventKind: String, healthReference: WenguaNativeCustomerReading? = nil) -> WenguaNativeCustomerReading {
        var result = reading
        result.castMode = mode.rawValue
        result.castTimeZone = timezone
        result.confirmedISO = iso(confirmedAt, timezone: timezone)
        result.comparisonGroupID = groupID
        result.candidateIndex = index
        result.plannedEventKind = mode == .plannedEvent ? eventKind : nil
        result.timingGrade = nil
        result.timingGradeScope = nil
        result.timingReferenceSections = nil
        result.timingReferenceVersion = nil
        let reference = healthReference ?? reading
        if mode == .plannedEvent && ["health.severity", "health.discomfort"].contains(reading.topicID),
           reference.iso == reading.iso, let grade = reference.resolvedHealthGrade {
            result.timingGrade = grade
            result.timingGradeScope = "health.severity.V9/V11"
            if reading.topicID == "health.discomfort" {
                result.timingReferenceSections = reference.sections
                result.timingReferenceVersion = reference.version
            }
        }
        return result
    }
}

// One encoded group is one UserDefaults value. Compute every chart/reading
// before calling this method; failure never leaves half a comparison group.
enum WenguaCaseBatchStore {
    static func save(_ records: [LocalNativeCase], defaults: UserDefaults = .standard) throws {
        guard !records.isEmpty else { throw WenguaCastTimeError.invalidCandidates }
        let data = try JSONEncoder().encode(records)
        let key = "wengua:nativecase:" + UUID().uuidString
        defaults.set(data, forKey: key)
        guard defaults.data(forKey: key) == data else {
            defaults.removeObject(forKey: key)
            throw WenguaCastError.invalidChart
        }
    }

    static func decode(_ data: Data) -> [LocalNativeCase] {
        if let batch = try? JSONDecoder().decode([LocalNativeCase].self, from: data) { return batch }
        return (try? JSONDecoder().decode(LocalNativeCase.self, from: data)).map { [$0] } ?? []
    }
}
