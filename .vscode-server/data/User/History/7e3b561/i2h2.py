import geopandas as gpd
import pycountry
from shapely.ops import nearest_points


def calculate_country_distances():
    # Load the world dataset from GeoPandas
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Filter out entries without valid geometries or with multipolygon geometries
    world = world[world.geometry.type == 'Polygon']

    # Ensure the GeoDataFrame uses the WGS84 coordinate system (latitude/longitude)
    world = world.to_crs(epsg=4326)

    # Create a dictionary to store the shortest distances
    distance_map = {}

    # Get a list of country names from pycountry
    countries = [country.name for country in pycountry.countries]

    # Filter the world GeoDataFrame to include only countries from the pycountry list
    world = world[world['name'].isin(countries)]

    # Loop through each country to compute the shortest distance to every other country
    for i, country1 in world.iterrows():
        for j, country2 in world.iterrows():
            if country1['name'] != country2['name']:
                # Find the nearest points
                p1, p2 = nearest_points(country1.geometry, country2.geometry)
                # Calculate the distance in degrees
                distance = p1.distance(p2)
                # Convert the distance to kilometers using the approximate conversion factor
                distance_km = distance * 111.32  # 1 degree latitude ~ 111.32 km
                distance_map[(country1['name'], country2['name'])] = distance_km

    # Example output for a few country pairs
    for key, value in list(distance_map.items())[:10]:
        print(f"The shortest distance between {key[0]} and {key[1]} is {value:.2f} km.")
    
    
    # Define the output file path
    output_file = 'country_distances.json'

    # Save the distance map to a file
    with open(output_file, 'w') as f:
        json.dump(distance_map, f, indent=4)

    print(f"Distance calculations saved to {output_file}")

if __name__ == "__main__":
    calculate_country_distances()
Step 2: Run distance_calculator.py
Run this script to generate the country_distances.json file:

sh
Copy code
python distance_calculator.py
This script will output a country_distances.json file containing the distances between countries.

Step 3: Use country_distances.json in main.py
Here's your main.py script updated to use the generated country_distances.json:

python
Copy code
import argparse
import pickle
import json
import math
from geopy.distance import great_circle
from aquatools.topo.Traceroutes import RIPETraceroute

def calculate_radius(curr_min_rtt, prev_min_rtt):
    if curr_min_rtt is None:
        print("Error when parsing RTTs; Cannot Calculate Radius")
        return None
    
    rtt_diff = abs(curr_min_rtt - prev_min_rtt)
    speed_of_light = 299.792458  # Speed of light in km/ms
    radius = (rtt_diff / 2) * ((speed_of_light) * (2 / 3))  # travel speed of optic fiber
    return radius

def is_within_radius(lat1, lon1, lat2, lon2, radius):
    if None in [lat1, lon1, lat2, lon2]:
        print(f"Invalid coordinates received: {lat1}, {lon1}, {lat2}, {lon2}")
        return False
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon1 - lat2

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    f = 1 / 298.257223563
    b = (1 - f) * 6371

    distance = c * b
    
    if distance <= radius:
        return True 
    else:
        print("A wrong IP mapping has occurred")
        return False

def find_nearest_points(country1, country2, distance_map):
    # Find and return the shortest distance between country1 and country2
    return distance_map.get((country1, country2), None)

def process_traceroute_data(tr, distance_map):
    floor_test_results = []
    valid_data_points = []
    all_data_points = []

    prev_latitude, prev_longitude, prev_min_rtt = None, None, None
    prev_city, prev_region, prev_country = None, None, None
    first_valid_row = True
    
    for hop in tr.hops:
        ip_address, rtt = hop.addr, hop.rtt
        geolocation = hop.geoloc
        city, region, country = geolocation.city, geolocation.state, geolocation.country

        all_data_points.append({
            'ip_address': ip_address,
            'rtt': rtt,
            'geolocation': geolocation._asdict()  # Convert namedtuple to dictionary
        })

        if rtt is None:
            first_valid_row = True  # Reset for the next valid row
            continue  # Skip if RTT is invalid

        if city == 'None' or region == 'None':
            # Use previous valid geolocation
            city, region, country = prev_city, prev_region, prev_country

        if city == 'None' or region == 'None':
            country1 = country.strip()
            country2 = "SG"  # Default to Singapore as the fallback (or adjust as needed)
            if not country1 or len(country1) != 2:
                print(f"Invalid country code detected: {country1}")
                continue
            nearest_points = find_nearest_points(country1, country2, distance_map)
            if nearest_points is None:
                first_valid_row = True  # Reset for the next valid row
                continue  # Skip if nearest points calculation fails
            latitude, longitude = nearest_points

            valid_data_points.append({
                'ip_address': ip_address,
                'rtt': rtt,
                'latitude': latitude,
                'longitude': longitude
            })
            if first_valid_row:
                prev_latitude, prev_longitude, prev_min_rtt = latitude, longitude, rtt
                first_valid_row = False
            continue
        else:
            latitude, longitude = hop.coords.lat, hop.coords.lon
            if latitude is None or longitude is None:
                first_valid_row = True  # Reset for the next valid row
                continue  # Skip if geolocation lookup fails

        valid_data_points.append({
            'ip_address': ip_address,
            'rtt': rtt,
            'latitude': latitude,
            'longitude': longitude
        })

        prev_city, prev_region, prev_country = city, region, country

    if not valid_data_points:
        print("No valid data points found.")
        return

    for data_point in valid_data_points:
        latitude, longitude, rtt = data_point['latitude'], data_point['longitude'], data_point['rtt']
        
        if first_valid_row:
            prev_latitude, prev_longitude, prev_min_rtt = latitude, longitude, rtt
            first_valid_row = False
            continue

        radius = calculate_radius(rtt, prev_min_rtt) if prev_min_rtt is not None else None
        within_radius = is_within_radius(prev_latitude, prev_longitude, latitude, longitude, radius) if radius is not None else True

        floor_test_results.append({
            'ip_address': data_point['ip_address'],
            'rtt': rtt,
            'radius': radius,
            'geolocation_within_radius': within_radius
        })

        prev_latitude, prev_longitude, prev_min_rtt = latitude, longitude, rtt

    return {
        'all_data_points': all_data_points,
        'floor_test_results': floor_test_results
    }

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--file', type=str, required=True)
    args = argparser.parse_args()

    traceroute_pkl = args.file

    with open(traceroute_pkl, 'rb') as f:
        tr_json = pickle.load(f)

    tr = RIPETraceroute(tr_json)

    # Load the precomputed distance map
    with open('country_distances.json', 'r') as f:
        distance_map = json.load(f)

    results = process_traceroute_data(tr, distance_map)

    if results:
        output_file_path = os.path.splitext(traceroute_pkl)[0] + "_floor_test_results.json"
        with open(output_file_path, "w") as file:
            json.dump(results, file, indent=4)
        print(f"Floor test results logged for










