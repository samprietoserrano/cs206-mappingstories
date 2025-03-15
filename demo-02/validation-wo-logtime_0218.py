import json
import numpy as np
import time
import os
from rapidfuzz import fuzz, process
from transcript_analysis_0218 import analyze_transcript
from relevance_factors_0218 import haversine_distance

# package_options = ["geonames", "googlemaps", "geocoder", "geopy", "pgeocode"]

components = ["freq", "segment", "cluster", "graph"]
# components = ["freq", "segment"]


threshold = 75 # Threshold for a fuzzy match (e.g., 80% similarity)

def compare_groups(found_locations, found_coords, truth_locations, truth_coords):
    if not found_locations or not truth_locations or not found_coords or not truth_coords:
        print("compare_groups: An input array was empty.")
        return False
    
    truth_locations = [loc.lower() for loc in truth_locations]

    lats = truth_coords["latitude"]
    lons = truth_coords["longitude"]
    truth_coords = [[pair[0], pair[1]] for pair in zip(lats, lons)]

    found_coords = [found_coords[loc] for loc in found_locations if loc in found_coords]

    for key in truth_locations:
        best_match = process.extractOne(key, found_locations, scorer=fuzz.partial_ratio)
        if best_match and best_match[1] >= threshold:
            # print(f"Good match for truth '{key}' within {best_match}")
            return True
        
        key_coords = truth_coords[truth_locations.index(key)]
        for coord in found_coords:
            if haversine_distance(key_coords, coord) < 20:
                close_loc = found_locations[found_coords.index(coord)]
                # print(f"Good geo-match for truth '{key}' within {close_loc}")
                return True

    # print(f"No good match for truth '{truth_locations}' within {found_locations}.")
    return False


def validate(file_path, weights_list):
    # Start time tracking for the entire function
    # start_time = time.time()

    # Load the JSON data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Prepare log file name with automatic suffixing
    # log_filename = "validation_log.txt"
    # base_name, ext = os.path.splitext(log_filename)
    # counter = 1
    # while os.path.exists(log_filename):
    #     log_filename = f"{base_name}_{counter}{ext}"
    #     counter += 1

    # with open(log_filename, 'w') as log_file:
        # def log_print(*args):
        #     message = " ".join(str(arg) for arg in args)
        #     print(message)
        #     log_file.write(message + "\n")

        matches = list(np.array([0.0] * len(weights_list)))
        episodes_processed = 0
        tmp_skip, seek = 0, 2
        for episode in data["episodes"]:
            # 010225, 011124
            # if "transcript-010225.txt" not in episode["episode_file"]:
            #     continue

            loop_start_time = time.time()  # Track time for each loop iteration

            # tmp_skip += 1
            # if tmp_skip < seek:
            #     continue
            # elif tmp_skip > seek:
            #     break
            # if tmp_skip == seek:
            #     continue

            title, filename = episode["data"][0]["title"], episode["episode_file"]
            truth_names, truth_coords = episode["data"][0]["location"], episode["data"][0]["coordinates"]
            text_info = [title, "transcripts/all-compiled/" + filename]

            print(f"\nEpisode {filename} begins.\n")

            loc_coords, relevant_locations = analyze_transcript(text_info, "geonames", components, weights_list)
            # time.sleep(2)
            # continue
            print("\nNEW EPISODE BEGINS ->")
            for i in range(len(weights_list)):
                print("\n"+f"Outcomes for weights {weights_list[i]}:")
                
                loc_names = [loc[0] for loc in relevant_locations[i]] 
                print("Top 3 Rated Locations: ", relevant_locations[i]) # can output the scores with the locs if needed
                print("Truth Locations: ", truth_names)

                if compare_groups(loc_names, loc_coords, truth_names, truth_coords):
                    print("Match found ✅.")
                    matches[i] += 1

            episodes_processed += 1
            loop_end_time = time.time()  # End timing for the loop iteration
            print(f"\nEpisode {filename} done. (Loop Duration: {loop_end_time - loop_start_time:.4f} seconds)\n")

        # return
        accuracy = [n / episodes_processed for n in matches]
        for i in range(len(accuracy)):
            print(f"Total accuracy {accuracy[i]:.4f} using weights {weights_list[i]}.")

        # Log total execution time
        # end_time = time.time()
        # print(f"\nTotal execution time: {end_time - start_time:.4f} seconds.")
        

# Run the script
if __name__ == "__main__":
    weights_list = [[0.33, 0.33, 0.33, 0], [0.2, 0.50, 0.3, 0], [0.35, 0.50, 0.15, 0], 
                    [0.25, 0.25, 0.25, 0.25], [0.3, 0.45, 0.15, 0.1], [0.3, 0.4, 0.15, 0.15]]
    weights_list = [[0.3, 0.7, 0, 0]]
    validate("episode-truths-v2.json", weights_list)

