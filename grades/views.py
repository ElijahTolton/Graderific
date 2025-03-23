from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from . import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import PermissionDenied

# Create your views here.

@login_required
def index(request):
    assignmentList = models.Assignment.objects.all()

    context = {
        "assignments": assignmentList
    }

    return render(request, "index.html", context)

@login_required
def assignment(request, assignmentID):
    currUser = request.user # Get the current user
    currAssign = get_object_or_404(models.Assignment, id=assignmentID) # Get the assignment object
    submissions = currAssign.submission_set
    totSubmissions = submissions.count() # Get the total number of submissions for this assignment
    myAssignedSubmissionCt = 1
    numStudents = 1
    userSubmission = None
    submissionStatus = ""
    percentageGrade = 0

    # Determine the type of the user
    isStudent = currUser.groups.filter(name="Students").exists()
    isTa = currUser.groups.filter(name="Teaching Assistants").exists()
    isAnonymous = not currUser.is_authenticated
    isAdmin = currUser.is_superuser

    try:
        userSubmission = models.Submission.objects.filter(assignment=currAssign, author=currUser).last()
    except:
        userSubmission = None

    if isStudent:
        if userSubmission is None:
            if currAssign.deadline < now():
                submissionStatus = "Missing"
            else:
                submissionStatus = "Not Due"
        else:
            if userSubmission.score is None and currAssign.deadline < now():
                submissionStatus = "Being Graded"
            elif userSubmission.score is None and currAssign.deadline > now():
                submissionStatus = "Ungraded"
            else:
                submissionStatus = "Graded"
                percentageGrade = (userSubmission.score / currAssign.points) * 100
    elif isAnonymous:
        submissionStatus = "Not Due"
        userSubmission = None
        myAssignedSubmissionCt = 0
    elif isTa:
        myAssignedSubmissionCt = currUser.graded_set.filter(assignment=currAssign).count # number of submissions assigned to this user in this assignment
        numStudents = models.Group.objects.get(name="Students").user_set.count() # total number of students
    else:
        # This is the superuser
        numStudents = models.Group.objects.get(name="Students").user_set.count() # total number of students
        userSubmission = None
        myAssignedSubmissionCt = totSubmissions

    if request.method == "POST" and 'file' in request.FILES:
        if isStudent:
            fileSub = request.FILES['file']
            
            if userSubmission is not None:
                if currAssign.deadline < now():
                    return HttpResponseBadRequest("Submission deadline has passed. You cannot update your submission.")
                else:
                    userSubmission.file = fileSub
                    userSubmission.save()
            else:
                # Uses pick grader function which selects the TA with the least to grade.
                models.Submission.objects.create(assignment=currAssign, author=currUser, file=fileSub, score=None, grader=pick_grader(currAssign))
            return redirect(f"/{assignmentID}/")


    context = {
        "submissionCount" : totSubmissions,
        "mySubmissionCt" : myAssignedSubmissionCt,
        "numStudents" : numStudents,
        "assignment" : currAssign,
        "userSub" : userSubmission,
        "student" : isStudent,
        "ta" : isTa,
        "loggedOut" :isAnonymous,
        "superUser" : isAdmin,
        "submissionStatus" : submissionStatus,
        "percentageGrade" : percentageGrade,
    }

    return render(request, "assignment.html", context)

@login_required
def submissions(request, assignmentID):
    currAssign = models.Assignment.objects.get(id=assignmentID)
    errors = {}
    currUser = request.user # Get the current user

    if request.method == "POST":
        # get all changed grades and associate them with a submission ID
        grades = processGrades(request.POST, errors)
        for subID, grade in grades.items():
            try:
                # If it is a valid submission update the value, otherwise add to errors map
                submission = models.Submission.objects.get(id=subID, assignment=currAssign)
                if grade == None:
                    submission.changedGrade(currUser, None)
                    submission.save()
                elif (grade < 0 or grade > currAssign.points):
                    # Check that the grade is within the bounds
                    errors[subID] = f"Grade must be between 0 and {currAssign.points}"
                else:
                    submission.changedGrade(currUser, int(grade))
                    submission.save()
            except Exception as e:
                print(f"Error processing submission {subID}: {e}")
                errors[subID] = "Submission does not exist or is not part of this assignment."

    if currUser.is_superuser:
        submissions = currAssign.submission_set.all()
    else:
        submissions = currAssign.submission_set.filter(grader=currUser).order_by('author__username')

    # Ensure that the current user is a ta
    isTa = currUser.groups.filter(name="Teaching Assistants").exists()
    if not isTa and not currUser.is_superuser:
        raise PermissionDenied("You do not have permission to access this page.")

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

@login_required
def profile(request):
    currUser = request.user # Get the current user

    isStudent = currUser.groups.filter(name="Students").exists()
    finalGrade = 0
    
    # Show the staff view of the table
    if not isStudent:
        if currUser.is_superuser:
            assignmentList = models.Assignment.objects.annotate(
                totalSubmissions=Count('submission'),
                gradedSubmissions=Count('submission', filter=Q(submission__score__isnull=False)),
            )
        else:
            assignmentList = models.Assignment.objects.annotate(
                totalSubmissions=Count('submission', filter=Q(submission__grader=currUser)),
                gradedSubmissions=Count('submission', filter=Q(submission__grader=currUser, submission__score__isnull=False)),
            )
    else:
        # Show the student's assignments and grades
        assignmentList = models.Assignment.objects.all()
        totalWeight = 0
        totalEarned = 0

        for assignment in assignmentList:
            try:
                submission = assignment.submission_set.filter(author=currUser).last()
            except:
                submission = None

            earnedPoints = 0
            percentageGrade = 0
            # Calcuate submission status
            if submission is None:
                if assignment.deadline < now():
                    subStatus = "Missing"
                    totalWeight += assignment.weight
                else:
                    subStatus = "Not Due"
            else:
                if submission.score is None:
                    subStatus = "Ungraded"
                else:
                    subStatus = "Graded"
                    percentageGrade = (submission.score / assignment.points) * 100
                    earnedPoints = (submission.score / assignment.points) * assignment.weight
                    totalWeight += assignment.weight
                    totalEarned += earnedPoints
            
            setattr(assignment, "submissionStatus", subStatus)
            setattr(assignment, "percentageScore", percentageGrade)
            setattr(assignment, "score", submission.score if submission else None)
            setattr(assignment, "earnedPoints", earnedPoints)

        finalGrade = round((totalEarned / totalWeight) * 100, 1)
        
    context = {
        "curUser" : currUser,
        "assignments" : assignmentList,
        "student" : isStudent,
        "finalGrade" : finalGrade
    }

    return render(request, "profile.html", context)

def login_form(request):
    next = request.GET.get("next", "/profile/")
    print(next)

    if request.method == "POST":
        loginInfo = request.POST
        user = loginInfo.get("user", "")
        passWord = loginInfo.get("pass", "")
        next = loginInfo.get("next", "/profile/")

        # Authenticate the user
        user = authenticate(username=user, password=passWord)
        if user is not None:
            login(request, user)
        else:
            error = {"error" :"Username and password do not match"}
            return render(request, "login.html", error)

        # Ensure that redirect is from our own server
        if url_has_allowed_host_and_scheme(next, None):
            return redirect(next)
        else:
            return redirect("/")

    return render(request, "login.html", context = {"next" : next})

def logout_form(request):
    logout(request)
    return redirect("login")

# Show file submisisons in the browser
@login_required
def show_upload(request, filename):
    submission = models.Submission.objects.get(file__endswith=filename)
    return HttpResponse(submission.file.open())

# Choose the TA with the least assignments to grade to grade new assignment.
def pick_grader(assignment):
    tas = models.Group.objects.get(name="Teaching Assistants").user_set.annotate(
        total_assigned=Count('graded_set')
    ).order_by('total_assigned')
    print(tas.first())
    return tas.first()