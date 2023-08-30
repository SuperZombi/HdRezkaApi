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
