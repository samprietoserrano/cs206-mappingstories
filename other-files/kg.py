import spacy
import requests
import networkx as nx
import pandas as pd
from collections import Counter

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Function to extract locations using Named Entity Recognition (NER)
def extract_locations(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT"}]
    return locations

# Function to query Wikidata for geographic relationships
def get_wikidata_info(location):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "search": location,
        "language": "en"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "search" in data and data["search"]:
        return data["search"][0]["id"], data["search"][0]["label"]
    return None, None

# Function to build a knowledge graph of locations
def build_knowledge_graph(locations):
    G = nx.Graph()

    for loc in locations:
        entity_id, entity_label = get_wikidata_info(loc)
        if entity_id:
            G.add_node(entity_label, id=entity_id)

    return G

# Function to determine the most central location
def get_main_location(graph):
    if len(graph.nodes) == 0:
        return None
    centrality = nx.degree_centrality(graph)
    return max(centrality, key=centrality.get)

# Load and process the text file
with open("transcripts/transcript-050924.txt", "r", encoding="utf-8") as file:
    text = file.read()

locations = extract_locations(text)
graph = build_knowledge_graph(locations)
main_location = get_main_location(graph)

print("Extracted Locations:", locations)
print("Main Location:", main_location)