from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os.path
import json

app = Flask(__name__)
CORS(app, origins=["https://bgg.paradice.wien", "https://brettspielomat.paradice.wien"])

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

def get_auth() -> dict:
    user = ''
    password = ''
    with open('basic-auth.conf', "r") as auth_file:
        for line in auth_file:
            if line.startswith('username'):
                user = line.split('=')[1].strip()
            elif line.startswith('password'):
                password = line.split('=')[1].strip()
        return { 'username': user.strip('"'), 'password': password.strip('"') }



@app.get("/games")
def get_games():
    credentials = get_auth()
    if (request.authorization and request.authorization.username == credentials['username']
            and request.authorization.password == credentials['password']):
        return jsonify(get_game_list())
    return make_response("Access denied.", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

app.run('0.0.0.0', 8081)
