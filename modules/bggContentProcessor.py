import json
from typing import List
from glom import glom
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


                game = Game(game_id=item["@objectid"],
                            game_name=glom(item, "name.#text"),
                            game_rating=glom(item, "stats.rating.bayesaverage.@value"),
                            game_location=game_location,
                            game_min_players=min_players,
                            game_max_players=statistics["@maxplayers"],
                            game_thumbnail=thumbnail,
                            game_languages=languages)

                # yearpublished => group
                # play_time (categories)

                # per default only "version" entries have weight
                # Derive values based on categories

                game_in_list = False
                for list_entry in processed_game_list:
                    if list_entry.id == game.id:
                        game_in_list = True
                if not game_in_list:
                    processed_game_list.append(game)
        return processed_game_list


    @staticmethod
    def _get_language_dependency(poll_results):
        result_dict = { }
        for poll_result in poll_results['result']:
            result_dict[poll_result['@level']] = int(poll_result['@numvotes'])
        return max(result_dict, key=result_dict.get)

    @staticmethod
    def _get_recommended_player_numbers(player_number_votings):
        recommended_player_numbers = []
        for entry in player_number_votings['result']:
            # todo
            recommended_player_numbers.append('42')

    '''
    Batch information has been requested for a number of games. This information is now parsed
    and used to enrich the details of the existing game list. The original list is updated right
    away to avoid using too much memory. Every batch of game details is processed right away to
    free up resources for the next batch.
    '''
    def enrich_bulk_information(self, games: List[Game], bulk_infos):
        for game in games: # might have to iterate via index
            for item in glom(bulk_infos, self.root_keys):
                if game.id == item['@id']:
                    game.set_release_year_group(glom(item, 'yearpublished.@value'))
                    game.set_play_time_category(glom(item, 'maxplaytime.@value'))
                    game.set_difficulty_category(glom(item, 'statistics.ratings.averageweight.@value'))
                    language_poll = {}
                    player_number_poll = {}
                    for poll_data in item['poll']:
                        if poll_data['@name'] == 'language_dependence':
                            language_poll = poll_data['results']
                        elif poll_data['@name'] == 'suggested_numplayers':
                            player_number_poll = poll_data['results']
                    game.language_dependency_group = self._get_language_dependency(language_poll)
                    # todo: take care of the attribute/setter inside the game class
                    self._get_recommended_player_numbers(player_number_poll)
                    game.set_cooperative_indicator(-1)
                    for reference in item['link']:
                        if reference['@value'] == 'Cooperative Game':
                            game.set_cooperative_indicator(1)
                        elif reference['@value'] == 'Semi-Cooperative Game' or reference['@value'] == 'Team-Based Game':
                            game.set_cooperative_indicator(0)
        return games