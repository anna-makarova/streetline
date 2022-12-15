from django.db import models
from django.contrib.auth.models import User


class Marker(models.Model):
    lat = models.FloatField()
    long = models.FloatField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)


class Segment(models.Model):
    segment = models.TextField()
    mean_score = models.IntegerField(default=3)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)


class Description(models.Model):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    type = models.CharField(max_length=100)
    comment = models.CharField(max_length=400)
    date = models.DateField(auto_now=False, auto_now_add=False)
