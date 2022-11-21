"""show_route URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from route.api import NavigationApi, SegmentApi
from route.views import showroute, register_page, login_page, main_map, navigation_page, test_page
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register_page, name='register'),
    path('login/', login_page, name='login'),
    path('', main_map, name='main'),
    path('navigation/<str:lat_start>,<str:long_start>,<str:lat_stop>,<str:long_stop>', navigation_page, name='navigation'),
    path('segment/<str:lat_start>,<str:long_start>,<str:lat_stop>,<str:long_stop>', showroute, name='showroute'),

    path('api/navigation/<str:lat_start>,<str:long_start>,<str:lat_stop>,<str:long_stop>', NavigationApi.as_view(), name='navigation_api'),
    path('api/segment/<str:lat_start>,<str:long_start>,<str:lat_stop>,<str:long_stop>', SegmentApi.as_view(), name='segment_api'),


    path('test/', test_page, name='test'), # убрать при релизе
    ] + staticfiles_urlpatterns()

