"""Exact customer clarity and approved friend routing: existing V8 strength unchanged."""
import json,unittest
from pathlib import Path
from src.wengua.health_reading_template_vnext import template
from src.wengua.health_macro_facts_vnext import tianxian_palace_bonus
from scripts import ios_vnext_three_random_20261026 as samples

ROOT=Path(__file__).resolve().parents[1]
ACTORS=ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json"

class FriendConfirmedConciseV80(unittest.TestCase):
    def test_only_friend_month_stem_user_confirmed(self):
        j=json.loads(ACTORS.read_text(encoding="utf8"))
        friend=next(p for p in j["profiles"] if p["id"]=="friend")
        self.assertEqual(friend["references"][0]["kind"],"casting_month_stem")
        self.assertEqual(friend["references"][0]["status"],
                         "user_explicit_direction_verified_by_actual_chart")
        self.assertEqual(friend["palaces"],[])
        self.assertIn("不因性别",friend["note"])
        self.assertNotIn("research_candidate_only",str(friend))
        self.assertIn("friend",j["event_news_override"]["eligible"])
    def test_original_book_81_preserved_and_internal_scoring_hidden(self):
        j=template()
        self.assertIn("古文：{classical_text}",j["formation"])
        self.assertIn("天地格：{patterns}",j["macros"]["palace_compact"])
        self.assertNotIn("古文",j["macros"]["palace_compact"])
        self.assertIn("五不遇",j["macros"]["macro_five_customer"])
        for x in ("每宫","两分","扣2","+2","矩阵","按用户规则"):
            self.assertNotIn(x,j["macros"]["macro_five_customer"])
        self.assertEqual(tianxian_palace_bonus(5,triggered=True,fuyin=True),7)
    def test_same_clock_friend_python_live_customer_reading(self):
        old=samples.RELATIONS
        try:
            samples.RELATIONS=(("friend","朋友","direct_proxy",None),)
            batch=samples.produce(seed=343710187,count=1)
        finally:
            samples.RELATIONS=old
        c=batch["cases"][0]
        self.assertEqual(c["instant"],"2025-12-28T17:00:00-05:00")
        self.assertEqual(c["four_pillars"],
                         {"year":"乙巳","month":"戊子","day":"辛未","hour":"丁酉"})
        self.assertEqual(c["summary"]["score"],-5)
        self.assertNotIn("natal",c["roles"])
        self.assertEqual(c["auxiliaries"],{})
        text=c["python_reading_text"]
        for bad in ("古文：","古诀大意：","天地盘取象：","长生/冠带/临官",
                    "各实际参与实宫均减两分","按用户规则","加分","矩阵限制"):
            self.assertNotIn(bad,text)
        self.assertIn("戊势",text)
        self.assertIn("「螣蛇相缠」",text)
        self.assertIn("综上所述，此病为极大凶",text)
        self.assertLess(len(text),2100)
        self.assertNotIn("全部因素推断后",text)
if __name__=="__main__":unittest.main()
