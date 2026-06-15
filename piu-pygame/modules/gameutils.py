import pygame
from modules.imports import *

def measurestoms(measures: float, bpm: float) -> float:
    return measures * 240000 / bpm

def sign(n: float) -> int:
    if n == 0:
        return 0
    if n > 0:
        return 1
    return -1

def judge(offset: int) -> tuple:
    # negative offset value = early
    judge = 4
    combobreak = True
    scoremult = 0
    if -32 < offset < 96:
        judge = 0
        combobreak = False
        scoremult = 1
    elif -64 < offset < 150:
        judge = 1
        combobreak = False
        scoremult = 0.6
    elif -96 < offset < 200:
        judge = 2
        combobreak = None
        scoremult = 0.2
    elif -144 < offset < 250:
        judge = 3
        scoremult = 0.1
    return judge, combobreak, scoremult

def fadecalc(t: float, bpm: float) -> float:
    if t < 0:
        return 0
    t /= 1000
    x = max(((bpm * t) / 60) % 1, 0)
    return (1 - x)**2

def extend(stream: list, n: int) -> list:
    ct = -1
    new = []
    stream = stream * 8
    for i in stream:
        if i[1] == 0:
            ct += 1
        lis = (ct, i[1], i[2])
        new.append(lis)
    return new