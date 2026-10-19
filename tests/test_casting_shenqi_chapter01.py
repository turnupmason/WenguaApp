"""Shenqi chapter casting: compare ALL 9 palaces of both supplied worked charts.

They are checks against user's textual reproduction, NOT independent scan or
calendar confirmation. No fixed lucky/unlucky interpretation is asserted.
"""
import unittest
from src.wengua.casting_shenqi import (
    bureau_for_term,cycle60,earth_plate,hour_branch_from_wall_clock,
    hour_ganzhi_from_day,layout_from_explicit_bureau,xun_shou,TERMS,
    YANG_TERMS,YIN_TERMS
)

# source chapter first completed worked diagram (text table + steps)
YANG_3 = {
    1:("丙","景门","白虎",(("天芮星","乙"),("天禽星","庚"))),
    2:("乙","生门","螣蛇",(("天冲星","戊"),)),
    3:("戊","惊门","九地",(("天心星","辛"),)),
    4:("己","开门","九天",(("天蓬星","丙"),)),
    5:("庚",None,None,()),
    6:("辛","杜门","六合",(("天英星","丁"),)),
    7:("壬","伤门","太阴",(("天辅星","己"),)),
    8:("癸","死门","玄武",(("天柱星","壬"),)),
    9:("丁","休门","值符",(("天任星","癸"),)),
}
# source chapter second worked diagram: original image OCR was rearranged from prose
YIN_8 = {
    1:("丙","死门","螣蛇",(("天英星","乙"),)),
    2:("丁","伤门","白虎",(("天任星","戊"),)),
    3:("癸","开门","九天",(("天柱星","己"),)),
    4:("壬","休门","九地",(("天心星","庚"),)),
    5:("辛",None,None,()),
    6:("庚","景门","太阴",(("天辅星","壬"),)),
    7:("己","杜门","六合",(("天冲星","癸"),)),
    8:("戊","惊门","值符",(("天芮星","丁"),("天禽星","辛"))),
    9:("乙","生门","玄武",(("天蓬星","丙"),)),
}

class OriginalChapterTests(unittest.TestCase):
    def test_all_24_term_bureau_groups(self):
        self.assertEqual(len(TERMS),24)
        self.assertEqual(len(YANG_TERMS),12)
        self.assertEqual(len(YIN_TERMS),12)
        self.assertEqual(YANG_TERMS["芒种"],(6,3,9))
        self.assertEqual(YIN_TERMS["立秋"],(2,5,8))
    def test_fu_tou_is_not_current_day_branch(self):
        # 癸酉 itself is 酉, but fu-tou 己巳 is middle yuan.
        a=bureau_for_term("癸酉","芒种")
        self.assertEqual((a["futou"],a["yuan"],a["dun"],a["ju"]),
                         ("己巳","middle","yang",3))
        b=bureau_for_term("丙子","立秋")
        self.assertEqual((b["futou"],b["yuan"],b["dun"],b["ju"]),
                         ("甲戌","lower","yin",8))
        self.assertEqual(a["calendar_status"],"supplied_solar_term_not_independently_checked")
    def test_hour_table_and_five_rat_stems(self):
        for t,branch in [(0,"子"),(1,"丑"),(2,"丑"),(9,"巳"),
                         (20,"戌"),(22,"亥"),(23,"子")]:
            self.assertEqual(hour_branch_from_wall_clock(t),branch)
        self.assertEqual(hour_ganzhi_from_day("癸","巳"),"丁巳")
        self.assertEqual(hour_ganzhi_from_day("丙","戌"),"戊戌")
        for a,b,start in [("甲","己","甲子"),("乙","庚","丙子"),
                          ("丙","辛","戊子"),("丁","壬","庚子"),
                          ("戊","癸","壬子")]:
            self.assertEqual(hour_ganzhi_from_day(a,"子"),start)
            self.assertEqual(hour_ganzhi_from_day(b,"子"),start)
    def test_xun_shou_and_hidden_stem_six_jia(self):
        for hour,head,hidden in [("乙亥","甲戌","己"),
                                  ("辛亥","甲辰","壬"),
                                  ("戊戌","甲午","辛"),
                                  ("丁巳","甲寅","癸")]:
            self.assertEqual(xun_shou(hour)[::2],(head,hidden))
    def test_earth_yang_and_yin(self):
        self.assertEqual(earth_plate("yang",3),{3:"戊",4:"己",5:"庚",
             6:"辛",7:"壬",8:"癸",9:"丁",1:"丙",2:"乙"})
        self.assertEqual(earth_plate("yin",8),{8:"戊",7:"己",6:"庚",
             5:"辛",4:"壬",3:"癸",2:"丁",1:"丙",9:"乙"})
    def assert_chart(self,chart,expected):
        self.assertEqual(len(chart["palaces"]),9)
        for p, (stem,door,deity,heavens) in expected.items():
            row=chart["palaces"][str(p)]
            with self.subTest(palace=p):
                self.assertEqual(row["earth_stem"],stem)
                self.assertEqual(row["door"],door)
                self.assertEqual(row["deity"],deity)
                self.assertEqual(set((s["star"],s["carried_stem"])
                                     for s in row["heaven_stars"]),set(heavens))
        self.assertEqual(chart["status"],"source_text_consistency_only")
    def test_example_1995_06_11_complete_all_palaces(self):
        a=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        self.assertEqual((a["xun_shou"],a["hidden_stem"],a["xun_start_palace"]),
                         ("甲寅","癸",8))
        self.assertEqual((a["value_star"],a["value_star_palace"],
                          a["value_door"],a["value_door_palace"]),
                         ("天任星",9,"生门",2))
        self.assert_chart(a,YANG_3)
    def test_example_1995_08_13_complete_all_palaces(self):
        a=layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="戊戌")
        self.assertEqual((a["xun_shou"],a["hidden_stem"],a["xun_start_palace"]),
                         ("甲午","辛",5))
        self.assertEqual((a["value_star"],a["value_star_palace"],
                          a["value_door"],a["value_door_palace"]),
                         ("天禽星",8,"死门",1))
        self.assert_chart(a,YIN_8)
    def test_additional_hand_example_value_star_and_door(self):
        a=layout_from_explicit_bureau(dun="yang",ju=2,hour_ganzhi="壬戌")
        self.assertEqual((a["xun_shou"],a["hidden_stem"],a["xun_start_palace"]),
                         ("甲寅","癸",7))
        self.assertEqual((a["value_star"],a["value_star_palace"],
                          a["value_door"],a["value_door_palace"]),
                         ("天柱星",6,"惊门",6))
    def test_hour_and_term_are_not_silently_inferred(self):
        with self.assertRaises(ValueError):
            bureau_for_term("癸酉","not-a-real-term")
        with self.assertRaises(ValueError):
            layout_from_explicit_bureau(dun="yang",ju=0,hour_ganzhi="丁巳")
        with self.assertRaises(ValueError):
            layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="fake")
        with self.assertRaises(ValueError):
            hour_branch_from_wall_clock(24)
    def test_middle_door_placement_is_blocked_until_method_resolved(self):
        # At 戊辰 hour, 甲子旬's value door reaches palace 5 for 阳1.
        # Avoid assuming that a door may sit in the unhosted centre.
        with self.assertRaisesRegex(ValueError,"centre 5"):
            layout_from_explicit_bureau(dun="yang",ju=1,hour_ganzhi="戊辰")

if __name__=="__main__":
    unittest.main()
