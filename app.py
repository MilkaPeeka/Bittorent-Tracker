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
from logs_handler import LogHandler
from TorrentLog import TorrentLog
from AnnounceLog import AnnounceLog
import re
import urllib
import datetime
from bencoding import encode
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'   
IPAddr="192.168.1.41"  
announce_port = 25565

lh = LogHandler("logs.db")

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


def return_response():
    # need to return interval and a peer list
    to_ret = {
        "interval": 1800,

        "peers": 
            {"ip": "127.0.0.1",
            "port": 25565}


    }

    return encode(to_ret)

def get_relevant_info_from_announce(full_log_in_bytes):
    full_log = full_log_in_bytes.decode('utf-8')
    # need to save event, uploaded, downloaded
    uploaded = re.search(r'&uploaded=([0-9]+)', full_log).group(1)
    port = re.search(r'&port=([0-9]+)', full_log).group(1)
    downloaded = re.search(r'&downloaded=([0-9]+)', full_log).group(1)
    event = re.search(r'&event=([a-zA-Z]+)', full_log)
    if event:
        event = event.group(1)
    else:
        event = "resume"

    return int(port), event, int(uploaded), int(downloaded)
    


@app.route('/announce/')
def announce():
    announce_ip = request.remote_addr
    announce_log = get_relevant_info_from_announce(request.query_string)
    announced_torrent_info_hash = get_infohash_from_announce(request.query_string)
    torrent = get_torrent_from_info_hash(announced_torrent_info_hash)

    # First we will update the torrent witht the announce content and then return a response
    
    newly_announced = AnnounceLog(datetime.datetime.now(), announce_ip, *announce_log)

    torrent.add_announcement(newly_announced)

    print(torrent.get_announcement_peers())
    print(torrent.get_peers())

    return return_response()


@app.route('/upload_torrent', methods=['GET', 'POST'])
def upload_torrent():
    if request.method == 'POST':
        torrent_file = request.files['torrent'].read()
        torrent_name = request.form['name']

        added_torrent_log = TorrentLog(torrent_file, torrent_name)
        added_torrent_log.repack("udp://" + IPAddr +f':{announce_port}') # replacing whatever announce url with ours
        lh.add_torrent(added_torrent_log)
        
        response = make_response(added_torrent_log.bencoded_info)
        # Set the headers for the response
        response.headers.set('Content-Disposition', f'attachment; filename={torrent_name}-TrackerVersion-.torrent')
        response.headers.set('Content-Type', 'application/bittorrent')

        return response
    else:
        return render_template('upload-torrent.html')

@app.route('/')
def show_torrents():
    torrents = [{"name": torrent.torrent_name,
                 "size": torrent.size,
                 "is_torrentx": torrent.is_torrentx,
                 "leechers": 4,
                 "seeders": 3} for torrent in lh.get_torrents()]
    
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