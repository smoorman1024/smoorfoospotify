# SmoorFooSpotify
## About
This application is intended to pull your specified spotify playlists from your personal Spotify account into a file format that Foobar2000 can read in.
## Relevant
[Spotify](https://open.spotify.com/)
[Spotify Developer Portal](https://developer.spotify.com/dashboard/applications)
[Spotify Developer Documentation](https://developer.spotify.com/documentation/)
[Foobar2000](https://www.foobar2000.org/)
[Foobar2000 Spotify Integration Component](https://www.foobar2000.org/components/view/foo_spotify)
[M3U File Format](https://en.wikipedia.org/wiki/M3U)
## Usage
```
Save a playlist: ./smoorfoospotify.py -p|--playlist playlist_name -o|--output output_name [-c|--clientid clientid.txt] [-s|--clientsecret clientsecret.txt] [-t|--tokens tokens.csv]
List playlists: ./smoorfoospotify.py -l|--list [-c|--clientid clientid.txt] [-s--clientsecret clientsecret.txt] [-t|--tokens tokens.csv]
```
- `playlist_name` the name of the playlist you wish to save
- `output` the output file you wish to save the playlist to
- `clientid` path to a file which is a single line entry of the client id for your spotify app which you have authorized. Default: data/clientid.txt
- `clientsecret` path to a file which is a single line entry of the client secret for your spotify app which you have authorized. Default: data/clientsecret.txt
- `tokens` path to a file which either contains or will be written to access and refresh tokens
## Getting Started
In order for the application to be able to access your playlists you will need to create a Spotify application which you have authorized your own spotify account as permitted to access it. See [Spotify Web API quick start](https://developer.spotify.com/documentation/web-api/quick-start/).

