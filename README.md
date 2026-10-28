# 问卦 · WenguaApp

**当前唯一现行疾病引擎：V8.0。** 本项目是持续开发的原生离线奇门遁甲 iPhone 应用，不是重新起盘或新建项目。当前正式投入开发与验收的专题是 **健康 → 病情轻重**；婚姻、工作、求财、出行等以后依其古籍用神规则分别开发，**绝不把疾病的加分模板套进其他领域**。

[开始阅读项目规范](AGENTS.md) · [最新项目状态](docs/PROJECT_STATUS.md) · [新窗口交接指令](docs/PROJECT_START_PROMPT_V80_20261027.md) · [中文分类导航](项目导航/README.md) · [完整规则审计](docs/V80_RULE_ENERGY_AND_XCODE_AUDIT_20261027.md)

## 一、现行 V8.0 计算规则

1. 根据领域、子题、问测人物关系，**先确定本题真正需要的用神**。再按真实时辰自动起盘，九宫真实星、门、八神、天盘干/地盘干、81有序天地格及空亡、马、墓、刑、迫、五不遇时、伏吟反吟均是可追溯原盘事实；中五不造普通神星门。
2. **只因用神落入一个实宫才对该宫计分**。该宫的九星、八门、八神、有序81格和成立的限制条件都必须完整审查，生成一个 **带正负号的宫位吉凶等级**；同宫再出现几个角色，这份**宫位基础分只算一次**。81格已涉及真实天盘干能量，不再叠加同一干的第二份基本票。
3. **宫位吉凶分绝对不是力量**。当同宫有天心、乙、值符、时干、年命，或任何其他真正的用神，每一枚**不同的物理符号**都独立查自己在月令与落宫的源200格强弱；八神按本神与宫五行关系，不凭星或任意宫位数字代替。同一个符号兼任两种角色仍只是一枚，不许自己临自己产生独立加分。
4. 所有宫对宫（克、被克、生、被生、比和）分别识别**施力用神与受力用神**，两边各读独立力量；五行关系由真实宫确定。克须查来源有向5×5及空亡/刑墓门迫等限制，非克无源规定不得杜撰新作用分。同宫吉助是否成立依**本领域适用条件与真实独立宿主**，不能只看到吉神就泛加分；空亡统一按已核规则处理。
5. 用神证据、吉凶汇总、格局优先级、有效应期只按本专题来源成立时出具；正式离线客户断词采用 [V8.0 模板](data/templates/health_severity_vnext/reading_template.json)，Python/Swift 同时辰应严格一致。面向客户不显示内部计算分数、矩阵名、调试信息。

**完整宫位图关系候选层**：[`selected_signifier_graph_v80.py`](src/wengua/selected_signifier_graph_v80.py) 以 `role_key/kind/symbol_id/palace_id/energy_fact_id` 标识角色；还记录每个已选宫里的**全部星、门、八神、天/地干、81格及空墓刑迫**、每枚实际符号的源强度和同宫/相邻/跨宫证据。它**只做事实图和证据图，不改V8.0分数**。新领域的用神与条件另定义，任何 V8.next 加分都须独立审查后才能晋升。

## 二、V8.0 真正通过的工程验收

- [V8.0 Python/Swift 源算法、2张已见固定案例+20张新时辰全文对照](https://github.com/turnupmason/WenguaApp/actions/runs/40621011300) — 已成功。
- [Xcode 16.4 原生 SwiftUI iOS Simulator 全工程编译、200格/81格/人物/模板打包校验](https://github.com/turnupmason/WenguaApp/actions/runs/40622696702) — 已成功。
- [八类用神及星门神干格完整宫环境组合图测试](https://github.com/turnupmason/WenguaApp/actions/workflows/v80_signifier_graph_combinations.yml) — 单独门槛；模拟排列是**逻辑测试**，不得当原书真实盘。
- 已知两例 V8.0 固定回归：同事`己丑 戊辰 辛卯 丁酉` 的传统吉凶模型结果 `-5`；1920年女性长辈`己丑 庚午 丁亥 乙巳`结果`+3`。用户已提供后来反馈，**不是未见盲测，更不是医疗诊断/预后能力的验证**。
- 所有旧历史版本与失败记录保留在 Git 历史和独立归档；**不作为现役疾病引擎或V8 release验收预期答案**。现阶段 Xcode 是未签名 Simulator 包，尚不等于真机安装或上架。

## 三、在 Mac 上打开现有 iOS 工程

```bash
git clone https://github.com/turnupmason/WenguaApp.git
cd WenguaApp/ios/WenguaAppUI
brew install xcodegen   # 若尚未安装
xcodegen generate --spec project.yml
open WenguaApp.xcodeproj
```

在 Xcode 选择 `WenguaApp` Scheme 与 iPhone Simulator，直接运行 **问卦**。工程入口是 `WenguaDesignPreviewApp.swift`，实际调用 `WenguaNativeCore → WenguaNativeReadingRouter → WenguaNativeVNextEngine → WenguaPythonVNextVerbatim → WenguaNativeCustomerView`；不存在第二套网络端的正式疾病引擎。完整设备准备参见 [Mac Xcode 使用说明](docs/MAC_XCODE_LOCAL_DEVELOPMENT.md)。

## 四、开发与验收

```bash
# 当前 V8.0 疾病引擎的数值、源表、镜像完整性
python3 -m unittest discover -s tests -p 'test_health_v79_independent_cohost_matrix_20261027.py' -v
python3 -m unittest discover -s tests -p 'test_important_mirror_integrity_20261026.py' -v
# 新版跨领域、全部宫内因素与排列关系只读测试
python3 -m unittest discover -s tests -p 'test_selected_signifier_graph_v80_20261027.py' -v
# 历史全量开发测试留作历史审计；部分 V7 预期不能当 V8 现行断词断言
```

开发每次提交必须读 `AGENTS.md`、状态和章节账本；同步 `Important/` 两语言镜像和 `MANIFEST.json`；保留失败 CI、原书出处、所有历史事件及修订；不可用两个已知结局反复调参。新增领域按本领域古籍原文建立用神、格局、反证、应期和模板。

## 五、中文导航与目录

- [项目导航/](项目导航/README.md)：现行版本、基础表与排盘、疾病、后续领域、iOS、测试、历史及失败分类入口。
- `src/wengua/`：**Python 正式源路径**（不能直接改中文破坏导入）。
- `ios/WenguaAppUI/`：**Xcode 正式源码与资源引用**（不能直接搬动破坏 App）。
- `data/`：原始来源表与专业模板；`tests/`：通用和现役回归。
- `Important/`：按项目既定规范保留的源码**字节镜像**，不可视为多余复本删掉。
- `docs/`、`archives/`、`schema/`、`sources/`：来源、规则、历史案例、版本与失败证据。历史资料保留可追溯，并由中文导航分类而非作为现行入口。
