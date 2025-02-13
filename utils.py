# utils.py

def validate_positive_number(value):
    """Validate that the input is a positive number."""
    try:
        number = float(value)
        if number <= 0:
            raise ValueError("The number must be positive.")
        return number
    except ValueError:
        raise ValueError("Invalid input. Please enter a positive number.")

def format_session_output(session_data):
    """Format the session data for output."""
    output = f"Session Details:\n"
    output += f"Start Time: {session_data['start_time']}\n"
    output += f"End Time: {session_data['end_time']}\n"
    output += f"Duration: {session_data['duration']} minutes\n"
    output += f"Workouts:\n"
    for workout in session_data['workouts']:
        output += f"  - {workout['type']}: {workout['duration']} minutes, {workout['calories']} calories\n"
    return output

def format_duration(minutes):
    """Convert minutes to hours and minutes format."""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"

def calculate_calories_per_minute(calories, duration):
    """Calculate calories burned per minute."""
    return calories / duration if duration > 0 else 0