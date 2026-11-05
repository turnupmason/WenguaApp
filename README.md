> 当前本地模型入口：**V5.1继承已训练V4补课**。先读[逐epoch审核与PowerShell启动](docs/COURSE_REPAIR_V51_20261105.md)，使用 `unlock_course_v51.py` 和 `train_wengua_v51.cmd`。旧V4/V5目录保留，下列旧模型入口仅供复现。

# 问卦 · WenguaApp

两本书来源库、原有确定性起盘、离线 iPhone App，以及独立的 Qwen3-8B 课程训练和来源 RAG。

[![CI](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml)

## 当前模型课程

当前训练为 **V5.1继承V4补课**，见[当前训练指南](docs/COURSE_REPAIR_V51_20261105.md)。V4/V5和全部起盘代码保留；当前V5.1的教材、参数、源码与恢复合同冻结。

[两书独立RAG及Windows入口](docs/WENGUA_TWO_BOOK_RAG_20261105.md)：43章、194案、1,008索引分析和全文来源，5,320项独立检索记录；附私有Excel/HTML审阅。CPU构建/检索可与当前训练并行，模型问答等训练完成后再启动。程序起盘沿用现有代码；不让模型起盘，不混旧人工计分。

课程覆盖指已经入库的 43 个章节。原书错断、学生意见、后续反馈、字形疑点和作者假说明确标记；不声称原书或模型百分之百正确，不把案例复盘分数称为现实命中率。

Windows PowerShell，先恢复RAG来源并用CPU检索：

```powershell
Set-Location "$env:USERPROFILE\WenguaApp"
git pull --ff-only origin main
.\local\qwen_env\Scripts\python.exe -X utf8 unlock_wengua_rag.py
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py build
.\local\qwen_env\Scripts\python.exe -X utf8 run_wengua_rag.py search --question "天芮和天心的作用有什么区别？"
```

解密时使用此前V4/V5.1教材口令；来源ZIP自动恢复到Downloads，构建时安装至`local/wengua_rag/sources_v1`。公开仓库只有密文、源码、来源索引和摘要。其余八本尚未收到，按章归档、核对来源后增加新索引；数据库持续更新，模型按版本集中微调。

## 目录

| 路径 | 内容 |
|---|---|
| `src/wengua/`、`scripts/` | 当前功能及必要的历史兼容代码 |
| `configs/course_v5*.json` | 新课程的独立训练与参数扫描 |
| `data/knowledge/course_v5/` | 私有课程发行哈希和覆盖摘要 |
| `data/delivery/course_v5/` | 已认证加密的课程包 |
| `archives/sqlite/` | 当前两书原库、历史库压缩件及校验目录 |
| `ios/` | 离线 App 与原生历法、排盘 |
| `tests/` | 全量回归；历史库按需校验恢复 |
| `Important/` | 按项目约定保留的关键源码镜像，不从此处导入或编译 |
| `docs/history/` | 历史报告压缩包、逐文件校验目录和恢复说明 |
| `local/` | Git 忽略的教材明文、训练输出、权重和检查点 |

旧训练源码因恢复合同和导入依赖而保留。旧数据路线不等于当前训练输入；V5 不读取它们的评分教师或适配器。

## 原书来源与历史恢复

当前只读两书源库：

`archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3`

SHA256：`21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405`。

66 份重复展开的历史数据库已移除，原始字节仍保存在各自 `.sqlite3.xz`，全部验证可无损还原。836 份重复 CI 报告压缩归档；软件直接读取的报告保留。详见 [恢复说明](docs/history/README.md)。清理前目录可在 [Git 标签](https://github.com/turnupmason/WenguaApp/tree/course-v4-before-cleanup-20261105) 查看；没有重写 Git 历史。

## App 与开发交接

App 原有封存数学和资源不随模型课程修改：[封存说明](docs/HEALTH_PRODUCTION_RELEASE_20261102.md)、[应期 V4](docs/HEALTH_RECOVERY_V4_SOURCE_CORRECTION_20261103.md)。模型研究与 App 保持独立。

继续开发先读 [AGENTS.md](AGENTS.md)、[当前状态](docs/PROJECT_STATUS.md)、[章节流程](docs/CHAPTER_WORKFLOW.md)。历史开发细节保留在章节台账和历史记录中。

历史数据库构建与归档工作流改为手动重放，日常代码/课程更新不再自动重建旧快照。原回归测试保留；私有原始来源需要按历史流程准备。
