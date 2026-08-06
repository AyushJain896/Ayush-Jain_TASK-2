"""
Database Module for BMI Calculator & Health Tracker
===================================================
This module handles all database interactions using SQLite3.
It creates the database schema automatically, stores calculation records,
retrieves user history, fetches distinct user profiles, and allows record management.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

# Default database file name
DEFAULT_DB_PATH = "bmi.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Creates and returns a SQLite database connection with row factory configured.

    Args:
        db_path (str): File path to the SQLite database.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes the SQLite database by creating the `BMI_Records` table if it does not exist.

    Table Schema:
        BMI_Records:
            - id: INTEGER PRIMARY KEY AUTOINCREMENT
            - username: TEXT NOT NULL
            - weight: REAL NOT NULL (in kg)
            - height: REAL NOT NULL (in meters)
            - bmi: REAL NOT NULL
            - category: TEXT NOT NULL
            - date: TEXT NOT NULL (Timestamp format: YYYY-MM-DD HH:MM:SS)

    Args:
        db_path (str): File path to the SQLite database.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS BMI_Records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        weight REAL NOT NULL,
        height REAL NOT NULL,
        bmi REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL
    );
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
    except sqlite3.Error as e:
        print(f"[Database Error] Failed to initialize database schema: {e}")
        raise e


def save_record(
    username: str,
    weight: float,
    height: float,
    bmi: float,
    category: str,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Saves a new BMI calculation record to the database with the current timestamp.

    Args:
        username (str): User's identifier.
        weight (float): User's weight in kg.
        height (float): User's height in meters.
        bmi (float): Calculated BMI value.
        category (str): Health category (e.g. Underweight, Normal Weight, Overweight, Obese).
        db_path (str): Database file path.

    Returns:
        int: The ID of the newly inserted database row.

    Raises:
        sqlite3.Error: If the insert query fails.
    """
    # Format current date and time
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_sql = """
    INSERT INTO BMI_Records (username, weight, height, bmi, category, date)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(insert_sql, (username, weight, height, bmi, category, current_timestamp))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"[Database Error] Failed to save record for user '{username}': {e}")
        raise e


def get_user_history(username: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves all BMI records for a specific user, sorted by date in ascending order.

    Args:
        username (str): Username to filter records.
        db_path (str): Database file path.

    Returns:
        List[Dict[str, Any]]: List of dictionary records containing:
            id, username, weight, height, bmi, category, date.
    """
    select_sql = """
    SELECT id, username, weight, height, bmi, category, date
    FROM BMI_Records
    WHERE LOWER(username) = LOWER(?)
    ORDER BY date ASC, id ASC;
    """
    records = []
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(select_sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                records.append({
                    "id": row["id"],
                    "username": row["username"],
                    "weight": row["weight"],
                    "height": row["height"],
                    "bmi": row["bmi"],
                    "category": row["category"],
                    "date": row["date"]
                })
    except sqlite3.Error as e:
        print(f"[Database Error] Failed to retrieve history for user '{username}': {e}")
        raise e

    return records


def get_all_users(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """
    Fetches a list of all distinct usernames stored in the database, sorted alphabetically.

    Args:
        db_path (str): Database file path.

    Returns:
        List[str]: List of unique user names.
    """
    select_sql = "SELECT DISTINCT username FROM BMI_Records ORDER BY username COLLATE NOCASE ASC;"
    users = []
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(select_sql)
            rows = cursor.fetchall()
            users = [row["username"] for row in rows]
    except sqlite3.Error as e:
        print(f"[Database Error] Failed to retrieve user list: {e}")
        raise e

    return users


def delete_record(record_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Deletes a specific record by its primary key ID.

    Args:
        record_id (int): Primary key ID of the record.
        db_path (str): Database file path.

    Returns:
        bool: True if a row was deleted, False otherwise.
    """
    delete_sql = "DELETE FROM BMI_Records WHERE id = ?;"
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_sql, (record_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[Database Error] Failed to delete record ID {record_id}: {e}")
        raise e


def clear_user_history(username: str, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Deletes all records associated with a specific username.

    Args:
        username (str): Username whose history should be cleared.
        db_path (str): Database file path.

    Returns:
        int: Number of deleted records.
    """
    delete_sql = "DELETE FROM BMI_Records WHERE LOWER(username) = LOWER(?);"
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_sql, (username,))
            conn.commit()
            return cursor.rowcount
    except sqlite3.Error as e:
        print(f"[Database Error] Failed to clear history for user '{username}': {e}")
        raise e
