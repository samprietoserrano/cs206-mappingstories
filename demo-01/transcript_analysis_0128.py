import spacy
from collections import Counter

from geodata_packages_0128 import determine_filter

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
    entire_transcript = transcript_text.split()
    first_200 = " ".join(entire_transcript[:200])
    last_200 = " ".join(entire_transcript[-200:])

    ner_title = extract_named_entities_in_group(title)
    ner_full = extract_named_entities_in_group(transcript_text)
    ner_first200 = extract_named_entities_in_group(first_200)
    ner_last200 = extract_named_entities_in_group(last_200)

    return [ner_title, ner_full, ner_first200, ner_last200]


def extract_named_entities_in_group(transcript):
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
    location_entities = [loc.lower() for loc in location_entities] 

    return location_entities


def filter_locations(locations, package_option):
    """
    Filter locations to validate they exist and are within the Bay Area using different API.
    """
    if len(locations) != 4:
        all_locations = locations
    else:
        all_locations = locations[0] + locations[1] + locations[2] + locations[3]

    valid_locations = determine_filter(all_locations, package_option)

    return valid_locations


def determine_relevance(initial_locations, valid_locations, simple=False):
    """
    Determine relevance based on frequency of mentions.
    """
    location_counts = Counter(valid_locations)

    if not simple:
        for loc in location_counts:
            if loc in initial_locations[0]: # amplify title mentions
                location_counts[loc] *= 2

            if loc in initial_locations[2] or loc in initial_locations[3]: # amplify first and last 200 mentions
                location_counts[loc] *= 1.5

    return location_counts.most_common(3)


def analyze_transcript(text_info, package_option):
    """
    Analyze a transcript file for location-based named entities and relevance.
    """
    with open(text_info[1], 'r') as f:
        transcript_text = f.read()
    
    # Step 1: Extract named entities
    locations = extract_named_entities(text_info[0], transcript_text)

    # Step 2: Filter locations by region
    valid_locations = filter_locations(locations, package_option)
    # print(f"Valid Locations with {package_option}: ", valid_locations)

    # Step 2: Determine relevance
    relevant_locations = determine_relevance(locations, valid_locations)
    relevant_locations = [key for key, value in relevant_locations]

    # relevant_coords = determine_coords(relevant_locations,)
    # return relevant_locations, relevant_coords

    return relevant_locations


def analyze_transcript_simple(transcript, filter_option, simple=True):
    """
    Analyze a transcript text for location-based named entities and relevance.
    This simple version does not use a relevance equation. 
    """
    # Step 1: Extract named entities
    initial_locations = extract_named_entities(transcript[0], transcript[1])

    # Step 2: Filter locations by region
    valid_locations = filter_locations(initial_locations, filter_option)

    # Step 3: Determine relevance
    relevant_locations = determine_relevance(initial_locations, valid_locations, simple=simple)

    return relevant_locations

