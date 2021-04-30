import sys

sys.path.append('../musicServer')
from databases import Database
import sqlalchemy
from sqlalchemy import MetaData

__database_url = "sqlite:///xiaoma.db"
__database = Database(__database_url)
__metadata = MetaData()
# 歌单列表
table_albums = sqlalchemy.Table(
    "albums", __metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(length=64), nullable=False),
    sqlalchemy.Column("desc", sqlalchemy.String(length=128)),
    sqlalchemy.Column("owner", sqlalchemy.Integer))

# 歌曲表
table_songs = sqlalchemy.Table(
    "songs", __metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(length=64), nullable=False),
    sqlalchemy.Column("singer", sqlalchemy.String(length=64), nullable=False),
    sqlalchemy.Column("file", sqlalchemy.String(length=128), unique=True),
    sqlalchemy.Column("duration", sqlalchemy.Integer),
    sqlalchemy.Column("netease_id", sqlalchemy.Integer, unique=True))

table_songs_album = sqlalchemy.Table(
    "songs_album", __metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("song_id", sqlalchemy.Integer),
    sqlalchemy.Column("album_id", sqlalchemy.Integer),
    sqlalchemy.Column("title", sqlalchemy.String(length=64), nullable=False),
    sqlalchemy.Column("singer", sqlalchemy.String(length=64), nullable=False),
    sqlalchemy.Column("file", sqlalchemy.String(length=128)),
    sqlalchemy.Column("duration", sqlalchemy.Integer))


def create_table(drop=False):
    if drop:
        drop_database()
    engine = sqlalchemy.create_engine(__database_url)
    __metadata.create_all(engine)
    print("建表完毕！")


def drop_database():
    engine = sqlalchemy.create_engine(__database_url)
    __metadata.drop_all(engine)
    print("已经清空数据库！")


# 获取所有歌曲
async def all_songs():
    query = table_songs.select()
    rows = await __database.fetch_all(query=query)
    return rows


# 添加一个歌单
async def add_album(album_name, desc):
    value = {"name": album_name, "desc": desc}
    query = table_albums.insert()
    await __database.execute(query=query, values=value)


# 获取歌单列表
async def all_albums():
    query = table_albums.select()
    rows = await __database.fetch_all(query=query)
    return rows


# 删除一个歌单
async def del_album(album_id):
    query = sqlalchemy.sql.delete(table_albums).where(
        table_albums.c.id == album_id)
    await __database.execute(query=query)


# 添加一首歌曲记录
async def add_song(song):
    value = {
        "title": song['title'],
        "file": song['file'],
        "duration": song['duration'],
        "singer": song['singer'],
        "netease_id": song['song_id']
    }
    query = table_songs.insert()
    await __database.execute(query=query, values=value)


# 查询歌曲信息
async def song_info(song_id):
    query = sqlalchemy.sql.select([table_songs
                                   ]).where(table_songs.c.id == song_id)
    song = await __database.fetch_one(query=query)
    return song


# 查询歌单歌曲信息
async def album_song_info(album_id, song_id):
    query = sqlalchemy.sql.select([
        table_songs_album
    ]).where(table_songs_album.c.album_id == album_id).where(
        table_songs_album.c.song_id == song_id)
    song = await __database.fetch_one(query=query)
    return song


# 向歌单添加一首歌曲
async def album_add_song(album_id, song):
    value = {
        "song_id": song['id'],
        "album_id": album_id,
        "title": song['title'],
        "singer": song['singer'],
        "file": song['file'],
        "duration": song['duration']
    }
    print(value)
    query = table_songs_album.insert()
    await __database.execute(query=query, values=value)


# 删除指定歌单的指定歌曲
async def album_del_song(album_id, song_id):
    query = sqlalchemy.sql.delete(table_songs_album).where(
        table_songs_album.c.album_id == album_id).where(
            table_songs_album.c.song_id == song_id)
    await __database.execute(query=query)


# 获取歌单中的所有歌曲
async def album_songs(album_id):
    query = sqlalchemy.sql.select(
        [table_songs_album]).where(table_songs_album.c.album_id == album_id)
    rows = await __database.fetch_all(query=query)
    return rows


# 清空指定歌单
async def album_drop_all_songs(album_id):
    query = sqlalchemy.sql.delete(table_songs_album).where(
        table_songs_album.c.album_id == album_id)
    await __database.execute(query=query)


if __name__ == "__main__":
    import asyncio
    # asyncio.get_event_loop().run_until_complete(add_album('歌单3', ''))
    # asyncio.get_event_loop().run_until_complete(all_albums())
    # asyncio.get_event_loop().run_until_complete(album_songs(1))
    create_table(True)
