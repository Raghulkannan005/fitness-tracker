from datetime import datetime
from colorama import Fore, Style

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
            print(f"{Fore.GREEN}Session started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        else:
            print("Session is already active.")

    def end_session(self):
        """Enhanced session end with summary."""
        if self.is_active:
            self.is_active = False
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds() / 60
            stats = self.get_session_stats()
            
            print(f"\n{Fore.CYAN}════════ Session Summary ════════{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Session ended at: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total session time: {duration:.1f} minutes")
            print(f"Workouts completed: {stats['total_workouts']}")
            print(f"Total calories burned: {stats['total_calories']:.1f}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No active session to end.{Style.RESET_ALL}")

    def add_workout(self, workout):
        """Add a workout to the current session."""
        if self.is_active:
            self.workouts.append(workout)
            print(f"{Fore.GREEN}Added workout: {workout}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Cannot add workout - no active session.{Style.RESET_ALL}")

    def get_session_stats(self):
        """Calculate and return session statistics."""
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
        """Enhanced session details display with statistics."""
        if not self.workouts:
            print(f"{Fore.YELLOW}No workouts logged in this session.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}════════ Session Details ════════{Style.RESET_ALL}")
        if self.start_time:
            print(f"{Fore.WHITE}Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        stats = self.get_session_stats()
        
        print(f"\n{Fore.YELLOW}Workouts:{Style.RESET_ALL}")
        for i, workout in enumerate(self.workouts, 1):
            print(f"{Fore.WHITE}{i}. {workout}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Session Statistics:{Style.RESET_ALL}")
        print(f"Total Workouts: {stats['total_workouts']}")
        print(f"Total Duration: {stats['total_duration']:.1f} minutes")
        print(f"Total Calories: {stats['total_calories']:.1f}")
        print(f"Average Duration: {stats['avg_duration']:.1f} minutes")
        print(f"Average Calories: {stats['avg_calories']:.1f}")