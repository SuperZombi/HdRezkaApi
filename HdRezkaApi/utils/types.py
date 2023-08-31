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
	def __init__(self, value, votes):
		self.value = value
		self.votes = votes
	def __str__(self):
		return f"{self.value} ({self.votes})"
	def __repr__(self):
		return f"<HdRezkaRating(value:{self.value}, votes:{self.votes})>"

	def __float__(self):
		return float(self.value)

	def __gt__(self, other):
		return self.value > other.value
	def __lt__(self, other):
		return self.value < other.value
	def __ge__(self, other):
		return self.value >= other.value
	def __le__(self, other):
		return self.value <= other.value
	def __eq__(self, other):
		return self.value == other.value
