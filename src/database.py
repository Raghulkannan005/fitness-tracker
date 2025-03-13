import sqlite3
import datetime
from typing import List, Dict, Any, Tuple, Optional

def create_db():
    """Create a SQLite database and tables if they don't exist."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Create workouts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_type TEXT NOT NULL,
            duration REAL NOT NULL,
            calories_burned REAL NOT NULL,
            session_id INTEGER,
            date TEXT NOT NULL,
            notes TEXT,
            intensity TEXT DEFAULT 'Medium',
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            total_duration REAL,
            total_calories REAL,
            notes TEXT,
            rating INTEGER
        )
    ''')

    # Create goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_type TEXT NOT NULL,
            target_value REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            notes TEXT
        )
    ''')

    # Create user_profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            gender TEXT,
            bmr REAL,
            activity_level TEXT,
            date_updated TEXT
        )
    ''')

    conn.commit()
    conn.close()
    
    # Perform schema migrations if needed
    migrate_database()

def migrate_database():
    """Update database schema if needed."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    # Check if 'intensity' column exists in workouts table
    cursor.execute("PRAGMA table_info(workouts)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'intensity' not in columns:
        try:
            print("Migrating database: Adding 'intensity' column to workouts table")
            cursor.execute("ALTER TABLE workouts ADD COLUMN intensity TEXT DEFAULT 'Medium'")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error during migration: {e}")
    
    # Check for other required columns
    if 'notes' not in columns:
        try:
            print("Migrating database: Adding 'notes' column to workouts table")
            cursor.execute("ALTER TABLE workouts ADD COLUMN notes TEXT")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error during migration: {e}")
    
    conn.close()

# Add function to reset database if needed (be careful with this!)
def reset_database():
    """Delete and recreate the database with empty tables."""
    import os
    try:
        if os.path.exists('fitness_tracker.db'):
            os.remove('fitness_tracker.db')
            print("Database reset: Deleted existing database.")
        create_db()
        print("Database reset: Created new empty database.")
        return True
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False

def add_workout(workout_type, duration, calories_burned, session_id, intensity="Medium", notes=""):
    """Insert a new workout into the database."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO workouts (workout_type, duration, calories_burned, session_id, date, notes, intensity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (workout_type, duration, calories_burned, session_id, date, notes, intensity))
    conn.commit()
    conn.close()

def add_session(start_time, end_time, total_duration, total_calories, session_id=None, notes="", rating=None):
    """Insert or update a session in the database."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    if session_id:
        # Update existing session
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, total_duration = ?, total_calories = ?, notes = ?, rating = ?
            WHERE id = ?
        ''', (end_time, total_duration, total_calories, notes, rating, session_id))
    else:
        # Insert new session
        cursor.execute('''
            INSERT INTO sessions (start_time, end_time, total_duration, total_calories, notes, rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (start_time, end_time, total_duration, total_calories, notes, rating))
        session_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return session_id

def get_session_details(session_id):
    """Retrieve all workouts for a session."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT workout_type, duration, calories_burned, intensity, notes
        FROM workouts
        WHERE session_id = ?
    ''', (session_id,))
    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_sessions(start_date=None, end_date=None):
    """Retrieve sessions from the database with optional date filtering."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    query = 'SELECT * FROM sessions'
    params = []
    
    if start_date and end_date:
        query += ' WHERE start_time BETWEEN ? AND ?'
        params = [start_date, end_date]
    elif start_date:
        query += ' WHERE start_time >= ?'
        params = [start_date]
    elif end_date:
        query += ' WHERE start_time <= ?'
        params = [end_date]
    
    query += ' ORDER BY start_time DESC'
    
    cursor.execute(query, params)
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_stats_by_workout_type(start_date=None, end_date=None):
    """Get statistics grouped by workout type."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            workout_type, 
            COUNT(*) as count, 
            SUM(duration) as total_duration, 
            AVG(duration) as avg_duration,
            SUM(calories_burned) as total_calories,
            AVG(calories_burned) as avg_calories,
            AVG(CASE 
                WHEN intensity = 'High' THEN 3
                WHEN intensity = 'Medium' THEN 2
                ELSE 1
            END) as avg_intensity
        FROM workouts
    '''
    
    params = []
    if start_date and end_date:
        query += ' WHERE date BETWEEN ? AND ?'
        params = [start_date, end_date]
    elif start_date:
        query += ' WHERE date >= ?'
        params = [start_date]
    elif end_date:
        query += ' WHERE date <= ?'
        params = [end_date]
    
    query += ' GROUP BY workout_type ORDER BY total_duration DESC'
    
    cursor.execute(query, params)
    stats = cursor.fetchall()
    conn.close()
    return stats

def update_session(session_id, end_time=None, total_duration=None, total_calories=None, notes=None, rating=None):
    """Update session details."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if end_time is not None:
        updates.append("end_time = ?")
        params.append(end_time)
    
    if total_duration is not None:
        updates.append("total_duration = ?")
        params.append(total_duration)
        
    if total_calories is not None:
        updates.append("total_calories = ?")
        params.append(total_calories)
        
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
        
    if rating is not None:
        updates.append("rating = ?")
        params.append(rating)
    
    if updates:
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        params.append(session_id)
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()

def add_goal(goal_type, target_value, start_date, end_date, notes=""):
    """Add a new fitness goal."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO goals (goal_type, target_value, start_date, end_date, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (goal_type, target_value, start_date, end_date, notes))
    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id

def get_active_goals():
    """Get all active goals (end date in the future)."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM goals 
        WHERE end_date >= ? AND completed = 0
        ORDER BY end_date ASC
    ''', (today,))
    goals = cursor.fetchall()
    conn.close()
    return goals

def update_goal_progress(goal_id, completed=None):
    """Update the status of a goal."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    if completed is not None:
        cursor.execute('''
            UPDATE goals
            SET completed = ?
            WHERE id = ?
        ''', (1 if completed else 0, goal_id))
    
    conn.commit()
    conn.close()

def save_user_profile(name, age, weight, height, gender, activity_level, bmr=None):
    """Save user profile information."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    # Calculate BMR if not provided
    if bmr is None:
        if gender.lower() == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Check if profile exists
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    count = cursor.fetchone()[0]
    
    date_updated = datetime.datetime.now().strftime('%Y-%m-%d')
    
    if count == 0:
        # Insert new profile
        cursor.execute('''
            INSERT INTO user_profile 
            (name, age, weight, height, gender, activity_level, bmr, date_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, weight, height, gender, activity_level, bmr, date_updated))
    else:
        # Update existing profile
        cursor.execute('''
            UPDATE user_profile 
            SET name = ?, age = ?, weight = ?, height = ?, gender = ?,
                activity_level = ?, bmr = ?, date_updated = ?
            WHERE id = 1
        ''', (name, age, weight, height, gender, activity_level, bmr, date_updated))
    
    conn.commit()
    conn.close()

def get_user_profile():
    """Get the user profile information."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    profile = cursor.fetchone()
    conn.close()
    return profile

def get_trends(period_days=30):
    """Get workout trends over a specified period."""
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    
    # Calculate the date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=period_days)
    
    # Query for daily workout stats
    cursor.execute('''
        SELECT 
            date,
            COUNT(*) as workout_count,
            SUM(duration) as total_duration,
            SUM(calories_burned) as total_calories
        FROM workouts
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date ASC
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    trends = cursor.fetchall()
    conn.close()
    return trends