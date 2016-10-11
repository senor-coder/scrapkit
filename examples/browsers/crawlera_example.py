from pybrowser.crawlera import CrawleraSession

url = 'https://twitter.com'
# Assuming that crawlera-ca.crt is in the working directory. Else specify the path for cert parameter
# to set certificate path, pass cert = /path/to/crawlera-ca.crt
session = CrawleraSession('API_KEY')
r = session.get(url)

print("""
Requesting [{}]
Request Headers:
{}
Response Time: {}
Response Code: {}
Response Headers:
{}
Response Url: {}
""".format(url, r.request.headers, r.elapsed.total_seconds(),
           r.status_code, r.headers, r.url))
