# 问卦 · WenguaApp

两本书来源库、离线 iPhone App，以及独立的 Qwen3-8B 课程训练。

[![CI](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/turnupmason/WenguaApp/actions/workflows/ci.yml)

## 当前模型课程

**V4 已在用户电脑运行，继续保留原数据、参数、代码合同和检查点。** 补齐后的 V5 使用新目录、新适配器，不向正在运行的 V4 注入新教材。

[V5 课程与训练说明](docs/COURSE_COMPLETE_V5_20261105.md)：11,196 核心任务，逐项处置 1,451 个知识单元、194 原案、1,008 索引分析，并补入索引外正文、老师按语和原表读取。全部目标经官方 tokenizer 验证，无长度丢弃。只用两书来源，排除旧人工计分。

课程覆盖指已经入库的 43 个章节。原书错断、学生意见、后续反馈、字形疑点和作者假说明确标记；不声称原书或模型百分之百正确，不把案例复盘分数称为现实命中率。

Windows PowerShell，在 V4 结束后：

```powershell
Set-Location "$env:USERPROFILE\WenguaApp"
git pull --ff-only origin main
.\local\qwen_env\Scripts\python.exe -X utf8 unlock_course_v5.py
.\train_wengua_v5.cmd
```

解密时使用此前私有对话中的 V4 密钥；明文课程和 Excel 自动恢复到 Downloads。公开仓库只有密文、源码、来源索引和摘要。不要同时启动两套 GPU 训练。

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
