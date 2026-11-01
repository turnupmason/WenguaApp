"""V19 independent location evidence order and genuine family relationship gates."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class V19LocationFamily(unittest.TestCase):
    def test_nine_source_sections_complete(self):
        t=json.loads((ROOT/"data/templates/health_discomfort_v11/native_discomfort_v15.json").read_text())
        self.assertEqual(t["schema"],"wengua_health_discomfort_native_v19_full_source_sequence_20261101")
        self.assertEqual([s["id"] for s in t["sections"]],[
            "01_location","02_injury","03_assist_doors","04_hour","05_person",
            "06_auxiliary","07_formation","08_constraints","09_conclusion"])
        swift=(ROOT/"ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift").read_text()
        rendered=swift.split('let values:[String:String]=[',1)[1].split('let required=',1)[0]
        keys=set(re.findall(r'"([a-z_]+)":',rendered))
        refs=set(re.findall(r'\{([a-z_]+)\}'," ".join(x["text"] for x in t["sections"])))
        self.assertFalse(refs-keys)
        for required in ('sourceStrength("door",d,p)','sourceStrength("star",star.star,p)',
                         '(patientPalace,actorCarrier,patientPower)','(hourPalace,hourStem,hourPower)','tier(injuryPower)',
                         'WenguaVNextEngine.striking[stem]','p.tombs.contains',
                         'formationNames.joined','if illnessVoid=="true_void"',
                         'var candidateSites=originalSites','other.0.id != p.id'):
            self.assertIn(required,swift)
        self.assertNotIn("WenguaVNextEngine.compute(",swift)
        self.assertNotIn("abs(",swift)
    def test_real_family_and_friend_guards(self):
        src=(ROOT/"ios/WenguaAppUI/WenguaNativeActorBinding.swift").read_text()
        ui=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        for tag in ('inquiry.familyRelativeConfirmed==true',
                    'profile.id=="older_sister" && inquiry.birthOrder != "eldest"',
                    'profile.id=="friend"'):
            self.assertIn(tag,src)
        for tag in ('friendRelativeAge','familyRelativeConfirmed',
                    '朋友必须选性别及比自己大或小','亲属辅助宫须确认真实家庭关系'):
            self.assertIn(tag,ui)
        catalog=json.loads((ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json").read_text())
        self.assertTrue(catalog["sibling_identity_policy"]["family_kinship_required"])
        self.assertTrue(catalog["sibling_identity_policy"]["older_sister_requires_eldest_rank"])
        self.assertFalse(catalog["sibling_identity_policy"]["automatic_on_named_relationship"])
    def test_real_native_gate_in_ci(self):
        wf=(ROOT/".github/workflows/ios_v80_xcode_simulator_build.yml").read_text()
        self.assertIn("len(native['sections'])==9",wf)
        self.assertIn("xcodebuild -project",wf)
        self.assertIn("NativeDiscomfortV15Smoke.swift",wf)
if __name__=="__main__":unittest.main()
