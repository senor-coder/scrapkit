from functools import wraps


def debug(http_method_func):
    @wraps(http_method_func)
    def log(instance, *args, **kwargs):
        response = http_method_func(instance, *args, **kwargs)
        if instance.debug:
            with open('log.html', 'wb') as html:
                html.write(response.text.encode('UTF-8'))
        return response

    return log


from browser import *
from crawlera import *
