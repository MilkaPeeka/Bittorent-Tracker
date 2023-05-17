from logs_handler import LogHandler
from dataclasses import dataclass

@dataclass
class User:
    addr: str
    fake_ratio: int = 0
    tests_count: int = 0
    index: int = 0


class Users:
    def __init__(self, log_handler: LogHandler, user_handler: UserHandler) -> None:
        self.log_handler = log_handler
        self.user_handler = user_handler

    def test_users(self):
        
            get_announcement_peers

    def build_user_dict_from_torrents(self):
        # builds the user list from torrents

        users = {user:list() for user in self.user_handler.get_users()}
        for torrent in self.log_handler.get_torrents():
            for peer in torrent.get_peers():
                if peer in [user.addr for user in users.keys()]:
                    self.users[peer].append(torrent)
                else:
                    # we will create a user object if thats a new peer
                    self.users[peer] = [torrent]
                    self.user_handler.add(User(peer))

        return users
        

def return_json(users_dict):
    users = []

    for user, torrents in users_dict.items():
        users.append({
            'ip': user.addr,
            'fake_precent': round(user.fake_ratio * 100 , 2),
            'shared_torrents': torrents
        })

    return users