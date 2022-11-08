import folium
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
import numpy as np
from .models import Segment, Description
from .forms import CreateUserForm
from . import getroute


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
        figure = folium.Figure()
        map = folium.Map(location=[56.8,60.6],
                         zoom_start=12)
        map.add_to(figure)
        segments = Segment.objects.all()
        for segment in segments:
            draw_polyline_by_segment(segment, map)
        figure.render()
        context = {'map': figure}
        segment_list = []
        for i, segment in zip(range(len(segments)), segments):
            segment_list.append((i, segment.segment))
        context['segments'] = segment_list
        return render(request, 'main-map.html', context)

def showmap(request):
    return render(request, 'showmap.html')


def showroute(request, lat_start, long_start, lat_stop, long_stop):
    if request.method == 'GET':
        figure = folium.Figure()

        lat_start, long_start, lat_stop, long_stop = float(lat_start), float(long_start), float(lat_stop), float(long_stop)
        route = getroute.get_route(long_start, lat_start, long_stop, lat_stop)
        map = folium.Map(location=[(route['start_point'][0]),
                             (route['start_point'][1])],
                   zoom_start=15)
        map.add_to(figure)
        draw_polyline(route, map)
        figure.render()
        context = {'map': figure}
        return render(request, 'showroute.html', context)

    elif request.method == 'POST' and 'add_to_db_form' in request.POST:
        score = int(request.POST.get('score'))
        type_dict = {
                "0": 'Брусчатка',
                "1": 'Ямы',
                "2": 'Поребрики',
                "3": 'Ливневка'
        }

        type = type_dict[request.POST.get('type')]
        comment = request.POST.get('comment')
        json_path = getroute.get_and_save_path(lat_start, long_start, lat_stop, long_stop)
        user = request.user
        segment = save_segment(json_path, user)
        save_description(segment, user, score, type, comment)
        return redirect('/')



def draw_polyline(route, map):
    folium.PolyLine(route['route'], weight=8, color='blue', opacity=0.6).add_to(map)
    folium.Marker(location=route['start_point'], icon=folium.Icon(icon='play', color='green')).add_to(map)
    folium.Marker(location=route['end_point'], icon=folium.Icon(icon='stop', color='red')).add_to(map)

def draw_polyline_by_segment(segment, map):
    path = getroute.load_path(segment.segment)
    descriptions_by_segment = Description.objects.filter(segment=segment)
    score = int(np.mean([description.score for description in descriptions_by_segment]))
    color_dict = {
        5 : 'green',
        4 : 'blue',
        3 : 'yellow',
        2 : 'red',
        1 : 'black'
    }
    color = color_dict[score]
    folium.PolyLine(path, weight=5, color=color, opacity=0.6).add_to(map)


def save_segment(path, user):
    segment_object = Segment(segment=path, creator=user)
    segment_object.save()
    return segment_object


def save_description(segment, user, score, type, comment):
    description_object = Description(segment=segment, creator=user, score=score, type=type, comment=comment)
    description_object.save()