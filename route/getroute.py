import requests
import json
import polyline
import folium
import json

def get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat):
    loc = "{},{};{},{}".format(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    url = "http://router.project-osrm.org/route/v1/foot/"
    r = requests.get(url + loc) 
    if r.status_code != 200:
        return {}
    res = r.json()   
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']
    
    out = {
        'route' : routes,
        'start_point': start_point,
        'end_point': end_point,
        'distance': distance
    }

    return out


def get_and_save_path(lat_start, lon_start, lat_stop, lon_stop):
    res = requests.get(f"http://router.project-osrm.org/route/v1/driving/{lon_start},{lat_start};{lon_stop},{lat_stop}")
    path = polyline.decode(res.json()['routes'][0]['geometry'])
    return json.dumps(path)


def load_path(json_path):
    return json.loads(json_path)