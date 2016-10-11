from bs4 import BeautifulSoup, Comment
import json


class ExtremeSoup(BeautifulSoup):
    def __init__(self, *args, **kwargs):
        BeautifulSoup.__init__(self, *args, **kwargs)

    def get_all_comments(self):
        return self.findAll(text=lambda text: isinstance(text, Comment))

    def find(self, name=None, attrs={}, recursive=True, text=None, default=None, procedure=None, keys=[], **kwargs):
        result = super(ExtremeSoup, self).find(name, attrs, recursive, text, **kwargs)

        if result is not None:
            for key in keys:
                if not result.has_attr(key):
                    return default

            result.__class__ = ExtremeSoup
            if procedure is not None:
                return procedure(result)
            return result

        return default

    def find_next_sibling(self, name=None, attrs={}, text=None, default=None, procedure=None, keys=[], **kwargs):
        result = super(ExtremeSoup, self).find(name, attrs, text, **kwargs)
        if result is not None:
            for key in keys:
                if not result.has_attr(key):
                    return default

            result.__class__ = ExtremeSoup
            if procedure is not None:
                return procedure(result)
            return result
        return default

    def find_all(self, name=None, attrs={}, recursive=True, text=None,
                 limit=None, **kwargs):
        results = super(ExtremeSoup, self).find_all(name, attrs, recursive, text, limit, **kwargs)
        for result in results:
            result.__class__ = ExtremeSoup
        return results

    def find_in_comments(self, *args, **kwargs):
        for comment in self.get_all_comments():
            soup = ExtremeSoup(comment)
            result = soup.find(*args, **kwargs)
            if result is not None:
                return result
        return None

    def form_details(self, *args, **kwargs):
        payload = {}
        form = self.find('form', *args, **kwargs)
        if form is None:
            return None
        for input in form.find_all('input'):
            try:
                payload[input['name']] = input['value']
            except KeyError:
                continue
        try:
            return form['action'], payload
        except KeyError:
            return '', payload

    def find_form_in_comments(self, predicate):
        payload = {}
        form = None
        for comment in self.get_all_comments():
            soup = ExtremeSoup(comment)
            for tag_item in soup.find_all('form'):
                if predicate(tag_item):
                    form = tag_item
                    break
        if form is None:
            return None
        for input in form.find_all('input'):
            try:
                payload[input['name']] = input['value']
            except KeyError:
                continue
        try:
            return form['action'], payload
        except KeyError:
            return '', payload

    def scripts(self):
        return self.find_all('script')

    def script_jsons(self, predicate=None):
        scripts = [x.text for x in self.scripts()]
        jsons = []
        for script in scripts:
            try:
                start = script.index('{')
                end = script.rindex('}')
                probable_json_string = script[start:end + 1]
                json_data = json.loads(probable_json_string)
                jsons.append(json_data)
            except ValueError:
                continue
        if predicate is not None:
            return filter(predicate, jsons)
        return jsons
