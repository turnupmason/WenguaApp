"""24 actor IDs, 26 V11 configurations: one friend + parent/spouse gender split.

Each actor has own exact role source, four-month date slots, Excel and checkpoint.
No birth Ganzhi, age/sex guesses, alternate event news, V8 retune, or posthoc
approval. The integrated original BigFish TypeScript sample is a SEPARATE CI.
"""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/wengua_bigfish_518400_offline_editorial_20261029.py"

def load():
    stub=types.ModuleType("local_batch")
    stub.FROZEN=ROOT/"data/knowledge/phrase_library/health_v20"
    stub.OUTPUT=ROOT/"output"
    stub.BIGFISH_SHA="6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c"
    stub.WENGUA_SHA="a288d127883157cb2bea96b676d2c86a45c2ab12"
    stub.GRADE={x:str(x) for x in range(-5,6)}
    prev=sys.modules.get("local_batch")
    try:
        sys.modules["local_batch"]=stub
        spec=importlib.util.spec_from_file_location("bigfish_all_roles_test",SCRIPT)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        if prev is not None:sys.modules["local_batch"]=prev
        else:sys.modules.pop("local_batch",None)

M=load()
PROFILES=json.loads((ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json").read_text())

class ActorLoop(unittest.TestCase):
    def test_default_all_24_source_profiles_26_configs(self):
        self.assertEqual(M.RELATIONSHIP,"all")
        self.assertEqual(M.BATCH_MODE,"real_clock")
        self.assertIsNone(M.PATIENT_BIRTH_GANZHI)
        catalog=M.all_signifier_configs(PROFILES)
        self.assertEqual(len(PROFILES["profiles"]),24)
        self.assertEqual(len(catalog),26)
        self.assertEqual({x["relationship"] for x in catalog},
                         {p["id"] for p in PROFILES["profiles"]})
        self.assertEqual(len({(x["relationship"],x["patient_sex"],x["relative_age"])
                               for x in catalog}),26)
        self.assertEqual({(x["patient_sex"],x["relative_age"])
                          for x in catalog if x["relationship"]=="friend"},
                         {("male","older"),("male","younger"),
                          ("female","older"),("female","younger")})
        self.assertEqual([x["patient_sex"] for x in catalog
                          if x["relationship"]=="spouse"],["male","female"])
        self.assertEqual([x["patient_sex"] for x in catalog
                          if x["relationship"]=="parent"],["male","female"])
        self.assertEqual(next(x for x in catalog if x["relationship"]=="self")["context"],
                         "direct_self")
        self.assertTrue(all(x["context"]=="direct_proxy"
                            for x in catalog if x["relationship"]!="self"))
        self.assertTrue(all(x["needs_human_review"] for x in catalog))
        self.assertTrue(any(x["source_status"]=="research_candidate_only" for x in catalog))
    def test_four_distinct_siblings_and_original_composites_preserved(self):
        catalog=M.all_signifier_configs(PROFILES)
        four={"older_brother":"male","older_sister":"female",
              "younger_brother":"male","younger_sister":"female"}
        self.assertEqual({q["relationship"] for q in catalog if q["relationship"] in four},set(four))
        self.assertNotIn("older_sibling",{q["relationship"] for q in catalog})
        self.assertNotIn("younger_sibling",{q["relationship"] for q in catalog})
        self.assertEqual({v["id"] for v in PROFILES["legacy_composite_profiles"]},
                         {"older_sibling","younger_sibling"})
        profiles={x["id"]:x for x in PROFILES["profiles"]}
        for key,sex in four.items():
            with self.subTest(key=key):
                x=profiles[key]
                self.assertEqual(x["references"][0]["kind"],"casting_month_stem")
                self.assertEqual(x["sibling_auxiliary"]["role_sex"],sex)
                self.assertEqual(x["palaces"],[])
                with patch.object(M,"RELATIONSHIP",key),patch.object(M,"PATIENT_SEX",None):
                    self.assertEqual(M.validate_actor_settings(PROFILES)["profile"]["id"],key)
                with patch.object(M,"RELATIONSHIP",key),patch.object(M,"PATIENT_SEX",
                                                                    "female" if sex=="male" else "male"):
                    with self.assertRaisesRegex(ValueError,"性别"):
                        M.validate_actor_settings(PROFILES)
        self.assertEqual([profiles[x]["sibling_auxiliary"]["palace"]
                          for x in four],[3,4,8,7])
    def test_reject_unsupported_blank_or_duplicate_source_profiles(self):
        for catalog in ({"profiles":[]},
                        {"profiles":[PROFILES["profiles"][0],PROFILES["profiles"][0]]},
                        {"profiles":[{"id":"invented","references":[]}]}):
            with self.assertRaises(ValueError):
                M.all_signifier_configs(catalog)
    def test_26_separate_expected_bound_role_sources_validate_without_natal(self):
        for config in M.all_signifier_configs(PROFILES):
            with patch.object(M,"RELATIONSHIP",config["relationship"]),\
                 patch.object(M,"PATIENT_SEX",config["patient_sex"]),\
                 patch.object(M,"PATIENT_RELATIVE_AGE",config["relative_age"]):
                v=M.validate_actor_settings(PROFILES)
                inquiry=M.build_inquiry(v)
                self.assertEqual(v["reference"]["kind"],config["source_kind"])
                self.assertEqual(inquiry["relationship"],config["relationship"])
                self.assertEqual(inquiry.get("relative_age"),config["relative_age"])
                self.assertNotIn("patient_birth_ganzhi",inquiry)
                self.assertNotIn("patient_age_band",inquiry)
                self.assertNotIn("birth_order",inquiry)
                self.assertEqual(inquiry["consultation_context"],config["context"])
    def test_run_dispatch_uses_real_not_abstract_and_rejects_legacy_all(self):
        with patch.object(M,"run_all_real_calendar",return_value="all-real") as all_run:
            self.assertEqual(M.run(),"all-real")
            all_run.assert_called_once_with()
        with patch.object(M,"BATCH_MODE","abstract_518400_legacy"):
            with self.assertRaisesRegex(ValueError,"禁止"):
                M.run()
    def test_parent_spouse_sex_variants_separate_immutable_paths(self):
        with tempfile.TemporaryDirectory() as d,patch.object(M.base,"OUTPUT",Path(d)):
            folders=[]
            for role in ("parent","spouse"):
                for sex in ("male","female"):
                    with patch.object(M,"RELATIONSHIP",role),\
                         patch.object(M,"PATIENT_SEX",sex):
                        zone=M.REAL_TIMEZONE.replace("/","_")
                        root=(M.base.OUTPUT/"real_calendar_20261115_20270315" /
                              M.RELATIONSHIP/zone/"source_v1")
                        condition={"sex":M.PATIENT_SEX,"age":None,
                                   "order":None,"natal":None,"context":None}
                        path=root/("性别_"+sex+"_"+
                                   M.sha_text(M.canonical(condition))[:10])
                        folders.append(path)
            self.assertEqual(len(set(folders)),4)
            self.assertTrue(all("父亲" not in str(p) for p in folders))
    def test_full_loop_calls_each_actor_and_restores_global_state(self):
        plan=M.all_signifier_configs(PROFILES)
        observed=[]
        class Worker:
            def __init__(self,*args):self.closed=False
            def close(self):self.closed=True
        def actual(**kwargs):
            self.assertIsNotNone(kwargs["shared_worker"])
            self.assertEqual(kwargs["installed_manifest"],{"sha":"frozen"})
            self.assertIs(kwargs["catalog"],PROFILES)
            observed.append((M.RELATIONSHIP,M.PATIENT_SEX,M.PATIENT_RELATIVE_AGE,
                             M.PATIENT_BIRTH_GANZHI,M.BIRTH_ORDER))
            return {"status":"completed","new_rows":20,"failures":0}
        originals=(M.RELATIONSHIP,M.PATIENT_SEX)
        with tempfile.TemporaryDirectory() as d,patch.object(M.base,"OUTPUT",Path(d)),\
             patch.object(M,"activate_six_jia_sources"),\
             patch.object(M,"ensure_install",return_value={"sha":"frozen"}) as installer,\
             patch.object(M,"actor_catalog",return_value=PROFILES),\
             patch.object(M,"BigFishWorker",Mock(side_effect=Worker)) as worker,\
             patch.object(M,"run_real_calendar",side_effect=actual):
            M.run_all_real_calendar()
            installer.assert_called_once()
            worker.assert_called_once()
            log=Path(d)/"real_calendar_20261115_20270315"/"_all_profiles_audit"/"每次运行人物用神结果.jsonl"
            events=[json.loads(x) for x in log.read_text(encoding="utf8").splitlines()]
            self.assertEqual(len(events),len(plan))
            self.assertEqual({e["relationship"] for e in events},
                             {p["id"] for p in PROFILES["profiles"]})
            self.assertTrue(all(e["candidate_not_published"] for e in events))
            self.assertEqual(observed,
                             [(x["relationship"],x["patient_sex"],x["relative_age"],None,None)
                              for x in plan])
        self.assertEqual((M.RELATIONSHIP,M.PATIENT_SEX),originals)
    def test_friend_no_demographic_requirement_and_one_config(self):
        with patch.object(M,"RELATIONSHIP","friend"),\
             patch.object(M,"PATIENT_SEX",None),\
             patch.object(M,"PATIENT_RELATIVE_AGE",None):
            result=M.validate_actor_settings(PROFILES)
            self.assertEqual(result["reference"]["kind"],"casting_month_stem")
            inquiry=M.build_inquiry(result)
            self.assertNotIn("patient_sex",inquiry)
            self.assertNotIn("relative_age",inquiry)

    def test_one_failure_recorded_all_others_continue_and_final_not_false_pass(self):
        observed=[]
        class Worker:
            def __init__(self,*args):pass
            def close(self):pass
        def actual(**kwargs):
            observed.append(M.RELATIONSHIP)
            if M.RELATIONSHIP=="father":raise RuntimeError("source error retained")
            return {"status":"completed"}
        with tempfile.TemporaryDirectory() as d,patch.object(M.base,"OUTPUT",Path(d)),\
             patch.object(M,"activate_six_jia_sources"),\
             patch.object(M,"ensure_install",return_value={}),\
             patch.object(M,"actor_catalog",return_value=PROFILES),\
             patch.object(M,"BigFishWorker",Worker),\
             patch.object(M,"run_real_calendar",side_effect=actual):
            with self.assertRaisesRegex(RuntimeError,"1种人物配置"):
                M.run_all_real_calendar()
            log=Path(d)/"real_calendar_20261115_20270315"/"_all_profiles_audit"/"每次运行人物用神结果.jsonl"
            events=[json.loads(x) for x in log.read_text(encoding="utf8").splitlines()]
            self.assertEqual(len(events),26)
            failed=[e for e in events if e["status"]=="FAILED_RETAINED"]
            self.assertEqual(len(failed),1)
            self.assertEqual(failed[0]["relationship"],"father")
            self.assertIn("source error retained",failed[0]["error"])
            self.assertEqual(observed[-1],"son_in_law")
        self.assertEqual(M.RELATIONSHIP,"all")
    def test_all_mode_disallows_global_birth_or_guessed_patient_features(self):
        for option,value in (("PATIENT_BIRTH_GANZHI","甲子"),
                             ("PATIENT_AGE_BAND","young"),
                             ("BIRTH_ORDER","eldest"),
                             ("PATIENT_SEX","male"),
                             ("CONSULTATION_CONTEXT","event_news"),
                             ("PATIENT_RELATIVE_AGE","older")):
            with patch.object(M,option,value):
                with self.assertRaisesRegex(ValueError,"不接受"):
                    M.run_all_real_calendar()

if __name__=="__main__":
    unittest.main()
