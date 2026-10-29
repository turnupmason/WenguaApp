# 2026-10-29 PyCharm 518400 BigFish Node worker fast-path failure / no-natal scope

## Mac真实复现
用户直接从 PyCharm 以 Python 3.11 venv 运行 `Wengua_BigFish_518400.py`，打印 father / casting_year_stem / 乾6 / direct_proxy / 无年命 / 已完成0后，`BigFishWorker.__init__` 的 `subprocess.Popen(['node', ...])` 抛 `FileNotFoundError [Errno 2]`。尚未进入一个双节气的真实读盘循环；不是 V8分数、人物用神、BigFish原TS本身的失败。

## 原因与修复
源 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 的 `ensure_install()` 旧逻辑先 `return base.check_install()`，已有 frozen/source 环境时绕过 `_extend_macos_tool_path()` 和 `ensure_node_available()`，之后 worker 靠字符串 `'node'` 启动导致 PyCharm Finder PATH 与 Terminal 不一致即崩。现修成每次启动**先补PATH和验证/自动准备Node**再走已有安装快速路径；worker用 `shutil.which('node')` 查真实路径后启动，找不到则抛针对性的 RuntimeError 而不是裸 FileNotFoundError。保留官方签名/HTTPS SHA校验自动安装逻辑，不关闭TLS，不删原文件。

## 年命与可审核范围
用户本轮明确：**所有人物关系主辅用神全部验收前，年命一律关闭。** `PATIENT_BIRTH_GANZHI = None`，无年命角色、无年命宫、无年命得分。未来用户提供经真实日期/立春核定的完整年命时，作为额外真实独立用神参加源强度/同宫/跨宫判断，并在独立新版本条件库存档，**不得覆盖本轮无年命结果、已有失败/Excel和人工审稿**。父亲此时仍为问测年干、乾6辅助，不把出生年命偷换问测年干；其它关系从原22 profile ID来源逐个校验，未核准不记成功。

## 质量门槛
新增 `tests/test_bigfish_node_runtime_pycharm_20261029.py`：已有安装也做Node初始化、worker使用绝对可执行文件、缺Node先明确提示、默认无年命四项；已纳入 BigFish batch 专项 Actions。只有 GitHub 真实运行后才可标 PASS。本环境无用户 Mac 文件系统，**不能声称已经在用户 PyCharm 或518400条上成功运行**。此补丁不改冻结 V8/V10.2、200/81源、Swift/iOS、Important双镜像/MANIFEST、不清历史失败。

## 新增真实CI失败及原因（保留而非掩盖）

首次专项 `#40944733685` 在现有BigFish/人物原测试与Python py_compile全部PASS之后，新4项 Node回归 **4 ERROR**：测试夹具 `local_batch` 少提供上游 `BIGFISH_SHA`/Wengua SHA；异常发生于被测脚本模块载入行416，**不是应用代码 Node路径修复的失败，也不表示Mac已通过**。已按仓库现成 fixture 的真实常量补齐，重跑专项 Actions，旧失败历史不删除。链接：https://github.com/turnupmason/WenguaApp/actions/runs/40944733685 。
