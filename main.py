from typing import List
from datetime import datetime

import openai
from deepl import QuotaExceededException

from modules.configLoader import ConfigLoader
from modules.bggCollectionAgent import BggCollectionAgent
from modules.bggContentProcessor import ContentProcessor, Game
from modules.data.filterReference import FilterReference
from modules.gameImporterExporter import GameImporterExporter
from modules.gameListMerger import LocationManager
from modules.data.collection import CollectionConfig, GameCollection
from modules.data.connection import ConnectionProperties

import deepl

from modules.translationLibraryManager import TranslationLibraryManager


# Reads json config files and transforms them into class objects for easier interaction.
# This get the application ready for all subsequent tasks.
def initialize():
    loader = ConfigLoader()
    collection_config_list: List[CollectionConfig] = loader.read_collections_config()
    connections_config_list: List[ConnectionProperties] = loader.read_connections_config()
    return collection_config_list, connections_config_list


# Returns the target connection based on a name filter
def get_connection(connections: List[ConnectionProperties], name: str):
    for item in connections:
        if item.name == name:
            return item
    return None

# BGG public API call
# Retrieves the list of games for a particular BGG username
def retrieve_collection(collection_user_name: str, bgg_connection: ConnectionProperties):
    agent = BggCollectionAgent()
    return agent.get_collection(collection_user_name, bgg_connection)


# Process data and filter accordingly
def process_raw_content(raw_content_file):
    processor = ContentProcessor()
    return processor.process_game_list(raw_content_file)


# Merge game lists and standardize location strings
def merge_game_lists(collections: List[GameCollection]) -> List[Game]:
    all_games: List[Game] = []
    location_manager = LocationManager()
    for collection in collections:
        # no filter for duplicate games due to different locations
        all_games = (all_games + location_manager.streamline_location_strings(
                                 collection.collection_config.filters, collection.games))
    return all_games


# Send requests to the BGG API to retrieve more game details
# The details are requested in batches, each response provides details for multiple games at once
def aggregate_game_infos(game_list: List[Game], game_mechanics: List[FilterReference],
                         game_themes: List[FilterReference], connection: ConnectionProperties):
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
        game_list = processor.enrich_bulk_information(game_list, agent.request_batch_information(batch_ids, connection),
                                                      game_mechanics, game_themes)
        index += batch_size
    # finish the rest which may be less than a full batch_size
    if index <= len(game_list) < (index + batch_size):
        final_batch = game_list[index:]
        batch_id_list = []
        for element in final_batch:
            batch_id_list.append(element.id)
        batch_ids = ",".join(batch_id_list)
        game_list = processor.enrich_bulk_information(game_list, agent.request_batch_information(batch_ids, connection),
                                                      game_mechanics, game_themes)
    return game_list

def read_filter_categories():
    loader = ConfigLoader()
    return loader.read_game_mechanics_config(), loader.read_game_themes()

# Translates and rephrases the game descriptions of all games to
# - standardize English game descriptions
# - provide German game descriptions
# - WARNING: Rate limit = 500.000 characters/month, which is reached in no time with 1000+ games
def standardize_descriptions(games: List[Game], connection: ConnectionProperties) -> List[Game]:
    deepl_client = deepl.DeepLClient(connection.api_key)
    library_file_path = 'translations/translationLibrary.json'
    target_language_code = 'DE'
    translation_lib_manager = TranslationLibraryManager(translation_library_file=library_file_path)
    translation_lib_manager.load_library()

    reached_ai_quota = False
    for game in games:
        translation = translation_lib_manager.get_translation(game.id, target_language_code)
        if translation == '' or translation_lib_manager.requires_modification(game.id, game.descriptions[target_language_code], target_language_code):
            if not reached_ai_quota:
                try:
                    translation = deepl_client.translate_text(game.descriptions.get('EN'), target_lang=target_language_code)
                    print("Translated description for game: " + game.name)
                except QuotaExceededException:
                    # write all changes to the library file; no further translations possible due to quota
                    translation_lib_manager.persist_library()
                    reached_ai_quota = True
                except TypeError:
                    print('Translation error happened for [' + game.id + '] ' + game.name)
                    # write all changes to the library file; saves all successful translations
                    translation_lib_manager.persist_library()
                translation_lib_manager.add_translation(game.id, game.name, game.descriptions['EN'], translation, target_language_code)

        if target_language_code == 'DE':
            game.descriptions.update(DE=translation)
    translation_lib_manager.persist_library()
    return games


# Currently not used
def handle_chat_gpt_request(games: List[Game], connection: ConnectionProperties):
    openai.api_key = connection.api_key
    # iterate games, create a prompt
    prompt = ""
    # todo: magic
    # response = openai.Completion.create(
    #     model='text-davinci-003',
    #     prompt=prompt
    # )
    #
    # output = list()
    # for item in response['choices']:
    #     output.append(item['text'].strip())
    # todo: do something with the output
    return games

# offer API section
# TODO: implement the API to provide the JSON content from the file

def main():
    # (1) Reading config
    collection_config_list, connections_config_list = initialize()
    bgg_connection = get_connection(connections_config_list, 'BGG')
    # (2) Requesting BGG lists and processing data (select relevant information)
    collections: List[GameCollection] = []
    for collection in collection_config_list:
        print ("Processing BGG collection for username: " + collection.bgg_name)
        game_collection_dict = retrieve_collection(collection.bgg_name, bgg_connection)
        collections.append(GameCollection(collection_config=collection, games=process_raw_content(game_collection_dict)))

    # (3) Merging game lists and standardizing location strings
    merged_list = merge_game_lists(collections)

    # (4) Load local game mechanics and theme category definitions
    game_mechanics, game_themes = read_filter_categories()

    # (5) Data aggregation / data enrichment based on additional BGG requests information,
    #     filter criterion categories, and pre-defined classification
    game_list = aggregate_game_infos(merged_list, game_mechanics, game_themes, bgg_connection)


    # (6) standardize & translate game descriptions; involves LLMs (AI)
    deepl_connection = get_connection(connections_config_list, 'DeeplAI')
    standardize_descriptions(game_list, deepl_connection)

    # (?) Write game list to a JSON file
    # The output is used for the API; also serves for the purpose of testing/checking the final values
    exporter = GameImporterExporter('./game_lists/')
    today_date = datetime.today().strftime('%Y-%m-%d')
    exporter.write_game_file('Paradice-BGG-list-' + today_date + '.json', game_list)


main()