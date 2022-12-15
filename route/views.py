import json

from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from . import getroute, api
from .forms import CreateUserForm
from .models import Segment, Description
import requests
from bs4 import BeautifulSoup

def register_page(request):
    if request.method == 'GET':
        form = CreateUserForm()
        context = {'form': form}
        return render(request, 'register.html', context)
    elif request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
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
                                 [[description.score, description.type, description.comment, description.creator, description.date] for description in relevant_descriptions]))
        context = {'segments': segment_list}
        return render(request, 'main-map.html', context)
    elif request.method == 'POST':
        starting_address = request.POST.get('start')
        ending_address = request.POST.get('end')
        start_coordinates = translate_address(starting_address)
        end_coordinates = translate_address(ending_address)
        return redirect(f'/navigation/{start_coordinates},{end_coordinates}')

def test_page(request):
    return render(request, 'test.html')


def showroute(request, lat_start, long_start, lat_stop, long_stop):
    if request.method == 'GET':
        _, coordinates = getroute.get_route(api.map_graph, long_start, lat_start, long_stop, lat_stop)
        # coordinates = json.loads(Segment.objects.all()[0].segment)
        context = {'coordinates': coordinates}
        return render(request, 'showroute.html', context)

    elif request.method == 'POST' and 'add_to_db_form' in request.POST:
        #score = int(request.POST.get('score')) # достаем данные из формы и приводим к нужным типам
        #user = User.objects.all()[0]
        scores = {
            1: request.POST.get('score_1'),
            2: request.POST.get('score_2'),
            3: request.POST.get('score_3'),
            4: request.POST.get('score_4'),
            5: request.POST.get('score_5')
        }
        print(scores)
        score = [key for key in scores.keys() if scores[key] != None][0]

        types = {
            'Хорошая дорога': request.POST.get('Хорошая дорога'),
            'Брусчатка': request.POST.get('Брусчатка'),
            'Ямы': request.POST.get('Ямы'),
            'Поребрики': request.POST.get('Поребрики'),
            'Ливневка': request.POST.get('Ливневка'),
        }
        print(types)
        type = ', '.join([key for key in types.keys() if types[key] != None])
        print(type, score)
        #type = type_dict[request.POST.get('type')]
        comment = request.POST.get('comment')
        if comment == None:
            comment = ''
        route, coordinates = getroute.get_route(api.map_graph, long_start, lat_start, long_stop, lat_stop)
        json_path = json.dumps(coordinates)
        user = request.user
        try:
            segment = Segment.objects.filter(segment=json_path)[0]
            previous_scores = [description.score for description in Description.objects.filter(segment=segment)[:10]]
            segment.mean_score = getroute.update_mean(api.navigation_graph, route, segment, score, api.score_coeffs, previous_scores)
            segment.save()
            save_description(segment, user, score, type, comment)
        except:
            segment = save_segment(json_path, user, score)
            save_description(segment, user, score, type, comment)
            getroute.add_weights_from_segment(api.navigation_graph, route, score, api.score_coeffs)
        return redirect('/')

def navigation_page(request, lat_start, long_start, lat_stop, long_stop):
    if request.method == 'GET':
        _, coordinates = getroute.get_route(api.navigation_graph, long_start, lat_start, long_stop, lat_stop)
        # coordinates = json.loads(Segment.objects.all()[0].segment)
        context = {'coordinates': coordinates}
        return render(request, 'navigation.html', context)

def save_segment(path, user, score):
    segment_object = Segment(segment=path, creator=user, mean_score=score)
    segment_object.save()
    return segment_object


def save_description(segment, user, score, type, comment):
    description_object = Description(segment=segment, creator=user, score=score, type=type, comment=comment, date=date.today())
    description_object.save()

def translate_address(address):
    url = f'https://geocode-maps.yandex.ru/1.x/?apikey=03d8d000-854f-4bfa-88af-980bfbdd108f&geocode=Eкатеринбург,+{address.replace(" ", "+")}'
    response = requests.get(url).text
    position = BeautifulSoup(response).find('pos').text.split()
    position.reverse()
    return ','.join(position)


# API


