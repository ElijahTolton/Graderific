from django.shortcuts import render
from . import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


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
    totSubmissions = currAssign.submission_set.count() # Get the total number of submissions for this assignment
    myAssignedSubmissionCt = currUser.graded_set.count() # number of submissions assigned to this user
    numStudents = models.Group.objects.get(name="Students").user_set.count() # total number of students

    context = {
        "submissionCount" : totSubmissions,
        "mySubmissionCt" : myAssignedSubmissionCt,
        "numStudents" : numStudents,
        "assignment" : currAssign,
    }

    return render(request, "assignment.html", context)

def submissions(request, assignmentID):
    return render(request, "submissions.html")

def profile(request):
    return render(request, "profile.html")

def login_form(request):
    return render(request, "login.html")