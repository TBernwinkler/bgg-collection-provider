from typing import List

"""
The class is used the logical container for both
- game mechanics filter
- game theme filter
as the structure and way of processing are identical.
"""
class FilterReference:
    def __init__(self, category: str, selectors: List[str]):
        self.category = category
        self.selectors = selectors

    # todo: implement this one
    def is_in_category(self, game_mechanics: List[str]) -> bool:
        for selector in self.selectors:
            for mechanic in game_mechanics:
                print ("Open todo!")
        return False
