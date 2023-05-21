"""
TODO:
1. add support for checking for torrentx in udp announce. that way we could get leechers in seeders when starting to announce

"""
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from logs_handler import LogHandler
from torrent_log import TorrentLog
import announce_tests
import socket
import threading
import asyncio
import udp_announce
import hashlib
import time
import json
import pathlib
from users import Users, return_json
import itertools

settings = None
settings_path = pathlib.Path("settings.json")
if settings_path.exists():
    with open("settings.json", "r") as f:
        settings = json.load(f)
    threading.Thread(target=udp_announce.start, args=(settings,)).start()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'   
lh = LogHandler("logs.db")

lh.start_update_loop()


def _async_tests():
    print("started test thread")
    while True:
        asyncio.run(announce_tests.main_loop(lh.get_torrents(), lh))
        time.sleep(30 * 60)


threading.Thread(target=_async_tests).start()


def format_size(size_in_bytes):
    # Define the units and their corresponding sizes in bytes
    units = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}
    # Initialize the size and unit
    size = size_in_bytes
    unit = "B"
    # Loop through the units, dividing the size by 1024 until it's less than 1024
    for unit_name, unit_size in units.items():
        if size < 1024:
            unit = unit_name
            break
        size /= 1024
    # Return the size with the appropriate unit
    return f"{size:.2f} {unit}"

def filter_last_entry_by_peer_ip(announce_log_list):
    # Sort the list by peer_ip and log_time
    announce_log_list_sorted = sorted(announce_log_list, key=lambda x: (x.peer_ip, x.log_time))
    
    # Group the list by peer_ip
    grouped_by_peer_ip = itertools.groupby(announce_log_list_sorted, key=lambda x: x.peer_ip)
    
    # Create a new list with only the last entry of each unique peer_ip
    last_entry_list = [list(group)[-1] for key, group in grouped_by_peer_ip]
    
    return last_entry_list


def get_leechers_count(torrent):
    last_entry_for_every_peer_ip = filter_last_entry_by_peer_ip(torrent.announcements_logs)
    count = 0
    for announce_log in last_entry_for_every_peer_ip:
        if announce_log.downloaded < torrent.size:
            count+=1

    return count

def get_seeders_count(torrent):
    last_entry_for_every_peer_ip = filter_last_entry_by_peer_ip(torrent.announcements_logs)
    count = 0
    for announce_log in last_entry_for_every_peer_ip:
        if announce_log.downloaded == torrent.size:
            count+=1

    return count
    

@app.route('/upload_torrent', methods=['GET', 'POST'])
def upload_torrent():
    if request.method == 'POST':
        torrent_file = request.files['torrent'].read()
        torrent_name = request.form['name']

        added_torrent_log = TorrentLog(torrent_file, torrent_name)
        new_ip = "udp://" + settings["IP"] +f':{settings["PORT"]}'
        added_torrent_log.repack(new_ip) # replacing whatever announce url with ours
        
        lh.add_torrent(added_torrent_log)
        
        response = make_response(added_torrent_log.bencoded_info)
        # Set the headers for the response
        response.headers.set('Content-Disposition', f'attachment; filename={torrent_name}-custom-.torrent')
        response.headers.set('Content-Type', 'application/bittorrent')

        return response
    else:
        return render_template('upload-torrent.html')

@app.route('/')
def show_torrents():
    if not settings_path.exists():
        return redirect(url_for('on_first_startup'))
    

    torrents = [{"name": torrent.torrent_name,
                 "size": format_size(torrent.size),
                 "is_torrentx": torrent.is_torrentx,
                 "leechers": get_leechers_count(torrent),
                 "seeders": get_seeders_count(torrent)} for torrent in lh.get_torrents()]
    
    # Render the template with the data
    return render_template("existing_torrents.html", torrents=torrents)


@app.route('/on_startup',  methods=['GET', 'POST'])
def on_first_startup():
    ip_address = socket.gethostbyname(socket.getfqdn())
    port = 9889
    interval = 600

    if request.method == 'POST':
        ip_address = request.form['ip_address']
        port = request.form['port']
        interval = request.form['interval']
        passw = request.form['admin_password']

        global settings

        settings = {"IP": ip_address,
                    "PORT": int(port),
                    "INTERVAL": int(interval),
                    "PASS_HASH": hashlib.sha256(passw.encode()).hexdigest()}
        
        with open(settings_path, "w") as f:
            json.dump(settings, f)

        threading.Thread(target=udp_announce.start, args=(settings,)).start()


        return redirect(url_for('show_torrents'))

    return render_template('startup.html', ip_address=ip_address, port=port, interval = interval)




@app.route('/delete/<torrent_name>', methods=['POST'])
def delete_torrent(torrent_name):
    entered_code = request.form.get('code')
    if hashlib.sha256(entered_code.encode()).hexdigest() != settings["PASS_HASH"]:
        flash("Incorrect code entered. Please try again.", "error")
    else:
        # delete the torrent
        t = None
        for torrent in lh.get_torrents():
            if torrent.torrent_name == torrent_name:
                t = torrent
            break
        lh.delete_torrent(t)
        flash("Torrent has been successfully deleted.", "success")
    
    return redirect(url_for('show_torrents'))

    

@app.route('/show_users')
def show_users():
    users_handler = Users(lh)
    users = return_json(users_handler.build_user_dict_from_torrents())
    return render_template('show_users.html', users=users)


    

@app.route('/download/<torrent_name>')
def download_requested_torrent(torrent_name):
    # Your code to download the torrent here

    t = None
    for torrent in lh.get_torrents():
        if torrent.torrent_name == torrent_name:
            t = torrent
            break
    

    response = make_response(t.bencoded_info)
    # Set the headers for the response
    response.headers.set('Content-Disposition', f'attachment; filename={torrent_name}-custom-.torrent')
    response.headers.set('Content-Type', 'application/bittorrent')

    return response
    


if __name__ == '__main__':
    app.run(debug=False, port=5000)