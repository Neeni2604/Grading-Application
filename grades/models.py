from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Assignment(models.Model):
    field = models.Field

class Submission(models.Model):
    print()