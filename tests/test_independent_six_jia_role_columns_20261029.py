"""Authorized independent source pillar 六甲遁六仪 for all four role columns.

Does not change scores or invent natal years; preserves historical fail fixtures.
"""
import unittest
from src.wengua.casting_shenqi import SIX_JIA,layout_from_explicit_bureau
from src.wengua.health_severity_template import _find_heaven_stem
from src.wengua.health_dynamic_v21 import bind_patient
from src.wengua.core import cycle60

class IndependentJiaSource(unittest.TestCase):
    def test_six_jia_x_year_month_day_hour_source_distinct_from_hour_xun(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=8,hour_ganzhi="甲戌")
        for role_col in ("year","month","day","hour"):
            for pillar,carrier in SIX_JIA.items():
                # if sourced from year/month/day, hour MUST NOT remap it
                selected=_find_heaven_stem(chart,"甲",source_ganzhi=pillar)
                self.assertIsNotNone(selected,(role_col,pillar))
                self.assertTrue(any(x["carried_stem"]==carrier for x in selected["heaven_stars"]))
        # Source 甲子 is 戊, even if actual hour 甲戌 hides 己.
        year_cell=_find_heaven_stem(chart,"甲",source_ganzhi="甲子")
        hour_cell=_find_heaven_stem(chart,"甲",source_ganzhi="甲戌")
        self.assertNotEqual(year_cell["palace"],hour_cell["palace"])
    def test_binder_source_own_column_main_stem_preserved(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=8,hour_ganzhi="甲戌")
        forms=[
            ("father","casting_year_stem","year_ganzhi"),
            ("self","day_stem","day_ganzhi"),
            ("younger_sibling","casting_month_stem","month_ganzhi"),
            ("son","casting_hour_stem","hour_ganzhi")]
        for relation,via,col in forms:
            for jia,carrier in SIX_JIA.items():
                calendar=dict(year_ganzhi="甲子",month_ganzhi="丙寅",
                              day_ganzhi="甲子",hour_ganzhi="甲戌")
                if col=="hour_ganzhi":
                    # Actual chart has only one true hour, not an invented hour.
                    if jia!="甲戌": continue
                else: calendar[col]=jia
                inquiry=dict(intent="severity",relationship=relation,
                             consultation_context="direct_self" if relation=="self" else "direct_proxy")
                role=bind_patient(chart,inquiry,calendar)
                self.assertEqual(role["stem"],"甲",(relation,jia))
                self.assertEqual(role["source_ganzhi"],jia)
                self.assertEqual(role["carrier_stem"],carrier)
                self.assertTrue(any(x["carried_stem"]==carrier
                                    for x in role["main_cell"]["heaven_stars"]))
                self.assertIsNone(role["birth_cell"])
    def test_invalid_source_fails_closed(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=8,hour_ganzhi="甲戌")
        for invalid in ("甲丑","甲","乙丑"):
            with self.assertRaises(ValueError):
                _find_heaven_stem(chart,"甲",source_ganzhi=invalid)
    def test_no_birth_year_inferred_from_cast_year(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=8,hour_ganzhi="乙丑")
        inquiry=dict(intent="severity",relationship="father",
                     consultation_context="direct_proxy")
        calendar=dict(year_ganzhi="甲子",month_ganzhi="丙寅",
                      day_ganzhi="甲子",hour_ganzhi="乙丑")
        role=bind_patient(chart,inquiry,calendar)
        self.assertEqual(role["source_ganzhi"],"甲子")
        self.assertIsNone(role["birth_cell"])
        self.assertEqual(role["carrier_stem"],"戊")

if __name__=="__main__":unittest.main()
