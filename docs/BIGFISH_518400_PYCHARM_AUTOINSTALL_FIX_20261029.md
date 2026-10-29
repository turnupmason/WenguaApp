# BigFish Mac 518400 Python首次安装失败修复 · 2026-10-29

## 真实用户复现

用户在 PyCharm 执行
`/Users/masonliu/PycharmProjects/Wengua/venv/bin/python /Users/masonliu/PycharmProjects/Wengua/Wengua_BigFish_518400.py`。
报错来自 `local_batch.py:55`: `RuntimeError: 首次先双击 install.command（联网安装 Git 固定版本）`。这是 `base.check_install()` 源码依赖检测失败，518400循环尚未运行，不代表时家盘面计算失败。

## Python-only bugfix交付

本轮会话新生成并实测 `/mnt/data/Wengua_BigFish_518400.py`，**SHA256 `7e134f10184611fe4aba2d7784ef3e3fdca9d6bc6de2d5a68ff9d3376065bf55`**，762行。ZIP `Wengua_BigFish_518400_自动安装修复.zip` SHA256 `3ee1bcffecd705aa0d929e3e6ce3f3029269cf098a5d6dfa86f8eeaad5686874`。请直接在用户PyCharm项目将旧 `Wengua_BigFish_518400.py` 备份后用此同名文件替换，保留 `local_batch.py` 在同目录；不需要 `.command`。顶部 `AUTO_INSTALL=True`、`INSTALL_ONLY=False`，可设置 `INSTALL_ONLY=True` 单独验证安装，`MAX_NEW_ROWS=20` 做首批小测试，`0` 跑全部。

修改后的 `ensure_install()` 先用原 `base.check_install()` 完整SHA校验；缺失时在Python内调用 Git/NPM 下载 BigFish 固定commit `6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c`、Wengua冻结commit `0eae7d2b94742939e885938f8603e85c9452d1c3`，npm固定TS `5.8.3`，原TS编译到 `vendor/bigfish-compiled`，由真正冻结Git源复制四份资源并产出SHA manifest；**所有既有 `output/` 和SQLite完全保留**，已存在但不符SHA的用户资源/未提交Git内容拒绝覆盖。首次需要GitHub/npm联网和 Mac 上Git/Node/npm；从PyCharm启动时补充Homebrew常用PATH；后续离线。独立源门槛 `bigfish_candidate_only` 已**嵌入该单独.py**，不再依赖用户另有 `candidate_source_gate.py`。旧V8原计分模块无任何修改。BigFish 原始物理九宫强制使用原TS的真实 `bureau.yuan`：修复原本worker未将 `chaiBuJuByGanZhi` 得出的三元写入 `shiJiaGenerate` 返回九宫对象，随后 `base.normalize_bigfish()` 查 `chart['yuan']` 导致 KeyError/误判的问题（原 `bigfish_cast.cjs` 已有正确 `chart.yuan=bureau.yuan`）。首行两个可能节气均失败时保留失败原因并立即停止，避免用户挂机灌满伪断词。Node worker的原始错误写到 `_bigfish_node_errors.log` 而非丢弃。

## 实测与限制

本轮本地新Python `py_compile` PASS，九项隔离 Python unittest PASS：518400组合/五虎遁/五鼠遁、安装后直接跳过网络、缺Git与AUTO_INSTALL=False路径、固定源SHA与4冻结资源映射、原始三元传入normalize合同、SQLite两条状态/Excel CSV+XLSX与不覆盖修订稿、源码门槛不借旧盘、已存在非Git目录不覆盖。Node桥 `node --check` PASS，ZIP CRC PASS。容器不能解析 `github.com`，**未执行真实联网Git clone/npm Mac首次完整安装或真实518400 Python V8批次**。GitHub Actions历史原TS 1080结构 #40920402953、真实两盘进冻结V8 #40921478524 PASS，但不是本次新安装器验收。Mac可用Git/Node/npm和真实 PyCharm venv 仍需用户首次运行实证。未运行Xcode，此改动不是iOS发布与原盘替换。代码作为会话文件交付，**本次 GitHub commit 仅记录交接文档，原大文件未伪称已推送GitHub**。

## 不变范围

不改 200格、81格、V8冻结分数、V10.2断词、人物取用、Swift原生起盘、原著、历史CI失败、Important双镜像、MANIFEST。518400为抽象干支条件总数，12个月各两节气候选并不等于全部有真实公历起盘时刻；所有文本保持候选未审批。
