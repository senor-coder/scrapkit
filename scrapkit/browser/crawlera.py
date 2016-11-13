import warnings

import requests
from random import choice

from requests.auth import HTTPBasicAuth
from requests.auth import HTTPProxyAuth
from debugger import debug

PROXY_HOST = "proxy.crawlera.com"
PROXY_PORT = "8010"

PROXIES = {
    "https": "https://{}:{}/".format(PROXY_HOST, PROXY_PORT),
    "http": "http://{}:{}/".format(PROXY_HOST, PROXY_PORT)
}

DEFAULT_TIMEOUT = 100
TIMEOUT = 100
REDIRECT_CODES = [301, 302, 303, 307]


class SessionCreateException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, 'ERROR CREATING A NEW CRAWLERA SESSION: ' + msg)


class SessionDestroyException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, 'ERROR DESTROYING SESSION: ' + msg)


class CrawleraSession():
    def __init__(self, api_key, user_agent=None, cert='crawlera-ca.crt', debug=False, max_tries=3):
        requests.Session.__init__(self)
        self.api_key = api_key
        self.user_agent = user_agent
        self.cert = cert
        self.debug = debug
        self.session = requests.session()
        self.max_tries = max_tries
        self.cookies = self.session.cookies
        self.proxy_auth = HTTPProxyAuth(api_key, "")
        self.server_auth = HTTPBasicAuth(api_key, "")
        self.__create_session();

    def __create_session(self):
        url = "http://proxy.crawlera.com:8010/sessions"
        response = requests.post(url, auth=self.server_auth, timeout=TIMEOUT, verify=self.cert)
        if response.status_code == 200:
            self.session_id = response.text
            self.session.headers["X-Crawlera-Session"] = response.text
            self.session.headers["Referer"] = "http://www.cdnplanet.com/tools/cdnfinder/"
            if self.user_agent is not None:
                self.session.headers['X-Crawlera-UA'] = 'pass'
                self.session.headers['User-agent'] = self.user_agent
        else:
            raise Exception("Problem creating session. RESPONSE CODE: " + str(response.status_code))

    def clear(self):
        self.__create_session()

    def head(self, url, **kwargs):
        while True:
            response = self.session.head(self, url, **kwargs)
            if response.status_code in REDIRECT_CODES:
                if 'location' in response.headers:
                    url = response.headers['location']

            else:
                return url

    @debug
    def get(self, url, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            params = {
                'proxies': PROXIES,
                'auth': self.proxy_auth,
                'timeout': TIMEOUT,
                'verify': self.cert,
                'allow_redirects': False
            }
            params.update(kwargs)
            for i in xrange(self.max_tries):
                response = self.session.get(url, **params)
                if response.status_code in REDIRECT_CODES:
                    if 'location' in response.headers:
                        url = response.headers['location']
                else:
                    return response

    @debug
    def post(self, url, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                params = {
                    'proxies': PROXIES,
                    'auth': self.proxy_auth,
                    'timeout': TIMEOUT,
                    'verify': self.cert,
                    'allow_redirects': False
                }
                params.update(kwargs)
                for i in xrange(self.max_tries):
                    response = self.session.post(url, **params)
                    if response.status_code in REDIRECT_CODES:
                        if 'location' in response.headers:
                            url = response.headers['location']
                    else:
                        return response

    def destroy(self):
        url = "http://proxy.crawlera.com:8010/sessions/" + self.session_id
        response = requests.delete(url, auth=self.server_auth, timeout=TIMEOUT, verify=self.cert)
        if response.status_code != 204:
            raise Exception("Problem destroying session. RESPONSE CODE: " + self.status_code)

    def get_all_sessions(self):
        url = "http://proxy.crawlera.com:8010/sessions"
        response = requests.get(url, auth=self.server_auth, verify=self.cert)
        if response.status_code != 200:
            raise Exception("Problem destroying session. RESPONSE CODE: " + self.status_code)
        return response.json()

    def clear_all_session(self):
        url = "http://proxy.crawlera.com:8010/sessions"
        response = requests.get(url, auth=self.server_auth, verify=self.cert)
        if response.status_code != 200:
            raise Exception("Problem destroying session. RESPONSE CODE: " + self.status_code)
        sessions = response.json()
        for session in sessions.keys():
            url = "http://proxy.crawlera.com:8010/sessions/" + session
            response = requests.delete(url, auth=self.server_auth, timeout=TIMEOUT, verify=self.cert)
            if response.status_code != 204:
                raise Exception("Problem destroying session. RESPONSE CODE: " + self.status_code)


class Crawlera:
    def __init__(self, api_key, user_agent=None, cert='crawlera-ca.crt', log=False):
        self.user_agent = user_agent
        self.api_key = api_key
        self.cert = cert
        self.log = log
        self.proxy_auth = HTTPProxyAuth(self.api_key, "")

    def get(self, url):
        return requests.get(url, proxies=PROXIES, auth=self.proxy_auth, timeout=TIMEOUT, verify=self.cert)

    def get_session(self):
        return CrawleraSession(self.api_key, self.user_agent)

    def post(self, url, data):
        response = requests.post(url, proxies=PROXIES, auth=self.proxy_auth, data=data, timeout=TIMEOUT,
                                 verify=self.cert)
        return response


class RandomizedCrawlera(Crawlera):
    def __init__(self, api_keys, user_agent=None, cert='crawlera-ca.crt', log=False):
        Crawlera.__init__(self, choice(api_keys), user_agent=user_agent, cert=cert, log=log)
        self.api_keys = api_keys

    def get(self, url, **kwargs):
        self.api_key = choice(self.api_keys)
        return super(RandomizedCrawlera, self).get(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        self.api_key = choice(self.api_keys)
        return super(RandomizedCrawlera, self).post(url, data, json, **kwargs)


def log_response_info(response):
    print response.status_code, ' ', response.request.url
