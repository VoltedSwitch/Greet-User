import os
import sys
import termios
import tty
import select

def clear_screen():
    """Clears the terminal screen."""
    os.system("clear")


def instant_input(prompt, timeout=None, special_keys=None):
    print(prompt, end="", flush=True)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)

        if timeout:
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if not rlist:
                return "no key pressed"

        key_pressed = sys.stdin.read(1)  # Read one character

        # Handle escape sequences for arrow keys
        if key_pressed == "\x1b":
            key_pressed += sys.stdin.read(2)  # Read the next two bytes

        # Use the provided special_keys dictionary, or default to None
        if special_keys is None:
            return key_pressed  # Return raw keypress if no special keys are set
        else:
            return special_keys.get(key_pressed, key_pressed)  # Apply mapping if provided

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class CursorRelated:
    """A class that provides methods for manipulating the cursor."""
    
    @staticmethod
    def hide_cursor():
        """Hides the cursor using ANSI escape sequences."""
        print("\033[?25l")

    @staticmethod
    def show_cursor():
        """Shows the cursor using ANSI escape sequences."""
        print("\033[?25h")
