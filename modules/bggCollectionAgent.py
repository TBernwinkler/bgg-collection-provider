import requests
import time
import xmltodict

from modules.data.connection import ConnectionProperties


class BggCollectionAgent:
    def __init__(self):
        self.collection_path='/xmlapi2/collection'
        self.batch_path='/xmlapi2/thing'
        self.internal_api_path = '/bgg-internal-json-api/api/geekitems'
        self.waiting_time = 10 #seconds
        self.too_many_requests_waiting = 60 #seconds

    def _make_bgg_request(self, request_string: str, authorization: str):
        headers = {'Authorization': 'Bearer ' + authorization}
        bgg_response = requests.get(request_string, headers=headers)
        while bgg_response.status_code == 202:
            # Waiting for 10s for BGG to get the content ready
            print ("Received status code 202. BGG list not ready, yet.")
            print (f"Waiting { str(self.waiting_time) } seconds before trying again.")
            time.sleep(self.waiting_time)
            bgg_response = requests.get(request_string, headers=headers)

        iteration = 0
        while bgg_response.status_code == 429 and iteration < 10:
            print (f"Hit the request limit. Waiting for {str((iteration + 1) * self.too_many_requests_waiting)} seconds.")
            time.sleep((iteration + 1) * self.too_many_requests_waiting)
            bgg_response = requests.get(request_string, headers=headers)
            iteration += 1

        # Proceeding once the status code is not/no longer 202
        if bgg_response.status_code == 200:
            print ('OK. BGG request completed: ' + request_string)
            return xmltodict.parse(bgg_response.text)
        else:
            print ('BGG request failed. The failing request was sent and failed:')
            print (request_string)
            raise Exception(f"Non-success status code: {bgg_response.status_code}")


    def get_collection(self, bgg_username: str, connection: ConnectionProperties):
        request_string = (connection.server_address
                          + self.collection_path + '?'
                          + 'username=' + bgg_username
                          + '&minbggrating=""'
                          + '&type=boardgame'
                          + '&excludesubtype=boardgameexpansion'
                          + '&own=1'
                          + '&version=1'
                          + '&stats=1')
        return self._make_bgg_request(request_string, connection.api_key)


    def request_batch_information(self, game_ids: str, connection: ConnectionProperties):
        request_string = (connection.server_address
                          + self.batch_path + '?'
                          + 'id=' + game_ids
                          + '&stats=1')
        return self._make_bgg_request(request_string, connection.api_key)
