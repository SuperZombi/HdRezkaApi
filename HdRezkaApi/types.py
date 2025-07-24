from bs4 import BeautifulSoup

class BeautifulSoupCustom(BeautifulSoup):
	def __repr__(self): return "<HTMLDocument>"

default_cookies = {
	"hdmbbs": "1"
}
default_headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

class HdRezkaType():
	def __init__(self, name, type):
		self.name = name
		self.type = type
	def __str__(self):
		return f"{self.type}.{self.name}"
	def __repr__(self): return str(self)
	def __eq__(self, other):
		return self.__class__ == other.__class__ or self.__class__ == other or self.name == other

class HdRezkaFormat(HdRezkaType):
	def __init__(self, name):
		super().__init__(name, "format")
class HdRezkaCategory(HdRezkaType):
	def __init__(self, name):
		super().__init__(name, "category")


class TVSeries(HdRezkaFormat):
	def __init__(self): super().__init__("tv_series")
class Movie(HdRezkaFormat):
	def __init__(self): super().__init__("movie")


class Film(HdRezkaCategory):
	def __init__(self): super().__init__("film")
class Series(HdRezkaCategory):
	def __init__(self): super().__init__("series")
class Cartoon(HdRezkaCategory):
	def __init__(self): super().__init__("cartoon")
class Anime(HdRezkaCategory):
	def __init__(self): super().__init__("anime")


class HdRezkaRating():
	def __init__(self, value:float, votes:int):
		self.value = value
		self.votes = votes
	def __str__(self): return f"{self.value} ({self.votes})"
	def __repr__(self): return f"<HdRezkaRating({self.value})>"

	def __float__(self): return float(self.value)
	def __int__(self): return int(self.value)

	def __gt__(self, other):
		return self.value > other.value
	def __lt__(self, other):
		return self.value < other.value
	def __ge__(self, other):
		return self.value >= other.value
	def __le__(self, other):
		return self.value <= other.value
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.value == other.value
		return self.value == other

class HdRezkaEmptyRating(HdRezkaRating):
	def __init__(self):
		super().__init__(value=None, votes=None)
	def __str__(self): return f"HdRezkaRating(Empty)"
	def __repr__(self): return f"<HdRezkaEmptyRating>"
	def __float__(self): return 0
	def __int__(self): return 0
	def __bool__(self): return False

	def __gt__(self, other): return False                          # >
	def __lt__(self, other): return True if other.value else False # <
	def __ge__(self, other): return False if other.value else True # >=
	def __le__(self, other): return True if other.value else False # <=


default_translators_priority = [
	56, # Дубляж
	105, # StudioBand
	111, # HDrezka Studio
]
default_translators_non_priority = [
	238, # Оригинал + субтитры
]
