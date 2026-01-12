# Notes

## How to get metadata

### Inputs

- Playlist URL
- Tracks limit

### Outputs

For each track:

- Audio tags:
  - `title`
  - `artist` (Artist One; Artist Two)
  - `album`
  - `albumartist`
  - `tracknumber`
  - `year`
- Embedded cover art (1:1 format)

Format: Pydantic model. Pretty print using Rich, summary of the whole process and the results.

### Process

```
# output
meta: [Metadata] = []

playlist = get_playlist()
for each track in playlist.track
  if track is ATV (@atv_get_playlist.json)
    album = get_album(track.album) (@atv_get_album.json)
  else if track is OMV (@omv_get_playlist.json)
    enriched_track = search("{track.artist} {track.title})[0]
    album = get_album(track.album) (@atv_get_album.json)
  meta[track].title = album[track].title
  meta[track].artist = album[track].artists
  meta[track].album = album[track].album
  meta[track].albumartist = album.artists
  meta[track].tracknumber = album[track].trackNumber
  meta[track].year = album.year
```
