"""Two user-selected raw Zhuanpan charts for interpretation WITHOUT V8 scores."""
import json,argparse
from pathlib import Path
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau

def produce():
    out=[]
    for iso in ("2026-10-28T06:00:00-04:00","2026-10-28T10:00:00-04:00"):
        c=solar_chart_clock(iso,"America/New_York")
        p=c["four_pillars"]
        b=bureau_for_term(p["day"],c["active_solar_term"])
        board=layout_from_explicit_bureau(dun=b["dun"],ju=b["ju"],hour_ganzhi=p["hour"])
        assert len(board["palaces"])==9
        assert board["palaces"]["5"]["door"] is None
        out.append(dict(instant=iso,solar_term=c["active_solar_term"],four_pillars=p,
                        bureau=b,palaces=board["palaces"],xun_shou=board["xun_shou"]))
    return {"no_scores":True,"no_template":True,"charts":out}
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True)
    args=a.parse_args()
    result=produce()
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    for c in result["charts"]:
        print("RAW_CHART",c["instant"],json.dumps(c,ensure_ascii=False))
