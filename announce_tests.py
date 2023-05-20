
from torrent_log import TorrentLog
from typing import List
from announce_log import AnnounceLog
import aioudp
import struct
import asyncio
import random

def gen_piece_hash_struct(torrent, index, offset, length):
    info_hash = torrent.info_hash

    return struct.pack("! i b 20s i i i 20s", 20 + 20 + 4 + 4 + 4 + 1, 3, info_hash, index, offset, length, bytes([0] * 20))


async def ask_and_wait_for_hash(peer_addr, piece_hash_msg):
    try:
        conn_with_peer = await asyncio.wait_for(aioudp.open_remote_endpoint(*peer_addr), 1)
    except TimeoutError:
        return None
    conn_with_peer.send(piece_hash_msg)
    await conn_with_peer.drain()

    try:
        res = await asyncio.wait_for(conn_with_peer.receive(), 1)
        return res
    
    except TimeoutError:
        return None
    

def get_announcements_in_a_row_with_matching_attribute(announce_log_list: List[AnnounceLog], attr: str, value: str) -> List[List[AnnounceLog]]:
    matching_announcements = []
    i = 0
    while i < len(announce_log_list) - 1:
        current_value = getattr(announce_log_list[i], attr)
        next_value = getattr(announce_log_list[i+1], attr)
        if current_value == value and next_value == current_value:
            j = i + 1
            while j < len(announce_log_list) - 1 and getattr(announce_log_list[j], attr) == current_value:
                j += 1
            matching_announcements.append(announce_log_list[i:j+1])
            i = j
        else:
            i += 1
    return matching_announcements

def calculate_time_difference_seconds(announce_log1: AnnounceLog, announce_log2: AnnounceLog) -> int:
    time_diff = announce_log2.log_time - announce_log1.log_time
    return int(time_diff.total_seconds())


async def main_loop(torrents, tu_handler):
    tasks = []
    for torrent in torrents:
        test = AnnounceTest(torrent, tu_handler)
        test.downloadChangeTooFast()
        test.uploadChangeTooFast()
        test.leecherUploadTest()
        test.seederDownloadTest()

        tasks.append(test.gather_hashes_for_torrent_test())
    
    await asyncio.gather(*tasks)

class AnnounceTest:
    def __init__(self, torrent: TorrentLog, torrent_user_handler) -> None:
        self.torrent = torrent
        self.leechers_threshold = 2 # abritary number 
        self.seeders_threshold = 4 # abritary number
        self.torrent_user_handler = torrent_user_handler


    async def gather_hashes_for_torrent_test(self):
        pieces_amount = self.torrent.piece_list_len
        piece_size = self.torrent.piece_size
        index = random.randint(0, pieces_amount - 1) # we will never ask for last piece because it may be shorter than regular piece size
        offset = random.randint(0, piece_size) 
        length = random.randint(0, piece_size - offset) # we will want the offset + chosen length < piece size

        piece_hash_msg = gen_piece_hash_struct(self.torrent, index, offset, length)


        tasks = [ask_and_wait_for_hash(peer.split(':'), piece_hash_msg) for peer in self.torrent.get_peers()]

        results = await asyncio.gather(*tasks)

        if not results:
            return None

        hash_counts = {}
        for result in results:
            if result is None:
                continue

            if result in hash_counts:
                hash_counts[result] += 1
            else:
                hash_counts[result] = 1

        most_common_hash = max(hash_counts, key=hash_counts.get)
        
        if hash_counts[most_common_hash] < (len([result for result in results if result is not None]) / 2):
            print("too many unhonest peers, cant determine nothing")
            return
        
        peer_result = dict()
        
        for result, peer in zip(results, self.torrent.get_peers()):
            if result is None:
                continue

            ip = peer.split(':')[0]
            self.torrent_user_handler.find_by_ip(ip).add_test(result == most_common_hash)
        
        return peer_result

    def leecherUploadTest(self):
        # when torrent uploads data yet there are no leechers
        # how can we test for that? if there are 2+ announcements in a row when there are no leechers and the data is being uploaded
        # hole: if a torrent is small or upload is fast - there can be uploads that wont be recorded in the announcement

        # we will iterate over each peer in torrent list
        # we will get all announecements for every peer
        # if it says "leechers - 0" yet our upload data changed we will fail him


        for peer_ip, peer_announcements in self.torrent.get_announcement_peers().items():
            announcements_in_a_row = get_announcements_in_a_row_with_matching_attribute(peer_announcements, 'leechers', 0)

            if not announcements_in_a_row:
                self.torrent_user_handler.find_by_ip(peer_ip).add_test(True)
                continue

            total_upload_data_set = set()
            for res in announcements_in_a_row:
                total_upload_data_set.add(res.uploaded)


            if len(total_upload_data_set) != 1:
                self.torrent_user_handler.find_by_ip(peer_ip).add_test(False)


            else:
                self.torrent_user_handler.find_by_ip(peer_ip).add_test(True)

    def seederDownloadTest(self):
        # when torrent downloads yet there are no seeders
        # how can we test for that? just as previous function - we will test with the same principals but checking for seeders\downloaded attributes

        for peer_ip, peer_announcements in self.torrent.get_announcement_peers().items():
            announcements_in_a_row = get_announcements_in_a_row_with_matching_attribute(peer_announcements, 'seeders', 0)

            if not announcements_in_a_row:
                self.torrent_user_handler.find_by_ip(peer_ip).add_test(True)
                continue

            total_upload_data_set = set()
            for res in announcements_in_a_row:
                total_upload_data_set.add(res.uploaded)


            if len(total_upload_data_set) != 1:
                self.torrent_user_handler.find_by_ip(peer_ip).add_test(False)


            else:
                self.torrent_user_handler.find_by_ip(peer_ip).add_test(True)

    def downloadChangeTooFast(self):
        threshold_seeder_avarage = self.seeders_threshold 

        threshold_avarage_download_speed_in_torrent_in_second = 2**20 # abritary number. 1MB.


        for i in range(len(self.torrent.announcements_logs) - 1):
            record = self.torrent.announcements_logs[i]
            next_record = self.torrent.announcements_logs[i+1]
            time_diff = calculate_time_difference_seconds(record, next_record)
            
            should_be_downloaded = threshold_avarage_download_speed_in_torrent_in_second * time_diff

            # if that number is too high we will check how many seeders there were in the first record
            if should_be_downloaded < next_record.downloaded - record.downloaded:
                # check for how many seeders there are
                if next_record.seeders < threshold_seeder_avarage:
                    ip = next_record.peer_ip
                    self.torrent_user_handler.find_by_ip(ip).add_test(False)
                else:
                    self.torrent_user_handler.find_by_ip(ip).add_test(True)

    
    def uploadChangeTooFast(self):
        threshold_leecher_avarage = self.leechers_threshold

        threshold_avarage_upload_speed_in_torrent_in_second = 4000 # just an abritray number for now. in bytes.


        for i in range(len(self.torrent.announcements_logs) - 1):
            record = self.torrent.announcements_logs[i]
            next_record = self.torrent.announcements_logs[i+1]
            time_diff = calculate_time_difference_seconds(record, next_record)
            
            should_be_uploaded = threshold_avarage_upload_speed_in_torrent_in_second * time_diff

            # if that number is too high we will check how many seeders there were in the first record
            if should_be_uploaded < next_record.uploaded - record.uploaded:
                # check for how many seeders there are
                if next_record.leechers < threshold_leecher_avarage:
                    ip = next_record.peer_ip
                    self.torrent_user_handler.find_by_ip(ip).add_test(False)
                else:
                    self.torrent_user_handler.find_by_ip(ip).add_test(True)
