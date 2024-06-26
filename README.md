# HdRezkaApi

<img src="https://shields.io/badge/version-v7.1-blue">

### Install:
```
pip install HdRezkaApi
```

### Usage:

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

#### `self.id` - Film id (`post_id`)
#### `self.name` - Film name (`post__title`)
#### `self.type` - `HdRezkaTVSeries` or `HdRezkaMovie`
#### `self.thumbnail` - Film thumbnail url
#### `self.rating` - Film rating (<a href="#hdrezkarating">Hdrezka Rating</a>)
#### `self.translators` - Translators array
#### `self.seriesInfo` - Seasons and Episodes array
#### `self.otherParts` - Other parts of this film

<hr>

### getStream(`season`, `episode`, `translation=None`, `index=0`)
```
getStream(
    translation='Дубляж' or translation='56' or index=0
)                                               ^ this is index in translators array
```
If type == movie then there is no need to specify season and episode.
```python
stream = rezka.getStream() # if movie
```
<hr>

### getSeasonStreams(`season`, `translation=None`, `index=0`, `ignore=False`, `progress=None`)
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
#### `self.videos` - dict of videos, where key is resolution and value is url
#### `self.name`
#### `self.translator_id`
#### `self.season` - (`None` if film)
#### `self.episode` - (`None` if film)
#### `self.subtitles` - <a href="#hdrezkastreamsubtitles" >HdRezkaStreamSubtitles</a>
#### `HdRezkaStream(resolutin)` - call object with argument to get url of video

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

<br>

# HdRezkaStreamSubtitles:
#### `self.subtitles` - dict of subtitles
#### `self.keys` - list of subtitles codes
#### `self(id)` - call object with argument to get url of subtitles

### Usage examples:

```python
stream = rezka.getStream(1, 5)

print( stream.subtitles.keys )        # ['en', 'ru']
print( stream.subtitles.subtitles )   # { 'en': {'title': 'English', 'link': 'https:/'}, ...  }
print( stream.subtitles('en') )       # 'https:/'
print( stream.subtitles('English') )  # 'https:/'
print( stream.subtitles(0) )          # 'https:/'
#                       ^ index
```

<br>

# HdRezkaRating:
#### `self.value` - rating value (`float`)
#### `self.votes` - votes amount (`int`)

<hr>

### Proxy usage example:
```python
rezka = HdRezkaApi(url, proxy={'http': 'http://192.168.0.1:80'})
```
