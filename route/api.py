from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Segment, Description
from .getroute import get_route
import osmnx as ox
import json

def load_graphs():
    map_graph = ox.graph_from_place('Yekaterinburg, Russia', 'walk')
    navigation_graph = map_graph.copy()
    return navigation_graph, map_graph

navigation_graph, map_graph = load_graphs()

class NavigationApi(APIView):
    def get(self, request, lat_start, long_start, lat_stop, long_stop):
        global navigation_graph

        _, coordinates = get_route(navigation_graph, long_start, lat_start, long_stop, lat_stop)
        context = {'route': json.dumps(coordinates)}
        return Response(context)

class SegmentApi(APIView):
    def get(self, request, lat_start, long_start, lat_stop, long_stop):
        global map_graph

        _, coordinates = get_route(map_graph, long_start, lat_start, long_stop, lat_stop)
        context = {'route' : json.dumps(coordinates)}
        return Response(context)