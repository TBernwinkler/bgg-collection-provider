import json
import logging
from typing import List
from glom import glom

from .data.filterReference import FilterReference
from .data.game import Game


class ContentProcessor:
    def __init__(self):
        self.root_keys = "items.item"
        self.optional = ["version", "thumbnail"]


    # Iterates through the raw BGG file and filters for the needed properties
    # Eventually creates a list with the properties that are really needed
    def process_game_list(self, raw_object):
        processed_game_list: List[Game] = []
        for item in glom(raw_object, self.root_keys):
            statistics = item["stats"]
            # ensure that only boardgames (no expansions) with a valid max player count are considered
            if item["@subtype"] == "boardgame" and "@maxplayers" in statistics:
                # minplayers is not always set
                min_players = ""
                if "@minplayers" in statistics:
                    min_players = statistics["@minplayers"]

                # in some games, a specific version (language, release year etc. is provided
                # These can have a different thumbnail image
                # Multiple languages (e.g. Captain Flip) are possible
                languages = []
                thumbnail = ""
                if "thumbnail" in item:
                    thumbnail = item["thumbnail"]
                if "version" in item:
                    version_specifics = glom(item, "version.item")
                    if "thumbnail" in version_specifics:
                        thumbnail = version_specifics["thumbnail"]
                    if "link" in version_specifics:
                        for entry in version_specifics["link"]:
                            if "@type" in entry and entry["@type"] == "language":
                                languages.append(entry["@value"])

                # Derive Paradice location from the comments if applicable
                game_location = ""
                if "comment" in item:
                    game_location = item["comment"]

                game_types = []
                for game_type in glom(item, "stats.rating.ranks.rank"):
                    if '@type' in game_type and '@name' in game_type and game_type["@type"] == "family":
                        game_types.append(game_type["@name"])

                game = Game(game_id=item["@objectid"],
                            game_name=glom(item, "name.#text"),
                            game_rating=float(glom(item, "stats.rating.average.@value")), # use the BGG depicted rating, rather than 'bayesaverage'
                            game_location=game_location,
                            game_min_players=int(min_players),
                            game_max_players=int(statistics["@maxplayers"]),
                            game_thumbnail=thumbnail,
                            game_languages=languages,
                            game_types=game_types)

                # per default only "version" entries have weight
                # Derive values based on categories
                game_in_list = False
                for list_entry in processed_game_list:
                    if list_entry.id == game.id:
                        game_in_list = True
                if not game_in_list:
                    processed_game_list.append(game)
        return processed_game_list


    """
    This method takes all the poll results and evaluates them. As for all other values, the results are put in a range
    from 2 to -2. In this particular case, the processing not obvious. The representation is as follows:
    2: No necessary in-game text
    1: Some necessary text - easily memorized or small crib sheet
    0: Moderate in-game text - needs crib sheet or paste ups
    -1: Extensive use of text - massive conversion needed to be playable
    -2: Unplayable in another language
    The number that is mapped to the category with the most upvotes will be returned.
    """
    @staticmethod
    def _get_language_dependency(poll_results):
        result_dict = { }
        iteration = 0
        if 'result' in poll_results:
            for poll_result in poll_results['result']:
                # range from 1-5
                result_dict[str(iteration+1)] = int(poll_result['@numvotes'])
                iteration+=1
            if max(result_dict.values()) > 0:
                return max(result_dict, key=result_dict.get)
        return -1


    """
    This method iterates through the community voting of "Best", "Recommended" and "Not Recommended" number of players
    for the game in question. If around 2/3 of the community are in favor of the player number, the number is added
    to the array of recommendations for the number of players for this particular game. 
    """
    @staticmethod
    def _get_recommended_player_numbers(player_number_votings, min_players: int, max_players: int):
        recommended_player_numbers = []
        for entry in player_number_votings:
            try:
                for number in range(min_players, max_players+1):
                    if str(number) in str(entry['@numplayers']):
                        best = 0
                        recommended = 0
                        avoid = 0
                        for result in entry['result']:
                            if result['@value'] == 'Best':
                                best = int(result['@numvotes'])
                            elif result['@value'] == 'Recommended':
                                recommended = int(result['@numvotes'])
                            else:
                                avoid = int(result['@numvotes'])
                        if best + recommended >= 2 * avoid:
                            recommended_player_numbers.append(number)
            except Exception as e:
                logging.warning("A game has not received any player voting, yet.")
                logging.error(e)
        return recommended_player_numbers


    """
    This method processes all relevant filters regarding game mechanics as well as game themes.
    It receives all relevant filter values that are connected to the games and compares them to
    predefined filter categories that are defined in the respective JSON files (config directory).
    """
    # todo: check if theme strings are different and/or maybe the JSON content are substrings
    @staticmethod
    def _get_applicable_filters(game_links, available_filters: List[FilterReference]):
        applicable_categories = []
        for link in game_links:
            for filter_item in available_filters:
                matches = 0
                for selector in filter_item.selectors:
                    if link['@value'] == selector:
                        matches += 1
                if matches == len(filter_item.selectors):
                    applicable_categories.append(filter_item.category)
        return applicable_categories


    @staticmethod
    def _get_min_age(game_info):
        if 'poll' in game_info:
            for poll in game_info['poll']:
                if '@name' in poll and poll['@name'] == 'suggested_playerage' and 'results' in poll and 'result' in poll['results']:
                    max_value = 0
                    min_age = -1
                    poll_results = glom(poll, 'results.result')
                    for poll_result in poll_results:
                        try:
                            votes = int(poll_result['@numvotes'])
                            if poll_result['@value'] == '21 and up':
                                age = 21
                            else:
                                age = int(poll_result['@value'])
                            if votes > max_value:
                                max_value = votes
                                min_age = age
                        except Exception as e:
                            logging.error('Failed to get min mage from poll result (cast from string to number failed). Exception: %s', repr(e))
                    return min_age
        elif 'minage' in game_info and '@value' in game_info['minage']:
            return glom(game_info, 'minage.@value')
        return -1


    '''
    Batch information has been requested for a number of games. This information is now parsed
    and used to enrich the details of the existing game list. The original list is updated right
    away to avoid using too much memory. Every batch of game details is processed right away to
    free up resources for the next batch.
    '''
    def enrich_bulk_information(self, games: List[Game], bulk_infos,
                                gameMechanics: List[FilterReference], gameThemes: List[FilterReference]):
        for game in games: # might have to iterate via index
            logging.info(f'Processing data for game [{game.name}]')
            for item in glom(bulk_infos, self.root_keys):
                if game.id == item['@id']:
                    game.set_release_year_group(glom(item, 'yearpublished.@value'))
                    game.set_play_time_category(glom(item, 'maxplaytime.@value'))
                    game.set_difficulty_category(glom(item, 'statistics.ratings.averageweight.@value'))
                    game.min_age = self._get_min_age(item)
                    language_poll = {}
                    player_number_poll = {}
                    for poll_data in item['poll']:
                        if 'results' in poll_data:
                            if poll_data['@name'] == 'language_dependence':
                                language_poll = poll_data['results']
                            elif poll_data['@name'] == 'suggested_numplayers':
                                player_number_poll = poll_data['results']
                        else:
                            logging.info('No results in poll_data for game: ', game.name)
                    game.language_dependency_group = self._get_language_dependency(language_poll)
                    game.set_recommended_player_numbers(self._get_recommended_player_numbers(player_number_poll, game.min_players, game.max_players))
                    game.set_cooperative_indicator(-1)
                    for reference in item['link']:
                        if reference['@value'] == 'Cooperative Game':
                            game.set_cooperative_indicator(1)
                        elif reference['@value'] == 'Semi-Cooperative Game' or reference['@value'] == 'Team-Based Game':
                            game.set_cooperative_indicator(0)
                    game.set_game_mechanics(self._get_applicable_filters(item['link'], gameMechanics))
                    game.set_game_themes(self._get_applicable_filters(item['link'], gameThemes))
                    if 'description' in item:
                        game.descriptions.update(EN=item['description'])
        return games
