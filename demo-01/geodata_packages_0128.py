import requests
import googlemaps
import pgeocode
import geocoder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

gcp_api_key = "YOUR_GOOGLE_CLOUD_PLATFORM_API_KEY"
geonames_username = "YOUR_GEONAMES_USERNAME"
geonames_max_rows = 1 # Limit the number of results to 1 per location

pg_nomi = pgeocode.Nominatim('US')

# Define Bay Area geographic bounds
bay_area_bounds = {
        "northeast": {"lat": 38.32, "lng": -121.81},  # Upper-right corner
        "southwest": {"lat": 36.9, "lng": -122.6},  # Lower-left corner
    }

bay_area_bbox = {
        "northeast": [38.32,  -121.81],  # Upper-right corner
        "southwest": [36.9, -122.6],  # Lower-left corner
    }

def filter_locations_pgeocode(locations):
    """
    Filter locations using pgeocode library.
    """
    south, north = bay_area_bounds["southwest"]["lat"], bay_area_bounds["northeast"]["lat"]
    west, east = bay_area_bounds["southwest"]["lng"], bay_area_bounds["northeast"]["lng"]
    valid_locations = []

    for loc in locations:
        try:
            result = pg_nomi.query_location(loc)
            if (south <= result.latitude <= north) and (west <= result.longitude <= east):
                valid_locations.append(loc)
        except:
            continue
    return valid_locations


def filter_locations_geonames(locations, username=geonames_username):
    """
    Filter locations to validate they exist and are within the Bay Area using the Geonames API.
    """
    south, north = bay_area_bounds["southwest"]["lat"], bay_area_bounds["northeast"]["lat"]
    west, east = bay_area_bounds["southwest"]["lng"], bay_area_bounds["northeast"]["lng"]
    valid_locations = []
    
    for loc in locations:
        # Query the Geonames API for location data within the Bay Area bounds
        # url = f"http://api.geonames.org/searchJSON?q={loc}&south={south}&north={north}&west={west}&east={east}&orderby=relevance&maxRows={max_rows}&username={username}"
        url = f"http://api.geonames.org/searchJSON?name={loc}&south={south}&north={north}&west={west}&east={east}&orderby=relevance&maxRows={geonames_max_rows}&username={username}"
        response = requests.get(url).json()

        # Check if any results were returned
        if response["totalResultsCount"] > 0:
            valid_locations.append(loc)
                    
    return valid_locations


def filter_locations_googlemaps(locations, api_key=gcp_api_key):
    """
    Filter locations using Google Maps Geocoding API.
    """
    gmaps = googlemaps.Client(key=api_key)
    valid_locations = []

    for loc in locations:
        geocode_result = gmaps.geocode(loc, region="us", bounds=bay_area_bounds)
        if geocode_result:
            valid_locations.append(loc)

    return valid_locations


def filter_locations_geocoder(locations):
    """
    Verify locations and filter those within the Bay Area.
    """
    south, north = bay_area_bounds["southwest"]["lat"], bay_area_bounds["northeast"]["lat"]
    west, east = bay_area_bounds["southwest"]["lng"], bay_area_bounds["northeast"]["lng"]
    valid_locations = []

    for loc in locations:
        geo_result = geocoder.geonames(loc, key=geonames_username, south=south, 
                                       north=north, west=west, east=east, maxRows=geonames_max_rows)
        # geo_result = geocoder.google(loc, key=gcp_api_key, region="us", proximity=bay_area_bbox)
        if geo_result:
            valid_locations.append(loc)
    
    return valid_locations


def filter_locations_geopy(locations):
    """
    Verify locations and filter those within the Bay Area.
    """
    geolocator = Nominatim(user_agent="location_verifier")
    south, north = bay_area_bounds["southwest"]["lat"], bay_area_bounds["northeast"]["lat"]
    west, east = bay_area_bounds["southwest"]["lng"], bay_area_bounds["northeast"]["lng"]

    valid_locations = []
    for loc in locations:
        try:
            geo_result = geolocator.geocode(loc, timeout=5)
            if geo_result:
                lat, lon = geo_result.latitude, geo_result.longitude
                if (south <= lat <= north) and (west <= lon <= east):
                    valid_locations.append(loc)
        except GeocoderTimedOut:
            print(f"Timeout error for location: {loc}")
    
    return valid_locations


def determine_filter(locations, package_option):
    if package_option == "geonames":
        return filter_locations_geonames(locations)
    elif package_option == "googlemaps":
        return filter_locations_googlemaps(locations)
    elif package_option == "geocoder":
        return filter_locations_geocoder(locations)
    elif package_option == "geopy":
        return filter_locations_geopy(locations)
    elif package_option == "pgeocode":
        return filter_locations_pgeocode(locations)
    

def geonames_coordinates(location, username=geonames_username):
    """
    Determine coordinates for a location using the Geonames API.
    """
    url = f"http://api.geonames.org/searchJSON?name={location}&maxRows={geonames_max_rows}&username={username}"
    response = requests.get(url).json()
    
    if response["totalResultsCount"] > 0:
        lat = response["geonames"][0]["lat"]
        lng = response["geonames"][0]["lng"]
        return [lat, lng]
    else:
        return [0, 0]


def determine_coords(locations, package_option):
    """
    Determine coordinates for a list of locations using the specified API.
    """
    if package_option == "geonames":
        return geonames_coordinates(locations)


