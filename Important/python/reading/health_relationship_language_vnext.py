"""Compact, action-oriented Qimen health-relationship prose from REAL chart facts.

Does not merely recite 五行 directions. Uses the user's current exact 200-cell
control results, star/stem actual tiers and (if known) palace signed values.
Outputs candidate traditional illness-symbol interpretation ONLY, never a
clinical treatment recommendation or a promise of improvement.
"""
from __future__ import annotations

from .selected_duel_table_vnext import matchup
from .health_palace_detailed_vnext import void_kwargs

SOLID=frozenset(("有效克制","高效克制","有效主克","强力主克",
                 "绝对主克","极限压制","完全清除"))
WEAK=frozenset(("微弱克制","减力克制","断续克制","效力递减"))
FAILED=frozenset(("克制失效","反侮受损","完全失控","系统性失控",
                   "终极解体","丧失能力"))
LABELS={
    "doctor":("天心医生","医药之助","医生制病","医生难以发挥制病作用"),
    "medicine":("乙奇医药","药力","医药制病","药力难以压住病象"),
    "patient":("患者用神","患者自身之力","患者有力抗病","患者自身制病能力受限"),
    "hour":("时干事体","求测事体之力","事体可制病","事体难以形成制病之助"),
    "chief":("值符大吉神","值符的护持力","吉神护持可制病","值符未形成制病之助"),
    "natal":("患者年命","年命之力","年命有制病之象","年命难形成有效制病之助"),
    "gender":("性别辅助宫","辅助宫之力","辅助宫可协助制病","辅助宫护持有限"),
}

def explain_role_against_illness(*,role,role_factor,disease_factor,
                                 role_palace,illness_palace,relation,
                                 actual_edge=None):
    """Human reading uses the real attacker for 被克, not swapped fiction."""
    who,source,success,fail=LABELS.get(role,(
        "辅助用神","辅助力量","辅助能制病","辅助制病作用不明"))
    strength=role_factor.get("strength_label")
    disease_strength=disease_factor.get("strength_label")
    cond=("本宫独立用神力量"+str(strength or "待核")+
          "，天芮病星独立用神力量"+str(disease_strength or "待核"))
    if relation=="克":
        edge=actual_edge
        if edge is None:raise ValueError("Actual control edge required")
        outcome=edge.get("control_result")
        if edge.get("control_status")!="matched":
            verdict="有克病的五行方向，但当前克制条件尚未形成唯一有效结论"
        elif outcome in SOLID:
            verdict=success+"，从传统盘象看有压制病势、缓解病象的机会"
        elif outcome in WEAK:
            verdict=source+"可形成一定制约，但力度有限，只能说勉强压制病宫"
        elif outcome in FAILED:
            verdict=fail+"，尚看不出由此推动病象缓解的有效力量"
        else:
            verdict="克制原格为"+str(outcome)+"，应结合已核宫内证据"
        if role=="chief" and outcome in SOLID:
            verdict="求测人有值符吉神护持，"+verdict
        if role=="chief" and outcome in FAILED:
            verdict="本盘虽见值符大吉神，但"+verdict
        return (who+"宫克天芮病宫；"+cond+"；克制表为"+
                str(outcome or "条件待核")+"，"+verdict+"。")
    if relation=="被克":
        # Actual attacker is disease. The caller supplies a legitimate
        # reverse lookup, NOT role-power pretending to attack illness.
        edge=actual_edge
        out=edge.get("control_result") if edge else None
        if out in SOLID:
            interpretation="病宫有力克制本方，"+source+"受到明显压制，难以形成有效的制病助力"
        elif out in WEAK:
            interpretation="病宫虽来克本方，但克力有限，仍有相持空间"
        elif out in FAILED:
            interpretation="病宫名义克本宫却难落实，不能因此反断病必重"
        else:
            interpretation="病宫克本方的实际力度尚需按原格和限制核算"
        return (who+"宫受天芮病宫克；"+cond+"；病宫施克结果"+
                str(out or "条件待核")+"，"+interpretation+"。")
    if relation=="生":
        return (who+"宫生天芮病宫；"+cond+"。五行方向为生病，实际生扶程度按两枚用神各自力量及限制判断，不凭宫位吉凶数字推算作用强弱。")
    if relation=="被生":
        return (who+"宫得病宫生扶；"+cond+"。实际受生程度依两枚用神力量判定，不等于主动克病；两宫吉凶分另行计入。")
    if relation=="比和":
        return (who+"宫与病宫比和；"+cond+"。同五行不等于两枚用神等力，亦非已经克住病宫。")
    if relation=="同宫":
        return (who+"与天芮同宫；"+cond+"。本宫吉凶只算一次，但两枚不同用神仍各保留独立力量，不能虚构跨宫相克。")
    return who+"与病宫的作用方向仍未核。"


def explain_selected_role(*,role,roles,edges):
    if role not in roles or "illness" not in roles:
        return ""
    own=roles[role];ill=roles["illness"]
    edge=edges.get(role+"->illness")
    if edge is None:return ""
    rel=edge["relation"]
    current=edge
    if rel=="被克":
        current=matchup(
            ill["primary_strength_25"],own["primary_strength_25"],
            actor_role="illness",target_role=role,
            **void_kwargs(ill["complete_palace"],own["complete_palace"]))
    return explain_role_against_illness(
        role=role,role_factor=own["primary_strength_25"],
        disease_factor=ill["primary_strength_25"],
        role_palace=own["palace"],illness_palace=ill["palace"],
        relation=rel,actual_edge=current)
