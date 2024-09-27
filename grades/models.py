from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Assignment(models.Model):
    title = models.CharField(max_length=200 , null=False , blank=False)
    description = models.TextField(null=False , blank=False)
    deadline = models.DateTimeField(null=False , blank=False)
    weight = models.IntegerField(null=False , blank=False)
    points = models.IntegerField(null=False , blank=False)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment , on_delete=models.CASCADE)
    author = models.ForeignKey(User , on_delete=models.CASCADE)
    grader = models.ForeignKey(User , on_delete=models.CASCADE , related_name='graded_set', null=True, blank=True)
    file = models.FileField(null=False , blank=False)
    score = models.FloatField(null=True, blank=True)

    