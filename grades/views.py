from django.http import HttpResponse
from django.shortcuts import redirect, render
from . import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout

# Create your views here.

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

    # Display alices algorithmer student submission view for each assignment
    alice = User.objects.get(username='a')  # Get Alice Algorithm
    try:
        aliceSubmission = models.Submission.objects.filter(assignment=currAssign, author=alice).last()
    except:
        aliceSubmission = None
    
    if request.method == "POST" and 'file' in request.FILES:
        fileSub = request.FILES['file']
        
        if aliceSubmission is not None:
            aliceSubmission.file = fileSub
            aliceSubmission.save()
        else:
            models.Submission.objects.create(assignment=currAssign, author=alice, file=fileSub, score=None, grader=currUser)
        return redirect(f"/{assignmentID}/")

    context = {
        "submissionCount" : totSubmissions,
        "mySubmissionCt" : myAssignedSubmissionCt,
        "numStudents" : numStudents,
        "assignment" : currAssign,
        "aliceSub" : aliceSubmission,
    }

    return render(request, "assignment.html", context)

def submissions(request, assignmentID):
    currAssign = models.Assignment.objects.get(id=assignmentID)
    errors = {}

    if request.method == "POST":
        # get all changed grades and associate them with a submission ID
        grades = processGrades(request.POST, errors)
        for subID, grade in grades.items():
            try:
                # If it is a valid submission update the value, otherwise add to errors map
                submission = models.Submission.objects.get(id=subID, assignment=currAssign)
                if grade == None:
                    submission.score = None
                    submission.save()
                elif (grade < 0 or grade > currAssign.points):
                    # Check that the grade is within the bounds
                    errors[subID] = f"Grade must be between 0 and {currAssign.points}"
                else:
                    submission.score = int(grade)
                    submission.save()
            except:
                errors[subID] = "Submission does not exist or is not part of this assignment."

    currUser = User.objects.get(username='g') # Get the current user
    submissions = currAssign.submission_set.filter(grader=currUser).order_by('author__username')

    context = {
        "user" : currUser,
        "assignment" : currAssign,
        "submissions" : submissions,
        "errors" : errors
    }
    
    return render(request, "submissions.html", context)

def processGrades( updatedGrades , errors):
    grades = {}
    for submission in updatedGrades:
        # Skip any keys that don't start with grade-
        if submission.startswith("grade-"):
            subID = int(submission.removeprefix("grade-"))
            grade = updatedGrades[submission]
            if grade == "":
                grades[subID] = None
            else:
                # Ensure only numbers are entered as grades
                try:
                    gradeNum = float(grade)
                    gradeNum = int(gradeNum)
                    grades[subID] = gradeNum
                except Exception as e:
                    errors[subID] = "Grade must be a number"
    return grades

def profile(request):
    currUser = request.user # Get the current user

    if currUser.is_anonymous:
        return redirect("/profile/login")
        
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

    if request.method == "POST":
        loginInfo = request.POST
        user = loginInfo.get("user", "")
        passWord = loginInfo.get("pass", "")
        user = authenticate(username=user, password=passWord)
        if user is not None:
            login(request, user)
            return redirect("/profile/")
        else:
            print("Athuntificatio failed")
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

def logout_form(request):
    logout(request)
    return render(request, "login.html")



# Show file submisisons in the browser
def show_upload(request, filename):
    submission = models.Submission.objects.get(file__endswith=filename)
    return HttpResponse(submission.file.open())