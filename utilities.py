import os

def clear_screen():
    """Clears the terminal screen."""
    os.system("clear")


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
