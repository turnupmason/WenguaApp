# 2026-10-31 · 原 Wengua BigFish 未来四个月真实起盘：一键循环全部人物用神

## 用户原始要求

用户先把预生成窗口缩至 **2026-11-15 至 2027-03-15（含）**，指定必须修改既有 `Wengua_BigFish_518400.py` 对应GitHub脚本而非另开发程序。随后要求“给我写个loop，loop所有用神”。本次按原始 `data/knowledge/phrase_library/health_v20/actor_profiles.json` 的**人物来源身份**逐一循环，不把天芮等多用神抹成同一个宫，也不把一个物理盘误当所有角色都能复用相同断词。

## 现行直接可运行代码

唯一变更 Python 文件 `scripts/wengua_bigfish_518400_offline_editorial_20261029.py` 默认：
```python
BATCH_MODE = 'real_clock'
RELATIONSHIP = 'all'
REAL_DATE_START = '2026-11-15'
REAL_DATE_END = '2027-03-15'
REAL_TIMEZONE = 'America/New_York'
MAX_NEW_ROWS = 20
PATIENT_BIRTH_GANZHI = None
```

- `all_signifier_configs` 直接从当前固定SHA人物JSON读取**22个不同profile ID**，不猜测或从聊天记忆复制规则。合称 `parent` 按患者男、女各一支；`spouse` 按患者男、女各一支，因此总计 **24个独立配置**，人物主源 day/year/month/hour/spouse乙庚取用各由原规则定；`self` 仅direct_self，其他仅direct_proxy。特殊 `event_news` 必须明确为实际闻讯事而非默认代问，不自动加入。年龄、出生排行、真实出生年命未知均保持None，绝不填实不存在的年命。
- `run_all_real_calendar` 顺序运行每个配置，**使用同一个已编译真实 BigFish TypeScript Node worker**；所有关系在同一个真实时辰只共享真实物理宫底盘，其他患者源、辅助宫、V8评分与V10.2原文每一关系均独立重新运行。单人仍可把 `RELATIONSHIP='father'`；`all` 配合 `abstract_518400_legacy` 会拒绝执行，防24×518400误大量生成。
- 先按 `MAX_NEW_ROWS=20` **每配置20条**，默认共最多480条；人工检查后改 `0` 为**每配置完整1452条**，总最多 **24×1452=34,848** 条真实本地时辰代表样本。它们**不是**已经覆盖全部实时秒数、节气交界、23点子初等时刻。手机版仍用当前手机时区/真实时间现场起盘；生产预生成的文字候选只能人工审核后进入离线资源。
- 每人物的独立 `output/real_calendar_20261115_20270315/<relationship>/<timezone>/source_v1/` 源配置、SQLite断点、Excel/CSV/JSONL全不覆盖。合称 `parent` 和 `spouse` 男/女分别进入 `source_v1/性别_male_<hash>`、`source_v1/性别_female_<hash>`，不能互相串用；每次总循环结果仅**追加**在 `real_calendar_20261115_20270315/_all_profiles_audit/每次运行人物用神结果.jsonl`。单个人物发生计算或导出问题保留真实FAIL并继续后续配置，末尾总循环报错而非虚假全PASS；Ctrl-C即停止整个循环且保留已写盘数据。
- 仍调用真正BigFish原TS、真实历算实际唯一节气、六甲独立源柱、冻结V8.0计分及V10.2断词；没有修改正式Swift、九宫、200/81、古籍、人工稿及Important资源。非明确已核的参考人物 `source_status=research_candidate_only` 仍是研究候选，测试成功只表示**技术正确输出该来源身份的文本**，绝不自动升级为原书证明或可发布的客户断案。

## 实际测试和失败历史

- 新 `tests/test_bigfish_all_22_signifiers_loop_20261031.py`：查22源ID顺序、24种关系/性别选用、各源kind、本人/代问区别、合称男女性路径隔离、拒绝一刀切年命/年龄/排行、续跑异常保留、总循环中止和原配置还原、全部循环不会改518400研究模式。专项首轮 [#41208404262](https://github.com/turnupmason/WenguaApp/actions/runs/41208404262) **FAIL**：测试模拟Worker只给class但断言它是Mock，属测试夹具，不是正式BigFish源；修测试spy后 [#41208459608](https://github.com/turnupmason/WenguaApp/actions/runs/41208459608) **PASS**，旧真实日历/DST/XLSX及518400断点合同也通过。
- **真正原BigFish固定 TS TypeScript 源代码编译实际运行** + Wengua V8.0/V10.2 的全体24配置同一真实公历时辰： [#41208505466](https://github.com/turnupmason/WenguaApp/actions/runs/41208505466) **24/24 PASS**，每条核 `person_binding.role_via` 与原JSON `references[0].kind` 相同、原符号落宫、无编造年命、源章节/原文SHA与评分存在。6张其它日期的真实BigFish专项仍独立运行；**24/24只是同一时刻每人物1条，并不代表已对全窗口24×1452跑过，不能声称书源全22规则权威验收**。
- 原Python V8主CI与Swift native parity及Xcode Simulator后续需核真Actions，不能以单独Python run冒称真机验收；未曾在用户Mac机器运行过新all loop，且App上游并未切换成只读候选库。
- 原版本、已见结局案例、失败和人工稿**全部保留**；后续不因源标记research_candidate_only而硬改V8。

## 本机使用

仅用当前GitHub main完整源覆盖Mac的 `Wengua_BigFish_518400.py`，要先保存原.py备份，不删旧 `local_batch.py`、`vendor/`、`frozen/`、`output/`；PyCharm无需额外第二脚本。用户首次运行后按 `_all_profiles_audit` 和每人物前3条日志人工核确。只有在真实每人前20条的失败分布/原文质量审查后，才将 `MAX_NEW_ROWS=0` 扩至整个窗口。
