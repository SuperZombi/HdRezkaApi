import requests
from bs4 import BeautifulSoup

class HdRezkaApi():
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
			r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=js)
			response = r.json()
			if response['success']:
				seasons, episodes = HdRezkaApi.getEpisodes(response['seasons'], response['episodes'])
				arr[i] = {
					"translator_id": self.translators[i],
					"seasons": seasons, "episodes": episodes
				}

		self.seriesInfo = arr
		return arr

	def getStream(self, season, episode, resolution, translation=None, index=0):
		if not resolution in ["360p", "480p", "720p", "1080p", "1080p Ultra"]:
			available_res = '"360p", "480p", "720p", "1080p", "1080p Ultra"'
			raise ValueError(f'Resolution "{resolution}" is not defined\nUse one of these: {available_res}')

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
		r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=js)
		r = r.json()
		if r['success']:
			arr = r['url'].split(",")
			for i in arr:
				# 360p, 480p, 720p, 1080p, 1080p Ultra
				res = i.split("[")[1].split("]")[0]
				if res == resolution:
					stream = i.split("[")[1].split("]")[1].split(" or ")[1]
					return stream


	def getSeasonStreams(self, season, resolution, translation=None, index=0):
		if not resolution in ["360p", "480p", "720p", "1080p", "1080p Ultra"]:
			available_res = '"360p", "480p", "720p", "1080p", "1080p Ultra"'
			raise ValueError(f'Resolution "{resolution}" is not defined\nUse one of these: {available_res}')

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

		for episode_id in series:
			js = {
				"id": self.id,
				"translator_id": tr_id,
				"season": season,
				"episode": episode_id,
				"action": "get_stream"
			}
			r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=js)
			r = r.json()
			if r['success']:
				arr = r['url'].split(",")
				for i in arr:
					# 360p, 480p, 720p, 1080p, 1080p Ultra
					res = i.split("[")[1].split("]")[0]
					if res == resolution:
						stream = i.split("[")[1].split("]")[1].split(" or ")[1]
						streams[episode_id] = stream
						print(f"> {episode_id}")
		return streams



def main():
	#url = "https://rezka.ag/cartoons/fiction/26246-gorod-geroev-2017.html"
	#url = "https://rezka.ag/animation/fantasy/41055-agent-vremeni-2021.html"
	#url = "https://rezka.ag/cartoons/fantasy/7924-udivitelnyy-mir-gambola-2008.html"
	#url = "https://rezka.ag/animation/adventures/42697-reinkarnaciya-bezrabotnogo-tv-2-2021.html"

	rezka = HdRezkaApi(url)
	print(rezka.name)
	print( rezka.getTranslations() )
	print( rezka.getOtherParts() )
	print( rezka.getSeasons() )

	print( rezka.getStream('1', '1', '720p') )
	print( rezka.getSeasonStreams('1', '720p') )


# DOCS:

#print( rezka.getStream(season='1', episode='1', resolution='720p'))
# getStream(
# 	translation='Дубляж' or translation='56' or index=0
# )                                             ^ this is index in translators array


#print( rezka.getStream(season='1', resolution='720p'))
# getSeasonStreams(
# 	translation='Дубляж' or translation='56' or index=0
# )                                             ^ this is index in translators array
