import argparse 
import pickle 
import math
from aquatools.topo.Traceroutes import RIPETraceroute 
import json 
import os



def calculate_radius(curr_min_rtt, prev_min_rtt):
    if curr_min_rtt is None:
        print("Error when parsing RTTs; Cannot Calculate Radius")
        return None
    
    rtt_diff = abs(curr_min_rtt - prev_min_rtt)
    speed_of_light = 299.792458  # Speed of light in km/ms
    radius = (rtt_diff / 2) * ((speed_of_light) * (2 / 3))  # travel speed of optic fiber
    return radius

def is_within_radius(distance, radius):
    if distance <= radius:
        return True 
    else:
        return False

# compute the nearest points between two countries 
def dist_bet_countries(country, prev_country, distance_map):
    return distance_map.get((country, prev_country))

# compute the distance between two pairs of coordinates
def dist_bet_coords(lon1, lat1, lon2, lat2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon1 - lat2

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    f = 1 / 298.257223563
    b = (1 - f) * 6371

    distance = c * b
    
    return distance

def process_traceroute(tr, distance_map):
    floor_test_results = []
    all_data_points = []

    prev_city, prev_state, prev_country = None, None, None
    prev_lat, prev_lon, prev_rtt = None, None, None
    first_valid_row = True

    for hop in tr.hops:
        ip_address, rtt = hop.addr, hop.rtt
        geolocation = hop.geoloc

        city = geolocation.city if geolocation and geolocation.city else None
        state = geolocation.state if geolocation and geolocation.state else None
        country = geolocation.country if geolocation and geolocation.country else None
        lon = hop.coords.lon if hop.coords else None
        lat = hop.coords.lat if hop.coords else None

        all_data_points.append({
            'ip_address': ip_address,
            'rtt': rtt,
            'geolocation': geolocation  # Convert namedtuple to dictionary
        })

        # if the program wants to pause immediately after encounterring an invalid hop 
        #if rtt is None or geolocation is None:
        #    break
        
        # if the code wants to preceed even encounter an invalid hop 
        if rtt is None or geolocation is None: 
            first_valid_row = False
            continue

        if first_valid_row:
            prev_lon, prev_lat, prev_city, prev_state, prev_country, prev_rtt = lon, lat, city, state, country, rtt
            first_valid_row = False 
            continue
        
        if city is None or prev_city is None:
            distance = dist_bet_countries(country, prev_country, distance_map)
            
        distance = dist_bet_coords(lon, lat, prev_lon, prev_lat) 

        radius = calculate_radius(rtt, prev_rtt)
        within_radius = is_within_radius(distance, radius)

        floor_test_results.append({
            'ip_address': ip_address,
            'rtt': rtt,
            'radius': radius,
            'geolocation_within_radius': within_radius
        })

        prev_lon, prev_lat, prev_city, prev_state, prev_country, prev_rtt= lon, lat, city, state, country, rtt

    return {
        'traceroute': tr,
        'floor_test_results': floor_test_results
    }


def main():
    directory = 'data/'
    
    try:
        # Load the distance map from the pickle file
        with open('country_distances.pkl', 'rb') as f:
            distance_map = pickle.load(f)
        
        while True:
            traceroute_pkl = input("Enter the traceroute file name (or 'q' to quit): ")
            
            if traceroute_pkl.lower() == 'q':
                break
            
            filename = f"{directory}/{traceroute_pkl}"
            
            try:
                with open(filename, 'rb') as f:
                    tr_json = pickle.load(f)
                
                tr = RIPETraceroute(tr_json)
                result = process_traceroute(tr, distance_map)
                
                # extract the base filename
                base_filename = os.path.splitext(traceroute_pkl)[0]
                
                # Write the floor test results to a JSON file
                floor_test_filename = f"results/{base_filename}_floor_test_results.json"
                with open(floor_test_filename, 'w') as f:
                    json.dump(result['floor_test_results'], f, indent=4)
                
                print(f"Floor test results written to: {floor_test_filename}")
                
                # Write the traceroute object to a JSON file
                
                traceroute_filename = f"results/{base_filename}_traceroute.json"
                with open(traceroute_filename, 'w') as f:
                    json.dump(result['traceroute'], f, indent=4)
                
                print(f"Traceroute object written to: {traceroute_filename}")
            
            except FileNotFoundError:
                print(f"File '{filename}' not found. Please try again.")
            
            except Exception as e:
                print(f"An error occurred: {str(e)}")
    
    except FileNotFoundError:
        print("Distance map file 'country_distances.pkl' not found.")
    
    except Exception as e:
        print(f"An error occurred while loading the distance map: {str(e)}")

if __name__ == "__main__":
    main()