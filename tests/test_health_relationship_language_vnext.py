"""Truth-conditional patient-facing interpretations of REAL 200-cell controls."""
import unittest
from src.wengua.health_relationship_language_vnext import (
    explain_role_against_illness,explain_selected_role)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

def source(role,relation,outcome,status="matched"):
    return explain_role_against_illness(
        role=role,role_factor={"strength_label":"大"},
        disease_factor={"strength_label":"小"},
        role_palace=3,illness_palace=2,relation=relation,
        actual_edge={"control_status":status,"control_result":outcome})


class NaturalDiseaseRoleInterpretation(unittest.TestCase):
    def test_physician_effective_marginal_failed_not_one_generic_sentence(self):
        good=source("doctor","克","强力主克")
        weak=source("doctor","克","微弱克制")
        bad=source("doctor","克","完全失控")
        self.assertIn("天心医生宫克天芮病宫",good)
        self.assertIn("压制病势",good)
        self.assertIn("缓解病象的机会",good)
        self.assertIn("勉强压制",weak)
        self.assertIn("医生难以发挥制病作用",bad)
        self.assertNotIn("缓解病象的机会",bad)
        self.assertNotEqual(good,weak)
        self.assertNotEqual(weak,bad)
        self.assertIn("实际",weak+"实际")

    def test_chief_god_protects_only_when_control_really_applicable(self):
        good=source("chief","克","极限压制")
        bad=source("chief","克","反侮受损")
        birth=source("patient","克","有效主克")
        hour=source("hour","克","高效克制")
        self.assertIn("值符吉神护持",good)
        self.assertIn("未形成制病之助",bad)
        self.assertIn("患者有力抗病",birth)
        self.assertIn("事体可制病",hour)
        self.assertIn("事体",hour)

    def test_illness_attacks_others_must_not_be_reversed(self):
        forced=source("medicine","被克","绝对主克")
        partial=source("medicine","被克","减力克制")
        self.assertIn("病宫有力克制本方",forced)
        self.assertIn("病宫虽来克本方，但克力有限",partial)
        self.assertIn("本方生扶病宫",source("doctor","生",None))
        self.assertIn("不是主动克病",source("doctor","被生",None))
        self.assertIn("同气相持",source("patient","比和",None))
        self.assertIn("不能虚构两宫的相克",source("hour","同宫",None))
        self.assertIn("不能",source("chief","克",None,status="factor_power_pending"))

    def test_real_caster_selected_roles_have_grounded_prose(self):
        report=auto_cast_health_review_text(
            iso="2025-10-21T03:00:00-04:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"self",
                     "consultation_context":"direct_self"})
        net=report["full_health_role_strength_network"]
        for key in ("doctor","medicine","patient","hour","chief"):
            self.assertIn(key,net["nodes"])
            term={"doctor":"天心医生","medicine":"乙奇医药",
                  "patient":"患者用神","hour":"时干事体",
                  "chief":"值符大吉神"}[key]
            self.assertIn(term,report["reading_text"])
        self.assertIn("克制",report["reading_text"])
        self.assertIn("宫内吉凶能量",report["reading_text"])


if __name__=="__main__":
    unittest.main()
