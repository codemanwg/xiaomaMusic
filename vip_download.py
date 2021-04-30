import asyncio
import httpx
import base64
import binascii
import json
import os
from Crypto.Cipher import AES
from lib import parse_song

MODULUS = ("00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
           "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
           "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
           "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
           "3ece0462db0a22b8e7")
PUBKEY = "010001"
NONCE = b"0CoJUm6Qyw8W8jud"


# 登录加密算法, 基于https://github.com/stkevintan/nw_musicbox
def encrypted_request(text):
    data = json.dumps(text).encode("utf-8")
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encseckey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubkey, 16),
             int(modulus, 16))
    return format(rs, "x").zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]


async def download_mp3(music_info):
    song_id = music_info['song_id']
    title = parse_song(music_info['title'])
    singer = parse_song(music_info['singer'])
    file = f'./musics/{title}-{singer}.mp3'
    music_info['file'] = file
    if not os.path.exists(file):
        api = "http://music.163.com/weapi/song/enhance/player/url"
        headers = {
            "Host":
            "music.163.com",
            "Referer":
            "http://music.163.com",
            "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.87 Safari/537.36",
            "Cookie":
            "MUSIC_U=6xxff42e44dbab42ef535264fac1515d3e77a0e92573ef730bf880b29f9097d50931c3a9fbfe3df2"
        }
        data = {
            "ids": [song_id],
            "br": 320000,
        }
        data = encrypted_request(data)
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(api,
                                      headers=headers,
                                      data=data,
                                      timeout=8)
                ret_data = r.json()
                if len(ret_data['data']) < 1:
                    return {'code': -3, 'msg': f'[{title}]未搜到'}
                else:
                    url = ret_data['data'][0]['url']
                    r = await client.get(url, timeout=8)
                    with open(file, 'wb') as f:
                        f.write(r.content)
                    return {'code': 1, 'msg': f'[{title}]下载完成', 'song': music_info}
            except:
                return {'code': -2, 'msg': '网络错误'}
    else:
        return {'code': 2, 'msg': f'[{title}]已存在'}


if __name__ == "__main__":
    async def demo():
        print(await download_mp3({
            'song_id': 1488780845,
            'title': 'Piu Piu Piu',
            'singer': '拼音师'
        }))

    asyncio.get_event_loop().run_until_complete(demo())
