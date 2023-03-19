from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main-page.html')

@app.route('/upload_torrent', methods=['GET', 'POST'])
def upload_torrent():
    if request.method == 'POST':
        torrent_file = request.files['torrent']
        torrent_name = request.form['name']
        # do something with the uploaded file and form data
        return "Torrent uploaded successfully."
    else:
        # display form
        return render_template('upload-torrent.html')

@app.route('/show_torrents')
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