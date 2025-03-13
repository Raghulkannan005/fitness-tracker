import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'src'))

# Import required modules
from app import FitnessTrackerApp
from database import create_db, reset_database
from setup_assets import setup_assets

def launch_app():
    """Launch the Fitness Tracker application."""
    # Create assets
    try:
        setup_assets()
    except Exception as e:
        print(f"Warning: Could not create assets: {e}")
    
    # Ensure database is initialized
    try:
        create_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        if messagebox.askyesno("Database Error", 
                              f"Error initializing database: {e}\n\nWould you like to reset the database? (This will delete all existing data)"):
            reset_database()
    
    # Launch the application
    root = tk.Tk()
    try:
        app = FitnessTrackerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        print(f"Application error: {e}")
        root.destroy()

if __name__ == "__main__":
    launch_app()