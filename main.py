import tty 
import sys
import time
import termios 
import datetime

if sys.platform == "win32":
    import msvcrt  # Windows-only library for non-blocking input detection
else:
    import select  # Unix/macOS library for monitoring input availability

from color_constants import cc 
from file_handler import FileHandler  
from utilities import clear_screen, instant_input, CursorRelated

class LectureTracker:
    DECREMENT_LECTURE_COUNTER = "d"
    RESET_LECTURE_COUNTER = "l"
    RESET_GOAL_COUNTER = "r" 
    TURN_OFF_STREAK_BASED_COUNTING = "o" 
    TURN_ON_STREAK_BASED_COUNTING = "n"
    FULL_RESET = "f"  
    LECTURE_COMPLETED = "c"
    SAVE_AND_EXIT = "e"

    VALID_OPTIONS = (
        DECREMENT_LECTURE_COUNTER,
        RESET_LECTURE_COUNTER,
        RESET_GOAL_COUNTER,
        TURN_OFF_STREAK_BASED_COUNTING,
        TURN_ON_STREAK_BASED_COUNTING,
        FULL_RESET,
        LECTURE_COMPLETED,
        SAVE_AND_EXIT
    )

    def __init__(self):
        self.lecture_goal, self.total_lectures_listened, self.is_streak_based, self.date_to_reset_streak = FileHandler.load_data()
        self.should_display_broke_out_of_streak_mode_message = False

    def color_text_state(self, text):
        # Calculate percentage completed
        percentage_completed = (self.total_lectures_listened / self.lecture_goal) * 100

        # Assign colors based on percentage ranges
        if percentage_completed >= 80:
            colored_text = f"{cc.LIGHT_GREEN}{text}"  
        elif percentage_completed >= 50:
            colored_text = f"{cc.YELLOW}{text}"
        elif percentage_completed >= 20:
            colored_text = f"{cc.ORANGE}{text}"
        else:
            colored_text = f"{cc.LIGHT_RED}{text}"

        return colored_text
    
    def show_program_intro(self):
        print("Lecture Tracker 📝")

    def show_progress_bar(self):
        percentage = (self.total_lectures_listened / self.lecture_goal) * 100
        bar_length = 20
        filled_length = int(bar_length * (self.total_lectures_listened / self.lecture_goal))
        colored_bar = self.color_text_state('█')

        bar = f"{colored_bar * filled_length}{cc.LIGHT_RED}{'-' * (bar_length - filled_length)}{cc.END}"
        return f"[{bar}] {cc.DARK_GRAY}{percentage:.1f}%{cc.END}"
            
    def set_lecture_goal(self):
        display_invalid_integer_error_message = False
        display_goal_equal_to_listened_lectures_error_message = False
        display_goal_less_than_listened_lectures_error_message = False
        while True:
            self.show_program_intro()
        
            if display_invalid_integer_error_message:
                print(f"{cc.RED}Total Lectures amount must be a valid integer!{cc.END}")
                display_invalid_integer_error_message = False

            if display_goal_less_than_listened_lectures_error_message:
                print(f"{cc.RED}Lectures goal cannot be LESS than the amount of lectures completed so far!{cc.END}")
                display_goal_less_than_listened_lectures_error_message = False

            if display_goal_equal_to_listened_lectures_error_message:
                print(f"{cc.RED}Lectures goal cannot be EQUAL to the amount of lectures completed so far!{cc.END}")
                display_goal_equal_to_listened_lectures_error_message = False

            try:
                print()
                self.lecture_goal = int(input(f"Enter amount of lectures to complete: "))
                clear_screen()
            except ValueError:
                clear_screen()
                display_invalid_integer_error_message = True
                continue

            if self.lecture_goal < self.total_lectures_listened:
                display_goal_less_than_listened_lectures_error_message = True
            elif self.lecture_goal == self.total_lectures_listened:
                display_goal_equal_to_listened_lectures_error_message = True
            else:
                break

    def reset_streak(self):
        while True:
            print()
            proceed_input = instant_input(f"❌ You missed a day! Your streak has restarted 😣. ({cc.DARK_GRAY}p{cc.END}) proceed: ").strip().lower()
            clear_screen()
            self.show_program_intro()

            if proceed_input == "p":
                self.total_lectures_listened = 0
                break
                
    def error_msg_and_reset_streak_conditon(self):
        return (
            self.total_lectures_listened > 0 and
            self.today_s_date() == self.date_to_reset_streak
        )
    
    def streak_mode_input(self):
        # Windows implementation
        if sys.platform == "win32":
            while True:
                if self.error_msg_and_reset_streak_conditon():
                    return "_nothing_"  # Condition met, exit immediately

                if msvcrt.kbhit():  # Check if a key was pressed
                    return msvcrt.getwch().lower()  # Return the key instantly

                time.sleep(0.05)  # Small delay for efficiency

        # Unix/macOS implementation
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)  # Set terminal to raw mode
                while True:
                    if self.error_msg_and_reset_streak_conditon():
                        return "_nothing_"  # Condition met, exit immediately

                    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)  # Check input availability
                    if rlist:  # If input is available
                        return sys.stdin.read(1).lower()  # Return first detected key

            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore terminal settings

    def options_menu(self):
        right_lecture_word = "Lecture" if self.lecture_goal == 1 else "Lectures"
        if self.is_streak_based:
            prompt = f"""
Your Progress: {self.show_progress_bar()}
                                
{cc.ITALIC}Goal To Complete {cc.ITALIC}{cc.LIGHT_PURPLE}{self.lecture_goal}{cc.END} {cc.ITALIC}{right_lecture_word}{cc.END}

({cc.BLACK}{self.DECREMENT_LECTURE_COUNTER}{cc.END}) decrement lecture counter
({cc.LIGHT_CYAN}{self.RESET_LECTURE_COUNTER}{cc.END}) reset lecture counter
({cc.BROWN}{self.RESET_GOAL_COUNTER}{cc.END}) reset lecture goal
({cc.LIGHT_BLUE}{self.TURN_OFF_STREAK_BASED_COUNTING}{cc.END}) ❌ turn off streak counting mode
({cc.LIGHT_RED}{self.FULL_RESET}{cc.END}) reset lecture counter, goal and mode
({cc.PURPLE}{self.SAVE_AND_EXIT}{cc.END}) save and exit

{cc.LIGHT_WHITE}Lecture {self.total_lectures_listened + 1} ({cc.LIGHT_GREEN}{self.LECTURE_COMPLETED}{cc.LIGHT_WHITE})ompleted?{cc.END}

> """
        else:
            prompt = f"""
Your Progress: {self.show_progress_bar()}
                                    
{cc.ITALIC}Goal To Complete {cc.ITALIC}{cc.LIGHT_PURPLE}{self.lecture_goal}{cc.END} {cc.ITALIC}{right_lecture_word}{cc.END}

({cc.BLACK}{self.DECREMENT_LECTURE_COUNTER}{cc.END}) decrement lecture counter
({cc.LIGHT_CYAN}{self.RESET_LECTURE_COUNTER}{cc.END}) reset lecture counter
({cc.BROWN}{self.RESET_GOAL_COUNTER}{cc.END}) reset lecture goal
({cc.LIGHT_BLUE}{self.TURN_ON_STREAK_BASED_COUNTING}{cc.END}) ✅ turn on streak counting mode
({cc.LIGHT_RED}{self.FULL_RESET}{cc.END}) reset lecture counter, goal and mode
({cc.PURPLE}{self.SAVE_AND_EXIT}{cc.END}) save and exit

{cc.LIGHT_WHITE}Lecture {self.total_lectures_listened + 1} ({cc.LIGHT_GREEN}{self.LECTURE_COMPLETED}{cc.LIGHT_WHITE})ompleted?{cc.END}

> """
            
        print(prompt, end="", flush=True)

        if not self.is_streak_based:
            return instant_input().strip().lower()
        return self.streak_mode_input()
    
    def display_invalid_option_error_msg(self):
        valid_options_list = list(self.VALID_OPTIONS)
        if self.is_streak_based:
            valid_options_list.remove(self.TURN_ON_STREAK_BASED_COUNTING)
        else:
            valid_options_list.remove(self.TURN_OFF_STREAK_BASED_COUNTING)
        
        print(f"{cc.RED}Please enter a valid option:", end=" ")
        for option in valid_options_list:
            if option == valid_options_list[2]:
                print()
            if option == valid_options_list[-1]:
                print(f"or {option}.{cc.END}")
                continue
            print(option, end=", ")

    def get_valid_user_menu_choice(self):
        display_invalid_choice_error_message = False
        display_disabled_mode_switch_error_message = False

        while True:
            self.show_program_intro()

            if self.should_display_broke_out_of_streak_mode_message:
                print('"You broke out of streak mode!"')
                self.should_display_broke_out_of_streak_mode_message = False

            if display_invalid_choice_error_message:
                self.display_invalid_option_error_msg()
                display_invalid_choice_error_message = False

            if display_disabled_mode_switch_error_message:
                print(f"{cc.RED}You can only start a streak from scratch!\n(starting from zero lectures listened){cc.END}")
                display_disabled_mode_switch_error_message = False

            if self.is_streak_based and self.error_msg_and_reset_streak_conditon():
                self.reset_streak()

            if self.is_streak_based and self.total_lectures_listened == 1:
                print(f'"You\'re on base streak {self.total_lectures_listened}!"')

            user_choice = self.options_menu()
            clear_screen()

            if user_choice in self.VALID_OPTIONS:
                if user_choice == self.TURN_ON_STREAK_BASED_COUNTING and self.total_lectures_listened > 0:
                    display_disabled_mode_switch_error_message = True
                    continue
                return user_choice
            
            elif user_choice != "_nothing_":
                display_invalid_choice_error_message = True

    def confirm_user_full_reset(self):
        while True:
            surity = instant_input(f"Are you sure you want to reset everything? ({cc.LIGHT_GREEN}y{cc.END}) or ({cc.LIGHT_RED}n{cc.END}): ").strip().lower()
            clear_screen()
            if surity == "y":
                self.lecture_goal = 0
                self.total_lectures_listened = 0
                self.is_streak_based = False   
                return True
            elif surity == "n":
                return False

    def today_s_date(self):
        return datetime.date.today()

    def increment_lectures_listened(self):
        self.total_lectures_listened += 1
        if self.is_streak_based:
            self.date_to_reset_streak = self.today_s_date() + datetime.timedelta(days=2)

    def decrement_lectures_listened(self):
        self.total_lectures_listened = max(0, self.total_lectures_listened - 1)

    def reset_lectures_listened(self):
        self.total_lectures_listened = 0

    def reset_lecture_goal(self):
        self.lecture_goal = 0

    def enable_streak_based_counting(self):
        self.is_streak_based = True

    def disable_streak_based_counting(self):
        self.is_streak_based = False
        self.should_display_broke_out_of_streak_mode_message = True

    def if_lecture_goal_met(self):
        CursorRelated.hide_cursor()
        print(f"Your Progress: {self.show_progress_bar()}")
        time.sleep(3)
        clear_screen()

        if self.lecture_goal == 1:
            print(f"Congrats on completing 1 lecture 🥳!")
        else:
            print(f"Congrats on completing all {self.lecture_goal} of your lectures 🥳!")

        self.lecture_goal = 0
        self.total_lectures_listened = 0
        self.is_streak_based = False

        self.save_and_exit()

    def save_and_exit(self):
        self.save_state()
        exit()

    def save_state(self):
        FileHandler.save_data(
            self.lecture_goal,
            self.total_lectures_listened,
            self.is_streak_based,
            self.date_to_reset_streak
        )
    
    def run(self):
        clear_screen()
        while True:
            if self.lecture_goal == 0:
                self.set_lecture_goal()

            while True:
                user_menu_choice = self.get_valid_user_menu_choice()

                if user_menu_choice == self.DECREMENT_LECTURE_COUNTER:
                    self.decrement_lectures_listened()

                elif user_menu_choice == self.RESET_LECTURE_COUNTER:
                    self.reset_lectures_listened()

                elif user_menu_choice == self.RESET_GOAL_COUNTER:
                    self.reset_lecture_goal()
                    break

                elif user_menu_choice == self.TURN_ON_STREAK_BASED_COUNTING:
                    self.enable_streak_based_counting()

                elif user_menu_choice == self.TURN_OFF_STREAK_BASED_COUNTING:
                    self.disable_streak_based_counting()

                elif user_menu_choice == self.FULL_RESET:
                    if self.confirm_user_full_reset():
                        break
    
                elif user_menu_choice == self.LECTURE_COMPLETED:
                    self.increment_lectures_listened()

                    if self.total_lectures_listened == self.lecture_goal:
                        self.if_lecture_goal_met()
                
                elif user_menu_choice == self.SAVE_AND_EXIT:
                   self.save_and_exit()


app = LectureTracker()

if __name__ == "__main__":
    app.run()
