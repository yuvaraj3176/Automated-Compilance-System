import unittest
from app import create_app, db
from app.models import User
from app import bcrypt

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.bcrypt = bcrypt
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_registration(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        with self.app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'testuser')
    
    def test_login(self):
        # Create user first
        with self.app.app_context():
            hashed_password = self.bcrypt.generate_password_hash('password123')
            user = User(username='testuser', email='test@example.com', password=hashed_password)
            db.session.add(user)
            db.session.commit()
        
        # Test login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123',
            'remember': False
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

if __name__ == '__main__':
    unittest.main()