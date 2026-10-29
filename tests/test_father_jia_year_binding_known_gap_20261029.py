"""Historical father 甲 binding failure retained as a regression (fixed by
explicit user authorization 2026-10-29: source pillar 六甲遁六仪).
Previous failure/audit logs remain preserved; never source hidden stem from
a different column's hour xun. This is not a scored-answer retune.
"""
import unittest

from src.wengua.casting_shenqi import SIX_JIA, layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import bind_patient


class FatherJiaYearIdentityAudit(unittest.TestCase):
    def _role(self, hour):
        chart = layout_from_explicit_bureau(dun="yang", ju=8, hour_ganzhi=hour)
        inquiry = {"intent":"severity", "relationship":"father",
                   "consultation_context":"direct_proxy"}
        calendar = {"year_ganzhi":"甲子", "month_ganzhi":"丙寅",
                    "day_ganzhi":"甲子", "hour_ganzhi":hour}
        return bind_patient(chart, inquiry, calendar)

    @staticmethod
    def _carried(cell):
        return {x["carried_stem"] for x in cell["heaven_stars"]} if cell else set()

    def test_verified_six_jia_table_is_not_person_year_source_proof(self):
        self.assertEqual(SIX_JIA["甲子"], "戊")
        self.assertEqual(SIX_JIA["甲戌"], "己")
        # This table establishes six-instrument identities; alone it DOES NOT
        # authorize using an hourly xun to substitute a casting-year role.

    def test_first_case_hour_jiazi_happens_to_resolve_as_wu(self):
        role = self._role("甲子")
        self.assertEqual(role["stem"], "甲")
        self.assertIn("戊", self._carried(role["main_cell"]))

    def test_year_jiazi_role_locatable_when_hour_yichou(self):
        # Workbook row 2: source currently returns None (explicit guard).
        role = self._role("乙丑")
        self.assertIsNotNone(role["main_cell"],
                             "casting-year 甲子 identity must be independently established")

    def test_year_jiazi_identity_not_changed_to_hour_jiaxu_ji(self):
        # Workbook row 11: current code wrongly chooses hour-xun 己 as dad's
        # casting-year 甲; a properly year-sourced identity cannot do that.
        role = self._role("甲戌")
        self.assertIsNotNone(role["main_cell"])
        self.assertIn("戊", self._carried(role["main_cell"]),
                      "甲子 year must not silently inherit 甲戌 hour hidden 己")


if __name__ == "__main__":
    unittest.main()
