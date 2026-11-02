import Foundation

// Each visible run is an exact substring of the stored source. Separators
// remain attached so joining runs recovers every original source character.
struct WenguaReadingBlock {
    let heading: String?
    let runs: [String]
}

enum WenguaReadingLayout {
    static func blocks(_ source: String) -> [WenguaReadingBlock] {
        let markers: [(String, String)] = [
            ("天地格：", "天地格"), ("本宫条件：", "本宫条件"),
            ("另宫刑墓：", "另宫刑墓")]
        var result: [WenguaReadingBlock] = []
        var start = source.startIndex
        var heading: String? = nil
        var cursor = start
        while cursor < source.endIndex {
            let atLineStart = cursor == source.startIndex || source[source.index(before:cursor)] == "\n"
            let lineMarkers: [(String,String)] = atLineStart ? [
                ("天芮在","病位"),("天芮星力量","星门神"),("天盘","天干")] : []
            if let marker = (markers + lineMarkers).first(where: { source[cursor...].hasPrefix($0.0) }) {
                if cursor > start {
                    result.append(.init(heading: heading, runs: runs(String(source[start..<cursor]))))
                }
                start = cursor
                heading = marker.1
                cursor = source.index(cursor, offsetBy: marker.0.count)
            } else { cursor = source.index(after: cursor) }
        }
        if start < source.endIndex {
            result.append(.init(heading: heading, runs: runs(String(source[start...]))))
        }
        return result
    }

    private static func runs(_ source: String) -> [String] {
        var result: [String] = []
        var start = source.startIndex
        for index in source.indices {
            if source[index] == "；" || source[index] == "。" || source[index] == "\n" {
                let end = source.index(after: index)
                result.append(String(source[start..<end]))
                start = end
            }
        }
        if start < source.endIndex { result.append(String(source[start...])) }
        return result
    }
}
