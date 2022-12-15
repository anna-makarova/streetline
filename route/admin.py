from django.contrib import admin
from .models import Segment, Description
# Register your models here.

@admin.register(Segment)
class Segment(admin.ModelAdmin):
    list_display = ['creator']
    list_filter = ['creator']

@admin.register(Description)
class Segment(admin.ModelAdmin):
    list_display = ['score', 'type', 'creator', 'date']
    list_filter = ['creator', 'type']