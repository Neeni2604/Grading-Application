from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied

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
    grader = models.ForeignKey(User , on_delete=models.SET_NULL , related_name='graded_set', null=True, blank=True)
    file = models.FileField(null=False , blank=False)
    score = models.FloatField(null=True, blank=True)

    def change_grade(self, user, newGrade):
        if not user.groups.filter(name="Teaching Assistants").exists() and not user.is_superuser:
            raise PermissionDenied("Only TAs can change grades.")
        
        if self.grader != user and not user.is_superuser:
            raise PermissionDenied("You are not assigned to grade this submission.")
        else:
            self.score = newGrade
            

    def view_submission(self, user):
        if user == self.author or user == self.grader or user.is_superuser:
            return self.file
        raise PermissionDenied("You do not have permission to view this submission.")