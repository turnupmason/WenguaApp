"""V9 real-clock six-case preview; deterministic seed, no fabricated chart.

Each successful real Gregorian instant is independently cast with the current
offline Python engine, actual month JieQi and original BigFish-independent
Wengua nine palace. Failed casts stay in the log, not relabeled or substituted
with an old board; no outcomes used for choosing examples.
"""
from __future__ import annotations
import json
import random
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.astro_calendar import solar_chart_clock

rng=random.Random(903104)
zone=ZoneInfo("America/New_York")
groups=[
 ("哥哥","older_brother",None,None),
 ("姐姐","older_sister",None,None),
 ("弟弟","younger_brother",None,None),
 ("妹妹","younger_sister",None,None),
 ("女性比自己年长的朋友","friend","female","older"),
 ("男性比自己年幼的朋友","friend","male","younger"),
]
for ordinal,(label,role,sex,relative) in enumerate(groups,1):
 inquiry={"intent":"severity","relationship":role,"consultation_context":"direct_proxy"}
 if sex: inquiry["patient_sex"]=sex
 if relative: inquiry["relative_age"]=relative
 failures=[]
 for attempt in range(1,35):
  # Draw before checking any grade or outcome. Only invalid/unsupported casts
  # may be retried; keep all failure sources for independent investigation.
  moment=datetime(2026,11,16,10,30,tzinfo=zone)+timedelta(
      days=rng.randrange(108),hours=rng.randrange(0,9))
  iso=moment.isoformat()
  try:
   result=auto_cast_health_review_text(
       iso=iso,timezone_name="America/New_York",inquiry=inquiry)
  except Exception as err:
   failures.append({"instant":iso,"reason":repr(err)})
   continue
  break
 else:
  print("V90_PREVIEW_UNAVAILABLE "+json.dumps({
      "role":role,"failures":failures},ensure_ascii=False))
  raise RuntimeError("No cast accepted for "+role)
 print("\n"+("="*64))
 print("V9.0 "+str(ordinal)+"/6 "+label+" 真实时刻 "+iso)
 print("实际四柱 "+" ".join(result["four_pillars"][k] for k in ("year","month","day","hour")))
 print("实时节气 "+result["solar_term"]+" | 实际局 "+str(result["bureau"]))
 audit=result["full_health_role_strength_network"]
 nodes=audit["nodes"]
 for kind in ("patient","sibling","illness"):
  row=nodes.get(kind)
  if row: print("用神事实 "+kind+" "+str({k:row.get(k) for k in ("palace","kind","symbol","strength")}))
 for sec in result["sections"]:
  if sec["id"] in ("01_macro","02_illness","05_patient","09a_sibling","90_review","91_timing"):
   print(sec["title"]+"："+sec["text"])
 print("V90_REJECTED_REAL_INSTANTS "+json.dumps(failures,ensure_ascii=False))
