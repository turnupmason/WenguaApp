"""Recovery end-to-end, source exceptions, timezone periods and frozen isolation."""
import copy
from datetime import datetime,timedelta
import hashlib,json
from pathlib import Path
import unittest
from src.wengua.health_recovery_v3 import (load_runtime,calendar_periods,role_method,analyze_recovery,
    auto_cast_health_recovery_text,facts_from_assessment)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ROOT=Path(__file__).resolve().parents[1]
GOOD='2026-10-27T05:00:00-04:00'
BAD='2026-11-10T04:00:00-05:00'
ZONE='America/New_York'
INQUIRY={'intent':'recovery','relationship':'self','consultation_context':'direct_self'}


def synthetic_role(id='patient',palace=3,carrier='乙',earth='丙',void='not_void',vb=None,horse=None,tombs=None):
    return {'id':id,'palace':palace,'symbol':carrier,'carrier':carrier,'earth_stem':earth,
            'void_state':void,'void_branches':vb or [],'horse_branch':horse,'tomb_branches':tombs or []}

class RecoverySourceMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.runtime=load_runtime();cls.facts={'fuyin':False,'fanyin':False}
    def method(self,role):return role_method(role,self.facts,self.runtime)
    def test_void_uses_only_role_branches_and_flow_ambiguity_is_preserved(self):
        m=self.method(synthetic_role(void='true_void',vb=['卯'],horse='寅',tombs=['辰']))
        self.assertEqual(m['method'],'void');self.assertEqual(m['branches'],['卯','酉'])
        self.assertEqual(m['status'],'void_flow_unresolved');self.assertEqual(m['stems'],['乙'])
        self.assertEqual(self.method(synthetic_role(void='fake_void',vb=['卯'],horse='寅'))['method'],'horse')
    def test_horse_precedes_tomb_and_applies_only_at_selected_palace(self):
        self.assertEqual(self.method(synthetic_role(horse='寅',tombs=['辰']))['branches'],['寅','申'])
        m=self.method(synthetic_role(tombs=['辰']))
        self.assertEqual((m['method'],m['branches']),('tomb',['戌']))
    def test_ordinary_and_chief_jia_wu_zhen_exceptions_stay_distinct(self):
        normal=self.method(synthetic_role(palace=3,carrier='戊',earth='乙'))
        chief=self.method(synthetic_role(id='chief',palace=3,carrier='戊',earth='乙'))
        self.assertEqual(normal['branches'],['午','戌']);self.assertEqual(chief['branches'],['丑'])
        self.assertIn('T064',normal['rule_ids']);self.assertIn('T085',chief['rule_ids'])
    def test_geng_gen_ordinary_tomb_differs_from_chief_clash(self):
        normal=self.method(synthetic_role(palace=8,carrier='庚',earth='丙'))
        chief=self.method(synthetic_role(id='chief',palace=8,carrier='庚',earth='丙'))
        self.assertEqual((normal['method'],normal['branches']),('tomb',['丑','寅','未','申']))
        self.assertEqual(normal['status'],'tomb_context_conflict')
        self.assertEqual((chief['method'],chief['branches']),('clash',['巳']))
    def test_self_punishment_and_hidden_palace_join(self):
        m=self.method(synthetic_role(palace=7,carrier='辛',earth='辛'))
        self.assertEqual((m['method'],m['branches']),('punishment',['未']))
        m=self.method(synthetic_role(palace=8,carrier='戊',earth='丙'))
        self.assertEqual((m['method'],m['branches']),('combination',['午']))
    def test_coexisting_clash_and_join_is_not_forced_to_earliest_date(self):
        m=self.method(synthetic_role(palace=9,carrier='戊',earth='癸'))
        self.assertEqual(m['status'],'method_conflict')
    def test_sky_earth_clash_preserves_stem_and_branch_alternatives(self):
        m=self.method(synthetic_role(palace=2,carrier='辛',earth='戊'))
        self.assertEqual(m['status'],'stem_branch_alternatives');self.assertEqual(m['stems'],['丙'])
    def test_unrestricted_fuyin_and_fanyin_have_separate_triggers(self):
        r=synthetic_role(palace=3,carrier='乙',earth='丙')
        self.assertEqual(role_method(r,{'fuyin':True,'fanyin':False})['branches'],['酉'])
        self.assertEqual(role_method(r,{'fuyin':False,'fanyin':True})['branches'],['戌'])

class RecoveryCalendar(unittest.TestCase):
    def test_book_day_anchor_and_upcoming_dates(self):
        rows=calendar_periods('1995-06-11T12:00:00+08:00','Asia/Shanghai','day')
        self.assertEqual(rows[0]['ganzhi'],'癸酉');self.assertEqual(rows[1]['ganzhi'],'甲戌')
        self.assertEqual(rows[0]['start_iso'],'1995-06-11T12:00:00+08:00')
        self.assertIn('source_book_day_anchor',rows[0]['calendar_receipt'])
    def test_dst_day_lengths_not_fixed_86400(self):
        for iso,hours in [('2026-03-08T00:00:00-05:00',23),('2026-11-01T00:00:00-04:00',25)]:
            row=calendar_periods(iso,ZONE,'day')[0]
            a,b=[datetime.fromisoformat(row[k]) for k in ('start_iso','end_iso')]
            self.assertEqual((b-a).total_seconds(),hours*3600)
    def test_solar_month_and_year_use_real_jie_instants(self):
        for scale in ('month','year'):
            rows=calendar_periods('2026-11-10T04:00:00-05:00',ZONE,scale)
            self.assertEqual(rows[0]['start_iso'],'2026-11-10T04:00:00-05:00')
            self.assertEqual(rows[0]['ganzhi'],'己亥' if scale=='month' else '丙午')
            end=datetime.fromisoformat(rows[0]['end_iso'])
            self.assertNotEqual((end.day,end.hour,end.minute),(1,0,0))
            self.assertIn('strict',rows[0]['calendar_method'])
    def test_deadline_clips_every_unit_and_no_backdating(self):
        deadline='2026-11-12T10:00:00-05:00'
        for scale in ('day','month','year','hour'):
            rows=calendar_periods(BAD,ZONE,scale,deadline_iso=deadline)
            self.assertTrue(rows)
            for row in rows:
                self.assertGreaterEqual(datetime.fromisoformat(row['start_iso']),datetime.fromisoformat(BAD))
                self.assertLessEqual(datetime.fromisoformat(row['end_iso']),datetime.fromisoformat(deadline))
    def test_hour_uses_five_rat_and_rejects_ambiguous_dst_boundary(self):
        rows=calendar_periods('2026-10-20T05:00:00-04:00',ZONE,'hour')
        self.assertEqual(rows[0]['branch'],'卯')
        self.assertFalse(any(row['branch']=='子' for row in rows))
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            calendar_periods('2026-11-01T00:00:00-04:00',ZONE,'hour')
    def test_naive_offset_mismatch_and_unsupported_solar_coverage(self):
        for iso in ('2026-11-10T04:00:00','2026-11-10T04:00:00+08:00'):
            with self.assertRaises(ValueError):calendar_periods(iso,ZONE,'day')
        with self.assertRaisesRegex(ValueError,'coverage'):
            calendar_periods('2020-01-01T01:00:00-05:00',ZONE,'year')

class RecoveryEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good=auto_cast_health_recovery_text(iso=GOOD,timezone_name=ZONE,inquiry=INQUIRY)
        cls.bad=auto_cast_health_recovery_text(iso=BAD,timezone_name=ZONE,inquiry=INQUIRY)
    def test_real_cast_to_windows_and_all_four_sections(self):
        r=self.good
        self.assertEqual(r['status'],'conditional_scales');self.assertTrue(r['windows'])
        self.assertEqual({w['scale'] for w in r['windows']},{'day','month'})
        self.assertEqual([s['title'] for s in r['sections']],['病愈时间','应期缓急','取期依据','综合断语'])
        self.assertIn('时间单位尚未明确',r['sections'][0]['text'])
        self.assertFalse(r['medical_validity_claimed']);self.assertFalse(r['severity_recalculated'])
        self.assertTrue(all(w['calendar_receipt'] and w['rule_ids'] and w['method_roles'] for w in r['windows']))
    def test_original_random_draw_does_not_gain_invented_cure_date(self):
        self.assertEqual(self.bad['status'],'recovery_premise_unresolved');self.assertEqual(self.bad['windows'],[])
        self.assertIn('伏吟',self.bad['sections'][1]['text'])
    def test_positive_grade_alone_never_supplies_recovery_premise(self):
        f=copy.deepcopy(self.good['facts']);f['controls']=[];f['net_grade']='极大吉'
        r=analyze_recovery(f);self.assertEqual(r['windows'],[])
        self.assertEqual(r['status'],'recovery_premise_unresolved')
    def test_opposing_effective_control_blocks_cure_window(self):
        f=copy.deepcopy(self.good['facts']);f['controls'].append({'role':'patient','direction':'被克','cell':'绝对主克','eligible':True,'attacker':'illness'})
        r=analyze_recovery(f);self.assertEqual(r['status'],'recovery_premise_conflict');self.assertEqual(r['windows'],[])
    def test_alternative_method_dates_are_audit_only(self):
        f=copy.deepcopy(self.good['facts'])
        patient=next(x for x in f['roles'] if x['id']=='patient')
        patient.update(void_state='true_void',void_branches=['午'])
        r=analyze_recovery(f,time_scale='day')
        self.assertEqual(r['status'],'method_conflict');self.assertEqual(r['windows'],[])
        self.assertTrue(r['alternative_windows']);self.assertEqual({w['kind'] for w in r['alternative_windows']},{'branch','stem'})
    def test_actual_other_person_and_role_specific_jia_carrier(self):
        q={'intent':'recovery','relationship':'father','consultation_context':'direct_proxy'}
        r=auto_cast_health_recovery_text(iso='2024-05-28T13:00:00-04:00',timezone_name=ZONE,inquiry=q)
        role=next(x for x in r['facts']['roles'] if x['id']=='patient')
        self.assertEqual(r['four_pillars']['year'],'甲辰');self.assertEqual(role['symbol'],'甲');self.assertEqual(role['carrier'],'壬')
    def test_does_not_change_severity_or_location_sources(self):
        old=json.loads((ROOT/'archives/engineering_patch_20261102/before_recovery_v3/data/releases/health_frozen_20261102.json').read_text())
        changed={'ios/WenguaAppUI/WenguaDesignPreviewApp.swift','ios/WenguaAppUI/WenguaNativeReadingRouter.swift','ios/WenguaAppUI/WenguaPremiumReadingView.swift','ios/WenguaAppUI/project.yml'}
        for item in old['files']:
            if item['path'] not in changed:
                self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['sha256'],item['path'])
    def test_posterior_inputs_and_cached_other_person_are_rejected(self):
        for key in ('actual_outcome','actual_recovery_date','reported_feedback'):
            f=copy.deepcopy(self.good['facts']);f[key]='tomorrow'
            with self.assertRaises(ValueError):analyze_recovery(f)
        report=auto_cast_health_review_text(iso=GOOD,timezone_name=ZONE,inquiry={**INQUIRY,'intent':'severity'})
        with self.assertRaisesRegex(ValueError,'identity receipt'):
            auto_cast_health_recovery_text(iso=GOOD,timezone_name=ZONE,inquiry=INQUIRY,assessment=report)
    def test_app_route_is_enabled_and_uses_runtime_instead_of_drafts(self):
        app=(ROOT/'ios/WenguaAppUI/WenguaDesignPreviewApp.swift').read_text()
        self.assertIn('QuestionTopic(id:"health.recovery",title:"病愈应期",domainTitle:"疾病健康",enabled:true)',app)
        project=(ROOT/'ios/WenguaAppUI/project.yml').read_text()
        self.assertIn('runtime_v3_20261102.json',project);self.assertNotIn('reading_template_v2_user_timing.json',project)
        self.assertIn('reading.topicID=="health.recovery"',(ROOT/'ios/WenguaAppUI/WenguaPremiumReadingView.swift').read_text())
        router=(ROOT/'ios/WenguaAppUI/WenguaNativeReadingRouter.swift').read_text()
        self.assertIn('WenguaNativeRecovery.compose',router)

if __name__=='__main__':unittest.main()
