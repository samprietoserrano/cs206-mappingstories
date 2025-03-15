import sys
sys.dont_write_bytecode = True

import json
import numpy as np
import time
import os
from rapidfuzz import fuzz, process, utils
from transcript_analysis import analyze_transcript
from relevance_factors import haversine_distance

# package_options = ["geonames", "googlemaps", "geocoder", "geopy", "pgeocode"]
components = ["freq", "segment", "cluster", "graph"]

threshold = 75 # Threshold for a fuzzy match (e.g., 80% similarity)

def compare_groups(found_locations, found_coords, truth_locations, truth_coords):
    """
    Compare two groups of locations for matches.
    """
    res = ""
    if not found_locations or not truth_locations or not found_coords or not truth_coords:
        print("compare_groups(): An input array of location names was empty.")
        return res

    # Extract latitude and longitude from truth coordinates
    lats = truth_coords["latitude"]
    lons = truth_coords["longitude"]
    truth_coords = [[pair[0], pair[1]] for pair in zip(lats, lons)]

    # Extract coordinates for found locations
    found_coords = [found_coords[loc] for loc in found_locations if loc in found_coords]

    for key in truth_locations:
        # Check for a fuzzy TEXT match
        matches = process.extract(key, found_locations, scorer=fuzz.partial_ratio,
                                  score_cutoff=threshold, limit=len(found_locations),
                                  processor=utils.default_process)
        if matches:
            if res != "":
                # res += "\n"
                res += " + "
            # print_list = print_formatted_list(matches, True) if isinstance(matches, list) else matches
            # res += f"Good text-match for truth '{key}' within {print_list}"
            res += "textmatch"
            break

        # if res != "":
        #     print("moving beyond textmatch")

        # Check for a GEOGRAPHIC match
        key_coords = truth_coords[truth_locations.index(key)]
        for coord in found_coords:
            if haversine_distance(key_coords, coord) < 20:
                if res != "":
                    # res += "\n"
                    res += " + "
                # close_loc = found_locations[found_coords.index(coord)]
                # res += f"Good geo-match for truth '{key}' within {close_loc}"
                res += "geomatch"
                break

    return res


def print_formatted_list(lst, fuzz_print=False):
    """
    Print a list in a formatted way.
    """
    # Util function to convert a list to a string
    def string_of_items(lst):
        return str(lst).replace("[", "").replace("]", "").replace("'", "")
    
    # Determine the number of chunks to process
    chunks_per = 1 if fuzz_print else 4
    tab_str = "\t" * 4

    # Process the list in chunks
    res = "\n" + tab_str + "[" if fuzz_print else "NER from text: ["
    for i in range(0, len(lst), chunks_per):  # Process in chunks
        if fuzz_print:
            chunk = lst[i]
        else:
            chunk = lst[i:i+chunks_per] # Get a sublist of items
        res += string_of_items(chunk) + ",\n" + tab_str # Append the chunk to the string

    return res[:-6] + "]"


def validate(file_path, weights_list):
    # Start time tracking for the entire function
    start_time = time.time()

    # Load the JSON data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Prepare log file name with automatic suffixing
    # log_filename = "backendviz_log.txt"
    log_filename = "validation_log.txt"
    # log_filename = "v_ner_log.txt"
    base_name, ext = os.path.splitext(log_filename)
    counter = 1
    while os.path.exists(log_filename):
        log_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    with open(log_filename, 'w') as log_file:
        def log_print(*args):
            message = " ".join(str(arg) for arg in args)
            print(message, flush=True)  # Force immediate print
            log_file.write(message + "\n")
            log_file.flush()  # Force immediate write

        matches = list(np.array([0.0] * len(weights_list)))
        episodes_processed = 0
        # tmp_skip, seek = 0, 1
        for episode in data["episodes"]:
            loop_start_time = time.time()  # Track time for each loop iteration

            # tmp_skip += 1
            # if tmp_skip < seek:
            #     continue
            # elif tmp_skip > seek:
            #     break
            
            # Extract episode information from truth data
            title, filename = episode["data"][0]["title"], episode["episode_file"]

            # if filename != "transcript-060323.txt":
            #     continue
            truth_names, truth_coords = episode["data"][0]["location"], episode["data"][0]["coordinates"]
            text_info = [title, "transcripts-2/all-compiled/" + filename]

            # Analyze the transcript for location-based named entities and relevance
            # OUTPUT FORMAT: loc_coords = {loc: [lat, lon]}, relevant_locations = [[loc, score]]
            loc_coords, relevant_locations = analyze_transcript(text_info, "geonames", components, weights_list)
            # text_ner = analyze_transcript(text_info, "geonames", components, weights_list, only_ner=True)
            # backend_info = analyze_transcript(text_info, "geonames", components, weights_list, backend_catch=True)

            # Run the comparison function for each set of weights
            log_print("\nNEW EPISODE BEGINS ->", filename)
            for i in range(len(weights_list)):
                log_print("\n"+f"Outcomes for weights {weights_list[i]}:")
                
                loc_names = [loc[0] for loc in relevant_locations[i]] 
                log_print(f"Episode title: '{title}'") 
                log_print(print_formatted_list(loc_names))
                log_print("Truth Locations: ", truth_names)

                # Compare the found locations with the truth locations
                # comparison = compare_groups(loc_names, [], truth_names, [])
                comparison = compare_groups(loc_names, loc_coords, truth_names, truth_coords)
                if comparison != "":
                    # log_print(comparison) # choosing to not print the comparison results in details
                    # log_print("Match found ✅.")
                    log_print(f"Match found via {comparison} ✅.")
                    matches[i] += 1

            episodes_processed += 1
            loop_end_time = time.time()  # End timing for the loop iteration
            log_print(f"\nEpisode {filename} done. (Loop Duration: {loop_end_time - loop_start_time:.4f} seconds)\n")
            # break
        
        # Calculate and log the total accuracy for each set of weights
        accuracy = [n / episodes_processed for n in matches]
        for i in range(len(accuracy)):
            log_print(f"Total accuracy {accuracy[i]:.4f} using weights {weights_list[i]}.")

        # Log total execution time
        end_time = time.time()
        log_print(f"\nTotal execution time: {end_time - start_time:.4f} seconds.")
        

# Run the script
if __name__ == "__main__":
    weights_list = [[0.33, 0.33, 0.33, 0], [0.2, 0.50, 0.3, 0], [0.35, 0.50, 0.15, 0], 
                    [0.25, 0.25, 0.25, 0.25], [0.3, 0.45, 0.15, 0.1], [0.3, 0.4, 0.15, 0.15]]
    # weights_list = [[0, 0, 0, 0]]
    # weights_list = [[0.33, 0.33, 0.33, 0], [0.3, 0.4, 0.15, 0.15]]
    validate("episode-truths-v4.json", weights_list)
    # print(len())
            

    

