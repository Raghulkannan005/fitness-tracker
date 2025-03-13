class Workout:
    def __init__(self, workout_type, duration, calories_burned, intensity="Medium", notes=""):
        self.workout_type = workout_type
        self.duration = duration  # in minutes
        self.calories_burned = calories_burned
        self.calories = calories_burned  # Add alias for compatibility
        self.intensity = intensity
        self.notes = notes

    def __str__(self):
        return f"{self.workout_type:10} │ {self.duration:6.1f} min │ {self.calories_burned:6.1f} cal"