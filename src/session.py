from datetime import datetime
from database import add_workout, add_session, get_session_details, get_sessions

class Session:
    def __init__(self):
        self.workouts = []
        self.is_active = False
        self.start_time = None
        self.end_time = None
        self.session_id = None
        self.total_calories = 0
        self.duration = 0

    def start(self):
        """Start a new session."""
        if not self.is_active:
            self.is_active = True
            self.start_time = datetime.now()
            # Create a new session in database
            self.session_id = self.start_new_session()
            return True
        return False

    def end(self):
        """End the current session."""
        if self.is_active:
            self.is_active = False
            self.end_time = datetime.now()
            self.duration = (self.end_time - self.start_time).total_seconds() / 60
            self.total_calories = sum(w.calories_burned for w in self.workouts)
            # Update session in database
            add_session(
                self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                self.duration,
                self.total_calories,
                session_id=self.session_id
            )
            return True
        return False

    def add_workout(self, workout):
        """Add a workout to the current session."""
        if self.is_active:
            try:
                self.workouts.append(workout)
                # Save the workout to the database
                add_workout(
                    workout.workout_type, 
                    workout.duration, 
                    workout.calories_burned, 
                    self.session_id,
                    intensity=workout.intensity,
                    notes=workout.notes
                )
                # Update session totals
                self.total_calories = sum(w.calories_burned for w in self.workouts)
                self.duration = sum(w.duration for w in self.workouts)
                return True
            except Exception as e:
                print(f"Error adding workout: {e}")
                return False
        return False

    def get_session_stats(self):
        """Get current session statistics."""
        if not self.workouts:
            return {
                "total_workouts": 0,
                "total_duration": 0,
                "total_calories": 0,
                "avg_duration": 0,
                "avg_calories": 0
            }
        
        stats = {
            "total_workouts": len(self.workouts),
            "total_duration": self.duration,
            "total_calories": self.total_calories,
            "avg_duration": self.duration / len(self.workouts),
            "avg_calories": self.total_calories / len(self.workouts)
        }
        return stats

    def display_session_details(self):
        """Get formatted session details for display."""
        if not self.is_active and not self.session_id:
            return "No active session to display."
        
        if not self.workouts:
            return "No workouts logged for this session."
            
        stats = self.get_session_stats()
        details = f"Session details:\n\n"
        details += f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        details += f"Workouts:\n"
        
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

    def start_new_session(self):
        """Initialize a new session in the database."""
        try:
            session_id = add_session(
                self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                None, 0, 0
            )
            return session_id
        except Exception as e:
            print(f"Error creating new session: {e}")
            return None