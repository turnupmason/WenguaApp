"""Real compiled BigFish TypeScript -> actual Wengua frozen V8/V10.2 role+birth audit.

This is a 4-case smoke, NOT full 518400 validation or medical prediction.
The research candidate source gate must not be published to Swift unchanged.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
import tempfile
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1] if Path(__file__).parent.name=='scripts' else Path(__file__).resolve().parent
SOURCE=ROOT/'scripts/wengua_bigfish_518400_offline_editorial_20261029.py'


def load_adapter(compiled:Path):
    base=types.ModuleType('local_batch')
    from scripts.bigfish_local_batch_reference_20261029 import normalize_bigfish
    base.normalize_bigfish=normalize_bigfish
    base.COMPILED=compiled
    base.OUTPUT=Path(tempfile.gettempdir())/'wengua-bigfish-actor-natal-smoke'
    base.FROZEN=ROOT/'data/knowledge/phrase_library/health_v20'
    base.BIGFISH_SHA='6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c'
    base.WENGUA_SHA='0eae7d2b94742939e885938f8603e85c9452d1c3'
    base.GRADE={-5:'极大凶',-4:'大凶',-3:'中凶',-2:'小凶',-1:'极小凶',
                0:'微恙',1:'极小吉',2:'小吉',3:'中吉',4:'大吉',5:'极大吉'}
    sys.modules['local_batch']=base
    spec=importlib.util.spec_from_file_location('actual_bigfish_batch',SOURCE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(compiled:Path):
    script=load_adapter(compiled)
    pillars={'year':'丙午','month':'戊戌','day':'乙亥','hour':'己卯'}
    worker=script.BigFishWorker(script.base.OUTPUT)
    try:
        profiles=script.actor_catalog()
        for relationship,natal in (('father',None),('father','乙丑'),
                                   ('mother','乙丑'),('younger_brother',None)):
            with_name={p['id']:p for p in profiles['profiles']}
            profile=with_name[relationship]
            inquiry={'intent':'severity','relationship':relationship,
                     'consultation_context':'direct_proxy'}
            if natal:inquiry['patient_birth_ganzhi']=natal
            result=script.compute_variant(worker,pillars,'霜降',inquiry)
            if not result.get('text'):
                raise AssertionError('BigFish->V8/V10.2 produced no original text for '+
                                     str((relationship,natal,result.get('error'))))
            lock=result['source_fact_lock']
            binding=lock['person_binding']
            kind=profile['references'][0]['kind']
            assert binding['role_via']==kind,(relationship,kind,binding)
            assert binding['stem']==('戊' if relationship=='younger_brother' else '丙')
            expected_aux=6 if relationship=='father' else 2 if relationship=='mother' else 8 if relationship=='younger_brother' else None
            roles=result['source_fact_lock']['selected_roles']
            assert roles['patient']['palace']==binding['palace']
            if relationship=='younger_brother':
                assert 'gender' not in roles
                assert roles['sibling']['palace']==expected_aux
            else:
                assert ('gender' in roles)==(expected_aux is not None)
                if expected_aux:assert roles['gender']['palace']==expected_aux
            assert binding['natal_active']==bool(natal)
            assert ('natal' in roles)==bool(natal)
            if natal:assert roles['natal']['palace']==binding['natal_palace']
            assert result['score'] in range(-5,6)
            assert result['sections'] and result['original_text_sha256']
            print('REAL_BIGFISH_V80_V102_ACTOR_NATAL_PASS '+json.dumps({
                'relationship':relationship,'natal':natal,
                'physical':result['base_id'],'bureau':result['bureau'],
                'role_via':binding['role_via'],'patient':binding['stem'],
                'patient_palace':binding['palace'],'auxiliary':expected_aux,
                'natal_palace':binding['natal_palace'],'score':result['score'],
                'text_sha256':result['original_text_sha256'],
                'status':'research_candidate_not_app_approved',
            },ensure_ascii=False),flush=True)
    finally:
        worker.close()

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--compiled',type=Path,required=True)
    args=p.parse_args()
    main(args.compiled)
