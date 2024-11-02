from . import models
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    return render(request, "index.html" , {
        "assignments" : models.Assignment.objects.all(),
    })


def assignment(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id=assignment_id)
        alice_algorithm = models.User.objects.get(username="a") 
        aliceSubmission = assignment.submission_set.filter(author=alice_algorithm).first()

        if request.method == "POST":
            submittedFile = request.FILES.get('subFile')

            if submittedFile:
                if aliceSubmission:
                    aliceSubmission.file = submittedFile
                else:
                        aliceSubmission = models.Submission.objects.create(
                        assignment=assignment,
                        author=alice_algorithm,
                        grader=models.User.objects.get(username="g"),  
                        file=submittedFile,
                        score=None  
                    )
                aliceSubmission.save()
            return redirect(f"/{assignment_id}/")

        return render(request, "assignment.html" , {
        "assignment" : assignment,
        "number_of_students" : models.Group.objects.get(name="Students").user_set.count(),
        "number_of_submissions" : assignment.submission_set.count(),
        "number_of_submissions_assigned_to_you" : models.User.objects.get(username="g").graded_set.filter(assignment = assignment).count(),
        "alice_algorithm" : alice_algorithm,
        "aliceSubmission" : aliceSubmission,
        })
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")
    except models.User.DoesNotExist:
        raise Http404("User not found")


def submissions(request, assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    garry_grader = models.User.objects.get(username="g")
    submissions = assignment.submission_set.filter(grader=garry_grader).order_by("author")
    errors = {}
    invalidSubs = []

    if request.method == "POST":
        valid_submissions = []
        
        for key, value in request.POST.items():
            if key.startswith("grade-"):
                try:
                    submission_id = int(key.removeprefix('grade-'))
                    submission = models.Submission.objects.get(id=submission_id, assignment=assignment)
                    
                    if value == '':
                        submission.score = None
                    else:
                        if float(value) < 0 or float(value) > assignment.points:
                            raise ValueError(f"Grade must be between 0 and {assignment.points}.")
                        submission.score = float(value)
                        
                    valid_submissions.append(submission)
                except ValueError as ve:
                    errors[submission_id] = [str(ve)]
                except models.Submission.DoesNotExist:
                    invalidSubs.append(submission_id)
                    errors[submission_id] = ["Submission does not exist."]

        if valid_submissions:
            models.Submission.objects.bulk_update(valid_submissions, ['score'])
        
        if not errors:
            return redirect(f"/{assignment_id}/submissions")
        
    submissionsArray = []

    for sub in submissions:
        dict = {}
        dict["id"] = sub.id
        dict["name"] = sub.author.get_full_name()
        dict["sub"] = sub.file.url
        dict["score"] = sub.score
        dict["errors"] = errors.get(sub.id, [])
        submissionsArray.append(dict)

    return render(request, "submissions.html", {
        "assignment": assignment,
        "submissionsArray" : submissionsArray,
        "invalidSubs" : invalidSubs,
    })


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
        "user": request.user,
    })


def login_form(request):
    if request.method=="POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")            

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, "login.html")

def show_upload(request, filename):
    submission = models.Submission.objects.get(file=filename)
    return HttpResponse(submission.file.open())

def logout_form(request):
    logout(request)
    return redirect(f"/profile/login/")