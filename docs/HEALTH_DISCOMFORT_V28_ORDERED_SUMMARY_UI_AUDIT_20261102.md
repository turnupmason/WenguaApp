# V28 病位开头结论、墓刑优先与真实UI接线

用户本轮要求：第一段即给最终关注部位和先后，综合天芮宫干、81格、八神、门、落宫、启用的伤门、时干、关系用神和全盘墓刑；同步Python/Swift及现有iOS，并随机爷爷none预览。

## 真实缺口
- 原首段只报宫象；末段仅一处主位加首条跨宫异常，未给全证据排序。
- WenguaPremiumReadingView.swift 病位摘要读取不存在的06_conclusion；实际为09_conclusion，造成有全文却无首页结论。本轮修复为直接读取bodySiteSummary并兼容旧09段。
- 旧main源码0c0d6fa的Xcode任务41392726907：真正Simulator编译和bundle已成功，独立文本对照失败，并非Xcode未编译。job125107431644实际diff是Swift“与天芮同宫”/Python“两者同宫”。其余反向方向近义差异一并统一，未改五行或源力量；旧FAIL归档保留。

## 实现
- V28 schema wengua_health_discomfort_native_v28_ordered_summary_tomb_priority_20261102；两个composer各自真实读取源规则，新增相同bodySiteSummary。第一实际段前置该摘要，末段以相同摘要开头；UI直接显示同一字段，未建立第三套推断。
- 启用事故/骨肉/出血/剧痛时实际伤门宫仍首位，手术另报手术候选部位；none不输出独立伤门段或injury角色，病宫实门仍照常分析。
- 全八实宫真实天地干逐符查墓刑，同宫同干归并。墓刑部位提升关注顺序，前两个异常按真实源200力量、宫ID、干排序；保留全部异常原文。源极小不会因墓刑改成极大，V8轻重冻结不动。墓刑仅传统象意，不能声称实际医学损伤已确认。
- 摘要再纳入天芮主位与独立强干、时干/关系用神的部位证据，聚焦四个可区分部位；末段合读天盘地盘、双81格、门神、时干与患者。宽泛旧来源“脏腑泛象”只保留原有提示，不拿巽宫耳朵等替代该干对应器官，不擅自新增三源混用规则。此项细部不明仍保留限制。
- 真实人物源JSON/出生年命条件不改。新的爷爷时辰在实现前随机抽得2026-11-12 19:00 -05，真实丙午/己亥/庚寅/丙戌，阴遁三局；年干丙与时干丙同源同宫，乾辅独立，未补出生年命；非秘密盲测，作为预览固定复核。
- 原UI项目project.yml已打包同一native_discomfort_v15.json并编译本次原生文件，无另建工程。Important镜像和MANIFEST Git blob SHA同步。

## 回归和失败保留
- 本轮初跑病位59测试通过；新增V28三测试，24实盘条件输出、弱戊入墓原极小保留、数据不变与摘要一致通过。
- 初跑旧V23源字符串断言bodyEvidence.append失败：V28已用orderedFormations+summary取代旧单证据列表；更新该结构断言为新归并路径，保留400/45真实源力核对，不降低源证据要求。全库及本次源码macOS的最终真实结果待实际填入，不用旧PASS代替。
- NativeDiscomfortV19Parity追加用户爷爷none同一时刻，连同弟弟/妻子/女儿旧固定回归四盘独立Python全文比较；NativeInjuryContextAcceptance再验四盘×六条件24个真实Swift输出与Python逐字一致。第一段/末段/DTO摘要须相同。旧女儿已揭晓盘非盲测。

本轮不改原著、81/200/255源及V8评分。签名iPhone安装/App Store不在本次Simulator验收内。

## 本轮本地最终实测和发布边界
- 病位全部62项通过，Important逐字镜像检查通过。
- 当前全库834项：41 failures、11 errors、3 skipped。独立detached旧main 61e4a26同环境全库831项同样41 failures、11 errors、3 skipped；52个失败/错误标题集合完全相同，新增V28三项通过。没有用旧V8断言驱动本次改算法。
- 自动审批两次拒绝直推main，理由是当前用户消息没有直接授权默认分支发布；虽项目上下文有长期main指令，审批不采纳其为直接本轮授权。没有改用其它工具绕过。改在codex/v28-body-site-summary审阅分支交付，PR构建禁止自动归档步骤推送main；真实Xcode/Swift及资源通过后仍须用户明确确认合入main。
