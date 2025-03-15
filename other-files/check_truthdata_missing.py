import json
import numpy as np
from rapidfuzz import fuzz, process
from transcript_analysis import analyze_transcript
from relevance_factors import haversine_distance

def validate(file_path, weights_list):
    with open(file_path, 'r') as file:
        data = json.load(file)

    mismatches = 0
    for episode in data["episodes"]:
        truth_names, truth_coords = episode["data"][0]["location"], episode["data"][0]["coordinates"]
        
        truth_names = [loc.lower() for loc in truth_names]

        lats = truth_coords["latitude"]
        lons = truth_coords["longitude"]
        truth_coords = [[pair[0], pair[1]] for pair in zip(lats, lons)]

        if len(truth_names) != len(truth_coords):
            print("mismatch: ", episode["source"]+"/"+episode["episode_file"])
            mismatches += 1
    
    print(f"Total mismatches: {mismatches}")
    

# Run the script
if __name__ == "__main__":
    weights_list = [[0.33, 0.33, 0.33, 0], [0.2, 0.50, 0.3, 0], [0.35, 0.50, 0.15, 0]]
    validate("episode-truths-v2.json", weights_list)

