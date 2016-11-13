from scrapkit.browser import Session

session = Session()
response = session.get('http://www.facebook.com')
print response.content
