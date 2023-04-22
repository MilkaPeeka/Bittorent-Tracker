"""
We have a total of 96 announcements (48 hours of announcements)

Assumptions:
1. 

Suggested tests:

1. If upload when there are no leechers #DONE
2. If download with no seeders #DONE
3. If consistently downloading fast with not a lot of seeders #DONE
4. If upload amount is ridciously high compared to leechers amount #DONE
5. If sole uploader yet the leecher download status does not update # DONE
6. If sole leecher yet no one uploads # DONE


how can we know it not really downloading?



torrentX suggested tests:

1. request hash of a random piece and compare it 
2. for downloaders - requests a peer table and compare it with the stored table in the tracker;
 

"""
from TorrentLog import TorrentLog
from typing import List
from announce_log import AnnounceLog


def get_announcements_with_matching_attribute(announce_log_list: List[AnnounceLog], attr: str, value: str) -> List[List[AnnounceLog]]:
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
class AnnounceTest:
    def __init__(self, torrent: TorrentLog, seeders_threshold, leechers_threshold) -> None:
        self.torrent = torrent

    def leecherUploadTest(self):
        # when torrent uploads data yet there are no leechers
        # how can we test for that? if there are 2+ announcements in a row when there are no leechers and the data is being uploaded
        # hole: if a torrent is small or upload is fast - there can be uploads that wont be recorded in the announcement

        """That function currently doesnt work as expected as it doesnt count for cases when there are 0 leechers, and then there are leechers for a short period or time (thus the upload value changes even tho no cheating happened).
        Also fitting results returns a list of lists"""

        fitting_results: List[AnnounceLog] = get_announcements_with_matching_attribute(self.torrent.announcements_logs, "leechers")

        if not fitting_results: # if list is len(zero) than there are no zero leechers so theres nothing to check
            return True
        

        total_upload_data_set = set()
        for res in fitting_results:
            total_upload_data_set.add(res.uploaded)


        if len(total_upload_data_set) != 1:
            # that means that there are non similarities
            print(f"there are {len(total_upload_data_set)} different uploaded values for {len(fitting_results)} announcement logs. failure precentage: {round(total_upload_data_set / fitting_results), 2}")
            return False
        
        return True
    
    def seederDownloadTest(self):
        # when torrent downloads yet there are no seeders
        # how can we test for that? just as previous function - we will test with the same principals but checking for seeders\downloaded attributes
        fitting_results: List[AnnounceLog] = get_announcements_with_matching_attribute(self.torrent.announcements_logs, "seeders")

        if not fitting_results: # if list is len(zero) than there are no zero seeders so theres nothing to check as there are seeders
            return True
        
        total_download_data_set = set()
        for res in fitting_results:
            total_download_data_set.add(res.downloaded)


        if len(total_download_data_set) != 1:
            # that means that there are non similarities
            print(f"there are {len(total_download_data_set)} different downloaded values for {len(fitting_results)} announcement logs. failure precentage: {round(total_download_data_set / fitting_results), 2}")
            return False
        
        return True
    
    def downloadChangeTooFast(self):
        threshold_seeder_avarage = self.seeders_threshold 

        threshold_avarage_download_speed_in_torrent_in_second = 4000 # just a number to be determined by a function


        for i in range(len(self.torrent.announcements_logs) - 1):
            record = self.torrent.announcements_logs[i]
            next_record = self.torrent.announcements_logs[i+1]
            time_diff = calculate_time_difference_seconds(record, next_record)
            
            should_be_downloaded = threshold_avarage_download_speed_in_torrent_in_second * time_diff

            # if that number is too high we will check how many seeders there were in the first record
            if should_be_downloaded < next_record.downloaded - record.downloaded:
                # check for how many seeders there are
                if next_record.seeders < threshold_seeder_avarage:
                    return False # there are not alot of seeders so it doesnt make sense that he downloaded too fast



        # we didnt found out of the ordinary cases, passing the test
        return True
    
    def uploadChangeTooFast(self):
        threshold_leecher_avarage = self.leecher_threshold

        threshold_avarage_upload_speed_in_torrent_in_second = 4000 # just a number to be determined by a function


        for i in range(len(self.torrent.announcements_logs) - 1):
            record = self.torrent.announcements_logs[i]
            next_record = self.torrent.announcements_logs[i+1]
            time_diff = calculate_time_difference_seconds(record, next_record)
            
            should_be_uploaded = threshold_avarage_upload_speed_in_torrent_in_second * time_diff

            # if that number is too high we will check how many seeders there were in the first record
            if should_be_uploaded < next_record.uploaded - record.uploaded:
                # check for how many seeders there are
                if next_record.leechers < threshold_leecher_avarage:
                    return False # there are not alot of seeders so it doesnt make sense that he downloaded too fast



        # we didnt found out of the ordinary cases, passing the test
        return True
    

    def uploadToNoOne(self):
        # checking if user suggests to upload yet there are no seeders

        for i in range(len(self.torrent.announcements_logs) - 1):
            record = self.torrent.announcements_logs[i]
            next_record = self.torrent.announcements_logs[i+1]

            if next_record.uploaded - record.uploaded > 0:
                if next_record.leechers == 0 or record.leechers == 0:
                    return False
                
                else:
                    for leecher in record.peers:
                        if not tracketTests.checkIsPeer(leecher):
                            return False

        return True
    

    def downloadFromoNoOne(self):
        # checking if user suggests to upload yet there are no seeders

        for i in range(len(self.torrent.announcements_logs) - 1):
            record = self.torrent.announcements_logs[i]
            next_record = self.torrent.announcements_logs[i+1]

            if next_record.downloaded - record.downloaded > 0:
                if next_record.seeders == 0 or record.seeders == 0:
                    return False
                            
                else:
                    for seeder in record.peers:
                        if not tracketTests.checkIsPeer(seeder):
                            return False
            

        return True
    


class tracketTests:
    @classmethod
    def checkIsPeer(cls, ip):
        return True
# a class that will help us do server-wide operations, for example: checking if an IP address is a peer

