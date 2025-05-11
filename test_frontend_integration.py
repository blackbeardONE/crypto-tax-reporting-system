import unittest
from ui import app

class AdminPanelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def login(self, username, password):
        return self.app.post('/admin/auth/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/admin/auth/logout', follow_redirects=True)

    def test_admin_login_logout(self):
        rv = self.login('admin', 'adminpass')
        self.assertIn(b'Admin Dashboard', rv.data)
        rv = self.logout()
        self.assertIn(b'Admin Login', rv.data)

    def test_access_protected_route_without_login(self):
        rv = self.app.get('/admin/users', follow_redirects=True)
        self.assertIn(b'Admin Login', rv.data)

    def test_user_crud(self):
        self.login('admin', 'adminpass')
        # Create user
        rv = self.app.post('/admin/users', json={
            'username': 'testuser',
            'password': 'testpass',
            'complete_name': 'Test User',
            'company_name': 'Test Co',
            'company_address': '123 Test St',
            'company_email': 'test@example.com',
            'company_phone': '1234567890'
        })
        self.assertEqual(rv.status_code, 201)
        # Get users
        rv = self.app.get('/admin/users')
        self.assertIn(b'testuser', rv.data)
        # Update user
        rv = self.app.put('/admin/users/testuser', json={
            'company_phone': '0987654321'
        })
        self.assertEqual(rv.status_code, 200)
        # Delete user
        rv = self.app.delete('/admin/users/testuser')
        self.assertEqual(rv.status_code, 200)
        self.logout()

if __name__ == '__main__':
    unittest.main()
