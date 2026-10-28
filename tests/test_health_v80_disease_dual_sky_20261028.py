"""User-approved Tianrui+Tianqin disease-palace two-source exception.

Synthetic sources (not original book cases): the independently qualifying
乙/丁 sky carriers each receive own exact source 25-cell tier and each
creates its own 81-cell sky/earth formation. Non-health palaces and repeated
roles retain the old single-stem-family rule. Historical verdicts are NEVER
re-labeled as unseen or clinical validation.
"""
from pathlib import Path
import unittest
from src.wengua.health_quant_overlay_vnext import (
    disease_dual_sky_bonus, special_cohost_total,
)

ROOT=Path(__file__).resolve().parents[1]

class DiseaseDualSkySource(unittest.TestCase):
    def test_two_independent_qualified_sky_stars(self):
        source=[("天芮星","乙"),("天禽星","丁")]
        candidates=[(3,"乙奇","天盘"),(3,"丁奇","天盘")]
        self.assertEqual(disease_dual_sky_bonus(source,candidates,True),6)
        self.assertEqual(disease_dual_sky_bonus(
            source,[(2,"乙奇","天盘"),(1,"丁奇","天盘")],True),3)
        self.assertEqual(special_cohost_total(
            3,6,void=True,disease_dual_sky=True),4)
    def test_never_two_for_one_symbol_or_two_roles(self):
        self.assertIsNone(disease_dual_sky_bonus(
            [("天芮星","乙"),("天禽星","乙")],
            [(3,"乙奇","天盘")],True))
        self.assertIsNone(disease_dual_sky_bonus(
            [("天芮星","乙")],
            [(3,"乙奇","天盘"),(3,"乙奇","天盘")],True))
    def test_no_ordinary_palace_or_earth_copy_double(self):
        stars=[("天芮星","乙"),("天禽星","丁")]
        self.assertIsNone(disease_dual_sky_bonus(
            stars,[(3,"乙奇","天盘"),(3,"丁奇","天盘")],False))
        self.assertIsNone(disease_dual_sky_bonus(
            stars,[(3,"乙奇","天盘"),(3,"丁奇","地盘")],True))
        with self.assertRaises(ValueError):
            special_cohost_total(0,6)
    def test_illness_81_scores_two_real_sky_earth_pairs(self):
        py=(ROOT/"src/wengua/health_quant_overlay_vnext.py").read_text()
        swift=(ROOT/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text()
        narration=(ROOT/"ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift").read_text()
        detailed=(ROOT/"src/wengua/health_palace_detailed_vnext.py").read_text()
        self.assertIn('for source_pair in detail["ordered_book_81_pairs"]:',py)
        self.assertIn('for (star,actualEarth) in realPairs {',swift)
        # Original V8 paired both sky carriers against host earth. User
        # explicitly corrected Tianqin to use the real centre-earth host.
        self.assertIn('if p.id==2 && p.heavenStars.count==1',swift)
        self.assertIn('let key=star.carriedStem+"|"+actualEarth',swift)
        self.assertIn('"disease_dual_carrier_81_exception":role=="illness"',py)
        self.assertIn('diseaseDualSky:diseaseDualSky',swift)
        self.assertIn('let accepted=p.heavenStars',narration)
        self.assertIn('let names=formation.sentences.map',narration)
        self.assertIn('book=detail["ordered_book_81_pairs"]',detailed)
        self.assertNotIn('if disease_stem:',detailed)
        self.assertIn('if role=="illness" and entry["name"]!="天芮星"',py)
        self.assertIn('if role=="illness" && star.star != "天芮星" {continue}',swift)
    def test_star_to_carried_stem_visual_owner(self):
        ui=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        self.assertIn('real.heavenStars.map',ui)
        self.assertIn('$0.carriedStem',ui)
        # Updated UI renders one star row, independent sky above earth.
        # Real star-carried-stem identity is retained in accessibility and
        # the detailed source table rather than forced into two star rows.
        self.assertIn('ForEach(0..<starCarriers.count',ui)
        self.assertIn('starCarriers.reversed().enumerated()',ui)
        self.assertIn('accessibilityLabel("天盘星干："',ui)
        self.assertIn('markedStem(pair.element.1,plane:"地盘",size:size)',ui)
        self.assertIn('symbolRow(palace.door,kind:"door",stem:""',ui)
        self.assertNotIn('symbolRow(palace.deity,kind:"deity",stem:palace.sky',ui)

if __name__=="__main__":
    unittest.main()
