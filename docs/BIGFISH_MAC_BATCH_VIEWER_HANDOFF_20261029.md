# BigFish Mac 本地逐时辰批量结果可视化 · 2026-10-29

## 用户问题
用户问「怎么开始批量生成？我sql看不了」。真正需要的是一键触发批量、可见的中文结果与 Excel/Numbers 表，而不是让用户直接操作 SQLite。

## 交付
本轮会话生成了 `WenguaBigFishLocal_20261029_可视化批量版.zip`，SHA256 `2bf7e5b1c7fe2140e1fda99918d3c2c03278303ee49f5b6e89071dd55e8ff3f3`；如果用户已安装前版且有进度，另有不包含 vendor/frozen/output 的补丁 ZIP `WenguaBigFishLocal_结果查看补丁_20261029.zip`，SHA256 `9a1151954993f6b8fd0c32ce6f014fb2aa974ad4c1b69c2b79f160f782af91b4`。它们是本轮聊天下载文件，不应编造本仓长期托管的附件地址。

新本地文件：
- `export_results.py`：Python标准库 sqlite3 **read-only** 读取 `output/progress.sqlite3`，输出 `output/点击查看_批量结果.html`（完全本地网页、搜索/过滤/展开中文）、`output/批量断词汇总_Excel打开.csv`（带UTF-8 BOM；全部行含年月日时四柱、人物、状态、完整候选断词、失败原因）、`output/批量中文断词_全文.txt`（只汇总有真实文本者）；不改变计分、盘、审计或数据库。网页上限500条视图，CSV/TXT全量。
- `RUN_ONE.command`：单盘后自动导出/打开本地HTML；`RUN_BATCH.command`：每次最多新增24真实条件案例后导出/打开；`批量生成240条.command`：稳定后最多新增240条；`导出并查看结果.command`：只导出不计算；`查看运行状态.command`：查看已记录/失败进度。重复运行原脚本保留SQLite进度并跳过已记录事务。
- `START_HERE_使用顺序.txt`、`README_使用说明.md`：一键顺序与不手动打开/删除SQL说明；已有目录升级应保留 `vendor/`、`frozen/`、`output/`，补丁仅覆盖新增脚本/README，避免丢失已有候选。
- 表格 CSV 对以 `=,+,-,@` 开头的源文本采取安全转义，HTML 动态内容转义；失败记录与有断词的研究候选分开展示。未生成即显示零条，绝不放样例假结果。

## 实测
本会话实际执行 `python3 -m unittest discover -s tests -v` 7/7 PASS（原5项 BigFish字段适配器合同＋新2项 exporter测试，含真实SQLite临时库读取、HTML/CSV/TXT内容/中文、HTML注入防御、数据库字节未修改与公式注入规避），`python3 -m py_compile export_results.py` PASS，所有 `.command` 脚本 `bash -n` PASS，两份ZIP CRC全过。没有用户电脑的 `vendor/` 与实际进度库，不能说已在用户 Mac 跑成功，更不能把测试中人为构建的DB样本说成任何真实干支排盘。

## 冻结范围与后续
本轮只改 Mac **导出查看体验**；`src/wengua` 现行V8.0疾病轻重、V10.2模板、200/81/人物、Swift/Important/MANIFEST及真源历史失败**完全未变**。新的 BigFish 原TS跨仓样本 CI #40921478524 PASS，但它只验证2个真实时辰并不能证明1080真实历法全盘/Swift逐字段或预测临床效力。旧晚子时与特殊历法差异依然拒绝/留痕。离线批量文本一律为待审核候选，不能未经审查自动发布到 App。
