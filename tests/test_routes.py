import unittest
import sys
import os
from flask import Flask

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

class TestFlaskRoutes(unittest.TestCase):
    """
    Unit test suite validating session locks, authentication redirects, and endpoints.
    """
    
    def setUp(self):
        """
        Initializes our modular Flask application in test mode with an in-memory DB.
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app = create_app({
            'TESTING': True,
            'SECRET_KEY': 'testing_key',
            'DATABASE': ':memory:',
            'UPLOAD_PROFILES_DIR': os.path.join(root_dir, 'instance', 'test_uploads', 'profiles'),
            'UPLOAD_ALERTS_DIR': os.path.join(root_dir, 'instance', 'test_uploads', 'alerts')
        })
        self.client = self.app.test_client()
        
    def tearDown(self):
        """
        Clean up created test upload directories if any.
        """
        import shutil
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_uploads = os.path.join(root_dir, 'instance', 'test_uploads')
        if os.path.exists(test_uploads):
            shutil.rmtree(test_uploads)
            
    def test_unauthenticated_redirect(self):
        """
        Tests that requesting locked pages (like the camera or logs) without a logged session
        properly redirects the visitor back to the login portal.
        """
        response = self.client.get('/camera')
        
        # Should redirect (Status 302)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])
        
    def test_login_page_loads(self):
        """
        Tests that the login portal loads successfully (Status 200).
        """
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
