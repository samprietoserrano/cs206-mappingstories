import sys
sys.dont_write_bytecode = True

# Description: This file contains the location_results function, which processes the transcript text
# to extract location-based named entities and their relevance scores. 

from analyzer_transcript_analysis import analyze_transcript

components = ["freq", "segment", "cluster", "graph"]
weights_list = [[0.3, 0.4, 0.15, 0.15]]

def location_results(title, transcript_text):
    text_info = [title, transcript_text]

    # Analyze the transcript for location-based named entities and relevance
    # OUTPUT FORMAT: loc_coords = {loc: [lat, lon]}, relevant_locations = [[loc, score]]
    _, relevant_locations = analyze_transcript(text_info, "geonames", components, weights_list)

    locations = format_locations(relevant_locations[0]) # assuming only one weight list is tested

    return locations[:5] if len(locations) > 5 else locations


def format_locations(locations):
    # Find maximum score
    max_score = max(max(score for _, score in locations), 0.0000000000001)
    
    # Transform each entry: title case and normalize scores
    processed = [(location.title(), score / max_score) for location, score in locations]

    return processed
