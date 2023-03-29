from dataclasses import dataclass

@dataclass
class AnnounceLog:
    log_time: None
    query_string: str
    peer_ip: str 