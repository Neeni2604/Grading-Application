from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    weight = models.IntegerField()
    points = models.IntegerField()

class Submission(models.Model):
    assignment = models.CharField(max_length=200)
    