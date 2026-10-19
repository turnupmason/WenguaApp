"""Draft-only formation AST tests; no copyrighted raw source or real prediction."""
import json
from pathlib import Path
import tempfile
import unittest

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.formation_candidates import evaluate_candidates
from src.wengua.formation_candidates import _matched

class FormationDraftTests(unittest.TestCase):
    def test_real_source_text_example_matches_but_never_approves(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        r=evaluate_candidates(chart)
        self.assertEqual(r["status"],"draft_review_candidates_only")
        self.assertTrue(r["do_not_publish_as_prediction"])
        # Original source chapter one Yang3 has 癸天盘+丁地盘 in palace 9.
        hits=[x for x in r["matches"] if x["formation_name"]=="螣蛇夭矫"]
        self.assertTrue(any(x["palace"]==9 for x in hits))
        self.assertTrue(all(x["review_status"]=="candidate_match_only_not_approved" for x in r["matches"]))
        self.assertFalse(any("prediction_result" in x for x in r["matches"]))

    def test_no_cross_palace_or_cross_star_unification(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        # Put the 乙+开 evidence in 3, and earth 癸 in 2; none alone
        # supports 龙遁 because 3 is not palace 1 and not earth 癸.
        for r in chart["palaces"].values():
            r["heaven_stars"]=[]
            r["door"]=None
        chart["palaces"]["3"]["heaven_stars"]=[{"star":"天蓬星","carried_stem":"乙"}]
        chart["palaces"]["3"]["door"]="开门"
        chart["palaces"]["3"]["earth_stem"]="戊"
        chart["palaces"]["2"]["earth_stem"]="癸"
        answer=evaluate_candidates(chart)
        self.assertFalse(any(v["formation_name"]=="龙遁" for v in answer["matches"]))

    def test_strict_conditions_and_bad_source(self):
        self.assertTrue(_matched([],{"heaven_stem":"乙"}))
        self.assertTrue(_matched([{"field":"heaven_stem","op":"in","values":["乙","丙"]}],{"heaven_stem":"乙"}))
        self.assertFalse(_matched([{"field":"heaven_stem","op":"eq","value":"癸"}],{"heaven_stem":"乙"}))
        with self.assertRaises(ValueError):
            _matched([{"field":"unsafe","op":"eq","value":"乙"}],{"unsafe":"乙"})
        with self.assertRaises(ValueError):
            evaluate_candidates({"status":"invented"})
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"bad.json"
            f.write_text('{"schema":"bad"}')
            with self.assertRaises(ValueError):
                evaluate_candidates(layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="戊戌"),f)

if __name__=="__main__":
    unittest.main()
