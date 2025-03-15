import spacy
from collections import Counter

from relevance_factors import determine_component, get_cluster_info

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(title, transcript_text):
    """
    Extract named entities categorized as physical places from the text.

    NER Tag Descriptions:
    FAC:         Buildings, airports, highways, bridges, etc.
    ORG:         Companies, agencies, institutions, etc.
    GPE:         Countries, cities, states.
    LOC:         Non-GPE locations, mountain ranges, bodies of water.
    PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
    """
    # entire_transcript = transcript_text.split()
    # first_200 = " ".join(entire_transcript[:200])
    # last_200 = " ".join(entire_transcript[-200:])

    ner_title = ner_group(title)
    ner_full = ner_group(transcript_text)
    # ner_first200 = extract_named_entities_in_group(first_200)
    # ner_last200 = extract_named_entities_in_group(last_200)

    # return [ner_title, ner_full, ner_first200, ner_last200]
    return [ner_title, ner_full]


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

    return location_entities


def determine_relevance(locations_in_groups, package_option, components, weights, simple=False):
    """
    Determine relevance based on frequency of mentions.
    """
    all_locations = []
    for locations in locations_in_groups:
        all_locations += locations

    if "cluster" in components:
        cluster_info = get_cluster_info(all_locations, package_option)

    scores = Counter()
    n_entities = len(all_locations)
    for loc in list(set(all_locations)):
        score = 0
        for component in components:
            weight = weights[components.index(component)]
            title_ner = locations_in_groups[0]
            score += weight * determine_component(component, loc, all_locations, title_ner, n_entities, package_option, cluster_info)
        scores[loc] = score

    return scores.most_common(3)


def analyze_transcript(text_info, package_option, components, weights, only_ner=False):
    """
    Analyze a transcript file for location-based named entities and relevance.
    """
    with open(text_info[1], 'r') as f:
        transcript_text = f.read()
    
    # Step 1: Extract named entities
    locations_in_groups = extract_named_entities(text_info[0], transcript_text)

    # if only_ner:
        # m = [item for sublist in locations_in_groups for item in sublist]
        # return sorted(m)
        # return sorted(locations_in_groups[0]), sorted(locations_in_groups[1])

    # Step 2: Determine relevance
    relevant_locations = determine_relevance(locations_in_groups, package_option, components, weights)
    # relevant_locations = [key for key, value in relevant_locations]
    relevant_locations = [[key, value] for key, value in relevant_locations]

    return relevant_locations

