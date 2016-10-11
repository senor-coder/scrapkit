import json

from .exceptions import *


class DictionarySoup:
    def __init__(self, object, strict=False):
        self.json_object = object if isinstance(object, (dict, list)) else json.loads(str(object), strict=strict)

    def find_all(self, search_key=None, predicate=None, recursive=False):
        results = []
        stack = [self.json_object]

        if search_key is None and predicate is None:
            raise InsufficientParamsException('Both search_key and predicate are None.')

        while len(stack) > 0:
            json_object = stack.pop()
            hit = False

            if isinstance(json_object, (dict, list)):

                if predicate is not None and predicate(json_object):
                    if search_key is not None and search_key in json_object:
                        results.append(json_object[search_key])
                        hit = True
                    else:
                        results.append(json_object)
                        hit = True

                elif search_key is not None:
                    if search_key in json_object:
                        results.append(json_object[search_key])
                        hit = True

                if hit and not recursive:
                    continue

                if isinstance(json_object, dict):
                    stack.append(json_object.values())
                else:
                    stack.extend(json_object)
        return results

    def find(self, search_key=None, predicate=None, default=None):
        stack = [self.json_object]

        if search_key is None and predicate is None:
            raise InsufficientParamsException('Both key and predicate are None.')

        while len(stack) > 0:
            json_object = stack.pop()

            if isinstance(json_object, (dict, list)):

                if predicate is not None and predicate(json_object):
                    if search_key is not None and search_key in json_object:
                        return json_object[search_key]
                    else:
                        return json_object
                elif search_key is not None:
                    if search_key in json_object:
                        return json_object[search_key]

                if isinstance(json_object, dict):
                    stack.append(json_object.values())
                else:
                    stack.extend(json_object)
        return default
