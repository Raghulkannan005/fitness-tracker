import os
import time
from colorama import init, Fore, Style
from session import Session
from workout import Workout
from utils import validate_positive_number

# Initialize colorama for cross-platform colored output
init()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print a stylized header."""
    print(f"{Fore.CYAN}╔════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║    {Fore.WHITE}FITNESS TRACKER{Fore.CYAN}     ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚════════════════════════════╝{Style.RESET_ALL}")

def get_workout_details():
    """Get workout details from user input with enhanced UI."""
    workout_types = ["Running", "Cycling", "Swimming", "Walking", "Weights", "Other"]
    
    print(f"\n{Fore.GREEN}Available workout types:{Style.RESET_ALL}")
    for i, w_type in enumerate(workout_types, 1):
        print(f"{Fore.YELLOW}{i}. {w_type}{Style.RESET_ALL}")
    
    while True:
        try:
            workout_type = input(f"\n{Fore.WHITE}Enter workout type (or number): {Style.RESET_ALL}").strip()
            try:
                idx = int(workout_type) - 1
                if 0 <= idx < len(workout_types):
                    workout_type = workout_types[idx]
                    break
            except ValueError:
                if workout_type in workout_types:
                    break
                print(f"{Fore.RED}Please enter a valid workout type or number{Style.RESET_ALL}")
        except KeyboardInterrupt:
            return None

    try:
        duration = validate_positive_number(input(f"{Fore.WHITE}Enter duration (in minutes): {Style.RESET_ALL}"))
        calories = validate_positive_number(input(f"{Fore.WHITE}Enter calories burned: {Style.RESET_ALL}"))
        return Workout(workout_type, duration, calories)
    except ValueError as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        return None

def display_menu(session):
    """Display the main menu with color formatting."""
    print_header()
    if session.is_active:
        print(f"\n{Fore.GREEN}📍 Session Active{Style.RESET_ALL}")
    
    print(f"\n{Fore.BLUE}Menu Options:{Style.RESET_ALL}")
    menu_items = [
        "Start Session",
        "Add Workout",
        "Display Session Details",
        "End Session",
        "Exit"
    ]
    
    for i, item in enumerate(menu_items, 1):
        print(f"{Fore.YELLOW}{i}. {Fore.WHITE}{item}{Style.RESET_ALL}")

def main():
    session = Session()
    
    while True:
        try:
            clear_screen()
            display_menu(session)
            
            choice = input(f"\n{Fore.GREEN}Enter your choice (1-5): {Style.RESET_ALL}")
            
            if choice == "1":
                clear_screen()
                session.start_session()
            elif choice == "2":
                if session.is_active:
                    workout = get_workout_details()
                    if workout:
                        session.add_workout(workout)
                        print(f"{Fore.GREEN}Workout added successfully!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Please start a session first.{Style.RESET_ALL}")
            elif choice == "3":
                clear_screen()
                session.display_session_details()
            elif choice == "4":
                session.end_session()
            elif choice == "5":
                clear_screen()
                print(f"{Fore.GREEN}Thank you for using Fitness Tracker!{Style.RESET_ALL}")
                time.sleep(1)
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            
            input(f"\n{Fore.BLUE}Press Enter to continue...{Style.RESET_ALL}")
        
        except KeyboardInterrupt:
            clear_screen()
            print(f"{Fore.YELLOW}\nExiting...{Style.RESET_ALL}")
            time.sleep(1)
            break

if __name__ == "__main__":
    print(f"{Fore.GREEN}Welcome to Fitness Tracker!{Style.RESET_ALL}")
    time.sleep(1)
    main()