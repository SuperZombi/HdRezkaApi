import requests
from bs4 import BeautifulSoup
import base64
from itertools import product

class HdRezkaStream():
	def __init__(self, season, episode):
		self.videos = {}
		self.season = season
		self.episode = episode
	def append(self, resolution, link):
		self.videos[resolution] = link
	def __str__(self):
		resolutions = list(self.videos.keys())
		return "<HdRezkaStream> : " + str(resolutions)
	def __repr__(self):
		return f"<HdRezkaStream(season:{self.season}, episode:{self.episode})>"
	def __call__(self, resolution):
		coincidences = list(filter(lambda x: str(resolution) in x , self.videos))
		if len(coincidences) > 0:
			return self.videos[coincidences[0]]
		raise ValueError(f'Resolution "{resolution}" is not defined')


class HdRezkaApi():
	__version__ = 3.0
	def __init__(self, url):
		self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
		self.url = url.split(".html")[0] + ".html"
		self.page = self.getPage()
		self.soup = self.getSoup()
		self.id = self.extractId()
		self.name = self.getName()

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
			children = translators.findChildren()
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
				tmp = s.text.split("sof.tv.initCDNSeriesEvents")[-1].split("{")[0]
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
				seasons, episodes = HdRezkaApi.getEpisodes(response['seasons'], response['episodes'])
				arr[i] = {
					"translator_id": self.translators[i],
					"seasons": seasons, "episodes": episodes
				}

		self.seriesInfo = arr
		return arr

	def getStream(self, season, episode, translation=None, index=0):
		season = str(season)
		episode = str(episode)

		if not self.translators:
			self.translators = self.getTranslations()
		trs = self.translators

		if translation:
			if translation.isnumeric():
				if translation in trs.values():
					tr_id = translation
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

		if not episode in list(seasons[tr_str]['episodes'][season]):
			raise ValueError(f'Episode "{episode}" is not defined')

		js = {
			"id": self.id,
			"translator_id": tr_id,
			"season": season,
			"episode": episode,
			"action": "get_stream"
		}
		r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=js, headers=self.HEADERS)
		r = r.json()
		if r['success']:
			arr = HdRezkaApi.clearTrash(r['url']).split(",")
			stream = HdRezkaStream(season, episode)
			for i in arr:
				res = i.split("[")[1].split("]")[0]
				video = i.split("[")[1].split("]")[1].split(" or ")[1]
				stream.append(res, video)
			return stream


	def getSeasonStreams(self, season, translation=None, index=0, ignore=False, progress=None):
		season = str(season)

		if not self.translators:
			self.translators = self.getTranslations()
		trs = self.translators

		if translation:
			if translation.isnumeric():
				if translation in trs.values():
					tr_id = translation
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

		for episode_id in series:
			def make_call():
				stream = self.getStream(season, episode_id, tr_str)
				streams[episode_id] = stream
				if progress:
					progress(episode_id, series_length)
				else:
					print(f"> {episode_id}", end="\r")

			if ignore:
				try:
					make_call()
				except Exception as e:
					print(e)
			else:
				make_call()
		return streams
