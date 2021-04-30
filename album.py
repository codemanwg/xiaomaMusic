import random

import sys

sys.path.append('../musicServer')
import database


class AsyncAlbumManager:
    current_album_id = None
    current_album_name = None
    current_song = {}
    next_song = {}
    current_play_list = []
    play_list_length = 0

    def get_random_song(self):
        return random.choice(self.current_play_list)

    def set_current_album_id(self, album_id):
        self.current_album_id = album_id

    def set_current_album_name(self, album_name):
        self.current_album_name = album_name

    async def set_current_play_list(self, album_id):

        if album_id == self.current_album_id:
            print(album_id, self.current_album_id)
            return

        # 如果歌单为空
        if album_id == 0:
            self.current_play_list = await self.all_songs()
            return
        self.current_play_list = await self.get_album_songs(album_id)
        print("当前歌单", self.current_play_list)

    async def set_current_song(self, song_id):
        self.current_song = await self.get_song_info(song_id)
        return self.current_song

    def set_next_song(self):
        song_list_length = len(self.current_play_list)
        print("当前歌单", self.current_play_list)

        for index, item in enumerate(self.current_play_list):
            if item['song_id'] == self.current_song['id']:
                if index + 1 > song_list_length - 1:
                    self.next_song = self.current_play_list[0]
                    return
                else:
                    self.next_song = self.current_play_list[index + 1]
                    return

    def current_state(self):
        return self.current_album_id, self.current_album_name

    @staticmethod
    async def add_song(song):
        await database.add_song(song)

    @staticmethod
    async def add_album_song(album_id, song):
        await database.album_add_song(album_id, song)

    @staticmethod
    async def get_song_info(song_id, album_id=None):
        if album_id:
            song = await database.album_song_info(album_id, song_id)
            return dict(song)
        song = await database.song_info(song_id)
        return dict(song)

    @staticmethod
    async def get_album_list():
        albums = await database.all_albums()
        album_list = [dict(i) for i in albums]
        return album_list

    @staticmethod
    async def get_album_songs(album_id):
        songs = await database.album_songs(album_id)
        song_list = [dict(i) for i in songs]
        return song_list

    @staticmethod
    async def all_songs():
        songs = await database.all_songs()
        raw_songs = [dict(i) for i in songs]
        song_list = []
        for song in raw_songs:
            song.update({'song_id': song['id']})
            song_list.append(song)
        return song_list

    @staticmethod
    async def del_album_song(album_id, song_id):
        await database.album_del_song(album_id, song_id)

    @staticmethod
    async def add_album(name, desc):
        await database.add_album(name, desc)

    @staticmethod
    async def del_album(album_id):
        await database.album_drop_all_songs(album_id)
        await database.del_album(album_id)


InstanceAsyncAlbumManager = AsyncAlbumManager()

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(InstanceAsyncAlbumManager.all_songs())
    # loop.run_until_complete(InstanceAsyncAlbumManager.get_album_list())
    # loop.run_until_complete(InstanceAsyncAlbumManager.del_album(5))
    # loop.run_until_complete(InstanceAsyncAlbumManager.get_album_song_info(1, 1))
    # loop.run_until_complete(InstanceAsyncAlbumManager.del_album_song(1, 9))
    loop.run_until_complete(InstanceAsyncAlbumManager.get_album_songs(1))
