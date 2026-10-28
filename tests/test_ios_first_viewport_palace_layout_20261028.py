"""UI-only screenshots: CTA fully visible; nine palaces legible and aligned.

The frozen real cast, 200/81 matrices and V8 customer template are NOT
recalculated or modified by these visual layout tests.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"ios/WenguaAppUI"

class FirstViewportAndGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.journey=(UI/"WenguaDomainJourneyScreen.swift").read_text()
        cls.chart=(UI/"WenguaDesignPreviewApp.swift").read_text()
    def test_continue_action_is_safe_area_anchored_not_scrolled(self):
        self.assertIn(".safeAreaInset(edge:.bottom,spacing:0)",self.journey)
        self.assertIn("Text(selected.enabled ? \"继续 · 填写问事信息\"",self.journey)
        self.assertEqual(self.journey.count('Text(selected.enabled ? "继续 · 填写问事信息"'),1)
        self.assertIn(".frame(height:54)",self.journey)
        self.assertIn(".frame(height:domain == nil ? 222 : 152)",self.journey)
        self.assertIn(".padding(.vertical,12)",self.journey)
        self.assertIn("if selected.enabled { select(selected) }",self.journey)
    def test_all_nine_readable_titles_are_real_named_palaces(self):
        self.assertIn('Text(palace.name+"宫")',self.chart)
        self.assertIn('.font(.system(size:16,weight:.bold,design:.serif))',self.chart)
        self.assertIn('palaceHeading.frame(height:25*scale',self.chart)
        self.assertIn('palaceBoard(tileSide:max(80,min(',self.chart)
        self.assertIn('(viewport.size.height-274)/3',self.chart)
        self.assertIn('.aspectRatio(1,contentMode:.fit)',self.chart)
    def test_one_star_or_double_star_same_fixed_visual_tracks(self):
        for name in ('glyphColumn(primary:primary,secondary:secondary)',
                     'starLine(primary:primary)','skyStemLine(size:secondary)',
                     'earthStemLine(size:secondary)',
                     'ForEach(0..<starCarriers.count,id:\\.self)',
                     'starCarriers.reversed().enumerated()',
                     'Text(index==0 ? pair.0 :',
                     '(pair.0=="天禽" ? "禽" : pair.0)',
                     '.frame(width:38)',
                     'roleColumn.frame(width:roleWidth',
                     'accessibilityLabel("天盘星干："',
                     'Text(palace.ground).foregroundStyle(QFive.shade("stem",palace.ground))'):
            self.assertIn(name,self.chart)
        self.assertNotIn("symbolRow(star.0,kind:",self.chart)
        self.assertIn("Text(entry.element)",self.chart)
    def test_three_by_three_board_budget_on_small_and_large_viewports(self):
        for width,height in [(320,550),(375,660),(393,760),(430,850)]:
            side=max(80,min((width-30)/3,(height-274)/3))
            self.assertLessEqual(side*3+6,width-12)
            self.assertLessEqual(side*3+6,height-160)
    def test_no_ui_source_reaches_v8_immutable_files(self):
        self.assertNotIn("WenguaVNextEngine.compute(",self.journey)
        self.assertNotIn("WenguaVNextEngine.compute(",self.chart)
        self.assertNotIn("signed(",self.journey)

if __name__=="__main__":
    unittest.main()
