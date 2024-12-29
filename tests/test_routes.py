import unittest
from app import create_app, db
from app.models import User
from flask import url_for

class TestRoutes(unittest.TestCase):

    def setUp(self):
        app = create_app()  # Create the app using the create_app function
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite for testing
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registration(self):
        response = self.app.post('/register', data={'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check for redirection after successful registration

        response = self.app.post('/register', data={'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 200) # Check for error on duplicate username

    def test_login(self):
        # Register a test user
        self.app.post('/register', data={'username': 'testuser', 'password': 'password'})
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check for redirection after successful login

        response = self.app.post('/login', data={'username': 'wronguser', 'password': 'password'})
        self.assertEqual(response.status_code, 200)  # Check unsuccessful login attempt

    def test_logout(self):
        # Register and login a user
        self.app.post('/register', data={'username': 'testuser', 'password': 'password'})
        self.app.post('/login', data={'username': 'testuser', 'password': 'password'})
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302) # check redirect after successful logout

    def test_upload(self):
        # Test without login
        response = self.app.post('/upload', data={'file': 'test'}) # Test file upload without login
        self.assertEqual(response.status_code, 302) # expect redirect to login

        # Test with Login
        self.app.post('/register', data={'username': 'testuser', 'password': 'password'})
        self.app.post('/login', data={'username': 'testuser', 'password': 'password'})
        with open("test.txt", "w") as f:
            f.write("Test file content")
        with open("test.txt", "rb") as f:
            response = self.app.post('/upload', data={'file':(f, 'test.txt')})
        import os
        os.remove("test.txt")
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        # Test without login
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 302)

        # Test with login
        self.app.post('/register', data={'username': 'testuser', 'password': 'password'})
        self.app.post('/login', data={'username': 'testuser', 'password': 'password'})
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
