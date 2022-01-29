#!/usr/bin/python3

import base64, csv, datetime, getopt, os, requests, sys
import http.server
import socket

client_id_file_default = 'data/clientid.txt'
client_secret_file_default = 'data/clientsecret.txt'
code_file = 'data/code.txt'
#access_token,expiry_time,refresh_token
tokens_file_default = 'data/tokens.csv'
token_url = 'https://accounts.spotify.com/api/token'
redirect_uri = 'http://localhost:8888/',
code_uri = 'https://accounts.spotify.com/authorize?response_type=code&scope=user-read-private%20user-read-email%20playlist-read-private%20playlist-read-collaborative&redirect_uri=http%3A%2F%2Flocalhost%3A8888%2F&client_id='

def get_token(client_id, client_secret):
    auth_header = b'Basic ' + base64.standard_b64encode((client_id+':'+client_secret).encode('utf-8'))
    resp = requests.post(url=token_url,headers={'Content-Type':'application/x-www-form-urlencoded','Authorization':auth_header},data={'grant_type':'client_credentials'})
    resp.json()
    token = resp.json()['access_token']
    return token

def get_code_from_file(filename):
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

def get_code(client_id):
    print('enter this in your browser and login to spotify')
    code_uri_with_client_id = code_uri + client_id
    print(code_uri_with_client_id)
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

def refresh_client_token(client_id, client_secret, refresh_token):
    auth_header = b'Basic ' + base64.standard_b64encode((client_id+':'+client_secret).encode('utf-8'))
    resp = requests.post(url=token_url,headers={'Content-Type':'application/x-www-form-urlencoded','Authorization':auth_header},data={'refresh_token':refresh_token,'grant_type':'refresh_token'})
    token = resp.json()['access_token']
    refresh_token = None
    if 'refresh_token' in resp.json():
        refresh_token = resp.json()['refresh_token']
    expires_in = resp.json()['expires_in']
    expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
    return (token, refresh_token, expires_at)

def get_client_token(client_id, client_secret, code):
    auth_header = b'Basic ' + base64.standard_b64encode((client_id+':'+client_secret).encode('utf-8'))
    resp = requests.post(url=token_url,headers={'Content-Type':'application/x-www-form-urlencoded','Authorization':auth_header},data={'code':code,'redirect_uri':redirect_uri,'grant_type':'authorization_code'})
    token = resp.json()['access_token']
    refresh_token = resp.json()['refresh_token']
    expires_in = resp.json()['expires_in']
    expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
    return (token, refresh_token, expires_at)

def load_client_token(filename):
    if not os.path.exists(filename):
        return None
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
    t = load_client_token(filename)
    if t is None:
        code = get_code(client_id)
        (client_token, refresh_token, expires_at) = get_client_token(client_id,client_secret,code)
        save_client_token(tokens_file, client_token, refresh_token, expires_at)
        return client_token
    (client_token, refresh_token, expires_at) = t
    if datetime.datetime.now() < expires_at:
        return client_token
    else:
        client_token, new_refresh_token, expires_at = refresh_client_token(client_id, client_secret, refresh_token)
        if new_refresh_token is None:
            new_refresh_token = refresh_token
        save_client_token(filename, client_token, new_refresh_token, expires_at)
        return client_token
        


def save_client_token(filename, token, refresh_token, expires_at):
    ofd = open(filename, 'a')
    ofd.write("%s,%s,%s\n"%(token,refresh_token,expires_at.strftime("%Y%m%d-%H%M%S")))
    ofd.close()

#curl --request GET 'https://api.spotify.com/v1/me/playlists' --header 'Authorization: Bearer B...w'
def get_playlists(client_token):
    auth_header = 'Authorization: Bearer ' + client_token
    resp = requests.get(url='https://api.spotify.com/v1/me/playlists', headers={'Authorization':auth_header})
    name_to_ids = {}
    for playlist in resp.json()['items']:
        name_to_ids[playlist['name']] = playlist['id']
    return name_to_ids

def get_playlist(client_token,playlist_id):
    auth_header = 'Authorization: Bearer ' + client_token
    resp = requests.get(url='https://api.spotify.com/v1/playlists/%s'%(playlist_id), headers={'Authorization':auth_header})
    ids = []
    for item in resp.json()['tracks']['items']:
        ids.append(item['track']['id'])
    return ids

def usage():
    print("Save a playlist: %s -p|--playlist playlist_name -o|--output output_name [-c|--clientid clientid.txt] [-s|--clientsecret clientsecret.txt] [-t|--tokens tokens.csv]"%(sys.argv[0]),file=sys.stderr)
    print("List playlists: %s -l|--list [-c|--clientid clientid.txt] [-s--clientsecret clientsecret.txt] [-t|--tokens tokens.csv]"%(sys.argv[0]),file=sys.stderr)

def main():

    playlist_name = None
    output_name = None
    client_id_file = None
    client_secret_file = None
    tokens_file = None
    do_list = False
    opts, args = getopt.getopt(sys.argv[1:],"c:s:p:o:t:l",["clientid=","clientsecret=","playlist=","output=","tokens=","list"])
    for o,a in opts:
        if o in ["-c","--clientid"]:
            client_id_file = a
        elif o in ["-s","--clientsecret"]:
            client_secret_file = a
        elif o in ["-p","--playlist"]:
            playlist_name = a
        elif o in ["-o","--output"]:
            output_name = a
        elif o in ["-t","--tokens"]:
            tokens_file = a
        elif o in ["-l","--list"]:
            do_list = True
    if not do_list:
        if playlist_name is None:
            usage()
            print('-p|--playlist required',file=sys.stderr)
            sys.exit(1)
        if output_name is None:
            usage()
            print('-o|--output required',file=sys.stderr)
            sys.exit(1)
    if client_id_file is None:
        client_id_file = client_id_file_default
    if client_secret_file is None:
        client_secret_file = client_secret_file_default
    if tokens_file is None:
        tokens_file = tokens_file_default

    # get app token
    client_id = get_client_id(client_id_file)
    client_secret = get_client_secret(client_secret_file)
    app_token = get_token(client_id,client_secret)
    # get client token
    client_token = get_or_refresh_client_token(tokens_file, client_id, client_secret)
    # get a map of all playlist names to their ids
    name_to_ids = get_playlists(client_token)
    if do_list:
        for name in name_to_ids.keys():
            print(name)
    else:
        playlist_id = name_to_ids[playlist_name]
        ids = get_playlist(client_token,playlist_id)
        ofd = open(output_name,'w')
        ofd.write('#\n')
        for sid in ids:
            ofd.write('sptf://spotify:track:%s\n'%(sid))
        ofd.close()


if __name__=="__main__":
    main()
