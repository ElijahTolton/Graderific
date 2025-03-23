from django.db import models
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.core.exceptions import PermissionDenied

# Create your models here.

# Assignment model with title, description, deadline, weight, points
class Assignment(models.Model):
    title = models.CharField(max_length=199)
    description = models.TextField()
    deadline = models.DateTimeField()
    weight = models.IntegerField(default=100)
    points = models.IntegerField(default=100)

    def __str__(self):
        return self.title + ": " + self.description

# Submission model with assignment, author
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE) # if assignment is deleted, delete all submissions
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='graded_set', null=True) # Allow grader feild to be null
    file = models.FileField()
    score = models.DecimalField(null=True, decimal_places=2, max_digits=5)  # Allow score to be null, when it has not been graded

    def __str__(self):
        return f"{self.assignment.title} by {self.author.username}"
    
    # Define the security policy in one place
    def changedGrade(self, user, grade):
        if user.groups.filter(name="Teaching Assistants").exists() or user.is_superuser:
            self.score = grade
            print("hello")
        else:
            raise PermissionDenied("You do not have premission to change grades")
