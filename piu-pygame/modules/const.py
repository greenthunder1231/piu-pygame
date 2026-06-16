import pygame
from modules.imports import *
from modules.files import defaultbeatmaps
from modules.autostep import rotatept

class _const:
    def __init__(self):
        self.WINDOW_WIDTH = 1024
        self.WINDOW_HEIGHT = 768
        self.BPM = 220 # map bpm
        self.OFFSET = -3.376177
        self.MEASUREOFFSET = 112
        self.DOUBLE = True # if beatmap is double or not
        self.BEATMAP = defaultbeatmaps['double']['paradoxx'] # the actual beatmap
        new = []
        for n in self.BEATMAP:
            val = 1000 * (n[1] + 4 * n[0]) * (60 / self.BPM)
            if len(n) == 4:
                new.append((val, n[2], n[3] if n[3] else None))
            else:
                new.append((val, n[2], None))
        self.BEATMAP = new
        self.RECEPTORY = 70
        self.JUDGEY = 0.5 * self.WINDOW_HEIGHT
        self.KEYS = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_SEMICOLON]
        if not self.DOUBLE:
            self.KEYS = self.KEYS[:5]
        # self.KEYS = [pygame.K_KP_1, pygame.K_KP_7, pygame.K_KP_5, pygame.K_KP_9, pygame.K_KP_3]
        if self.DOUBLE:
            self.COLUMNX = [(self.WINDOW_WIDTH / 2) + 64 * (i - 4.5) for i in range(10)]
        else:
            self.COLUMNX = [(self.WINDOW_WIDTH / 2) + 64*(i - 2) for i in range(5)]
        self.SHOWSTEPOFFSETX = [-64, -64, 0, 64, 64]
        self.SHOWSTEPOFFSETY = [-4768/83, 4768/83, 0, 4768/83, -4768/83]
        self.SHOWSTEPFOOTPTS = [
            (*rotatept((-45, -35), (-45, -15), -0.5), -30),
            (*rotatept((-45, 35), (-45, 18), 0.5), 30),
            (*rotatept((45, 35), (45, 18), -0.5), -30),
            (*rotatept((45, -35), (45, -15), 0.5), 30),
            (0, 50, 90),
            (0, -50, 90),
            (*rotatept((-45, -35), (-45, -15), -0.5), -30),
            (*rotatept((-45, 35), (-45, 18), 0.5), 30),
            (*rotatept((45, 35), (45, 18), -0.5), -30),
            (*rotatept((45, -35), (45, -15), 0.5), 30)
        ]