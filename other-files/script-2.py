import spacy
from collections import Counter
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import googlemaps
import requests
import json

gcp_api_key = "YOUR_GCP_KEY"
geonames_username = "YOUR_GEONAMES_USERNAME"

validations = {
    "episodes": [
        {
            "episode_file": "transcript-050924.txt",
            "data": [
                {
                    "location": "Golden Gate Bridge",
                    "coordinates": {
                        "latitude": 37.8199,
                        "longitude": -122.4783
                    }
                }
            ]
        }, 
        {
            "episode_file": "transcript-050924.txt",
            "data": [
                {
                    "location": "Golden Gate Bridge",
                    "coordinates": {
                        "latitude": 37.8199,
                        "longitude": -122.4783
                    }
                }
            ]
        }, 
        {
            "episode_file": "transcript-050924.txt",
            "data": [
                {
                    "location": "Golden Gate Bridge",
                    "coordinates": {
                        "latitude": 37.8199,
                        "longitude": -122.4783
                    }
                }
            ]
        }, 
        {
            "episode_file": "transcript-050924.txt",
            "data": [
                {
                    "location": "Golden Gate Bridge",
                    "coordinates": {
                        "latitude": 37.8199,
                        "longitude": -122.4783
                    }
                }
            ]
        }, 
        {
            "episode_file": "transcript-050924.txt",
            "data": [
                {
                    "location": "Golden Gate Bridge",
                    "coordinates": {
                        "latitude": 37.8199,
                        "longitude": -122.4783
                    }
                }
            ]
        }, 
        {
            "episode_file": "transcript-050924.txt",
            "data": [
                {
                    "location": "Golden Gate Bridge",
                    "coordinates": {
                        "latitude": 37.8199,
                        "longitude": -122.4783
                    }
                }
            ]
        }
    ]
}


def save_validation_json(validations):
    # Convert to a JSON string
    json_string = json.dumps(validations, indent=4)

    # Save to a file
    with open("episodes.json", "w") as f:
        f.write(json_string)

    print("JSON data formatted and saved!")


def filter_locations_geonames(locations, username):
    """
    Filter locations to validate they exist and are within the Bay Area using the Geonames API.
    """
    # Define Bay Area geographic bounds
    bay_area_bounds = {
        "north": 38.35,
        "south": 36.95,
        "east": -121.5,
        "west": -123.2
    }
    
    valid_locations = []
    
    for loc in locations:
        # Query the Geonames API for location data
        url = f"http://api.geonames.org/searchJSON?q={loc}&maxRows=1&username={username}"
        response = requests.get(url).json()
        # with open("geonames.json", "w") as json_file:
        #     json.dump(response, json_file)

        # Debugging: Print the response to inspect its structure
        # print(f"Response for location '{loc}': {response}")
        # break        
        # continue

        # Check if any results were returned
        if response["totalResultsCount"] > 0:
            # Get the first result's coordinates
            lat = response["geonames"][0]["lat"]
            lng = response["geonames"][0]["lng"]
            
            # Check if the location is within the Bay Area bounds
            if (bay_area_bounds["south"] <= float(lat) <= bay_area_bounds["north"] and
                bay_area_bounds["west"] <= float(lng) <= bay_area_bounds["east"]):
                valid_locations.append(loc)
                    
    return valid_locations

def filter_locations_googlemaps(locations, api_key):
    """
    Filter locations using Google Maps Geocoding API.
    """
    gmaps = googlemaps.Client(key=api_key)
    bay_area_bounds = {
        "northeast": {"lat": 38.0, "lng": -121.0},  # Upper-right corner
        "southwest": {"lat": 37.0, "lng": -123.0},  # Lower-left corner
    }

    valid_locations = []
    for loc in locations:
        geocode_result = gmaps.geocode(loc, region="us", bounds=bay_area_bounds)
        if geocode_result:
            valid_locations.append(loc)
    
    return valid_locations

def filter_locations_geopy(locations, region_name="Bay Area"):
    """
    Verify locations and filter those within the Bay Area.
    """
    geolocator = Nominatim(user_agent="location_verifier")
    bay_area_coords = {
        "lat_min": 37.0,  # Approximate latitude range for Bay Area
        "lat_max": 38.0,
        "lon_min": -123.0,  # Approximate longitude range for Bay Area
        "lon_max": -121.0,
    }

    valid_locations = []
    for loc in locations:
        try:
            geo_result = geolocator.geocode(loc, timeout=10)
            if geo_result:
                lat, lon = geo_result.latitude, geo_result.longitude
                # Check if the location falls within the Bay Area bounding box
                if (
                    bay_area_coords["lat_min"] <= lat <= bay_area_coords["lat_max"]
                    and bay_area_coords["lon_min"] <= lon <= bay_area_coords["lon_max"]
                ):
                    valid_locations.append(loc)
            else:
                print(f"Location not found: {loc}")
        except GeocoderTimedOut:
            print(f"Timeout error for location: {loc}")
    
    return valid_locations

def extract_named_entities(transcript_text):
    """
    Extract named entities categorized as physical places from the text.
    """
    nlp = spacy.load("en_core_web_sm")  # Load spaCy's English model
    doc = nlp(transcript_text)
    
    # Extract entities of interest
    location_entities = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT"}]
    location_entities = [loc.lower() for loc in location_entities] 
    return location_entities


def determine_relevance(locations):
    """
    Determine relevance based on frequency of mentions.
    """
    location_counts = Counter(locations)

    # Return sorted locations by frequency
    return location_counts.most_common()


def analyze_transcript(file_path):
    """
    Analyze a transcript file for location-based named entities and relevance.
    """
    with open(file_path, 'r') as f:
        transcript_text = f.read()
    
    # Step 1: Extract named entities
    locations = extract_named_entities(transcript_text)

    # print(locations)

    # Step 2: Filter locations by region
    # locations = filter_locations_geopy(locations)
    # locations = filter_locations_googlemaps(locations, gcp_api_key)
    # locations = filter_locations_bingmaps(locations, bing_api_key)
    locations = filter_locations_geonames(locations, geonames_username)

    # Step 2: Determine relevance
    relevant_locations = determine_relevance(locations)
    
    # Print results
    print("Detected Locations and Relevance Rankings:")
    for loc, count in relevant_locations:
        print(f"{loc}: {count}")
    
    # Most relevant location
    if relevant_locations:
        most_relevant = relevant_locations[0]
        print("\nMost Relevant Location:")
        print(f"{most_relevant[0]} (mentioned {most_relevant[1]} times)")
    else:
        print("No locations detected in the transcript.")

# Example Usage
if __name__ == "__main__":
    transcript_file = "transcript-050924.txt"  # Replace with your transcript file path
    analyze_transcript(transcript_file)
