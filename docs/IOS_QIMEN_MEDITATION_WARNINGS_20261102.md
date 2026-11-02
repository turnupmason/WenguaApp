# 奇门论疾简明首页、静心动画及Xcode警告 · p3

用户本轮明确要求清理Xcode issues、第一页直接说实际病位、旁证只在专业解盘，以及30秒等待时的小和尚敲木鱼诵念动画。此为授权展示/工程补丁，不变更V9计分/V11模板或V27规则。

## 实际缺陷与修改

| 位置 | 复现/之前 | 预期及修改 |
|---|---|---|
| PremiumReadingView 的病位摘要 | 用户截图已有真实右侧肋腰结论，首句仍夹“先从伤门落宫看” | 从同份09结论首句显示“本次因属伤损，先看右侧肋腰一带”，剧痛分支同样直接说“先看” |
| PremiumReadingView 的 details 文本 | 首卡重复天禽伏吟、胃部刑墓和核实说明 | 首页仅显示主位首句；完整原文/旁证在专业解盘与历史reading保持逐字不变 |
| DesignPreviewApp 静心页 | 单独圆形数字等待 | 同一等待页接入原生矢量小和尚：闭目、袈裟、坐垫、木鱼、抬槌敲击、声纹及循环诵念文字，保留进度/秒数与完成按钮 |
| DesignPreviewApp onChange | iOS17提示旧单参数API弃用 | 采用双参数API，人物变化仍重置原4字段 |
| NativeDiscomfortV15 未用变量 | companion/witnesses/secondary/sourceSites/ending | 删除不参与输出的纯死值；保留真实部位排序、独立力量/关系与详细断词 |
| NativeReadingRouter macro | 拼成后不使用，但try可能验证短句完整性 | 保留原try与求值次序，以 `_ = try` 显式验证，不删除错误守门 |
| NativeDiscomfortV15及Smoke的guard | map/filter尾闭包与guard语句体歧义 | 使用显式括号，判断语义不变 |

截图仅UI样本，没有起盘时辰，不为它编造实盘。“右侧肋腰”来自截图原句；实际每盘继续读取自己的真实V27结论，不固定显示此部位。

完整编译比增量问题导航显示更多未用值，原始诊断从实际 #41469280778/#41468305381 提取保留于 [prior_swift_warnings.json](audits/ios_meditation_p3_20261102/prior_swift_warnings.json)。正式Target启用Swift警告即错误，CI同时查实际App编译日志中的Swift源警告并归档计数；未关闭/抑制警告。Apple工具未链接AppIntents时的metadata提示不属于Swift源警告，也不冒称本App已经使用AppIntents。

## 等待与离线边界

- Canvas矢量与Timeline在App本地绘制，不新增图片下载或第三方包，默认无声音；诵念以文字节奏呈现。
- 敲击每1.6秒一个周期；未开始或完成后静止。系统“减少动态效果”时改静态插图，后台暂停动画；原有30秒真实截止时间继续控制确认，不按动画帧累计秒数。
- 确认时才调用原生真实起盘，15天限制仍只在成功保存后登记。不存在跳过等待、拿动画时间替代起局时刻或提前锁题。
- 这次未接入康复应期，也未将古籍象意改成现实病理诊断。

## 封存与验证

p2清单逐字保存在 `archives/engineering_patch_20261102/health_frozen_20261102_before_meditation.json`，当前清单明确engineering_p3。只改5份已有生产源pin（入口、首页、病位Swift的死值/闭包、Router验证绑定、project.yml），新增1份动画源pin。7份规则资源/模板和所有Python/评分源码的SHA不变。p2范围测试继续核归档p2，p3单独核当前，绝不放宽旧范围断言。

本地8项专项通过；完整843 tests仍原2个手动真实时辰入口失败、0 errors、3既有skip，完整日志无损压缩保存于 [python_unittest_full.log.gz](audits/ios_meditation_p3_20261102/python_unittest_full.log.gz)，不以新skip/删断言隐藏失败。新增实际Swift源码运行检查覆盖普通病位、伤损/剧痛直接措辞、正文不污染、原reading不变、木鱼节奏与停止状态，继续对两份真实native输出验摘要。正式Xcode执行实际App编译、零Swift警告、包资源SHA、两主题Bundle路由及六伤损条件/1080回归。

本地环境无Swift/Xcode；其新执行结果以本提交真实Actions完成后另追加。源码检查不称动画像素验收或真机安装。

## Mac查看

按根README先pull，再执行 `xcodegen generate --spec project.yml`，打开 `WenguaApp.xcodeproj`，选iPhone Simulator按⌘R。需重新生成工程才能纳入动画文件与警告即错误设置。奇门论疾旧V27记录可直接查看简明首页；新起局进入静心页可看完整动画，等待结束后确认仍使用现场时间。


### 2026-11-02 · p3简明首页、静心动画及Swift零警告实测完成
生产源码f7c0ab453f3d295abf6db4cd1f946d93a09b4211：正式macOS Xcode #41474512486 success，Swift源码警告0，正式Target以警告即错误编译；实际App资源SHA/白名单、哥哥/妻子两主题4次Bundle调用、V27全文逐字、全部6伤损条件及1080数据集通过。完整原日志 docs/IOS_V80_XCODE_PASS_RUN_41474512486_ATTEMPT_1.md 含PASS SWIFT_PRODUCTION_WARNINGS_ZERO和PASS QIMEN_LUNJI_FRONT_PAGE。
共享原生 #41474512713 success：首页普通/伤损/剧痛简明文案、真实两张V27输出、保留完整原reading、木鱼周期/停止状态实际Swift运行通过；主CI #41474512568（Python3.11/3.12）与独立iOS真实App Xcode/全部原生回归 #41474512484 success。本轮这四个Actions均无失败；全库843 tests原2个手动时辰入口失败与3个原skip另行原样保留，不称全库全绿。
README、Important字节镜像/Git blob SHA及封存p3清单已同步。两个模板/7份规则资源/Python/评分源pin不变。没有进行真机签名、动画截图或整套XCUITest像素/按钮验收；动画为本地矢量与诵念文字，默认静音。Mac须按README pull后重新xcodegen generate并⌘R，将新增动画文件加入现有工程；历史V27结论直接使用新首页展示。病愈应期尚未开放。
