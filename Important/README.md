# Important · WenguaApp 核心文件导航（2026-10-26）

这是用户要求的统一核心文件夹，仅分 `python/` 与 `swift/` 两个语言子目录；各目录下按 **engine/reading/scoring/scripts/data/templates/tests/ci（Python）** 和 **engine/ui/project/data/templates/tests/ci（Swift）** 分组。

- [Python：起盘、专题取用、宫位能量、81格与200格、模板、盲测](python/README.md)
- [Swift：iOS 真正离线引擎、生产断词、SwiftUI、构建、同源数据与对照](swift/README.md)
- [完整、可自动校验的一对一源文件镜像清单](MANIFEST.json)

**极其重要：这些文件是对当前仓库现役文件的字节级镜像，不是第二套各自修改的逻辑。** 原 `src/wengua/`、`ios/WenguaAppUI/`、`data/`、`scripts/`、`tests/` 及 GitHub workflow 仍然是真实运行/编译路径；绝不通过移动源文件破坏导入或 Xcode 打包。每次修改源文件必须在同一次提交同步更新这里的镜像，CI 内 `tests/test_important_mirror_integrity_20261026.py` 会逐个字节检查。必要时依照 MANIFEST 的 `canonical` 字段找到原位。

范围：当前健康·病情轻重 V-next Python/Swift 共同实现，保留健康旧 V3.9.1 关联依赖。**其它未移植专题、全部古籍库、失败试验、历史行为版本不迁入本目录，也不被删除或重置。** 完整源仓仍是最终审计事实。
