import json
from rapidfuzz import fuzz, process

from transcript_analysis import analyze_transcript

# package_options = ["geonames", "googlemaps", "geocoder", "geopy", "pgeocode"]
# package_options = ["geocoder"]

components = ["freq", "segment", "cluster", "graph"]

# weights = [0.3, 0.4, 0.2, 0.1]
# weights = [0.33, 0.33, 0.33, 0] 

threshold = 80 # Threshold for a fuzzy match (e.g., 80% similarity)

def compare_groups(found_locations, truth_locations):
    if not found_locations or not truth_locations:
        return False
    
    truth_locations = [loc.lower() for loc in truth_locations]
    
    for key in truth_locations:
        best_match = process.extractOne(key, found_locations, scorer=fuzz.partial_ratio)
        if best_match and best_match[1] >= threshold:
            print(f"Good match for truth '{key}' within {best_match}")
            return True
    print(f"No good match for truth '{truth_locations}' within {found_locations}.")
    return False


def validate(file_path, weights):
    with open(file_path, 'r') as file:
        data = json.load(file)

    ep_log = {}

    matches = 0
    tmp_skip, seek = 0, 7
    for episode in data["episodes"]:
        # tmp_skip += 1
        # if tmp_skip < seek:
        #     continue
        # elif tmp_skip > seek:
        #     break
        title, filename, truths = episode["data"][0]["title"], episode["episode_file"], episode["data"][0]["location"]
        text_info = [title, "transcripts/" + filename]
        relevant_locations = analyze_transcript(text_info, "geonames", components, weights)

        for i in range(len(weights)):
            print("Relevant Locations: ", relevant_locations[i])
            print("Truth Locations: ", episode["data"][0]["location"])

            if compare_groups(relevant_locations[i], truths):
                matches += 1
                # print(f"Validation correct for {episode['episode_file']} using {option} filter.")
            # else:
                # print(f"Validation wrong for {episode['episode_file']} using {option} filter.")  

            ep_log[filename] = {"relevant": relevant_locations, "truth": truths}     
            print(f"Episode {filename} done."+"\n")

        accuracy = matches / len(data["episodes"])
        print(f"Total accuracy {accuracy:.4f} using weights {weights}."+"\n")
    

# Run the script
if __name__ == "__main__":
    weights = [[0.33, 0.33, 0.33, 0], [0.2, 0.50, 0.3, 0]]
    for weight in weights:
        validate("episode-truths.json", weight)

