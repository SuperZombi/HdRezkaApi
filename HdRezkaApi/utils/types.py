from bs4 import BeautifulSoup

class BeautifulSoupCustom(BeautifulSoup):
	def __repr__(self): return "<HTMLDocument>"

class HdRezkaType():
	def __init__(self, name):
		self.name = name
	def __str__(self):
		return self.name
	def __eq__(self, other):
		return self.__class__ == other.__class__ or self.__class__ == other or self.name == other

class HdRezkaTVSeries(HdRezkaType):
	def __init__(self):
		super().__init__("tv_series")
class HdRezkaMovie(HdRezkaType):
	def __init__(self):
		super().__init__("movie")


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
