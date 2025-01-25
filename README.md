# HdRezkaApi

<img src="https://shields.io/badge/version-v7.5.0-blue"> <a href="#donate"><img src="https://shields.io/badge/💲-Support_Project-2ea043"></a>

## Install:
```
pip install HdRezkaApi
```

## Table of Contents:
1. [Usage](#usage)
2. [Film Information](#film-information)
3. [getStream](#getstream)
4. [getSeasonStreams](#getseasonstreams)
5. [HdRezkaStream](#hdrezkastream)
6. [HdRezkaStreamSubtitles](#hdrezkastreamsubtitles)
7. [HdRezkaRating](#hdrezkarating)
8. [Proxy](#proxy)
9. [Cookies](#cookies)
10. [HdRezkaSession](#hdrezkasession)

<hr>

## Usage:

```python
from HdRezkaApi import *

url = "https://hdrezka.ag/   __YOUR_URL__   .html"

rezka = HdRezkaApi(url)
print(rezka.name)
print(rezka.thumbnail)
print( rezka.rating.value )
print( rezka.rating.votes )
print( rezka.translators )
print( rezka.otherParts )
print( rezka.seriesInfo )

print(rezka.type)
print(rezka.type == HdRezkaTVSeries == HdRezkaTVSeries() == "tv_series")

print( rezka.getStream()('720p') ) # if movie
print( rezka.getStream('1', '1')('720p') )
print( dict(rezka.getSeasonStreams('1')) )
```

## Film Information

| Attribute                        | Description                          |
|----------------------------------|--------------------------------------|
| <a id="film-id" href="#film-id">`self.id`</a>| Film ID                  |
| <a id="film-name" href="#film-name">`self.name`</a>| Film name          |
| <a id="film-description" href="#film-description">`self.description`</a>| Film description |
| <a id="film-type" href="#film-type">`self.type`</a> | `HdRezkaTVSeries` or `HdRezkaMovie`  |
| <a id="film-thumbnail" href="#film-thumbnail">`self.thumbnail`</a>     | Film thumbnail URL|
| <a id="film-thumbnailhq" href="#film-thumbnailhq">`self.thumbnailHQ`</a>| Film thumbnail in high quality |
| <a id="film-rating" href="#film-rating">`self.rating`</a> |Film rating ([HdRezkaRating](#hdrezkarating)) |
| <a id="film-otherparts" href="#film-otherparts">`self.otherParts`</a>|Other parts of this film `[{Film_name: url}]`|
| <a id="film-translators" href="#film-translators">`self.translators`</a>|Translators dict `{Translator_name: translator_id}`|
| <a id="film-seriesinfo" href="#film-seriesinfo">`self.seriesInfo`</a>| [Series info](#seriesInfo) by translators|
| <a id="film-episodesinfo" href="#film-episodesinfo">`self.episodesInfo`</a>|All [seasons and episodes](#episodesInfo)|

#### `seriesInfo`
```
{
	Translator_name: {
		translator_id,
		seasons: {1, 2},
		episodes: {
			1: {1, 2, 3},
			2: {1, 2, 3}
		}
	}
}
```

#### `episodesInfo`
```
[
	{
		season: 1, season_text,
		episodes: [
			{
				episode: 1, episode_text,
				translations: [{translator_id, translator_name}]
			}
		]
	}
]
```

<hr>

### getStream
`getStream(season, episode, translation=None, index=0)`
```
getStream(
    translation='Дубляж' or translation='56' or index=0
)                                               ^ this is index in translators array
```
If type is movie then there is no need to specify season and episode.
```python
stream = rezka.getStream() # if movie
```
<hr>

### getSeasonStreams
`getSeasonStreams(season, translation=None, index=0, ignore=False, progress=None)`
```
getSeasonStreams(
    translation='Дубляж' or translation='56' or index=0
)                                               ^ this is index in translators array
```

#### `ignore` - ignore errors
#### `progress` - callback function

```python
def progress(current, all):
	percent = round(current * 100 / all)
	print(f"{percent}%: {current}/{all}", end="\r")

print( dict(rezka.getSeasonStreams(1, ignore=True, progress=progress)) )
```

Output example:
```
{'1': <HdRezkaStream(season:1, episode:1)>, '2': <HdRezkaStream(season:1, episode:2)>, ...}
```

If an error occurs, an attempt will be made to repeat the request again.<br>
But if the error occurs again, then `None` will be added to the final dict.<br>
To ignore errors and retry requests until a response is received, specify the `ignore=True` option.

```python
for i, stream in rezka.getSeasonStreams('1'):
	print(stream)
```

<hr>
<br>

# HdRezkaStream:

| Attribute              | Description                                             |
|------------------------|---------------------------------------------------------|
|<a id="stream-videos" href="#stream-videos">`self.videos`</a>|Dict of videos where the key is resolution and value is list of URLs|
|<a id="stream-name" href="#stream-name">`self.name`</a>| Film name                |
|<a id="stream-translatorid" href="#stream-translatorid">`self.translator_id`</a>  | Translator ID |
|<a id="stream-season" href="#stream-season">`self.season`</a> | Season number (`None` if film)    |
|<a id="stream-episode" href="#stream-episode">`self.episode`</a>| Episode number (`None` if film) |
|<a id="stream-subtitles" href="#stream-subtitles">`self.subtitles`</a>| [HdRezkaStreamSubtitles](#hdrezkastreamsubtitles) object|
|<a id="stream-call" href="#stream-call">`HdRezkaStream(resolution)`</a>|Call object with argument to get the URL of the video|

### Usage examples:

```python
stream = rezka.getStream(1, 5)

print( stream('720p') )
print( stream('720') )
print( stream(1080) )
print( stream('Ultra') )
print( stream('1080p Ultra') )
print( stream.videos )
```
```
{
	'360p': ['https://sambray.org/...mp4', 'https://stream.voidboost.cc/...mp4'],
	'480p': ['https://sambray.org/...mp4', 'https://stream.voidboost.cc/...mp4'],
	'720p': ['https://sambray.org/...mp4', 'https://stream.voidboost.cc/...mp4'],
}
```

<br>

# HdRezkaStreamSubtitles:
| Attribute              | Description                   |
|------------------------|-------------------------------|
|<a id="subtitles" href="#subtitles">`self.subtitles`</a>|Dict of subtitles where the key is the language code and value is the subtitle information|
| <a id="subtitles-keys" href="#subtitles-keys">`self.keys`</a>|List of available subtitle language codes|
| <a id="subtitles-call" href="#subtitles-call">`self(id)`</a> |Call object with argument to get URL of subtitles|

### Usage examples:

```python
stream = rezka.getStream(1, 5)

print( stream.subtitles.subtitles )  # { 'en': {'title': 'English', 'link': 'https:/'}, ...  }
print( stream.subtitles.keys )       # ['en', 'ru']
print( stream.subtitles('en') )      # 'https:/'
print( stream.subtitles('English') ) # 'https:/'
print( stream.subtitles(0) )         # 'https:/'
#                       ^ index
```

<br>

# HdRezkaRating:
| Attribute                         | Description                                      |
|-----------------------------------|--------------------------------------------------|
| <a id="rating-value" href="#rating-value">`self.value`</a> | Rating value (`float`)  |
| <a id="rating-votes" href="#rating-votes">`self.votes`</a> | Number of votes (`int`) |

<br>

# Proxy:
```python
rezka = HdRezkaApi(url, proxy={'http': 'http://192.168.0.1:80'})
```

<br>

# Cookies:
```python
rezka = HdRezkaApi(url, cookies={"dle_user_id": user_id, "dle_password": password_hash})
```
If you are not sure:
```python
rezka = HdRezkaApi(url, cookies=HdRezkaApi.make_cookies(user_id, password_hash))
```
Manually login:
```python
rezka = HdRezkaApi(url)
rezka.login("your_email@gmail.com", "your_password1234")
```
<br>

# HdRezkaSession
HdRezkaSession allows you to log in once and not send login requests every time.

You can also specify origin to make requests to a same site. Origin in full urls will be ignored.<br>
In the next example, the request will be made to the url: `"https://rezka_mirror.com/__YOUR_URL__.html"`
```python
with HdRezkaSession("https://rezka_mirror.com/") as session:
	session.login("email@gmail.com", "password")
	rezka = session.get("https://hdrezka.ag/__URL_PATH__.html")
```
Also when specifying origin you can specify only url path.
```python
with HdRezkaSession("https://rezka_mirror.com/") as session:
	rezka = session.get("__URL_PATH__.html")
```
<br>

You can also not specify origin and then requests will be made to the URL you specified.
```python
with HdRezkaSession() as session:
	rezka = session.get("https://hdrezka.ag/__URL_PATH__.html")
```
```python
with HdRezkaSession(cookies=cookies, headers=headers, proxy=proxy) as session:
	# also inline seting up
	session.cookies = cookies
	session.headers = headers
	session.proxy = proxy
```

<br>

## 💲Donate

<table>
	<tr>
		<td>
			<img width="18px" src="https://www.google.com/s2/favicons?domain=https://donatello.to&sz=256">
		</td>
		<td>
			<a href="https://donatello.to/super_zombi">Donatello</a>
		</td>
	</tr>
	<tr>
		<td>
		<img width="18px" src="https://www.google.com/s2/favicons?domain=https://www.donationalerts.com&sz=256">
		</td>
		<td>
		<a href="https://www.donationalerts.com/r/super_zombi">Donation Alerts</a>
		</td>
	</tr>
</table>
