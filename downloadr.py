import deluge
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('magnet_url')
parser.add_argument('torrent_id')

# gets info about particular torrent, deletes a torrent
class Torrent(Resource):
    def get(self, torrent_id):
        return deluge.get_torrent_status(torrent_id)

    def delete(self, torrent_id):
        deluge.remove_torrent(torrent_id)
        return '', 204

# gets a list of all torrents, posts a new torrent
class Torrents(Resource):
    def get(self):
        torrents = deluge.get_torrents_list()
        results = {}
        for torrent in torrents:
            results[torrent] = deluge.get_torrent_status(torrent)
        return results

    def post(self):
        args = parser.parse_args()
        torrent_id = deluge.add_torrent_url(args['magnet_url'])
        # status = deluge.get_torrent_status(torrent_id)
        return torrent_id, 201

api.add_resource(Torrents, '/')
api.add_resource(Torrent, '/<torrent_id>')

if __name__ == '__main__':
    app.run(debug=True)
