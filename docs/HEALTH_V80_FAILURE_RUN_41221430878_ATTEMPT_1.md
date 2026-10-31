# V8.0 实际 CI 未通过，保留全部失败现场\n\nRun: https://github.com/turnupmason/WenguaApp/actions/runs/41221430878\n\n\n## matrix_tests.log\n\n\`\`\`text\nsetUpClass (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix) ... ERROR

======================================================================
ERROR: setUpClass (test_health_v79_independent_cohost_matrix_20261027.IndependentCohostMatrix)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/src/wengua/health_reading_template_vnext.py", line 46, in render
    try:return template()["macros"][slot].format_map(values)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'support'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/WenguaApp/WenguaApp/tests/test_health_v79_independent_cohost_matrix_20261027.py", line 109, in setUpClass
    cls.clock_colleague=colleague()["cases"][0]
                        ^^^^^^^^^^^
  File "/home/runner/work/WenguaApp/WenguaApp/scripts/ios_vnext_manual_colleague_natal_yi_20261027.py", line 24, in produce
    r = auto_cast_health_review_text(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/WenguaApp/WenguaApp/src/wengua/health_text_pipeline_vnext_review.py", line 22, in auto_cast_health_review_text
    review=analyze_health_severity_review(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/WenguaApp/WenguaApp/src/wengua/health_severity_vnext_review.py", line 207, in analyze_health_severity_review
    sections=format_sequence_sections(sequence,actor=actor,chart=chart)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/WenguaApp/WenguaApp/src/wengua/health_palace_sequence_vnext.py", line 406, in format_sequence_sections
    return selected_health_sections(result,actor=actor,chart=chart)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/WenguaApp/WenguaApp/src/wengua/domain_selected_energy_vnext.py", line 612, in selected_health_sections
    evidence=render_slot("summary_concise",illness=ill_text,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/WenguaApp/WenguaApp/src/wengua/health_reading_template_vnext.py", line 47, in render
    except KeyError as exc:raise ValueError(
                           ^^^^^^^^^^^^^^^^^
ValueError: Unknown/missing placeholder in user template slot summary_concise: 'support'

----------------------------------------------------------------------
Ran 0 tests in 0.078s

FAILED (errors=1)
\n\`\`\`\n