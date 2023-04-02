import requests
from bs4 import BeautifulSoup
import base64
from itertools import product
import threading

class HdRezkaStreamSubtitles():
	def __init__(self, data, codes):
		self.subtitles = {}
		self.keys = []
		if data:
			arr = data.split(",")
			for i in arr:
				temp = i.split("[")[1].split("]")
				lang = temp[0]
				link = temp[1]
				code = codes[lang]
				self.subtitles[code] = {'title': lang, 'link': link}
			self.keys = list(self.subtitles.keys())
	def __str__(self):
		return str(self.keys)
	def __call__(self, id=None):
		if self.subtitles:
			if id:
				if id in self.subtitles.keys():
					return self.subtitles[id]['link']
				for key, value in self.subtitles.items():
					if value['title'] == id:
						return self.subtitles[key]['link']
				if str(id).isnumeric:
					code = list(self.subtitles.keys())[id]
					return self.subtitles[code]['link']
				raise ValueError(f'Subtitles "{id}" is not defined')
			else:
				return None

class HdRezkaStream():
	def __init__(self, season, episode, subtitles={}):
		self.videos = {}
		self.season = season
		self.episode = episode
		self.subtitles = HdRezkaStreamSubtitles(**subtitles)
	def append(self, resolution, link):
		self.videos[resolution] = link
	def __str__(self):
		resolutions = list(self.videos.keys())
		if self.subtitles.subtitles:
			return f"<HdRezkaStream> : {resolutions}, subtitles={self.subtitles}"
		return "<HdRezkaStream> : " + str(resolutions)
	def __repr__(self):
		return f"<HdRezkaStream(season:{self.season}, episode:{self.episode})>"
	def __call__(self, resolution):
		coincidences = list(filter(lambda x: str(resolution) in x , self.videos))
		if len(coincidences) > 0:
			return self.videos[coincidences[0]]
		raise ValueError(f'Resolution "{resolution}" is not defined')


class HdRezkaApi():
	__version__ = 5.0
	def __init__(self, url):
		self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
		self.url = url.split(".html")[0] + ".html"
		self.page = self.getPage()
		self.soup = self.getSoup()
		self.id = self.extractId()
		self.name = self.getName()
		self.type = self.getType()

		#other
		self.translators = None
		self.seriesInfo = None

	def getPage(self):
		return requests.get(self.url, headers=self.HEADERS)

	def getSoup(self):
		return BeautifulSoup(self.page.content, 'html.parser')

	def extractId(self):
		return self.soup.find(id="post_id").attrs['value']

	def getName(self):
		return self.soup.find(class_="b-post__title").get_text().strip()

	def getType(self):
		return self.soup.find('meta', property="og:type").attrs['content']

	@staticmethod
	def clearTrash(data):
		trashList = ["@","#","!","^","$"]
		trashCodesSet = []
		for i in range(2,4):
			startchar = ''
			for chars in product(trashList, repeat=i):
				data_bytes = startchar.join(chars).encode("utf-8")
				trashcombo = base64.b64encode(data_bytes)
				trashCodesSet.append(trashcombo)

		arr = data.replace("#h", "").split("//_//")
		trashString = ''.join(arr)

		for i in trashCodesSet:
			temp = i.decode("utf-8")
			trashString = trashString.replace(temp, '')

		finalString = base64.b64decode(trashString+"==")
		return finalString.decode("utf-8")

	def getTranslations(self):
		arr = {}
		translators = self.soup.find(id="translators-list")
		if translators:
			children = translators.findChildren(recursive=False)
			for child in children:
				if child.text:
					arr[child.text] = child.attrs['data-translator_id']

		if not arr:
			#auto-detect
			def getTranslationName(s):
				table = s.find(class_="b-post__info")
				for i in table.findAll("tr"):
					tmp = i.get_text()
					if tmp.find("переводе") > 0:
						return tmp.split("В переводе:")[-1].strip()
			def getTranslationID(s):
				initCDNEvents = {'video.tv_series': 'initCDNSeriesEvents',
								 'video.movie'    : 'initCDNMoviesEvents'}
				tmp = s.text.split(f"sof.tv.{initCDNEvents[self.type]}")[-1].split("{")[0]
				return tmp.split(",")[1].strip()

			arr[getTranslationName(self.soup)] = getTranslationID(self.page)

		self.translators = arr
		return arr

	def getOtherParts(self):
		parts = self.soup.find(class_="b-post__partcontent")
		other = []
		if parts:
			for i in parts.findAll(class_="b-post__partcontent_item"):
				if 'current' in i.attrs['class']:
					other.append({
						i.find(class_="title").text: self.url
					})
				else:
					other.append({
						i.find(class_="title").text: i.attrs['data-url']
					})
		return other

	@staticmethod
	def getEpisodes(s, e):
		seasons = BeautifulSoup(s, 'html.parser')
		episodes = BeautifulSoup(e, 'html.parser')

		seasons_ = {}
		for season in seasons.findAll(class_="b-simple_season__item"):
			seasons_[ season.attrs['data-tab_id'] ] = season.text

		episods = {}
		for episode in episodes.findAll(class_="b-simple_episode__item"):
			if episode.attrs['data-season_id'] in episods:
				episods[episode.attrs['data-season_id']] [ episode.attrs['data-episode_id'] ] = episode.text
			else:
				episods[episode.attrs['data-season_id']] = {episode.attrs['data-episode_id']: episode.text}

		return seasons_, episods

	def getSeasons(self):
		if not self.translators:
			self.translators = self.getTranslations()

		arr = {}
		for i in self.translators:
			js = {
				"id": self.id,
				"translator_id": self.translators[i],
				"action": "get_episodes"
			}
			r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=js, headers=self.HEADERS)
			response = r.json()
			if response['success']:
				seasons, episodes = self.getEpisodes(response['seasons'], response['episodes'])
				arr[i] = {
					"translator_id": self.translators[i],
					"seasons": seasons, "episodes": episodes
				}

		self.seriesInfo = arr
		return arr

	def getStream(self, season=None, episode=None, translation=None, index=0):
		def makeRequest(data):
			r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=data, headers=self.HEADERS)
			r = r.json()
			if r['success']:
				arr = self.clearTrash(r['url']).split(",")
				stream = HdRezkaStream( season,
										episode,
										subtitles={'data':  r['subtitle'], 'codes': r['subtitle_lns']}
									  )
				for i in arr:
					res = i.split("[")[1].split("]")[0]
					video = i.split("[")[1].split("]")[1].split(" or ")[1]
					stream.append(res, video)
				return stream

		def getStreamSeries(self, season, episode, translation_id):
			if not (season and episode):
				raise TypeError("getStream() missing required arguments (season and episode)")
			
			season = str(season)
			episode = str(episode)

			if not self.seriesInfo:
				self.getSeasons()
			seasons = self.seriesInfo

			tr_str = list(self.translators.keys())[list(self.translators.values()).index(translation_id)]

			if not season in list(seasons[tr_str]['episodes']):
				raise ValueError(f'Season "{season}" is not defined')

			if not episode in list(seasons[tr_str]['episodes'][season]):
				raise ValueError(f'Episode "{episode}" is not defined')

			return makeRequest({
				"id": self.id,
				"translator_id": translation_id,
				"season": season,
				"episode": episode,
				"action": "get_stream"
			})
			

		def getStreamMovie(self, translation_id):
			return makeRequest({
				"id": self.id,
				"translator_id": translation_id,
				"action": "get_movie"
			})			


		if not self.translators:
			self.translators = self.getTranslations()

		if translation:
			if translation.isnumeric():
				if translation in self.translators.values():
					tr_id = translation
				else:
					raise ValueError(f'Translation with code "{translation}" is not defined')

			elif translation in self.translators:
				tr_id = self.translators[translation]
			else:
				raise ValueError(f'Translation "{translation}" is not defined')

		else:
			tr_id = list(self.translators.values())[index]


		if self.type == "video.tv_series":
			return getStreamSeries(self, season, episode, tr_id)
		elif self.type == "video.movie":
			return getStreamMovie(self, tr_id)
		else:
			raise TypeError("Undefined content type")


	def getSeasonStreams(self, season, translation=None, index=0, ignore=False, progress=None):
		season = str(season)

		if not progress:
			progress = lambda cur, all: print(f"{cur}/{all}", end="\r")

		if not self.translators:
			self.translators = self.getTranslations()
		trs = self.translators

		if translation:
			if translation.isnumeric():
				if translation in trs.values():
					tr_id = translation
				else:
					raise ValueError(f'Translation with code "{translation}" is not defined')

			elif translation in trs:
				tr_id = trs[translation]
			else:
				raise ValueError(f'Translation "{translation}" is not defined')

		else:
			tr_id = list(trs.values())[index]

		tr_str = list(trs.keys())[list(trs.values()).index(tr_id)]

		if not self.seriesInfo:
			self.getSeasons()
		seasons = self.seriesInfo

		if not season in list(seasons[tr_str]['episodes']):
			raise ValueError(f'Season "{season}" is not defined')

		series = seasons[tr_str]['episodes'][season]
		streams = {}

		series_length = len(series)

		threads = []
		for episode_id in series:
			def make_call(ep_id, retry=True):
				try:
					stream = self.getStream(season, ep_id, tr_str)
					streams[ep_id] = stream
				except Exception as e:
					if retry:
						return make_call(ep_id, retry=False)
					if not ignore:
						ex_name = e.__class__.__name__
						ex_desc = e
						print(f"{ex_name} > ep:{ep_id}: {ex_desc}")
						streams[ep_id] = None
			
			t = threading.Thread(target=make_call, args=(episode_id,))
			t.start()
			threads.append(t)

		progress(0, series_length)
		for i in range(len(threads)):
			threads[i].join()
			progress(i+1, series_length)

		sorted_streams = {k: streams[k] for k in sorted(streams, key=lambda x: int(x))}
		return sorted_streams
