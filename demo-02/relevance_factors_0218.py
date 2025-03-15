import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations
from math import radians, sin, cos, sqrt, atan2

from geodata_packages_0218 import determine_coords

def frequency(loc, all_locations, n_entities):
    """
    Determine the proportional frequency of a location in the text.
    """    
    return all_locations.count(loc)/n_entities


def title_mention(loc, title_ner):
    """
    Determine the inclusion of a location in the title segment.
    """ 
    if "sunol" in loc:
        print(loc, title_ner)
    return loc in title_ner


def haversine_distance(coord1, coord2):
    """
    Calculate the great-circle distance between two points 
    on the Earth (specified in decimal degrees).
    """

    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Earth's radius in kilometers (mean value)
    R = 6371.0  
    return R * c


def compute_centrality_scores(locations):
    """
    Given a dictionary with location names mapped to coordinates,
    returns a dictionary with centrality scores (higher is more central).
    """
    # Extract coordinates
    coords = np.array(list(locations.values()))

    # Compute centroid (mean of latitudes and longitudes)
    centroid = np.mean(coords, axis=0)

    # Compute distances from centroid
    distances = {loc: haversine_distance(coord, centroid) for loc, coord in locations.items()}

    # Normalize distances to get a score (invert so closer means higher score)
    max_dist = max(distances.values())
    scores = {loc: 1 - (dist / max_dist) for loc, dist in distances.items()} if max_dist > 0 else {loc: 1.0 for loc in locations}

    return scores, centroid


def get_cluster_info(all_locations, package_option):
    """
    Get cluster information for locations.
    """
    locations = list(set(all_locations))
    location_json = {}
    for loc in locations:
        location_json[loc] = determine_coords(package_option, loc)
    
    scores, _ = compute_centrality_scores(location_json)
    return scores, location_json


def cluster_distance(loc, cluster_info):
    """
    Determine the inclusion of a location in the text segment.
    """    
    return cluster_info[loc]


def build_graph(locations, sentences):
    """
    Build a graph of location co-occurrences in the text.
    """
    G = nx.Graph()

    for sentence in sentences:
        sentence_locs = [loc for loc in locations if loc in sentence]
        if len(sentence_locs) > 1:
            for loc1, loc2 in combinations(sentence_locs, 2):
                if G.has_edge(loc1, loc2):
                    G[loc1][loc2]['weight'] += 1
                else:
                    G.add_edge(loc1, loc2, weight=1)
    
    return G


def get_graph_info(sentences, all_locations):
    """
    Determine the relevance of a location in the text using graph metrics.
    """
    locations = list(set(all_locations))
    location_graph = build_graph(locations, sentences)

    # Compute centrality metric(s)
    pagerank = nx.pagerank(location_graph)

    # Store rank for each location
    ranking = {loc: pagerank.get(loc, 0) for loc in locations}

    # Sort locations by their PageRank score
    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    sorted_ranking = {loc[0]: loc[1] for loc in sorted_ranking}
    # print(sorted_ranking)
    return sorted_ranking


def graph_distance(loc, graph_info):
    """
    Determine the inclusion of a location in the text segment.
    """
    return graph_info[loc]


def determine_component(component,loc, all_locations, title_ner, n_entities, package_option, cluster_info, graph_info):
    """
    Determine the value of a component for a location.
    """
    if component == "freq":
        return frequency(loc, all_locations, n_entities)
    elif component == "segment":
        return title_mention(loc, title_ner)
    elif component == "cluster":
        return cluster_distance(loc, cluster_info)
    elif component == "graph":
        return graph_distance(loc, graph_info)