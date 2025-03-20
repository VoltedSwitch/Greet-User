import json
import datetime

class FileHandler:
    FILE_NAME = "lectures_listened.json"

    @staticmethod
    def save_data(lecture_goal, total_lectures_listened, is_streak_based, date_to_reset_streak):
        """Saves the total lectures and completed lectures to a JSON file."""
        with open(FileHandler.FILE_NAME, "w") as file:
            json.dump([
                lecture_goal,
                total_lectures_listened,
                is_streak_based,
                date_to_reset_streak.isoformat()
            ], file)

    @staticmethod
    def load_data():
        """Loads the saved lecture data or returns a default value if the file is missing/corrupt."""
        try:
            with open(FileHandler.FILE_NAME, "r") as file:
               data = json.load(file)

               data[3] = datetime.date.fromisoformat(data[3])

               return data

        except (FileNotFoundError, json.JSONDecodeError):
            return [0, 0, False, datetime.date.today()]