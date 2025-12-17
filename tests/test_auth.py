import unittest
import os
from app import create_app, db
from app.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config=True)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        response = self.client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Check if user was created
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')
        
        # Check redirect to login
        self.assertIn(b'Iniciar Sesion', response.data.replace(b'\xc3\xb3', b'o'))

    def test_login(self):
        # Create user first
        u = User(name='Test User', email='test@example.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

        # Login
        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Check if logged in (should see chats page or redirect to a chat)
        self.assertIn(b'Wavii', response.data) 


if __name__ == '__main__':
    unittest.main()
