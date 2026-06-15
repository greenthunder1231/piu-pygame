import pygame
from modules.imports import *

defbmpath = Path(__file__).parent / 'defaultbeatmaps.json'

try:
    with open(defbmpath, 'r') as f:
        defaultbeatmaps = json.load(f)
except FileNotFoundError:
    print(f'Default beatmaps not found. Put default beatmap file in {str(defbmpath)}')

def extract(path: Path, width: int, height: int) -> list:
    '''Given a spritesheet, provide all sprites width by height in the spritesheet.'''
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        raise FileNotFoundError(f'Error loading {path}')
    
    sheetwidth, sheetheight = sheet.get_size()
    sprites = []

    for y in range(0, sheetheight, height):
        for x in range(0, sheetwidth, width):
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), (x, y, width, height))
            sprites.append(sprite)
    return sprites

def loadbeatmap(mapstr: str) -> list:
    return []