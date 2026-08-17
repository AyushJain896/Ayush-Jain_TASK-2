"""
Unit Tests for SQLite Database Module (database.py)
"""

import os
import sqlite3
import unittest
from database import (
    init_db,
    save_record,
    get_user_history,
    get_all_users,
    delete_record,
    clear_user_history
)

TEST_DB = "test_bmi.db"


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        """Initialize temporary database for testing."""
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)

    def tearDown(self):
        """Clean up test database file."""
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_save_and_retrieve_history(self):
        """Test saving records and querying user history."""
        row_id = save_record("Charlie", 70.0, 1.75, 22.86, "Normal Weight", db_path=TEST_DB)
        self.assertGreater(row_id, 0)

        history = get_user_history("Charlie", db_path=TEST_DB)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["username"], "Charlie")
        self.assertEqual(history[0]["bmi"], 22.86)

    def test_get_all_users(self):
        """Test retrieving distinct user names."""
        save_record("Alice", 60.0, 1.65, 22.04, "Normal Weight", db_path=TEST_DB)
        save_record("Bob", 85.0, 1.80, 26.23, "Overweight", db_path=TEST_DB)
        save_record("Alice", 59.0, 1.65, 21.67, "Normal Weight", db_path=TEST_DB)

        users = get_all_users(db_path=TEST_DB)
        self.assertEqual(users, ["Alice", "Bob"])

    def test_delete_record(self):
        """Test deleting individual record."""
        row_id = save_record("David", 90.0, 1.70, 31.14, "Obese", db_path=TEST_DB)
        deleted = delete_record(row_id, db_path=TEST_DB)
        self.assertTrue(deleted)

        history = get_user_history("David", db_path=TEST_DB)
        self.assertEqual(len(history), 0)

    def test_clear_user_history(self):
        """Test clearing all records for a user."""
        save_record("Eva", 50.0, 1.60, 19.53, "Normal Weight", db_path=TEST_DB)
        save_record("Eva", 52.0, 1.60, 20.31, "Normal Weight", db_path=TEST_DB)

        count = clear_user_history("Eva", db_path=TEST_DB)
        self.assertEqual(count, 2)

        history = get_user_history("Eva", db_path=TEST_DB)
        self.assertEqual(len(history), 0)


if __name__ == "__main__":
    unittest.main()
