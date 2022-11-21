import folium
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
import osmnx as ox
import networkx as nx
import numpy as np
from .models import Segment, Description
from .forms import CreateUserForm
from . import getroute
import json

def load_graphs():
    map_graph = ox.graph_from_place('Yekaterinburg, Russia', 'walk')
    navigation_graph = map_graph.copy()
    return navigation_graph, map_graph

navigation_graph, map_graph = load_graphs()


def register_page(request):
    if request.method == 'GET':
        form = CreateUserForm()
        context = {'form': form}
        return render(request, 'register.html', context)
    elif request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            return redirect('login')
        else:
            context = {'form': form}
            return render(request, 'register.html', context)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')

    return render(request, 'login.html')

def main_map(request):
    if request.method == 'GET':
        segment_list = []
        segments = Segment.objects.all()
        for i, segment in zip(range(len(segments)), segments):
            relevant_descriptions = Description.objects.filter(segment=segment)[:10]
            segment_list.append((i, segment.segment, segment.mean_score, \
                                 [[description.score, description.type, description.comment, description.creator] for description in relevant_descriptions]))
        context = {'segments': segment_list}
        return render(request, 'main-map.html', context)

def test_page(request):
    return render(request, 'test.html')


def showroute(request, lat_start, long_start, lat_stop, long_stop):
    global navigation_graph, map_graph
    if request.method == 'GET':
        _, coordinates = getroute.get_route(map_graph, long_start, lat_start, long_stop, lat_stop)
        context = {'coordinates': coordinates}
        return render(request, 'showroute.html', context)

    elif request.method == 'POST' and 'add_to_db_form' in request.POST:
        score = int(request.POST.get('score')) # достаем данные из формы и приводим к нужным типам
        type_dict = {
            "0": 'Брусчатка',
            "1": 'Ямы',
            "2": 'Поребрики',
            "3": 'Ливневка'
        }
        score_coeffs = {
            5: 1,
            1: 7.5,
            2: 3,
            3: 1.875,
            4: 1.2,
        }
        type = type_dict[request.POST.get('type')]
        comment = request.POST.get('comment')

        route, coordinates = getroute.get_route(map_graph, long_start, lat_start, long_stop, lat_stop)
        json_path = json.dumps(coordinates)
        user = request.user
        try:
            segment = Segment.objects.filter(segment=json_path)[0]
            previous_scores = [description.score for description in Description.objects.filter(segment=segment)[:10]]
            segment.mean_score = getroute.update_mean(navigation_graph, route, segment, score, score_coeffs, previous_scores)
            segment.save()
            save_description(segment, user, score, type, comment)
        except:
            segment = save_segment(json_path, user, score)
            save_description(segment, user, score, type, comment)
            getroute.add_weights_from_segment(navigation_graph, route, score, score_coeffs)
        return redirect('/')

def navigation_page(request, lat_start, long_start, lat_stop, long_stop):
    global navigation_graph
    if request.method == 'GET':
        _, coordinates = getroute.get_route(navigation_graph, long_start, lat_start, long_stop, lat_stop)
        context = {'coordinates': coordinates}
        return render(request, 'navigation.html', context)

def save_segment(path, user, score):
    segment_object = Segment(segment=path, creator=user, mean_score=score)
    segment_object.save()
    return segment_object


def save_description(segment, user, score, type, comment):
    description_object = Description(segment=segment, creator=user, score=score, type=type, comment=comment)
    description_object.save()



# API


