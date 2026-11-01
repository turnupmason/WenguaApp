# 2026-11-01 · 疾病「难受部位」V13 细节归因与真实条件审计（未发布）

## 输入身份与已有资料复用

本轮是用户重新提供的《疾病难受部位》长篇**整理性补充资料**，不是一份带版次页码和原书 SHA 的新上传原著章节；不得把其每句话自动标作《神奇之门》或《开悟之门》的已核原文。原书已存在的唯一可核结构索引仍为：

- `data/knowledge/shenqi/health_prediction_ch01/method_index.json`，原章节 SHA256 `3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a`，相关八宫类象索引第5–7行、天芮/伤门/时干第9行。
- `data/knowledge/kaiwu/health_prediction_ch02_section01/method_index.json`，原章节 SHA256 `49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d`，第31行阴离属内盘、第85行阳坤外/阴坤内及两源案例综合取干门。案例已见，不算新增盲测。
- 既有外部候选 `data/knowledge/health_discomfort/traditional_body_clue_candidates_20261029.json` 已有八宫及十干（72干宫候选）、八门**illness/patient 两套含义**、八神候选；本次不复制覆盖该大表、也不删除冲突项。没有原书版次的病名细项继续 `draft_unverified_external_notes`。

## 本次真的增加什么

- V13 专用 `data/knowledge/health_discomfort/body_location_condition_detail_v13_20261101.json`：上离/巽/坤，中震/兑，下艮/坎/乾；中五是「中部」的象意索引，绝不是拥有普通星门神的第九个物理部位宫。
- 传统内外盘已由 V12 阴阳八宫真实排布确定。用户新增「内为新病、外为旧疾」仅作为**单独待核候选**；不能把原书已有「内近外远，内快外慢」解释直接替换成发病时间/年龄。新旧病审计 `new_or_old_determined=false`，不会出现在客户结论。
- V13 `inspect_detail` 从完整九宫直接读取天芮携干（主）、天禽携干（辅）、病宫实际地盘干（有条件的第三层），真坤二另外记录中五寄地盘干；地盘休囚须有**被核准的源格与真实月令**，尚无证据时 `conditional_eligible=false`，绝不擅取为病因。天空/地盘组合按既有81真实有序格读取，不把「合」自动等于综合症。
- 病宫本门使用 `doors[门].illness`、患者实际用神宫本门使用 `doors[门].patient`；同门可有不同身份，异门更不能串换。八神优先用病宫实际神，患者神若没有合法人物侧定义则不造。未提供出生年命不补，朋友按现行V11月干，长辈辅助按选人条件。
- 用户提供的「乾宫长幼区别」「男性坎宫」「壬癸临兑的性别区别」「震前兑后」只在实际落宫和显式提供的性别/年龄条件成立时保留 `conditional_signals`，默认不展示为病名或强制唯一部位。
- OCR 原样 `王`、`王癸`、`自虎`、`成肚` 不在原著数据上自动改写。候选规范字符壬/壬癸/白虎/戊肚（最后一个仍有歧义）独立留审计，待原本核对。
- 死门、白虎、庚等有癌症/死亡的传统联想、螣蛇的神鬼附体及各式具体药方/手术建议，在资料中作为历史文化说法保留辨析，**不进入现代病名、病死或治疗判定**；V8病情轻重原分数、评分表和正式断词完全不修改。

## 源码与验收边界

- 数据：`data/knowledge/health_discomfort/body_location_condition_detail_v13_20261101.json`
- 独立代码：`src/wengua/health_discomfort_detail_v13_draft.py`
- 在旧六段草稿中接入：`src/wengua/health_discomfort_template_v11_draft.py`，只补「上中下宫区」及「患者八门专义」并保存V13机器审计；不把文化象意合并为确诊。
- 新专项：`tests/test_health_discomfort_v13_detail_20261101.py` 包括1080真实阴阳局排布、主次天盘携干/实际地盘/中五寄坤、8个地理身体区、病人/病星八门语义隔离、明确乾宫年龄条件、无临床绝对断词；加入GitHub主CI Python3.11/3.12。
- Important 更新 Python/Swift 的模板镜像及 source、tests、engine 的 SHA，MANIFEST 保持原旧项完整，不删历史。
- App 原生 Swift 尚未接入此「难受部位」模块，iOS入口保持 disabled，不消耗15日锁。原生Swift V8 parity ≠ V13 新专题 Swift parity；实机签名/App Store/医学定位有效性全都未验。

## 过程发现及失败日志（永久保留）

专项早期CI首次失败，定位为新测试遍历 `body_axis` 时错误把 `caveat` 字符串当成 `palaces` 数据对象；实际8宫来源与运行选择没有异常。测试修改为仅遍历真实字典宫区，保持反例、错误 Actions 和测试源码历史不删。中间版本因 Important 镜像未同步也出现CI失败；在已复现原因后同步 canonical+snapshot blob SHA，后续运行应按**实际最终SHA和GitHub Actions结果**判断，不将失败说成PASS。旧 V7 综合原生归档测试存在已知历史不一致，独立保留。

未结项：原版书逐页核对年纪/性别病位特例、地盘休囚与准确月令源200格、干合病象的真实且方向明确的条件、选择唯一器官的可靠证据优先级及新专题原生Swift逐字全文验证。原书新章0，独立历史家庭0。


### 2026-11-01 · V13 最终 macOS / Python / 原生门禁实测
- 源提交 bd3a758217fb19c8ec97b95527111c303e1f36d6：主 CI [#41317341939](https://github.com/turnupmason/WenguaApp/actions/runs/41317341939) Python3.11/3.12 PASS；V13 专项5测试覆盖实际1080局/上下区/疾病与人物八门/坤二携干/年纪明确条件/新旧未决/中宫禁造。V8 Python-Swift native 逐字 parity [#41317342093](https://github.com/turnupmason/WenguaApp/actions/runs/41317342093) PASS，V7.7 legacy fixed two clocks [#41317341835](https://github.com/turnupmason/WenguaApp/actions/runs/41317341835) PASS。
- 真 macOS Xcode Simulator 构建以及App现有资源bundle验收 [#41317341932](https://github.com/turnupmason/WenguaApp/actions/runs/41317341932) PASS。这里验证仍为现有 V8 发布App，不是把V13研究文案打包发布，V13仍Python draft且 Swift未实现新专题parity，iOS入口enabled:false。
- 旧历史综合原生工作流 [#41317341843](https://github.com/turnupmason/WenguaApp/actions/runs/41317341843) FAIL（包含旧V7测试合同），历史失败如实保留，不拿新版成功偷换旧版结果。未经过签名真机或科学医学定位有效性测试。V8冻结打分不修改，原章/事件+0。
