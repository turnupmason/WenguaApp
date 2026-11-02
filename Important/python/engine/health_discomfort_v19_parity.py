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
        if s and s != "头发" and s not in result and not any(c in s for c in ("病","疾","风","寒","症","虚","咳","疝")):
            result.append(s)
    return result

def _same(a,b):
    if ("左" in a and "右" in b) or ("右" in a and "左" in b):return False
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

def compose(chart,actor,relationship,injury_context,sources=None):
    valid={"none","accident","bone","bleeding","severe_pain","surgery"}
    if injury_context not in valid:
        raise ValueError("Missing explicit body-site injury condition")
    use_injury=injury_context!="none"
    trauma=injury_context in {"accident","bone","bleeding"}
    doc,stemdoc,template,energy,pairtxt=sources or load_sources()
    rules=doc["rules"]
    assert len(rules)==255 and len(doc["cases"])==12 and len(doc["conflicts"])==20
    assert len(pairtxt.strip().splitlines())==82
    assert len(template["sections"])==9
    tables=energy["tables"]
    palaces={p["id"]:p for p in chart["palaces"]}
    assert set(palaces)==set(range(1,10))
    illness,= [p for p in palaces.values() if any(s["star"]=="天芮星" for s in p["heavenStars"])]
    inj,=[p for p in palaces.values() if p.get("door")=="伤门"]
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
    injuryPower=source_strength("door","伤门",inj) if use_injury else "待核"
    doorRel=_directed(DOOR_ELEMENTS[door],ELEMENTS[ip])
    def void_state(p):
        if not p["voidBranches"]:return "not_void"
        if p["id"]==chart["hourHorsePalace"]:return "fake_void"
        if any(CLASH[b]==chart["hourHorse"] for b in p["voidBranches"]):return "not_void"
        pe=ELEMENTS[p["id"]]
        return "fake_void" if month==pe or GENERATES[month]==pe else "true_void"
    illnessVoid=void_state(illness)
    pmap={}
    pfull={}
    for line in pairtxt.splitlines()[1:]:
        c=line.split("|")
        if len(c)>=6:
            pmap[(c[0],c[1])]=c[2]
            pfull[(c[0],c[1])]=(c[2],c[3],c[5])
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
    injurySites=source_location(inj) if use_injury else []
    if use_injury and not injurySites:raise ValueError("No source mapped injury palace")
    witness=[(patient,actorCarrier,patientPower),(hour,hourCarrier,hourPower)]+(
        [(inj,"伤门",injuryPower)] if use_injury else [])+aux
    # Other doors may confirm the chosen area, not create distant new organs.
    candidates=list(injurySites if trauma else originalSites)
    if trauma:
        for site in originalSites:
            if not _matched(site,candidates):candidates.append(site)
    # For surgery and severe pain, 伤门 remains a conditional witness.
    # Only explicit accident, bone injury or bleeding can make it the main site.
    # V21: independent role palaces can corroborate the main site, never
    # replace a real Tianrui or activated injury site with an unrelated organ.
    scores=[]
    for idx,site in enumerate(candidates):
        val=_tier(illnessPower) if _matched(site,originalSites) else 0
        if trauma and _matched(site,injurySites):
            val+=25+_tier(injuryPower)
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
        if use_injury and inj["id"]!=ip and _matched(site,injurySites):
            val+=_tier(injuryPower)
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
    leadSites=[x[0] for x in ranked[:1]]
    lead="、".join(leadSites)
    remain=[x[0] for x in ranked[2:]]
    supported=[site for site in alternateSites if
               not _matched(site,leadSites) and
               (_matched(site,skySites) or _matched(site,earthSites) or _matched(site,birdSites))]
    injurySecondary=([site for site,score,idx in ranked if
                      _matched(site,injurySites) and not _matched(site,leadSites)][:1]
                     if use_injury and not trauma else [])
    secondary=[]
    for site in injurySecondary+remain+supported:
        if not _matched(site,secondary):secondary.append(site)
    secondSite=""  # Keep alternate evidence internal; do not advertise unrelated organs.
    injuryReason={
        "accident":"意外受伤","bone":"骨肉受损",
        "bleeding":"伤口或出血","severe_pain":"剧烈疼痛",
        "surgery":"已做或拟做手术"}
    selectedInjurySites=([site for site,score,idx in ranked
                          if _matched(site,injurySites)][:1]
                         if trauma else injurySites[:1])
    injurySiteNames="、".join(selectedInjurySites)
    injuryScope="体内" if inj["id"] in inner else "体表"
    injuryOverlap=next((s for s in injurySites if _matched(s,originalSites)),None)
    injuryRelation=("伤门与天芮同宫，两条线索落在同一处。"
        if inj["id"]==ip else
        f"两宫同指{injuryOverlap}，因此这处有交叉印证。"
        if injuryOverlap else
        f"天芮另在{label(illness)}宫，两宫须分别取证。")
    openPalace=next((p for p in palaces.values() if p.get("door")=="开门"),None)
    surgicalControl=(injury_context=="surgery" and openPalace is not None
        and openPalace["id"]!=inj["id"] and
        CONTROLS[ELEMENTS[openPalace["id"]]]==ELEMENTS[inj["id"]])
    surgicalClue=(f"开门所在{label(openPalace)}宫五行克伤门宫，传统上有医伤相制之象，不据此认定必须手术。"
                 if surgicalControl else "")
    injuryRoomEvidence=[]
    if use_injury:
        for star in inj["heavenStars"]:
            starPower=source_strength("star",star["star"],inj)
            carrier=star["carriedStem"]
            carrierPower=stem_power(carrier,inj)
            candidates=_parts("/".join(stems[carrier]["qimen_secret_vol13"]))
            site=next((x for x in candidates if _matched(x,selectedInjurySites)),None)
            if _tier(starPower)>=2 and _tier(carrierPower)>=2 and site:
                injuryRoomEvidence.append(
                    f"宫中{star['star']}携{carrier}的部位干象也取{site}，故这处有星与干的同宫互证。")
        injuryEarthPower=source_strength("stem",inj["earthStem"],inj,inj["earthStages"])
        injuryEarthSites=_parts("/".join(stems[inj["earthStem"]]["qimen_secret_vol13"]))
        earthSite=next((x for x in injuryEarthSites if _matched(x,selectedInjurySites)),None)
        if _tier(injuryEarthPower)>=2 and earthSite:
            injuryRoomEvidence.append(
                f"地盘{inj['earthStem']}的独立干象也指{earthSite}，再收窄到这一带。")
        if inj["deity"]=="白虎":
            injuryRoomEvidence.append(
                "该宫同时临白虎，仅构成传统伤损同宫条件，不足以确认出血、骨折或手术必要性。")
        if _directed(DOOR_ELEMENTS["伤门"],ELEMENTS[inj["id"]])=="符号克宫":
            injuryRoomEvidence.append("伤门木克本宫土而成门迫，伤损部位线索须结合宫内星干审看。")
        activeSigns={t["stem"] for t in inj["tombs"]}
        if (any(x["carriedStem"] in activeSigns for x in inj["heavenStars"])
            or inj["earthStem"] in activeSigns):
            injuryRoomEvidence.append("此宫实见携干或地盘干入墓，相关部位暂不单凭一条线索定死。")
    injuryLimit=("伤门宫真空，须减看这一处的部位依据。"
          if void_state(inj)=="true_void" else
          "伤门自身取力偏弱，这处仍须其他符号印证。"
          if _tier(injuryPower)<=2 else "")
    injuryFull=(f"此次{injuryReason[injury_context]}，伤门落{label(inj)}宫，"
        f"{'阴' if yin else '阳'}遁{injuryScope}取{injurySiteNames}；"
        +injuryRelation+"".join(injuryRoomEvidence)+injuryLimit+surgicalClue if use_injury else "")
    matchingDoors=sorted((x for x in otherDoors if _tier(x[2])>=2 and
                         any(_matched(s,leadSites) for s in source_location(x[0]))),
                         key=lambda x:-_tier(x[2]))
    doorSentences=[]
    for p,d,power in matchingDoors[:2]:
        hit=next((s for s in source_location(p) if _matched(s,leadSites)),None)
        if hit:doorSentences.append(
            f"{d}在{label(p)}宫，该宫也取{hit}，与已选病位重合，故可作为另一宫的交叉印证。")
    doorsFull="".join(doorSentences)
    hourMatch=next((s for s in source_location(hour) if _matched(s,leadSites)),None)
    if hour["id"]==ip and patient["id"]==ip and actorCarrier==hourCarrier:
        hourFull=""
    elif hour["id"]==ip:
        hourFull=f"时干{hourStem}也落{label(hour)}宫，与病星同宫参看。"
    elif hourMatch:
        hourFull=f"时干{hourStem}落{label(hour)}宫，亦指{hourMatch}，与主位相互印证。"
    else:
        hourFull=f"时干{hourStem}落{label(hour)}宫，另宫只作病事参照。"
    actorOverlap=next((s for s in source_location(patient) if _matched(s,leadSites)),None)
    if patient["id"]==ip and hour["id"]==ip and actorCarrier==hourCarrier:
        personFull=(f"{relationship}用神{actor['mainStem']}就是时干，二者同符同落"
                    f"{label(illness)}宫，与天芮合看，不重复计位。")
    elif patient["id"]==ip:
        personFull=f"{relationship}用神{actor['mainStem']}在{label(illness)}宫，与天芮同宫。"
    elif patient["id"]==hour["id"] and actorCarrier==hourCarrier:
        personFull=f"{relationship}用神{actor['mainStem']}与时干同符同在{label(patient)}宫，只作一次位置证据。"
    elif actorOverlap:
        personFull=(f"{relationship}用神{actor['mainStem']}在{label(patient)}宫，"
                    f"另见{actorOverlap}，与主位相合。")
    else:
        personFull=f"{relationship}用神{actor['mainStem']}在{label(patient)}宫，与病星分宫取证。"
    auxTexts=[]
    for p,star,power in aux:
        name=("已确认的亲属排行辅助" if p["id"]==actor.get("siblingAuxiliaryPalace") else
              f"{relationship}长辈辅宫" if p["id"]==actor.get("genderPalace") else "已提供的年命")
        if p["id"] in (patient["id"],ip):
            auxTexts.append(f"{name}在{label(p)}宫，与已取实宫相同，不另计一次。")
        else:
            hit=next((s for s in source_location(p) if _matched(s,leadSites)),None)
            if hit:auxTexts.append(f"{name}在{label(p)}宫，也见{hit}，作为旁证。")
            else:auxTexts.append(f"{name}在{label(p)}宫，与主位分开参看。")
    auxFull="".join(auxTexts)
    # Two actual branches may map to different 200-grid stages.
    # Never fabricate a single consolidated source tier.
    def stem_branch_facts(stem,p,stages):
        if not stages:raise ValueError("Missing original branch-stage facts")
        facts=[]
        for stage in stages:
            strength=source_strength("stem",stem,p,[stage])
            if _tier(strength)==0:raise ValueError("Unmapped real 200-grid stem row")
            facts.append((stage["branch"]+stage["stage"],strength))
        return facts
    def selected_stem_image(stem,power,stages):
        candidates=_parts("/".join(stems[stem]["qimen_secret_vol13"]))
        original=next((x for x in candidates if _matched(x,leadSites)),
                      candidates[0] if candidates else "无已核实的细部候选")
        selected="脏腑泛象" if original=="脏（笼统）" else original
        facts=stem_branch_facts(stem,illness,stages)
        distinct={v for _,v in facts}
        if _tier(power)>0:powerWords="力量"+power
        elif len(distinct)==1:powerWords="两支同为"+facts[0][1]
        else:powerWords="分支力量"+"、".join(branch+"为"+v for branch,v in facts)
        effect=("这一干象较为突出" if
                _tier(power)>=4 or all(_tier(v)>=4 for _,v in facts) else
                "此干象偏弱" if all(_tier(v)<=2 for _,v in facts) else
                "此干象仍须与病宫其他符号互证")
        return selected+"，"+powerWords+"，"+effect
    def formation_meaning(top,ground):
        detail=pfull.get((top,ground))
        if detail is None:return None
        name,nature,gist=detail
        # Preserve original label in 81 TSV but do not say sexually charged
        # non-disease idioms to someone asking about a family member illness.
        name="壬加癸旧格" if name=="幼女奸淫" else name
        if "伏吟" in name:reading="同干重叠，取缠滞反复之象"
        elif any(x in name for x in ("网","狱","牢","罗","困","地户","墓")):
            reading="受困闭滞，取不畅之象"
        elif any(x in name for x in ("蛇","缠","夭矫")):
            reading="纠缠牵扯，取反复之象"
        elif any(x in name for x in ("刑","伤","折","破","克")):
            reading="上下干相制，取受损牵制之象"
        elif any(x in name for x in ("合","生","佐","返首","耀明")):
            reading="两干相助，取有缓解条件之象"
        else:
            reading="两干有相助之象" if nature=="吉" else "两干有牵制之象"
        return f"{name}，{nature}格，{reading}"
    orderedFormations=[]
    mainMeaning=formation_meaning(sky,illness["earthStem"])
    if mainMeaning:orderedFormations.append(
        f"天盘{sky}加地盘{illness['earthStem']}为"+mainMeaning)
    if bird:
        centre=palaces[5]
        hostedMeaning=formation_meaning(bird,centre["earthStem"])
        if hostedMeaning:orderedFormations.append(
            f"天禽携{bird}加寄宫地干{centre['earthStem']}为"+hostedMeaning)
    skyText=f"天盘{sky}主{selected_stem_image(sky,skyPower,next(x['stages'] for x in illness['heavenStars'] if x['star']=='天芮星'))}"
    earthText=f"地盘{illness['earthStem']}主{selected_stem_image(illness['earthStem'],earthPower,illness['earthStages'])}"
    birdText=(f"；同宫天禽星力量{source_strength('star','天禽星',illness)}，"
              f"所携{bird}主{selected_stem_image(bird,birdStemPower,next(x['stages'] for x in illness['heavenStars'] if x['star']=='天禽星'))}"
              if bird else "")
    formsFull=skyText+"；"+earthText+birdText+"。天地格："+"；".join(orderedFormations)+"。"
    danger=[]
    recorded=set()
    for stem in [sky,illness["earthStem"]]+([bird] if bird else []):
        signs=flags(stem,illness)
        if signs:
            key=stem+"/"+"、".join(signs)
            if key not in recorded:
                recorded.add(key)
                danger.append(f"{stem}实见{'、'.join(signs)}，传统取其受制、受伤之象，须细察本宫相应干象")
    if illnessVoid=="true_void":
        danger.append("天芮宫真空，病位显象减看")
    elif illnessVoid=="fake_void":
        danger.append("天芮宫假空，不作全无")
    doorPower=source_strength("door",door,illness)
    deity=illness["deity"]
    GOD_ELEMENTS={"值符":"土","螣蛇":"火","太阴":"金","六合":"木",
                  "白虎":"金","玄武":"水","九地":"土","九天":"金"}
    GOD_TIERS={"符号生宫":"中等","符号克宫":"中等",
               "比和":"大","宫克符号":"小","宫生符号":"极大"}
    deityPower=GOD_TIERS[_directed(GOD_ELEMENTS[deity],ELEMENTS[ip])]
    def original_clue(kind,symbol):
        rows=[r for r in rules if r["类别"]==kind and
              r["符号组合"]==symbol and r["证据级别"].startswith("A")]
        if len(rows)!=1:return "暂无可独立定位的细项"
        phrase=rows[0]["古籍象意或候选"].split("；")[0].split("（")[0]
        return ("无可用于细分身体部位的额外信息"
                if any(x in phrase for x in ("原文","不是","节气群")) else phrase)
    matchingDeity=[r for r in rules if r["类别"]=="八神病象" and
                   deity in r["符号组合"].split("／")]
    deityClue=(matchingDeity[0]["古籍象意或候选"] if matchingDeity else "其他传统象意")
    deityClue=deityClue.split("；")[0].split("（")[0]
    deityText="传统神象待核" if deityClue=="其他传统象意" else deityClue
    if doorRel=="符号克宫":
        terms={"开门":"金门迫木宫，传统指施治有阻",
               "休门":"水门迫火宫，传统指休养反复",
               "生门":"土门迫水宫，传统指生机受阻",
               "伤门":"木门迫土宫，传统指筋骨牵扯",
               "杜门":"木门迫土宫，传统指闭滞不畅",
               "景门":"火门迫金宫，传统指热象与肺系受扰",
               "死门":"土门迫水宫，传统指闭塞积滞",
               "惊门":"金门迫木宫，传统指惊扰、抽掣"}
        doorText=f"{door}落{label(illness)}宫形成门迫，"+terms.get(door,"门克落宫")
    elif doorRel=="宫克符号":
        doorText=f"{door}受{label(illness)}宫所克，门象受制，但不是门迫"
    else:doorText=""
    doorClue=original_clue("八门病象",door)
    starDoorGodFull=(f"天芮星力量{illnessPower}，以它的实际落宫定主要位置；"
                     f"{door}力量{doorPower}，旧籍取{doorClue}，"
                     +("门象较突出" if _tier(doorPower)>=4 else "门象只作旁证")
                     +f"；{deity}力量{deityPower}，旧籍取{deityText}，"
                     +("神象也较明显。" if _tier(deityPower)>=4
                       else "神象须配合其它证据。"))
    if doorText:danger.append(doorText)
    dangerFull="本宫条件："+"；".join(danger)+"。" if danger else ""
    ending="。"
    originalFocus=(lead if not trauma and _matched(lead,originalSites)
                   else "、".join(originalSites[:1]))
    originalLocation=(f"天芮在{label(illness)}宫，{'阴' if yin else '阳'}遁{sector}象先指{originalFocus}；"
                      "此次确有伤损，另从伤门实际落宫优先核位。"
                      if trauma else
                      f"天芮在{label(illness)}宫，{'阴' if yin else '阳'}遁{sector}象先指{originalFocus}。")
    locationFull="\n".join(x for x in (originalLocation,starDoorGodFull,formsFull,dangerFull) if x)
    # Never convert a left lung into a right-sided organ to sound concise.
    if lead=="肝胆":focusRegion="右上腹肝胆一带"
    elif lead=="左肩":focusRegion="左肩一带"
    elif lead=="左耳":focusRegion="左耳周围"
    elif lead=="左臂":focusRegion="左臂一带"
    elif lead=="右肩":focusRegion="右肩一带"
    elif lead=="右耳":focusRegion="右耳周围"
    elif lead=="右臂":focusRegion="右臂一带"
    elif lead in ("右肋","右腰"):focusRegion="右侧肋腰一带"
    elif lead in ("外阴","下部"):focusRegion="下身会阴一带"
    elif lead=="左肺":focusRegion="左侧胸部"
    else:focusRegion=lead
    bodyEvidence=[]
    earthSite=next((x for x in earthSites if _matched(x,leadSites)),None)
    skySite=next((x for x in skySites if _matched(x,leadSites)),None)
    if earthSite and _tier(earthPower)>=4:
        bodyEvidence.append(f"地盘{illness['earthStem']}所指{earthSite}力量{earthPower}，与主病位同向，这一处更值得留意")
    elif skySite and _tier(skyPower)>=4:
        bodyEvidence.append(f"天盘{sky}所指{skySite}力量{skyPower}，与主病位相合")
    if _tier(doorPower)>=4 and not trauma:
        bodyEvidence.append(f"{door}力量{doorPower}，旧籍{doorClue}所指的"+
                            ("筋脉牵扯" if door=="伤门" else "伴随征象")+"更显")
    if _tier(deityPower)>=4 and not trauma:
        bodyEvidence.append(f"{deity}力量{deityPower}，旧籍所指{deityText}可作伴随线索")
    if "伏吟" in formation[0]:
        bodyEvidence.append("本宫天地干伏吟，传统取反复迟滞之象")
    elif any("伏吟" in x for x in formation[1:]):
        bodyEvidence.append("同宫天禽寄格见伏吟，传统取反复迟滞为旁象，仍按天禽实际力量衡量")
    closing="盘中"+"；".join(bodyEvidence)+"。" if bodyEvidence else ""
    final=(f"综上，{relationship}本次"+
           ("因属伤损，先从伤门落宫看" if trauma else "病位先看")+
           focusRegion+"。"+closing+"以上为传统病位和症候象意，需以实际检查核实。")
    values={
       "person":relationship,"palace":label(illness)+"宫","dun":"阴" if yin else "阳",
       "sector":sector,"focus_site":lead,"location_full":locationFull,"injury_full":injuryFull,
       "other_doors":doorsFull,"hour_site":hourFull,"actor_full":personFull,
       "auxiliary_full":auxFull,"formation_full":"","danger_full":"",
       "final_site":final
    }
    sections=[]
    for x in template["sections"]:
        if x["id"]=="02_injury" and not use_injury:continue
        rendered=x["text"]
        for name,val in values.items():rendered=rendered.replace("{"+name+"}",val)
        if "{" in rendered or "}" in rendered:raise ValueError("Unbound customer template")
        if rendered.strip():
            sections.append({"id":x["id"],"title":x["title"],"text":rendered})
    return {"sections":sections,
            "rolePalaces":dict({"illness":ip,"patient":patient["id"],
                                "hour":hour["id"]},
                               **({"injury":inj["id"]} if use_injury else {})),
            "version":"discomfort_v23_integrated_palace_20261101","topicID":"health.discomfort"}

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
        actual=compose(board,actor,relationship,case["injuryContext"],sources)
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
