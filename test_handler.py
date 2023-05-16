# class to handle each test we perform, weather it is on page_load or as a part of a routine

import announce_tests
import asyncio

class TestHandler:

    def __init__(self, torrent_log_handler) -> None:
        self.torrent_log_handler = torrent_log_handler

    
    def perform_piece_hash_test(self):
        res = asyncio.run(self._pefrorm_piece_hash_test)
        return res

    async def _pefrorm_piece_hash_test(self):
        torrents = self.torrent_log_handler.get_torrents()
        tasks = [announce_tests.gather_hashes_for_torrent_test(torrent) for torrent in torrents]

        return await asyncio.gather(*tasks)