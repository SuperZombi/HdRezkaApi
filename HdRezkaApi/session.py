from urllib.parse import urlparse
from .api import HdRezkaApi
from .search import HdRezkaSearch
from .types import default_cookies, default_headers
from .types import default_translators_priority, default_translators_non_priority


class HdRezkaSession:
	def __init__(self, origin="", proxy={}, headers={}, cookies={},
		translators_priority=None, translators_non_priority=None
	):
		self.origin = None
		if origin:
			uri = urlparse(origin)
			self.origin = f'{uri.scheme}://{uri.netloc}'
		self.proxy = proxy
		self.cookies = {**default_cookies, **cookies}
		self.HEADERS = {**default_headers, **headers}
		self._translators_priority = translators_priority or default_translators_priority
		self._translators_non_priority = translators_non_priority or default_translators_non_priority

	def __enter__(self): return self
	def __exit__(self, type, value, traceback): pass

	@property
	def translators_priority(self):
		return self._translators_priority

	@translators_priority.setter
	def translators_priority(self, value):
		self._translators_priority = value or []

	@property
	def translators_non_priority(self):
		return self._translators_non_priority

	@translators_non_priority.setter
	def translators_non_priority(self, value):
		self._translators_non_priority = value or []

	def login(self, email:str, password:str, **kwargs):
		if not self.origin: raise ValueError("For login origin is required")
		rezka = HdRezkaApi(self.origin,headers=self.HEADERS,proxy=self.proxy)
		if rezka.login(email=email, password=password, **kwargs):
			self.cookies = {**self.cookies,**rezka.cookies}
			return True

	def get(self, url, **kwargs):
		if self.origin:
			uri = urlparse(url)
			url = self.origin+"/"+uri.path.lstrip("/")
		rezka = HdRezkaApi(url, **{
			"proxy": self.proxy,
			"headers": self.HEADERS,
			"cookies": self.cookies,
			"translators_priority": self._translators_priority,
			"translators_non_priority": self._translators_non_priority,
			**kwargs
		})
		if rezka.ok: return rezka
		else: raise rezka.exception

	def search(self, query, find_all=False):
		if not self.origin: raise ValueError("For search origin is required")
		return HdRezkaSearch(self.origin,proxy=self.proxy,headers=self.HEADERS,cookies=self.cookies)(query, find_all=find_all)
