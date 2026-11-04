"""Stdlib checker for V3 structured facts + limited final-grade wording.
Not an automatic proof of complete professional or predictive correctness.
"""
import json
import re

def display_grade(x):
 return (x or '').replace('中等吉','中吉').replace('中等凶','中凶').replace('中性0分','不凶不吉')

def check(reference, proposed):
 result={'schema_passed':False,'structured_claims_available':False,'fact_consistency':None,
         'mechanical_checks_passed':False,'natural_final_grade_checked':False,'semantic_support_verified':False,'prediction_validated':False,'errors':[]}
 required={'mode','summary','evidence','counter_evidence','missing_information','event_probability'}
 if not isinstance(proposed,dict) or not required<=set(proposed):result['errors'].append('missing_response_fields');return result
 if proposed['mode']!='source_study' or not isinstance(proposed['summary'],str) or any(not isinstance(proposed[k],list) for k in ('evidence','counter_evidence','missing_information')):
  result['errors'].append('wrong_response_types_or_mode');return result
 if proposed['event_probability'] is not None:result['errors'].append('uncalibrated_generated_probability');return result
 allowed={e['citation'] for e in reference['answer']['evidence']};claims=[]
 for evidence in proposed['evidence']:
  if not isinstance(evidence,dict) or evidence.get('citation') not in allowed or not isinstance(evidence.get('statement'),str):
   result['errors'].append('unknown_or_malformed_citation');return result
  try:
   value=json.loads(evidence['statement'])
   if isinstance(value,dict) and isinstance(value.get('claims'),dict):claims.append(value['claims'])
  except ValueError:pass
 result['schema_passed']=True
 expected=reference.get('audit_claims')
 if expected is not None:
  result['structured_claims_available']=bool(claims)
  if claims:
   result['fact_consistency']=all(v==expected for v in claims)
   if not result['fact_consistency']:result['errors'].append('claims_disagree_with_source_derived_facts')
  else:result['errors'].append('structured_claims_not_present_not_a_semantic_error_score')
  if 'project_grade' in expected:
   found=re.search(r'综上所述，此病为([^；。\n]+)',proposed['summary'])
   if found:
    result['natural_final_grade_checked']=True
    if found.group(1)!=display_grade(expected['project_grade']):result['errors'].append('natural_final_grade_conflicts_with_evidence')
 result['mechanical_checks_passed']=result['schema_passed'] and result['fact_consistency'] is not False and not any(e!='structured_claims_not_present_not_a_semantic_error_score' for e in result['errors'])
 if expected is not None and not claims and result['mechanical_checks_passed']:
  result['mechanical_checks_passed']=None
 return result
