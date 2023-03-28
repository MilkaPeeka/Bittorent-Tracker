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
app.templates_auto_reload = 10

fh = FileHandler("logs_db.py")

@app.route('/announce/')
def announce():
    qs = request.query_string
    qs = urllib.parse.unquote(qs)
    # qs = qs.replace("%", "%25")
    # qs = qs.replace("\ufffd", r"")
    qs = urllib.parse.parse_qs(qs)
    info_hash = qs['info_hash'][0]
    hex_info_hash = binascii.hexlify(info_hash.encode())
    print(hex_info_hash)
    return qs



    encoded_info_hash_url = urllib.parse.unquote(encoded_info_hash_url)
    encoded_info_hash_url = encoded_info_hash_url.replace('%', '%25')
    hex_info_hash = binascii.hexlify(encoded_info_hash_url.encode('utf-8')).decode('ascii')
    return hex_info_hash

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