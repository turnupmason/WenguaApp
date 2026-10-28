import SwiftUI
import Foundation

// Private-by-default offline records. No network requests, no historical
// training-case outcomes, and no uploading the user's question.
struct WenguaStoredCase: Identifiable {
    let id: String
    let record: LocalNativeCase
}

enum WenguaRecordStore {
    static let recordPrefix="wengua:nativecase:"
    static let issuePrefix="wengua:completed:"

    static func load() -> [WenguaStoredCase] {
        UserDefaults.standard.dictionaryRepresentation().compactMap { key, value in
            guard key.hasPrefix(recordPrefix),
                  let data=value as? Data,
                  let record=try? JSONDecoder().decode(LocalNativeCase.self,from:data)
            else {return nil}
            return WenguaStoredCase(id:key,record:record)
        }
        .sorted { $0.record.completedAt > $1.record.completedAt }
    }

    static func deleteRecord(_ id:String) {
        guard id.hasPrefix(recordPrefix) else {return}
        UserDefaults.standard.removeObject(forKey:id)
        // An individual record deletion does NOT silently reset the
        // user-requested once-per-specific-issue / 15-day commitment.
    }

    static func eraseAllLocalIssueData() {
        // Deliberate user privacy control: clears both original snapshots
        // and the local-only lock hashes. Caller must confirm in UI.
        let keys=UserDefaults.standard.dictionaryRepresentation().keys
        for key in keys where key.hasPrefix(recordPrefix) ||
                               key.hasPrefix(issuePrefix) {
            UserDefaults.standard.removeObject(forKey:key)
        }
    }
}

// Keep List's result-builder small enough for the real Xcode type-checker.
private struct WenguaStoredCaseRow: View {
    let record: LocalNativeCase
    var body: some View {
        VStack(alignment:.leading,spacing:5) {
            Text(record.topicID=="health.severity" ? "健康 · 病情轻重" : record.topicID)
                .font(.headline)
            Text(record.relation + " · " +
                 record.completedAt.formatted(date:.abbreviated,time:.shortened))
                .font(.caption).foregroundStyle(.secondary)
            Text("真实本地盘 · " + [
                record.chart.pillars.year,record.chart.pillars.month,
                record.chart.pillars.day,record.chart.pillars.hour
            ].joined(separator:" "))
                .font(.caption2).foregroundStyle(.secondary)
        }
        .padding(.vertical,3)
    }
}

struct WenguaLocalHistoryView: View {
    @State private var entries:[WenguaStoredCase]=[]
    @State private var confirmEraseAll=false

    var body: some View {
        List {
            Section {
                if entries.isEmpty {
                    ContentUnavailableView("暂无本地记录",systemImage:"books.vertical",
                        description:Text("只有成功生成并保存的真实九宫才会出现在这里。"))
                } else {
                    ForEach(entries) { item in
                        NavigationLink {
                            TraditionalReadingPreview(
                                nativeChart:item.record.chart,sampleIndex:-1,
                                nativeReading:item.record.reading)
                        } label: {
                            WenguaStoredCaseRow(record:item.record)
                        }
                    }
                    .onDelete { indices in
                        let ids=indices.map{entries[$0].id}
                        ids.forEach(WenguaRecordStore.deleteRecord)
                        refresh()
                    }
                }
            } header: {
                Text("已完成的起局")
            } footer: {
                Text("左滑可删除一条记录；删除记录不会自动解除该事项的15天限制。")
            }
            Section("隐私与本机资料") {
                NavigationLink("隐私说明与资料用途") { WenguaPrivacyScreen() }
                Button("清空全部问事记录与本机限制",role:.destructive) {
                    confirmEraseAll=true
                }
            }
        }
        .navigationTitle("本地记录")
        .onAppear(perform:refresh)
        .alert("确认删除所有本地问事数据？",isPresented:$confirmEraseAll) {
            Button("全部删除",role:.destructive) {
                WenguaRecordStore.eraseAllLocalIssueData()
                refresh()
            }
            Button("取消",role:.cancel) {}
        } message: {
            Text("将删除真实九宫、已保存的断词快照和本地15天事项摘要；无法恢复。本功能不代表跨设备解除一事一占原则。")
        }
    }

    private func refresh() {entries=WenguaRecordStore.load()}
}

struct WenguaPrivacyScreen: View {
    var body: some View {
        List {
            Section("数据如何使用") {
                Text("问卦依据确认时刻计算传统时家奇门九宫及对应解读。记录仅保存在当前设备；无需创建账号。")
                Text("成功起局时仅在本机保存问事领域、关系、可选出生公历年份、时间、真实九宫和当次话术快照，以及该事项的本地SHA256摘要；不将具体问题原文写入保存记录。")
            }
            Section("本地记录与删除") {
                Text("历史记录可在「本地记录」查看及逐条删除。15天本机事项限制默认保留；选择「清空全部问事记录与本机限制」可同时清除此设备存储的相应内容。删除不可恢复。")
                Text("不跨设备同步；卸载应用、换设备或清空数据可能使本机限制失去历史上下文。")
            }
            Section("健康说明") {
                Text("所有健康相关内容均为古籍文化和术数方法的研究展示，并不提供任何医学诊断、疾病严重程度、康复、治疗效果或预后的科学预测。")
            }
        }
        .navigationTitle("隐私说明")
    }
}
