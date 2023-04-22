from logs_handler import LogHandler

class User:
    def __init__(self, addr) -> None:
        self.addr = addr
        self.torrents_in_share = []

    def add_torrent(self, torrent_name):
        self.torrents_in_share.append(torrent_name)

class Users:
    def __init__(self, log_handler : LogHandler) -> None:
        self.log_handler = log_handler

    def users_test(self):
        # runs a test on every user 
        pass

    def build_user_list_from_torrents(self):
        # builds the user list from torrents
        total_addrs = []

        for torrent in self.log_handler.get_torrents():
            total_addrs += torrent.get_peers()
        
        
        total_addrs = set(total_addrs)

        user_list = [User(addr) for addr in total_addrs]

        for user in user_list:
            for torrent in self.log_handler.get_torrents():
                if user.addr in torrent.get_peers():
                    user.add_torrent(torrent.torrent_name)


        return user_list
    

def return_json(user_list):
    users = []

    for user in user_list:
        users.append({
            'ip': user.addr,
            'fake_precent': 0.0,
            'shared_torrents': user.torrents_in_share
        })

    return users