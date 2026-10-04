import numbers
from datetime import datetime
from typing import List


class Game:
    def __init__(self, game_id, game_name, game_rating, game_location,
                 game_min_players, game_max_players, game_thumbnail, game_languages, game_types):
        # generic fix values
        self.difficulty_limiters = [1.6, 2.25, 3.0, 3.5]
        self.current_year = datetime.now().year
        self.play_time_multiplier = 1.25 # for more realistic play time
        # assignments from constructor
        self.id = game_id
        self.name = game_name
        self.rating = game_rating
        self.location = game_location
        self.restricted = False
        self.min_players = game_min_players
        self.max_players = game_max_players
        self.thumbnail = game_thumbnail
        self.languages = game_languages
        self.types = game_types # Examples: familygames, strategygames, thematic, ... abstract, children, party, wargame
        self.difficulty_category = -1 # not rated -> -1 -> max. in-range score punishment
        self.year_published = -1 # not rated -> -1 -> max. in-range score punishment
        self.release_group = -1 # not rated -> -1 -> max. in-range score punishment
        self.playing_time_category = -1 # not rated -> -1 -> max. in-range score punishment
        self.language_dependency_group = -1 # not rated -> -1 -> max. in-range score punishment
        self.is_cooperative = -1 # 1=cooperative, 0=team-based; -1=competitive
        self.recommended_player_numbers = []
        self.game_mechanics = []
        self.game_themes = []
        self.descriptions = {'DE': '', 'EN': ''}
        self.min_age = -1 # value not provided in poll or game data


    @staticmethod
    def _is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_integer(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    """
    As the function name indicates: Assigns a release year category to the game. It also
    saves the publishing year to the game entry, so it can be displayed in the web app.
    Based on originally arbitrary numbers, the category groups are in alignment with the
    quiz questions of the associated web app. The higher the number, the more recent the
    game was published.
    """
    def set_release_year_group(self, release_year):
        # default: 99; to be ignored on the FE part
        if self._is_integer(release_year):
            released = int(release_year)
            self.year_published = released
            if (self.current_year - released) <= 2:
                self.release_group = 1
            elif (self.current_year - released) <= 5:
                self.release_group = 2
            elif (self.current_year - released) <= 10:
                self.release_group = 3
            elif (self.current_year - released) <= 20:
                self.release_group = 4
            else:
                self.release_group = 5


    # Same concept as for the release year group. In this function, the category for the
    # time spent playing a particular game is set.
    def set_play_time_category(self, max_play_time):
        # default: -1
        if self._is_integer(max_play_time):
            play_time = int(max_play_time)
            if play_time < 45:
                self.playing_time_category = 1
            elif play_time < 90:
                self.playing_time_category = 2
            elif play_time < 120:
                self.playing_time_category = 3
            elif play_time < 180:
                self.playing_time_category = 4
            elif play_time > 180:
                self.playing_time_category = 5
            else:
                self.playing_time_category = -1

    # After playing time, game "weight" / perceived difficulty is also categorized.
    # Again, the categories are only relevant for the decisions made in the quiz.
    def set_difficulty_category(self, difficulty_rating):
        # default: init is -1
        if self._is_number(difficulty_rating):
            rating = float(difficulty_rating)
            if rating < 1.6:
                self.difficulty_category = 1
            elif rating < 2.25:
                self.difficulty_category = 2
            elif rating < 3.0:
                self.difficulty_category = 3
            elif rating < 3.5:
                self.difficulty_category = 4
            else:
                self.difficulty_category = 5


    def set_cooperative_indicator(self, value: int):
        self.is_cooperative = value

    # Saves the list of all recommended numbers of player for a game to the object
    def set_recommended_player_numbers(self, recommended: List[int]):
        self.recommended_player_numbers = recommended

    def set_game_mechanics(self, mechanics: List[str]):
        self.game_mechanics = mechanics

    def set_game_themes(self, themes: List[str]):
        self.game_themes = themes
