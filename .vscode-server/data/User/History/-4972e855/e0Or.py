import argparse 
import pickle 
import math
from aquatools.topo.Traceroutes import RIPETraceroute 



def calculate_radius(curr_min_rtt, prev_min_rtt):
    if curr_min_rtt is None:
        print("Error when parsing RTTs; Cannot Calculate Radius")
        return None
    
    print(curr_min_rtt, prev)
    rtt_diff = abs(curr_min_rtt - prev_min_rtt)
    speed_of_light = 299.792458  # Speed of light in km/ms
    radius = (rtt_diff / 2) * ((speed_of_light) * (2 / 3))  # travel speed of optic fiber
    return radius

def is_within_radius(distance, radius):
    if distance <= radius:
        return True 
    else:
        print(f"A wrong IP mapping has occurred: distance = {distance}, radius = {radius}")
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
        print(city, country, lon, lat)

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
            print("do we get here")
            first_valid_row = False
            continue

        if first_valid_row:
            prev_lon, prev_lat, prev_city, prev_state, prev_country = lon, lat, city, state, country
            first_valid_row = False 
            continue
        
        if city is None or prev_city is None:
            distance = dist_bet_countries(country, prev_country, distance_map)
            
        distance = dist_bet_coords(lon, lat, prev_lon, prev_lat) 

        radius = calculate_radius(rtt, prev_rtt)
        within_radius = is_within_radius(distance, radius)

        print(f"Processing hop: {ip_address}, rtt: {rtt}, prev_rtt: {prev_rtt}, distance: {distance}, radius: {radius}, within_radius: {within_radius}")

        floor_test_results.append({
            'ip_address': ip_address,
            'rtt': rtt,
            'radius': radius,
            'geolocation_within_radius': within_radius
        })

        prev_lon, prev_lat, prev_city, prev_state, prev_country, prev_rtt= lon, lat, city, state, country, rtt

    return {
        'all_data_points': all_data_points,
        'floor_test_results': floor_test_results
    }


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--file', type=str, required=True) 
    args = argparser.parse_args() 

    # Load the distance map from the pickle file
    with open('country_distances.pkl', 'rb') as f:
        distance_map = pickle.load(f)

    directory = 'data/'
    traceroute_pkl = args.file 

    filename = f"{directory}/{traceroute_pkl}" 

    with open(filename, 'rb') as f:
        tr_json = pickle.load(f) 

    #import pprint 
    #pprint.pprint(tr_json)


    tr = RIPETraceroute(tr_json)
    #print(tr)

    result = process_traceroute(tr, distance_map)

    # Example of using the result
    print("Floor Test Results:")
    for res in result['floor_test_results']:
        print(res)


if __name__ == "__main__":
    main()