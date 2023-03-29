from dataclasses import dataclass, field
import hashlib
from typing import List
from bencoding import decode, encode

def pieces_list_from_bytes(pieces_bytes: bytes):
    piece_size = 20 # each SHA-1 hash is 20 bytes
    pieces = [pieces_bytes[i:i+piece_size] for i in range(0, len(pieces_bytes), piece_size)]
    return pieces

@dataclass
class TorrentLog:
    bencoded_info : bytes # we don't have to decode that part when storing the torrent file as its details don't matter to the tracker when saving
    torrent_name : str
    announcements_logs : List[bytes] = field(default_factory=list) # we will log every announcement here.
    index: int = 0

    @property
    def info_hash(self):
        return hashlib.sha1(encode(decode(self.bencoded_info)[0][b'info'])).digest()

    @property
    def size(self):
        piece_size = self.bencoded_info[b'piece length']
        pieces_list = pieces_list_from_bytes(self.bencoded_info[b'pieces'])
        return piece_size * pieces_list
    
    @property
    def is_torrentx(self):
        return False
    

    def repack(self, new_announce_url):
        # that function will repack the bencoded torrent into a fitting bencode

        decoded = decode(self.bencoded_info)[0]
        decoded[b'announce'] = new_announce_url.encode()

        self.bencoded_info = encode(decoded)

    def get_peers(self):
        # if latest announcement is less than 30 minuts then now then we will count it as connected peer
        leechers = []
        seeders = []

        for announcement_log in self.announcements_logs:
            pass


"""
From that class we could store each torrent uploaded to our tracker. By looking into the announcement log, we could build a "peer announcement" list and by using that we could check if a peer sharing data is fake or not
"""

