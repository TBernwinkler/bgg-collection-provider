# reminder to install dependencies
# pip install -r requirements.txt

import simplejson
from typing import List
from modules.configLoader import ConfigLoader
from modules.bggCollectionAgent import BggCollectionAgent
from modules.bggContentProcessor import ContentProcessor, Game
from modules.gameListMerger import LocationManager
from modules.data.collection import CollectionConfig, GameCollection
from modules.data.connection import ConnectionProperties

# Reads json config files and transforms them into class objects for easier interaction.
# This get the application ready for all subsequent tasks.
def initialize():
    loader = ConfigLoader()
    collection_config_list: List[CollectionConfig] = loader.read_collections_config()
    connections_config: ConnectionProperties = loader.read_connections_config()
    return collection_config_list, connections_config


# BGG public API call
# Retrieves the list of games for a particular BGG username
def retrieve_collection(collection_user_name: str):
    agent = BggCollectionAgent()
    return agent.get_collection(collection_user_name)


# Process data and filter accordingly
def process_raw_content(raw_content_file):
    processor = ContentProcessor()
    return processor.process_game_list(raw_content_file)


# Merge game lists and standardize location strings
def merge_game_lists(collections: List[GameCollection]) -> List[Game]:
    all_games = []
    location_manager = LocationManager()
    for collection in collections:
        # merge the updated lists and return the value to main
        # todo: kick out duplicates of the merged list
        all_games = all_games + location_manager.streamline_location_strings(collection.collection_config.filters, collection.games)
    return all_games


# Send requests to the BGG API to retrieve more game details
# The details are requested in batches, each response provides details for multiple games at once
def retrieve_game_batch_information(game_list: List[Game]):
    batch_size = 20
    index = 0
    agent = BggCollectionAgent()
    processor = ContentProcessor()
    # regular batch processing
    while (index + batch_size) <= len(game_list):
        batch = game_list[index:(index + batch_size)]
        batch_id_list = []
        for element in batch:
            batch_id_list.append(element.id)
        batch_ids = ",".join(batch_id_list)
        game_list = processor.enrich_bulk_information(game_list, agent.request_batch_information(batch_ids))
        index += batch_size
    # finish the rest which may be less than a full batch_size
    if index <= len(game_list) < (index + batch_size):
        final_batch = game_list[index:]
        batch_id_list = []
        for element in final_batch:
            batch_id_list.append(element.id)
        batch_ids = ",".join(batch_id_list)
        game_list = processor.enrich_bulk_information(game_list, agent.request_batch_information(batch_ids))
    return game_list


# BGG internal API call for additional data enrichment
# TODO: reuse the content for the JSON BGG API

# AI rework call
# TODO: Standardize game descriptions via AI API

# Save to JSON file
# TODO: Save final file to disk; makes it available for the API sharing

# offer API section
# TODO: implement the API to provide the JSON content from the file

def main():
    # (1) Reading config
    collection_config_list, connections_config = initialize()

    # (2) Requesting BGG lists and processing data (select relevant information)
    collections: List[GameCollection] = []
    for collection in collection_config_list:
        print ("Processing BGG collection for username: " + collection.bgg_name)
        game_collection_dict = retrieve_collection(collection.bgg_name)
        collections.append(GameCollection(collection_config=collection, games=process_raw_content(game_collection_dict)))

    # (3) Merging game lists and standardizing location strings
    merged_list = merge_game_lists(collections)
    print(len(merged_list))

    latest_infos = retrieve_game_batch_information(merged_list)
main()