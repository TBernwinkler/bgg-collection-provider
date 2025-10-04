import json

import requests
import time
import xmltodict


class BggCollectionAgent:
    def __init__(self):
        self.base_url="https://boardgamegeek.com/xmlapi2/collection"
        self.batch_url="https://boardgamegeek.com/xmlapi2/thing"
        self.waiting_time = 10 #seconds

    def _make_bgg_request(self, request_string: str):
        bgg_response = requests.get(request_string)
        while bgg_response.status_code == 202:
            # according to documentation, waiting for 5s is required to be safe
            print ("Received status code 202. BGG list not ready, yet.")
            print ("Waiting 5s before trying again.")
            time.sleep(self.waiting_time)
            bgg_response = requests.get(request_string)

        # Proceeding once the status code is not/no longer 202
        if bgg_response.status_code == 200:
            print ('OK. BGG request completed: ' + request_string)
            return xmltodict.parse(bgg_response.text)
        else:
            print ('BGG request failed. The failing request was sent and failed:')
            print (request_string)
            raise Exception(f"Non-success status code: {bgg_response.status_code}")


    def get_collection(self, bgg_username: str):
        request_string = self.base_url + '?' \
                                     + 'username=' + bgg_username \
                                     + '&minbggrating=""' \
                                     + '&type=boardgame' \
                                     + '&excludesubtype=boardgameexpansion' \
                                     + '&own=1' \
                                     + '&version=1' \
                                     + '&stats=1'
        return self._make_bgg_request(request_string)


    def request_batch_information(self, game_ids: str):
        request_string = self.batch_url + '?' \
                            + 'id=' + game_ids \
                            + '&stats=1'
        return self._make_bgg_request(request_string)