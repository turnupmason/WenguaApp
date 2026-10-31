#!/usr/bin/env python3
"""Three new seeded REAL BigFish TypeScript casts for older brother, older sister, friend.

The sample uses original TS physical boards, strict instant-JieQi BigFish calendar,
pinned V11 native/Python source, true individual patient role and complete customer
sections. Failed casts are retained with actual errors; no grades are cherry-picked.
"""
from __future__ import annotations
import json
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import wengua_bigfish_518400_offline_editorial_20261029 as b

SEED=202610311729
THREE=(('哥哥','older_brother'),('姐姐','older_sister'),('朋友','friend'))

def main():
    rng=random.Random(SEED)
    b.activate_six_jia_sources()
    manifest=b.ensure_install()
    # Standalone entry runs from scripts/; Python does not automatically import repo-root src.
    # Resolve the EXACT pinned Wengua source that BigFish just SHA-verified.
    sys.path.insert(0,str(b.base.SOURCE))
    assert manifest['wengua_sha']==b.SIX_JIA_APPROVED_WENGUA_SHA
    assert b.REAL_PIPELINE_VERSION.endswith('v6_V11_full_two_tab_friend_month_only')
    source=b.base.FROZEN/'reading_template.json'
    template=json.loads(source.read_text(encoding='utf8'))
    assert template['schema']=='health_severity_user_editable_template_v20261031_v11_full_evidence'
    print('新随机种子',SEED)
    print('起盘源 BigFish 原始 TypeScript', b.base.BIGFISH_SHA)
    print('断案源 Wengua V8计分+V11完整中文', b.base.WENGUA_SHA)
    print('模板',template['schema'])
    slots=list(b.real_calendar_slots())
    rng.shuffle(slots)  # Choose before checking ANY outcome or grade.
    seen=set()
    with tempfile.TemporaryDirectory(prefix='wengua_bigfish_v11_real_') as d:
        worker=b.BigFishWorker(Path(d))
        try:
            for i,(label,relationship) in enumerate(THREE,1):
                failures=[]
                b.RELATIONSHIP=relationship
                b.PATIENT_SEX=None
                b.PATIENT_RELATIVE_AGE=None
                b.BIRTH_ORDER=None
                b.PATIENT_BIRTH_GANZHI=None
                inquiry=b.build_inquiry(b.validate_actor_settings(b.actor_catalog()))
                for slot in slots[(i-1)*90:i*90]:
                    if slot['instant'] in seen:
                        continue
                    seen.add(slot['instant'])
                    result=b.real_case_from_slot(worker,slot,inquiry)
                    if result['status'].startswith('失败'):
                        failures.append({'instant':slot['instant'],
                                         'error':result.get('error','')})
                        continue
                    if not result['status'].startswith('原始断词'):
                        failures.append({'instant':slot['instant'],
                                         'error':result.get('status')})
                        continue
                    break
                else:
                    print('保留失败清单:',json.dumps(failures,ensure_ascii=False))
                    raise RuntimeError(label+'：90个预抽真实时辰均失败，禁止冒充BigFish成功')

                receipt=result['calendar_receipt']
                front=result['first_page']
                assert front['grade']==('不凶不吉' if result['grade']=='微恙' else result['grade'])
                assert front['source_review_sha256']==b.sha_text(
                    next(x['text'] for x in result['sections'] if x['id']=='90_review'))
                assert len(result['sections'])>=8
                print('\n'+'='*64)
                print(f'V11 BigFish {i}/3 {label} 真实时刻 {slot["instant"]}')
                print('四柱 '+' '.join(receipt['four_pillars'][k] for k in ('year','month','day','hour')))
                print('真实节气 '+receipt['active_solar_term']+' | BigFish真盘 '+result['bureau']+
                      ' | 物理盘 '+result['base_id'])
                print('患者角色 '+relationship+' | 患者年命 未提供不采用')
                print('原始V8十档 '+front['grade']+' | 首页正文 '+str(front['character_count'])+'字')
                print('\n【第一页 · 专业解卦（同Swift短断语）】')
                print(front['display_text'])
                print('\n【第二页 · 专业解盘（全部原始章节，逐一保留）】')
                for ix,sec in enumerate(result['sections'],1):
                    print(f'\n{ix:02d} {sec["title"]} [{sec["id"]}]')
                    print(sec['text'])
                print('BigFish与人物源SHA '+result['source_fact_lock']['bigfish_source_sha']+
                      ' / '+result['source_fact_lock']['wengua_source_sha'])
                print('失败真实时辰 '+json.dumps(failures,ensure_ascii=False))
                print('本样本仅为原著规则技术演示，不是临床疗效或真实预后结论。')
        finally:
            worker.close()

if __name__=='__main__':
    main()
