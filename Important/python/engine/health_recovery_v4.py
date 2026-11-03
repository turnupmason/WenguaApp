"""Source-led timing convergence. V3 is retained as historical behavior.

Monthly support, scoped hidden-branch relations, executor stems and explicit
source durations constrain one date. Retrospective adverse source replay is
separate from the application's recovery-only route; no feedback is an input.
"""
from datetime import datetime,timedelta
from pathlib import Path
import json
from .health_recovery_v3 import (load_runtime,calendar_periods,facts_from_assessment,
    role_method,FORBIDDEN,_instant)
from .health_lifecycle_v391 import source_full12
from .health_palace_sequence_vnext import element_month_stage
from .semantic_lookup import nine_star_month_status

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/knowledge/health_recovery/runtime_v4_20261103.json'
GENERATES={'木':'火','火':'土','土':'金','金':'水','水':'木'}
CONTROLS={'木':'土','土':'水','水':'火','火':'金','金':'木'}
GROUPS=[set('申子辰'),set('亥卯未'),set('寅午戌'),set('巳酉丑')]

def config():return json.loads(DATA.read_text())
def half_join(a,b):return a!=b and any({a,b}<=g for g in GROUPS)
def fill(s,**fields):
    for k,v in fields.items():s=s.replace('{'+k+'}',str(v))
    if '{' in s or '}' in s:raise ValueError('Incomplete V4 timing phrase')
    return s

def context_from_assessment(a, facts=None):
    r=load_runtime();t=r['tables'];cells=a['nine_palaces'];pp=a['four_pillars']
    door=next(c for c in cells.values() if c['door']==a['chart_facts']['value_door'])
    def stem_role(symbol,gz=None):
        carrier={'甲子':'戊','甲戌':'己','甲申':'庚','甲午':'辛','甲辰':'壬','甲寅':'癸'}.get(gz) if symbol=='甲' else symbol
        found=[c for c in cells.values() if any(s['carried_stem']==carrier for s in c['heaven_stars'])]
        if len(found)!=1:raise ValueError('Timing role requires its own real carrier')
        return {'symbol':symbol,'carrier':carrier,'palace':found[0]['palace'],'earth_stem':found[0]['earth_stem']}
    n=a['full_health_role_strength_network']['nodes'];ill=n['illness']['palace']
    natal=n.get('natal')
    return {'executor':{'palace':door['palace'],'name':door['door'],
                        'sky_stems':[s['carried_stem'] for s in door['heaven_stars']],
                        'sky_sources':[s['star'] for s in door['heaven_stars']],
                        'earth_stem':door['earth_stem']},
            'year':stem_role(pp['year'][0],pp['year']),
            'natal':(next(({'symbol':v['symbol'],'carrier':v['carrier'],'palace':v['palace'],'earth_stem':v['earth_stem']} for v in facts['roles'] if v['id']=='natal'),None) if facts else stem_role(natal['symbol']) if natal and natal['symbol']!='甲' else None),
            'illness_palace':ill,'illness_palace_element':t['palace_elements'][str(ill)],
            'illness_element':'土','month_branch':pp['month'][1]}

def month_facts(context,branch):
    t=load_runtime()['tables'];el=t['branch_elements'][branch];p=context['illness_palace_element']
    return {'month_branch':branch,'palace_stage':element_month_stage(p,el),
            'illness_star_stage':nine_star_month_status('天芮星',el)['value'],
            'palace_controls_star':CONTROLS[p]==context['illness_element']}

def scoped_method(role,facts):
    """Resolve the exact external-hidden-branch/palace join cited by user.

    A sky/earth clash does not erase a separately bound sky/palace join.
    This selects its external branch's clash, never silently combines layers.
    """
    t=load_runtime()['tables'];a=t['hidden'].get(role['carrier']);pb=t['palace_branches'][str(role['palace'])]
    if role['carrier']=='癸' and role['palace']==4 and not role['tomb_branches'] and role['void_state'] in ('not_void','fake_void') and not role['horse_branch']:
        # Both Jia and Gui have no tomb at Chen/Si in the sealed 120-stage
        # table. The notes' bare 'tomb' wording cannot invent a Chen tomb.
        # The independently explicit Yin-Si striking is relieved by Hai join.
        return {'role':role['id'],'palace':4,'method':'punishment','branches':['亥'],'stems':[],
                'rule_ids':['T060','T063','U006'],'status':'selected'}
    if role['void_state'] in ('not_void','fake_void') and not role['horse_branch'] and not role['tomb_branches'] and a and t['join'][a] in pb:
        return {'role':role['id'],'palace':role['palace'],'method':'combination','branches':[t['clash'][a]],'stems':[],
                'rule_ids':['T078','U003'],'status':'selected'}
    return role_method(role,facts)

def month_consensus(context):
    t=load_runtime()['tables'];natal=context.get('natal');year=context['year']
    if not natal:return []
    h=t['hidden'].get(natal['carrier']);yh=t['hidden'].get(year['carrier'])
    if not h or not yh:return []
    if t['join'][h] not in t['palace_branches'][str(natal['palace'])]:return []
    target=t['clash'][h]
    opposing=[b for b in t['palace_branches'][str(year['palace'])] if t['clash'][yh]==b]
    return [target] if any(half_join(target,b) for b in opposing) else []

def constrain_days(periods,facts,*,duration=None,months=None,branches=None,stems=None):
    """One shared month -> duration -> branch -> stem convergence primitive."""
    ref=_instant(facts['reference_iso'],facts['timezone']);result=[]
    for row in periods:
        d=datetime.fromisoformat(row['start_iso'])
        elapsed=(d.date()-ref.date()).days
        if duration and not duration[0]<=elapsed<=duration[1]:continue
        if branches and row['branch'] not in branches:continue
        if stems and row['stem'] not in stems:continue
        if months:
            from .astro_calendar import solar_chart_clock
            noon=d.replace(hour=12,minute=0,second=0,microsecond=0)
            month=solar_chart_clock(noon.isoformat(),facts['timezone'])['four_pillars']['month'][1]
            if month not in months:continue
        result.append(row)
    return result

def source_five_path_replay(facts,context,*,duration=(30,38)):
    """Reconstruct the supplied adverse case, without reading its outcome date.

    Explicit duration is the author's case-specific, post-feedback reasoning;
    it is not inferred as a universal Zhen-palace formula or an initial forecast.
    """
    if FORBIDDEN.intersection(facts):raise ValueError('Feedback not allowed in timing inputs')
    r=load_runtime();t=r['tables'];ref=_instant(facts['reference_iso'],facts['timezone'])
    natal=context.get('natal');year=context['year'];executor=context['executor']
    if not natal:raise ValueError('Source replay requires the actually corrected natal identity')
    hidden=t['hidden'][natal['carrier']];pb=t['palace_branches'][str(natal['palace'])]
    joins=[b for b in pb if t['join'][hidden]==b]
    if not joins:raise ValueError('No source-scoped natal-palace join')
    target=t['clash'][hidden]
    yhidden=t['hidden'][year['carrier']];ypb=t['palace_branches'][str(year['palace'])]
    opposing=[b for b in ypb if t['clash'][yhidden]==b]
    evidence=month_facts(context,target)
    if not(evidence['palace_controls_star'] and evidence['palace_stage']=='死'):
        raise ValueError('Case loss-of-control month not independently reconstructed')
    if not any(half_join(target,b) for b in opposing):raise ValueError('Year half-join does not corroborate month')
    tomb=source_full12()[natal['symbol']]['stage_to_branch']['墓'];day_branch=t['clash'][tomb]
    periods=calendar_periods(facts['reference_iso'],facts['timezone'],'day')
    matched=constrain_days(periods,facts,duration=duration,months=[target],branches=[day_branch],stems=executor['sky_stems'])
    days=[{'date':p['start_iso'][:10],'ganzhi':p['ganzhi'],'elapsed_days':(datetime.fromisoformat(p['start_iso']).date()-ref.date()).days} for p in matched]
    return {'kind':'retrospective_adverse_source_reconstruction_not_recovery_prediction',
            'month_branch':target,'duration_days':list(duration),'duration_is_case_specific':True,
            'natal_hidden_branch':hidden,'natal_palace_join':joins,'year_clash_palace_branches':opposing,
            'year_half_join':True,'natal_tomb_branch':tomb,'day_branch':day_branch,
            'executor_stems':executor['sky_stems'],'executor_stem_sources':executor['sky_sources'],
            'executor_month_stage':element_month_stage(t['palace_elements'][str(t['home_doors'][executor['name']])],t['branch_elements'][context['month_branch']]),
            'case_numbers':[3,8],
            'month_evidence':evidence,'computed_dates':days,'original_exact_date_prediction_made':False}

def analyze_recovery_v4(facts,context,*,duration=None):
    """Compute one supported day; state whether this is recovery or a release.

    Dates come from a real source-scoped trigger. A raw effective control that
    is currently restricted can supply a *release/turning point*, not an
    unconditional cure. The palace's restraint of Tianrui is separately
    audited, and is not equated with successful treatment.
    """
    if FORBIDDEN.intersection(facts):raise ValueError('Feedback forbidden')
    r=load_runtime();c=config();tx=c['text'];t=r['tables'];ref=_instant(facts['reference_iso'],facts['timezone'])
    roles={v['id']:v for v in facts['roles']};executor=context['executor']
    paths=[v for v in facts['controls'] if v['role'] in c['priority'] and v['direction']=='克' and v['attacker']==v['role'] and v['cell'] in t['strong_cells']]
    paths.sort(key=lambda v:(not v['eligible'],c['priority'].index(v['role'])))
    counter=any(v['role']=='patient' and v['direction']=='被克' and v['attacker']=='illness' and v['eligible'] and v['cell'] in t['strong_cells'] for v in facts['controls'])
    methods=[];chosen=None;basis=[];internal=month_facts(context,context['month_branch'])
    if internal['palace_controls_star']:
        basis.append(fill(tx['internal'],palace=c['palaces'][str(context['illness_palace'])],stage=internal['palace_stage'],star_stage=internal['illness_star_stage']))
    coarse=month_consensus(context)
    if coarse:
        adverse=any(month_facts(context,b)['palace_controls_star'] and month_facts(context,b)['palace_stage']=='死' for b in coarse)
        basis.append(fill(tx['coarse_adverse' if adverse else 'coarse'],branches='、'.join(coarse)))
    periods=calendar_periods(facts['reference_iso'],facts['timezone'],'day')
    if duration:
        if set(duration)!={'min_days','max_days','source_ref'} or not duration['source_ref'] or not 0<=duration['min_days']<=duration['max_days']<=59:raise ValueError('Explicit sourced duration required')
        periods=[p for p in periods if duration['min_days']<=(datetime.fromisoformat(p['start_iso']).date()-ref.date()).days<=duration['max_days']]
        basis.append(fill(tx['duration'],a=duration['min_days'],b=duration['max_days']))
    for path in paths:
        role=roles[path['role']];method=scoped_method(role,facts);methods.append(method)
        # Ambiguities without a supplied scoped resolution remain explicit.
        if method['status']!='selected':continue
        if not path['eligible'] and method['method'] in ('growth','fuyin','fanyin'):continue
        coarse=month_consensus(context)
        # A loss of the palace's restraint is counterevidence for recovery,
        # never a positive cure month copied from the adverse source case.
        if coarse and any(month_facts(context,b)['palace_controls_star'] and month_facts(context,b)['palace_stage']=='死' for b in coarse):continue
        candidates=constrain_days(periods,facts,months=coarse,branches=method['branches'])
        patient=roles['patient'];patient_method=scoped_method(patient,facts)
        ready_date=None
        if patient['void_state']=='true_void' or patient['tomb_branches']:
            releases=[p for p in periods if p['branch'] in patient_method['branches']]
            if not releases:continue
            ready_date=releases[0]['start_iso'];candidates=[p for p in candidates if p['start_iso']>=ready_date]
        if not candidates:continue
        # Stem is a refinement after branch, and never creates an impossible
        # Ganzhi or an unbounded stem-only calendar date. All carried stems,
        # including a genuine hosted Tianqin stem, belong to the executor.
        natal_role=roles.get('natal')
        if natal_role and natal_role['tomb_branches']:
            natal_triggers=[t['clash'][b] for b in natal_role['tomb_branches']]
            narrowed=constrain_days(candidates,facts,branches=natal_triggers)
            if narrowed:candidates=narrowed
        stem_matches=constrain_days(candidates,facts,stems=executor['sky_stems'])
        row=(stem_matches or candidates)[0]
        chosen={**row,'support_role':path['role'],'conditional_release':not path['eligible'] or counter,
                'executor_stem_matched':bool(stem_matches),'patient_ready_iso':ready_date}
        basis.append(fill(tx['control'],role=r['text']['role_names'][path['role']],palace=c['palaces'][str(role['palace'])],cell=path['cell']))
        basis.append(fill(tx['method'],method=r['text']['method_names'][method['method']],branches='、'.join(method['branches'])))
        if ready_date:basis.append(fill(tx['patient_ready'],date=human_date(ready_date)))
        if 'U006' in method['rule_ids']:basis.append(tx['verified_striking'])
        if not path['eligible']:basis.append(tx['release_condition'])
        if counter:basis.append(tx['patient_counter'])
        break
    basis.append(fill(tx['executor'],door=executor['name'],palace=c['palaces'][str(executor['palace'])],stems='、'.join(executor['sky_stems'])))
    if chosen and chosen['executor_stem_matched']:basis.append(fill(tx['stem_refinement'],stem=chosen['stem']))
    if not context.get('natal'):basis.append(tx['no_natal'])
    # Year and natal relations are real, separately bound corroboration facts.
    corroboration=[]
    for name,role in [('year',context['year']),('natal',context.get('natal'))]:
        if role is None:continue
        h=t['hidden'].get(role['carrier']);pb=t['palace_branches'][str(role['palace'])]
        if h:
            joins=[x for x in pb if t['join'][h]==x];clashes=[x for x in pb if t['clash'][h]==x]
            corroboration.append({'role':name,'carrier':role['carrier'],'hidden':h,'palace':role['palace'],'joins':joins,'clashes':clashes})
            if joins:basis.append(fill(tx['hidden_join'],role=tx['role_titles'][name],a=h,b='、'.join(joins),target=t['clash'][h]))
            if clashes:basis.append(fill(tx['year_clash'],role=tx['role_titles'][name],a=h,b='、'.join(clashes)))
    if chosen:
        day=human_date(chosen['start_iso']);status='release_day' if chosen['conditional_release'] else 'recovery_day'
        headline=fill(tx[status],date=day,ganzhi=chosen['ganzhi']);summary=headline
    else:
        status='recovery_not_established';headline=tx['no_day'];summary=tx['no_day']
        if not paths:basis.append(tx['no_control'])
        elif methods:basis.append(tx['unresolved_method'])
    pace=('星门伏吟，进展偏慢。' if facts['fuyin'] else '星门反吟，变化较快。' if facts['fanyin'] else '合看本次用神与病情取期。')
    sections=[{'id':i,'title':title,'text':text} for i,title,text in zip(
        ['01_recovery_time','02_pace','03_method','04_summary'],['病愈应期','缓急','取期依据','综合断语'],[headline,pace,'\n\n'.join(basis),summary])]
    return {'version':'health.recovery.V4','topic_id':'health.recovery','status':status,'sections':sections,'selected_day':chosen,
            'methods':methods,'corroboration':corroboration,'internal_restraint':internal,'context':context,
            'uses_reported_outcome':False,'medical_validity_claimed':False}

def human_date(iso):
    d=datetime.fromisoformat(iso);return f'{d.year}年{d.month}月{d.day}日'

def auto_cast_health_recovery_v4(*,iso,timezone_name,inquiry):
    if FORBIDDEN.intersection(inquiry):raise ValueError('Feedback forbidden')
    from .health_text_pipeline_vnext_review import auto_cast_health_review_text
    a=auto_cast_health_review_text(iso=iso,timezone_name=timezone_name,inquiry={**inquiry,'intent':'severity'})
    facts=facts_from_assessment(a,inquiry);context=context_from_assessment(a,facts)
    result=analyze_recovery_v4(facts,context);result['facts']=facts
    result['reading_text']='\n\n'.join(s['title']+'\n'+s['text'] for s in result['sections'])
    return result
