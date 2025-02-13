from django.shortcuts import render

# Create your views here.

# Handle HTTP requests for static webpages.
def index(request):
    return render(request, "index.html")

def assignment(request, assignmentID):
    return render(request, "assignment.html")

def submissions(request, assignmentID):
    return render(request, "submissions.html")

def profile(request):
    return render(request, "profile.html")

def login_form(request):
    return render(request, "login.html")