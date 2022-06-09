# HDrezka-api

<img src="https://shields.io/badge/version-v3.0-blue">

#### Works with the new API from 01.05.2022

<hr></br>

### Usage:

```python
url = "https://rezka.ag/   __YOUR_URL__   .html"

rezka = HdRezkaApi(url)
print(rezka.name)
print( rezka.getTranslations() )
print( rezka.getOtherParts() )
print( rezka.getSeasons() )

print( rezka.getStream('1', '1')('720p') )
print( rezka.getSeasonStreams('1') )
```

#### `self.id` - `post_id`
#### `self.name` - `post__title`
#### `self.translators` - translators array
#### `self.seriesInfo` - seasons and episodes array

<hr>

### getStream(`season`, `episode`, `translation=None`, `index=0`)
```
getStream(
    translation='Дубляж' or translation='56' or index=0
)                                               ^ this is index in translators array
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
	print(str(current) + "/" + str(all))

print( rezka.getSeasonStreams(1, ignore=True, progress=progress) )
```

<hr>
<br>

# HdRezkaStream:
#### `self.videos` - dict of videos, where key is resolution and value is url
#### `HdRezkaStream(resolutin)` - call object with argument to get url of video

### Usage examples:

```python
print( rezka.getStream('1', '1')('720p') )
print( rezka.getStream('1', '1')('720') )
print( rezka.getStream(1, 1)(1080) )
print( rezka.getStream(1, 1)('Ultra') )
print( rezka.getStream(1, 1)('1080 Ultra') )
print( rezka.getStream(1, 1).videos )
```
