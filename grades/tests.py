from django.test import TestCase
from django.test import Client
from .models import Assignment, Submission, User

# Create your tests here.
class GradingAppTests(TestCase):
    def setUp(self):
        # Set up test database below.
        # assign = Assignment.objects.create(title="A8", description="Testing website")
        # Submission.objects.create(assignment = assign, author=)
        # Use actual databse with pass keyword.
        pass
    
    # Test that we properly get the login page.
    def test_login_true(self):
        client = Client()
        response = client.get("/profile/login/")
        print(str(response.content))
        self.assertTrue("Log in" in str(response.content))