"""Independent Python V19 body-site paragraph composer.

The Swift CLI supplies a JSON-encoded *board*, not its prose or calculated
evidence. Python independently looks up original 200-grid strengths, 81
formations, 255 source entries and selected roles, then renders the same
nine source-templated Chinese sections. This is a cross-language *text/role*
parity test, NOT a clinical diagnosis or V8 severity engine.
"""
from __future__ import annotations
from collections.abc import Mapping
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
PHYSICAL={1,2,3,4,6,7,8,9}
INNER_YANG={1,8,3,4}
INNER_YIN={9,2,7,6}
DIGITS={1:"一",2:"二",3:"三",4:"四",6:"六",7:"七",8:"八",9:"九"}
ELEMENTS={1:"水",2:"土",3:"木",4:"木",6:"金",7:"金",8:"土",9:"火"}
GENERATES={"木":"火","火":"土","土":"金","金":"水","水":"木"}
CONTROLS={"木":"土","土":"水","水":"火","火":"金","金":"木"}
STEM_ELEMENTS=dict(zip("甲乙丙丁戊己庚辛壬癸",["木","木","火","火","土","土","金","金","水","水"]))
STAR_ELEMENTS={"天蓬星":"水","天芮星":"土","天冲星":"木","天辅星":"木",
"天禽星":"土","天心星":"金","天柱星":"金","天任星":"土","天英星":"火"}
DOOR_ELEMENTS=dict(zip(["开门","休门","生门","伤门","杜门","景门","死门","惊门"],
                       ["金","水","土","木","木","火","土","金"]))
STAGES_JIA=dict(zip("亥子丑寅卯辰巳午未申酉戌",
                    ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]))
SIX_JIA={"甲子":"戊","甲戌":"己","甲申":"庚","甲午":"辛","甲辰":"壬","甲寅":"癸"}
STRIKING={"戊":3,"己":2,"庚":8,"辛":9,"壬":4,"癸":4}
CLASH=dict(zip("子丑寅卯辰巳午未申酉戌亥","午未申酉戌亥子丑寅卯辰巳"))
ANCHORS=["肩","耳","臂","手","头","眼","鼻","面","颈","喉",
 "胸","心","肺","脾","肝","胆","胃","肠","肾","腹","腰","腿","足","脚","膝","股",
 "背","筋","骨","皮","肤","膀胱","阴","胰","血管","食道","经络","脑"]
LIMBS=["肩","臂","手","足","腿","背","膝","筋","骨","腰","股"]
TIERS=["极小","小","中等","大","极大"]

def load_sources():
    get=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
    return (get("data/knowledge/health_discomfort/complete_255_rules_v15_20261101.json"),
            get("data/knowledge/health_discomfort/three_source_stem_variants_v14_20261101.json"),
            get("data/templates/health_discomfort_v11/native_discomfort_v15.json"),
            get("data/mobile/health_vnext/health_energy_200.json"),
            (ROOT/"data/knowledge/health_81_excel_20261025/81_pairs.tsv").read_text(encoding="utf-8"))

def _tier(value):
    return TIERS.index(value)+1 if value in TIERS else 0

def _parts(raw):
    bits=raw.replace("／","/").replace("、","/").replace("，","/").split("/")
    result=[]
    for b in bits:
        s=b.strip()
        if s and s not in result and not any(c in s for c in ("病","疾","风","寒","症","虚","咳","疝")):
            result.append(s)
    return result

def _same(a,b):
    return a==b or a in b or b in a or any(k in a and k in b for k in ANCHORS)

def _matched(site,items):
    return any(_same(site,it) for it in items)

def _monthly(branch):
    for element,values in (("木","寅卯"),("火","巳午"),("金","申酉"),("水","亥子"),("土","辰未戌丑")):
        if branch in values:return element
    raise ValueError("Unknown true month branch")

def _directed(symbol,palace):
    if symbol==palace:return "比和"
    if GENERATES[symbol]==palace:return "符号生宫"
    if GENERATES[palace]==symbol:return "宫生符号"
    if CONTROLS[symbol]==palace:return "符号克宫"
    if CONTROLS[palace]==symbol:return "宫克符号"
    raise ValueError((symbol,palace))

def _normal_month(element,month):
    if element==month:return "旺"
    if GENERATES[month]==element:return "相"
    if GENERATES[element]==month:return "休"
    if CONTROLS[element]==month:return "囚"
    if CONTROLS[month]==element:return "死"
    raise ValueError((element,month))

def _star_month(element,month):
    if GENERATES[element]==month:return "旺"
    if element==month:return "相"
    if GENERATES[month]==element:return "废"
    if CONTROLS[element]==month:return "休"
    if CONTROLS[month]==element:return "囚"
    raise ValueError((element,month))

def _power(kind,symbol,p,month,tables,stages=()):
    element=({"star":STAR_ELEMENTS,"door":DOOR_ELEMENTS,"stem":STEM_ELEMENTS}[kind])[symbol]
    palace=ELEMENTS[p["id"]]
    rel=_directed(element,palace)
    if kind=="star":
        row=_star_month(element,month);col=rel
    elif kind=="door":
        row=_normal_month(element,month)
        col={"宫生符号":"被宫生","宫克符号":"宫迫","符号克宫":"门破",
             "符号生宫":"生宫","比和":"比和"}[rel]
    else:
        col=("比和" if element==month else
             "被月令生" if GENERATES[month]==element else
             "被月令克" if CONTROLS[month]==element else
             "克月令" if CONTROLS[element]==month else "生月令")
        def key(stage):
            if stage in {"长生","冠带","临官","帝旺","沐浴"}:
                return "长生/冠带/临官/帝旺/沐浴"
            if stage in {"胎","养"}:return "胎 / 养"
            if stage in {"衰","病"}:return "衰 / 病"
            if stage in {"死","墓","绝"}:return "死 / 墓 / 绝"
            return "囚"
        rows={key(s["stage"]) for s in stages}
        if symbol=="庚" and p["id"]==4 and len(stages)==2 and {
                s["branch"]+":"+s["stage"] for s in stages}=={"辰:养","巳:长生"}:
            rows={"长生/冠带/临官/帝旺/沐浴"}
        vals={_lookup(tables,kind,row,col) for row in rows}
        return next(iter(vals)) if len(vals)==1 else "待核"
    return _lookup(tables,kind,row,col)

def _lookup(tables,kind,row,col):
    table=tables[kind]
    return table["rows"][row][table["columns"].index(col)]

def compose(chart,actor,relationship,sources=None):
    doc,stemdoc,template,energy,pairtxt=sources or load_sources()
    rules=doc["rules"]
    assert len(rules)==255 and len(doc["cases"])==12 and len(doc["conflicts"])==20
    assert len(pairtxt.strip().splitlines())==82
    assert len(template["sections"])==9
    tables=energy["tables"]
    palaces={p["id"]:p for p in chart["palaces"]}
    assert set(palaces)==set(range(1,10))
    illness,= [p for p in palaces.values() if any(s["star"]=="天芮星" for s in p["heavenStars"])]
    inj,=[p for p in palaces.values() if p["door"]=="伤门"]
    ip=illness["id"]
    sky=next(s["carriedStem"] for s in illness["heavenStars"] if s["star"]=="天芮星")
    door=illness["door"]
    bird=next((s["carriedStem"] for s in illness["heavenStars"] if s["star"]=="天禽星"),None)
    yin=chart["bureau"]["dun"]=="yin"
    inner=INNER_YIN if yin else INNER_YANG
    sector="体内" if ip in inner else "体表"
    def label(p):return p["gua"]+DIGITS[p["id"]]
    def find_rule(p,subtype):
        matches=[row for row in rules if row["类别"]=="九宫定位" and
                 row["子类"]==subtype and row["符号组合"]==label(p)+"·"+subtype.split("-")[-1] and
                 row["证据级别"].startswith("A")]
        if len(matches)!=1:raise ValueError(("Missing original source",label(p),subtype))
        return matches[0]["古籍象意或候选"]
    primary=find_rule(illness,"神奇之门-"+sector)
    originalSide="内" if sector=="体内" else "外"
    alternate=find_rule(illness,"秘笈大全-"+originalSide)
    patient=palaces[actor["mainPalace"]]
    hourStem=chart["pillars"]["hour"][0]
    hourPillar=chart["pillars"]["hour"]
    def real_carrier(stem,complete):
        return SIX_JIA.get(complete,"") if stem=="甲" else stem
    hourCarrier=real_carrier(hourStem,hourPillar)
    hlist=[p for p in palaces.values() if p["id"]!=5 and
           any(s["carriedStem"]==hourCarrier for s in p["heavenStars"])]
    if len(hlist)!=1:raise ValueError("Hour carrier not unique")
    hour=hlist[0]
    def relation(p):
        other=p["id"]
        if other==ip:return "同宫"
        a,b=ELEMENTS[ip],ELEMENTS[other]
        if a==b:return "比和"
        if CONTROLS[a]==b:return "病宫克此宫"
        if CONTROLS[b]==a:return "此宫克病宫"
        if GENERATES[a]==b:return "病宫生此宫"
        if GENERATES[b]==a:return "此宫生病宫"
        raise ValueError("Missing directed relation")
    def natural(p):
        return {"同宫":"两者同宫","比和":"两宫比和","病宫克此宫":"此宫受病宫所克",
         "此宫克病宫":"此宫克病宫","病宫生此宫":"此宫得病宫相生",
         "此宫生病宫":"此宫生扶病宫"}[relation(p)]
    month=_monthly(chart["pillars"]["month"][-1])
    def source_strength(kind,symbol,p,stages=()):
        return _power(kind,symbol,p,month,tables,stages)
    def stem_power(stem,p):
        star=next((s for s in p["heavenStars"] if s["carriedStem"]==stem),None)
        if star:return source_strength("stem",stem,p,star["stages"])
        if p["earthStem"]==stem:return source_strength("stem",stem,p,p["earthStages"])
        return "待核"
    def role_power(stem,carrier,p,pillar):
        if stem=="甲":
            if not pillar or SIX_JIA.get(pillar)!=carrier:return "待核"
            stages=[{"branch":b,"stage":STAGES_JIA[b]} for b in p["branches"]]
            return source_strength("stem","甲",p,stages)
        return stem_power(carrier,p)
    illnessPower=source_strength("star","天芮星",illness)
    skyPower=stem_power(sky,illness)
    earthPower=source_strength("stem",illness["earthStem"],illness,illness["earthStages"])
    birdStemPower=stem_power(bird,illness) if bird else "待核"
    actorCarrier=real_carrier(actor["mainStem"],actor.get("sourceGanzhi"))
    patientPower=role_power(actor["mainStem"],actorCarrier,patient,actor.get("sourceGanzhi")) if actorCarrier else "待核"
    hourPower=role_power(hourStem,hourCarrier,hour,hourPillar)
    injuryPower=source_strength("door","伤门",inj)
    doorRel=_directed(DOOR_ELEMENTS[door],ELEMENTS[ip])
    def void_state(p):
        if not p["voidBranches"]:return "not_void"
        if p["id"]==chart["hourHorsePalace"]:return "fake_void"
        if any(CLASH[b]==chart["hourHorse"] for b in p["voidBranches"]):return "not_void"
        pe=ELEMENTS[p["id"]]
        return "fake_void" if month==pe or GENERATES[month]==pe else "true_void"
    illnessVoid=void_state(illness)
    pmap={}
    for line in pairtxt.splitlines()[1:]:
        c=line.split("|")
        if len(c)>=4:pmap[(c[0],c[1])]=c[2]
    formation=[pmap[(sky,illness["earthStem"])]]
    if bird and (bird,palaces[5]["earthStem"]) in pmap:
        formation.append(pmap[(bird,palaces[5]["earthStem"])])
    stems=stemdoc["mapping"]
    variant=stems[sky]
    skySites=_parts("/".join(variant["qimen_secret_vol13"]+variant["sanming_viscera"]+variant["sanming_body_surface"]))
    earthSites=_parts("/".join(stems[illness["earthStem"]]["qimen_secret_vol13"]))
    birdSites=_parts("/".join(stems[bird]["qimen_secret_vol13"])) if bird else []
    originalSites=_parts(primary)
    alternateSites=_parts(alternate)
    def source_location(p):
        scope="体内" if p["id"] in inner else "体表"
        return _parts(find_rule(p,"神奇之门-"+scope))
    def flags(stem,p):
        o=[]
        if any(t["stem"]==stem for t in p["tombs"]):o.append("入墓")
        if any(s["carriedStem"]==stem for s in p["heavenStars"]) and STRIKING.get(stem)==p["id"]:
            o.append("六仪击刑")
        return o
    aux_ids=sorted({v for v in (actor.get("siblingAuxiliaryPalace"),
                              actor.get("genderPalace"),actor.get("natalPalace")) if v is not None})
    aux=[(palaces[i],palaces[i]["heavenStars"][0]["star"],
          source_strength("star",palaces[i]["heavenStars"][0]["star"],palaces[i]))
         for i in aux_ids if i in PHYSICAL]
    otherDoors=[(p,p["door"],source_strength("door",p["door"],p))
                for p in chart["palaces"] if p["id"] in PHYSICAL and
                p["id"]!=ip and p["id"]!=inj["id"]]
    witness=[(patient,actorCarrier,patientPower),(hour,hourCarrier,hourPower),
             (inj,"伤门",injuryPower)]+aux+otherDoors
    candidates=list(originalSites)
    added=0
    for p,symbol,power in witness:
        if p["id"]==ip or _tier(power)<4:continue
        for site in source_location(p):
            if _matched(site,candidates):continue
            direct=symbol!="伤门" and bool(flags(symbol,p))
            corroboration=any(other["id"] not in (p["id"],ip) and _tier(power2)>=3 and
                              _matched(site,source_location(other))
                              for other,_,power2 in witness)
            if direct or corroboration:
                candidates.append(site);added+=1
            if added>=4:break
        if added>=4:break
    scores=[]
    for idx,site in enumerate(candidates):
        val=_tier(illnessPower) if _matched(site,originalSites) else 0
        if _matched(site,originalSites):
            if illnessVoid=="true_void":val=0
            if illnessVoid=="fake_void":val=max(0,val-1)
        if _matched(site,alternateSites):val+=2
        if _matched(site,skySites):
            val+=_tier(skyPower)
            if flags(sky,illness):val+=5
        if _matched(site,earthSites):
            val+=_tier(earthPower)
            if flags(illness["earthStem"],illness):val+=5
        if bird and _matched(site,birdSites):
            val+=_tier(birdStemPower)
            if flags(bird,illness):val+=5
        counted=set()
        for p,stem,power in ((patient,actorCarrier,patientPower),(hour,hourStem,hourPower)):
            if p["id"]==ip:continue
            key=(p["id"],stem)
            if _matched(site,source_location(p)) and key not in counted:
                counted.add(key);val+=_tier(power)
                if flags(stem,p):val+=5
        if inj["id"]!=ip and _matched(site,source_location(inj)):val+=_tier(injuryPower)
        for p,star,power in aux:
            if p["id"]==ip:continue
            key=(p["id"],star)
            if _matched(site,source_location(p)) and key not in counted:
                counted.add(key);val+=_tier(power)
        for p,doorName,power in otherDoors:
            if _matched(site,source_location(p)):
                key=(p["id"],"door",doorName)
                if key not in counted:counted.add(key);val+=_tier(power)
        scores.append((site,val,idx))
    ranked=sorted(scores,key=lambda x:(-x[1],x[2]))
    leadSites=[x[0] for x in ranked[:2]]
    lead="、".join(leadSites)
    remain=[x[0] for x in ranked[2:]]
    supported=[site for site in alternateSites if
               not _matched(site,leadSites) and
               (_matched(site,skySites) or _matched(site,earthSites) or _matched(site,birdSites))]
    secondary=[]
    for site in remain+supported:
        if not _matched(site,secondary):secondary.append(site)
    secondSite="、".join(secondary[:2])
    actorOverlap=next((s for s in source_location(patient) if _matched(s,leadSites)),None) if patient["id"]!=ip else None
    actorLine=(f"{relationship}用神{actor['mainStem']}在{label(patient)}宫，该宫亦见{actorOverlap}。"
              if actorOverlap else "")
    if relationship=="父亲":
        qian=palaces[6]
        if qian["id"] not in (ip,patient["id"]):
            hit=next((s for s in source_location(qian) if _matched(s,leadSites)),None)
            if hit:actorLine+=f"父亲乾六宫另见{hit}。"
    injuryMatching=any(any(k in s for k in LIMBS) for s in leadSites)
    injuryCross=next((s for s in source_location(inj) if _matched(s,leadSites)),None)
    injuryLine=(f"伤门也在{label(illness)}宫，与肢体部位相接。"
                if inj["id"]==ip and injuryMatching else
                f"另看{label(inj)}宫的伤门，亦指{injuryCross}。"
                if inj["id"]!=ip and _tier(injuryPower)>=3 and injuryCross else "")
    injuryFull=injuryLine or f"伤门在{label(inj)}宫，主筋骨牵扯之象，仅作旁线。"
    matchingDoors=sorted((x for x in otherDoors if _tier(x[2])>=2 and
                         any(_matched(s,leadSites) for s in source_location(x[0]))),
                         key=lambda x:-_tier(x[2]))
    doorCross="；".join(f"{d}在{label(p)}宫，所指部位与{lead}相接" for p,d,_ in matchingDoors[:2])
    doorsFull=f"病宫临{door}，人物宫临{patient['door']}。"+(doorCross+"。" if doorCross else "其余门象不另增加主位。")
    hourMatch=next((s for s in source_location(hour) if _matched(s,leadSites)),None)
    hourFull=f"时干{hourStem}在{label(hour)}宫，{natural(hour)}；"+(f"其宫亦指{hourMatch}。" if hourMatch else "作为事体旁证。")
    personFull=f"{relationship}取用神{actor['mainStem']}在{label(patient)}宫，{natural(patient)}；"+(actorLine or "病位仍以天芮所示部位为先。")
    auxTexts=[]
    for p,star,power in aux:
        name=("亲属排行辅助" if p["id"]==actor.get("siblingAuxiliaryPalace") else
              "长辈乾坤辅助" if p["id"]==actor.get("genderPalace") else "真实年命辅助")
        hit=next((s for s in source_location(p) if _matched(s,leadSites)),None)
        auxTexts.append(name+label(p)+"宫"+(f"，亦见{hit}" if hit else "，另作参考"))
    auxFull="；".join(auxTexts)+"。" if auxTexts else "没有符合条件的额外人物辅宫。"
    formsFull=f"天芮携{sky}加地盘{illness['earthStem']}，见"+"、".join(formation)+f"格；合参本宫门神，以{lead}为主线。"
    danger=[]
    for stem,sites in ((sky,skySites),(illness["earthStem"],earthSites)):
        signs=flags(stem,illness)
        site=next((s for s in sites if _matched(s,leadSites)),None)
        if signs and site:danger.append(stem+"、".join(signs)+f"，传统不利象集中在{site}一带")
    if bird:
        signs=flags(bird,illness)
        site=next((s for s in birdSites if _matched(s,leadSites)),None)
        if signs and site:danger.append("天禽携"+bird+"、".join(signs)+f"，亦指{site}")
    if illnessVoid=="true_void":danger.append("病宫真空，本宫候选减看")
    elif illnessVoid=="fake_void":danger.append("病宫假空，本宫线索仍留")
    if doorRel=="宫克符号":danger.append(door+"门迫，门象受制")
    dangerFull="；".join(danger)+"。" if danger else "本宫未见重合主部位的墓刑空迫象。"
    ending="。" if not secondSite else "；另参"+secondSite+"。"
    final=f"综上，{relationship}本次病位首先看{lead}{ending}这是传统部位取象，不等于医学诊断。"
    values={
       "person":relationship,"palace":label(illness)+"宫","dun":"阴" if yin else "阳",
       "sector":sector,"focus_site":lead,"injury_full":injuryFull,
       "other_doors":doorsFull,"hour_site":hourFull,"actor_full":personFull,
       "auxiliary_full":auxFull,"formation_full":formsFull,"danger_full":dangerFull,
       "final_site":final
    }
    sections=[]
    for x in template["sections"]:
        rendered=x["text"]
        for name,val in values.items():rendered=rendered.replace("{"+name+"}",val)
        if "{" in rendered or "}" in rendered:raise ValueError("Unbound customer template")
        sections.append({"id":x["id"],"title":x["title"],"text":rendered})
    return {"sections":sections,
            "rolePalaces":{"illness":ip,"patient":patient["id"],"injury":inj["id"],"hour":hour["id"]},
            "version":"discomfort_v19_full_evidence_rank_20261101","topicID":"health.discomfort"}

def compare_jsonl(path):
    sources=load_sources()
    cases=[json.loads(row) for row in Path(path).read_text(encoding="utf-8").splitlines() if row.strip()]
    if len(cases)<2:raise AssertionError("Need two genuinely different native clocks")
    outputs=[]
    seen=set()
    for case in cases:
        board=case["chart"];actor=case["actor"];relationship=case["reading"]["relationship"]
        if board["iso"] in seen:raise AssertionError("Duplicate real instant")
        seen.add(board["iso"])
        actual=compose(board,actor,relationship,sources)
        expected=case["reading"]
        for key in ("version","topicID","sections","rolePalaces"):
            if actual[key]!=expected[key]:
                from difflib import unified_diff
                left=json.dumps(expected[key],ensure_ascii=False,indent=2)
                right=json.dumps(actual[key],ensure_ascii=False,indent=2)
                diff="\n".join(unified_diff(left.splitlines(),right.splitlines(),
                                            fromfile="actual-Swift",tofile="independent-Python"))
                raise AssertionError(f"{board['iso']} {relationship} {key} PARITY_FAIL\n{diff}")
        outputs.append((relationship,board["iso"],len(actual["sections"])))
    return outputs

if __name__=="__main__":
    import sys
    for person,instant,count in compare_jsonl(sys.argv[1]):
        print("V19_PYTHON_SWIFT_BYTE_EXACT_PASS",person,instant,count)
