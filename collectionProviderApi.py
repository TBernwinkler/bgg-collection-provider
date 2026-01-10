from flask import Flask, jsonify
from datetime import datetime, timedelta
import os.path
import json

app = Flask(__name__)

file_directory = 'game_lists'
file_pattern = 'Paradice-BGG-list-'

def get_game_list() -> str:
    game_list = ''

    today_date = datetime.today().strftime('%Y-%m-%d')
    file_name = file_directory + '/' + file_pattern + today_date + '.json'

    prior_days = 0
    while not os.path.isfile(file_name) and prior_days < 10:
        prior_days += 1
        target_date = (datetime.today() - timedelta(days=prior_days)).strftime('%Y-%m-%d')
        file_name = file_directory + '/' + file_pattern + target_date + '.json'
    if file_name != '':
        with open(file_name, "r") as input_file:
            game_list = json.loads(input_file.read())
        return game_list
    else:
        return '{ "Error": "Not files for the last 10 days." }'


@app.get("/game_list")
def get_countries():
    return jsonify(get_game_list())

app.run('0.0.0.0', 8081)
