import httpx
import os
import asyncio
from lib import parse_song
from encrypyed import Encrypyed


# import database


class Search:
    """
    跟歌单直接下载的不同之处
    1.就是headers的referer
    2.加密的text内容不一样！
    3.搜索的URL也是不一样的
    输入搜索内容，可以根据歌曲ID进行下载，大家可以看我根据跟单下载那章，自行组合
    """

    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            # 'Cookie': '_ntes_nnid=16c547f1f4221165b97a521637b3bf57,1603088697057; _ntes_nuid=16c547f1f4221165b97a521637b3bf57; UM_distinctid=175530794e02d7-07fac621bb116f-3f6b4b05-1fa400-175530794e17f5; vinfo_n_f_l_n3=d55a393823705eaa.1.0.1603415805873.0.1603415810372; NMTID=00OvqqJOnVlnnQAJUdLuHlhxRfeEIYAAAF13y6C4g; _iuqxldmzr_=32; ntes_kaola_ad=1; WM_TID=EKjMmaBhjBRFBUAFFUc%2FMrbqCPmRx6Ry; P_INFO=m18451019200@163.com|1610611839|1|mail163|00&99|jis&1609037462&mail_client#jis&320500#10#0#0|184200&1||18451019200@163.com; nts_mail_user=18451019200@163.com:-1:1; hb_MA-B407-E266474A0BB8_source=m.163yun.com; WEVNSM=1.0.0; WNMCID=rkskkj.1612319296579.01.0; WM_NI=Ws%2F25yBFnr61EVa1rMc6mh%2FXdLRpG%2B0kX5zG%2BnrRUchAWreYX2cP5i6v%2FP9BplJ1QKMQSYKxXdHgu%2BeR%2FXD1Vg9t1MhP37%2BqGz31CiDU7GllXm5xGQgFjQPQQ4MraEO9S04%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee93f57e8795b6b6b13fa6eb8aa2c14a929a8bbaf548f2b4fd8bf34a82ec9daecd2af0fea7c3b92a95ade1d3b873829aa293b53b878aafd2f147a1eaa389ae54a8949e91c621f4b598d6f94de9b2beb3d869ac9f9993e8539ceeadb1b863f6aae1b1bc4ab4b486d2d4418f8f9dbaca749cbc8888f821a78ee1b9c73b96b9f795b447ac90fdd8aa7b85a6fdd2c263888bf9a8ef689cb3fb99c65ba59aa6b2d35b93ec8393e44f8de79dd1b737e2a3; JSESSIONID-WYYY=w2A%5Ck2P8JIgCgNMW%5C8PRiJmK1Y2ikv%5CV4em5k%2F3xgDzn%2FW40lCYtrzfawlvmaJ0u4OhJEoO%2B3FrHS61cJX60Bh54NCGxcUA%2BVfa57w2eimJg3E9OXX%2FrkM6WZVzD6zC9W%5Cwjl%2FeC4sZ%2BRgIRUfpm%2BwM%2BktOe4PO1p5dDsCqGkej0tWxc%3A1612342712135; MUSIC_U=6aaff42e44dbab42ef535264fac1515d3e77a0e92573ef730bf880b29f9097d50931c3a9fbfe3df2; __csrf=a3ef5306ad1f1aad34060e5fc01a7b5e; playerid=99514492'
        }  # !!注意，搜索跟歌单的不同之处！！
        self.ep = Encrypyed()

    # 搜索歌曲信息
    async def song_detail(self, song_id):
        url = 'http://music.163.com/api/song/detail?ids=[' + str(song_id) + ']'
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=self.headers, timeout=8)

            print(r.text)
            # TODO
            # 获取歌曲信息， 添加 歌曲 记录
            # database.add_song(netease_id=song_id)

    async def search_song(self, search_content, search_type=1, limit=20):
        """
        根据音乐名搜索
        :params search_content: 音乐名
        :params search_type: 不知
        :params limit: 返回结果数量
        return: 可以得到id 再进去歌曲具体的url
        """
        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        text = {
            's': search_content,
            'type': search_type,
            'offset': 0,
            'sub': 'false',
            'limit': limit
        }
        data = self.ep.search(text)
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=self.headers, data=data, timeout=8)
            assert r.status_code == 200
            ret_data = r.json()
            if ret_data['result']['songCount'] <= 0:
                print('搜不到！！')
                return []
            else:
                songs = ret_data['result']['songs']
                search_list = []
                for song in songs:
                    search_list.append({
                        'song_id': song['id'],
                        'title': song['name'],
                        'singer': song['ar'][0]['name'],
                        'duration': round(song['dt']/1000)
                    })
                return search_list

    @staticmethod
    async def download_music(music_info):
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            # 'Cookie': '_ntes_nnid=16c547f1f4221165b97a521637b3bf57,1603088697057; _ntes_nuid=16c547f1f4221165b97a521637b3bf57; UM_distinctid=175530794e02d7-07fac621bb116f-3f6b4b05-1fa400-175530794e17f5; vinfo_n_f_l_n3=d55a393823705eaa.1.0.1603415805873.0.1603415810372; NMTID=00OvqqJOnVlnnQAJUdLuHlhxRfeEIYAAAF13y6C4g; _iuqxldmzr_=32; ntes_kaola_ad=1; WM_TID=EKjMmaBhjBRFBUAFFUc%2FMrbqCPmRx6Ry; P_INFO=m18451019200@163.com|1610611839|1|mail163|00&99|jis&1609037462&mail_client#jis&320500#10#0#0|184200&1||18451019200@163.com; nts_mail_user=18451019200@163.com:-1:1; hb_MA-B407-E266474A0BB8_source=m.163yun.com; WEVNSM=1.0.0; WNMCID=rkskkj.1612319296579.01.0; WM_NI=Ws%2F25yBFnr61EVa1rMc6mh%2FXdLRpG%2B0kX5zG%2BnrRUchAWreYX2cP5i6v%2FP9BplJ1QKMQSYKxXdHgu%2BeR%2FXD1Vg9t1MhP37%2BqGz31CiDU7GllXm5xGQgFjQPQQ4MraEO9S04%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee93f57e8795b6b6b13fa6eb8aa2c14a929a8bbaf548f2b4fd8bf34a82ec9daecd2af0fea7c3b92a95ade1d3b873829aa293b53b878aafd2f147a1eaa389ae54a8949e91c621f4b598d6f94de9b2beb3d869ac9f9993e8539ceeadb1b863f6aae1b1bc4ab4b486d2d4418f8f9dbaca749cbc8888f821a78ee1b9c73b96b9f795b447ac90fdd8aa7b85a6fdd2c263888bf9a8ef689cb3fb99c65ba59aa6b2d35b93ec8393e44f8de79dd1b737e2a3; JSESSIONID-WYYY=w2A%5Ck2P8JIgCgNMW%5C8PRiJmK1Y2ikv%5CV4em5k%2F3xgDzn%2FW40lCYtrzfawlvmaJ0u4OhJEoO%2B3FrHS61cJX60Bh54NCGxcUA%2BVfa57w2eimJg3E9OXX%2FrkM6WZVzD6zC9W%5Cwjl%2FeC4sZ%2BRgIRUfpm%2BwM%2BktOe4PO1p5dDsCqGkej0tWxc%3A1612342712135; MUSIC_U=6aaff42e44dbab42ef535264fac1515d3e77a0e92573ef730bf880b29f9097d50931c3a9fbfe3df2; __csrf=a3ef5306ad1f1aad34060e5fc01a7b5e; playerid=99514492'
        }
        song_id = music_info['song_id']
        title = parse_song(music_info['title'])
        singer = parse_song(music_info['singer'])
        file = f'{title}-{singer}.mp3'
        if not os.path.exists(f'./musics/{file}'):
            api = f'https://music.163.com/song/media/outer/url?id={song_id}.mp3'
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(api, headers=headers, timeout=20)
                    if '404' in str(r.url):
                        return {'code': -1, 'msg': f'[{title}]为Vip歌曲'}
                    with open(f'./musics/{file}', 'wb') as f:
                        f.write(r.content)
                    return {'code': 1, 'msg': f'[{title}]下载完成'}
                except:
                    return {'code': -2, 'msg': '网络错误'}
        else:
            return {'code': 2, 'msg': f'[{title}]已存在'}


if __name__ == '__main__':
    async def main():
        print(await Search().search_song('piupiupiu'))


    # async def test():
    #     print(await Search().download_music({
    #         'song_id': 5281398,
    #         'title': '财神到',
    #         'singer': '林子祥'
    #     }))

    asyncio.get_event_loop().run_until_complete(main())
    # asyncio.get_event_loop().run_until_complete(Search().song_detail("1380720351"))
    # asyncio.get_event_loop().run_forever()
    # search = Search()
    # ret_data = await search.search_song('悠哉大王')
    # print(ret_data)
    # music = {'song_id': 1380720351, 'title': '悠哉山歌大王', 'singer': '穗乃果奶'}
    # download_music(music)
