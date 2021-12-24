import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

#url = "https://rezka.ag/cartoons/fiction/26246-gorod-geroev-2017.html"
#url = "https://rezka.ag/animation/fantasy/41055-agent-vremeni-2021.html"
#url = "https://rezka.ag/cartoons/fantasy/7924-udivitelnyy-mir-gambola-2008.html"
url = "https://rezka.ag/animation/adventures/42697-reinkarnaciya-bezrabotnogo-tv-2-2021.html"

def extractId(url):
	return url.split("https://")[1].split("/")[-1].split("-")[0]

def getOtherParts(url):
	r = requests.get(url, headers=HEADERS)
	soup = BeautifulSoup(r.content, 'html.parser')
	parts = soup.find(class_="b-post__partcontent")
	other = []
	if parts:
		for i in parts.findAll(class_="b-post__partcontent_item"):
			if 'current' in i.attrs['class']:
				other.append({
					i.find(class_="title").text: url
				})
			else:
				other.append({
					i.find(class_="title").text: i.attrs['data-url']
				})
	return other

def getName(url):
	r = requests.get(url, headers=HEADERS)
	soup = BeautifulSoup(r.content, 'html.parser')
	return soup.find(class_="b-post__title").get_text().strip()

def getTranslations(url):
	arr = {}
	r = requests.get(url, headers=HEADERS)
	soup = BeautifulSoup(r.content, 'html.parser')
	translators = soup.find(id="translators-list")
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
		def getTranslationID(link):
			options = Options()
			options.headless = True
			options.add_argument('log-level=2')
			driver = webdriver.Chrome(options=options)
			driver.get(link)
			el = driver.find_element(By.XPATH, '//*[@id="simple-episodes-list-1"]/li[2]')
			el.click()

			# waiting timeout
			time.sleep(0.5)
			arr = driver.current_url.split(link)
			driver.quit()	
			if len(arr) > 0:
				return arr[-1].split("-")[0].split(":")[-1]

		arr[getTranslationName(soup)] = getTranslationID(url)
	return arr

def getEpisodes(s, e):
	seasons = BeautifulSoup(s, 'html.parser')
	episodes = BeautifulSoup(e, 'html.parser')

	seasons_ = []
	for season in seasons.findAll(class_="b-simple_season__item"):
		seasons_.append({season.attrs['data-tab_id']: season.text})

	episods = {}
	for episode in episodes.findAll(class_="b-simple_episode__item"):
		if episode.attrs['data-season_id'] in episods:
			episods[episode.attrs['data-season_id']].append({episode.attrs['data-episode_id']: episode.text})
		else:
			episods[episode.attrs['data-season_id']] = [{episode.attrs['data-episode_id']: episode.text}]

	return seasons_, episods


def getSeasons(url, cashed_translators=None):
	if cashed_translators:
		translators = cashed_translators
	else:
		translators = getTranslations(url)

	if translators:
		arr = {}
		for i in translators:
			js = {
				"id": extractId(url),
				"translator_id": translators[i],
				"action": "get_episodes"
			}
			r = requests.post("https://rezka.ag/ajax/get_cdn_series/", data=js)
			response = r.json()
			if response['success']:
				seasons, episodes = getEpisodes(response['seasons'], response['episodes'])
				arr[i] = {
					"seasons": seasons, "episodes": episodes
				}

	else:
		arr = []
		r = requests.get(url, headers=HEADERS)
		soup = BeautifulSoup(r.content, 'html.parser')
		seasons = soup.find(id="simple-seasons-tabs")
		episodes = soup.find(id="simple-episodes-tabs")
		if seasons:
			seasons = seasons.findChildren()
		if episodes:
			episodes = episodes.findChildren()

		seasons, episodes = getEpisodes(str(seasons), str(episodes))
		arr.append({"seasons": seasons, "episodes": episodes})

	return arr

def getSeasonStreams(url, season, resolutions, translation=None, index=0):
	trs = getTranslations(url)
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
		
	seasons = getSeasons(url, cashed_translators=trs)
	if not season in list(seasons[tr_str]['episodes'].keys()):
		raise ValueError(f'Season "{season}" is not defined')
	series = seasons[tr_str]['episodes'][season]
	streams = {}

	for i in series:
		episode_id = list(i.keys())[0]

		js = {
			"id": extractId(url),
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
				if res == resolutions:
					stream = i.split("[")[1].split("]")[1].split(" or ")[1]
					streams[episode_id] = stream
					print(f"> {episode_id}")
	return streams


#print( getName(url) )
#print( getTranslations(url) )
#print( getOtherParts(url) )
#print( getSeasons(url) )

# print(getSeasonStreams(url, '1', '720p'))
# print(getSeasonStreams(url, '2', '720p', index=0))
# print(getSeasonStreams(url, '2', '720p', '56'))
# print(getSeasonStreams(url, '2', '720p', 'Дубляж'))
