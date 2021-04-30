import os
from mutagen.mp3 import MP3


def get_local_music_list(dir_path):
    music_list = []
    for index, item in enumerate(os.listdir(dir_path)):
        music = parse_path(item)
        music_list.append({
            'index': index,
            'title': music['title'],
            'singer': music['singer'],
            # 'duration': get_music_duration(self.root_dir, item)
            'duration': '2:30'
        })
    return music_list


def parse_path(music_path):
    music = music_path.replace('.mp3', '')
    title, singer = music.rsplit('-', 1)
    return {'title': title, 'singer': singer}


def parse_file_path(root, music_dict):
    return music_dict["file"]


def get_music_duration(root, music):
    try:
        audio = MP3(f'{root}/{music}')
        length = audio.info.length
        minute = int(length // 60)
        second = int(length % 60)
        second = second if second >= 10 else f'{second}0'
        duration = f'{minute}:{second}'
    except:
        duration = '2:30'
    return duration


def parse_song(song):
    return song.strip().replace('/', '&').replace('（', '(').replace('）', ')')
