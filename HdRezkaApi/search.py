import requests
from bs4 import BeautifulSoup
from functools import lru_cache, cached_property
from urllib.parse import urlparse
from .types import default_cookies, default_headers
from .types import (HdRezkaCategory, Film, Series, Cartoon, Anime)
from .errors import HTTP, LoginRequiredError, CaptchaError


class HdRezkaSearch:
	def __init__(self, origin, proxy={}, headers={}, cookies={}):
		uri = urlparse(origin)
		self.origin = f'{uri.scheme}://{uri.netloc}'
		self.proxy = proxy
		self.cookies = {**default_cookies, **cookies}
		self.HEADERS = {**default_headers, **headers}

	def __call__(self, query, find_all=False):
		return self.advanced_search(query) if find_all else self.fast_search(query)

	def fast_search(self, query):
		r = requests.post(f'{self.origin}/engine/ajax/search.php', data={'q': query}, headers=self.HEADERS, proxies=self.proxy, cookies=self.cookies)
		if r.ok:
			soup = BeautifulSoup(r.content, 'html.parser')
			results = []
			for item in soup.select('.b-search__section_list li'):
				title = item.find('span', class_='enty').get_text().strip()
				url = item.find('a').attrs['href']
				rating_span = item.find('span', class_='rating')
				rating = float(rating_span.get_text()) if rating_span else None
				results.append({"title": title, "url": url, "rating": rating})
			return results
		raise HTTP(r.status_code, r.reason)

	def advanced_search(self, query):
		return SearchResult(self.origin, query, proxy=self.proxy, cookies=self.cookies, headers=self.HEADERS)


class SearchResult:
	def __init__(self, origin, query, proxy=None, headers=None, cookies=None):
		self.origin = origin
		self.query = query
		self.proxy = proxy
		self.headers = headers
		self.cookies = cookies
	def __str__(self): return f"SearchResult({self.query})"
	def __len__(self): return len(self.all_pages)

	def __iter__(self):
		self.current_page = 1
		return self
	def __next__(self):
		result = self.get_page(self.current_page)
		if result:
			self.current_page += 1
			return result
		raise StopIteration

	def __getitem__(self, key):
		if isinstance(key, int) and key >= 0:
			return self.get_page(key+1)
		return self.all_pages[key]

	@cached_property
	def all(self): return [item for page in self for item in page]
	@cached_property
	def all_pages(self): return [page for page in self]

	@lru_cache(maxsize=None)
	def get_page(self, page):
		data = {
			'do': 'search',
			'subaction': 'search',
			'q': self.query,
			'page': page
		}
		r = requests.get(f'{self.origin}/search/', params=data, headers=self.headers, proxies=self.proxy, cookies=self.cookies)
		if r.ok:
			soup = BeautifulSoup(r.content, 'html.parser')
			if soup.title.text == "Sign In": raise LoginRequiredError()
			if soup.title.text == "Verify": raise CaptchaError()
			items = soup.find_all(class_='b-content__inline_item')
			if len(items) > 0: return list(map(self.process_item, items))

	@classmethod
	def process_item(cls, item):
		link = item.find(class_='b-content__inline_item-link').find('a')
		cover = item.find(class_='b-content__inline_item-cover').find('img')
		url = link.attrs['href']
		title = link.text.strip()
		image = cover.attrs['src']
		cat = item.find(class_='cat')
		type_ = cls.detect_type(list(filter(lambda x:x!='cat',cat['class']))) if cat else None
		return {"title": title, "url": url, "image": image, "category": type_}

	@staticmethod
	def detect_type(classes):
		if 'films' in classes: return Film()
		if 'series' in classes: return Series()
		if 'cartoons' in classes: return Cartoon()
		if 'animation' in classes: return Anime()
		return HdRezkaCategory(classes[0])
