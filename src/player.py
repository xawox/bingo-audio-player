import pygame

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.file_path = None
        self.is_playing = False
        self.is_paused = False

    def load(self, file_path):
        self.file_path = file_path
        pygame.mixer.music.load(self.file_path)

    def play(self):
        if self.file_path:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False

    def pause(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False