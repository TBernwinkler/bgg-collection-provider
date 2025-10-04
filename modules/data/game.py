import numbers
from datetime import datetime


class Game:
    def __init__(self, game_id, game_name, game_rating, game_location,
                 game_min_players, game_max_players, game_thumbnail, game_languages):
        # generic fix values
        self.difficulty_limiters = [1.6, 2.25, 3.0, 3.5]
        self.current_year = datetime.now().year
        self.play_time_multiplier = 1.25 # for more realistic play time
        # assignments from constructor
        self.id = game_id
        self.name = game_name
        self.rating = game_rating
        self.location = game_location
        self.min_players = game_min_players
        self.max_players = game_max_players
        self.thumbnail = game_thumbnail
        self.languages = game_languages
        self.difficulty_category = 99 # arbitrary value in the original
        self.release_group = 99
        self.playing_time_category = 99
        self.language_dependency_group = 99
        self.is_cooperative = -1 # 1=cooperative, 0=team-based; -1=competitive
        # coop means conflict score = 1
        # todo: coop and conflict potential

    @staticmethod
    def _is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False


    def set_release_year_group(self, release_year):
        # default: 99; to be ignored on the FE part
        if self._is_number(release_year):
            released = float(release_year)
            if (self.current_year - released) <= 2:
                self.release_group = 2
            elif (self.current_year - released) <= 5:
                self.release_group = 1
            elif (self.current_year - released) <= 10:
                self.release_group = 0
            elif (self.current_year - released) <= 20:
                self.release_group = -1
            else:
                self.release_group = -2



    def set_play_time_category(self, max_play_time):
        # default: 99 as above
        if self._is_number(max_play_time):
            play_time = float(max_play_time)
            if play_time < 45:
                self.playing_time_category = 2
            elif play_time < 90:
                self.playing_time_category = 1
            elif play_time < 120:
                self.playing_time_category = 0
            elif play_time < 180:
                self.playing_time_category = -1
            else:
                self.playing_time_category = -2


    def set_difficulty_category(self, difficulty_rating):
        # default: 99 as above
        if self._is_number(difficulty_rating):
            rating = float(difficulty_rating)
            if rating < 1.6:
                self.difficulty_category = 2
            elif rating < 2.25:
                self.difficulty_category = 1
            elif rating < 3.0:
                self.difficulty_category = 0
            elif rating < 3.5:
                self.difficulty_category = -1
            else:
                self.difficulty_category = -2


    # again, using arbitrary numbers from the original project
    def set_language_dependency(self, language_dependence):
        if self._is_number(language_dependence):
            self.language_dependency_group = 2 - int(language_dependence)


    def set_cooperative_indicator(self, value: int):
        self.is_cooperative = value