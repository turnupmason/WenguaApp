import Foundation

// Each visible run is an exact substring of the stored source. Separators
// remain attached so joining runs recovers every original source character.
struct WenguaReadingBlock {
    let heading: String?
    let runs: [String]
}

enum WenguaReadingLayout {
    static func blocks(_ source: String, sectionID:String = "") -> [WenguaReadingBlock] {
        let markers: [(String, String)] = [
            ("天地格：", "天地格"), ("本宫条件：", "本宫条件"),
            ("另宫刑墓：", "另宫刑墓")]
        var result: [WenguaReadingBlock] = []
        var start = source.startIndex
        var heading: String? = sectionID=="90_review" ? "病宫与患者" : sectionID=="02_injury" ? "伤损部位" : sectionID=="09_conclusion" ? "主要结论" : nil
        var cursor = start
        while cursor < source.endIndex {
            let atLineStart = cursor == source.startIndex || source[source.index(before:cursor)] == "\n"
            let lineMarkers: [(String,String)] = atLineStart ? [
                ("天芮在","病位"),("天芮星力量","星门神"),("天盘","天干")] : []
            var scoped:[(String,String)]=[]
            if sectionID=="90_review" {
                scoped=[("医药两端分别看","医药依据"),("另参","病事与辅助"),("长辈乾坤辅助","长辈辅助"),("大吉神","大吉神依据"),("综上所述","全盘结论")]
            } else if sectionID=="02_injury" {
                scoped=[("伤门力量","星门神"),("宫中","星干信息"),
                        ("伤门自身取力","取象限制"),("伤门木克","条件限制")]
                if source[cursor...].hasPrefix("天盘"),
                   let stop=source[cursor...].firstIndex(of:"。"),
                   source[cursor..<stop].contains("加地盘") {scoped.insert(("天盘","天地格"),at:0)}
            } else if sectionID=="09_conclusion" {
                scoped=[("盘中","旁证与分宫核对"),("以上为传统","核实说明")]
            }
            if let marker = (markers + scoped + lineMarkers).first(where: { source[cursor...].hasPrefix($0.0) }) {
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

    static func paragraphs(_ block:WenguaReadingBlock) -> [String] {
        var result:[String]=[]
        var current=""
        for run in block.runs {
            current += run
            // Keep related short clauses together; separate on original line
            // boundaries or a complete, comfortably sized sentence.
            if run.hasSuffix("\n") || (current.count>=38 && (run.hasSuffix("。") || run.hasSuffix("；"))) {
                result.append(current);current=""
            }
        }
        if !current.isEmpty {result.append(current)}
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
