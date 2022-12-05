import requests
import json
import polyline
import folium
import osmnx as ox
import networkx as nx
import numpy as np

def get_route(graph, start_lat, start_lon, end_lat, end_lon):
    start_lat, start_lon, end_lat, end_lon = float(start_lat), float(start_lon), float(end_lat), float(end_lon)
    start_node = ox.nearest_nodes(graph, X=start_lat, Y=start_lon)
    end_node = ox.nearest_nodes(graph, X=end_lat, Y=end_lon)
    route = nx.shortest_path(graph, start_node, end_node, weight='length')
    nodes = graph.nodes()
    coordinates = [[nodes[node]['x'], nodes[node]['y']] for node in route]
    return route, coordinates



def add_weights_from_segment(graph, route, score, score_coeffs):
    pairs = [(route[i - 1], route[i]) for i in range(1, len(route))]
    for pair in pairs:
        graph[pair[0]][pair[1]][0]['length'] = graph[pair[0]][pair[1]][0]['length'] * score_coeffs[score]


def update_mean(graph, route, segment, current_score, score_coeffs, previous_scores):
    old_score = segment.mean_score
    new_score = int(np.mean(previous_scores + [current_score]))
    old_multiplicator = score_coeffs[old_score]
    new_multiplicator = score_coeffs[new_score]
    pairs = [(route[i - 1], route[i]) for i in range(1, len(route))]
    for pair in pairs:
        graph[pair[0]][pair[1]][0]['length'] = graph[pair[0]][pair[1]][0]['length'] / old_multiplicator * new_multiplicator
    return new_score