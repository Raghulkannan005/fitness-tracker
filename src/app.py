# Fix the imports at the top of app.py
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import calendar
from PIL import Image, ImageTk
import webbrowser
import threading
import sqlite3

# Remove the dot from relative imports
from session import Session  # Changed from .session
from workout import Workout  # Changed from .workout
from database import (create_db, get_sessions, get_session_details,
                     get_stats_by_workout_type, get_user_profile,
                     save_user_profile, add_goal, get_trends)

# Initialize the database
create_db()

def validate_positive_number(value):
    """Validate that the input is a positive number."""
    try:
        number = float(value)
        if number <= 0:
            raise ValueError("The number must be positive.")
        return number
    except ValueError:
        raise ValueError("Invalid input. Please enter a positive number.")

class FitnessTrackerApp:
    def __init__(self, root):
        """Initialize the application with the given root window."""
        self.root = root
        self.root.title("Fitness Tracker Pro")
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        self.session = Session()
        self.current_tab = None
        self.chart_instances = {}

        # Initialize theme and styles
        self.theme = "light"
        self.accent_colors = {
            "primary": "#2196F3",  # Blue
            "secondary": "#4CAF50",  # Green
            "accent": "#FF4081",  # Pink
            "warning": "#FFC107",  # Amber
            "error": "#F44336",  # Red
            "success": "#4CAF50",  # Green
            "info": "#2196F3"  # Blue
        }
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create main container with padding
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Add status bar
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(
            self.status_frame, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add progress bar for background operations
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame, 
            variable=self.progress_var,
            mode='indeterminate', 
            length=100
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.pack_forget()

        # Initialize UI components
        self.setup_ui_components()
        
        # Apply theme
        self.apply_theme()

    def setup_ui_components(self):
        """Setup all UI components in the correct order."""
        # Initialize header with logo and title
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo.png")
            if os.path.exists(logo_path):
                logo = ImageTk.PhotoImage(Image.open(logo_path).resize((40, 40), Image.LANCZOS))
                logo_label = ttk.Label(header_frame, image=logo)
                logo_label.image = logo
                logo_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        self.header_label = ttk.Label(
            header_frame, 
            text="Fitness Tracker Pro",
            font=("Helvetica", 24, "bold"),
            foreground=self.accent_colors["primary"]
        )
        self.header_label.pack(side=tk.LEFT, padx=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs with modern styling
        self.dashboard_tab = ttk.Frame(self.notebook, padding=10)
        self.session_tab = ttk.Frame(self.notebook, padding=10)
        self.stats_tab = ttk.Frame(self.notebook, padding=10)
        self.settings_tab = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.session_tab, text="Session")
        self.notebook.add(self.stats_tab, text="Statistics")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Initialize details_text with modern styling
        self.details_text = tk.Text(
            self.session_tab,
            height=15,
            width=70,
            state=tk.DISABLED,
            font=("Helvetica", 10),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        
        # Now setup each tab
        self.setup_dashboard()
        self.setup_session_tab()
        self.setup_stats_tab()
        self.setup_settings_tab()
        
        # Menu bar with modern styling
        self.create_menu_bar()
        
        # Set window size and center it
        width = 1200
        height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # Bind events
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.window_width = width
        self.window_height = height
        self.root.bind("<Configure>", self.on_window_resize)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Session", command=self.start_session, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data, accelerator="Ctrl+E")
        file_menu.add_command(label="Import Data", command=self.import_data, accelerator="Ctrl+I")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app, accelerator="Alt+F4")
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_theme, accelerator="Ctrl+D")
        view_menu.add_command(label="Refresh Dashboard", command=self.setup_dashboard, accelerator="F5")
        view_menu.add_command(label="Refresh Stats", command=self.refresh_stats, accelerator="Ctrl+R")
        
        # Workout menu
        workout_menu = tk.Menu(menu_bar, tearoff=0)
        workout_menu.add_command(label="Start Session", command=self.start_session)
        workout_menu.add_command(label="Add Workout", command=self.add_workout)
        workout_menu.add_command(label="End Session", command=self.end_session)
        workout_menu.add_separator()
        workout_menu.add_command(label="Set Workout Goal", command=self.add_workout_goal)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="User Guide", command=lambda: webbrowser.open("https://www.example.com/fitness-guide"))
        help_menu.add_command(label="About", command=self.show_about)
        
        # Add menus to menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        menu_bar.add_cascade(label="Workout", menu=workout_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.start_session())
        self.root.bind('<Control-e>', lambda e: self.export_data())
        self.root.bind('<Control-i>', lambda e: self.import_data())
        self.root.bind('<Control-d>', lambda e: self.toggle_theme())
        self.root.bind('<Control-r>', lambda e: self.refresh_stats())
        self.root.bind('<F5>', lambda e: self.setup_dashboard())

    def quit_app(self):
        """Close the application with confirmation."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def show_about(self):
        """Show about dialog with app information."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Fitness Tracker")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        # Center the window
        about_window.geometry("+{}+{}".format(
            self.root.winfo_x() + (self.root.winfo_width() // 2) - 200,
            self.root.winfo_y() + (self.root.winfo_height() // 2) - 150))
        
        # Logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo.png")
            if os.path.exists(logo_path):
                logo = ImageTk.PhotoImage(Image.open(logo_path).resize((100, 100), Image.LANCZOS))
                logo_label = ttk.Label(about_window, image=logo)
                logo_label.image = logo  # Keep reference
                logo_label.pack(pady=10)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # App info
        ttk.Label(about_window, text="Fitness Tracker Pro", 
                 font=("Helvetica", 16, "bold")).pack(pady=5)
        ttk.Label(about_window, text="Version 1.0").pack()
        ttk.Label(about_window, text="Developed by Raghul Kannan").pack(pady=10)
        ttk.Label(about_window, text="© 2024 All Rights Reserved").pack()
        
        # Close button
        ttk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=20)

    def on_window_resize(self, event):
        """Handle window resize events for responsive UI."""
        # Only process if this is a root window event
        if event.widget == self.root:
            # Check if the size actually changed
            if self.window_width != event.width or self.window_height != event.height:
                self.window_width = event.width
                self.window_height = event.height
                
                # Update UI elements as needed
                # For example, adjust column widths in treeview, etc.
                if hasattr(self, 'history_tree'):
                    self.history_tree.column('workouts', width=max(200, event.width - 500))

    def setup_dashboard(self):
        """Set up the dashboard with informative widgets."""
        # Clear existing widgets first
        for widget in self.dashboard_tab.winfo_children():
            widget.destroy()
            
        # Main container for dashboard
        dashboard_container = ttk.Frame(self.dashboard_tab)
        dashboard_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome banner with animation effect
        welcome_frame = ttk.Frame(dashboard_container)
        welcome_frame.pack(fill=tk.X, pady=10)
        
        # A more prominent header
        header_style = "Dashboard.TLabel" if self.theme == "light" else "DashboardDark.TLabel"
        welcome_title = ttk.Label(
            welcome_frame, 
            text="Welcome to Fitness Tracker Pro", 
            font=("Helvetica", 24, "bold"),
            style=header_style
        )
        welcome_title.pack(anchor=tk.W)
        
        welcome_msg = ttk.Label(
            welcome_frame, 
            text="Track your workouts, monitor your progress, and achieve your fitness goals.",
            wraplength=800
        )
        welcome_msg.pack(anchor=tk.W, pady=5)
        
        # Quick stats and actions in three columns
        stats_frame = ttk.Frame(dashboard_container)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Column 1: Quick Actions
        actions_frame = ttk.LabelFrame(stats_frame, text="Quick Actions")
        actions_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Enhanced buttons with icons (would need icon files)
        ttk.Button(
            actions_frame, 
            text="Start New Session", 
            command=lambda: [self.notebook.select(1), self.start_session()]
        ).pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(
            actions_frame, 
            text="View Statistics", 
            command=lambda: self.notebook.select(2)
        ).pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(
            actions_frame, 
            text="Add Quick Workout", 
            command=self.add_workout
        ).pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(
            actions_frame, 
            text="Set New Goal", 
            command=self.add_workout_goal
        ).pack(fill=tk.X, pady=5, padx=10)
        
        # Column 2: Recent Activity with more detail
        recent_frame = ttk.LabelFrame(stats_frame, text="Recent Activity")
        recent_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Get recent sessions
        sessions = get_sessions()
        if sessions:
            # Create a mini treeview for recent sessions
            columns = ('date', 'duration', 'calories')
            recent_tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=5)
            
            # Define headings
            recent_tree.heading('date', text='Date & Time')
            recent_tree.heading('duration', text='Duration')
            recent_tree.heading('calories', text='Calories')
            
            # Configure columns
            recent_tree.column('date', width=150)
            recent_tree.column('duration', width=80)
            recent_tree.column('calories', width=80)
            
            # Add data
            for session in reversed(sessions[-5:]):  # Show last 5 sessions
                session_id = session[0]
                start_time = session[1]
                end_time = session[2] if len(session) > 2 else None
                duration = session[3] if len(session) > 3 else None
                calories = session[4] if len(session) > 4 else None
                
                duration_str = f"{duration:.1f} min" if duration else "Active"
                calories_str = f"{calories:.1f}" if calories else "-"
                
                recent_tree.insert('', tk.END, values=(start_time, duration_str, calories_str))
                
            recent_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Add view all button
            ttk.Button(
                recent_frame, 
                text="View All History", 
                command=lambda: [self.notebook.select(2), self.stats_notebook.select(2)]
            ).pack(fill=tk.X, padx=5, pady=5)
        else:
            ttk.Label(recent_frame, text="No recent activity").pack(pady=10, padx=10)
        
        # Column 3: Summary Stats with graphical elements
        summary_frame = ttk.LabelFrame(stats_frame, text="Workout Summary")
        summary_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Calculate total stats
        total_sessions = len(sessions) if sessions else 0
        total_duration = 0
        total_calories = 0
        
        for session in sessions:
            duration = session[3] if len(session) > 3 else None
            calories = session[4] if len(session) > 4 else None
            if duration:
                total_duration += duration
            if calories:
                total_calories += calories
        
        # Display stats with progress indicators
        stats_container = ttk.Frame(summary_frame)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sessions count
        ttk.Label(stats_container, text=f"Total Sessions:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_container, text=f"{total_sessions}", font=("Helvetica", 12, "bold")).grid(row=0, column=1, sticky=tk.E, pady=2)
        
        # Total duration with bar visualization
        ttk.Label(stats_container, text=f"Total Duration:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_container, text=f"{total_duration:.1f} min", font=("Helvetica", 12, "bold")).grid(row=1, column=1, sticky=tk.E, pady=2)
        
        # Calories with visualization
        ttk.Label(stats_container, text=f"Total Calories:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_container, text=f"{total_calories:.1f}", font=("Helvetica", 12, "bold")).grid(row=2, column=1, sticky=tk.E, pady=2)
        
        # Target section
        ttk.Separator(summary_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Get user profile for BMR if available
        profile = get_user_profile()
        if profile and profile[6]:  # If BMR is available
            bmr = profile[6]
            cal_target = bmr * 0.2  # Example: 20% of BMR as daily exercise target
            
            # Calculate progress percentage
            progress_pct = min(100, int((total_calories / cal_target) * 100)) if cal_target > 0 else 0
            
            ttk.Label(summary_frame, text=f"Daily Target: {cal_target:.1f} calories").pack(anchor=tk.W, padx=5)
            progress = ttk.Progressbar(summary_frame, value=progress_pct, maximum=100, length=200)
            progress.pack(pady=5, padx=5, fill=tk.X)
            ttk.Label(summary_frame, text=f"{progress_pct}% of daily target").pack(anchor=tk.E, padx=5)
        
        # Configure grid weights for responsive layout
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # Row 2: Achievements and Goals
        achievements_frame = ttk.Frame(dashboard_container)
        achievements_frame.pack(fill=tk.X, pady=10)
        
        # Left: Recent achievements
        recent_achievements = ttk.LabelFrame(achievements_frame, text="Recent Achievements")
        recent_achievements.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Example achievements (in a real app, these would be fetched from the database)
        achievements = [
            ("First Workout", "Completed your first workout session"),
            ("Consistency", "Worked out 3 days in a row"),
            ("Calorie Burner", "Burned over 1000 total calories")
        ]
        
        for i, (title, desc) in enumerate(achievements):
            achievement_frame = ttk.Frame(recent_achievements)
            achievement_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(
                achievement_frame, 
                text="🏆", 
                font=("Helvetica", 16)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(
                achievement_frame,
                text=title,
                font=("Helvetica", 10, "bold")
            ).pack(side=tk.LEFT, anchor=tk.W)
        
        # Right: Current goals
        current_goals = ttk.LabelFrame(achievements_frame, text="Current Goals")
        current_goals.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Example goals (would normally come from database)
        goals = [
            ("Weekly", "Complete 4 workouts this week", 75),
            ("Monthly", "Burn 5000 calories in a month", 30),
        ]
        
        for goal_type, goal_desc, progress in goals:
            goal_frame = ttk.Frame(current_goals)
            goal_frame.pack(fill=tk.X, pady=5, padx=5)
            
            ttk.Label(goal_frame, text=goal_type, width=10).pack(side=tk.LEFT)
            ttk.Label(goal_frame, text=goal_desc).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            progress_frame = ttk.Frame(goal_frame)
            progress_frame.pack(side=tk.RIGHT, padx=5)
            
            progress_bar = ttk.Progressbar(progress_frame, value=progress, length=100)
            progress_bar.pack(side=tk.LEFT)
            ttk.Label(progress_frame, text=f"{progress}%").pack(side=tk.RIGHT)
        
        # Update status
        self.status_bar.config(text="Dashboard refreshed")

    def on_tab_change(self, event):
        """Handle tab changes to update content as needed."""
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if tab_name == "Dashboard":
            self.setup_dashboard()  # Refresh dashboard on visit
        elif tab_name == "Statistics":
            self.refresh_stats()
        elif tab_name == "Session":
            self.update_session_status()  # Update session status display
    def update_session_status(self):
        """Update the session status information."""
        if hasattr(self, 'session_status_var'):
            if self.session.is_active:
                elapsed = datetime.now() - self.session.start_time
                elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
                self.session_status_var.set(f"Session active - started at {self.session.start_time.strftime('%H:%M:%S')} (Elapsed: {elapsed_str})")
            else:
                self.session_status_var.set("No active session")

    def refresh_stats(self):
        """Refresh all statistics data."""
        self.status_bar.config(text="Refreshing statistics...")
        
        # Start progress indicator
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.start(10)
        
        # Use a thread to prevent UI freezing during refresh
        def refresh_task():
            try:
                # Update summary stats if tab exists
                if hasattr(self, 'summary_content_frame'):
                    current_period = getattr(self, 'current_period', "All Time")
                    self.update_summary_stats(current_period)
                
                # Reload history
                if hasattr(self, 'history_tree'):
                    self.load_history()
                
                # Call finish_refresh on success
                self.root.after(0, self.finish_refresh)
            except Exception as e:
                # Only reference e inside the exception handler
                error_msg = f"Error refreshing stats: {e}"
                self.root.after(0, lambda: self.handle_error(error_msg))
        
        threading.Thread(target=refresh_task, daemon=True).start()

    def finish_refresh(self):
        """Complete the refresh operation."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_bar.config(text="Statistics refreshed")

    def handle_error(self, message):
        """Display error messages and reset progress indicators."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_bar.config(text="Error occurred")
        messagebox.showerror("Error", message)

    def export_data(self):
        """Export fitness data to a file."""
        # Optimize export by using a separate thread
        self.status_bar.config(text="Preparing export...")
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.start(10)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Fitness Data"
        )
        
        if not file_path:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.status_bar.config(text="Export cancelled")
            return
            
        def export_task():
            try:
                # Get all data
                sessions = get_sessions()
                data = []
                
                for session in sessions:
                    session_id = session[0]
                    start_time = session[1]
                    end_time = session[2] if len(session) > 2 else None
                    duration = session[3] if len(session) > 3 else None
                    calories = session[4] if len(session) > 4 else None
                    workouts = get_session_details(session_id)
                    
                    session_data = {
                        "id": session_id,
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration": duration,
                        "calories": calories,
                        "workouts": []
                    }
                    
                    for workout in workouts:
                        workout_type, duration, calories = workout[:3]
                        intensity = workout[3] if len(workout) > 3 else "Medium"
                        notes = workout[4] if len(workout) > 4 else ""
                        
                        workout_data = {
                            "type": workout_type,
                            "duration": duration,
                            "calories": calories,
                            "intensity": intensity,
                            "notes": notes
                        }
                        session_data["workouts"].append(workout_data)
                    
                    data.append(session_data)
                
                # Determine export format based on file extension
                if file_path.lower().endswith('.csv'):
                    self.export_as_csv(data, file_path)
                else:  # Default to JSON
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)
                
                self.root.after(0, lambda: self.finish_export(file_path))
            except Exception as e:
                self.root.after(0, lambda: self.handle_error(f"Error exporting data: {e}"))
        
        threading.Thread(target=export_task, daemon=True).start()

    def export_as_csv(self, data, file_path):
        """Export data in CSV format."""
        import csv
        
        # First write sessions data
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(["Session ID", "Start Time", "End Time", "Duration", "Calories"])
            
            # Write session rows
            for session in data:
                writer.writerow([
                    session["id"],
                    session["start_time"],
                    session["end_time"] or "",
                    session["duration"] or "",
                    session["calories"] or ""
                ])
            
            # Add a separator
            writer.writerow([])
            writer.writerow(["Workout Data:"])
            
            # Write workout header
            writer.writerow(["Session ID", "Type", "Duration", "Calories", "Intensity", "Notes"])
            
            # Write workout rows
            for session in data:
                session_id = session["id"]
                for workout in session["workouts"]:
                    writer.writerow([
                        session_id,
                        workout["type"],
                        workout["duration"],
                        workout["calories"],
                        workout["intensity"],
                        workout["notes"]
                    ])

    def finish_export(self, file_path):
        """Complete the export process."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_bar.config(text=f"Data exported to {os.path.basename(file_path)}")
        messagebox.showinfo("Export Successful", f"Data exported to {file_path}")

    def import_data(self):
        """Import fitness data from a file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Fitness Data"
        )
        
        if not file_path:
            return
            
        self.status_bar.config(text="Importing data...")
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.start(10)
        
        def import_task():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Confirm import
                result = messagebox.askyesno(
                    "Import Confirmation", 
                    f"Import {len(data)} sessions? This may duplicate data if sessions already exist."
                )
                
                if not result:
                    self.root.after(0, lambda: self.status_bar.config(text="Import cancelled"))
                    self.root.after(0, lambda: self.progress_bar.stop())
                    self.root.after(0, lambda: self.progress_bar.pack_forget())
                    return
                
                # Create a connection to the database
                conn = sqlite3.connect('fitness_tracker.db')
                cursor = conn.cursor()
                
                try:
                    # Start transaction
                    cursor.execute("BEGIN TRANSACTION")
                    
                    # Import each session
                    for session_data in data:
                        # Add session
                        cursor.execute('''
                            INSERT INTO sessions (start_time, end_time, total_duration, total_calories)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            session_data["start_time"],
                            session_data["end_time"],
                            session_data["duration"],
                            session_data["calories"]
                        ))
                        
                        session_id = cursor.lastrowid
                        
                        # Import workouts
                        for workout_data in session_data["workouts"]:
                            intensity = workout_data.get("intensity", "Medium")
                            notes = workout_data.get("notes", "")
                            
                            cursor.execute('''
                                INSERT INTO workouts (workout_type, duration, calories_burned, session_id, date, notes, intensity)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                workout_data["type"],
                                workout_data["duration"],
                                workout_data["calories"],
                                session_id,
                                session_data["start_time"].split()[0],  # Extract just the date part
                                notes,
                                intensity
                            ))
                    
                    # Commit transaction
                    conn.commit()
                    
                    self.root.after(0, lambda: self.finish_import(len(data)))
                    
                except Exception as e:
                    # Roll back on any error
                    conn.rollback()
                    raise e
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                self.root.after(0, lambda: self.handle_error(f"Error importing data: {e}"))
        
        threading.Thread(target=import_task, daemon=True).start()

    def finish_import(self, count):
        """Complete the import process."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_bar.config(text=f"Imported {count} sessions")
        messagebox.showinfo("Import Successful", f"Imported {count} sessions")

    def setup_session_tab(self):
        """Set up the session management tab."""
        # Header
        header_frame = ttk.Frame(self.session_tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        header_label = ttk.Label(header_frame, text="Session Management", font=("Helvetica", 16, "bold"))
        header_label.pack(side=tk.LEFT)
        
        # Session controls
        controls_frame = ttk.Frame(self.session_tab)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_button = ttk.Button(controls_frame, text="Start Session", command=self.start_session)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.add_workout_button = ttk.Button(controls_frame, text="Add Workout", command=self.add_workout)
        self.add_workout_button.pack(side=tk.LEFT, padx=5)
        
        self.end_button = ttk.Button(controls_frame, text="End Session", command=self.end_session)
        self.end_button.pack(side=tk.LEFT, padx=5)
        
        # Session status
        status_frame = ttk.LabelFrame(self.session_tab, text="Session Status")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.session_status_var = tk.StringVar(value="No active session")
        self.session_status_label = ttk.Label(status_frame, textvariable=self.session_status_var)
        self.session_status_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Session details
        details_frame = ttk.LabelFrame(self.session_tab, text="Session Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.details_text = tk.Text(details_frame, height=15, width=70, state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar for details text
        details_scrollbar = ttk.Scrollbar(self.details_text)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=details_scrollbar.set)
        details_scrollbar.config(command=self.details_text.yview)
    
    def setup_stats_tab(self):
        """Set up the statistics tab."""
        # Header
        header_frame = ttk.Frame(self.stats_tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        header_label = ttk.Label(header_frame, text="Workout Statistics", font=("Helvetica", 16, "bold"))
        header_label.pack(side=tk.LEFT)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.refresh_stats)
        refresh_button.pack(side=tk.RIGHT)
        
        # Notebook for different stat views
        self.stats_notebook = ttk.Notebook(self.stats_tab)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Summary tab
        summary_tab = ttk.Frame(self.stats_notebook)
        
        # Charts tab
        charts_tab = ttk.Frame(self.stats_notebook)
        
        # History tab
        history_tab = ttk.Frame(self.stats_notebook)
        
        self.stats_notebook.add(summary_tab, text="Summary")
        self.stats_notebook.add(charts_tab, text="Charts")
        self.stats_notebook.add(history_tab, text="History")
        
        # Summary tab content
        self.setup_summary_tab(summary_tab)
        
        # Charts tab content
        self.setup_charts_tab(charts_tab)
        
        # History tab content
        self.setup_history_tab(history_tab)
    
    def setup_summary_tab(self, parent):
        """Set up the summary statistics tab."""
        # Create a container frame
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        # Period selection
        period_frame = ttk.Frame(summary_frame)
        period_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(period_frame, text="Time Period:").pack(side=tk.LEFT, padx=5)
        
        period_var = tk.StringVar(value="All Time")
        period_combo = ttk.Combobox(
            period_frame, 
            textvariable=period_var,
            values=["This Week", "This Month", "This Year", "All Time"],
            state="readonly",
            width=15
        )
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", lambda e: self.update_summary_stats(period_var.get()))
        
        # Create StringVars for stats
        self.total_sessions_var = tk.StringVar(value="0")
        self.total_workouts_var = tk.StringVar(value="0")
        self.total_duration_var = tk.StringVar(value="0.0")
        self.total_calories_var = tk.StringVar(value="0.0")
        self.avg_duration_var = tk.StringVar(value="0.0")
        self.avg_calories_var = tk.StringVar(value="0.0")
        
        # Stats display frame
        stats_frame = ttk.LabelFrame(summary_frame, text="Summary Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create grid for stats
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Row 1: Total Sessions & Total Workouts
        ttk.Label(stats_grid, text="Total Sessions:", font=("Helvetica", 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Label(stats_grid, textvariable=self.total_sessions_var, font=("Helvetica", 11, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Total Workouts:", font=("Helvetica", 11)).grid(row=0, column=2, sticky=tk.W, pady=10, padx=(30, 0))
        ttk.Label(stats_grid, textvariable=self.total_workouts_var, font=("Helvetica", 11, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Row 2: Total Duration & Total Calories
        ttk.Label(stats_grid, text="Total Duration:", font=("Helvetica", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        ttk.Label(stats_grid, textvariable=self.total_duration_var, font=("Helvetica", 11, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, text="min", font=("Helvetica", 10)).grid(row=1, column=1, sticky=tk.E, padx=5)
        
        ttk.Label(stats_grid, text="Total Calories:", font=("Helvetica", 11)).grid(row=1, column=2, sticky=tk.W, pady=10, padx=(30, 0))
        ttk.Label(stats_grid, textvariable=self.total_calories_var, font=("Helvetica", 11, "bold")).grid(row=1, column=3, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, text="kcal", font=("Helvetica", 10)).grid(row=1, column=3, sticky=tk.E, padx=5)
        
        # Row 3: Average Duration & Average Calories
        ttk.Label(stats_grid, text="Avg Duration:", font=("Helvetica", 11)).grid(row=2, column=0, sticky=tk.W, pady=10)
        ttk.Label(stats_grid, textvariable=self.avg_duration_var, font=("Helvetica", 11, "bold")).grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, text="min", font=("Helvetica", 10)).grid(row=2, column=1, sticky=tk.E, padx=5)
        
        ttk.Label(stats_grid, text="Avg Calories:", font=("Helvetica", 11)).grid(row=2, column=2, sticky=tk.W, pady=10, padx=(30, 0))
        ttk.Label(stats_grid, textvariable=self.avg_calories_var, font=("Helvetica", 11, "bold")).grid(row=2, column=3, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, text="kcal", font=("Helvetica", 10)).grid(row=2, column=3, sticky=tk.E, padx=5)
        
        # Add some padding to columns
        for i in range(4):
            stats_grid.columnconfigure(i, pad=10)
        
        # Load initial stats
        self.update_summary_stats("All Time")
        
        return summary_frame
    
    def update_summary_stats(self, period):
        """Update the summary statistics based on the selected time period."""
        try:
            # Clear existing values
            self.total_sessions_var.set("0")
            self.total_workouts_var.set("0")
            self.total_duration_var.set("0.0")
            self.total_calories_var.set("0.0")
            self.avg_duration_var.set("0.0")
            self.avg_calories_var.set("0.0")
            
            # Get date range based on period
            end_date = datetime.now()
            start_date = None
            
            if period == "This Week":
                start_date = end_date - timedelta(days=7)
            elif period == "This Month":
                start_date = end_date - timedelta(days=30)
            elif period == "This Year":
                start_date = end_date - timedelta(days=365)
            
            # Convert dates to string format for database query
            start_date_str = start_date.strftime('%Y-%m-%d') if start_date else None
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Get sessions
            sessions = get_sessions(start_date_str, end_date_str)
            
            if not sessions:
                return
            
            # Initialize counters
            total_sessions = len(sessions)
            total_workouts = 0
            total_duration = 0
            total_calories = 0
            
            # Process each session
            for session in sessions:
                session_id = session[0]
                
                try:
                    # Get session duration and calories from the session record
                    session_duration = session[3] or 0
                    session_calories = session[4] or 0
                    
                    # Add to totals
                    total_duration += session_duration
                    total_calories += session_calories
                    
                    # Get workouts for this session
                    workouts = get_session_details(session_id)
                    total_workouts += len(workouts)
                except Exception as e:
                    print(f"Error processing session {session_id}: {e}")
                    continue
            
            # Calculate averages
            avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
            avg_calories = total_calories / total_sessions if total_sessions > 0 else 0
            
            # Update UI
            self.total_sessions_var.set(str(total_sessions))
            self.total_workouts_var.set(str(total_workouts))
            self.total_duration_var.set(f"{total_duration:.1f}")
            self.total_calories_var.set(f"{total_calories:.1f}")
            self.avg_duration_var.set(f"{avg_duration:.1f}")
            self.avg_calories_var.set(f"{avg_calories:.1f}")

        except Exception as e:
            self.handle_error(f"Error updating statistics: {e}")
            # Log error for debugging
            print(f"Error updating summary stats: {e}")

    def setup_charts_tab(self, parent):
        """Set up charts tab with visualization of workout data."""
        # Controls for chart selection
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        
        chart_types = ["Calories by Workout Type", "Duration by Workout Type", 
                      "Workout Frequency", "Progress Over Time"]
        chart_var = tk.StringVar(value=chart_types[0])
        chart_combo = ttk.Combobox(controls_frame, textvariable=chart_var, values=chart_types, state="readonly")
        chart_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="Time Period:").pack(side=tk.LEFT, padx=5)
        
        period_types = ["Last 7 Days", "Last 30 Days", "This Month", "This Year", "All Time"]
        period_var = tk.StringVar(value=period_types[1])
        period_combo = ttk.Combobox(controls_frame, textvariable=period_var, values=period_types, state="readonly")
        period_combo.pack(side=tk.LEFT, padx=5)
        
        update_button = ttk.Button(controls_frame, text="Update Chart", 
                                  command=lambda: self.update_chart(chart_var.get(), period_var.get(), chart_frame))
        update_button.pack(side=tk.LEFT, padx=5)
        
        # Frame for displaying charts
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial chart
        self.update_chart(chart_types[0], period_types[1], chart_frame)

    def update_chart(self, chart_type, period, container):
        """Update the chart based on selection."""
        # Clear existing chart
        for widget in container.winfo_children():
            widget.destroy()
        
        # Get date range based on period
        end_date = datetime.now()
        if period == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif period == "This Month":
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == "This Year":
            start_date = datetime(end_date.year, 1, 1)
        else:  # All Time
            start_date = None
        
        # Fetch data
        if start_date:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            stats = get_stats_by_workout_type(start_str, end_str)
        else:
            stats = get_stats_by_workout_type()
        
        # Adjust for empty dataset
        if not stats:
            empty_label = ttk.Label(container, text="No data available for the selected period", 
                                   font=("Helvetica", 14))
            empty_label.pack(expand=True)
            return
        
        # Create figure and axis
        fig = plt.Figure(figsize=(10, 6), dpi=100, tight_layout=True)
        ax = fig.add_subplot(111)
        
        # Get data for chart
        workout_types = [stat[0] for stat in stats]
        
        if chart_type == "Calories by Workout Type":
            values = [stat[4] for stat in stats]  # total_calories
            title = "Calories Burned by Workout Type"
            ylabel = "Calories"
            
            # Create bar chart
            bars = ax.bar(workout_types, values)
            
            # Customize
            ax.set_title(title, fontsize=14)
            ax.set_xlabel("Workout Type", fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom', fontsize=10)
                        
        elif chart_type == "Duration by Workout Type":
            values = [stat[2] for stat in stats]  # total_duration
            title = "Duration by Workout Type"
            ylabel = "Duration (minutes)"
            
            # Create bar chart
            bars = ax.bar(workout_types, values)
            
            # Customize
            ax.set_title(title, fontsize=14)
            ax.set_xlabel("Workout Type", fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom', fontsize=10)
                        
        elif chart_type == "Workout Frequency":
            values = [stat[1] for stat in stats]  # count
            title = "Workout Frequency by Type"
            ylabel = "Count"
            
            # Create pie chart
            ax.pie(values, labels=workout_types, autopct='%1.1f%%',
                   startangle=90, shadow=True)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title(title, fontsize=14)
            
        elif chart_type == "Progress Over Time":
            # For this chart, we need different data - workouts over time
            if start_date:
                ax.text(0.5, 0.5, "Progress Over Time chart requires\ndata analysis over multiple sessions",
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12)
            else:
                ax.text(0.5, 0.5, "Select a specific date range for this chart",
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12)
        
        # Create canvas and add to container
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_history_tab(self, parent):
        """Set up the history tab with session records."""
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        
        filter_entry = ttk.Entry(controls_frame, width=20)
        filter_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Search", 
                  command=lambda: self.filter_history(filter_entry.get())).pack(side=tk.LEFT, padx=5)
        
        # History table
        columns = ('session_id', 'date', 'duration', 'calories', 'workouts')
        self.history_tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Define headings
        self.history_tree.heading('session_id', text='ID')
        self.history_tree.heading('date', text='Date')
        self.history_tree.heading('duration', text='Duration (min)')
        self.history_tree.heading('calories', text='Calories')
        self.history_tree.heading('workouts', text='Workouts')
        
        # Define columns
        self.history_tree.column('session_id', width=50)
        self.history_tree.column('date', width=150)
        self.history_tree.column('duration', width=100)
        self.history_tree.column('calories', width=100)
        self.history_tree.column('workouts', width=400)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.history_tree.bind("<Double-1>", self.view_session_details)
        
        # Load history
        self.load_history()
    
    def load_history(self):
        """Load session history into the table."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get all sessions
        sessions = get_sessions()
        
        for session in sessions:
            session_id = session[0]
            start_time = session[1]
            end_time = session[2] if len(session) > 2 else None
            duration = session[3] if len(session) > 3 else None
            calories = session[4] if len(session) > 4 else None
            
            # Get workouts for this session
            workouts = get_session_details(session_id)
            workout_types = [w[0] for w in workouts]
            workout_summary = ", ".join(workout_types) if workout_types else "No workouts"
            
            # Format values
            duration_str = f"{duration:.1f}" if duration else "-"
            calories_str = f"{calories:.1f}" if calories else "-"
            
            self.history_tree.insert('', tk.END, values=(session_id, start_time, duration_str, calories_str, workout_summary))
    
    def filter_history(self, filter_text):
        """Filter session history based on the provided text."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get all sessions
        sessions = get_sessions()
        
        for session in sessions:
            session_id = session[0]
            start_time = session[1]
            end_time = session[2] if len(session) > 2 else None
            duration = session[3] if len(session) > 3 else None
            calories = session[4] if len(session) > 4 else None
            
            # Get workouts for this session
            workouts = get_session_details(session_id)
            workout_types = [w[0] for w in workouts]
            workout_summary = ", ".join(workout_types) if workout_types else "No workouts"
            
            # Format values
            duration_str = f"{duration:.1f}" if duration else "-"
            calories_str = f"{calories:.1f}" if calories else "-"
            
            # Apply filter
            filter_text = filter_text.lower()
            if (filter_text in str(session_id).lower() or
                filter_text in start_time.lower() or
                (end_time and filter_text in end_time.lower()) or
                filter_text in workout_summary.lower()):
                self.history_tree.insert('', tk.END, values=(session_id, start_time, duration_str, calories_str, workout_summary))
    
    def view_session_details(self, event):
        """View details of the selected session."""
        # Get selected item
        selected_item = self.history_tree.selection()[0]
        session_id = self.history_tree.item(selected_item, 'values')[0]
        
        # Create a new window to display session details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Session {session_id} Details")
        details_window.geometry("600x400")
        
        # Get session and workout details
        sessions = get_sessions()
        session = next((s for s in sessions if s[0] == int(session_id)), None)
        
        if not session:
            ttk.Label(details_window, text="Session not found").pack(pady=20)
            return
        
        start_time = session[1]
        end_time = session[2] if len(session) > 2 else None
        duration = session[3] if len(session) > 3 else None
        calories = session[4] if len(session) > 4 else None
        
        # Display session details
        ttk.Label(details_window, text=f"Session ID: {session_id}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_window, text=f"Start Time: {start_time}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_window, text=f"End Time: {end_time if end_time else 'Ongoing'}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_window, text=f"Duration: {duration:.1f} minutes" if duration else "Duration: -").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_window, text=f"Calories: {calories:.1f}" if calories else "Calories: -").pack(anchor=tk.W, padx=10, pady=5)
        
        # Display workout details
        workouts = get_session_details(session_id)
        if workouts:
            ttk.Label(details_window, text="Workouts:").pack(anchor=tk.W, padx=10, pady=5)
            for workout in workouts:
                workout_type, duration, calories = workout
                ttk.Label(details_window, text=f"{workout_type} - {duration:.1f} min, {calories:.1f} cal").pack(anchor=tk.W, padx=20, pady=2)
        else:
            ttk.Label(details_window, text="No workouts recorded").pack(anchor=tk.W, padx=10, pady=5)

    def setup_settings_tab(self):
        """Set up the settings tab with user profile and preferences."""
        # Header
        header_frame = ttk.Frame(self.settings_tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        header_label = ttk.Label(header_frame, text="Settings & Profile", font=("Helvetica", 16, "bold"))
        header_label.pack(side=tk.LEFT)
        
        # Create a notebook for different settings sections
        settings_notebook = ttk.Notebook(self.settings_tab)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Profile tab
        profile_tab = ttk.Frame(settings_notebook)
        
        # Appearance tab
        appearance_tab = ttk.Frame(settings_notebook)
        
        # Preferences tab
        preferences_tab = ttk.Frame(settings_notebook)
        
        # Add tabs to the notebook
        settings_notebook.add(profile_tab, text="User Profile")
        settings_notebook.add(appearance_tab, text="Appearance")
        settings_notebook.add(preferences_tab, text="Preferences")
        
        # Setup each settings tab
        self.setup_profile_tab(profile_tab)
        self.setup_appearance_tab(appearance_tab)
        self.setup_preferences_tab(preferences_tab)

    def setup_profile_tab(self, parent):
        """Set up the user profile settings tab."""
        # User profile form
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Get existing profile if available
        profile = get_user_profile()
        
        # Name field
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=profile[1] if profile else "")
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Age field
        ttk.Label(form_frame, text="Age:").grid(row=1, column=0, sticky=tk.W, pady=5)
        age_var = tk.StringVar(value=str(profile[2]) if profile else "")
        ttk.Entry(form_frame, textvariable=age_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Gender field
        ttk.Label(form_frame, text="Gender:").grid(row=2, column=0, sticky=tk.W, pady=5)
        gender_var = tk.StringVar(value=profile[5] if profile else "")
        gender_combo = ttk.Combobox(form_frame, textvariable=gender_var, values=["Male", "Female", "Other"])
        gender_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        gender_combo.current(0 if not profile else 0 if profile[5] == "Male" else 1 if profile[5] == "Female" else 2)
        
        # Weight field
        ttk.Label(form_frame, text="Weight (kg):").grid(row=3, column=0, sticky=tk.W, pady=5)
        weight_var = tk.StringVar(value=str(profile[3]) if profile else "")
        ttk.Entry(form_frame, textvariable=weight_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Height field
        ttk.Label(form_frame, text="Height (cm):").grid(row=4, column=0, sticky=tk.W, pady=5)
        height_var = tk.StringVar(value=str(profile[4]) if profile else "")
        ttk.Entry(form_frame, textvariable=height_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Activity level field
        ttk.Label(form_frame, text="Activity Level:").grid(row=5, column=0, sticky=tk.W, pady=5)
        activity_var = tk.StringVar(value=profile[6] if profile else "Moderate")
        activity_combo = ttk.Combobox(form_frame, textvariable=activity_var,
                                     values=["Sedentary", "Light", "Moderate", "Active", "Very Active"])
        activity_combo.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # BMR calculation (read-only)
        ttk.Label(form_frame, text="Estimated BMR:").grid(row=6, column=0, sticky=tk.W, pady=5)
        bmr_var = tk.StringVar(value=f"{profile[6]:.1f} calories/day" if profile and profile[6] else "")
        ttk.Entry(form_frame, textvariable=bmr_var, state="readonly", width=20).grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Calculation info
        ttk.Label(form_frame, text="BMR = Basal Metabolic Rate (calories burned at rest)",
                 font=("Helvetica", 8)).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Save button
        def save_profile():
            try:
                name = name_var.get()
                age = int(age_var.get())
                weight = float(weight_var.get())
                height = float(height_var.get())
                gender = gender_var.get()
                activity = activity_var.get()
                
                save_user_profile(name, age, weight, height, gender, activity)
                messagebox.showinfo("Success", "User profile saved successfully!")
                
                # Update BMR display
                profile = get_user_profile()
                if profile and profile[6]:
                    bmr_var.set(f"{profile[6]:.1f} calories/day")
                    
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numeric values for age, weight, and height.")
        
        ttk.Button(form_frame, text="Save Profile", command=save_profile).grid(row=8, column=0, columnspan=2, pady=20)
        
        # Configure grid weights for responsive layout
        form_frame.columnconfigure(1, weight=1)

    def setup_appearance_tab(self, parent):
        """Set up the appearance settings tab."""
        appearance_frame = ttk.Frame(parent)
        appearance_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Theme settings
        theme_frame = ttk.LabelFrame(appearance_frame, text="Theme Settings")
        theme_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(theme_frame, text="Choose Theme:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        # Theme radio buttons
        theme_var = tk.StringVar(value=self.theme)
        ttk.Radiobutton(theme_frame, text="Light Mode", variable=theme_var, value="light",
                      command=lambda: self.apply_theme("light")).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(theme_frame, text="Dark Mode", variable=theme_var, value="dark",
                      command=lambda: self.apply_theme("dark")).grid(row=0, column=2, padx=10)
        
        # Color accent settings
        color_frame = ttk.LabelFrame(appearance_frame, text="Color Accent")
        color_frame.pack(fill=tk.X, pady=10)
        
        colors = [("Blue", "#1e88e5"), ("Green", "#4caf50"), ("Purple", "#9c27b0"), 
                  ("Orange", "#ff9800"), ("Teal", "#009688")]
        
        color_var = tk.StringVar(value="#4caf50")  # Default green
        
        for i, (color_name, color_code) in enumerate(colors):
            ttk.Radiobutton(color_frame, text=color_name, variable=color_var, value=color_code,
                           command=lambda c=color_code: self.apply_accent_color(c)).grid(
                               row=i//3, column=i%3, padx=10, pady=10, sticky=tk.W)
        
        # Font settings
        font_frame = ttk.LabelFrame(appearance_frame, text="Font Settings")
        font_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(font_frame, text="Font Size:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        font_var = tk.StringVar(value="Medium")
        ttk.Combobox(font_frame, textvariable=font_var, values=["Small", "Medium", "Large"],
                    state="readonly").grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Button(font_frame, text="Apply Font", 
                  command=lambda: self.apply_font_size(font_var.get())).grid(
                      row=0, column=2, padx=10, pady=10)

    def setup_preferences_tab(self, parent):
        """Set up the preferences settings tab."""
        preferences_frame = ttk.Frame(parent)
        preferences_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notification settings
        notification_frame = ttk.LabelFrame(preferences_frame, text="Notifications")
        notification_frame.pack(fill=tk.X, pady=10)
        
        # Example checkboxes for notifications
        remind_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Session Reminders", 
                       variable=remind_var).pack(anchor=tk.W, padx=10, pady=5)
        
        goal_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Goal Achievements", 
                       variable=goal_var).pack(anchor=tk.W, padx=10, pady=5)
        
        inactivity_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(notification_frame, text="Inactivity Alerts", 
                        variable=inactivity_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # Data settings
        data_frame = ttk.LabelFrame(preferences_frame, text="Data Management")
        data_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(data_frame, text="Export All Data", 
                  command=self.export_data).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Button(data_frame, text="Import Data", 
                  command=self.import_data).pack(anchor=tk.W, padx=10, pady=5)
        
        backup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(data_frame, text="Auto-backup Data", 
                       variable=backup_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # Reset button
        reset_frame = ttk.Frame(preferences_frame)
        reset_frame.pack(fill=tk.X, pady=20)
        
        def confirm_reset():
            result = messagebox.askyesno("Confirm Reset", 
                                         "Are you sure you want to reset all data?\nThis action cannot be undone.")
            if result:
                # Logic to reset the database would go here
                messagebox.showinfo("Reset Complete", "All data has been reset.")
        
        ttk.Button(reset_frame, text="Reset All Data", 
                  command=confirm_reset).pack(side=tk.RIGHT)

    def apply_theme(self, theme_name=None):
        """Apply the selected theme to the application."""
        if theme_name:
            self.theme = theme_name
        
        style = self.style
        
        if self.theme == "light":
            bg_color = "#FFFFFF"
            fg_color = "#333333"
            selected_bg = self.accent_colors["primary"]
            hover_bg = "#F5F5F5"
            
            style.configure(".", 
                background=bg_color,
                foreground=fg_color,
                fieldbackground=bg_color,
                selectbackground=selected_bg,
                selectforeground="white"
            )
            
            # Configure specific styles
            style.configure("TFrame", background=bg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TButton", 
                background=self.accent_colors["primary"],
                foreground="white",
                padding=(10, 5)
            )
            style.map("TButton",
                background=[("active", self.accent_colors["info"])],
                foreground=[("active", "white")]
            )
            
            style.configure("Success.TButton",
                background=self.accent_colors["success"],
                foreground="white"
            )
            style.map("Success.TButton",
                background=[("active", "#45a049")]
            )
            
            style.configure("Danger.TButton",
                background=self.accent_colors["error"],
                foreground="white"
            )
            style.map("Danger.TButton",
                background=[("active", "#d32f2f")]
            )
            
            style.configure("TNotebook", background=bg_color, tabmargins=[2, 5, 2, 0])
            style.configure("TNotebook.Tab",
                background="#e0e0e0",
                foreground=fg_color,
                padding=[15, 5],
                font=("Helvetica", 10)
            )
            style.map("TNotebook.Tab",
                background=[("selected", selected_bg)],
                foreground=[("selected", "white")]
            )
            
            # Update text widgets
            self.details_text.configure(
                background="white",
                foreground=fg_color,
                font=("Helvetica", 10),
                selectbackground=selected_bg,
                selectforeground="white",
                insertbackground=fg_color
            )
            
        else:  # Dark theme
            bg_color = "#333333"
            fg_color = "#FFFFFF"
            selected_bg = self.accent_colors["primary"]
            hover_bg = "#424242"
            
            style.configure(".", 
                background=bg_color,
                foreground=fg_color,
                fieldbackground=bg_color,
                selectbackground=selected_bg,
                selectforeground="white"
            )
            
            # Configure specific styles
            style.configure("TFrame", background=bg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TButton", 
                background=self.accent_colors["primary"],
                foreground="white",
                padding=(10, 5)
            )
            style.map("TButton",
                background=[("active", self.accent_colors["info"])],
                foreground=[("active", "white")]
            )
            
            style.configure("Success.TButton",
                background=self.accent_colors["success"],
                foreground="white"
            )
            style.map("Success.TButton",
                background=[("active", "#45a049")]
            )
            
            style.configure("Danger.TButton",
                background=self.accent_colors["error"],
                foreground="white"
            )
            style.map("Danger.TButton",
                background=[("active", "#d32f2f")]
            )
            
            style.configure("TNotebook", background=bg_color, tabmargins=[2, 5, 2, 0])
            style.configure("TNotebook.Tab",
                background="#424242",
                foreground=fg_color,
                padding=[15, 5],
                font=("Helvetica", 10)
            )
            style.map("TNotebook.Tab",
                background=[("selected", selected_bg)],
                foreground=[("selected", "white")]
            )
            
            # Update text widgets
            self.details_text.configure(
                background="#424242",
                foreground=fg_color,
                font=("Helvetica", 10),
                selectbackground=selected_bg,
                selectforeground="white",
                insertbackground=fg_color
            )

    def apply_accent_color(self, color_code):
        """Apply the selected accent color to UI elements."""
        style = self.style
        style.configure("TButton", foreground=color_code)
        style.configure("TNotebook.Tab", foreground=[("selected", color_code)])
        self.header_label.config(background=color_code)

    def apply_font_size(self, size):
        """Change the application font size."""
        sizes = {"Small": 9, "Medium": 11, "Large": 14}
        font_size = sizes.get(size, 11)
        
        style = self.style
        style.configure("TLabel", font=("Helvetica", font_size))
        style.configure("TButton", font=("Helvetica", font_size))
        style.configure("TNotebook.Tab", font=("Helvetica", font_size))

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        new_theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(new_theme)

    def add_workout(self):
        """Add a workout to the current session."""
        if not self.session.is_active:
            messagebox.showerror("No Active Session", "Please start a session before adding workouts.")
            return
        
        # Create a dialog for adding a workout
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Workout")
        dialog.geometry("400x350")
        dialog.transient(self.root)  # Set as transient to main window
        dialog.grab_set()  # Make it modal
        
        # Center the dialog
        dialog.geometry("+{}+{}".format(
            self.root.winfo_x() + (self.root.winfo_width() // 2) - 200,
            self.root.winfo_y() + (self.root.winfo_height() // 2) - 150))
        
        # Create form fields
        form_frame = ttk.Frame(dialog, padding="20 20 20 20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Workout type
        ttk.Label(form_frame, text="Workout Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        workout_types = ["Running", "Walking", "Cycling", "Swimming", "Weight Training", "Yoga", "HIIT", "Other"]
        workout_var = tk.StringVar(value=workout_types[0])
        workout_combo = ttk.Combobox(form_frame, textvariable=workout_var, values=workout_types, state="readonly")
        workout_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Duration in minutes
        ttk.Label(form_frame, text="Duration (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        duration_var = tk.StringVar(value="30")
        ttk.Entry(form_frame, textvariable=duration_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Intensity
        ttk.Label(form_frame, text="Intensity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        intensity_var = tk.StringVar(value="Medium")
        ttk.Combobox(form_frame, textvariable=intensity_var, 
                    values=["Low", "Medium", "High"], state="readonly").grid(row=2, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Calories (optional, can be calculated)
        ttk.Label(form_frame, text="Calories (optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
        calories_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=calories_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=4, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(form_frame, height=4, width=30)
        notes_text.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Calculate calories based on workout type and duration
        def estimate_calories():
            try:
                workout_type = workout_var.get()
                duration = float(duration_var.get())
                intensity = intensity_var.get()
                
                # Rough calories estimation based on workout type and intensity
                # Values are approximate calories burned per minute for a 70kg person
                calories_per_min = {
                    "Running": {"Low": 8, "Medium": 10, "High": 14},
                    "Walking": {"Low": 3, "Medium": 4, "High": 5},
                    "Cycling": {"Low": 5, "Medium": 7, "High": 10},
                    "Swimming": {"Low": 6, "Medium": 8, "High": 10},
                    "Weight Training": {"Low": 3, "Medium": 5, "High": 6},
                    "Yoga": {"Low": 2, "Medium": 3, "High": 4},
                    "HIIT": {"Low": 8, "Medium": 12, "High": 15},
                    "Other": {"Low": 4, "Medium": 6, "High": 8}
                }
                
                # Calculate estimated calories
                cal_per_min = calories_per_min.get(workout_type, {"Low": 5, "Medium": 7, "High": 10}).get(intensity, 7)
                estimated_calories = round(cal_per_min * duration, 1)
                
                calories_var.set(str(estimated_calories))
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid duration.")
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Estimate Calories", command=estimate_calories).pack(side=tk.LEFT, padx=5)
        
        def save_workout():
            try:
                workout_type = workout_var.get()
                duration = float(duration_var.get())
                intensity = intensity_var.get()
                
                # Validate duration
                if duration <= 0:
                    messagebox.showerror("Input Error", "Duration must be greater than zero.")
                    return
                
                # Get calories, default to estimate if not provided
                if calories_var.get().strip():
                    try:
                        calories = float(calories_var.get())
                        if calories < 0:
                            messagebox.showerror("Input Error", "Calories cannot be negative.")
                            return
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter a valid number for calories.")
                        return
                else:
                    # Estimate calories if not provided
                    estimate_calories()
                    calories = float(calories_var.get())
                
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Create a workout and add to session
                workout = Workout(workout_type, duration, calories, intensity=intensity, notes=notes)
                self.session.add_workout(workout)
                
                # Update session display
                self.update_session_display()
                
                # Close the dialog
                dialog.destroy()
                
                # Show confirmation
                self.status_bar.config(text=f"Added {workout_type} workout: {duration} minutes, {calories} calories")
                
            except ValueError as e:
                messagebox.showerror("Input Error", str(e))
        
        ttk.Button(button_frame, text="Save", command=save_workout).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

    def start_session(self):
        """Start a new workout session."""
        if self.session.is_active:
            if not messagebox.askyesno("Session Already Active", 
                                       "A session is already active. Do you want to end it and start a new one?"):
                return
            self.end_session()
        
        self.session = Session()  # Create new session
        self.session.start()
        
        # Update UI
        self.update_session_status()
        self.update_session_display()
        
        # Update button states
        self.start_button.config(state=tk.DISABLED)
        self.end_button.config(state=tk.NORMAL)
        self.add_workout_button.config(state=tk.NORMAL)
        
        # Show confirmation
        self.status_bar.config(text="New session started")

    def end_session(self):
        """End the current workout session."""
        if not self.session.is_active:
            messagebox.showerror("No Active Session", "There is no active session to end.")
            return
        
        # End the session
        self.session.end()
        
        # Update UI
        self.update_session_status()
        self.update_session_display()
        
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        self.add_workout_button.config(state=tk.DISABLED)
        
        # Show confirmation
        self.status_bar.config(text=f"Session ended - Duration: {self.session.duration:.1f} min, " +
                                f"Calories: {self.session.total_calories:.1f}")

    def update_session_display(self):
        """Update the session details display."""
        # Enable text widget for updating
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        if not self.session.is_active and not self.session.workouts:
            self.details_text.insert(tk.END, "No active session.\n\n")
            self.details_text.insert(tk.END, "Click 'Start Session' to begin tracking your workout.")
        else:
            # Display session info
            if self.session.is_active:
                elapsed = datetime.now() - self.session.start_time
                elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
                self.details_text.insert(tk.END, f"Session active - started at {self.session.start_time.strftime('%H:%M:%S')}\n")
                self.details_text.insert(tk.END, f"Elapsed time: {elapsed_str}\n\n")
            else:
                duration = self.session.duration
                duration_str = f"{duration:.1f} minutes" if duration else "N/A"
                self.details_text.insert(tk.END, f"Session ended\n")
                self.details_text.insert(tk.END, f"Duration: {duration_str}\n\n")
            
            # Display workouts
            if self.session.workouts:
                self.details_text.insert(tk.END, "Workouts:\n")
                for i, workout in enumerate(self.session.workouts, 1):
                    self.details_text.insert(tk.END, f"{i}. {workout.workout_type} - {workout.duration:.1f} min, " +
                                            f"{workout.calories:.1f} calories\n")
                    if workout.notes:
                        self.details_text.insert(tk.END, f"   Notes: {workout.notes}\n")
                
                # Display total calories
                self.details_text.insert(tk.END, f"\nTotal Calories: {self.session.total_calories:.1f}\n")
            else:
                self.details_text.insert(tk.END, "No workouts added yet.\n\n")
                self.details_text.insert(tk.END, "Click 'Add Workout' to record your activities.")
        
        # Disable text widget again
        self.details_text.config(state=tk.DISABLED)

    def add_workout_goal(self):
        """Add a new workout goal."""
        # Create a dialog for setting a workout goal
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Workout Goal")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+{}+{}".format(
            self.root.winfo_x() + (self.root.winfo_width() // 2) - 200,
            self.root.winfo_y() + (self.root.winfo_height() // 2) - 150))
        
        # Create form fields
        form_frame = ttk.Frame(dialog, padding="20 20 20 20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Goal type
        ttk.Label(form_frame, text="Goal Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        goal_types = ["Workout Frequency", "Calories Burned", "Duration"]
        goal_var = tk.StringVar(value=goal_types[0])
        ttk.Combobox(form_frame, textvariable=goal_var, values=goal_types, state="readonly").grid(
            row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Target value
        ttk.Label(form_frame, text="Target Value:").grid(row=1, column=0, sticky=tk.W, pady=5)
        target_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=target_var).grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Time period
        ttk.Label(form_frame, text="Time Period:").grid(row=2, column=0, sticky=tk.W, pady=5)
        period_var = tk.StringVar(value="Weekly")
        ttk.Combobox(form_frame, textvariable=period_var, values=["Daily", "Weekly", "Monthly"], 
                    state="readonly").grid(row=2, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky=tk.W, pady=5)
        description_text = tk.Text(form_frame, height=3, width=30)
        description_text.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def save_goal():
            try:
                goal_type = goal_var.get()
                target = target_var.get().strip()
                period = period_var.get()
                description = description_text.get("1.0", tk.END).strip()
                
                # Validate target
                if not target:
                    messagebox.showerror("Input Error", "Please enter a target value.")
                    return
                
                try:
                    target_value = float(target)
                    if target_value <= 0:
                        messagebox.showerror("Input Error", "Target value must be greater than zero.")
                        return
                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid number for the target.")
                    return
                
                # Save goal to database
                add_goal(goal_type, target_value, period, description)
                
                # Show confirmation
                messagebox.showinfo("Goal Added", f"Your {period.lower()} {goal_type.lower()} goal has been added.")
                
                # Close dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add goal: {str(e)}")
        
        ttk.Button(button_frame, text="Save Goal", command=save_goal).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

    def handle_error(self, message):
        """Display an error message to the user."""
        messagebox.showerror("Error", message)
        self.status_bar.config(text=message)
        print(f"ERROR: {message}")

def launch_app():
    root = tk.Tk()
    app = FitnessTrackerApp(root)
    root.mainloop()