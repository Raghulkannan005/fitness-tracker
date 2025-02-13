class Workout:
    """
    Represents a single workout session with type, duration, and calories burned.
    
    Attributes:
        workout_type (str): Type of workout (e.g., Running, Cycling)
        duration (float): Duration of workout in minutes
        calories_burned (float): Calories burned during workout
    """
    def __init__(self, workout_type, duration, calories_burned):
        self.workout_type = workout_type
        self.duration = duration  # in minutes
        self.calories_burned = calories_burned

    def log_workout(self):
        return {
            "type": self.workout_type,
            "duration": self.duration,
            "calories": self.calories_burned
        }

    def __str__(self):
        """Return a formatted string representation of the workout."""
        return f"{self.workout_type:10} │ {self.duration:6.1f} min │ {self.calories_burned:6.1f} cal"