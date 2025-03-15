from collections import Counter

def relevance_test(title_section, key_section, valid_locations):
    """
    Determine relevance based on frequency of mentions.
    """
    location_counts = Counter(valid_locations)
    for loc in location_counts:
        if loc in title_section: # amplify title mentions
            location_counts[loc] *= 2

        if loc in key_section: # amplify first and last 200 mentions
            location_counts[loc] *= 1.5

    return location_counts.most_common()

sample_title = ["Alameda"]
sample_key = ["Alameda", "Berkeley"]
sample_valid = ["San Bruno", "Alameda", "Berkeley"]
print("\nSample locations: ", sample_valid, "\n")

relevant_locations = relevance_test(sample_title, sample_key, sample_valid)
for loc, count in relevant_locations:
        print(f"{loc}: {count}")