"""Offline recovery timing: frozen health facts -> source-scoped methods -> calendar.

This module reuses V9/V11 patient binding and control evidence. It does not
rescore severity, infer medical recovery from the net grade, or read feedback.
All computed windows are conditional traditional interpretations, not clinical
predictions. Ambiguous methods retain their alternatives without a cure date.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone, date
from pathlib import Path
from zoneinfo import ZoneInfo
from bisect import bisect_right
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
RESOURCE = ROOT / 'data/knowledge/health_recovery/runtime_v3_20261102.json'
FORBIDDEN = {'actual_outcome','reported_feedback','actual_recovery_date',
             'actual_discharge_date','book_outcome','posterior_diagnosis'}


def load_runtime():
    data = json.loads(RESOURCE.read_text())
    if data['schema'] != 'wengua_health_recovery_runtime_v3':
        raise ValueError('Wrong recovery runtime version')
    return data


def _iso(dt):
    return dt.isoformat(timespec='seconds') if not dt.microsecond else dt.isoformat(timespec='milliseconds')


def _instant(value, zone):
    d = datetime.fromisoformat(value)
    if d.tzinfo is None:
        raise ValueError('Explicit timezone offset required')
    local = d.astimezone(ZoneInfo(zone))
    if local.replace(tzinfo=None) != d.replace(tzinfo=None) or local.utcoffset() != d.utcoffset():
        raise ValueError('Civil instant and IANA timezone disagree')
    return local


def calendar_periods(reference_iso, zone, scale, runtime=None, deadline_iso=None):
    """Civil days, non-Zi two-hour periods, strict Jie months and LiChun years.

    Current periods are explicitly clipped to the remaining future portion.
    A declared deadline clips *every* interval, never silently extends it. The
    machine search horizon is an engineering cap, not the event's validity.
    DST days retain 23/25 actual hours; ambiguous/nonexistent hour boundaries
    are rejected. 23h/Zi rollover remains unavailable instead of invented.
    """
    r = runtime or load_runtime()
    if scale not in r['policy']['horizons']:
        raise ValueError('Unsupported time unit')
    local = _instant(reference_iso, zone)
    if not 1850 <= local.year <= 2150:
        raise ValueError('Calendar year outside tested range')
    start_utc = local.astimezone(timezone.utc)
    horizon = (local + timedelta(days=r['policy']['horizons'][scale])).astimezone(timezone.utc)
    if deadline_iso:
        end = _instant(deadline_iso, zone).astimezone(timezone.utc)
        if end <= start_utc:
            raise ValueError('Event deadline must follow the reference instant')
        horizon = min(horizon, end)
    t = r['tables']; rows = []
    def append(begin, end, gz, method):
        a, b = begin.astimezone(timezone.utc), end.astimezone(timezone.utc)
        lo, hi = max(a, start_utc), min(b, horizon)
        if lo >= hi: return
        rows.append({'scale':scale, 'start_iso':_iso(lo.astimezone(ZoneInfo(zone))),
                     'end_iso':_iso(hi.astimezone(ZoneInfo(zone))),
                     'period_start_iso':_iso(begin), 'period_end_iso':_iso(end),
                     'ganzhi':gz, 'branch':gz[1], 'stem':gz[0], 'calendar_method':method,
                     'calendar_receipt':method+'|'+zone+'|'+_iso(begin)+'|'+_iso(end)+'|'+gz})
    def day_gz(d):
        i = (9 + (d - date(1995,6,11)).days) % 60  # 癸酉 index 9, source book anchor
        return t['stems'][i % 10] + t['branches'][i % 12]
    if scale in ('day','hour'):
        day = local.date()
        while datetime.combine(day, datetime.min.time(), ZoneInfo(zone)).astimezone(timezone.utc) < horizon:
            midnight = datetime.combine(day, datetime.min.time(), ZoneInfo(zone))
            tomorrow = datetime.combine(day+timedelta(days=1), datetime.min.time(), ZoneInfo(zone))
            gz = day_gz(day)
            if scale == 'day':
                append(midnight, tomorrow, gz, 'source_book_day_anchor_civil_midnight_v1')
            else:
                for hour in range(1,23,2):
                    begin = midnight.replace(hour=hour); finish = midnight.replace(hour=hour+2)
                    # Check round trips and reject repeated boundary instants;
                    # a two-hour DST interval with unique endpoints is valid.
                    for point in (begin,finish):
                        back=point.astimezone(timezone.utc).astimezone(ZoneInfo(zone))
                        other=point.replace(fold=1)
                        if back.replace(tzinfo=None)!=point.replace(tzinfo=None) or other.utcoffset()!=point.utcoffset():
                            if finish.astimezone(timezone.utc)>start_utc and begin.astimezone(timezone.utc)<horizon:
                                raise ValueError('Ambiguous or nonexistent local hour boundary')
                    bi=(hour+1)//2
                    start_stem={'甲':0,'己':0,'乙':2,'庚':2,'丙':4,'辛':4,'丁':6,'壬':6,'戊':8,'癸':8}[gz[0]]
                    append(begin,finish,t['stems'][(start_stem+bi)%10]+t['branches'][bi],
                           'source_five_rat_non_zi_hour_v1')
            day += timedelta(days=1)
    else:
        crossings = r['calendar']['crossings_utc_ms']
        terms = [(v,(1+i)%24) for i,v in enumerate(crossings)]
        if scale == 'month': selected=[v for v,i in terms if i%2==1]
        else: selected=[v for v,i in terms if i==3]
        # Require a complete interval containing the reference. Available
        # future intervals may end at table coverage; disclose that cap.
        ms=round(start_utc.timestamp()*1000)
        k=bisect_right(selected,ms)-1
        if k<0 or k+1>=len(selected):
            raise ValueError('Requested solar period outside strict crossing coverage')
        horizon=min(horizon,datetime.fromtimestamp(selected[-1]/1000,timezone.utc))
        for a,b in zip(selected[k:],selected[k+1:]):
            begin=datetime.fromtimestamp(a/1000,timezone.utc).astimezone(ZoneInfo(zone))
            finish=datetime.fromtimestamp(b/1000,timezone.utc).astimezone(ZoneInfo(zone))
            if begin.astimezone(timezone.utc)>=horizon: break
            from .astro_calendar import solar_chart_clock
            # Crossing itself may land at 23h in some zone; sample the same
            # interval a day later at noon to obtain only its year/month GZ.
            sample=(begin+timedelta(days=1)).replace(hour=12,minute=0,second=0,microsecond=0)
            clock=solar_chart_clock(sample.isoformat(),zone)
            append(begin,finish,clock['four_pillars'][scale],r['calendar']['method'])
    return rows


def facts_from_assessment(assessment, inquiry=None):
    """Project actual frozen analysis; no second health interpretation."""
    n=assessment['full_health_role_strength_network'];q=n['candidate_five_grade_quantization']
    r=load_runtime();roles=[]
    for key,node in n['nodes'].items():
        if key not in r['policy']['support_roles']+['illness']: continue
        p=node['palace'];cell=assessment['nine_palaces'][str(p)]
        conditions=assessment['nine_palace_condition_facts'][str(p)]
        symbol=node['symbol']
        stars=cell['heaven_stars']
        if any(s['star']==symbol for s in stars):
            carrier=next(s['carried_stem'] for s in stars if s['star']==symbol)
        elif key=='chief':
            carrier=next(s['carried_stem'] for s in stars if s['star']==assessment['chart_facts']['value_star'])
        elif symbol=='甲':
            # Exact role binding already determined the palace and source
            # Ganzhi. Its real carrier is exported by the selected node.
            from .casting_shenqi import SIX_JIA
            if key=='hour':carrier=SIX_JIA[assessment['four_pillars']['hour']]
            elif key=='patient' and inquiry:
                from .health_dynamic_v21 import bind_patient
                from .casting_shenqi import layout_from_explicit_bureau
                board=layout_from_explicit_bureau(dun=assessment['bureau']['dun'],ju=assessment['bureau']['ju'],hour_ganzhi=assessment['four_pillars']['hour'])
                pp=assessment['four_pillars']
                bound=bind_patient(board,inquiry,{k+'_ganzhi':v for k,v in pp.items()})
                carrier=bound['carrier_stem']
            elif key=='natal' and inquiry:
                carrier=SIX_JIA.get(inquiry.get('patient_birth_ganzhi'))
            else:carrier=None
            if not carrier:raise ValueError('Jia timing role requires its exact frozen binding')
        else: carrier=symbol
        if carrier not in [s['carried_stem'] for s in stars]:
            raise ValueError('Selected timing carrier not in its real palace')
        role_q=q['roles'].get(key) or q['auxiliary_qian_kun'].get(key)
        if not role_q: raise ValueError('Selected role has no frozen void facts')
        tombs=[x['branch'] for x in conditions['sky_tombs'] if x['stem']==carrier]
        roles.append({'id':key,'palace':p,'symbol':symbol,'carrier':carrier,
                      'earth_stem':cell['earth_stem'],
                      'void_state':role_q['palace_score']['void_state'],
                      'void_branches':conditions['void']['void_branches'],
                      'horse_branch':next((b for b in cell.get('branches',[]) if b==assessment['macro_fuyin_fanyin'].get('horse_branch')),None),
                      'tomb_branches':sorted(set(tombs))})
    # Cast facts (including horse) come from the real chart, not narration.
    for role in roles:
        role['void_branches']=list(assessment['nine_palace_condition_facts'][str(role['palace'])]['void']['void_branches'])
        void=assessment['nine_palace_condition_facts'][str(role['palace'])]['void']
        role['horse_branch']=void['horse_branch'] if role['palace']==void['horse_palace'] else None
    controls=[]
    for key,c in n['role_group_reviews'].items():
        controls.append({'role':key,'direction':c['relation'],'cell':c.get('control_result'),
                         'eligible':c.get('control_status')=='matched' and c.get('direction') in ('favorable','adverse'),
                         'attacker':c.get('actual_control_source')})
    return {'reference_iso':assessment['instant'],'timezone':assessment['timezone'],
            'pillars':assessment['four_pillars'],'dun':assessment['bureau']['dun'],
            'fuyin':assessment['macro_fuyin_fanyin']['both_fuyin'],
            'fanyin':assessment['macro_fuyin_fanyin']['both_fanyin'],
            'roles':roles,'controls':controls}


def role_method(role, facts, runtime=None):
    """Return a source-bound branch/stem predicate, including ambiguity states."""
    r=runtime or load_runtime();t=r['tables'];p=role['palace'];c=role['carrier'];e=role['earth_stem']
    pb=t['palace_branches'][str(p)];a=t['hidden'].get(c);b=t['hidden'].get(e)
    clash=bool(a and ((b and t['clash'][a]==b) or t['clash'][a] in pb))
    join=bool(t['stem_join'].get(c)==e or (a and ((b and t['join'][a]==b) or t['join'][a] in pb)))
    punishment_key=c+':'+str(p)
    pun=punishment_key in t['ordinary_punishment'] or (a==b and a in ('辰','午'))
    def out(method,branches,refs,status='selected',stems=None):
        return {'role':role['id'],'palace':p,'method':method,'branches':sorted(set(branches),key=t['branches'].index),
                'stems':stems or [],'rule_ids':refs,'status':status}
    # A chief genuinely participating in an effective control has its own
    # explicit chapter track. Never overwrite ordinary-role special cases.
    if role['id']=='chief':
        if clash and a:return out('clash',[t['join'][a]],['T084','T088'])
        if pun and a:return out('punishment',[t['join'][a]],['T085','T088'])
        if role['void_state']=='true_void':
            return out('void',role['void_branches'],['T086','T088'],'chief_out_xun_requires_time_layer')
    if role['void_state'] not in ('not_void','fake_void','true_void'):
        return out('void',[],['T051'],'void_unknown')
    if role['void_state']=='true_void':
        vb=role['void_branches']
        if not vb:return out('void',[],['T051'],'void_unknown')
        return out('void',vb+[t['clash'][x] for x in vb],['T031','T051','T055'],
                   'void_flow_unresolved',stems=[c])
    if role['horse_branch']:
        h=role['horse_branch'];return out('horse',[h,t['clash'][h]],['T034','T056'])
    tombs=sorted(set(role['tomb_branches']+t['timing_tombs'].get(punishment_key,[])))
    if tombs:return out('tomb',[t['clash'][x] for x in tombs],['T032','T057','T058','T063'])
    if (pun or clash) and join and not (c=='辛' and p==2 and e=='戊'):return out('clash',[],['T060','T074'],'method_conflict')
    if punishment_key in t['ordinary_punishment']:
        return out('punishment',t['ordinary_punishment'][punishment_key],['T060','T064','T065','T066','T067'])
    if a==b and a in ('辰','午'):
        return out('punishment',[t['join'][a]],['T061'])
    if clash:
        participants=[x for x in [a,b]+pb if x and any(t['clash'][x]==y for y in [a,b]+pb if y)]
        branches=[t['join'][x] for x in participants]
        # Source explicitly allows a heavenly-stem join as another track;
        # keep it as a method alternative instead of silently discarding it.
        return out('clash',branches,['T068','T069','T070','T071','T073'],
                   'stem_branch_alternatives' if a and b and t['clash'][a]==b else 'selected',
                   stems=[t['stem_join'][c]] if a and b and t['clash'][a]==b else [])
    if join:
        targets=[]
        if a and t['join'][a] in pb:targets=[t['clash'][a]]
        else:targets=[t['clash'][x] for x in (a,b) if x]
        if not targets:targets=[x for x in t['palace_branches'][str(t['opposite'][str(p)])]]
        return out('combination',targets,['T074','T075','T077','T078'])
    if facts['fuyin']:return out('fuyin',[t['clash'][x] for x in pb],['T080'])
    if facts['fanyin']:return out('fanyin',[t['join'][x] for x in pb],['T081'])
    el=t['star_elements'].get(role['symbol']) or t['stem_elements'].get(role['symbol'])
    if not el:return out('growth',[],['T079'],'growth_need_unknown')
    return out('growth',[x for x in t['branches'] if t['branch_elements'][x]==el],['T028','T079'])


def _fill(text, **fields):
    for k,v in fields.items():text=text.replace('{'+k+'}',str(v))
    if '{' in text or '}' in text: raise ValueError('Unfilled recovery template field')
    return text


def analyze_recovery(facts, *, time_scale=None, deadline_iso=None, runtime=None):
    r=runtime or load_runtime();t=r['tables'];tx=r['text']
    if FORBIDDEN.intersection(facts): raise ValueError('Posterior outcome forbidden')
    _instant(facts['reference_iso'],facts['timezone'])
    roles={x['id']:x for x in facts['roles']}
    if not {'patient','illness','hour'}<=set(roles): raise ValueError('Same-cast patient/event binding required')
    for role in roles.values():
        if str(role['palace']) not in t['palace_branches']: raise ValueError('Timing role must occupy a real exterior palace')
    strong=lambda c: c['eligible'] and c['cell'] in t['strong_cells']
    supporters=[c for c in facts['controls'] if c['role'] in r['policy']['support_roles'] and c['direction']=='克' and c['attacker']==c['role'] and strong(c)]
    counter=[c for c in facts['controls'] if c['role']=='patient' and c['direction']=='被克' and c['attacker']=='illness' and strong(c)]
    supporters.sort(key=lambda c:r['policy']['role_priority'].index(c['role']))
    inner=[1,8,3,4] if facts['dun']=='yang' else [9,2,7,6]
    day_inside=roles['patient']['palace'] in inner;hour_inside=roles['hour']['palace'] in inner
    pace='主迟滞、较慢' if facts['fuyin'] else '主变动、较快' if facts['fanyin'] else '内盘为主、较快' if day_inside and hour_inside else '内外盘交参、较慢'
    pace_text=('星门伏吟，' if facts['fuyin'] else '星门反吟，' if facts['fanyin'] else '')+pace+'。'
    scales=[time_scale] if time_scale else ['day','month']
    if time_scale is not None and time_scale not in r['policy']['horizons']: raise ValueError('Unsupported expected time unit')
    if deadline_iso and _instant(deadline_iso,facts['timezone']) <= _instant(facts['reference_iso'],facts['timezone']):
        raise ValueError('Event deadline must follow the reference instant')
    state='recovery_premise_unresolved';reason=tx['premise_missing'];methods=[];windows=[];alternatives=[];traces=[];precision=[]
    if supporters and counter:state='recovery_premise_conflict';reason=tx['premise_conflict']
    elif supporters:
        state='conditional_windows' if time_scale else 'conditional_scales';reason=''
        patient_method=role_method(roles['patient'],facts,r)
        # Patient readiness is mandatory only for an actual obstructing state;
        # ordinary growth/fuyin does not become an unrelated extra hurdle.
        needs_patient=patient_method['method'] in ('void','horse','tomb','punishment','clash','combination')
        for support in supporters:
            method=role_method(roles[support['role']],facts,r)
            route=[method]
            if needs_patient and support['role']!='patient':route.append(patient_method)
            methods.extend(m for m in route if m not in methods)
            bad=[m for m in route if m['status'] not in ('selected',)]
            if bad:
                for m in bad:
                    alternatives.append(m)
                continue
            for scale in scales:
                try:periods=calendar_periods(facts['reference_iso'],facts['timezone'],scale,r,deadline_iso)
                except ValueError as exc:
                    precision.append({'scale':scale,'reason':str(exc)});continue
                matched=[]
                for period in periods:
                    if all(period['branch'] in m['branches'] for m in route):
                        matched.append({**period,'support_role':support['role'],'method_roles':[m['role'] for m in route],
                                        'rule_ids':sorted(set(x for m in route for x in m['rule_ids']))})
                selected=matched[:r['policy']['maximum_windows_per_scale']]
                windows.extend(w for w in selected if w not in windows)
                traces.append({'support_role':support['role'],'scale':scale,'searched_periods':len(periods),'matching_periods':len(matched),
                               'calendar_end_iso':periods[-1]['end_iso'] if periods else None})
        if not windows:
            if any(m['status']=='method_conflict' for m in alternatives):state='method_conflict';reason=tx['method_conflict']
            elif any(m['status'] in ('void_flow_unresolved','chief_out_xun_requires_time_layer','stem_branch_alternatives') for m in alternatives):state='method_conflict';reason=tx['flow_conflict'] if any(m['status']=='void_flow_unresolved' for m in alternatives) else tx['method_conflict']
            elif precision:state='precision_unavailable';reason=tx['precision_missing']
            else:state='missing_condition';reason=tx['no_candidate']
    # Compute ambiguous alternatives for audit only; never label these cure
    # windows or choose the earliest of unrelated conflicting methods.
    alternative_windows=[]
    for method in alternatives:
        for scale in scales:
            try:periods=calendar_periods(facts['reference_iso'],facts['timezone'],scale,r,deadline_iso)
            except ValueError:continue
            branches=[p for p in periods if p['branch'] in method['branches']][:3]
            stems=[p for p in periods if p['stem'] in method['stems']][:3]
            alternative_windows.extend({'role':method['role'],'kind':kind,**p} for kind,items in [('branch',branches),('stem',stems)] for p in items)
    methods.sort(key=lambda m:(m['role'],m['method']))
    if windows:
        lines=[tx['known_axis'].replace('{unit}',tx['units'][time_scale]) if time_scale else tx['unknown_axis'],_fill(tx['window_zone'],zone=facts['timezone'])]
        for scale in scales:
            group=[w for w in windows if w['scale']==scale]
            unique=[]
            for w in sorted(group,key=lambda w:datetime.fromisoformat(w['start_iso']).timestamp()):
                label=w['start_iso'][:16].replace('T',' ')+' 至 '+w['end_iso'][:16].replace('T',' ')+'（'+w['ganzhi']+tx['units'][scale]+'）'
                if label not in unique:unique.append(label)
            if unique:lines.append(_fill(tx['scale_line'],unit=tx['units'][scale],windows='；'.join(unique[:3])))
        time_text='\n\n'.join(lines);summary=tx['summary']+tx['conditions']
    else:time_text=reason;summary=tx['not_ready_summary']
    basis=[]
    for c in supporters:
        role=roles[c['role']]
        basis.append(_fill(tx['support'],role=tx['role_names'][c['role']],palace=role['palace'],cell=c['cell']))
    for m in methods:
        basis.append(_fill(tx['role_method'],role=tx['role_names'][m['role']],palace=m['palace'],
                           fact=tx['fact_names'][m['method']],method=tx['method_names'][m['method']],
                           branches='、'.join(m['branches']) or '未定'))
    if counter:basis.append(tx['premise_conflict'])
    if alternatives:basis.append('部分取法仍有分歧，未用其候选替代已成立的条件路径。' if windows else reason)
    if not basis:basis.append('现有分析未形成条件完整的制病链，不能仅凭全盘等级套用成功类应期。')
    if precision:basis.append(tx['precision_missing'])
    sections=[{'id':i,'title':title,'text':text} for i,title,text in zip(
        ['01_recovery_time','02_pace','03_method','04_summary'],tx['titles'],[time_text,pace_text,'\n\n'.join(basis),summary])]
    return {'version':r['version'],'topic_id':'health.recovery','status':state,'reference_iso':facts['reference_iso'],
            'timezone':facts['timezone'],'goal':'recovery','time_scale':time_scale,'deadline_iso':deadline_iso,
            'sections':sections,'windows':windows,'methods':methods,'alternative_windows':alternative_windows,
            'support':supporters,'counterevidence':counter,'calendar_search':traces,'precision_limits':precision,
            'source_id':r['source_id'],'source_sha256':r['source_sha256'],
            'runtime_sha256':hashlib.sha256(RESOURCE.read_bytes()).hexdigest(),
            'medical_validity_claimed':False,'conditional_only':True,
            'severity_recalculated':False,'body_location_recalculated':False}


def auto_cast_health_recovery_text(*, iso, timezone_name, inquiry, time_scale=None, deadline_iso=None, assessment=None):
    """Public Python route. Reuse a supplied same-person assessment verbatim."""
    if not isinstance(inquiry,dict) or FORBIDDEN.intersection(inquiry):raise ValueError('Invalid pre-outcome inquiry')
    if inquiry.get('intent') not in ('recovery','severity'):raise ValueError('Recovery intent required')
    if assessment is None:
        from .health_text_pipeline_vnext_review import auto_cast_health_review_text
        assessment=auto_cast_health_review_text(iso=iso,timezone_name=timezone_name,inquiry={**inquiry,'intent':'severity'})
    else:
        if assessment['instant']!=iso or assessment['timezone']!=timezone_name:
            raise ValueError('Cannot reuse another cast or timezone')
        # Bind the exact patient request, never accept somebody else's cached report.
        if assessment.get('recovery_inquiry_identity') != {k:v for k,v in inquiry.items() if k!='intent'}:
            raise ValueError('Cached assessment lacks matching patient identity receipt')
    facts=facts_from_assessment(assessment,inquiry)
    result=analyze_recovery(facts,time_scale=time_scale,deadline_iso=deadline_iso)
    result['facts']=facts
    result['four_pillars']=assessment['four_pillars'];result['bureau']=assessment['bureau']
    result['reading_text']='\n\n'.join(s['title']+'\n'+s['text'] for s in result['sections'])
    return result
