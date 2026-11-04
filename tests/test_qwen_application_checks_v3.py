import copy
import json
import unittest
from src.wengua.qwen_application_checks_v3 import check


def fixture():
    claims={'patient_carrier':'乙','patient_palace':8,'natal_provided':False,'unique_selected_palaces':[2,4,8],
            'project_grade':'中等吉','future_dates':[],'role_strengths':{'doctor':'小','medicine':None}}
    answer={'mode':'source_study','summary':'综上所述，此病为中吉。',
            'evidence':[{'citation':'RULE_FIXTURE','statement':json.dumps({'claims':claims},ensure_ascii=False)}],
            'counter_evidence':[],'missing_information':[],'event_probability':None}
    return {'audit_claims':claims,'answer':answer},answer


class ApplicationEvidenceCheckerV3(unittest.TestCase):
    def mutate_claim(self,fn):
        ref,ans=fixture();ans=copy.deepcopy(ans);data=json.loads(ans['evidence'][0]['statement']);fn(data['claims'])
        ans['evidence'][0]['statement']=json.dumps(data,ensure_ascii=False)
        result=check(ref,ans)
        self.assertFalse(result['fact_consistency']);self.assertFalse(result['mechanical_checks_passed'])

    def test_correct_claims_and_public_grade_alias_pass_without_semantic_claim(self):
        ref,answer=fixture();result=check(ref,answer)
        self.assertTrue(result['mechanical_checks_passed']);self.assertTrue(result['natural_final_grade_checked'])
        self.assertFalse(result['semantic_support_verified']);self.assertFalse(result['prediction_validated'])

    def test_wrong_patient_binding_is_rejected(self):
        self.mutate_claim(lambda c:c.update(patient_carrier='庚'))

    def test_missing_birth_cannot_be_filled(self):
        self.mutate_claim(lambda c:c.update(natal_provided=True))

    def test_independent_yi_strength_cannot_copy_doctor(self):
        self.mutate_claim(lambda c:c['role_strengths'].update(medicine=c['role_strengths']['doctor']))

    def test_same_palace_cannot_be_counted_twice(self):
        self.mutate_claim(lambda c:c['unique_selected_palaces'].append(8))

    def test_unsupported_precise_timing_is_rejected(self):
        self.mutate_claim(lambda c:c.update(future_dates=['2099-01-01']))

    def test_natural_conclusion_conflict_is_rejected_even_with_correct_claims(self):
        ref,ans=fixture();ans=copy.deepcopy(ans);ans['summary']='综上所述，此病为极大凶。'
        result=check(ref,ans);self.assertIn('natural_final_grade_conflicts_with_evidence',result['errors'])
        self.assertFalse(result['mechanical_checks_passed'])

    def test_missing_machine_claims_is_not_scored_as_wrong_reasoning(self):
        ref,ans=fixture();ans=copy.deepcopy(ans);ans['evidence'][0]['statement']='自然语言表述，尚无机器字段。'
        result=check(ref,ans);self.assertIsNone(result['fact_consistency']);self.assertFalse(result['structured_claims_available'])
        self.assertIn('structured_claims_not_present_not_a_semantic_error_score',result['errors'])
        self.assertIsNone(result['mechanical_checks_passed'])

    def test_unretrieved_citation_or_probability_does_not_pass_schema(self):
        ref,ans=fixture();bad=copy.deepcopy(ans);bad['evidence'][0]['citation']='UNSUPPLIED'
        self.assertFalse(check(ref,bad)['schema_passed'])
        bad=copy.deepcopy(ans);bad['event_probability']=0.9
        self.assertFalse(check(ref,bad)['schema_passed'])


if __name__=='__main__':unittest.main()
