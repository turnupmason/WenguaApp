# BigFish PyCharm 首次 Node 缺失：自动官方 LTS 完整性验证 · 2026-10-29

## 用户真实报错
用户的 PyCharm venv Python 已进入先前自动安装代码，第一次 `base.check_install()` 报需要本地安装之后，原脚本 `ensure_install()` 在检查程序时抛
`RuntimeError: 缺少 node：请先在 Mac 安装 Git 与 Node.js（npm 随 Node.js 安装），并重启 PyCharm。`
**当时尚未执行518400循环。**

## 修复与交付源码
本轮更新会话交付 `Wengua_BigFish_518400.py`，SHA256 `0ad19eeb969564f134cda29fda61591f2e4c7ca362d4fa088122f88fadb4dd0f`，48713 bytes、910行；备用 `Wengua_BigFish_518400_修复缺少Node_20261029.zip`，SHA256 `79c87b6c2da06bfe04439514807ea104bb416b112f94de873012e8ed52464c5c`，ZIP CRC PASS。该Python需与现有本地 `local_batch.py` 同目录；本仓保存本轮来源/哈希交接，不假称本轮已上传上述整个完整 48KB 源文件进 GitHub。

**Python only、不需要.command：** 保留 `AUTO_INSTALL=True`，新增 `AUTO_INSTALL_NODE=True`。首次核对 `base.check_install` 失败后扩展 PyCharm PATH，依次检查 `toolchain/node_runtime/bin`、Homebrew AppleSilicon/Intel、nvm、volta、fnm、mise、asdf 常用路径，找到可运行 Node >=20 + npm 即复用。若找不到则仅在 macOS使用Python stdlib urllib HTTPS读取 `https://nodejs.org/dist/index.json` 的最新LTS且包含当前 darwin arm64/x64 tar包，读取同目录 `SHASUMS256.txt`，下载官方 `node-v...-darwin-....tar.gz` 至临时目录并逐字节 SHA256验真，安全地只解压 `bin/node` 与 `lib/node_modules/npm/` 正规文件，拒绝目录穿越和下载的symlink，生成本地npm启动包装，校验 `node --version` 和 `npm --version`，然后原子重命名至 `toolchain/node_runtime`，不要求sudo/系统级安装、不覆盖已存在的runtime目录及任何结果文件。后续再下载已审固定BigFish SHA `6112b393...`、Wengua SHA `0eae7d2b...`、TS 5.8.3并按SHA校验冻结四资源；之后离线。Node官方网络不可用时提示 `brew install node` 或nodejs.org官方安装器。

## 本轮实测，真实界限
- `python -m py_compile Wengua_BigFish_518400.py` PASS。
- `python -m unittest ...test_bigfish_518400_nodefix.py -v` **13/13 PASS**（旧9项：518400逻辑组合、五虎五鼠、原上游元信息、SQLite/CSV/XLSX、无假盘旧源注入、版本等 + 新4项：mock官方Node LTS索引/官方SHA/tar包/安装路径与可执行校验、错误SHA拒绝、旧目录保留、关闭自动下载时友好报错）。安装网络测试使用**隔离人工构造的tar fixture**，不是已经真的连接nodejs.org、不是用户Mac实跑通过。
- ZIP内部文件CRC真实 PASS，Python文件实际存在且精确哈希已记录。
- Python脚本只修依赖安装检测，不改现有冻结V8.0/200/81/人物/V10.2/Swift/native入口/Important/MANIFEST，已有本地output/历史失败均不删。本轮不涉及新医学预后验证，也不能把518400个理论四柱组合都声称已有公历时间事实。
- 本轮容器不可用 GitHub DNS直接clone，上游真实安装及 Mac PyCharm 环境无法远程验收；现有Wengua Actions只能验证repo状态，不等于本轮会话Python大脚本已经在Mac完整安装/起盘。
