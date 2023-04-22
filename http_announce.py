"""
Discarded - most tracker only support udp announce.
The way I achieved http announce was too cumbersome anyways
"""


# @app.route('/announce/')
# def announce():
#     announce_ip = request.remote_addr
#     announce_log = get_relevant_info_from_announce(request.query_string)
#     announced_torrent_info_hash = get_infohash_from_announce(request.query_string)
#     torrent = get_torrent_from_info_hash(announced_torrent_info_hash)

#     # First we will update the torrent witht the announce content and then return a response
    
#     newly_announced = AnnounceLog(datetime.datetime.now(), announce_ip, *announce_log)

#     torrent.add_announcement(newly_announced)

#     print(torrent.get_announcement_peers())
#     print(torrent.get_peers())

#     return return_response()




# import urllib
# from logs_handler import LogHandler

# lh = LogHandler("logs.db")

# def get_infohash_from_announce(full_log_in_bytes):
#     full_log = full_log_in_bytes.decode('utf-8')

#     info_hash_part = full_log.split('&')[0] # ?info_hash=mG%95%DE%E7%0a%EB%88%E0%3eS6%CA%7c%9F%CF%0a%1e%20m
#     info_hash_part = info_hash_part.replace("info_hash=","")
#     info_hash = info_hash_part.replace('$', '%24').upper()
#     return info_hash


# def get_torrent_from_info_hash(url_encoded_infohash):
#     for torrent in lh.get_torrents():
#         urlencoded = urllib.parse.quote(torrent.info_hash).upper()
#         if urlencoded == url_encoded_infohash:
#             return torrent
        
#     return None


# def return_response():
#     # need to return interval and a peer list
#     to_ret = {
#         "interval": settings.INTERVAL,

#         "peers": 
#             {"ip": "127.0.0.1",
#             "port": 25565}


#     }

#     return encode(to_ret)

# def get_relevant_info_from_announce(full_log_in_bytes):
#     full_log = full_log_in_bytes.decode('utf-8')
#     # need to save event, uploaded, downloaded
#     uploaded = re.search(r'&uploaded=([0-9]+)', full_log).group(1)
#     port = re.search(r'&port=([0-9]+)', full_log).group(1)
#     downloaded = re.search(r'&downloaded=([0-9]+)', full_log).group(1)
#     event = re.search(r'&event=([a-zA-Z]+)', full_log)
#     if event:
#         event = event.group(1)
#     else:
#         event = "resume"

#     return int(port), event, int(uploaded), int(downloaded)
    
