import Foundation

struct AtlasNativeInput: Decodable {
    let base_id:String
    let iso:String
    let timezone:String
}
struct AtlasNativeOutput: Encodable {
    let base_id:String
    let chart:WenguaNativeChart
}
@main
struct AtlasNativeExecutable {
    static func main() throws {
        guard CommandLine.arguments.count==2 else {fatalError("Need fixture path")}
        let bytes=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
        let inputs=try JSONDecoder().decode([AtlasNativeInput].self,from:bytes)
        let fmt=ISO8601DateFormatter()
        fmt.formatOptions=[.withInternetDateTime]
        let encoder=JSONEncoder()
        encoder.outputFormatting=[.sortedKeys]
        for item in inputs {
            guard let date=fmt.date(from:item.iso) else {fatalError("Bad real ISO time "+item.iso)}
            let chart=try WenguaNativeCore.compute(at:date,timezone:item.timezone)
            let data=try encoder.encode(AtlasNativeOutput(base_id:item.base_id,chart:chart))
            print(String(decoding:data,as:UTF8.self))
        }
    }
}
