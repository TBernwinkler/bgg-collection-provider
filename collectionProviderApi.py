from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os.path
import json

from modules.validation.requestValidator import RequestValidator

app = Flask(__name__)
validator = RequestValidator()
CORS(app, origins=validator.get_allowed_origins())

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
    if file_name != '' and os.path.isfile(file_name):
        with open(file_name, "r") as input_file:
            game_list = json.loads(input_file.read())
        return game_list
    else:
        return '{ "Error": "Not files for the last 10 days." }'



@app.get("/games")
def get_games():
    if validator.authorize(request):
        return jsonify(get_game_list())
    return make_response("Access denied.", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

# LOCAL
# app.run('0.0.0.0', 8081)

# SERVER
app.run('0.0.0.0', 80)
