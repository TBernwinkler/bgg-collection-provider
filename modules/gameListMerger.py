from typing import List
from .data.collection import CollectionFilter

from .bggContentProcessor import Game

"""
Merges all BGG lists based on the usernames provided
Streamlines the Paradice location texts for the respective locations
"""
class LocationManager:
    # not the most efficient approach, but OK for this amount of data
    # going with this as it is easy to read/understand
    @staticmethod
    def streamline_location_strings(collection_filters: List[CollectionFilter], game_list: List[Game]) -> List[Game]:
        updated_game_list: List[Game] = []
        for game in game_list:
            for entry in collection_filters:
                if game.location and entry.filterString in game.location:
                    game.location = entry.displayText
                    game.restricted = entry.restricted
                elif not game.location and not entry.filterString:
                    game.location = entry.displayText
                    game.restricted = False
            # add all games regardless
            # O^2 runtime is acceptable, as the number of filters is limited
            updated_game_list.append(game)
        return updated_game_list
