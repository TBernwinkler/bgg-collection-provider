import json
import os.path
from types import SimpleNamespace
from typing import List
from modules.data.collection import CollectionConfig, CollectionFilter
from modules.data.connection import ConnectionProperties

# Read all configurations from JSON files
class ConfigLoader:
    def __init__(self):
        self.configPath = os.path.abspath(os.path.dirname(__file__))

    # Generic file reader to be used for both config files
    def _read_file(self, file_name: str):
        path = os.path.join(self.configPath, file_name)
        with open(path) as f:
            config_content = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
            return config_content
        return ""

    # Loads BGG specific information, such as usernames or filter criteria
    def read_collections_config(self):
        return self._setup_collection_object(self._read_file("../config/collections.json"))

    # Loads all relevant information such as API keys etc. to make connections possible
    def read_connections_config(self):
        return self._setup_connection_object(self._read_file("../config/connections.json"))

    @staticmethod
    def _setup_collection_object(collection_json):
        collection_config_list: List[CollectionConfig] = []
        for entry in collection_json:
            filters: List[CollectionFilter] = []
            for entry_filter in entry.filters:
                filters.append(CollectionFilter(display_text=entry_filter.displayText, filter_string=entry_filter.filterString))
            collection_config_list.append(CollectionConfig(entry.bggName, filters))
        return  collection_config_list

    @staticmethod
    def _setup_connection_object(connection_json):
        return ConnectionProperties(connection_json.aiApiKey,
                                    connection_json.server)

# test = ConfigLoader()
# collections=test.read_collections_config()
# connections=test.read_connections_config()
# print(collections, connections)