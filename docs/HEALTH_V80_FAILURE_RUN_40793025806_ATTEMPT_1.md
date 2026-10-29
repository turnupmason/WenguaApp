# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/40793025806\n\n\n## compile.log\n\n\`\`\`text\nios/WenguaAppUI/WenguaNativeReadingRouter.swift:211:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |         let fanyin=entire(actualStars,homeStars,true) ||
210 |                     entire(actualDoors,homeDoors,true)
211 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
212 |             fill(fiveNot ? "macro_five" : "macro_clear"),
213 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
\n\`\`\`\n\n## friend_swift.log\n\n\`\`\`text\n\n\`\`\`\n\n## friend_swift_stderr.log\n\n\`\`\`text\nV7_FULL_SOURCE_BONUS_COMPARE 2025-12-28T17:00:00-05:00 Swift base=3 result=Optional(-5) controls=[:] auspices=0 drainPalaces=[] real_day=辛未 real_hour=丁酉 Swift_tianxian=false Python_tianxian=false Python base=3 result=Optional(-5) controls=Optional([:]) auspices=Optional(0) drain=Optional(0)
Swift/ErrorType.swift:254: Fatal error: Error raised at top level: Error Domain=WenguaThreeFreshSourceParity Code=1 "(null)"UserInfo={NSLocalizedDescription=2025-12-28T17:00:00-05:00 [朋友] signed role-specific palace conclusion absent}

*** Signal 4: Backtracing from 0x7ff61a709fbf... done ***

*** Program crashed: Illegal instruction at 0x00007ff61a709fbf ***

Platform: x86_64 Linux (Ubuntu 24.04.5 LTS)

Thread 0 "native" crashed:

0      0x00007ff61a709fbf _assertionFailure(_:_:file:line:flags:) + 303 in libswiftCore.so
1 [ra] 0x00007ff61a7698fe swift_errorInMain + 765 in libswiftCore.so
2 [ra] 0x000055bdf1fa97b7 main + 54 in native
3 [ra] 0x00007ff61902a1ca <unknown> in libc.so.6
4 [ra] 0x00007ff61902a28b <unknown> in libc.so.6


Registers:

rax 0x0000000200000003  8589934595
rdx 0x0000000000000002  2
rcx 0xfffffffe00000000  18446744065119617024
rbx 0x0000000000000003  3
rsi 0x000055be07a4ed48  03 00 00 00 00 00 00 00 d0 00 00 00 00 00 00 80  ········Ð·······
rdi 0x000055be07a51520  64 00 00 00 00 00 00 00 e1 00 00 00 00 00 00 00  d·······á·······
rbp 0x00007ffd2bc7fb50  e0 fb c7 2b fd 7f 00 00 fe 98 76 1a f6 7f 00 00  àûÇ+ý···þ·v·ö···
rsp 0x00007ffd2bc7fb30  c6 00 00 00 00 00 00 30 40 ed a4 07 be 55 00 00  Æ······0@í¤·¾U··
 r8 0x000055be0798a010  07 00 07 00 07 00 07 00 07 00 07 00 07 00 07 00  ················
 r9 0x0000000000000007  7
r10 0x000055be07a51530  31 69 45 5c bb 55 00 00 e9 f2 d8 94 20 5e 37 99  1iE\»U··éòØ· ^7·
r11 0x99375e2094d8f2e9  11040396505551270633
r12 0x00000000000000c6  198
r13 0x00007ffd2bc7fba8  c6 00 00 00 00 00 00 30 40 ed a4 07 be 55 00 00  Æ······0@í¤·¾U··
r14 0x30000000000000c6  3458764513820541126
r15 0x0000000000000000  0
rip 0x00007ff61a709fbf  0f 0b 48 83 ec 08 48 8d 05 94 16 30 00 48 8d 3d  ··H·ì·H····0·H·=

rflags 0x0000000000010206  PF

cs 0x0033  fs 0x0000  gs 0x0000


Images (19 omitted):

0x000055bdf1eb6000–0x000055bdf1fbd158 d5042e74330b39e22672b074f381f2c79e50a27f native          /tmp/wengua-v80/native
0x00007ff619000000–0x00007ff6191b0039 a4a7992a8e66555c8141ab2a08a8465ff6e0ea65 libc.so.6       /usr/lib/x86_64-linux-gnu/libc.so.6
0x00007ff61a400000–0x00007ff61a9d9b30 7f58c0a650758160f6344ec08a47634d4f888be7 libswiftCore.so /usr/share/swift/usr/lib/swift/linux/libswiftCore.so

Backtrace took 0.16s

\n\`\`\`\n\n## matrix_tests.log\n\n\`\`\`text\ntest_all_25_power_pairs_never_infer_strength_from_signed_grade (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_all_25_power_pairs_never_infer_strength_from_signed_grade) ... ok
test_both_real_clocks_account_for_actual_distinct_palaces (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_both_real_clocks_account_for_actual_distinct_palaces) ... ok
test_distinct_illness_host_allows_one_yi_ding_family (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_distinct_illness_host_allows_one_yi_ding_family) ... ok
test_independent_selected_host_any_role_or_any_order (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_independent_selected_host_any_role_or_any_order) ... ok
test_one_family_per_palace_and_complete_void_half_once (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_one_family_per_palace_and_complete_void_half_once) ... ok
test_same_physical_doctor_and_medicine_have_separate_energies (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_same_physical_doctor_and_medicine_have_separate_energies) ... ok
test_symbol_self_never_adds_once_or_under_different_role_alias (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_symbol_self_never_adds_once_or_under_different_role_alias) ... ok
test_yearstem_yi_is_not_yi_own_auspice (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_yearstem_yi_is_not_yi_own_auspice) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.115s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
\n\`\`\`\n