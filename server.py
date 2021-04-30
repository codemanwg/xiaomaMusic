import sys

sys.path.append('../musicServer')
import asyncio
import websockets
import random
import json
from music_player import MusicPlayer
from search import Search
from vip_download import download_mp3
from lib import get_local_music_list, parse_path, parse_file_path
from album import InstanceAsyncAlbumManager


class MusicServer:
    client_list = {}
    root_dir = './musics'
    search_tool = Search()
    download_queue = []

    def __init__(self):
        # 0是全部列表
        self.current_menu_id = 0
        self.music_list = []
        self.music_player = MusicPlayer()
        self.album_manager = InstanceAsyncAlbumManager
        self.api_map = self.init_router()
        self.start_flag = False
        self.playing_flag = False
        self.play_mode = 'loop'
        self.current_index = -1
        self.current_music = {}

        websocket_server = websockets.serve(self.service, '0.0.0.0', 8888)
        asyncio.get_event_loop().run_until_complete(websocket_server)
        asyncio.ensure_future(self.auto_next())
        asyncio.ensure_future(self.download_task())
        asyncio.get_event_loop().run_forever()

    async def service(self, websocket, path):
        client_name = self.handle_client(websocket, path)
        async for message in websocket:
            await self.router(client_name, json.loads(message))

    async def router(self, client_name, request):
        print(f'{client_name}:{request}')
        await self.api_map[request['path']](request=request,
                                            client_name=client_name)

    async def send_response(self, path, data, client_name=None):
        response = json.dumps({'api': path, 'data': data})
        if client_name:
            await self.client_list[client_name].send(response)
        else:
            offline = []
            for client, ws in self.client_list.items():
                try:
                    await ws.send(response)
                except:
                    print(f'{client} offline')
                    offline.append(client)
            for client in offline:
                self.client_list.pop(client)

    async def get_player_info(self, **kwargs):
        request = kwargs['request']
        data = {
            'mode': self.play_mode,
            'music': self.current_music,
            'play_status': self.playing_flag,
            'volume': self.music_player.get_music_volume(),
            'menu_list': await self.album_manager.get_album_list(),
            'current_menu': self.album_manager.current_album_id
        }
        await self.send_response(request['path'], data)

    async def get_all_songs(self, **kwargs):
        self.current_menu_id = 0
        request = kwargs['request']
        self.music_list = await self.album_manager.all_songs()
        data = {
            'player_status': self.start_flag,
            'music_list': self.music_list
        }
        # send_mode = kwargs['send_mode'] if kwargs.get('send_mode') else 1
        await self.send_response(request['path'], data, kwargs['client_name'])

    async def get_menu_songs(self, **kwargs):
        request = kwargs['request']
        album_id = request['query']['menu_id']
        # self.current_menu_id = menu_id
        music_list = await self.album_manager.get_album_songs(album_id)
        data = {'menu_id': album_id, 'music_list': music_list}
        await self.send_response(request['path'], data, kwargs['client_name'])

    async def search_music_list(self, **kwargs):
        request = kwargs['request']
        search_value = request['query']['search_value']
        music_list = await self.search_tool.search_song(search_value)
        data = {'player_status': self.start_flag, 'music_list': music_list}
        await self.send_response(request['path'], data, kwargs['client_name'])

    async def download_music(self, **kwargs):
        request = kwargs['request']
        music = request['query']['music']
        self.download_queue.append(music)
        await self.send_response(request['path'], self.download_queue)

    async def set_mode(self, **kwargs):
        request = kwargs['request']
        self.play_mode = request['query']['mode']
        await self.send_response(request['path'],
                                 {'play_mode': self.play_mode})

    # 前端回传song_id 和 album_id
    async def play_music(self, **kwargs):
        if not self.start_flag:
            await self.send_response(
                'music/volume',
                self.music_player.get_music_volume() * 100)

        request = kwargs['request']
        index = request['query']['index']
        song_id = request['query']['song_id']
        album_id = request['query'].get('album_id', 0)
        song = await self.album_manager.set_current_song(song_id)
        print(song)
        # 设置歌单
        await self.album_manager.set_current_play_list(album_id)
        self.album_manager.set_current_album_id(album_id)
        self.album_manager.set_next_song()
        music_file = parse_file_path(self.root_dir, song)
        # music = await self.album_manager.get_song_info(self.current_menu_id, song_id)
        self.music_player.play_click(music_file)
        self.start_flag = True
        self.playing_flag = True
        self.current_index = index
        self.current_music = song
        # self.album_manager.set_current_album_id(album_id)
        song["album_id"] = album_id

        await self.send_response(request['path'], song)

    async def pause_music(self, **kwargs):
        request = kwargs['request']
        self.music_player.pause_click()
        self.playing_flag = False
        await self.send_response(request['path'], {'play_status': 'play'})

    async def unpause_music(self, **kwargs):
        if not self.start_flag:
            await self.next_music(request={'path': 'music/next'})
        else:
            request = kwargs['request']
            self.music_player.unpause_click()
            self.playing_flag = True
            await self.send_response(request['path'], {'play_status': 'pause'})

    async def pre_music(self, **kwargs):
        request = kwargs['request']
        index = self.get_index('pre')
        await self.play_music(request={
            'path': request['path'],
            'query': {
                'index': index
            }
        })

    async def next_music(self, **kwargs):
        request = kwargs['request']
        # index = self.get_index('next')
        song = self.album_manager.next_song if self.play_mode == "loop" else self.album_manager.get_random_song(
        )
        print(song)

        # index的逻辑没有动
        await self.play_music(
            request={
                'path': request['path'],
                'query': {
                    'index': 0,
                    'song_id': song['song_id'],
                    'album_id': self.album_manager.current_album_id
                }
            })

    async def set_volume(self, **kwargs):
        request = kwargs['request']
        volume = request['query']['volume_value']
        self.music_player.set_volume(volume / 100)
        await self.send_response(request['path'], volume)

    async def add_menu(self, **kwargs):
        request = kwargs['request']
        menu_name = request['query']['menu_name']
        await self.album_manager.add_album(menu_name, '')
        await self.send_response(request['path'], await
                                 self.album_manager.get_album_list())

    async def add_song_to_menu(self, **kwargs):
        request = kwargs['request']
        menu_id = request['query']['menu_id']
        song = request['query']['song']
        await self.album_manager.add_album_song(menu_id, song)

    async def del_song_from_menu(self, **kwargs):
        request = kwargs['request']
        song = request['query']['song']
        await self.album_manager.del_album_song(song['album_id'],
                                                song['song_id'])
        self.music_list = await self.album_manager.get_album_songs(
            song['album_id'])
        await self.get_menu_songs(request={
            'path': 'music/menu',
            'query': {
                'menu_id': song['album_id']
            }
        })

    def get_index(self, click_type):
        index = 0
        if not self.start_flag:
            return index
        if self.play_mode == 'loop':
            if click_type == 'pre':
                index = -1 if self.current_index == 0 else self.current_index - 1
            if click_type == 'next':
                index = 0 if self.current_index == len(
                    self.music_list) - 1 else self.current_index + 1
        elif self.play_mode == 'random':
            index = random.randrange(0, len(self.music_list))
        return index

    async def auto_next(self):
        while True:
            if self.start_flag:
                if self.music_player.get_music_pos() == -1:
                    await self.next_music(request={'path': 'music/next'})
            await asyncio.sleep(1)

    async def download_task(self):
        while True:
            if len(self.download_queue) >= 1:
                task_wait = self.download_queue[0]
                ret = await download_mp3(task_wait)
                self.download_queue.remove(task_wait)
                await self.send_response('music/download', self.download_queue)
                if ret['code'] == 1:
                    await self.album_manager.add_song(ret['song'])
                await self.send_response('music/msg', ret['msg'])
            else:
                await asyncio.sleep(1)

    def init_router(self):
        return {
            'music/playerInfo': self.get_player_info,
            'music/local': self.get_all_songs,
            'music/menu': self.get_menu_songs,
            'music/search': self.search_music_list,
            'music/download': self.download_music,
            'music/playMode': self.set_mode,
            'music/play': self.play_music,
            'music/pause': self.pause_music,
            'music/unpause': self.unpause_music,
            'music/pre': self.pre_music,
            'music/next': self.next_music,
            'music/volume': self.set_volume,
            'music/menu/add': self.add_menu,
            'music/menu/add/song': self.add_song_to_menu,
            'music/menu/del/song': self.del_song_from_menu,
        }

    def handle_client(self, ws, path):
        client_name = path.replace('/', '')
        self.client_list[client_name] = ws
        return client_name


if __name__ == '__main__':
    MusicServer()
