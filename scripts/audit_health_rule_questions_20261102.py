"""Read-only condition search on real clocks, never blind validation or tuning."""
from collections import defaultdict,Counter
from datetime import datetime,timedelta
import json
import hashlib
from pathlib import Path
from zoneinfo import ZoneInfo
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

OUT=Path('docs/audits/health_cleanup_20261102/rule_questions_observations.json')


def physical_inventory():
    atlas=Path('data/atlas/shijia_zhuanpan_physical_1080_v1.jsonl')
    counts=Counter();examples={}
    for line in atlas.read_text().splitlines():
        row=json.loads(line)
        for p in row['palaces']:
            stars=p.get('heaven_stars',[])
            doctor=any(x['star']=='天心星' for x in stars)
            sky_yi=any(x['carried_stem']=='乙' for x in stars)
            chief=p.get('deity')=='值符'
            flags={'tianxin_sky_yi':doctor and sky_yi,'tianxin_chief':doctor and chief,
                   'sky_yi_chief':sky_yi and chief,'tianxin_sky_yi_chief':doctor and sky_yi and chief,
                   'tianxin_ground_yi_chief':doctor and p['earth_stem']=='乙' and chief}
            for key,matched in flags.items():
                if matched:
                    counts[key]+=1
                    examples.setdefault(key,{'base_id':row['base_id'],'palace':p['palace'],
                        'stars':stars,'earth_stem':p['earth_stem'],'deity':p['deity']})
    counts['tianxin_sky_yi_chief']+=0
    return {'scope':'1080 canonical physical states only; NOT calendar clocks or clinical outcomes',
            'atlas_sha256':hashlib.sha256(atlas.read_bytes()).hexdigest(),
            'counts':dict(counts),'first_examples':examples}

def run():
    start=datetime(2026,1,9,6,tzinfo=ZoneInfo('America/New_York'))
    doc={'mode':'deterministic condition-seeking technical audit; no clinical outcomes or blind-test claim',
         'clocks_attempted':360,'valid_clocks':0,'technical_errors':[], 'conflicting_direction_groups':[],
         'examples':{},'physical_groups_checked':0}
    for slot in range(360):
        instant=(start+timedelta(hours=12*slot)).isoformat()
        try:
            result=auto_cast_health_review_text(iso=instant,timezone_name='America/New_York',
                inquiry={'intent':'severity','relationship':'self','consultation_context':'direct_self'})
        except ValueError as error:
            doc['technical_errors'].append({'iso':instant,'error':str(error)});continue
        doc['valid_clocks']+=1
        net=result['full_health_role_strength_network'];q=net['candidate_five_grade_quantization'];s=q['summary']
        groups=defaultdict(list)
        for role,review in net['role_group_reviews'].items():groups[review['physical_relation_id']].append((role,review))
        for physical,rows in groups.items():
            doc['physical_groups_checked']+=1
            directions={r['direction'] for _,r in rows}&{'favorable','adverse'}
            if len(directions)>1:doc['conflicting_direction_groups'].append({'iso':instant,'physical':physical,'reviews':dict(rows)})
        candidate=[]
        if s['weak_illness_drain_bonus_score']:
            candidate.append('weak_illness_drain_source_threshold_pending')
        special=defaultdict(list)
        for key in ('doctor','medicine','chief'):
            special[net['nodes'][key]['palace']].append(key)
        for pid,keys in special.items():
            actual_hosts={k:v['palace'] for k,v in net['nodes'].items() if k in {'illness','patient','hour','natal','gender','sibling'} and v['palace']==pid}
            if len(keys)>=2 and not actual_hosts:
                candidate.append('cohost_assistants_without_current_eligible_host')
        for _,rows in groups.items():
            if len(rows)>1 and len({r['energy'] for _,r in rows})>1 and len({r['direction'] for _,r in rows})>1:
                candidate.append('same_palace_different_strength_and_effect');break
        for kind in candidate:
            if kind in doc['examples']:continue
            doc['examples'][kind]={'iso':instant,'pillars':result['four_pillars'],
                'nodes':net['nodes'],'reviews':net['role_group_reviews'],
                'control_bonus_palaces':s['control_bonus_palaces'],'control_bonus_points':s['control_bonus_points'],
                'drain_bonus_palaces':s['drain_bonus_palaces'],'weak_illness_drain_bonus_score':s['weak_illness_drain_bonus_score'],
                'auspice_cohost_audit':s['auspice_cohost_audit'],'auspice_bonus_details':s['auspice_bonus_details'],
                'source_nine_palaces':result['nine_palaces']}
    OUT.with_name('physical_combo_inventory.json').write_text(json.dumps(physical_inventory(),ensure_ascii=False,indent=2)+'\n')
    OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in doc.items() if k!='examples'},ensure_ascii=False))
    print('Examples:',list(doc['examples']))

if __name__=='__main__':run()
