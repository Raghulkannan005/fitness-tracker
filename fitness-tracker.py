import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class Workout:
    def __init__(self, workout_type, duration, calories_burned):
        self.workout_type = workout_type
        self.duration = duration  # in minutes
        self.calories_burned = calories_burned

    def __str__(self):
        return f"{self.workout_type:10} │ {self.duration:6.1f} min │ {self.calories_burned:6.1f} cal"

class Session:
    def __init__(self):
        self.workouts = []
        self.is_active = False
        self.start_time = None
        self.end_time = None

    def start_session(self):
        if not self.is_active:
            self.is_active = True
            self.start_time = datetime.now()
            return f"Session started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return "Session is already active."

    def end_session(self):
        if self.is_active:
            self.is_active = False
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds() / 60
            stats = self.get_session_stats()
            summary = (
                f"Session ended at: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total session time: {duration:.1f} minutes\n"
                f"Workouts completed: {stats['total_workouts']}\n"
                f"Total calories burned: {stats['total_calories']:.1f}"
            )
            return summary
        else:
            return "No active session to end."

    def add_workout(self, workout):
        if self.is_active:
            self.workouts.append(workout)
            return f"Added workout: {workout}"
        else:
            return "Cannot add workout - no active session."

    def get_session_stats(self):
        if not self.workouts:
            return None
        stats = {
            "total_workouts": len(self.workouts),
            "total_duration": sum(w.duration for w in self.workouts),
            "total_calories": sum(w.calories_burned for w in self.workouts),
            "avg_duration": sum(w.duration for w in self.workouts) / len(self.workouts),
            "avg_calories": sum(w.calories_burned for w in self.workouts) / len(self.workouts)
        }
        return stats

    def display_session_details(self):
        if not self.workouts:
            return "No workouts logged in this session."
        stats = self.get_session_stats()
        details = (
            f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Workouts:\n"
        )
        for i, workout in enumerate(self.workouts, 1):
            details += f"{i}. {workout}\n"
        details += (
            f"\nSession Statistics:\n"
            f"Total Workouts: {stats['total_workouts']}\n"
            f"Total Duration: {stats['total_duration']:.1f} minutes\n"
            f"Total Calories: {stats['total_calories']:.1f}\n"
            f"Average Duration: {stats['avg_duration']:.1f} minutes\n"
            f"Average Calories: {stats['avg_calories']:.1f}"
        )
        return details

def validate_positive_number(value):
    try:
        number = float(value)
        if number <= 0:
            raise ValueError("The number must be positive.")
        return number
    except ValueError:
        raise ValueError("Invalid input. Please enter a positive number.")

class FitnessTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker")
        self.session = Session()

        # Apply styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", 14))
        style.configure("TFrame", background="#f0f0f0")
        style.map("TButton", background=[("active", "#45a049")])

        # Main frame
        main_frame = ttk.Frame(root, padding="20 20 20 20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.header_label = ttk.Label(main_frame, text="FITNESS TRACKER", font=("Helvetica", 20, "bold"), background="#4CAF50", foreground="white")
        self.header_label.pack(pady=10, fill=tk.X)

        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Session", command=self.start_session)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.add_workout_button = ttk.Button(button_frame, text="Add Workout", command=self.add_workout)
        self.add_workout_button.grid(row=0, column=1, padx=5, pady=5)

        self.display_details_button = ttk.Button(button_frame, text="Display Session Details", command=self.display_session_details)
        self.display_details_button.grid(row=1, column=0, padx=5, pady=5)

        self.end_button = ttk.Button(button_frame, text="End Session", command=self.end_session)
        self.end_button.grid(row=1, column=1, padx=5, pady=5)

        self.exit_button = ttk.Button(button_frame, text="Exit", command=root.quit)
        self.exit_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.output_text = tk.Text(main_frame, height=15, width=70, state=tk.DISABLED, font=("Helvetica", 12), background="#e0e0e0")
        self.output_text.pack(pady=10)

    def start_session(self):
        message = self.session.start_session()
        self.display_message(message)

    def end_session(self):
        message = self.session.end_session()
        self.display_message(message)

    def add_workout(self):
        if not self.session.is_active:
            self.display_message("Please start a session first.")
            return

        workout_window = tk.Toplevel(self.root)
        workout_window.title("Add Workout")

        ttk.Label(workout_window, text="Workout Type:").pack(pady=5)
        workout_type_entry = ttk.Entry(workout_window)
        workout_type_entry.pack(pady=5)

        ttk.Label(workout_window, text="Duration (minutes):").pack(pady=5)
        duration_entry = ttk.Entry(workout_window)
        duration_entry.pack(pady=5)

        ttk.Label(workout_window, text="Calories Burned:").pack(pady=5)
        calories_entry = ttk.Entry(workout_window)
        calories_entry.pack(pady=5)

        def submit_workout():
            try:
                workout_type = workout_type_entry.get()
                duration = validate_positive_number(duration_entry.get())
                calories = validate_positive_number(calories_entry.get())
                workout = Workout(workout_type, duration, calories)
                message = self.session.add_workout(workout)
                self.display_message(message)
                workout_window.destroy()
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))

        submit_button = ttk.Button(workout_window, text="Submit", command=submit_workout)
        submit_button.pack(pady=10)

    def display_session_details(self):
        message = self.session.display_session_details()
        self.display_message(message)

    def display_message(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, message)
        self.output_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#f0f0f0")  # Set the background color of the main window
    app = FitnessTrackerApp(root)
    root.mainloop()