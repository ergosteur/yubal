# OMV vs ATV Comparison

Same song: **Bzrp Music Sessions, Vol. 62/66** (Bizarrap & J Balvin)

- OMV = Official Music Video
- ATV = Album Track Video (audio-only with album art)

## get_playlist response

| Field                 | OMV                                 | ATV                                                    |
| --------------------- | ----------------------------------- | ------------------------------------------------------ |
| `videoId`             | `imfr5Px5D54`                       | `Tdv8XKco7PY`                                          |
| `title`               | `Bzrp Music Sessions, Vol. 62/66`   | `J Balvin: Bzrp Music Sessions, Vol. 62/66`            |
| `artists`             | `[{Bizarrap}, {J Balvin}]`          | `[{Bizarrap}, {J Balvin}]`                             |
| `album`               | `null`                              | `{name: "J Balvin: Bzrp...", id: "MPREb_NrwxuNFCzDK"}` |
| `videoType`           | `MUSIC_VIDEO_TYPE_OMV`              | `MUSIC_VIDEO_TYPE_ATV`                                 |
| `thumbnails`          | YouTube CDN, 1 size, 16:9 (400x225) | Google Photos CDN, 2 sizes, square (60x60, 120x120)    |
| `duration`            | `3:17`                              | `3:11`                                                 |
| `duration_seconds`    | `197`                               | `191`                                                  |
| `views`               | `null`                              | `null`                                                 |
| `likeStatus`          | `INDIFFERENT`                       | `INDIFFERENT`                                          |
| `inLibrary`           | `false`                             | `false`                                                |
| `pinnedToListenAgain` | `false`                             | `false`                                                |
| `isAvailable`         | `true`                              | `true`                                                 |
| `isExplicit`          | `false`                             | `false`                                                |

## get_song response

| Field                  | OMV                                | ATV                                         |
| ---------------------- | ---------------------------------- | ------------------------------------------- |
| `videoId`              | `imfr5Px5D54`                      | `Tdv8XKco7PY`                               |
| `title`                | `Bzrp Music Sessions, Vol. 62/66`  | `J Balvin: Bzrp Music Sessions, Vol. 62/66` |
| `lengthSeconds`        | `196`                              | `190`                                       |
| `channelId`            | `UCmS75G-98QihSusY7NfCZtw` (topic) | `UCONiUl5u7y2bMaVZJcuRDEQ` (Bizarrap)       |
| `author`               | `Bizarrap & J Balvin`              | `Bizarrap & J Balvin`                       |
| `musicVideoType`       | `MUSIC_VIDEO_TYPE_OMV`             | `MUSIC_VIDEO_TYPE_ATV`                      |
| `viewCount`            | `10,292,624`                       | `2,002,685`                                 |
| `thumbnail.thumbnails` | 3 sizes, 16:9 (YouTube CDN)        | 4 sizes, square (Google Photos CDN)         |
| `allowRatings`         | `true`                             | `true`                                      |
| `isOwnerViewing`       | `false`                            | `false`                                     |
| `isCrawlable`          | `true`                             | `true`                                      |
| `isPrivate`            | `false`                            | `false`                                     |
| `isUnpluggedCorpus`    | `false`                            | `false`                                     |
| `isLiveContent`        | `false`                            | `false`                                     |

## Key Differences (Same Song)

| Aspect          | OMV                      | ATV                                         |
| --------------- | ------------------------ | ------------------------------------------- |
| `videoId`       | Different                | Different                                   |
| `title`         | Short form               | Includes featured artist prefix             |
| `album`         | `null`                   | Has album name and ID                       |
| `duration`      | 3:17 (197s)              | 3:11 (191s) - 6 seconds shorter             |
| `channelId`     | Topic/Vevo channel       | Artist's official channel (Bizarrap)        |
| `viewCount`     | ~10.3M (5x higher)       | ~2M                                         |
| Thumbnail CDN   | YouTube (`i.ytimg.com`)  | Google Photos (`lh3.googleusercontent.com`) |
| Thumbnail ratio | 16:9 (video frames)      | 1:1 square (album art)                      |
| Content         | Music video with visuals | Static album art + audio                    |
