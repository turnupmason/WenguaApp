"""Full time-house rotation-domain correctness, not a new V8 scoring table."""
import unittest
from src.wengua.casting_shenqi import (
    DOORS,RING,cycle60,earth_plate,layout_from_explicit_bureau,xun_shou
)
class ValueDoorCentreKun2(unittest.TestCase):
    def test_all_1080_casting_bureau_hour_states(self):
        centre=normal=0
        for dun in ("yang","yin"):
            direction=1 if dun=="yang" else -1
            for ju in range(1,10):
                earth=earth_plate(dun,ju)
                for hour in cycle60():
                    head,steps,hidden=xun_shou(hour)
                    source=next(p for p,s in earth.items() if s==hidden)
                    counted=(source-1+steps*direction)%9+1
                    target=2 if counted==5 else counted
                    chart=layout_from_explicit_bureau(
                        dun=dun,ju=ju,hour_ganzhi=hour)
                    p=chart["palaces"]
                    self.assertEqual(chart["value_door_palace"],target,(dun,ju,hour))
                    self.assertEqual(chart["value_door"],DOORS[2 if source==5 else source])
                    self.assertEqual(p[str(target)]["door"],chart["value_door"])
                    self.assertEqual((p["5"]["door"],p["5"]["deity"],
                                      p["5"]["heaven_stars"]),(None,None,[]))
                    self.assertEqual(set(p[str(i)]["door"] for i in RING),
                                     set(DOORS.values()))
                    self.assertEqual(len([star for palace in p.values()
                                          for star in palace["heaven_stars"]]),9)
                    if counted==5:centre+=1
                    else:normal+=1
        self.assertEqual(centre+normal,1080)
        self.assertEqual(centre,120)
        print(f"ALL 1080 PASS, 120 counted middle 5 -> Kun2; 960 nonmiddle unaffected")
    def test_old_chapter_zero_and_two_nonzero_both_direction(self):
        zero=layout_from_explicit_bureau(dun="yang",ju=5,hour_ganzhi="甲子")
        self.assertEqual((zero["value_star"],zero["value_door"],
                          zero["value_door_palace"]),("天禽星","死门",2))
        for dun,ju,hour,door in [
            ("yang",1,"戊辰","休门"),("yin",1,"己巳","休门"),
            ("yang",2,"丁卯","死门")]:
            chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
            self.assertEqual((chart["value_door"],chart["value_door_palace"]), (door,2))
            self.assertIsNone(chart["palaces"]["5"]["door"])
if __name__=="__main__":unittest.main()
