import json
import os.path
from typing import List

import simplejson

from modules.data.game import Game


class GameImporterExporter:
    def __init__(self, directory: str):
        self.directory = directory

    # Transforms the object into JSON and writes the JSON file to the file system
    # The initial data is kept in classes to enforce data structures/types,
    # and make accessing/processing properties easier.
    def write_game_file(self, file_name: str, games: List[Game]):
        output_path = os.path.abspath(os.path.join(self.directory, file_name))
        # turns the class object into a valid JSON string, even though the format is not ideal at this stage
        output_json = '['
        for game in games:
            output_json += json.dumps(game.__dict__)
            output_json += ','
        # at the end of the JSON array no more ',' is needed
        output_json = output_json[:-1]
        output_json += ']'
        with open(output_path, 'w') as output_file:
            # creates a properly formatted JSON array and prints it to a file
            output_file.write(simplejson.dumps(simplejson.loads(output_json), indent=4, sort_keys=True))


    # Reads the game list in JSON format, so it can be forwarded via REST API
    def read_game_file(self, file_name: str) -> str:
        input_path = os.path.join(self.directory, file_name)
        input_json = ""
        with open(input_path, "r") as input_file:
            input_json = json.loads(input_file.read())
        return input_json
