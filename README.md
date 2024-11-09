# Case Reports Events Corpus
The corpus is composed by triples associating a subject and an object via a typed predicate.
Subjects and objects are entities explicitly mentioned mentioned in a sentence and identified
by their span. The relation has a type chosen from a closed set of 18 semantic relation types
from the UMLS semantic network and is not characterized by reference to a particular segment
of text. For instance the sentence ""The child showed complete recovery postoperatively
with full expansion of the ipsilateral lung." is annotated as
```
{
"entities": [
{
"id": "child_36316785_11",
"text": "child",
"type": "person"
},
{
"id": "complete_recovery_36316785_11",
"text": "complete recovery",
"type": "condition"
},
{
"id": "postoperatively_36316785_11",
"text": "postoperatively",
"type": "time"
},
{
"id": "full_expansion_36316785_11",
"text": "full expansion of the ipsilateral lungfull expansion",
"type": "condition"
}
],
"relations": [
{
"type": "exhibits",
"subject": "child_36316785_11",
"object": "complete_recovery_36316785_11"
},
{
"type": "temporally_related_to",
"subject": "complete_recovery_36316785_11",
"object": "postoperatively_36316785_11"
},
{
"type": "exhibits",
"subject": "child_36316785_11",
"object": "full_expansion_36316785_11"
}
]
}
```
In order to have a sound base for annotation we selected 500 abstracts from the journal 
Medical Case Reports on EuropePMC, all being positive responses to the query cardiac
issued via the standard PMC API. After the usual textual cleansing, we performed sentence
splitting by using the NLTK sentence tokenizer, obtaining 2700 sentences which represents
our raw corpus. Before starting the annotation phase, we passed all sentences to LLama-3
(AI@Meta (2024)) in order to have a reasonable segmentation of Named Entities (NE). Here
it is important to notice that the concept of “reasonability” is a fuzzy one, as, at the end, the
segmentation of the named entities respond to the following criteria :

- being LLM friendly with respect to the NE they would normally consider as having a
role in a relation : for instance we accept the decision LLAMA-3 makes of keeping out
the determiner from NEs.
- being linguistically motivated : for instance sometimes LLAMA-3 decides to replace
long Noun Phrases such as A 29 year old Caucasian male with patient. Moreover,
in certain cases a named entity is simply not recognized as it is not part of a relation.
- Not deal (yet) with intensional contexts (Frege (1892)) : for instance in the phrase
complaint of failure to thrive and short height we focus on failure to thrive and short
height.

The core of the annotation concerns linking named entities via relations. As hinted above,
we make use of the semantic relations in the UMLS Semantic Network to establish these links.
Admittedly, we slightly forced some of the relations to fit the eventive nature of case reports,
which are normally structured as a sequence of events and their outcomes. For instance the
relation carries_out has been extended to a more generic "playing a role into an event".
Also two non UMLS relation have been introduced, namely goal and negates.
200 randomly selected sentences from the ‘raw corpus’ have been annotated by an annotator with some exposure to texts in the medical domain, without being a practitioner in
medicine : this choice is mainly due to the fact that we wanted linking decisions to be groun-
ded in the text and not inspired by some extra linguistic knowledge that a professional in the
healthcare domain could have. For the same reason, sentences are annotated in “isolation”, i.e. without references to preceding and following context,
again to avoid the introduction of spurious contextual inferences in the annotation.

The corpus is composed of 200 completely annotated sentences (for a total of 2780 words).
Globally it contains 681 triples, completely annotated with subject and object roles.
There are a total of 18 predicate types and 20 entity types : the top ten are listed here:
<img width="325" alt="predicate types and  entity types " src="https://github.com/morning-star-1789/case_reports_events_corpus/blob/main/assets/table_types.png">
## Files
In this distribution you will find the following files:
- annotation_guidelines.pdf : the annotation guidelines
- gold.json: the 200 sentences annotated and exported in json format
- gold_new.json: 50 sentences which were annotated after the experiments described in the companion papers were performed
- gold.sqlite3: the whole annotated corpus as an sqlite3 file
- top-ten-predicate-normalization.pdf: a table containing the top ten normalization described in the paper
- relation_mapper.py: a python module containing the statements used to perfom predicate mapping. They are explained in detail in the long version of the paper.
- memory consumption-v3.xlsx: the detailed spreadsheet we used for the calculation of energy consumption

## Further works
This is not an immutable version of the corpus, but just a preliminary one. In the future we plan to publish a second version validated by a domain expert and, if possible, 
enriched with more sentences.
## How to quote:
```
@misc{ldpj,
      title={Rule-based Mapping: an Efficient Strategy for Event Extraction with LLMs}, 
      author={Luca Dini, Pierre Jourlin },
      year={Under Review}
}




