import requests
from bs4 import BeautifulSoup
import base64
from itertools import product
from functools import cached_property
from urllib.parse import urlparse
import time

from .utils.stream import HdRezkaStream
from .utils.search import HdRezkaSearch
from .utils.types import BeautifulSoupCustom
from .utils.types import (HdRezkaTVSeries, HdRezkaMovie, HdRezkaRating, HdRezkaEmptyRating)
from .utils.errors import (LoginRequiredError, LoginFailed, FetchFailed, HTTP)


class HdRezkaApi():
	__version__ = "7.6.2"
	def __init__(self, url, proxy={}, headers={}, cookies={}):
		self.url = url.split(".html")[0] + ".html"
		uri = urlparse(self.url)
		self.origin = f'{uri.scheme}://{uri.netloc}'
		self.proxy = proxy
		self.cookies = cookies
		self.HEADERS = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
			**headers
		}
	def __str__(self): return f'HdRezka("{self.name}")'
	def __repr__(self): return str(self)

	def login(self, email:str, password:str):
		response = requests.post(f"{self.origin}/ajax/login/",data={"login_name":email,"login_password":password},headers=self.HEADERS,proxies=self.proxy)
		data = response.json()
		if data['success']: self.cookies = {**self.cookies,**response.cookies.get_dict()}
		else: raise LoginFailed(data.get("message"))

	@staticmethod
	def make_cookies(user_id:str, password_hash:str):
		"""Build cookies helper"""
		return {"dle_user_id":str(user_id),"dle_password":password_hash}

	@cached_property
	def page(self):
		r = requests.get(self.url, allow_redirects=True, headers=self.HEADERS, proxies=self.proxy, cookies=self.cookies)
		if r.ok: return r
		raise HTTP(r.status_code, r.reason)

	@cached_property
	def soup(self):
		s = BeautifulSoupCustom(self.page.content, 'html.parser')
		if s.title.text == "Sign In": raise LoginRequiredError()
		return s

	@cached_property
	def id(self):
		def get_val(el, attr): return el.attrs.get(attr) if el else None
		return int(
			get_val(self.soup.find(id="post_id"), 'value') or
			get_val(self.soup.find(id="send-video-issue"), 'data-id') or
			get_val(self.soup.find(id="user-favorites-holder"), 'data-post_id') or
			self.url.split("/")[-1].split("-")[0]
		)

	@cached_property
	def name(self):
		return self.soup.find(class_="b-post__title").get_text().strip()

	@cached_property
	def description(self):
		return self.soup.find(class_="b-post__description_text").get_text().strip()

	@cached_property
	def thumbnail(self):
		return self.soup.find(class_="b-sidecover").find('img').attrs['src']

	@cached_property
	def thumbnailHQ(self):
		return self.soup.find(class_="b-sidecover").find('a').attrs['href']

	@cached_property
	def type(self):
		type_str = self.soup.find('meta', property="og:type").attrs['content']
		if type_str == "video.tv_series":
			return HdRezkaTVSeries()
		elif type_str == "video.movie":
			return HdRezkaMovie()
		return type_str

	@cached_property
	def rating(self):
		wraper = self.soup.find(class_='b-post__rating')
		if wraper:
			rating = wraper.find(class_='num').get_text()
			votes = wraper.find(class_='votes').get_text().strip("()")
			return HdRezkaRating(value=float(rating), votes=int(votes))
		else:
			return HdRezkaEmptyRating()

	@cached_property
	def translators(self):
		arr = {}
		translators = self.soup.find(id="translators-list")
		if translators:
			children = translators.findChildren(recursive=False)
			for child in children:
				if child.text:
					arr[child.text.strip()] = int(child.attrs['data-translator_id'])
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
				tmp = s.text.split(f"sof.tv.{initCDNEvents[f'video.{self.type}']}")[-1].split("{")[0]
				return int(tmp.split(",")[1].strip())

			arr[getTranslationName(self.soup)] = getTranslationID(self.page)
		return arr

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

	@cached_property
	def otherParts(self):
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
			seasons_[ int(season.attrs['data-tab_id']) ] = season.text

		episodes_ = {}
		for episode in episodes.findAll(class_="b-simple_episode__item"):
			if int(episode.attrs['data-season_id']) in episodes_:
				episodes_[int(episode.attrs['data-season_id'])] [ int(episode.attrs['data-episode_id']) ] = episode.text
			else:
				episodes_[int(episode.attrs['data-season_id'])] = {int(episode.attrs['data-episode_id']): episode.text}

		return seasons_, episodes_

	@cached_property
	def seriesInfo(self):
		arr = {}
		for i in self.translators:
			js = {
				"id": self.id,
				"translator_id": self.translators[i],
				"action": "get_episodes"
			}
			r = requests.post(f"{self.origin}/ajax/get_cdn_series/", data=js, headers=self.HEADERS, proxies=self.proxy, cookies=self.cookies)
			response = r.json()
			if response['success']:
				seasons, episodes = self.getEpisodes(response['seasons'], response['episodes'])
				arr[i] = {
					"translator_id": self.translators[i],
					"seasons": seasons, "episodes": episodes
				}
		return arr

	@cached_property
	def episodesInfo(self):
		output_data = []
		for translator_name, translator_info in self.seriesInfo.items():
			translator_id = translator_info["translator_id"]
			for season, season_text in translator_info["seasons"].items():
				season_obj = next((s for s in output_data if s["season"] == int(season)), None)
				if not season_obj:
					season_obj = {
						"season": int(season),
						"season_text": season_text,
						"episodes": []
					}
					output_data.append(season_obj)

				for episode, episode_text in translator_info["episodes"].get(season, {}).items():
					episode_obj = next((e for e in season_obj["episodes"] if e["episode"] == int(episode)), None)
					if not episode_obj:
						episode_obj = {
							"episode": int(episode),
							"episode_text": episode_text,
							"translations": []
						}
						season_obj["episodes"].append(episode_obj)

					episode_obj["translations"].append({
						"translator_id": translator_id,
						"translator_name": translator_name
					})
		return output_data

	def getStream(self, season=None, episode=None, translation=None, index=0):
		def makeRequest(data):
			r = requests.post(f"{self.origin}/ajax/get_cdn_series/", data=data, headers=self.HEADERS, proxies=self.proxy, cookies=self.cookies)
			r = r.json()
			if r['success'] and r['url']:
				arr = self.clearTrash(r['url']).split(",")
				stream = HdRezkaStream( season=season, episode=episode,
										name=self.name, translator_id=data['translator_id'],
										subtitles={'data': r['subtitle'], 'codes': r['subtitle_lns']}
									)
				for i in arr:
					temp = i.split("[")[1].split("]")
					quality = str(temp[0])
					links = filter(lambda x: x.endswith(".mp4"), temp[1].split(" or "))
					for video in links:
						stream.append(quality, video)
				return stream
			raise FetchFailed()

		def getStreamSeries(self, season, episode, translation_id):
			if not (season and episode):
				raise TypeError("getStream() missing required arguments (season and episode)")
			
			tr_str = list(self.translators.keys())[list(self.translators.values()).index(translation_id)]

			if not season in list(self.seriesInfo[tr_str]['episodes']):
				raise ValueError(f'Season "{season}" is not defined')

			if not episode in list(self.seriesInfo[tr_str]['episodes'][season]):
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

		if translation:
			if str(translation).isnumeric():
				if int(translation) in self.translators.values():
					tr_id = int(translation)
				else:
					raise ValueError(f'Translation with code "{translation}" is not defined')

			elif translation in self.translators:
				tr_id = self.translators[translation]
			else:
				raise ValueError(f'Translation "{translation}" is not defined')

		else:
			tr_id = list(self.translators.values())[index]


		if self.type == HdRezkaTVSeries:
			if season and episode:
				return getStreamSeries(self, int(season), int(episode), tr_id)
			elif season and (not episode):
				raise TypeError("getStream() missing one required argument (episode)")
			elif episode and (not season):
				raise TypeError("getStream() missing one required argument (season)")
			else:
				raise TypeError("getStream() missing required arguments (season and episode)")
		elif self.type == HdRezkaMovie:
			return getStreamMovie(self, tr_id)
		else:
			raise TypeError("Undefined content type")


	def getSeasonStreams(self, season, translation=None, index=0, ignore=False, progress=None):
		season = str(season)

		if not progress:
			progress = lambda cur, all: None

		if translation:
			if str(translation).isnumeric():
				if int(translation) in self.translators.values():
					tr_id = int(translation)
				else:
					raise ValueError(f'Translation with code "{translation}" is not defined')

			elif translation in self.translators:
				tr_id = self.translators[translation]
			else:
				raise ValueError(f'Translation "{translation}" is not defined')

		else:
			tr_id = list(self.translators.values())[index]

		tr_str = list(self.translators.keys())[list(self.translators.values()).index(tr_id)]

		if not int(season) in list(self.seriesInfo[tr_str]['episodes']):
			raise ValueError(f'Season "{season}" is not defined')

		series = self.seriesInfo[tr_str]['episodes'][int(season)]
		series_length = len(series)

		streams = {}
		progress(0, series_length)

		for episode_id in series:
			def make_call(ep_id, retry=True):
				try:
					stream = self.getStream(season, ep_id, tr_str)
					streams[ep_id] = stream
					progress(len(streams), series_length)
					return stream
				except Exception as e:
					if retry:
						time.sleep(1)
						if ignore:
							return make_call(ep_id)
						else:
							return make_call(ep_id, retry=False)
					if not ignore:
						ex_name = e.__class__.__name__
						ex_desc = e
						print(f"{ex_name} > ep:{ep_id}: {ex_desc}")
						streams[ep_id] = None
						progress(len(streams), series_length)

			yield episode_id, make_call(episode_id)


class HdRezkaSession:
	def __init__(self, origin="", proxy={}, headers={}, cookies={}):
		self.origin = None
		if origin:
			uri = urlparse(origin)
			self.origin = f'{uri.scheme}://{uri.netloc}'
		self.proxy = proxy
		self.cookies = cookies
		self.HEADERS = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
			**headers
		}
	def __enter__(self): return self
	def __exit__(self, type, value, traceback): pass

	def login(self, email:str, password:str):
		if not self.origin: raise ValueError("For login origin is required")
		response = requests.post(f"{self.origin}/ajax/login/",data={"login_name":email,"login_password":password},headers=self.HEADERS,proxies=self.proxy)
		data = response.json()
		if data['success']: self.cookies = {**self.cookies,**response.cookies.get_dict()}
		else: raise LoginFailed(data.get("message"))

	def get(self, url, **kwargs):
		if self.origin:
			uri = urlparse(url)
			url = self.origin+"/"+uri.path.lstrip("/")
		return HdRezkaApi(url, **{
			"proxy": self.proxy,
			"headers": self.HEADERS,
			"cookies": self.cookies,
			**kwargs
		})

	def search(self, query):
		if not self.origin: raise ValueError("For search origin is required")
		return HdRezkaSearch(self.origin,proxy=self.proxy,headers=self.HEADERS,cookies=self.cookies)(query)
