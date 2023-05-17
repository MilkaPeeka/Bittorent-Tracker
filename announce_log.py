from dataclasses import dataclass
import datetime

@dataclass
class sAnnounceLog:
    log_time: datetime.datetime
    peer_ip: str
    port: int    
    event: str
    downloaded: int
    uploaded: int
    seeders: int = -1
    leechers: int = -1
    index: int = 0