import spacy
import numpy as np
from collections import Counter

from relevance_factors_0218 import determine_component, get_cluster_info, get_graph_info

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(title, transcript_text):
    """
    Run NER on the title and full transcript text.
    """
    ner_title, _ = ner_group(title)
    # first_200 = " ".join(transcript_text[:200])
    # ner_first, _ = ner_group(first_200)
    ner_full, sentences = ner_group(transcript_text)

    # group = [ner_title, ner_first]

    # ner_groups = [loc for ner_list in group for loc in ner_list]

    return [ner_title, ner_full], sentences


def ner_group(transcript):
    """
    Extract named entities categorized as physical places from the text.

    NER Tag Descriptions:
    FAC:         Buildings, airports, highways, bridges, etc.
    ORG:         Companies, agencies, institutions, etc.
    GPE:         Countries, cities, states.
    LOC:         Non-GPE locations, mountain ranges, bodies of water.
    PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
    """
    doc = nlp(transcript)
    # location_entities = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT", "ORG"}]
    location_entities = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT"}]
    location_entities = [loc.lower() for loc in location_entities] 

    # Extract sentences
    sentences = [sent.text for sent in doc.sents]

    return location_entities, sentences


def determine_relevance(locations_in_groups, sentences, package_option, components, weights_list, simple=False):
    """
    Determine relevance based on frequency of mentions.
    """
    title_ner = locations_in_groups[0] if "segment" in components else []
    all_locations = [loc for locations in locations_in_groups for loc in locations]

    cluster_info, graph_info, location_json = [], [], {}
    if "cluster" in components:
        cluster_info, location_json = get_cluster_info(all_locations, package_option)

    if "graph" in components:
        graph_info = get_graph_info(sentences, all_locations)

    scores_dict = {}
    n_entities = len(all_locations)
    for loc in list(set(all_locations)):
        score_parts = []
        for component in components:
            unweighted_score = determine_component(component, loc, all_locations, title_ner, n_entities, package_option, cluster_info, graph_info)

            score_parts.append(unweighted_score)
        min_len = min(len(weights_list), len(score_parts))
        scores_dict[loc] = [np.dot(np.array(weights[:min_len]),  np.array(score_parts[:min_len])) for weights in weights_list]

    return location_json, [Counter(dict(zip(scores_dict.keys(), values))).most_common(3) for values in zip(*scores_dict.values())]
    # return {}, []
    # return location_json, []

def analyze_transcript(text_info, package_option, components, weights_list, only_ner=False):
    """
    Analyze a transcript file for location-based named entities and relevance.
    """
    with open(text_info[1], 'r') as f:
        transcript_text = f.read()
    
    # Step 1: Extract named entities
    locations_in_groups, sentences = extract_named_entities(text_info[0], transcript_text)

    # if only_ner:
        # m = [item for sublist in locations_in_groups for item in sublist]
        # return sorted(m)
        # return sorted(locations_in_groups[0]), sorted(locations_in_groups[1])

    # Step 2: Determine relevance
    location_json, relevant_locations = determine_relevance(locations_in_groups, sentences, package_option, components, weights_list)

    return location_json, relevant_locations
    # return locations_in_groups, sentences
    # return relevant_locations