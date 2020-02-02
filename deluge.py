import os
import requests
from dotenv import load_dotenv
load_dotenv()

# For reference!
# https://deluge.readthedocs.io/en/latest/devguide/how-to/curl-jsonrpc.html
# https://deluge.readthedocs.io/en/latest/reference/api.html

URL = os.getenv("DELUGE_URL")
PASSWORD = os.getenv("DELUGE_PASSWORD")
HEADERS = {"Accept": "application/json"}


def deluge_login_cookie():
    payload = {"method": "auth.login", "params": [PASSWORD], "id": 1}
    login = requests.post(URL, headers=HEADERS, json=payload)
    session_id = login.cookies["_session_id"]
    cookie = {"_session_id": session_id}

    return cookie


def test_connection():
    auth_cookie = deluge_login_cookie()
    payload = {"method": "web.connected", "params": [], "id": 1}
    r = requests.post(URL, headers=HEADERS, cookies=auth_cookie, json=payload)
    connection = r.json()['result']

    return connection


def get_host():
    auth_cookie = deluge_login_cookie()
    payload = {"method": "web.get_hosts", "params": [], "id": 1}
    r = requests.post(URL, headers=HEADERS, cookies=auth_cookie, json=payload)
    host_id = r.json()['result'][0][0]

    return host_id


def connect_host(host_id):
    auth_cookie = deluge_login_cookie()
    payload = {"method": "web.connect", "params": [host_id], "id": 1}
    r = requests.post(URL, headers=HEADERS, cookies=auth_cookie, json=payload)
    error = r.json()['error']

    return error


def ensure_connection():
    test = test_connection()
    if not test:
        host = get_host()
        connect_host(host)


def make_request(method, params):
    ensure_connection()
    auth_cookie = deluge_login_cookie()
    payload = {"method": method, "id": 1, "params": params}
    r = requests.post(URL, headers=HEADERS, cookies=auth_cookie, json=payload)

    return r


def add_torrent_url(magnet_url):
    method = "core.add_torrent_magnet"
    params = [magnet_url, {}]
    r = make_request(method, params)
    torrent_id = r.json()['result']

    return torrent_id


def remove_torrent(torrent_id):
    method = "core.remove_torrent"
    params = [torrent_id, True]
    r = make_request(method, params)

    return r


def get_torrent_status(torrent_id):
    method = "core.get_torrent_status"
    params = [torrent_id, {}]
    r = make_request(method, params)

    return r.json()['result']


def get_torrents_list():
    method = "core.get_session_state"
    params = []
    r = make_request(method, params)
    torrent_ids = r.json()['result']

    return torrent_ids


if __name__ == '__main__':

    list = get_torrents_list()
    for t in list:
        r = get_torrent_status(t)
        print("progress: {}".format(r['progress']))
        print("name: {}".format(r['name']))
