from . import models
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timezone

def index(request):
    return render(request, "index.html" , {
        "assignments" : models.Assignment.objects.all(),
    })


def assignment(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id=assignment_id)
        currentUser = request.user
        currentUserSubmission = assignment.submission_set.filter(author=currentUser).first()

        if request.method == "POST":
            submittedFile = request.FILES.get('subFile')

            if submittedFile:
                if currentUserSubmission:
                    currentUserSubmission.file = submittedFile
                else:
                        currentUserSubmission = models.Submission.objects.create(
                        assignment=assignment,
                        author=currentUser,
                        grader=None,    #replace with pick_grader
                        file=submittedFile,
                        score=None  
                    )
                currentUserSubmission.save()
            return redirect(f"/{assignment_id}/")

        return render(request, "assignment.html" , {
        "assignment" : assignment,
        "number_of_students" : models.Group.objects.get(name="Students").user_set.count(),
        "number_of_submissions" : assignment.submission_set.count(),
        "number_of_submissions_assigned_to_you" : assignment.submission_set.filter(grader=currentUser).count(),
        "currentUser" : currentUser,
        "is_ta": is_ta(currentUser),
        "is_student": is_student(currentUser),
        "currentUserSubmission" : currentUserSubmission,
        })
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")
    except models.User.DoesNotExist:
        raise Http404("User not found")


def submissions(request, assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    
    user = request.user
    if user.is_superuser:
        submissions = assignment.submission_set.all()
    else:
        submissions = assignment.submission_set.filter(grader=user).order_by("author")
        
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
    currentUser = request.user

    assignment_graded_column = []

    totalWeight = 0
    currWeight = 0
    finalGrade=0

    if(currentUser.is_superuser):
        for assignment in assignments:
            totalSubs = assignment.submission_set.count()
            gradedSubs = assignment.submission_set.filter(score__isnull=False).count()
            assignment_graded_column.append({"assignment":assignment, "totalSubs":totalSubs, "gradedeSubs":gradedSubs})
    
    elif(is_ta(currentUser)):
        for assignment in assignments:
            submissions_assigned_to_you = assignment.submission_set.filter(grader=currentUser).count()
            submissions_you_graded = assignment.submission_set.filter(grader=currentUser, score__isnull=False).count()
            assignment_graded_column.append({"assignment":assignment, "submissions_you_graded":submissions_you_graded ,"submissions_assigned_to_you": submissions_assigned_to_you})
    
    # Student view
    elif(is_student(currentUser)):
        for assignment in assignments:
            submissionForAssignment = assignment.submission_set.filter(author=currentUser).first()
            if submissionForAssignment:
                # calculate the grade
                if submissionForAssignment.score is not None:
                    assignmentGrade= calculateAssignmentGrade(assignment, submissionForAssignment)
                    totalWeight += assignment.weight
                    currWeight += assignment.weight * assignmentGrade
                    assignment_graded_column.append({"assignment":assignment, "status":assignmentGrade})
                else:
                    assignment_graded_column.append({"assignment":assignment, "status":"Ungraded"})
            else:
                if assignment.deadline > datetime.now(timezone.utc):
                    totalWeight += assignment.weight
                    assignment_graded_column.append({"assignment":assignment, "status":"Missing"})
                elif assignment.deadline <= datetime.now(timezone.utc):
                    assignment_graded_column.append({"assignment":assignment, "status":"Not Due"})
        
        finalGrade = (totalWeight / currWeight) * 100
    return render(request, "profile.html", {
        "assignment_graded_column": assignment_graded_column,
        "user": currentUser,
        "finalGrade": finalGrade,
        "is_student": is_student(currentUser),
        "is_ta": is_student(currentUser),
        "is_superuser": currentUser.is_superuser
    })


def login_form(request):
    if request.method=="POST":
        u = request.POST.get("username", "")
        p = request.POST.get("password", "")            

        user = authenticate(username=u, password=p)

        if user is not None:
            login(request, user)
            return redirect("/profile/")
        else:
            return render(request, "login.html")
    return render(request, "login.html")

def show_upload(request, filename):
    submission = models.Submission.objects.get(file=filename)
    return HttpResponse(submission.file.open())

def logout_form(request):
    logout(request)
    return redirect("/profile/login/")


def is_student(user):
    return user.groups.filter(name="Students").exists()

def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists()

def calculateAssignmentGrade(assignment, submissionForAssignment):
    points = assignment.points
    score = submissionForAssignment.score
    return (score / points) * 100

