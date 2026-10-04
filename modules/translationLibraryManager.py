import json
import logging
import simplejson


class TranslationLibraryManager:

    def __init__(self, translation_library_file):
        self.translation_library_file = translation_library_file
        self.translation_library = None

    # Read the JSON file with previous translations
    def load_library(self):
        if self.translation_library is None:
            print("Loading library ...")
            file_content = ''
            with open(self.translation_library_file, "r") as input_file:
                file_content = input_file.read()
            self.translation_library= json.loads(file_content) if file_content else []
            print(f"Loaded %s games", len(self.translation_library))
        else:
            logging.debug('Library already loaded. Skipping action.')

    # Update the JSON file with the given translations
    def persist_library(self):
        print("Persisting translation library")
        with open(self.translation_library_file, 'w') as output_file:
            output_file.write(simplejson.dumps(self.translation_library, indent=4, sort_keys=True))
            output_file.flush()
            output_file.close()

    """
    Returns translation if available
    Returns empty string if
      - not available
      - new entry
      - description changes detected
    Adds missing entries automatically
    Updates outdated descriptions automatically
    """
    # game ID = numeric value inside a JSON string
    def get_translation(self, game_id: str, target_language_code: str):
        translation = ''
        for entry in self.translation_library:
            if entry['id'] == game_id:
                translation = entry['translation' + target_language_code] # e.g. translationDE
        return translation

    """
    Checks if an entry in the translation library exists for a given game id. If so, the next step
    is to check if the description is available and/or has been modified ever since creating the
    original entry. Since an original entry can be created without a translation (e.g. when running
    out of AI credits, and/or to allow for manual translation), the translation entry is checked for
    its value. If the string is empty, a translation is required. Otherwise, the existing translation
    is considered sufficient.
    """
    def requires_modification(self, game_id: str, game_description: str, target_language_code: str):
        modify = True # modify/add if not in list
        for entry in self.translation_library:
            # game in list & properties present
            if 'id' in entry and 'description' in entry:
                # no modification needed if descriptions match
                # why the check? If the English descriptions match, there was no change and there is no need for a German translation
                if entry['id'] == game_id and entry['description'] == game_description:
                    # check if translation present
                    modify = entry['translation' + target_language_code] == ""
        return modify

    """
    Adds a new entry to the in memory translation library.
    Need to manually persist to also update the file. This is intentional for less disk writes and better performance.
    """
    def add_translation(self, game_id: str, game_name: str, game_description: str, game_translation: str, target_language_code: str):
        entry_exists = False
        for entry in self.translation_library:
            if not entry_exists and entry['id'] == game_id:
                entry['name'] = game_name
                entry['description'] = game_description
                entry['translation' + target_language_code] = game_translation
                entry_exists = True
        if not entry_exists:
            entry = {
                'id': game_id,
                'name': game_name,
                'description': game_description,
                'translation'+target_language_code: game_translation
            }
            self.translation_library.append(entry)
