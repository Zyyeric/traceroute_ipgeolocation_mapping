import argparse 
import pickle 
import math
from aquatools.topo.Traceroutes import RIPETraceroute 
from country_dist_cal import calculate_country_distances


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
        print("A wrong IP mapping has occurred")
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
    valid_data_points = []
    all_data_points = []

    prev_city, prev_region, prev_country = None, None, None
    prev_lat, prev_lon, prev_rtt = None, None, None
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

        # if the program wants to pause immediately after encounterring an invalid hop 
        if rtt is None or geolocation is None:
            break
        
        # if the code wants to preceed even encounter an invalid hop 
        if rtt is None or geolocation is None: 
            first_valid_row = True

        if city is None or prev_city is None:
            distance = dist_bet_countries(country, prev_country, distance_map)
        
        lon, lat = hop.coords.lon, hop.coords.lat
        distance = dist_bet_coords(lon, lat, prev_lon, prev_lat) 

        radius = calculate_radius(rtt, prev_rtt)
        is_within_radius = is_within_radius(distance, radius)

        


        




        

    







def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--file', type=str, required=True) 
    args = argparser.parse_args() 


    directory = 'data/'
    traceroute_pkl = args.file 

    filename = f"{directory}/{traceroute_pkl}" 

    with open(filename, 'rb') as f:
        tr_json = pickle.load(f) 

    #import pprint 
    #pprint.pprint(tr_json)


    tr = RIPETraceroute(tr_json)
    print(tr)

    result = process_traceroute(tr)



if __name__ == "__main__":
    main()



