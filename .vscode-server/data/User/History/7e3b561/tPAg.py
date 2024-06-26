import geopandas as gpd
import pycountry
from shapely.ops import nearest_points
from shapely.geometry import MultiPolygon
import pickle


#Does not include singapore 

def calculate_country_distances():
    # Load the world dataset from GeoPandas
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Filter out entries without valid geometries or with multipolygon geometries
    world = world[world.geometry.type.isin(['Polygon', 'MultiPolygon'])]

    # Ensure the GeoDataFrame uses the WGS84 coordinate system (latitude/longitude)
    world = world.to_crs(epsg=4326)

    # Create a dictionary to store the shortest distances
    distance_map = {}

    # Get a list of country names and their ISO codes from pycountry
    
    country_to_iso = {country.name: country.alpha_2 for country in pycountry.countries}
    print(country_to_iso)

    # Add manual mappings for country names that do not match pycountry names
    manual_mappings = {
        "United States of America": "United States",
        "Russian Federation": "Russia",
        "South Korea": "Korea, Republic of",
        "North Korea": "Korea, Democratic People's Republic of",
        "Vietnam": "Viet Nam",
        "Laos": "Lao People's Democratic Republic",
        "Myanmar": "Burma",
        "Macedonia": "North Macedonia",
        # Add any other necessary mappings here
    }

    world['name'] = world['name'].replace(manual_mappings)

    # Normalize country names to ensure consistent matching
    world['name'] = world['name'].apply(lambda x: x.title())

    # Filter the world GeoDataFrame to include only countries from the pycountry list
    world = world[world['name'].isin(country_to_iso.keys())]

    # Loop through each country to compute the shortest distance to every other country
    for i, country1 in world.iterrows():
        for j, country2 in world.iterrows():
            if i < j:  # Ensure each pair is only processed once
                # Find the nearest points
                p1, p2 = nearest_points(country1.geometry, country2.geometry)
                # Calculate the distance in degrees
                distance = p1.distance(p2)
                # Convert the distance to kilometers using the approximate conversion factor
                distance_km = distance * 111.32  # 1 degree latitude ~ 111.32 km
                distance_map[(country_to_iso[country1['name']], country_to_iso[country2['name']])] = distance_km
                distance_map[(country_to_iso[country2['name']], country_to_iso[country1['name']])] = distance_km

    # Example output for a few country pairs
    for key, value in list(distance_map.items())[:100]:
        print(f"The shortest distance between {key[0]} and {key[1]} is {value:.2f} km.")

    print(distance_map.get(('US', 'AO')))
    print(distance_map.get(('KR', 'SG')))
    print(distance_map.get(('ZA', 'AO')))
    
    # Save the distance map to a file using pickle
    output_file = 'country_distances.pkl'

    with open(output_file, 'wb') as f:
        pickle.dump(distance_map, f)

    print(f"Distance calculations saved to {output_file}")

if __name__ == "__main__":
    calculate_country_distances()
