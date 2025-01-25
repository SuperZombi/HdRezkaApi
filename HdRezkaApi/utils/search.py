import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class HdRezkaSearch:
	def __init__(self, origin, proxy={}, headers={}, cookies={}):
		uri = urlparse(origin)
		self.url = f'{uri.scheme}://{uri.netloc}/engine/ajax/search.php'
		self.proxy = proxy
		self.cookies = cookies
		self.HEADERS = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
			**headers
		}

	def __call__(self, query):
		r = requests.post(self.url, data={'q': query}, headers=self.HEADERS, proxies=self.proxy, cookies=self.cookies)
		soup = BeautifulSoup(r.content, 'html.parser')
		results = []
		for item in soup.select('.b-search__section_list li'):
			title = item.find('span', class_='enty').get_text().strip()
			url = item.find('a').attrs['href']
			rating_span = item.find('span', class_='rating')
                    	rating = float(rating_span.find('i').text) if rating_span else None
			results.append({"title": title, "url": url, "rating": rating})
		return results
