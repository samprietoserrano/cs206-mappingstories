import requests
import googlemaps
import pgeocode
import geocoder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

gcp_api_key = "YOUR_GOOGLE_CLOUD_PLATFORM_API_KEY"
geonames_username = "YOUR_GEONAMES_USERNAME"
geonames_max_rows = 1 # Limit the number of results to 1 per location    

def geonames_coordinates(location, username=geonames_username):
    """
    Determine coordinates for a location using the Geonames API.
    """
    url = f"http://api.geonames.org/searchJSON?name={location}&maxRows={geonames_max_rows}&username={username}&format=json"
    try:
        response = requests.get(url).json()

        # Check for API-specific error messages
        if "status" in response and "message" in response["status"]:
            print("Error in request: ", response["status"]["message"])
            return None
        
        if response["totalResultsCount"] > 0:
            # return response
            lat = response["geonames"][0]["lat"]
            lng = response["geonames"][0]["lng"]
            return [float(lat), float(lng)]
        else:
            return [0, 0]
    except:
        print(f"Error with requesting from Geonames.")
        return None
    

def geocoder_coordinates(location):
    """
    WORK IN PROGRESS.
    Determine coordinates for a location using the Geocoder API.
    """
    geocode_result = geocoder.osm(location)
    if geocode_result and geocode_result.latlng:
        return geocode_result.latlng
    return None


def determine_coords(package_option, location):
    """
    Determine coordinates for a list of locations using the specified API.
    """
    if package_option == "geonames":
        return geonames_coordinates(location)
    elif package_option == "geocoder":
        return geocoder_coordinates(location)
