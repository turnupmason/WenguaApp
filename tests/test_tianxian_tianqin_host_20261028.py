"""User-approved six-Jia Tianxian global +4 and Tianqin real earth hosting.

Do not replace immutable original 200/81 source tables or tune old outcomes.
All 10 day stems / six Jia clock pairs, negatives, and exact directed host
source are tested. This is a regression of explicit user instructions, not
independent evidence of clinical reliability.
"""
import unittest
from pathlib import Path
from src.wengua.health_macro_facts_vnext import tianxian_hour, TIANXIAN_HOURS
from src.wengua.health_81_excel_catalog_vnext import for_real_palace

ROOT=Path(__file__).resolve().parents[1]
class TianxianAndTianqinV80(unittest.TestCase):
    def test_exact_six_jia_mapping_all_ten_day_stems(self):
        self.assertEqual(len(TIANXIAN_HOURS),10)
        six=("甲子","甲戌","甲申","甲午","甲辰","甲寅")
        expected={"甲":{"甲子","甲戌"},"己":{"甲子","甲戌"},
                  "乙":{"甲申"},"庚":{"甲申"},
                  "丙":{"甲午"},"辛":{"甲午"},
                  "丁":{"甲辰"},"壬":{"甲辰"},
                  "戊":{"甲寅"},"癸":{"甲寅"}}
        for day,yes in expected.items():
            for hour in six:
                with self.subTest(day=day,hour=hour):
                    self.assertEqual(tianxian_hour(day+"子",hour),hour in yes)
            for hour in ("乙申","癸未","庚子","甲未",""):
                self.assertFalse(tianxian_hour(day+"子",hour))
        self.assertFalse(tianxian_hour("","甲子"))
    def test_single_global_bonus_preserves_palace_factors(self):
        py=(ROOT/"src/wengua/health_quant_overlay_vnext.py").read_text()
        swift=(ROOT/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text()
        self.assertIn('tianxian_bonus=4 if first_stage_macro.get("tianxian_hour_triggered") else 0',py)
        self.assertIn('qualified_bonus-macro_penalty+tianxian_bonus',py)
        self.assertIn('"tianxian_global_final_bonus":tianxian_bonus',py)
        self.assertIn('let finalRaw=known+relationshipBonus-',swift)
        self.assertIn('+(tianxian ? 4 : 0)',swift)
        self.assertIn('tianxianHour(chart.pillars.day,chart.pillars.hour)',swift)
        self.assertNotIn('tianxian ? 4',swift.split('private static func evaluate(')[1].split('private static func')[0])
    def test_tianqin_has_own_source_earth_not_host_duplicate(self):
        palace={"palace":2,"earth_stem":"戊","hosted_centre_earth_stem":"丁",
                "heaven_stars":[{"star":"天芮星","carried_stem":"戊"},
                                {"star":"天禽星","carried_stem":"丁"}]}
        pairs=for_real_palace(palace)
        self.assertEqual([(x["star"],x["heaven"],x["earth"]) for x in pairs],
                         [("天芮星","戊","戊"),("天禽星","丁","丁")])
        self.assertEqual(len({x["fact_id"] for x in pairs}),2)
        self.assertEqual(palace["earth_stem"],"戊")
        with self.assertRaisesRegex(ValueError,"Tianqin lacks real centre"):
            for_real_palace({k:v for k,v in palace.items()
                             if k!="hosted_centre_earth_stem"})
    def test_both_runtime_81_readers_use_real_central_earth_for_tianqin(self):
        bridge=(ROOT/"ios/WenguaAppUI/WenguaHealthTemplateBridge.swift").read_text()
        swift=(ROOT/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text()
        py=(ROOT/"src/wengua/health_palace_detailed_vnext.py").read_text()
        self.assertIn('let bottom=item.star=="天禽星" ?',bridge)
        self.assertIn('(byID[5]?.earthStem ?? "")',bridge)
        self.assertIn('let actualEarth=star.star=="天禽星" ? centreEarth : p.earthStem',swift)
        self.assertIn('let key=star.carriedStem+"|"+actualEarth',swift)
        self.assertIn('hosted_centre_earth_stem=hosted_centre',py)
        self.assertIn('"hosted_centre_earth_stem":hosted_centre',py)
    def test_real_ui_blank_centre_aligned_two_earth_stems_and_help(self):
        ui=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        detail=(ROOT/"ios/WenguaAppUI/WenguaPalacePowerDetail.swift").read_text()
        for snippet in ('if palace.id == 5 {',
                        'Color.clear.frame(maxWidth:.infinity,maxHeight:.infinity)',
                        'var hostedCentreEarthStem: String? = nil',
                        'if let centre=palace.hostedCentreEarthStem',
                        'Text(palace.name+"宫")',
                        'ZStack {',
                        'starCarriers.reversed().enumerated()'):
            self.assertIn(snippet,ui)
        self.assertNotIn('Text("中五").font(',ui.split('struct ProfessionalPalaceTile: View')[1].split('private var accessibleText')[0])
        for snippet in ('"太阴":"隐情、谨慎与筹划"','"天冲星":"行动、冲劲与速度"',
                        'explain(p.deity ?? "",kind:"deity")',
                        'explain(star.star,kind:"star")',
                        'explain(p.door ?? "",kind:"door")'):
            self.assertIn(snippet,detail)
if __name__=="__main__":unittest.main()
