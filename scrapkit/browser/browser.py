import requests

from random import *

from urlparse import urlparse
from useragents import *
from debugger import debug

REDIRECT_CODES = [301, 302, 303, 307]


def header_generator(host=None, user_agent=None):
    header = {
        'User-Agent': choice(USER_AGENTS),
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    if user_agent is not None:
        header['User-Agent'] = user_agent

    if host is not None:
        header["Host"] = host

    return header


def get_host(url):
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain


class Session(requests.Session):
    def __init__(self, user_agent=None, headers=None, timeout=None, proxies={}, debug=False):
        requests.Session.__init__(self)
        self.debug = debug
        self.timeout = timeout
        self.proxies.update(proxies)
        self.user_agent = choice(USER_AGENTS) if user_agent is None else user_agent
        if headers is None:
            self.headers = header_generator(user_agent=self.user_agent)
        else:
            headers['User-Agent'] = self.user_agent

    def clear(self):
        self = Session(self.user_agent, self.headers, self.timeout, self.proxies, self.debug)

    @debug
    def get(self, url, *args, **kwargs):
        self.headers["Host"] = get_host(url)
        response = super(Session, self).get(url, *args, **kwargs)
        return response

    @debug
    def post(self, url, data=None, json=None, **kwargs):
        self.headers["Host"] = get_host(url)
        response = super(Session, self).post(url, data=data, json=json, **kwargs)
        return response


class ProxySession(Session):
    def __init__(self, user_agent=None, headers=None, timeout=None, proxies={}, manual_redirects=True, debug=False):
        Session.__init__(self, user_agent, headers, timeout, proxies, debug)
        self.manual_redirects = manual_redirects

    def clear(self):
        self = Session(self.user_agent, self.headers, self.timeout, self.proxies, self.debug)

    @debug
    def get(self, url, **kwargs):
        self.headers["Host"] = get_host(url)
        if self.manual_redirects:
            kwargs['allow_redirects'] = False
        response = super(ProxySession, self).get(url, **kwargs)

        if self.manual_redirects:
            while response.status_code in REDIRECT_CODES:
                if 'location' in response.headers:
                    url = response.headers['location']
                    response = super(ProxySession, self).get(url, **kwargs)
                else:
                    return response
        return response

    @debug
    def post(self, url, **kwargs):
        if self.timeout is not None:
            kwargs['timeout'] = self.timeout
        self.headers["Host"] = get_host(url)
        if self.manual_redirects:
            kwargs['allow_redirects'] = False
        response = super(ProxySession, self).post(url, **kwargs)

        if self.manual_redirects:
            while response.status_code in REDIRECT_CODES:
                if 'location' in response.headers:
                    url = response.headers['location']
                    response = super(ProxySession, self).get(url, **kwargs)
                else:
                    return response
        return response


class Browser:
    def __init__(self, timeout=None, debug=False):
        self.debug = debug
        self.timeout = timeout

    @debug
    def get(self, url, **kwargs):
        if self.timeout is not None:
            kwargs['timeout'] = self.timeout
        response = requests.get(url, headers=header_generator(get_host(url)), **kwargs)
        return response

    def get_session(self, *args, **kwargs):
        return Session(*args, **kwargs)

    @debug
    def post(self, url, data=None, json=None, **kwargs):
        if self.timeout is not None:
            kwargs['timeout'] = self.timeout
        headers = header_generator(get_host(url))
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            kwargs.pop('headers')
        response = requests.post(url, data=data, json=json, headers=headers, **kwargs)
        return response
