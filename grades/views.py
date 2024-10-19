from . import models
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404

# Create your views here.
def index(request):
    return render(request, "index.html" , {
        "assignments" : models.Assignment.objects.all(),
    })


def assignment(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id=assignment_id)
        return render(request, "assignment.html" , {
        "assignment" : assignment,
        "number_of_students" : models.Group.objects.get(name="Students").user_set.count(),
        "number_of_submissions" : assignment.submission_set.count(),
        "number_of_submissions_assigned_to_you" : models.User.objects.get(username="g").graded_set.filter(assignment = assignment).count(),
        })
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")


def submissions(request, assignment_id):
    # def grade(request, assignment_id):
    #         if request.method == "POST":
    #             return redirect(f"/{assignment_id}/submissions")
    if request.method == "POST":
                return redirect(f"/{assignment_id}/submissions")
    
    assignment = models.Assignment.objects.get(id=assignment_id)
    garry_grader = models.User.objects.get(username="g")
    submissions = assignment.submission_set.filter(grader=garry_grader).order_by("author")

    return render(request, "submissions.html" , {
        "assignment" : assignment,
        "submissions" : submissions,
        })
    # try:     
    #     assignment = models.Assignment.objects.get(id=assignment_id)
    #     garry_grader = models.User.objects.get(username="g")
    #     submissions = assignment.submission_set.filter(grader=garry_grader).order_by("author")

    #     return render(request, "submissions.html" , {
    #     "assignment" : assignment,
    #     "submissions" : submissions,
    #     })
    # except models.Submission.DoesNotExist:
    #     raise Http404("Submission not found")
    


def profile(request):
    assignments = models.Assignment.objects.all()
    garry_grader = models.User.objects.get(username="g")

    assignment_graded_column = []

    for assignment in assignments:
        submissions_assigned_to_you = assignment.submission_set.filter(grader=garry_grader).count()
        submissions_you_graded = assignment.submission_set.filter(grader=garry_grader, score__isnull=False).count()
        assignment_graded_column.append({"assignment":assignment, "submissions_you_graded":submissions_you_graded ,"submissions_assigned_to_you": submissions_assigned_to_you})

    return render(request, "profile.html", {
        "assignment_graded_column": assignment_graded_column,
    })


def login_form(request):
    return render(request, "login.html")