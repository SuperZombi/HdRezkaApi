# HDrezka-api

### Usage:

```python
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
