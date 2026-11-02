import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/'ios/WenguaAppUI'
class InputHitAreaP8(unittest.TestCase):
 def test_explicit_patch_scope_and_sealed_resources(self):
  old=json.loads((ROOT/'archives/engineering_patch_20261102/before_p8/health_frozen_20261102.json').read_text())
  new=json.loads((ROOT/'archives/engineering_patch_20261102/before_p9/health_frozen_20261102.json').read_text())
  before={x['path']:x['sha256'] for x in old['files']}
  self.assertEqual(old['topics'],new['topics'])
  self.assertEqual({x['path'] for x in new['files'] if x['sha256']!=before[x['path']]},{'ios/WenguaAppUI/'+s for s in ['WenguaDesignPreviewApp.swift','WenguaNativeActorBinding.swift','WenguaSetupPresentation.swift','WenguaPremiumReadingView.swift','WenguaCastTimeView.swift']})
  self.assertTrue(all(len(x['sha256'])==64 for x in new['files']))
 def test_menu_label_owns_entire_hit_target_and_inputs_are_effective(self):
  setup=(UI/'WenguaSetupPresentation.swift').read_text().split('struct WenguaSelectionMenu:')[1]
  label=setup.rsplit('} label: {',1)[1].split('}.buttonStyle(.plain)')[0]
  self.assertIn('.contentShape(Rectangle())',label)
  self.assertIn('.frame(maxWidth:.infinity,minHeight:52',label)
  app=(UI/'WenguaDesignPreviewApp.swift').read_text().split('struct CastSetupScreen:')[1].split('struct TraditionalReadingPreview:')[0]
  for old in ['friendRelativeAge','TextField("例如辛酉','病程（','patientBirthGanzhi.trimmingCharacters']:
   self.assertNotIn(old,app)
  self.assertIn('patientBirthGanzhi:nil',app)
  self.assertIn('relativeAge:nil',app)
  self.assertIn('course:nil',app)
  self.assertIn('WenguaSnakeProgress(progress:',app)
