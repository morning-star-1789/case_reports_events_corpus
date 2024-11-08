'''
Created on May 27, 2024

@author: luca
'''

import copy
from collections import Counter
import json
from bacom import BACOM_STEP_4_FN, BACOM_DATA_DIR_CSV, BACOM_STEP_5_FN
from pandas.core.frame import DataFrame
import os
import pandas as pd
# import math
import pprint
import logging
from bacom.bacom_utils import jp
logger = logging.getLogger('bacom_log')


class Mapper(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.mappings = {
            'has_symptom': {
                'label':'exhibits',
                'id':'T145',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T145',
                'comment':' These are symptoms, which opposes to affected_by which reveal a disease'
                },
            'has_condition': {
                'label':'affected_by',
                'id':'R3.1',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T151',
                },
            'located_in': {
                'label':'has_location',
                'id':'R2.1',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T135',
                'comment':'possibly make disction between patient located in hospital and location of deseases'
                },
            'treatment': {
                'label':'treated_by',
                'id':'R3.1.2',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T154',
                'comment':'the subject is the patient or a desease(rare), if anything else, probaly wrong. The object is the operation'
                },
            'causes': {
                'label':'causes',
                'id':'T147',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T147'
                },
            'has_result': {
                'label':'has_result',
                'id':'R3.8',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T157',
                'comment':''' The subject is an analysis the object the results. The results of a treatment should be 
                under causes'''
                },
            'treated_with': {
                'label':'treated_by',
                'id':'R3.1.2',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T154',
                'comment':'the subject is the patient or a desease, if anything else, probaly wrong. The object is the operation'
                },
            
            'received': {
                'label':'treated_by',
                'id':'R3.1.2',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T154',
                'comment':'same as treated_with'
                },
            'treated_by': {
                'label':'treated_by',
                'id':'R3.1.2',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T154',
                'comment':'the subject is the patient or a desease, if anything else, probaly wrong. The object is the operation'
                },
            'has_component': {
                'label':'consists_of',
                'id':'T172',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T172'
                },
            'has_part': {
                'directive':'eliminates',
                'comment':'It produces systematically wrong relations. Probably just a place holder for unknown',
                },
            'performed': {
                'label':'carries_out',
                'id':'T141',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T141',
                'comment':'what is really performed it is usually the subject, therefore we must transfer the obj to subj and eliminate the subj',
                'role_actions':['invert', 'dummyfy_subj']  # actions are always executed in the order
                },
            'performed_by': {
                'label':'carries_out',
                'id':'T141',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T141',
                'comment':'few occurr. check the subject is a person. check also for the object is treatment. Unclear of invertable',
                },
            'has_attribute': {
                'directive':'eliminates',
                'comment':'It produces systematically wrong relations and in the few correct cases, they are relations inside NE',
                },
            'has_feature': {
                'label':'exhibits',
                'id':'T145',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T145',
                'comment':' In most cases a jolly relation which sometimes relates NE internal information.'
                },
            'presented_with': {
                'label':'exhibits',
                'id':'T145',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T145',
                'comment':' These are symptoms, which opposes to affected_by which reveal a disease'
                },
            'diagnosed_with': {
                'label':'diagnoses',
                'id':'T163',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T163',
                'comment':''' we use this relation in a deviated way. Indeed the original seems rather like:
                "The doctor diagnose a cancer". In our case the subject is the patient and not the doctor. '''
                },
            'developed': {
                'label':'produces',
                'id':'T144',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T144',
                'comment': '''in the data is either patient develop X or Y develop X, 
                where Y is either something absurd or a time. It deserve a special rule.'''
                },
            'temporal': {
                'label':'temporally_related_to',
                'id':'T136',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T136',
                'comment':''' We use a generic label as in the UMLSSemNET there is no treatment of temporality
                and in any case the network outputs generic (wrong) temporal rel.
                '''
                },
            'revealed': {
                'label':'indicates',
                'id':'T156',
                'source':'https://uts.nlm.nih.gov/uts/umls/semantic-network/T156'
                },
            'has_history': {
                'label':'precedes',
                'id':'T138',
                'source':'https://uts.nlm.nih.gov/uts/umls/semantic-network/T138',
                'comment':'''identify the label of the desease,usually the object. The subject is human. in the output
                the subject is network object and object is always a T0'''
        
                },
            'showed': {
                'directive':{'type':'subj_check',
                             'mappings':{'test': 'has_result',
                                         'procedure': 'has_result',
                                         'disease':'has_feature'}},
                'label':None,
                'id':'R3.8',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T157',
                'comment':''' The subject is an analysis the object the results as in "echocardiography showed improved systolic function". However it sometimes indicates
                             a desease showing something as in "myocarditis showed a tendency toward improvement" '''
                },
            'uses': {
                'directive':{'type':'subj_check',
                     'mappings':{'person': 'practices',
                                 'treatment': 'has_feature',
                                 'test':'has_feature',
                                 'medical-test':'has_feature',
                                 'device':'has_feature',
                                 'technique':'has_feature',}},
                'label':None,
                'id':'',
                'source':'',
                'comment':'''Two main cases: 
                            1) the subject is a patient who makes use of drugs, devices, etc.(practices)
                            2) The subject is an event (e.g test) which makes use of something (has feature))'''
                },
            'has_value': {
                'directive':'invert',
                'label':'measurement_of',
                'id':'T182',
                'source':'https://uts.nlm.nih.gov/uts/umls/semantic-network/T182'
                },
            'result': {
                'directive':{'type':'subj_check',
                     'mappings':{'person': 'has_feature',
                                 'treatment': 'causes',
                                 'test':'has_result',
                                 'medical-test':'has_result'}},
                'label':None,
                'id':None,
                'source':None
                },
            'confirmed_by': {
                'directive':'invert',
                'label':'indicates',
                'id':'T156',
                'source':'https://uts.nlm.nih.gov/uts/umls/semantic-network/T156',
                'comment': 'confirmation is more specific, but we have to do with that.'
                 },
            'ADMITTED_TO': {
                'label':'has_location',
                'id':'R2.1',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T135',
                'comment':'Almost always patient admitted to hospital, lab, etc.'
                },
            'has_duration': {
                'label':'temporally_related_to',
                'id':'T137',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T137',
                'comment':'No proper treatment of temporality in UMLS'
                },
            'underwent': {
                'label':'treated_by',
                'id':'R3.1.2',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T154',
                'comment':'the subject is the patient or a desease, if anything else, probaly wrong. The object is the operation'
                },
            'has_treatment': {
                'label':'treated_by',
                'id':'R3.1.2',
                'source':'https://evsexplore.semantics.cancer.gov/evsexplore/hierarchy/umlssemnet/T154',
                'comment':'the subject is the patient or a desease, if anything else, probaly wrong. The object is the operation'
                },
            'after': {
                'directive':'invert',
                'label':'precedes',
                'id':'T138',
                'source':'https://uts.nlm.nih.gov/uts/umls/semantic-network/T138'
                },
            '': {
                'label':'',
                'id':'',
                'source':''
                },

            }

    def interpret_direct(self, complex_directive:dict, sent_repr:dict, rel:dict, subj_id:str) -> dict:
        ''' It applies a directive on a whole representation and modifies in place the relation.
        @params:
        sent_repr: the whole representation for ent. retrieval
        rel: the raltion to modify.
        Notice that if a directive could not be interpreted the original predicate is left as it is.
        '''
        if complex_directive['type'] == 'subj_check':
            mappings:dict = complex_directive['mappings']
            for type_of_subj, pred in mappings.items():
                if is_subj_type(type_of_subj, subj_id, sent_repr):
                    rel['type'] = pred
                    return
        # if we are here the mapping had no effect
        logger.warning(f'A subj type looking map ({complex_directive}) could not apply on {sent_repr}')
    
    def map_to_umls (self, sent:str, i_repr:dict, ob, missing_mappings:Counter, print_all=False)->dict:
        changed = False
        # the copy is needed only for debug purposes
        new_out = copy.deepcopy(i_repr)
        
        rels = new_out['relations']
        new_rels = []  # add only mapped rels
        for rel in rels:
            t = rel['type']
            mapping_struct = self.mappings.get(t)
            if mapping_struct == None:
                missing_mappings.update([t])
                new_rels.append(rel)
            else:
                changed = True
                if mapping_struct.get('directive') == 'eliminates':
                    continue
                if mapping_struct.get('directive') == 'invert':
                    if rel.get('subject')==None:
                        logger.warning(f'Null subject  in {rel}') #eliminate the relation if inversion cannot be perdormed
                        continue
                    if rel.get('object')==None: #sometimes we have a value raher than an object
                        if rel.get('value')==None :
                            logger.warning(f'Null object and values  in {rel}') #eliminate the relation if inversion cannot be perdormed
                            continue
                        else : 
                            rel['object']=rel['value']
                        
                    prev_subj=rel['subject']
                    rel['subject']=rel.get('object')
                    rel['object']=prev_subj
                    rel['type'] = mapping_struct['label']
                    new_rels.append(rel)
                    continue
                if type(mapping_struct.get('directive')) == dict:
                    self.interpret_direct(mapping_struct.get('directive'), new_out, rel, rel['subject'])
                    new_rels.append(rel)
                    continue
                rel['type'] = mapping_struct['label']
                new_rels.append(rel)
        new_out['relations'] = new_rels
        if changed or print_all: 
            ob.write('\n*******')
            ob.write(sent + '\n')
            json.dump(i_repr, ob, indent=4)
            ob.write('\n')
            ob.write('----------------\n')
            json.dump(new_out, ob, indent=4)
        return new_out
                
    def compute_possible_target(self):
        ''' Used only once for computing drop box values '''
        ret:set=set()
        for val in self.mappings.values():
            label=val.get('label')
            if not label ==None:
                ret.add(label)
            elif val.get('directive') !=None and isinstance(val.get('directive'),dict):
                for v in val.get('directive')['mappings'].values(): 
                    ret.add(v)
            else:
                print(f'Exception for {val}')
        return sorted(list(ret)) 
    
    def do_mappings(self, run_id, input_csv=os.path.join(BACOM_DATA_DIR_CSV, BACOM_STEP_4_FN),out_file=os.path.join(BACOM_DATA_DIR_CSV,BACOM_STEP_5_FN)):
        df:DataFrame = pd.read_csv(input_csv, nrows=None)
        # out_df:DataFrame =  DataFrame(columns=df.columns.tolist()[1:]+['mapped_json'])
        df['mapped_json']=None
        missing_mappings:Counter = Counter()
        out = os.path.join(BACOM_DATA_DIR_CSV, run_id + '_' + 'entities_relations' + ".json")
        with open (out, "w") as ob:
            for __ind, row in df.iterrows():
                if not (row['cleaned_json']) != (row['cleaned_json']):  # check it was filled
                    new_repr=self.map_to_umls(row['sent'], json.loads(row['cleaned_json']), ob, missing_mappings, 
                                     print_all=False)
                    df.loc[__ind,('mapped_json')]=jp(new_repr)
                else:
                    df.loc[__ind,('mapped_json')]=None

        df.to_csv(out_file)
        return missing_mappings


def is_subj_type(expected_type:str, subj_id:str, sent_repr:dict):
    target_ents = list(filter(lambda x: x['id'] == subj_id, sent_repr['entities']))
    if len (target_ents) == 0:
        logger.error(f' No id {subj_id} in {sent_repr}')
        return False
    elif len (target_ents) > 1:
        logger.error(f' Ambiguous ids {target_ents} in {sent_repr}')
        return False
    subj_ent = target_ents[0]
    return expected_type == subj_ent['type']
    
    

if __name__ == '__main__':
    m = Mapper()
    missing = m.do_mappings('step_4')
    pprint.pprint(missing.most_common(20))