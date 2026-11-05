# 历史记录

本次清理保留历史证据，移除工作目录中的重复展开件。

- `ci_reports_manifest.json` 列出每份历史 CI 报告的原路径、大小、SHA256，以及已逐件回读验证的压缩包。
- `ci_reports_before_course_v5_20261105.tar.xz` 保存这些报告的原始字节。
- 原目录可在 [清理前 Git 标签](https://github.com/turnupmason/WenguaApp/tree/course-v4-before-cleanup-20261105) 浏览；旧文档链接已尽量转到该标签。
- 软件回归直接读取的报告继续留在原路径。

需要展开时，在仓库根目录运行：

```powershell
.\local\qwen_env\Scripts\python.exe -m scripts.restore_ci_history --all
```

输出在忽略的 `local/restored_ci_history/`，不会重新塞满 `docs/`。

数据库历史见 `archives/sqlite/source_archive_catalog.json`。当前两书源库保留展开件；其他历史版本保留经 SHA256 验证的 `.sqlite3.xz`。回归测试会显式恢复自己需要的库，历史导入脚本可先运行：

```powershell
.\local\qwen_env\Scripts\python.exe -m scripts.restore_source_archives --all
```

展开件仍被 Git 忽略。请勿把这次工作目录整理理解为 Git 历史瘦身：没有重写历史，也没有删掉用户的本地训练权重或检查点。

历史数据库构建与归档工作流改为手动重放，日常代码/课程更新不再自动重建旧快照。原回归测试保留；私有原始来源需要按历史流程准备。
