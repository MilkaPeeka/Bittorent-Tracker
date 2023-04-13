from dataclasses import dataclass, field
import hashlib
from typing import List
from bencoding import decode, encode
from AnnounceLog import AnnounceLog
"""
TODO:
1. remove peers that are more than 2 hours old (4 announcements old)
2. implement a method to hold maximum of 96 announcements, not more (that's 48 hours of announcements which is enough to determine if a peer is fake or not)
"""

@dataclass
class TorrentLog:
    bencoded_info : bytes # we don't have to decode that part when storing the torrent file as its details don't matter to the tracker when saving
    torrent_name : str
    announcements_logs : List[AnnounceLog] = field(default_factory=list) # we will log every announcement here.
    index: int = 0

    @property
    def info_hash(self):
        return hashlib.sha1(encode(decode(self.bencoded_info)[0][b'info'])).digest()

    @property
    def size(self):
        decoded = decode(self.bencoded_info)[0][b'info']
        piece_size = decoded[b'piece length']
        pieces_list_len = len(decoded[b'pieces']) / 20 # total bytes divided by 20 bytes a piece hash
        return piece_size * pieces_list_len
    
    @property
    def is_torrentx(self):
        return False
    

    def repack(self, new_announce_url):
        # that function will repack the bencoded torrent into a fitting bencode
        decoded = decode(self.bencoded_info)[0]
        decoded[b'announce'] = new_announce_url.encode()
        self.bencoded_info = encode(decoded)


    def add_announcement(self, announcement : AnnounceLog):
        self.announcements_logs.append(announcement)

    def get_announcement_peers(self):
        group = dict()

        for announce in self.announcements_logs:
            if announce.peer_ip in group:
                group[announce.peer_ip].append(announce)
            
            else:
                group[announce.peer_ip] = [announce]

        return group


    def get_peers(self):
        
        return set(f'{announce.peer_ip}:{announce.port}' for announce in self.announcements_logs)


"""
From that class we could store each torrent uploaded to our tracker. By looking into the announcement log, we could build a "peer announcement" list and by using that we could check if a peer sharing data is fake or not
"""

