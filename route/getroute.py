import requests
import json
import polyline
import folium
import osmnx as ox
import networkx as nx

def get_route(graph, start_lat, start_lon, end_lat, end_lon):
    start_lat, start_lon, end_lat, end_lon = float(start_lat), float(start_lon), float(end_lat), float(end_lon)
    start_node = ox.nearest_nodes(graph, X=start_lat, Y=start_lon)
    end_node = ox.nearest_nodes(graph, X=end_lat, Y=end_lon)
    route = nx.shortest_path(graph, start_node, end_node, weight='length')
    nodes = graph.nodes()
    coordinates = [[nodes[node]['x'], nodes[node]['y']] for node in route]
    print(route)
    print(coordinates)
    return route, coordinates


def add_weights_from_segment(graph, route, score, score_coeffs):
    pairs = [(route[i - 1], route[i]) for i in range(1, len(route))]
    for pair in pairs:
        graph[pair[0]][pair[1]][0]['length'] = graph[pair[0]][pair[1]][0]['length'] * score_coeffs[score]
