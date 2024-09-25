from . import models
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html" , {
        "assignments" : models.Assignment.objects.all(),
    })


def assignment(request, assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    return render(request, "assignment.html" , {
        "assignment" : assignment,
        "number_of_students" : models.Group.objects.get(name="Students").user_set.count(),
        "number_of_submissions" : assignment.submission_set.count(),
        "number_of_submissions_assigned_to_you" : models.User.objects.get(username="g").graded_set.filter(assignment = assignment).count(),
    })


def submissions(request, assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    submissions = assignment.submission_set.order_by("author")

    return render(request, "submissions.html" , {
        "assignment" : assignment,
        "submissions" : submissions,
    })


def profile(request):
    return render(request, "profile.html")


def login_form(request):
    return render(request, "login.html")