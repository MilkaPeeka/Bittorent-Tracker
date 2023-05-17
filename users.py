from dataclasses import dataclass

@dataclass
class User:
    addr: str
    fake_ratio: int = 0
    test_successes: int = 0 
    test_failures: int = 0
    index: int = 0

    def add_test(self, test_res):
        if test_res == True:
            self.test_successes += 1
        else:
            self.test_successes += 1

        self.fake_ratio = self.test_failures / (self.test_failures + self.test_successes)


class Users:
    def __init__(self, torrent_log_and_user_handler) -> None:
        self.torrent_log_and_user_handler = torrent_log_and_user_handler


    def build_user_dict_from_torrents(self):
        # builds the user list from torrents

        users = {user:list() for user in self.torrent_log_and_user_handler.get_users()}
        for torrent in self.torrent_log_and_user_handler.get_torrents():
            for peer in torrent.get_peers():
                if peer in [user.addr for user in users.keys()]:
                    self.users[peer].append(torrent)
                else:
                    # we will create a user object if thats a new peer
                    self.users[peer] = [torrent]
                    self.torrent_log_and_user_handler.add_user(User(peer))

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