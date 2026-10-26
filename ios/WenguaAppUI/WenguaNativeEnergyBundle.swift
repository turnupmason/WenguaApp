import Foundation

// Native read-only copy of ALL original user 8×25 grids. Never infer
// calendar stages or medical prognoses from the resource alone.
struct WenguaNativeEnergyGrid: Codable {
    let columns:[String]
    let rows:[String:[String]]
}
struct WenguaNativeEnergyCatalog: Codable {
    let schema:String
    let version:String
    let source:[String]
    let note:String
    let tables:[String:WenguaNativeEnergyGrid]
}
enum WenguaNativeEnergyBundle {
    static let schema="wengua_ios_native_energy_200_vnext_20261026"
    static let names:Set<String>=["star","door","stem","normal",
        "fake_void_attacker","fake_void_target","true_void_attacker","true_void_target"]
    static let levels=["极小","小","中等","大","极大"]
    static func fromBundle(_ bundle:Bundle = .main) throws -> WenguaNativeEnergyCatalog {
        guard let url=bundle.url(forResource:"health_energy_200",withExtension:"json") else {
            throw WenguaHealthTemplateError.unavailableResource
        }
        return try fromData(Data(contentsOf:url))
    }
    static func fromData(_ data:Data) throws -> WenguaNativeEnergyCatalog {
        let result=try JSONDecoder().decode(WenguaNativeEnergyCatalog.self,from:data)
        guard result.schema==schema,Set(result.tables.keys)==names else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        for (name,grid) in result.tables {
            guard grid.columns.count==5,Set(grid.columns).count==5,
                  grid.rows.count==5,
                  grid.rows.values.allSatisfy({$0.count==5 &&
                          $0.allSatisfy({!$0.isEmpty})}) else {
                throw WenguaHealthTemplateError.invalidCatalog
            }
            if !["star","door","stem"].contains(name) {
                guard grid.columns==levels,Set(grid.rows.keys)==Set(levels) else {
                    throw WenguaHealthTemplateError.invalidCatalog
                }
            }
        }
        return result
    }
    static func cell(_ name:String,row:String,column:String,
                     catalog:WenguaNativeEnergyCatalog) throws -> String {
        guard let grid=catalog.tables[name],
              let index=grid.columns.firstIndex(of:column),
              let values=grid.rows[row],index<values.count else {
            throw WenguaHealthTemplateError.invalidCatalog
        }
        return values[index]
    }
}
