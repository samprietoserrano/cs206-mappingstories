import json
import os
from rapidfuzz import fuzz, process

from transcript_analysis_0128_steve import analyze_transcript, analyze_transcript_simple

filter_options = ["geonames", "googlemaps", "geocoder", "geopy", "pgeocode"]
filter_options = ["geonames"]
threshold = 80 # Threshold for a fuzzy match (e.g., 80% similarity)

def compare_groups(found_locations, truth_locations):
    if not found_locations or not truth_locations:
        return False
    
    truth_locations = [loc.lower() for loc in truth_locations]
    
    for key in truth_locations:
        best_match = process.extractOne(key, found_locations, scorer=fuzz.partial_ratio)
        if best_match and best_match[1] >= threshold:
            # print(f"Good match for {key} (truth): {best_match}")
            return True
    return False


def validate(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    ep_results = []
    opt_results = {}
    for option in filter_options:
        opt_results[option] = 0
    tot_acc = 0

    
    for episode in data["episodes"]:
        text_info = [episode["data"][0]["title"], "demo-01/transcripts/" + episode["episode_file"]]
    
        ep_acc = 0
        ep_match_any = False
        for option in filter_options:
            # option = "geocoder"
            print("Truth Locations: ", episode["data"][0]["location"])
            relevant_locations = analyze_transcript(text_info, option)
            print(f"Relevant Locations with {option}: ", relevant_locations)
            if compare_groups(relevant_locations, episode["data"][0]["location"]):
                print(f"✅ Validation correct for {episode['episode_file']} using {option} filter."+"\n")
                ep_acc += 1
                ep_match_any = True
                # opt_results[option] += 1
            else:
                print(f"❌ Validation wrong for {episode['episode_file']} using {option} filter."+"\n")
            print(f"Episode {episode['episode_file']} with filter '{option}' done.")

        ep_results.append({"episode_file": episode["episode_file"], "ep_accuracy": ep_acc/len(filter_options)})    
        
        if ep_match_any:
            tot_acc += 1

        print(f"Episode {episode['episode_file']} done."+"\n")
        print()

    # for opt in opt_results:
    #     print(f"Filter option: '{opt}', Accuracy: {opt_results[opt]/len(data['episodes'])}")
    print()
    for ep in ep_results:
        print(ep)
    print()
    print(f"Total accuracy: {tot_acc/len(data['episodes'])}")
    
    #optional, results of ep by option


def validate_simple(file_path, title, loc_truths):
    with open(file_path, 'r') as f:
        text = f.read()

    for option in filter_options:
        relevant_locations = analyze_transcript_simple([title, text], option, simple=False)

        if relevant_locations:
            # Most common locations
            print(f"Detected Locations and Relevance Rankings using {option} filter:")
            for loc, count in relevant_locations:
                print(f"{loc}: {count}")
            
            # Validate the most relevant location
            print(f"Validation with {option}: ", compare_groups([relevant_locations[0][0]], loc_truths))

            # Print the most relevant location
            most_relevant = relevant_locations[0]
            print("Most Relevant Location:")
            print(f"{most_relevant[0]} (mentioned {most_relevant[1]} times)")
        else:
            print("No locations detected in the transcript.")

        print("\n\n")

# Run the script
if __name__ == "__main__":
    validate("././episode-truths.json")
    # print(os.path.exists('./demo-01/transcripts/transcript-010225.txt'))

