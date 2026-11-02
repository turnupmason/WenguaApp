import Foundation

enum WenguaCastClockMode: String, CaseIterable {
    case currentInquiry = "current_inquiry"
    case plannedEvent = "planned_event"
    var title: String { self == .currentInquiry ? "当前时辰问事" : "预定时辰起局" }
}

struct WenguaTimeCandidate: Identifiable {
    let id = UUID()
    var date: Date
    var isConfirmed = false
}

enum WenguaCastTimeError: Error, LocalizedError {
    case invalidZone, invalidCandidates, pastCandidate, duplicateCandidate, invalidCivilTime, invalidClockMode
    var errorDescription: String? {
        switch self {
        case .invalidCivilTime: return "所选年月日时分在该时区不存在，请重新选择。"
        case .invalidClockMode: return "普通问事使用当前时辰；选吉日仅使用未来预定时辰。"
        case .invalidZone: return "请选择事项发生地的有效时区。"
        case .invalidCandidates: return "请提供1至6个1850至2150年范围内的候选时辰。"
        case .pastCandidate: return "择时用于尚未发生的事项，请选择确认时刻之后的候选时间。"
        case .duplicateCandidate: return "候选时间重复，请保留不同的事项时间。"
        }
    }
}

struct WenguaScheduledClock {
    var year:Int
    var month:Int
    var day:Int
    var hour:Int
    var minute:Int
    init(date:Date,timezone:String) {
        var calendar=Calendar(identifier:.gregorian)
        calendar.timeZone=TimeZone(identifier:timezone) ?? .current
        let parts=calendar.dateComponents([.year,.month,.day,.hour,.minute],from:date)
        year=parts.year!;month=parts.month!;day=parts.day!;hour=parts.hour!;minute=parts.minute!
    }
    func daysInMonth(timezone:String) -> Int {
        var calendar=Calendar(identifier:.gregorian)
        calendar.timeZone=TimeZone(identifier:timezone) ?? .current
        guard let first=calendar.date(from:DateComponents(year:year,month:month,day:1)) else {return 28}
        return calendar.range(of:.day,in:.month,for:first)?.count ?? 28
    }
    func instants(timezone:String) throws -> [Date] {
        guard let zone=TimeZone(identifier:timezone) else {throw WenguaCastTimeError.invalidZone}
        var calendar=Calendar(identifier:.gregorian);calendar.timeZone=zone
        let expected=DateComponents(year:year,month:month,day:day,hour:hour,minute:minute,second:0)
        guard let seed=calendar.date(from:expected) else {throw WenguaCastTimeError.invalidCivilTime}
        func matches(_ date:Date) -> Bool {
            let c=calendar.dateComponents([.year,.month,.day,.hour,.minute],from:date)
            return c.year==year && c.month==month && c.day==day && c.hour==hour && c.minute==minute
        }
        guard matches(seed) else {throw WenguaCastTimeError.invalidCivilTime}
        let before=calendar.startOfDay(for:seed).addingTimeInterval(-1)
        let clock=DateComponents(hour:hour,minute:minute,second:0)
        let choices:[Calendar.RepeatedTimePolicy]=[.first,.last]
        let found=choices.compactMap { policy in
            calendar.nextDate(after:before,matching:clock,matchingPolicy:.strict,repeatedTimePolicy:policy)
        }.filter(matches)
        return Array(Set(found+[seed])).sorted()
    }
}

enum WenguaCastTimePlan {
    static let plannedTopicID = "timing.planned"
    static let eventKinds = ["旅游出发", "约会", "结婚", "手术", "其它计划事项"]

    static func supports(_ topic: String) -> Bool {
        WenguaDomainContract.lookup(topic)?.canCast == true
    }

    static func resolveForTopic(_ topic:String,mode:WenguaCastClockMode,candidates:[Date],
                                confirmedAt:Date,timezone:String) throws -> [Date] {
        guard let contract=WenguaDomainContract.lookup(topic),contract.canCast,
              (mode == .plannedEvent ? contract.acceptsPlannedTime : contract.acceptsCurrentTime) else {
            throw WenguaCastTimeError.invalidClockMode
        }
        return try resolve(mode:mode,candidates:candidates,confirmedAt:confirmedAt,timezone:timezone)
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
        guard let zone=timezone.flatMap({ TimeZone(identifier:$0) }) else {
            return iso.replacingOccurrences(of:"T",with:" ")
        }
        formatter.timeZone = zone
        formatter.dateFormat = "yyyy年M月d日 HH:mm"
        return formatter.string(from: date)
    }

    static func chartOnlyReading(chart: WenguaNativeChart, eventKind: String,
                                 topicID: String = plannedTopicID,
                                 relationship: String = "本人") -> WenguaNativeCustomerReading {
        let pillars = [chart.pillars.year, chart.pillars.month, chart.pillars.day, chart.pillars.hour]
        return WenguaNativeCustomerReading(
            version: "planned_event_chart_only_v1_20261102", topicID: topicID,
            relationship: relationship, iso: chart.iso,
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
        if mode == .plannedEvent, let contract=WenguaDomainContract.lookup(reading.topicID),
           let grade=contract.approvedGrade(primary:reading,reference:reference) {
            result.timingGrade = grade
            result.timingGradeScope = contract.gradeScope
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
