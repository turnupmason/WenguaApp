"""Actual 2026-10-28 13:44 palace UI and elder-only source evidence."""
import unittest
from pathlib import Path
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"ios/WenguaAppUI"
ISO="2026-10-28T13:44:00-04:00"
ZONE="America/New_York"

class PalaceSourceUX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui=(UI/"WenguaDesignPreviewApp.swift").read_text()
        cls.power=(UI/"WenguaPalacePowerDetail.swift").read_text()
        cls.engine=(UI/"WenguaNativeVNextEngine.swift").read_text()
        cls.pipeline=(ROOT/"src/wengua/health_text_pipeline_vnext_review.py").read_text()
    def test_one_star_line_two_real_sky_carriers_and_single_earth(self):
        for src in ('Text(index==0 ? pair.0 :',
                    '(pair.0=="天禽" ? "禽" : pair.0)',
                    'starCarriers.reversed().enumerated()',
                    'Text("天")','Text("地")',
                    'accessibilityLabel("天盘星干："'):
            self.assertIn(src,self.ui)
        self.assertNotIn('symbolRow(star.0,kind:"star",stem:star.1,',self.ui)
    def test_each_source_factor_independently_from_real_200(self):
        for src in ("WenguaNativeEnergyBundle.fromBundle()",
                    "WenguaVNextEngine.factor(kind:kind",
                    "WenguaVNextEngine.starMonth(element,month)",
                    "WenguaVNextEngine.normalMonth(element,month)",
                    "WenguaVNextEngine.godTiers",
                    'powerCard("八门")','powerCard("八神")',
                    'powerCard("九星")','powerCard("天盘干")',
                    'powerCard("地盘干")',
                    'stemPower(star.carriedStem,star.stages)',
                    'stemPower(p.earthStem,p.earthStages)',
                    "八神不以月令取旺衰"):
            self.assertIn(src,self.power)
        self.assertIn('Text(line.plane + "盘干：" + line.stem)',self.ui)
        self.assertIn('factCard("宫位属性 · 用神角色",text:roleDescription)',self.ui)
        self.assertNotIn("同宫同事实不得当作两个独立证据",self.ui)
    def test_only_source_selected_elders_receive_qian_kun_evidence(self):
        self.assertIn("let allSelected=personalized",self.engine)
        self.assertNotIn('allSelected.append((tag,cell,cell.heavenStars.first?.star ?? ""))',self.engine)
        self.assertNotIn('relevant_palaces.update((2,6))',self.pipeline)
        cases=(("self","direct_self",None),
               ("colleague","direct_proxy",None),
               ("father","direct_proxy","qian"),
               ("mother","direct_proxy","kun"),
               ("grandfather","direct_proxy","qian"),
               ("grandmother","direct_proxy","kun"))
        for role,context,expected in cases:
            with self.subTest(role=role):
                result=auto_cast_health_review_text(
                    iso=ISO,timezone_name=ZONE,inquiry={
                        "intent":"severity","relationship":role,
                        "consultation_context":context})
                network=result["full_health_role_strength_network"]
                observed=network["qian_kun_auxiliary_observations"]
                if expected is None:
                    self.assertEqual(observed,{})
                    self.assertNotIn("gender",network["nodes"])
                else:
                    self.assertEqual(set(observed),{expected})
                    self.assertEqual(observed[expected]["palace"],
                                     6 if expected=="qian" else 2)
                    self.assertIn("gender",network["nodes"])

if __name__=="__main__":unittest.main()
