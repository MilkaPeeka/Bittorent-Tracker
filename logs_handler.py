from torrent_log import TorrentLog
from users import User
import time
from dctodb import dctodb
import threading
"""
Instead of taking care of torrent handling (getting sorted list, adding torrent to list and database, remove from list and database etc)
we will create a torrent handler that will take care of that in every operation
"""

class LogHandler:
    def __init__(self, db_filename) -> None:
        self.torrent_db = dctodb(TorrentLog, db_filename)
        self.torrent_list = self.torrent_db.action_to_db(self.torrent_db.fetch_all)

        self.user_db = dctodb(User, db_filename)
        self.user_list = self.torrent_db.action_to_db(self.user_db.fetch_all)

    def add_torrent(self, torrent_log: TorrentLog):
        old_index = torrent_log.index

        self.torrent_db.action_to_db(self.torrent_db.insert_one, torrent_log)

        if old_index != torrent_log.index:
            self.torrent_list.append(torrent_log)
            return True
        return False
    

    def add_user(self, user: User):
        old_index = user.index

        self.torrent_db.action_to_db(self.user_db.insert_one, user)

        if old_index != user.index:
            self.user_db.append(user)
            return True
        return False
    
    def get_users(self):
        return self.user_list
    
    def delete_torrent(self, to_delete):
        self.torrent_list.remove(to_delete)
        self.torrent_db.action_to_db(self.torrent_db.delete, to_delete)


    def get_torrents(self):
        return self.torrent_list
    
    def find_by_ip(self, ip):
        for user in self.user_list:
            if user.addr.split(':')[0] == ip:
                return ip
            
        return None


    def _update_loop(self):
        print("started io thread")
        while True:
            self.torrent_db.action_to_db(self.torrent_db.update, *self.torrent_list)
            self.user_db.action_to_db(self.user_db.update, *self.user_list)
            time.sleep(1)

    
    def start_update_loop(self):
        threading.Thread(target=self._update_loop).start()
    