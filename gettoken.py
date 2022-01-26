#!/usr/bin/python3

import base64, csv, datetime, os, requests
import http.server
import socket

client_id_file = 'data/clientid.txt'
client_secret_file = 'data/clientsecret.txt'
code_file = 'data/code.txt'
#access_token,expiry_time,refresh_token
tokens_file = 'data/tokens.csv'
token_url = 'https://accounts.spotify.com/api/token'
redirect_uri = 'http://localhost:8888/',
code_uri = 'https://accounts.spotify.com/authorize?response_type=code&client_id=b43dfe37ba294ff1a7458a076722d9fd&scope=user-read-private%20user-read-email%20playlist-read-private%20playlist-read-collaborative&redirect_uri=http%3A%2F%2Flocalhost%3A8888%2F'

def get_token(client_id, client_secret):
    auth_header = b'Basic ' + base64.standard_b64encode((client_id+':'+client_secret).encode('utf-8'))
    resp = requests.post(url=token_url,headers={'Content-Type':'application/x-www-form-urlencoded','Authorization':auth_header},data={'grant_type':'client_credentials'})
    resp.json()
    token = resp.json()['access_token']
    return token

def get_code(filename):
    idfd = os.open(filename,0)
    code_bytes = os.read(idfd,1000)
    os.close(idfd)
    return code_bytes.decode('utf-8').rstrip()

def get_client_id(filename):
    idfd = os.open(filename,0)
    client_id_bytes = os.read(idfd,1000)
    os.close(idfd)
    return client_id_bytes.decode('utf-8').rstrip()

def get_client_secret(filename):
    idfd = os.open(filename,0)
    client_id_bytes = os.read(idfd,1000)
    os.close(idfd)
    return client_id_bytes.decode('utf-8').rstrip()

def get_code():
    print('enter this in your browser and login spotify')
    print(code_uri)
    s = socket.socket()
    s.bind(('',8888))
    s.listen(1)
    conn, addr = s.accept()
    print('recevied callback from')
    print(addr)
    data = conn.recv(1024*10).decode('utf-8')
    url = data.split(' ')[1]
    code = url.split('=')[1]
    return code

def get_client_token(client_id, client_secret, code):
    auth_header = b'Basic ' + base64.standard_b64encode((client_id+':'+client_secret).encode('utf-8'))
    resp = requests.post(url=token_url,headers={'Content-Type':'application/x-www-form-urlencoded','Authorization':auth_header},data={'code':code,'redirect_uri':redirect_uri,'grant_type':'authorization_code'})
    token = resp.json()['access_token']
    refresh_token = resp.json()['refresh_token']
    expires_in = resp.json()['expires_in']
    expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
    return (token, refresh_token, expires_at)

def load_client_token(filename):
    ifd = open(filename, 'r')
    csvr = csv.DictReader(ifd,fieldnames=['token','refresh_token','expires_at'])
    token = None
    refresh_token = None
    expires_at = None
    for row in csvr:
        token = row['token']
        refresh_token = row['refresh_token']
        expires_at = row['expires_at']
    return token, refresh_token, datetime.datetime.strptime(expires_at,"%Y%m%d-%H%M%S")

def get_or_refresh_client_token(filename, client_id, client_secret):
    (client_token, refresh_token, expires_at) = load_client_token(filename)
    if client_token is None:
        code = get_code()
        (client_token, refresh_token, expires_at) = get_client_token(client_id,client_secret,code)
        save_client_token(tokens_file, client_token, refresh_token, expires_at)
        return client_token
    elif datetime.datetime.now() < expires_at:
        return client_token
    else:
        client_token, refresh_token, expires_at = get_client_token(client_id, client_secret, refresh_token)
        save_client_token(filename, client_token, refresh_token, expires_at)
        return client_token
        


def save_client_token(filename, token, refresh_token, expires_at):
    ofd = open(filename, 'a')
    ofd.write("%s,%s,%s\n"%(token,refresh_token,expires_at.strftime("%Y%m%d-%H%M%S")))
    ofd.close()

#curl --request GET 'https://api.spotify.com/v1/me/playlists' --header 'Authorization: Bearer BQAYJi8gi-2rXG4gcvUlTyiJqqcnGiyjVk6lu9JQ2CnIW7yj3ZWqsGA31K6Cfl1jIZlVx1jnTTWfLsfn9kbLbUl5c4_0dpm2qjgRqPRUIgBoA39o-rOfLvgiwXUvLJfNqW6D-xJXcplsBmVGLERyzP-HUflZqv5pW7CWsoYBySmDgfYmXw'
def get_playlists(client_token):
    auth_header = 'Authorization: Bearer ' + client_token
    resp = requests.get(url='https://api.spotify.com/v1/me/playlists', headers={'Authorization':auth_header})
    name_to_ids = {}
    for playlist in resp.json()['items']:
        name_to_ids[playlist['name']] = playlist['id']
        print('%s,%s'%(playlist['name'],playlist['id']))
    return name_to_ids

def get_playlist(client_token,playlist_id):
    auth_header = 'Authorization: Bearer ' + client_token
    resp = requests.get(url='https://api.spotify.com/v1/playlists/%s'%(playlist_id), headers={'Authorization':auth_header})
    print(resp.json())
    ids = []
    for item in resp.json()['tracks']['items']:
        ids.append(item['track']['id'])
    return ids

def main():
    client_id = get_client_id(client_id_file)
    client_secret = get_client_secret(client_secret_file)
    app_token = get_token(client_id,client_secret)
    print('app_token: ' + app_token)
    client_token = get_or_refresh_client_token(tokens_file, client_id, client_secret)
    name_to_ids = get_playlists(client_token)
    playlist_id = name_to_ids['132']
    ids = get_playlist(client_token,playlist_id)
    ofd = open('132.m3u8','w')
    ofd.write('#\n')
    for sid in ids:
        ofd.write('sptf://spotify:track:%s\n'%(sid))
    ofd.close()


if __name__=="__main__":
    main()