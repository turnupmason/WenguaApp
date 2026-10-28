"""V8 universal SOURCE-ONLY graph invariants, not new health scoring.

8 distinct health roles; full resident stars/door/deity/stems/81/flags;
same identity with multiple role aliases; pairs and triples in 1-3 actual
palaces; spatial adjacency, void, tomb, striking and palace restraint.
Synthetic geometry does not pretend these are real already-cast charts.
"""
import itertools
import unittest

from src.wengua.selected_signifier_graph_v80 import (
    DomainCondition, PalaceEnvironment, PalaceFactor, SelectedSignifier,
    SelectedSignifierGraph, palace_spatial_relation,
)

ROLES = (
    ("illness", "star", "天芮星", "极小"),
    ("doctor", "star", "天心星", "极大"),
    ("medicine", "stem", "乙", "大"),
    ("patient", "stem", "戊", "小"),
    ("hour", "stem", "丁", "中等"),
    ("natal", "stem", "庚", "中等"),
    ("gender", "star", "天柱星", "大"),
    ("chief", "deity", "值符", "小"),
)

def factor(kind, symbol, strength="中等", grade=None, restrictions=frozenset()):
    return PalaceFactor(
        category=kind, symbol_id=symbol,
        energy_fact_id="synthetic-source-only:" + kind + ":" + symbol,
        strength=strength, signed_contribution=grade,
        restrictions=frozenset(restrictions),
    )

def environment(palace, grade, flags=frozenset()):
    return PalaceEnvironment(
        palace_id=palace,
        stars=(factor("star", "天芮星", "极小", -3),
               factor("star", "天心星", "极大", +3),
               factor("star", "天柱星", "小", -2)),
        door=factor("door", "开门", "中等", +3),
        deity=factor("deity", "值符", "小", +3),
        heaven_stems=(factor("heaven_stem","乙","大"),factor("heaven_stem","丁","中等")),
        earth_stem=factor("earth_stem","戊","大"),
        ordered_81_patterns=(factor("ordered_81_pattern", "乙加戊", "小", +4),),
        flags=frozenset(flags), auspicious_grade=grade,
    )

def select(entries=ROLES, layout=None, restrictions=frozenset()):
    if layout is None:
        layout = {role: 3 for role, *_ in entries}
    return [
        SelectedSignifier(
            role_key=role, kind=kind, symbol_id=symbol,
            palace_id=layout[role],
            energy_fact_id="synthetic-role-source:" + kind + ":" + symbol,
            strength=tier,
            restrictions=frozenset(restrictions),
        )
        for role,kind,symbol,tier in entries
    ]

def graph(entries=ROLES, layout=None, flags=frozenset(), grades=None):
    roles = select(entries,layout)
    palaces = sorted({r.palace_id for r in roles})
    levels = {p: ((p % 2)*8)-4 for p in palaces} if grades is None else grades
    env = {p: environment(p, levels[p],flags) for p in palaces}
    return SelectedSignifierGraph(
        domain_id="health.severity", roles=roles,
        palace_grades=levels, environments=env,
    )


class V80FullPalaceIndependentGraph(unittest.TestCase):
    def test_eight_selected_roles_always_read_every_environment_factor(self):
        g = graph()
        report = g.audit()
        self.assertEqual(report["palace_environment_completeness"],"complete")
        self.assertEqual(report["base_palace_total_once"],4)
        self.assertEqual(len(report["palace_environments"]),1)
        categories={f["category"] for f in report["palace_environments"][0]["factors"]}
        self.assertEqual(categories,{
            "star","door","deity","heaven_stem","earth_stem","ordered_81_pattern"})
        self.assertEqual(len(report["all_role_resident_evidence"]),
                         len(ROLES)*len(g.environments[3].residents))
        self.assertTrue(all(x["awarded_points"] is None
                            for x in report["all_role_resident_evidence"]))
        self.assertEqual(report["palace_grades_once"],{3:4})
        by_role={x["role_key"]:x["selected_source_strength"]
                 for x in report["all_role_resident_evidence"]}
        self.assertEqual(by_role["doctor"],"极大")
        self.assertEqual(by_role["medicine"],"大")
        self.assertEqual(by_role["chief"],"小")
        self.assertTrue(all(x["result_requires_domain_rule"]
                            for x in report["all_role_resident_evidence"]))

    def test_every_two_and_three_roles_same_double_triple_palace(self):
        for length in (2,3):
            for combo in itertools.combinations(ROLES,length):
                for shape in (
                    (3,)*length,
                    tuple((3,1,3)[i] for i in range(length)),
                    tuple((3,8,1)[i] for i in range(length)),
                ):
                    layout={item[0]:shape[i] for i,item in enumerate(combo)}
                    g=graph(combo,layout)
                    expected_palaces=set(shape)
                    self.assertEqual(set(g.palace_grades),expected_palaces)
                    self.assertEqual(len(g.nodes()),length)
                    self.assertEqual(len(g.edges()),length*(length-1))
                    self.assertEqual(len(g.environments),len(expected_palaces))
                    self.assertEqual(g.base_palace_total,
                                     sum(g.palace_grades.values()))
                    for e in g.edges():
                        self.assertEqual(e["actor_energy_fact_id"][:22],
                                         "synthetic-role-source:")
                        self.assertIsNone(e["bonus_points"])
                        self.assertIsNone(e["effect"])
                        self.assertTrue(e["source_and_target_independent"])

    def test_all_8_roles_separate_then_cohost_only_base_once(self):
        layout={x[0]:(3 if i<4 else 1) for i,x in enumerate(ROLES)}
        g=graph(layout=layout,grades={3:5,1:-5})
        self.assertEqual(g.base_palace_total,0)
        self.assertEqual(len(g.edges()),8*7)
        self.assertEqual(len(g.nodes()),8)
        self.assertEqual(len(g.palace_grades),2)
        self.assertEqual(g.audit()["changes_authorized_v80_score"],False)

    def test_self_identity_alias_never_meets_self_or_double_counts_source(self):
        aliases=(
            ("medicine", "stem", "乙", "大"),
            ("natal", "stem", "乙", "大"),
            ("hour", "stem", "乙", "大"),
        )
        g=graph(aliases)
        self.assertEqual(len(g.nodes()),1)
        self.assertEqual(g.base_palace_total,4)
        self.assertEqual(g.edges(),[])
        rule=DomainCondition("real-helper-yi","health.severity",
                             frozenset(("medicine","natal","hour")),"stem","乙")
        self.assertEqual(g.independent_cohost_evidence([rule]),[])
        with self.assertRaises(ValueError):
            SelectedSignifierGraph(
                domain_id="health.severity",
                roles=select(aliases[:2])[:1]+[
                    SelectedSignifier("natal","stem","乙",3,
                                     "other-unverified-table","极大")],
                palace_grades={3:4})

    def test_every_independent_host_includes_full_palace_and_source_strength(self):
        aliases=(
            ("doctor","star","天心星","极大"),
            ("medicine","stem","乙","大"),
            ("hour","stem","乙","大"),
            ("patient","stem","戊","小"),
            ("chief","deity","值符","小"),
        )
        g=graph(aliases)
        conditions=[
            DomainCondition("health:host-meets-yi","health.severity",
                            frozenset(("doctor","medicine","hour","patient","chief")),
                            "stem","乙"),
            DomainCondition("health:host-meets-doctor","health.severity",
                            frozenset(("doctor","medicine","hour","patient","chief")),
                            "star","天心星"),
            DomainCondition("health:host-meets-chief","health.severity",
                            frozenset(("doctor","medicine","hour","patient","chief")),
                            "deity","值符"),
        ]
        evidence=g.independent_cohost_evidence(conditions)
        self.assertTrue(evidence)
        self.assertTrue(all(x["host"]!=x["helper"] for x in evidence))
        self.assertTrue(all(x["bonus_points"] is None for x in evidence))
        yi=[x for x in evidence if x["condition_id"]=="health:host-meets-yi"]
        self.assertEqual(len(yi),3)
        self.assertFalse(any(x["host_roles"]==["medicine"] for x in yi))
        self.assertFalse(any(x["host_roles"]==["hour"] for x in yi))
        self.assertEqual(g.base_palace_total,4)

    def test_void_tomb_striking_and_palace_control_are_evidence_not_new_vote(self):
        for flags in (
            frozenset(("真空",)),
            frozenset(("假空","天盘入墓","六仪击刑","门迫")),
            frozenset(("地盘入墓","驿马")),
        ):
            entries=(
                ("illness","star","天芮星","小"),
                ("patient","stem","戊","极大"),
                ("doctor","star","天心星","极小"),
            )
            layout={"illness":1,"patient":8,"doctor":8}
            roles=select(entries,layout,{"入墓","击刑","被宫克"})
            g=SelectedSignifierGraph(
                domain_id="health.severity",roles=roles,
                palace_grades={1:-3,8:-5},
                environments={1:environment(1,-3,flags),8:environment(8,-5,flags)},
            )
            evidence=g.audit()
            self.assertEqual(evidence["base_palace_total_once"],-8)
            self.assertTrue(all(e["bonus_points"] is None for e in evidence["edges"]))
            self.assertTrue(all(e["palace_flags"]==sorted(flags)
                                for e in evidence["all_role_resident_evidence"]))
            self.assertTrue(any(e["relation"]=="克" and e["actor_strength"]=="极大"
                                and e["target_strength"]=="小" for e in evidence["edges"]))

    def test_spatial_adjacent_vs_five_element_relation_are_separate(self):
        self.assertEqual(palace_spatial_relation(3,8),"九宫正邻位")
        self.assertEqual(palace_spatial_relation(3,1),"九宫斜邻位")
        self.assertEqual(palace_spatial_relation(3,7),"九宫非邻位")
        self.assertEqual(palace_spatial_relation(3,3),"同宫")
        g=graph(ROLES[:3],{"illness":1,"doctor":3,"medicine":8})
        self.assertTrue(all(x["spatial_adjacency_is_not_a_bonus"]
                            for x in g.edges()))
        self.assertTrue(any(x["relation"]=="克" for x in g.edges()))

    def test_missing_environment_rejected_and_center_five_not_invented(self):
        with self.assertRaises(ValueError):
            SelectedSignifierGraph(
                domain_id="health.severity",roles=select(ROLES[:2]),
                palace_grades={3:4},environments={3:environment(3,3)})
        with self.assertRaises(ValueError):
            graph(ROLES[:1],grades={3:4}).audit(
                [DomainCondition("forbidden","marriage",
                                 frozenset(("illness",)),"star","天心星")])
        with self.assertRaises(ValueError):
            PalaceEnvironment(5,(factor("star","天芮星"),),
                              None,None,(),None,(),frozenset(),0)
        with self.assertRaises(ValueError):
            PalaceEnvironment(3,(),factor("door","开门"),None,
                              (),None,(),frozenset(),4)
        g=SelectedSignifierGraph(
            domain_id="work.employment",roles=(
                SelectedSignifier("work_hour","stem","丁",5,"source:ding","小"),),
            palace_grades={5:0},
            environments={5:PalaceEnvironment(
                5,(),None,None,(),factor("earth_stem","戊"),(),
                frozenset(),0)})
        self.assertEqual(g.base_palace_total,0)
        self.assertEqual(len(g.audit()["palace_environments"][0]["factors"]),1)
        self.assertEqual(g.audit()["cohost_evidence"],[])


if __name__=="__main__":
    unittest.main()
