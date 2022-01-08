# HDrezka-api

## ❗NOT WORKING❗
### ❗HdRezka blocked their API❗

<hr></br>

### Usage:

```python
url = "https://rezka.ag/   __YOUR_URL__   .html"

rezka = HdRezkaApi(url)
print(rezka.name)
print( rezka.getTranslations() )
print( rezka.getOtherParts() )
print( rezka.getSeasons() )

print( rezka.getStream('1', '1', '720p') )
print( rezka.getSeasonStreams('1', '720p') )
```

<hr>

### getStream(`season`, `episode`, `resolution`, `translation=None`, `index=0`)
```
getStream(
    translation='Дубляж' or translation='56' or index=0
)                                               ^ this is index in translators array
```
### getSeasonStreams(`season`, `resolution`, `translation=None`, `index=0`)
```
getSeasonStreams(
    translation='Дубляж' or translation='56' or index=0
)                                               ^ this is index in translators array
```
<hr>

#### `self.id` - `post_id`
#### `self.name` - `post__title`
#### `self.translators` - translators array
#### `self.seriesInfo` - seasons and episodes array
