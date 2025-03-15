geonames_username = "samxp"
geonames_max_rows = 1 # Limit the number of results to 1 per location





import geocoder

# Define Bay Area geographic bounds
bay_area_bounds = {
        "northeast": {"lat": 38.32, "lng": -121.81},  # Upper-right corner
        "southwest": {"lat": 36.9, "lng": -122.6},  # Lower-left corner
    }

def geocoder_test(locations):
    """
    Verify locations and filter those within the Bay Area.
    """
    south, north = bay_area_bounds["southwest"]["lat"], bay_area_bounds["northeast"]["lat"]
    west, east = bay_area_bounds["southwest"]["lng"], bay_area_bounds["northeast"]["lng"]
    valid_locations = []

    for loc in locations:
        geo_result = geocoder.geonames(loc, key=geonames_username, south=south, 
                                       north=north, west=west, east=east, maxRows=geonames_max_rows)
        if geo_result:
            valid_locations.append(loc)
    
    return valid_locations

sample = ["San Bruno", "Florida", "Brooklyn Bridge", "Tokyo"]
print("\n\nSample locations: ", sample, "\n")
print("\nValid Locations: ", geocoder_test(sample), "\n\n")