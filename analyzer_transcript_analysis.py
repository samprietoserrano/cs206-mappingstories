import sys
sys.dont_write_bytecode = True

import re
import spacy
import numpy as np
import pycountry
from collections import Counter
from rapidfuzz import fuzz, process, utils

from relevance_factors import determine_component, get_cluster_info, get_graph_info

# Load spaCy's English model
# nlp = spacy.load("en_core_web_sm") 
# nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_trf", disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
nlp.add_pipe('sentencizer')


def extract_named_entities(transcript_text):
    """
    Run NER on the title and full transcript text.
    """   
    ner_initial, sentences_initial = ner_process(transcript_text)
    ner_clean, sentences_clean = clean_ner_list(ner_initial, sentences_initial)

    return ner_clean, sentences_clean
    # return ner_initial, sentences_initial


def ner_process(transcript):
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
    location_entities = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT"}]
    # location_entities = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT", "ORG"}]
    # location_entities = [loc.lower() for loc in set(location_entities)] 

    # Extract sentences
    sentences = [sent.text for sent in doc.sents]

    return location_entities, sentences


def clean_ner_list(found_locations, sentences):
    """
    Clean the list of named entities extracted from the text.
    """
    # print(f"Initial locations: {found_locations}")

    # Remove common article words (for better fuzzy matching) and remove country/state names
    delimiters = r"[\/\\]"  # Regex pattern to match both '/' and '\'

    qkclean_loc_list = [locx for loc in found_locations for locx in re.split(delimiters, loc)]
    qkclean_loc_list = [re.sub(r'^(the|this|a|an)\s+', '', loc.lower().strip(), flags=re.IGNORECASE) for loc in qkclean_loc_list]
    qkclean_loc_set = [ent for ent in set(qkclean_loc_list) if not is_country_or_state(ent)]

    # print(f"Quick cleaned locations: {qkclean_loc_set}")

    # Compile similar location names, in format: [noalt1, noalt2, [alt1, alt2, ...], [alt3, alt4, ...], ...]
    compiled = []
    for loc in qkclean_loc_set:
        matches = process.extract(loc, qkclean_loc_set, scorer=fuzz.token_set_ratio,
                                    score_cutoff=90, processor=utils.default_process)
        match_names = [match[0] for match in matches]
        if len(match_names) > 1:
            match_names = sorted(match_names, key=len, reverse=True)    
            compiled.append(match_names)
        else: 
            compiled.append(loc)

    # Replace location names with longest string alternate
    replacement_map = create_location_map(get_unique_entries(compiled))
    replaced_locations = [replacement_map[loc] for loc in qkclean_loc_list if loc.lower() in replacement_map]

    # Update sentences with primary location names
    updated_sentences = [replace_sentences(sentence, replacement_map) for sentence in sentences]

    # Print replacement map
    # for key, value in replacement_map.items():
    #     if key != value:
    #         print(f"Replacing '{key}' with '{value}'")

    # print(f"Cleaned locations: {replaced_locations}")

    return replaced_locations, updated_sentences


def replace_sentences(sentence, replacement_map):
    """
    Replace location names in a sentence with the primary name.

    NOTE: This function could be cleaner in terms of replacing the full 
    location entity as origingally extracted, but since we will only care 
    about occurances of our new version of the loc in the sentence, this
    is sufficient.
    """
    pattern = re.compile(r'\b(' + '|'.join(re.escape(loc) for loc in replacement_map.keys()) + r')\b', re.IGNORECASE)
    
    def replacement(match):
        return replacement_map[match.group(0).lower()]
    
    return pattern.sub(replacement, sentence)


def create_location_map(location_list):
    """
    Create a mapping of alternative location names to primary names.
    """
    # Convert list to a dictionary mapping alternative names to primary location
    location_map = {}
    for item in location_list:
        if isinstance(item, list):
            primary_location = item[0]  # First entry in the list is the main name
            for alt in item:
                location_map[alt.lower()] = primary_location.lower()
        else:
            location_map[item.lower()] = item.lower()

    return location_map


def get_unique_entries(lst):
    """
    Remove duplicate entries from a list of lists.
    """
    unique_strings = set()  # To track unique strings
    unique_lists = []  # To store unique lists

    for item in lst:
        if isinstance(item, list):
            sorted_item = sorted(item)  # Normalize by sorting
            if sorted_item not in unique_lists:
                sorted_item = sorted(sorted_item, key=len, reverse=True)
                unique_lists.append(sorted_item)
        else:
            unique_strings.add(item)  # Add unique strings

    # Merge results: Convert list of lists back to list format
    packed_list = list(unique_strings) + unique_lists
    return packed_list
    # unpacked_list = [item[0] if isinstance(item, list) else item for item in packed_list]

    # return [packed_list, unpacked_list]


def is_country_or_state(entity):
    """
    Returns True if entity is a country or US state.
    """
    # Check if it's a country
    if pycountry.countries.get(name=entity) or any(entity in country.name for country in pycountry.countries):
        return True
    
    # Check if it's a US state
    if any(entity in state.name.lower() for state in pycountry.subdivisions if state.country_code == "US"):
        return True
    return False


def determine_relevance(locations, sentences, title, package_option, components, weights_list, simple=False):
    """
    Determine relevance based on frequency of mentions.
    """
    cluster_info, graph_info, location_json = [], [], {}
    if "cluster" in components:
        cluster_info, location_json = get_cluster_info(locations, package_option)

    if "graph" in components:
        graph_info = get_graph_info(sentences, locations)

    scores_dict = {}
    n_entities = len(locations)
    n_length = sum([len(sentence) for sentence in sentences])
    for loc in list(set(locations)):

        score_parts = []
        for component in components:
            unweighted_score = determine_component(component, loc, locations, title, [n_entities, n_length], package_option, cluster_info, graph_info)
            score_parts.append(unweighted_score)

        min_len = min(len(weights_list), len(score_parts))
        scores_dict[loc] = [np.dot(np.array(weights[:min_len]),  np.array(score_parts[:min_len])) for weights in weights_list]

    return location_json, [Counter(dict(zip(scores_dict.keys(), values))).most_common() for values in zip(*scores_dict.values())]
    # return {}, []
    # return location_json, []


def analyze_transcript(text_info, package_option, components, weights_list, only_ner=False):
    """
    Analyze a transcript file for location-based named entities and relevance.
    """
    transcript_text = text_info[1]
    
    # Step 1: Extract named entities
    locations, sentences = extract_named_entities(transcript_text)

    if only_ner:
        return set(locations)

    # Step 2: Determine relevance
    location_json, relevant_locations = determine_relevance(locations, sentences, text_info[0], package_option, components, weights_list)

    return location_json, relevant_locations
    # return locations_in_groups, sentences
    # return relevant_locations