"""Real pinned Wengua actor profile/binder contract + offline BigFish precompute actor inputs.

Does NOT claim all 518400 scenarios are real calendar instants or review-approved.
Keeps V8.0/200/81/V10.2 untouched; tests the Mac research adapter only.
"""
from __future__ import annotations
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1] if Path(__file__).parent.name=='tests' else Path(__file__).resolve().parent
SCRIPT=(ROOT/'scripts/wengua_bigfish_518400_offline_editorial_20261029.py'
        if (ROOT/'scripts/wengua_bigfish_518400_offline_editorial_20261029.py').exists()
        else ROOT/'Wengua_BigFish_518400.py')


def load():
    fake=types.ModuleType('local_batch')
    fake.FROZEN=ROOT/'data/knowledge/phrase_library/health_v20'
    fake.OUTPUT=ROOT/'output'
    fake.BIGFISH_SHA='6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c'
    fake.WENGUA_SHA='0eae7d2b94742939e885938f8603e85c9452d1c3'
    fake.GRADE={i:str(i) for i in range(-5,6)}
    old=sys.modules.get('local_batch')
    sys.modules['local_batch']=fake
    try:
        spec=importlib.util.spec_from_file_location('bigfish_batch_actor_check',str(SCRIPT))
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if old is None:sys.modules.pop('local_batch',None)
        else:sys.modules['local_batch']=old
    return module

M=load()

class RoleNatalRealSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if (ROOT/'src/wengua/health_dynamic_v21.py').exists():
            from src.wengua.casting_shenqi import layout_from_explicit_bureau
            cls.board=layout_from_explicit_bureau(dun='yin',ju=2,hour_ganzhi='己卯')
            cls.calendar={'year_ganzhi':'丙午','month_ganzhi':'戊戌',
                          'day_ganzhi':'乙亥','hour_ganzhi':'己卯','month_branch':'戌'}
        else:
            cls.board=None

    def profile_input(self, relationship,*,sex=None,birth=None,age=None,order=None):
        with patch.object(M,'RELATIONSHIP',relationship),patch.object(M,'PATIENT_SEX',sex),\
             patch.object(M,'PATIENT_BIRTH_GANZHI',birth),patch.object(M,'PATIENT_AGE_BAND',age),\
             patch.object(M,'BIRTH_ORDER',order),patch.object(M,'CONSULTATION_CONTEXT',None):
            profiles=M.actor_catalog() if (ROOT/'data/knowledge/phrase_library/health_v20/actor_profiles.json').exists() else {
                'profiles':[{'id':relationship,'label':relationship,'palaces':[],
                             'references':[{'kind':{'younger_sibling':'casting_month_stem','son':'casting_hour_stem','wife':'spouse_gender_harmony','spouse':'spouse_gender_harmony','self':'day_stem'}.get(relationship,'casting_year_stem'),'source':'test'}]}]}
            validation=M.validate_actor_settings(profiles)
            return M.build_inquiry(validation),validation['reference'],validation['profile']

    def test_22_profiles_loaded_from_frozen_original_json(self):
        if not (ROOT/'data/knowledge/phrase_library/health_v20/actor_profiles.json').exists():self.skipTest('No repository checkout')
        catalog=M.actor_catalog()
        self.assertEqual(len(catalog['profiles']),22)
        self.assertEqual(len({p['id'] for p in catalog['profiles']}),22)
        expectations={'father':'casting_year_stem','mother':'casting_year_stem',
                      'younger_sibling':'casting_month_stem','older_sibling':'casting_month_stem',
                      'self':'day_stem','son':'casting_hour_stem','wife':'spouse_gender_harmony'}
        for relation,kind in expectations.items():
            inquiry,ref,_=self.profile_input(relation)
            self.assertEqual(ref['kind'],kind)
            self.assertEqual(inquiry['relationship'],relation)

    @unittest.skipUnless((ROOT/'src/wengua/health_dynamic_v21.py').exists(),'Real source not available here')
    def test_real_father_mother_younger_sibling_palaces(self):
        for relation,source_stem,kind in (
            ('father','丙','casting_year_stem'),('mother','丙','casting_year_stem'),
            ('younger_sibling','戊','casting_month_stem')):
            inquiry,reference,profile=self.profile_input(relation)
            person=M.verify_actual_role(self.board,inquiry,self.calendar,reference)
            self.assertEqual(person['role_via'],kind)
            self.assertEqual(person['stem'],source_stem)
            self.assertIn(person['palace'],(1,2,3,4,6,7,8,9))
            self.assertFalse(person['natal_active'])
            if relation=='father':self.assertIn(6,person['auxiliary_palaces'])
            if relation=='mother':self.assertIn(2,person['auxiliary_palaces'])

    @unittest.skipUnless((ROOT/'src/wengua/health_dynamic_v21.py').exists(),'Real source not available here')
    def test_real_birth_year_uses_separate_palace_not_cast_year(self):
        inquiry,ref,_=self.profile_input('father',birth='乙丑')
        person=M.verify_actual_role(self.board,inquiry,self.calendar,ref)
        self.assertEqual(person['stem'],'丙')
        self.assertEqual(person['natal_stem'],'乙')
        self.assertTrue(person['natal_active'])
        self.assertIsInstance(person['natal_palace'],int)
        self.assertEqual(person['natal_year'],'乙丑')

    def test_missing_year_and_new_year_isolation(self):
        with tempfile.TemporaryDirectory() as d,patch.object(M.base,'OUTPUT',Path(d)):
            with patch.object(M,'RELATIONSHIP','father'),patch.object(M,'PATIENT_SEX',None),\
                 patch.object(M,'PATIENT_BIRTH_GANZHI',None),\
                 patch.object(M,'PATIENT_AGE_BAND',None),patch.object(M,'BIRTH_ORDER',None),\
                 patch.object(M,'CONSULTATION_CONTEXT',None):
                old=M.actor_output_folder()
            with patch.object(M,'RELATIONSHIP','father'),patch.object(M,'PATIENT_SEX',None),\
                 patch.object(M,'PATIENT_BIRTH_GANZHI','乙丑'),\
                 patch.object(M,'PATIENT_AGE_BAND',None),patch.object(M,'BIRTH_ORDER',None),\
                 patch.object(M,'CONSULTATION_CONTEXT',None):
                new=M.actor_output_folder()
            self.assertNotEqual(old,new)
            self.assertEqual(old,Path(d)/'full_518400'/'father')
            self.assertEqual(new.parent,old)
            self.assertTrue(new.name.startswith('年命_乙丑_'))

    def test_reject_spouse_unknown_sex_and_parent_ambiguous(self):
        for relation in ('spouse','parent'):
            with self.assertRaisesRegex(ValueError,'必须先明确'):
                self.profile_input(relation)
        with self.assertRaisesRegex(ValueError,'性别'):
            self.profile_input('father',sex='female')

    def test_prevent_sibling_incorrect_birth_order_shortcut(self):
        with self.assertRaisesRegex(ValueError,'排行'):
            self.profile_input('younger_sibling',sex='male',order='youngest')
        inquiry,ref,_=self.profile_input('younger_sibling',sex='male',age='young')
        self.assertEqual(ref['kind'],'casting_month_stem')
        self.assertEqual(inquiry['patient_age_band'],'young')

    def test_valid_birth_only_full_60_cycle(self):
        for fake in ('2020','甲','甲丑','庚庚'):
            with self.assertRaisesRegex(ValueError,'六十甲子'):
                self.profile_input('father',birth=fake)

    @unittest.skipUnless((ROOT/'src/wengua/health_dynamic_v21.py').exists(),'Real source not available here')
    def test_known_jia_cross_pillar_unsafe_is_not_false_success(self):
        from src.wengua.casting_shenqi import layout_from_explicit_bureau
        c=layout_from_explicit_bureau(dun='yang',ju=8,hour_ganzhi='甲戌')
        cal={**self.calendar,'year_ganzhi':'甲子','hour_ganzhi':'甲戌'}
        inquiry,ref,_=self.profile_input('father')
        with self.assertRaisesRegex(ValueError,'甲独立寻址'):
            M.verify_actual_role(c,inquiry,cal,ref)

    @unittest.skipUnless((ROOT/'src/wengua/health_dynamic_v21.py').exists(),'Real source not available here')
    def test_real_甲_natal_must_not_borrow_hour_xun(self):
        inquiry,ref,_=self.profile_input('father',birth='甲子')
        with self.assertRaisesRegex(ValueError,'年命为甲'):
            M.verify_actual_role(self.board,inquiry,self.calendar,ref)

if __name__=='__main__':unittest.main(verbosity=2)
