from typing import List
from .game import Game

class CollectionFilter:
    def __init__(self, display_text: str, filter_string: str):
        self.displayText = display_text
        self.filterString = filter_string

class CollectionConfig:
    def __init__(self, bgg_name: str, filters: List[CollectionFilter]):
        self.bgg_name = bgg_name
        self.filters = filters

class GameCollection:
    def __init__(self, collection_config: CollectionConfig, games: List[Game]):
        self.collection_config = collection_config
        self.games = games