import os

def hide_cursor():
    """Hides the cursor using ANSI escape sequences."""
    print("\033[?25l")


def show_cursor():
    """Shows the cursor using ANSI escape sequences."""
    print("\033[?25h")


def clear_screen():
    """Clears the terminal screen."""
    os.system("clear")
