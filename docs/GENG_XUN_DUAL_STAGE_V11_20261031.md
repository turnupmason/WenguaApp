# 2026-10-31 · 庚金巽四宫十二长生主断：V11.2 / BigFish 新批量版本独立审计

## 原因、具体真实盘、原始事实
复现真实时辰：2026-12-12T09:30:00-05:00 America/New_York，四柱丙午/庚子/庚申/辛巳，患者取朋友真实月干庚，巽四宫；原始 BigFish TypeScript 物理盘 yin-01-辛巳，见 docs/BIGFISH_V11_THREE_REAL_RANDOM_AUDIT_20261031.md。旧 Python 查表在不同地支源力量不一致时直接写 None；旧 Swift 同样写 nil，于是出现用户所见「势待核」，且影响克病矩阵的真实适用性。

原始十二长生两项均不删除：庚在巽四宫：辰=养、巳=长生；子月金生水，「生月令」列在源200格中，辰养行=中等、巳长生行=大。不可将物理宫的星门神81格 ±5 净分当作庚的独立源力量。

## 用户新确认的精确主断条件
仅当独立用神满足庚金、巽四宫、真实宫支两事实为辰养和巳长生时，选择巳长生作为主断源200格行；辰养仍在双支原事实和源200格候选中保留。此为用户 2026-10-31 明示的新取舍，不伪称《神奇之门》《开悟之门》原著逐字古诀，也不泛化为全部干、全部宫一律取旺/取最大。其它未经核准的双支差异不得偷偷填充。

## 实施及冻结边界
- Python src/wengua/user_domain_matrices_20261023.py:lookup_selected_factor 精确选择已核巳长生行，保留辰/巳原事实、两格候选、所选原行、独立强度及 user_explicit 来源；其它情况旧法不变。
- ios/WenguaAppUI/WenguaNativeVNextEngine.swift:factor 与 Python 相同条件、相同月令列、相同真实源200格强度。Python、Swift V11 全章节和综合断语保留独立真实角色及「巳长生主断，辰养备查」，无旧「庚势待核」；继续显示首屏「吉/凶/微恙→十档文学标题→盘与医药事实→两句完整结论」；专业全文不删。
- BigFish scripts/wengua_bigfish_518400_offline_editorial_20261029.py 固定 Wengua 源 commit 1da1e5035061ade8fbdb54ecd0451c6eaef7c1b8，使用独立 V11.2 新冻结源码路径、v8 新真实时辰输出文件夹，保留旧 source_v7、所有数据库、失败、原文本和已改写作品。真正 compute_variant 对所有符合庚巽四的选中用神按源实际再次校验，记录两个原分支及两格，若新旧不一致拒绝输出伪成功。
- 关联测试 tests/test_geng_xun_primary_changsheng_20261031.py、tests/test_bigfish_v11_full_two_tab_20261031.py、tests/test_bigfish_real_clock_nov2026_mar2027_20261031.py；main Python CI/BigFish CI 真实工作流新运行。原著、V8 既有计分矩阵、81格、双主干特殊病宫、空墓刑迫、同宫基础只算一次、五不遇、天显、伏吟/反吟以及已揭晓疾病结局不为迎合结果修改。
- 重要：这不是单纯文字修复。以前庚源强无效，如今源200格有效，会改变某些实际对抗条件及原V8数学应用的最终得分。必须在真实新盘和既有案例回归验证，不能声称分数一字未动、不能为迎合结果再改分。
- 书章与事件家族本次新增零；不以原始经验宣称科学有效预后。App 签名真机/App Store、Mac 全量所有人物1452条批量尚需用户设备真实执行，不因提交代码就算通过。

## 已保留且不能篡改的失败
此前 BigFish 用户盘庚巽四「待核」是实际缺陷而非古诀待定，已据此设新回归。历史此前脚本固定旧SHA不能当新版本发布；修复前 CI、临时预览归档失败链接、已见2个病案都保留。新运行结果一律以本次 Action 完成状态为准，不能先标成功。


## 2026-10-31 V11.2 本轮真实交付验收（后续追加，不覆盖早期失败）
- 主CI [#41247581024](https://github.com/turnupmason/WenguaApp/actions/runs/41247581024) PASS；包含单独的庚巽四双支十二个月回归及原V8现行测试。
- BigFish完整预审工作流 [#41247574228](https://github.com/turnupmason/WenguaApp/actions/runs/41247574228) PASS：200源格、旧1100父亲源冻结与不覆盖、121真实日×12代表时辰=1452槽、24人物源ID×26种条件配置、双页模板检查均成功。这是预审/回归，不等于已经在Mac批量生成26×1452条作品。
- BigFish真实原始TS起盘+原Wengua V8/V11.2 断词三随机真实时辰 [#41247580945](https://github.com/turnupmason/WenguaApp/actions/runs/41247580945) PASS；全稿另存 docs/BIGFISH_V11_2_THREE_REAL_RANDOM_COMPLETE_20261031.txt，旧 V11 已封存 TXT 不覆盖。三盘：2026-12-14哥哥极小凶、2027-02-01姐姐不凶不吉、2026-12-12朋友小凶；朋友实际庚在巽四，势大，证据明确「以巳长生主断，辰养备查」，末尾写完整小凶结论。
- 2026-10-31 底层 Swift 现行源码在真正 macOS iOS Xcode Simulator [#41247218548](https://github.com/turnupmason/WenguaApp/actions/runs/41247218548) PASS（含bundle资源验收）；Python/Swift native V8两套全文对照 [#41247218530](https://github.com/turnupmason/WenguaApp/actions/runs/41247218530) PASS。BigFish批量单独版本更新没有修改 Swift 层，正式签名真机/App Store未验。
- 历史失败仍保留：BigFish Pin 切换中间几次 CI FAIL，源旧测试SHA已同步；此前 V7.4 故事原始断词/历史独立1080及旧预览归档冲突失败不可擦除或当作本轮已通过。新旧结果不能按用户事后获悉结局做拟合；整套规则仍属古籍象意，不属医学诊断预测。
