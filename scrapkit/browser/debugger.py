from functools import wraps
import os

LOG_DIR = 'logs'
INCR = 1


def __create_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def debug(http_method_func):
    @wraps(http_method_func)
    def log(instance, *args, **kwargs):
        global INCR
        response = http_method_func(instance, *args, **kwargs)
        if instance.debug:
            __create_log_dir()
            with open(LOG_DIR + '/log' + str(INCR) + '.html', 'wb') as html:
                html.write(response.text.encode('UTF-8'))
                INCR += 1
            return response

    return log
