"""Regression: user-approved 庚巽四, 巳长生 primary, 辰养 retained (2026-10-31)."""
import unittest
from src.wengua.selected_duel_table_vnext import table_one
from src.wengua.user_domain_matrices_20261023 import STEM_STAGE_ROWS, STEM_POWER, STEM_COLUMNS, raw_cell

class GengXunChangsheng(unittest.TestCase):
    def test_real_two_source_cells_and_current_zi_month(self):
        p=table_one("stem","庚","子",4)
        self.assertEqual({(f["branch"],f["stage"]) for f in p["stem_life_source_facts"]},
                         {("辰","养"),("巳","长生")})
        self.assertEqual(p["stem_life_primary_branch"],"巳")
        self.assertEqual(p["stem_life_primary_stage"],"长生")
        self.assertEqual(p["user_cell_col"],"生月令")
        self.assertEqual(p["user_cell_row"],STEM_STAGE_ROWS["长生"])
        self.assertEqual(p["strength_label"],"大")
        self.assertFalse(p["stem_life_strength_pending"])
        self.assertEqual(p["stem_life_priority_source"],"user_explicit_20261031_geng_xun_only")
        cells={c["row"]:c["strength"] for c in p["stem_life_candidate_cells"]}
        self.assertEqual(len(cells),2)
        self.assertEqual(cells[STEM_STAGE_ROWS["养"]],"中等")
        self.assertEqual(cells[STEM_STAGE_ROWS["长生"]],"大")

    def test_twelve_actual_months_use_source_table_not_constant_big(self):
        for month in "寅卯辰巳午未申酉戌亥子丑":
            with self.subTest(month=month):
                p=table_one("stem","庚",month,4)
                expected=raw_cell(STEM_POWER,STEM_STAGE_ROWS["长生"],p["user_cell_col"],col_order=STEM_COLUMNS)
                self.assertEqual(p["strength_label"],expected)
                self.assertEqual(len(p["stem_life_source_facts"]),2)
                self.assertEqual(len(p["stem_life_candidate_cells"]),2)

    def test_other_stems_in_xun_do_not_automatically_take_max(self):
        for stem in "甲乙丙丁戊己辛壬癸":
            with self.subTest(stem=stem):
                p=table_one("stem",stem,"子",4)
                self.assertIsNone(p["stem_life_priority_source"])
                self.assertEqual(p["stem_life_strength_pending"],
                                 len({v["strength"] for v in p["stem_life_candidate_cells"]})>1)

    def test_swift_and_python_display_contract(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        python=(root/"src/wengua/domain_selected_energy_vnext.py").read_text("utf8")
        swift=(root/"ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift").read_text("utf8")
        engine=(root/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text("utf8")
        self.assertIn('Set(["辰:养","巳:长生"])',engine)
        for s in (python,swift):
            self.assertIn("巳长生主断，辰养并存",s)
            self.assertIn("以巳长生主断，辰养备查",s)
            self.assertNotIn("辰养与巳长生并见，双支原始力量不同",s)

if __name__=="__main__":
    unittest.main()
