import json
import osmnx as ox

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User

from . import getroute
from .models import Segment, Description
from .serializers import DescriptionSerializer
from .forms import CreateUserForm

def load_graphs():
    map_graph = ox.graph_from_place('Yekaterinburg, Russia', 'walk')
    navigation_graph = map_graph.copy()

    score_coeffs = {
        5: 0.5,
        1: 3.5,
        2: 2,
        3: 1,
        4: 0.75,
    }

    for segment in Segment.objects.all():
        segment_path = json.loads(segment.segment)
        segment_score = segment.mean_score
        route, _ = getroute.get_route(map_graph, segment_path[0][0], segment_path[0][1], segment_path[-1][0], segment_path[-1][0])
        getroute.add_weights_from_segment(navigation_graph, route, segment_score, score_coeffs)

    return navigation_graph, map_graph, score_coeffs

navigation_graph, map_graph, score_coeffs = load_graphs()

class NavigationApi(APIView):
    def get(self, request, lat_start, long_start, lat_stop, long_stop):
        global navigation_graph

        _, coordinates = getroute.get_route(navigation_graph, long_start, lat_start, long_stop, lat_stop)
        context = {'route': json.dumps(coordinates)}
        return Response(context)


class SegmentApi(APIView):
    def get(self, request, lat_start, long_start, lat_stop, long_stop):
        global map_graph

        _, coordinates = getroute.get_route(map_graph, long_start, lat_start, long_stop, lat_stop)
        context = {'route' : json.dumps(coordinates)}
        return Response(context)

class UserApi(APIView):
    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DescriptionApi(APIView):
    def get(self, request):
        objects = Description.objects.all()
        serializer = DescriptionSerializer(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        global navigation_graph, score_coeffs
        if request.POST.get('request_type') == 'route':
            segment = request.POST.get('segment')
            username = request.POST.get('username')
            initial_score = int(request.POST.get('score'))

            users = User.objects.filter(username=username)
            if len(users) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                user = users[0]
                save_segment(segment, user, initial_score)

                segment = json.loads(segment)
                route, _ = getroute.get_route(map_graph, segment[0][0], segment[0][1], segment[-1][0], segment[-1][1])
                getroute.add_weights_from_segment(navigation_graph, route, initial_score, score_coeffs)

            return Response(status=status.HTTP_200_OK)

        elif request.POST.get('request_type') == 'description':
            segment_coordinates = request.POST.get('segment')
            segments = Segment.objects.filter(segment=segment_coordinates)
            if len(segments) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                segment = segments[0]
                start_point = json.loads(segment.segment)[0]
                end_point = json.loads(segment.segment)[-1]
                route, _ = getroute.get_route(navigation_graph, start_point[0], start_point[1], end_point[0], end_point[1])
                score = int(request.POST.get('score'))
                type = request.POST.get('type')
                comment = request.POST.get('comment')
                username = request.POST.get('username')

                users = User.objects.filter(username=username)
                if len(users) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    user = users[0]
                    previous_scores = [description.score for description in Description.objects.filter(segment=segment)[:10]]
                    segment.mean_score = getroute.update_mean(navigation_graph, route, segment, score, score_coeffs, previous_scores)
                    segment.save()
                    save_description(segment, user, score, type, comment)

                    return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


def save_segment(path, user, score):

    segment_object = Segment(segment=path, creator=user, mean_score=score)
    segment_object.save()
    return segment_object


def save_description(segment, user, score, type, comment):
    description_object = Description(segment=segment, creator=user, score=score, type=type, comment=comment)
    description_object.save()