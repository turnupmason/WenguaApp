import Foundation
@main struct Native200SourceCheck {
    static func main() throws {
        guard CommandLine.arguments.count==2 else {
            throw WenguaHealthTemplateError.unavailableResource
        }
        let c=try WenguaNativeEnergyBundle.fromData(
            Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
        let normal=try WenguaNativeEnergyBundle.cell(
            "normal",row:"极小",column:"小",catalog:c)
        let door=try WenguaNativeEnergyBundle.cell(
            "door",row:"旺",column:"宫迫",catalog:c)
        let void=try WenguaNativeEnergyBundle.cell(
            "true_void_attacker",row:"小",column:"极大",catalog:c)
        guard c.tables.count==8,normal=="有效克制",door=="中等",
              void=="完全失控" else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        print("NATIVE_200_OFFLINE_BUNDLE_OK source exact")
    }
}
