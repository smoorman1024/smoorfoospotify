# SmoorFooSpotify
## About
This application is intended to pull your specified spotify playlists from your personal Spotify account into a file format that Foobar2000 can read in.
## Relevant Links
- [Spotify](https://open.spotify.com/)
- [Spotify Developer Portal](https://developer.spotify.com/dashboard/applications)
- [Spotify Developer Documentation](https://developer.spotify.com/documentation/)
- [Foobar2000](https://www.foobar2000.org/)
- [Foobar2000 Spotify Integration Component](https://www.foobar2000.org/components/view/foo_spotify)
- [M3U File Format](https://en.wikipedia.org/wiki/M3U)
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

The first time you run the application will need to enter a URI into your browser which facillitates Spotify's authentication workflow. The URI will redirect you to a Spotify login and authorization for your application to have access to your playlists. When done the redirect URI is to your localhost:8888 where the application has a server running to receive the request. Your browser will show that the server did not resepond but that does not indicate an error. The application just needs to capture the request from Spotify in order to get an access token. On subsequent calls the application will either reuse the existing access token or refresh the token with Spotify.

```
smoorman@DESKTOP-3J1LNVU:~/dev/smoorfoospotify$ ./smoorfoospotify.py -p 124 -o data/124.m3u8 -c data/clientid.txt -s data/clientsecret.txt -t data/accesstokens.csv
enter this in your browser and login to spotify
https://accounts.spotify.com/authorize?response_type=code&scope=user-read-private%20user-read-email%20playlist-read-private%20playlist-read-collaborative&redirect_uri=http%3A%2F%2Flocalhost%3A8888%2F&client_id=b43dfe37ba294ff1a7458a076722d9fd
recevied callback from
('127.0.0.1', 58183)
Discover Weekly
133
132
131
...
```

The above snippet demonstrates the output from the initial client call. There is some debug information printed out when the redirect is received from the authorization. The application then lists the available playlists because the `-l` option is specified.
