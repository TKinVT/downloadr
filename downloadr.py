import deluge
import os
from dotenv import load_dotenv
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, reqparse

load_dotenv()

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

parser = reqparse.RequestParser()
parser.add_argument('magnet_url')
parser.add_argument('torrent_id')

# auth stuff
users = {
    "bot": os.getenv("BOT_PASSWORD")
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        if password == users[username]:
            return True
    return False

# gets info about particular torrent, deletes a torrent
class Torrent(Resource):
    @auth.login_required
    def get(self, torrent_id):
        return deluge.get_torrent_status(torrent_id)

    @auth.login_required
    def delete(self, torrent_id):
        deluge.remove_torrent(torrent_id)
        return '', 204

# gets a list of all torrents, posts a new torrent
class Torrents(Resource):
    @auth.login_required
    def get(self):
        torrents = deluge.get_torrents_list()
        results = {}
        for torrent in torrents:
            results[torrent] = deluge.get_torrent_status(torrent)
        return results

    @auth.login_required
    def post(self):
        args = parser.parse_args()
        torrent_id = deluge.add_torrent_url(args['magnet_url'])
        # status = deluge.get_torrent_status(torrent_id)
        return torrent_id, 201

api.add_resource(Torrents, '/')
api.add_resource(Torrent, '/<torrent_id>')

if __name__ == '__main__':
    app.run(debug=True)
