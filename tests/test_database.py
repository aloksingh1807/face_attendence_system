import unittest
import os
import sqlite3
import sys

# Add project root to path for local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db, init_db
from database.models import get_all_users, get_user_by_email
from flask import Flask

class TestDatabaseLayer(unittest.TestCase):
    """
    Unit test suite verifying SQLite schemas, connectivity, and data lookups.
    """
    
    def setUp(self):
        """
        Creates a temporary Flask environment using a temporary test SQLite database file.
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app = Flask(__name__, root_path=root_dir)
        self.db_path = os.path.join(root_dir, 'instance', 'test_attendance.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.app.config['DATABASE'] = self.db_path
        
        # Initialize schema and seed admin
        init_db(self.app)
        
    def tearDown(self):
        """
        Removes the temporary test database file.
        """
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except:
                pass
        
    def test_admin_seeding(self):
        """
        Tests that database creation automatically inserts the default administrator.
        """
        with self.app.app_context():
            # Query for seeded Admin
            admin = get_user_by_email("admin@aurascan.com")
            
            self.assertIsNotNone(admin)
            self.assertEqual(admin["name"], "System Admin")
            self.assertEqual(admin["role"], "Admin")
            self.assertIsNotNone(admin["password_hash"])
            
    def test_models_retrieval(self):
        """
        Tests model wrapper listings.
        """
        with self.app.app_context():
            # Fetch all users (which only contains the Admin seed)
            users = get_all_users()
            
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0]["email"], "admin@aurascan.com")

if __name__ == '__main__':
    unittest.main()
