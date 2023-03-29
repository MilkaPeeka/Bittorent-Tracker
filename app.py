"""
TODO:

1. Add support for displaying size
2. Store torrents' data in a better manner
3. Uploading torrents and showing them in homescreen
4. Implement "torrent fakeness" tests for regular torrents
5. Implement the same for torrentx
6. Implement tracker url
"""

from flask import Flask, render_template, request, url_for, make_response
from FileHandler import FileHandler
from TorrentLog import TorrentLog
import urllib
import binascii
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

fh = FileHandler("logs.db")

def get_infohash_from_announce(full_log_in_bytes):
    full_log = full_log_in_bytes.decode('utf-8')

    info_hash_part = full_log.split('&')[0] # ?info_hash=mG%95%DE%E7%0a%EB%88%E0%3eS6%CA%7c%9F%CF%0a%1e%20m
    info_hash_part = info_hash_part.replace("info_hash=","")
    info_hash = info_hash_part.replace('$', '%24').upper()
    return info_hash


def get_torrent_from_info_hash(url_encoded_infohash):
    for torrent in fh.get_torrents():
        urlencoded = urllib.parse.quote(torrent.info_hash).upper()
        if urlencoded == url_encoded_infohash:
            return torrent
        
    return None

@app.route('/announce/')
def announce():
    announce_ip = request.remote_addr
    announce_log = request.args
    announced_torrent_info_hash = get_infohash_from_announce(request.query_string)
    torrent = get_torrent_from_info_hash(announced_torrent_info_hash)

    return "OK" if torrent else "NOT GOOD"


@app.route('/upload_torrent', methods=['GET', 'POST'])
def upload_torrent():
    if request.method == 'POST':
        torrent_file = request.files['torrent'].read()
        torrent_name = request.form['name']

        added_torrent_log = TorrentLog(torrent_file, torrent_name)
        added_torrent_log.repack(url_for('show_torrents', _external=True) + 'announce/') # replacing whatever announce url with ours
        fh.add_torrent(added_torrent_log)
        
        response = make_response(added_torrent_log.bencoded_info)
        # Set the headers for the response
        response.headers.set('Content-Disposition', f'attachment; filename={torrent_name}-TrackerVersion-.torrent')
        response.headers.set('Content-Type', 'application/bittorrent')

        return response
    else:
        return render_template('upload-torrent.html')

@app.route('/')
def show_torrents():
    torrents = [
        {"name": "Torrent 1", "size": "10 MB", "is_torrentx": True, "leechers": 5, "seeders": 2},
        {"name": "Torrent 2", "size": "5 GB", "is_torrentx": False, "leechers": 10, "seeders": 3},
        {"name": "Torrent 3", "size": "2.3 GB", "is_torrentx": True, "leechers": 2, "seeders": 8},
    ]
    
    # Render the template with the data
    return render_template("existing_torrents.html", torrents=torrents)

@app.route('/show_users')
def show_users():
    # Dummy user data for testing
    users = [
        {
            'ip': '192.168.1.1',
            'client': 'uTorrent',
            'fake_percent': 0.0,
            'shared_torrents': ['Movie1.torrent', 'Movie2.torrent']
        },
        {
            'ip': '192.168.1.2',
            'client': 'qBittorrent',
            'fake_percent': 10.5,
            'shared_torrents': ['TV1.torrent', 'TV2.torrent', 'Music1.torrent']
        },
        {
            'ip': '192.168.1.3',
            'client': 'Transmission',
            'fake_percent': 2.3,
            'shared_torrents': ['Movie1.torrent', 'Movie3.torrent', 'Game1.torrent']
        }
    ]
    
    return render_template('show_users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True, port=5000)