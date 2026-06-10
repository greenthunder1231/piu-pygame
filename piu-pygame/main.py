import pygame
import sys
from pathlib import Path

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class const:
    def __init__(self, beatmap=None):
        # you can change these
        self.fps = 60 # fps
        self.startdelay = 2000 # how long it takes from program open to beatmap start
        self.scroll = 400 # note scroll speed
        
        # dont change anything after this
        self.bpm = 120 # map bpm
        self.pps = self.scroll
        self.double = False # if beatmap is double or not
        if beatmap:
            self.BEATMAP = beatmap
            if any(i[2] >= 5 for i in self.BEATMAP): # overrides manual double mode if there is a 6th panel or more
                self.double = True
        else:
            # if self.double:
                self.BEATMAP = [ # the actual beatmap
                (0, 0, 0), (0, 0.25, 1), (0, 0.5, 2), (0, 0.75, 3),
                (0, 1, 4), (0, 1.25, 3), (0, 1.5, 2), (0, 1.75, 1),
                (0, 2, 0), (0, 2.25, 3), (0, 2.5, 1), (0, 2.75, 4),
                (0, 3, 2), (0, 3.25, 3), (0, 3.5, 1), (0, 3.75, 2)
                ]
        self.RECEPTORY = 68
        if self.double:
            self.COLUMNX = [(SCREEN_WIDTH/2) - 288 + (64 * i) for i in range(10)]
        else:
            self.COLUMNX = [(SCREEN_WIDTH/2) - 160 + (64 * i) for i in range(5)]

CONST = const()

class Receptor(pygame.sprite.Sprite):
    def __init__(self, x, y, i, normimg, blinkimg, glowimg):
        super().__init__()
        self.i = i
        self.normimg = normimg
        self.blinkimg = blinkimg
        self.glowimg = glowimg
        self.image = self.normimg.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self, fade, hit):
        if fade > 0:
            blink_overlay = self.blinkimg.copy()
            blink_overlay.set_alpha(int(255 * fade))
            self.image.blit(blink_overlay, (0, 0))
        if hit[self.i] > 0:
            glow_overlay = self.glowimg.copy()
            glow_overlay.set_alpha(int(255 * hit))
            self.image.blit(glow_overlay, (0, 0))


class Note(pygame.sprite.Sprite):
    def __init__(self, note, noteimg):
        super().__init__()
        self.note = note
        self.x = CONST.COLUMNX[self.note[2]]
        self.y = SCREEN_HEIGHT
        self.noteimg = noteimg
        self.image = self.noteimg.copy()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    def update(self, measure, beat):
        notetime = (self.note[1] * 4 + self.note[0]) * (60 / CONST.bpm)
        timediff = notetime - (beat * 4 + measure) * (60 / CONST.bpm)
        timediff *= 1000
        self.y = timediff * 0.1
        if self.y < -64 or self.y > 1024:
            return
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

def extract(path, width, height):
    '''Given a spritesheet, provide all sprites width by height in the spritesheet.'''
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        print(f'Error loading {path}')
        sys.exit()
    
    sheetwidth, sheetheight = sheet.get_size()
    sprites = []

    for y in range(0, sheetheight, height):
        for x in range(0, sheetwidth, width):
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), (x, y, width, height))
            sprites.append(sprite)
    return sprites

# 1. Initialize all imported pygame modules
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stupid It Up Prime")

# 3. Create a clock object to track and control frame rate
clock = pygame.time.Clock()

receptorpath = str(Path(__file__).parent / 'noteskin/default/tex receptors.png')
glowpath = str(Path(__file__).parent / 'noteskin/default/tex glow.png')
notepath = str(Path(__file__).parent / 'noteskin/default/tex notes.png')

allreceptors = extract(receptorpath, 64, 64)
receptors = allreceptors[:3]
receptorsblink = allreceptors[4:7]
glow = extract(glowpath, 64, 64)
notes = extract(notepath, 64, 64)

lane_normimgs = [
    receptors[0],
    receptors[1],
    receptors[2],
    pygame.transform.flip(receptors[1], True, False),
    pygame.transform.flip(receptors[0], True, False)
]
lane_blinkimgs = [
    receptorsblink[0],
    receptorsblink[1],
    receptorsblink[2],
    pygame.transform.flip(receptorsblink[1], True, False),
    pygame.transform.flip(receptorsblink[0], True, False)
]
lane_glowimgs = [
    glow[0],
    glow[1],
    glow[2],
    pygame.transform.flip(glow[1], True, False),
    pygame.transform.flip(glow[0], True, False)
]
lane_notes = [
    notes[0],
    notes[1],
    notes[2],
    pygame.transform.flip(notes[1], True, False),
    pygame.transform.flip(notes[0], True, False)
]



fade = 0
def fadecalc(t):
    if t < 0:
        return 0
    t /= 1000
    x = max(((CONST.bpm * t) / 60) % 1, 0)
    return (1 - x)**2

monospace = pygame.font.SysFont('Monospace', 20)

running = True
hitlen = 0
if CONST.double:
    hitlen = 10
else:
    hitlen = 5

hit = [0] * hitlen

while running:
    rawtime = pygame.time.get_ticks() - CONST.startdelay
    gametime = rawtime
    rawbeat = (gametime * CONST.bpm) / 60000
    beat = int(rawbeat) % 4
    measure = rawbeat // 4
    # --- 1. Event Handling ---
    # Pygame captures inputs (keys, mouse clicks, closing windows) as "events"
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # --- 2. Game Logic / State Updates ---
    # This is where physics, movement, and math happen every frame.

    # --- 3. Drawing / Rendering ---
    screen.fill((20, 20, 30))  # Clear the screen with a dark blue color
    
    # Draw a static receptor line where items will eventually be hit
    pygame.draw.line(screen, (70, 70, 70), (0, 100), (SCREEN_WIDTH, 100), 2)
    
    fade = fadecalc(gametime)
    
    notegroup = pygame.sprite.Group()
    receptorgroup = pygame.sprite.Group()
    
    for i in range(5):
        y = CONST.RECEPTORY
        if CONST.double:
            x1 = 192 + (i * 64)
            x2 = 192 + ((i + 5) * 64)
            newrecep1 = Receptor(x1, y, i, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            newrecep2 = Receptor(x2, y, i + 5, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            receptorgroup.add(newrecep1)
            receptorgroup.add(newrecep2)
        else:
            x = 352 + (i * 64)
            newrecep = Receptor(x, y, i, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            receptorgroup.add(newrecep)

    for note in CONST.BEATMAP:
        # pos = (note[0] * 4 + note[1]) * 60 / CONST.bpm - gametime
        newnote = Note(note, lane_notes[note[2]])
        notegroup.add(newnote)

    # rendering
    receptorgroup.update(fade, hit)
    receptorgroup.draw(screen)
    notegroup.update(measure, rawbeat)
    notegroup.draw(screen)
    txtsurf = monospace.render(f'time: {gametime}\nrwbt: {rawbeat}\nbeat: {beat}\nmeas: {measure}', True, (255, 255, 255))
    screen.blit(txtsurf, (0, 0))

    # Swap the back buffer with the front buffer to show the changes on screen
    pygame.display.flip()

    # --- 4. Frame Rate Control ---
    # Cap the game loop at 60 Frames Per Second (FPS)
    clock.tick(CONST.fps)

# Clean up and close the program safely
pygame.quit()
sys.exit()