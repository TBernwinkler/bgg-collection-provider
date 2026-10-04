# bgg-collection-provider
This repository is split into two major logical blocks.

### Big Picture
Once this application is up and running, it is possible to connect a Frontend solution to the tool to guide you
through the list of games, and recommend games based on your personal preferences.


### Core Functionality
The core part loads, processes and stores data. It performs the following steps:
* Read configuration files (API keys, BGG accounts to access)
* Downloads the collections from the users
* Transforms the XML data into a meaningful JSON structure
* Enriches the basic data for more context
* Translates the descriptions to German through deepl AI
* Writes the final game list to a JSON file, that also holds the current date


### JSON REST API
The second part is an API that offers the above mentioned JSON file via (minimally) protected GET request.



## installation & execution
Installing the dependencies to run the Python application  
`pip install -r requirements.txt`

Generating a new game list JSON file  
`python ./main.py`

Running the API server that provides the JSON formated game list  
`python ./api/collectionProviderApi.py`

## Features
### Translation Library
Given that the amount of AI tokens for free use is limited, not all game descriptions can be translated in a single 
month. Rather than only having a fraction of the games descriptions translated to German, a translation library 
will store all translations that have been requested before. Only new entries and modified game descriptions will
be translated in subsequent iterations of the game processing steps. This approach will reduce the use of AI to
almost zero while tweaking the performance of the overall solution.
