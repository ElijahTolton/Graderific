from django.shortcuts import redirect, render
from . import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q


# Create your views here.

# Handle HTTP requests for static webpages.
def index(request):
    assignmentList = models.Assignment.objects.all()

    context = {
        "assignments": assignmentList
    }

    return render(request, "index.html", context)

def assignment(request, assignmentID):
    currUser = User.objects.get(username='g') # Get the current user
    currAssign = get_object_or_404(models.Assignment, id=assignmentID) # Get the assignment object
    submissions = currAssign.submission_set
    totSubmissions = submissions.count() # Get the total number of submissions for this assignment
    myAssignedSubmissionCt = currUser.graded_set.filter(assignment=currAssign).count # number of submissions assigned to this user in this assignment
    numStudents = models.Group.objects.get(name="Students").user_set.count() # total number of students

    context = {
        "submissionCount" : totSubmissions,
        "mySubmissionCt" : myAssignedSubmissionCt,
        "numStudents" : numStudents,
        "assignment" : currAssign,
    }

    return render(request, "assignment.html", context)

def submissions(request, assignmentID):
    if request.method == "POST":
        grades = processGrades(request.POST)
        for subID, grade in grades.items():
            submission = models.Submission.objects.get(id=subID)
            if grade is None:
                submission.score = ""    
            else:
                submission.score = grade
            submission.save()
        return redirect(f"/{assignmentID}/submissions/")

    currUser = User.objects.get(username='g') # Get the current user
    currAssign = models.Assignment.objects.get(id=assignmentID)
    submissions = currAssign.submission_set.filter(grader=currUser).order_by('author__username')

    context = {
        "user" : currUser,
        "assignment" : currAssign,
        "submissions" : submissions,
    }
    
    return render(request, "submissions.html", context)

def processGrades( updatedGrades ):
    grades = {}
    for submission in updatedGrades:
        # Skip any keys that don't start with grade-
        if submission.startswith("grade-"):
            subID = int(submission.removeprefix("grade-"))
            grades[subID] = updatedGrades[submission]
    return grades

def profile(request):
    currUser = User.objects.get(username='g') # Get the current user
    assignmentList = models.Assignment.objects.annotate(
        totalSubmissions=Count('submission', filter=Q(submission__grader=currUser)),
        gradedSubmissions=Count('submission', filter=Q(submission__grader=currUser, submission__score__isnull=False)),
    )

    context = {
        "curUser" : currUser,
        "assignments" : assignmentList,
    }

    return render(request, "profile.html", context)

def login_form(request):
    return render(request, "login.html")