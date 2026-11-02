"""Generate reviewable Chinese timing notes and the fixed-goal recovery draft.

No chart is cast and no patient/date example is fabricated by this renderer.
"""
import argparse
import json
from pathlib import Path
from src.wengua.user_timing_notes_20261102 import ROOT, load_bundle

TEMPLATE = ROOT / 'data/knowledge/health_recovery/reading_template_v2_user_timing.json'
START = '<!-- GENERATED_TIMING_BEGIN -->'
END = '<!-- GENERATED_TIMING_END -->'


def line_refs(numbers):
    return '、'.join('L' + str(n) for n in numbers)


def render_summary(bundle):
    m = bundle['manifest']
    q = bundle['exceptions_and_duplicates.json']
    parts = [
        '# 用户应期资料：跨领域完整整理 · 2026-11-02', '',
        START, '',
        '## 原文与处理范围', '',
        f"原文件{m['utf8_bytes']}字节、{m['unicode_characters']}个Unicode字符、{m['source_lines']}行；"
        f"逐行建立哈希与字符位置，共归纳{m['rule_records']}条结构化规则记录（含类别分支和情境细则）、"
        f"{m['illustrations']}组讲义示例、{m['conflict_groups']}组需保留情境的分歧、"
        f"{m['normalization_candidates']}类疑字及{m['duplicate_groups']}组重复／续写段落。", '',
        f"原文SHA256：`{m['source_sha256']}`。原始字节保存在本地`{m['private_original_path']}`，"
        '带行号读本是另一个副本，未对原文执行任何改字。公开Git只保存原创结构化整理和来源收据。', '',
        '这是用户提供的讲义／摘录混合资料。材料对《开悟之门》《奇门法窍》和老师讲解的归属按其原说记录，'
        '没有伪称所有段落已与原书版次逐字校勘。旧书章、历史病例、计分与病位模板均不覆盖。', '',
        '## 共用取期流程', '',
        '1. 先明确事件和阶段：人是谁、事是什么、成功／失败／找寻阻截是哪一类。疾病只问病什么时候好，沿用已有疾病判断。',
        '2. 先确定时间脉络和有效范围，再结合内外盘、伏反吟判断缓急；年／月／日／时不能混换，也不能跨过已知期限找下一轮干支。',
        '3. 分人用神与事用神。应期点是本事实际需要发生作用的对象，不能所有事情都只看本人宫，也不能所有工作都只看开门。',
        '4. 对所选对象检查空、马、墓库、刑冲、合，再看生旺墓绝；保留下表前提及逆转／反跳等例外。这个顺序不是已验证的全局单选算法。',
        '5. 先定支，再配干。先遇必须在同一事件、同一单位和有效范围内计算；同气和特殊符号情境可能细分或改变候选。',
        '6. 确需符使参与才看值符先、值使后的作用；值使宫数的时长方法与符使干支作用是两条轨道。',
        '7. 区分发生日期与有效期限、整体与当前阶段。资料不支持天天重起局；本轮不改现有15天产品限制。', '',
        '## 用神状态顺序与前提', '',
        '| 状态 | 先决条件与取法 | 必须保留的限制 |',
        '|---|---|---|',
        '| 空亡 | 所选实际对象逢空，普通段参填／冲的先遇 | 失败类仅列填实；值符另论出旬；逆转／反跳有天盘干候选 |',
        '| 马星 | 明确不空，再查真实相关马星动／被冲 | 宫内有四马支不自动等于该盘实际马星；还参同气 |',
        '| 墓库 | 明确不空、无相关马，再辨实际墓库 | 回款开墓与病危入墓不是同一方向，不倒转成病愈 |',
        '| 刑冲 | 原段要求不空、无马、无墓后参合解 | 戊震、庚艮等有特殊例；外来支与本宫支须分清 |',
        '| 合 | 依适用对象参冲开 | 合与刑冲并存未给完整互斥表；某些例强调冲外来暗支 |',
        '| 生旺墓绝 | 前述状态不适用时，再按对象和事体需要 | 生患者、制病象等方向不同，不能见生就写病愈 |', '',
        '空亡、马星、墓库等未知时，不能把“未知”当作“不存在”跳到后面的规则。', '',
        '## 三类事情分别取法', '',
        '- **成功类**：资料明确列疾病能愈、工作能就、婚姻可成等；先有可成判断，再参得令、需生、需克、空填冲、库冲、刑冲逢合、马动、数干八法。',
        '- **失败类**：六法保留在共用库，不能把病危或失败的触发时间当成病愈时间。',
        '- **破获／找寻／阻止类**：庚的阻隔作用随事件目的取用，含直接年／月／日／时格及庚上／庚下；庚格空、乙庚同层合等失格条件必须同时保留。', '',
        '## 工作例揭示的人与事', '',
        '朋友的用神是月干，开门表示岗位状况与标准。资料一面说明不能只按开门判“何时找到”，'
        '后面又给出岗位空亡与朋友空亡两种等待条件；整理时保留这两层，不删任何一层。', '',
        '- 人已准备好而岗位开门空：关注岗位解除限制的候选。',
        '- 岗位机会到而朋友用神空：机会不能代替本人已能落实；等其限制解除。',
        '- 值使表示的有效期限另行记录；“9天内可办”不等于“第9天必上岗”。', '',
        '## 同气、宫数及符使', '',
        '四正为子午卯酉，四马为寅申巳亥，四库为辰戌丑未。丑寅宫例可据所用时间层细分为丑、寅或交接段；'
        'L74的“起局用事时间／时上”句按其时支语境记录；其它宽泛的用事时间须标明层次，不任意跨层。', '',
        '已知事情单位时以后天数为主，未知时程的先后天参用只给约量。资料没有唯一拼数／相加／倍乘算法，'
        '兑宫8年、3.5至4年、17或27天等不写成通用公式。', '',
        '符应先、使应后要带事件适用性。用神临值使可有已经启动的象，但空／墓例外仍在；不能倒填事实说事情必已发生。', '',
        '## 分歧和例外完整保留', '',
        '| 编号 | 情境 | 处理与来源 |', '|---|---|---|',
    ]
    for row in q['conflicts']:
        parts.append(f"| {row['id']} | {row['title']} | {row['detail']}（{line_refs(row['source_lines'])}） |")
    parts += ['', '## 疑字、重复与来源层次', '',
              '下列只是候选校读，未应用到原文。特别不全局替换“已”“成”“末”等正常词。', '',
              '| 原字／片段 | 候选 | 说明 |', '|---|---|---|']
    for row in q['normalization_candidates']:
        parts.append(f"| {row['raw_token']} | {row['candidate']} | {row['note']}（{line_refs(row['source_lines'])}） |")
    parts += ['', '末尾重述、近重复、断句续写全部保留；重复来源不作为多条独立证据加票。', '',
              '## 跨领域复用入口', '', '| 领域 | 事件和取用范围 |', '|---|---|']
    for row in bundle['domain_contracts.json']['domains']:
        parts.append(f"| {row['id']} | {row['event']}：{row['event_role']} |")
    parts += ['', '这是12个明确提及领域的入口记录，不代表这些领域均已完成专题解读或可借疾病评分。', '',
              '## 讲义示例及完整性', '',
              '29组示例完整链接到来源。下雨、出租车只有讲义报告，其他多为假设或局部符号示例；'
              '没有完整起局时刻／全九宫，不编造新实盘，也不计作新增完整历史病例或独立预测验证。', '',
              '| 示例 | 已知情境 | 原资料的说明／预测 | 后续报告 | 来源 |', '|---|---|---|---|---|']
    for row in bundle['illustrations.json']['illustrations']:
        parts.append(f"| {row['id']} | {row['known_context']} | {row['source_forecast_or_illustration']} | "
                     f"{row['reported_result'] or '未给出实际反馈'} | {line_refs(row['source_lines'])} |")
    parts += ['', '## 全部结构化规则索引', '',
              '前提表达式、例外引用和逐行哈希保存在`rules.json`与`source_units.json`；下表为可读归纳，非逐字原文。', '',
              '| 规则 | 归纳 | 来源 |', '|---|---|---|']
    for rule in bundle['rules.json']['rules']:
        parts.append(f"| {rule['id']} {rule['title']} | {rule['summary']} | {line_refs(rule['source_lines'])} |")
    parts += ['', '## 已实现与待实现', '',
              '已实现原始字节私有备份、逐行收据、完整覆盖、结构化条件三值校验与模板生成；'
              '条件为真只表示输入事实满足所记录前提，既不证明事实本身正确，也不等于规则已获准运行。', '',
              '原文讲年、月、日、时；现有历法区间生产器仅日／月。逆转反跳识别、多层符号墓库、'
              '病愈对象自动选择及新触发法须分别实现与验证。当前未改正式评分、病位、UI或开启病愈功能。', '', END]
    return '\n'.join(parts) + '\n'


def render_health_template(template, bundle):
    if (template['source_id'], template['source_sha256']) != (
            bundle['manifest']['source_id'], bundle['manifest']['source_sha256']):
        raise ValueError('Recovery template source differs from timing notes')
    labels = {
        'dated_window': '有具体候选期', 'bounded_relative_window': '有可靠相对时长',
        'recovery_premise_unresolved': '恢复转机尚未明确', 'missing_time_axis': '时间轮次未定',
        'missing_condition': '必要条件不足', 'method_conflict': '方法或对象存在分歧',
        'precision_unavailable': '尚不支持所需精度',
    }
    values = {key: '〔' + description + '〕' for key, description in template['fields'].items()}
    lines = ['# 疾病应期模板 V2：只看病什么时候好', '', START, '',
             '本版根据用户新提供的完整应期资料生成。沿用已完成的病情轻重、病位和人物取用，'
             '不再让用户区分好转／出院／临床治愈目标，也不重复强弱或病位报告。V1原稿继续保留。', '',
             '当前是可审阅的断词模板，尚未打包为手机正式资源。方括号须由同一次真实盘的取期结果填入，'
             '不是捏造的新病人、新盘或日期。', '']
    for section in template['sections']:
        lines += ['## ' + section['title'], '']
        if 'branch' in section:
            for state, paragraphs in template[section['branch']].items():
                lines += ['**' + labels[state] + '**', '']
                lines += [paragraph.format_map(values) for paragraph in paragraphs] + ['']
        else:
            for paragraph in section['paragraphs']:
                lines += [paragraph['text'].format_map(values), '']
    lines += ['## 使用顺序与边界', '',
              '沿用既有疾病判断及真实患者绑定 → 明确时程、缓急与单位 → 选定本次恢复所需的实际应期对象 → '
              '检查空马墓刑冲合生旺及其例外 → 先支后干并核时限 → 经历法计算后填写病愈候选期。', '',
              '资料L48要求先判疾病能愈，再取成功类应期；吉凶净分不能直接换算康复天数。'
              '已有病情结论若不足以确定恢复前提，应当补核这一前提，不重新输出一份强弱／病位报告。', '',
              '资料包含年、月、日、时；现有历法区间生产器仅日、月。其余粒度与新触发法仍须实现验证，'
              '不为了给日期而擅自把年／时换成月／日。', '',
              '仅在确有适用依据时才填写符使、同气、干支和有效时限段落；未知不填，冲突不任意取最近。', '',
              '完整共用方法、领域区别、29组示例、疑字与分歧见[应期资料整理](TIMING_METHODS_USER_NOTES_20261102.md)。',
              '', END]
    return '\n'.join(lines) + '\n'


def outputs():
    bundle = load_bundle()
    template = json.loads(TEMPLATE.read_text('utf8'))
    return {
        ROOT / 'docs/TIMING_METHODS_USER_NOTES_20261102.md': render_summary(bundle),
        ROOT / 'docs/HEALTH_RECOVERY_TEMPLATE_V2_20261102.md': render_health_template(template, bundle),
    }


def generated_part(text):
    return text[text.index(START):text.index(END) + len(END)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in outputs().items():
        if args.check:
            if generated_part(path.read_text('utf8')) != generated_part(text):
                raise ValueError('Generated timing review differs: ' + path.name)
        else:
            old = path.read_text('utf8') if path.exists() else ''
            tail = old[old.index(END) + len(END):] if END in old else ''
            path.write_text(text.rstrip() + tail if tail else text, encoding='utf8')
    print('Timing note summary and fixed-goal recovery V2 review: ' + ('checked' if args.check else 'generated'))


if __name__ == '__main__':
    main()
