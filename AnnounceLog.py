from dataclasses import dataclass
import datetime
@dataclass
class AnnounceLog:
    log_time: datetime.datetime
    peer_ip: str
    port: int    
    event: str
    downloaded: int
    uploaded: int
    seeders: int
    leechers: int
    index: int = 0