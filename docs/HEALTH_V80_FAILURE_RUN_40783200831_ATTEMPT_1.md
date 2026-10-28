# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/40783200831\n\n\n## compile.log\n\n\`\`\`text\nios/WenguaAppUI/WenguaNativeReadingRouter.swift:211:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
209 |         let fanyin=entire(actualStars,homeStars,true) ||
210 |                     entire(actualDoors,homeDoors,true)
211 |         let macro=try [
    |             `- warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
212 |             fill(fiveNot ? "macro_five" : "macro_clear"),
213 |             fill(fuyin && fanyin ? "macro_mixed" :

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift:209:13: warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
207 |         let doorPart=try signedSymbol("door",door,palace:p.id,
208 |                                       month:month,energy:energy)
209 |         let hasIllness=p.heavenStars.contains{$0.star=="天芮星"}
    |             `- warning: initialization of immutable value 'hasIllness' was never used; consider replacing with assignment to '_' or removing it [#NoUsage]
210 |         // Each actual sky carrier has a distinct 81 pattern; do not
211 |         // mis-attribute Tianqin's carried stem to Tianrui.

[#NoUsage]: <https://docs.swift.org/compiler/documentation/diagnostics/no-usage>
\n\`\`\`\n\n## friend_swift.log\n\n\`\`\`text\n\n\`\`\`\n\n## friend_swift_stderr.log\n\n\`\`\`text\nV7_FULL_SOURCE_BONUS_COMPARE 2025-12-28T17:00:00-05:00 Swift base=3 result=Optional(-5) controls=[:] auspices=0 drainPalaces=[] real_day=辛未 real_hour=丁酉 Swift_tianxian=false Python_tianxian=false Python base=3 result=Optional(-5) controls=Optional([:]) auspices=Optional(0) drain=Optional(0)
Swift/ErrorType.swift:254: Fatal error: Error raised at top level: native.WenguaNativeReadingError.invalidPhrase

*** Signal 4: Backtracing from 0x7f5b76709fbf... done ***

*** Program crashed: Illegal instruction at 0x00007f5b76709fbf ***

Platform: x86_64 Linux (Ubuntu 24.04.5 LTS)

Thread 0 "native" crashed:

0      0x00007f5b76709fbf _assertionFailure(_:_:file:line:flags:) + 303 in libswiftCore.so
1 [ra] 0x00007f5b767698fe swift_errorInMain + 765 in libswiftCore.so
2 [ra] 0x000055b2a0ee34f7 main + 54 in native
3 [ra] 0x00007f5b7502a1ca <unknown> in libc.so.6
4 [ra] 0x00007f5b7502a28b <unknown> in libc.so.6


Registers:

rax 0x0000000200000003  8589934595
rdx 0x0000000000000002  2
rcx 0xfffffffe00000000  18446744065119617024
rbx 0x0000000000000003  3
rsi 0x000055b2daace7a8  03 00 00 00 00 00 00 00 58 00 00 00 00 00 00 80  ········X·······
rdi 0x000055b2daada760  00 00 00 00 00 00 00 00 61 00 00 00 00 00 00 00  ········a·······
rbp 0x00007fffe4489070  00 91 48 e4 ff 7f 00 00 fe 98 76 76 5b 7f 00 00  ··Häÿ···þ·vv[···
rsp 0x00007fffe4489050  48 00 00 00 00 00 00 f0 a0 e7 ac da b2 55 00 00  H······ð ç¬Ú²U··
 r8 0x000055b2daa19010  02 00 02 00 07 00 06 00 07 00 07 00 06 00 06 00  ················
 r9 0x0000000000000007  7
r10 0x000055b2daada770  ca 4e 83 81 b7 55 00 00 32 bd e3 11 39 c0 f9 9d  ÊN···U··2½ã·9Àù·
r11 0x9df9c03911e3bd32  11383340884501445938
r12 0x0000000000000048  72
r13 0x00007fffe44890c8  48 00 00 00 00 00 00 f0 a0 e7 ac da b2 55 00 00  H······ð ç¬Ú²U··
r14 0xf000000000000048  17293822569102704712
r15 0x0000000000000000  0
rip 0x00007f5b76709fbf  0f 0b 48 83 ec 08 48 8d 05 94 16 30 00 48 8d 3d  ··H·ì·H····0·H·=

rflags 0x0000000000010206  PF

cs 0x0033  fs 0x0000  gs 0x0000


Images (19 omitted):

0x000055b2a0df0000–0x000055b2a0ef6ec0 002baaeb25369a1254c4502700ef0a0954520f34 native          /tmp/wengua-v80/native
0x00007f5b75000000–0x00007f5b751b0039 a4a7992a8e66555c8141ab2a08a8465ff6e0ea65 libc.so.6       /usr/lib/x86_64-linux-gnu/libc.so.6
0x00007f5b76400000–0x00007f5b769d9b30 7f58c0a650758160f6344ec08a47634d4f888be7 libswiftCore.so /usr/share/swift/usr/lib/swift/linux/libswiftCore.so

Backtrace took 0.39s

\n\`\`\`\n\n## matrix_tests.log\n\n\`\`\`text\ntest_all_25_power_pairs_never_infer_strength_from_signed_grade (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_all_25_power_pairs_never_infer_strength_from_signed_grade) ... ok
test_both_real_clocks_account_for_actual_distinct_palaces (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_both_real_clocks_account_for_actual_distinct_palaces) ... ok
test_distinct_illness_host_allows_one_yi_ding_family (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_distinct_illness_host_allows_one_yi_ding_family) ... ok
test_independent_selected_host_any_role_or_any_order (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_independent_selected_host_any_role_or_any_order) ... ok
test_one_family_per_palace_and_complete_void_half_once (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_one_family_per_palace_and_complete_void_half_once) ... ok
test_same_physical_doctor_and_medicine_have_separate_energies (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_same_physical_doctor_and_medicine_have_separate_energies) ... ok
test_symbol_self_never_adds_once_or_under_different_role_alias (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_symbol_self_never_adds_once_or_under_different_role_alias) ... ok
test_yearstem_yi_is_not_yi_own_auspice (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix.test_yearstem_yi_is_not_yi_own_auspice) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.107s

OK
\n\`\`\`\n\n## mirror_tests.log\n\n\`\`\`text\ntest_all_selected_important_snapshots_match_canonical_bytes (test_important_mirror_integrity_20261026.ImportantMirrorParity.test_all_selected_important_snapshots_match_canonical_bytes) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
\n\`\`\`\n