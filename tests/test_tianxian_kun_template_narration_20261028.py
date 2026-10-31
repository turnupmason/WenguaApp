"""The REAL approved Tianxian/Kun customer copy must be sourced from one JSON.

Synthetic conditions are deterministic language regression inputs, NOT
historic unseen-book or medically validated predictions.
"""
import json
import unittest
from pathlib import Path

from src.wengua.health_macro_facts_vnext import render_first_stage_macro, tianxian_palace_bonus
from src.wengua.health_reading_template_vnext import render, template

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"ios/WenguaAppUI"

def macro_facts(*,tianxian,fuyin=False,fanyin=False):
    return {
        "five_not_encounter":{"triggered":False},
        "tianxian_hour_triggered":tianxian,
        "star_fuyin":fuyin,"door_fuyin":False,
        "fuyin_fanyin":{
            "star":"伏吟" if fuyin else "非伏吟反吟",
            "door":"反吟" if fanyin else "非伏吟反吟",
        },
        "tempo":"mixed" if fuyin and fanyin else
                "slow" if fuyin else "fast" if fanyin else
                "not_assessed_from_fuyin",
    }

class TianxianTemplateActualRoute(unittest.TestCase):
    def test_customer_phrase_is_selected_from_editable_template(self):
        j=template()
        self.assertEqual(j["schema"],"health_severity_user_editable_template_v20261031_v11_full_evidence")
        normal=render_first_stage_macro(macro_facts(tianxian=True))
        slow=render_first_stage_macro(macro_facts(tianxian=True,fuyin=True))
        absent=render_first_stage_macro(macro_facts(tianxian=False,fuyin=True))
        self.assertIn(render("tianxian_regular"),normal)
        self.assertNotIn(render("tianxian_fuyin"),normal)
        self.assertIn(render("tianxian_fuyin"),slow)
        self.assertIn("伏吟主慢",slow)
        self.assertNotIn(render("tianxian_regular"),slow)
        self.assertNotIn(render("tianxian_fuyin"),absent)
        self.assertNotIn(render("tianxian_regular"),absent)
        self.assertEqual(tianxian_palace_bonus(3,triggered=True,fuyin=True),4)
        self.assertEqual(tianxian_palace_bonus(5,triggered=True,fuyin=True),7)

    def test_macro_and_final_evidence_share_source_on_both_engines(self):
        py=(ROOT/"src/wengua/domain_selected_energy_vnext.py").read_text()
        swift=(UI/"WenguaPythonVNextVerbatim.swift").read_text()
        for slot in ("tianxian_regular","tianxian_fuyin",
                     "tianxian_evidence_regular","tianxian_evidence_fuyin"):
            self.assertTrue(render(slot))
            if "evidence" not in slot:
                self.assertIn('"'+slot+'"',swift)
                self.assertIn('"'+slot+'"',(ROOT/"src/wengua/health_macro_facts_vnext.py").read_text())
            else:
                # Historical second-copy text retained but not shown twice.
                self.assertNotIn('render_slot("'+slot+'")',py)
                self.assertNotIn('phrase("'+slot+'")',swift)
            self.assertNotRegex(render(slot),r"\+2|\+4|1\.5|半分|源格|矩阵")
        self.assertIn('fullMacro(chart,review,macros:macros)',swift)
        self.assertNotIn("整盘得吉时扶助",py)
        self.assertNotIn("天显时成立，全局得吉时之助",swift)

    def test_kun_host_sentence_is_real_template_and_only_in_real_kun(self):
        py=(ROOT/"src/wengua/health_palace_detailed_vnext.py").read_text()
        swift=(UI/"WenguaPythonVNextVerbatim.swift").read_text()
        self.assertIn('if detail["palace"]==2:',py)
        self.assertIn('bottom+="、中五寄干"+hosted',py)
        self.assertIn('booktext+="；"+render("kun_host_note")',py)
        self.assertIn('if p.id==2 {',swift)
        self.assertIn('earthDesc+="、中五寄干"+hosted',swift)
        self.assertIn('kunNote=try phrase("kun_host_note")',swift)
        self.assertIn('kunHostNote:kunNote',swift)
        self.assertIn('if p.id==2 {text+=" "+kunHostNote}',swift)
        self.assertIn('两重天地格',render("kun_host_note"))
        self.assertNotIn("+2",render("kun_host_note"))

    def test_template_records_score_policy_without_changing_original_tables(self):
        j=template()
        self.assertIn("FLOOR ONCE",j["final_scoring_v80"]["tianxian_scope"])
        self.assertIn("Kun-2",j["final_scoring_v80"]["kun_centre_earth"])
        self.assertEqual(j["macros"]["overall_resolved"],"综上所述，此病为{grade}。")
        self.assertEqual(j["formation"],"{heaven}加{earth}「{name}」（{polarity}）。古文：{classical_text}；古诀大意：{classical_meaning}；天地盘取象：{imagery}")

if __name__=="__main__":unittest.main()
