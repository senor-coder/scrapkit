from pybrowser.browser import ProxySession

proxies = {
    'http': 'http://89.32.179.116:1200',
    'https': 'https://89.32.179.116:1200'
}

session = ProxySession(proxies=proxies)
response = session.get('http://httpbin.org/ip')

print 'FINAL: ', response.status_code
