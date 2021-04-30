import os
import sys
import time
import threading
import pygame
from pygame.mixer import music
import subprocess

class MusicPlayer:
    music_dir = './musics'
    pygame.mixer.init(48000, -16, 2, 4096)
    SONG_END = pygame.USEREVENT + 1

    def __init__(self):
        self.set_volume(1)

    def main(self):
        pass

    def play_click(self, music_file):
        while True:
            if music.get_busy():
                music.stop()
            else:
                break
        t = threading.Thread(target=self.__play, args=[music_file])
        t.start()
        # music.load(music_file)
        # music.play(1)

    def pause_click(self):
        music.pause()

    def unpause_click(self):
        music.unpause()

    def stop_click(self):
        music.stop()

    def set_volume(self, volume: float):
        music.set_volume(volume)

    def __play(self, music_file):
        # self.playing_flag = True
        # while self.playing_flag:
        #     if not music.get_busy():
        #         music.load(music_file)
        #         music.play(-1)
        music.load(music_file)
        music.play(1)

    def __stop(self):
        self.playing_flag = False

    def __get_music_list(self):
        return os.listdir(self.music_dir)

    def get_music_status(self):
        return music.get_busy()
        # while True:
        #     print(music.get_busy())
        #     time.sleep(0.5)

    def get_music_volume(self):
        return music.get_volume()

    def set_music_pos(self, pos: float):
        music.set_pos(pos)

    def get_music_pos(self):
        return music.get_pos()

    def handel_end_event(self):
        return music.get_endevent()


if __name__ == '__main__':
    music_player = MusicPlayer()
    music_player.play_click('./musics/傲七爷-是想你的声音啊(澜 & ISYUL & REGS & VaSka & CaSsie remix)-GARBAGE.mp3')

    # def pause_loop():
    #     while True:
    #         time.sleep(5)
    #         music_player.stop_click()
    #         time.sleep(5)
    #         music_player.unpause_click()
    #         time.sleep(5)
    #         music_player.play_click('./musics/Body Shots（翻自 Kaci Battaglia）  - 一条小团团OvO.mp3')
    # t = threading.Thread(target=pause_loop, args=[])
    # t.start()