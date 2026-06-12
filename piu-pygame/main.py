import pygame
import sys
from pathlib import Path
from screeninfo import get_monitors
from types import SimpleNamespace

import time

# monitorfps = 60

# for monitor in get_monitors():
#     if monitor.is_primary:
#         monitorfps = monitor.frequency

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

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

testing_beatmaps = {
    "single": {
        "stream": [
            (0, 0, 0), (0, 0.25, 1), (0, 0.5, 2), (0, 0.75, 3),
            (0, 1, 4), (0, 1.25, 3), (0, 1.5, 2), (0, 1.75, 1),
            (0, 2, 0), (0, 2.25, 3), (0, 2.5, 1), (0, 2.75, 4),
            (0, 3, 2), (0, 3.25, 3), (0, 3.5, 1), (0, 3.75, 2),
            (1, 0, 0), (1, 0.25, 4), (1, 0.5, 1), (1, 0.75, 3),
            (1, 1, 0), (1, 1.25, 3), (1, 1.5, 1), (1, 1.75, 4),
            (1, 2, 0), (1, 2.25, 3), (1, 2.5, 2), (1, 2.75, 4),
            (1, 3, 1), (1, 3.25, 2), (1, 3.5, 0), (1, 3.75, 4),
            (2, 0, 0)
        ],
        "sync": [
            (0, i, 0) for i in range(32)
        ],
        "debug": [
            (0, 0, 0), (1, 0, 1), (2, 0, 2), (3, 0, 3), (4, 0, 4)
        ]
    },
    "double": {
        "paradoxx": [
            (0, 0, 0), (0, 0.25, 2), (0, 0.5, 1), (0, 0.75, 3),
            (0, 1, 2), (0, 1.25, 4), (0, 1.5, 3), (0, 1.75, 5),
            (0, 2, 4), (0, 2.25, 6), (0, 2.5, 5), (0, 2.75, 7),
            (0, 3, 6), (0, 3.25, 8), (0, 3.5, 7), (0, 3.75, 9),
            (1, 0, 5), (1, 0.25, 8), (1, 0.5, 7), (1, 0.75, 8),
            (1, 1, 6), (1, 1.25, 9), (1, 1.5, 5), (1, 1.75, 8),
            (1, 2, 9), (1, 2.25, 8), (1, 2.5, 5), (1, 2.75, 6),
            (1, 3, 5), (1, 3.25, 7), (1, 3.5, 6), (1, 3.75, 8),
            (2, 0, 5), (2, 0.25, 8), (2, 0.5, 7), (2, 0.75, 8),
            (2, 1, 6), (2, 1.25, 9), (2, 1.5, 5), (2, 1.75, 8),
            (2, 2, 9), (2, 2.25, 8), (2, 2.5, 5), (2, 2.75, 6),
            (2, 3, 5), (2, 3.25, 7), (2, 3.5, 6), (2, 3.75, 8),
            (3, 0, 5), (3, 0.25, 7), (3, 0.5, 6), (3, 0.75, 9),
            (3, 1, 8), (3, 1.25, 9)
        ]
    }
}

class _settings:
    def __init__(self):
        # visual
        self.startdelay = 1500 # how long it takes from open to first beat of beatmap
        self.scroll = 700 # note scroll speed
        self.autostep = True # automate beatmap
        self.noteskin = '.fallback'
        self.showsteps = False
        
        # sound
        self.volume = SimpleNamespace(hitsound=0.1, song=0.1)
        self.notesounds = True

class _const:
    def __init__(self):
        # map info
        self.BPM = 220 # map bpm
        self.OFFSET = -3.376177
        self.DOUBLE = True # if beatmap is double or not
        self.BEATMAP = testing_beatmaps['double']['paradoxx'] # the actual beatmap
        
        new = []
        for n in self.BEATMAP:
            val = 1000 * (n[1] + 4 * n[0]) * (60 / self.BPM)
            new.append((val, n[2]))
        self.BEATMAP = new
        del(new)
        self.RECEPTORY = 70
        self.JUDGEY = 0.5 * WINDOW_HEIGHT
        self.KEYS = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_SEMICOLON]
        # self.KEYS = [pygame.K_KP_1, pygame.K_KP_7, pygame.K_KP_5, pygame.K_KP_9, pygame.K_KP_3]
        if self.DOUBLE:
            self.COLUMNX = [(WINDOW_WIDTH / 2) + 64 * (i - 4.5) for i in range(10)]
        else:
            self.COLUMNX = [(WINDOW_WIDTH / 2) + 64*(i - 2) for i in range(5)]

settings = _settings()
CONST = _const()

def judge(offset):
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
pygame.mixer.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
pygame.display.set_caption("Stupid It Up Prime")

# 3. Create a clock object to track and control frame rate
clock = pygame.time.Clock()

beatmap = CONST.BEATMAP

parentdir = Path(__file__).parent

receptorpath = parentdir / f'noteskin/{settings.noteskin}/receptors.png'
glowpath = parentdir / f'noteskin/{settings.noteskin}/glow.png'
notepath = parentdir / f'noteskin/{settings.noteskin}/notes.png'
judgepath = parentdir / f'noteskin/{settings.noteskin}/judgements.png'
clappath = parentdir / f'noteskin/{settings.noteskin}/clap.ogg'

song = None

for ext in  ['.mp3', '.ogg']:
    songpath = next(parentdir.rglob('*.ogg'), None)
    if songpath:
        song = pygame.mixer.music.load(str(songpath))
        pygame.mixer.music.set_volume(settings.volume.song)
        print(f'Song file found: {songpath.name}')
        break
if not songpath:
    print('No song file found.')

clap = None

noteskinflag = False

if not receptorpath.is_file():
    noteskinflag = True
    receptorpath = parentdir / f'noteskin/.fallback/receptors.png'
if not glowpath.is_file():
    noteskinflag = True
    glowpath = parentdir / f'noteskin/.fallback/glow.png'
if not notepath.is_file():
    noteskinflag = True
    notepath = parentdir / f'noteskin/.fallback/notes.png'
if not judgepath.is_file():
    noteskinflag = True
    judgepath = parentdir / f'noteskin/.fallback/judgements.png'

# extra things
if clappath.is_file():
    clap = pygame.Sound(str(clappath))
    clap.set_volume(settings.volume.hitsound)

if noteskinflag:
    print(f'Noteskin {settings.noteskin} does not contain required files, reverting to fallback')

del(noteskinflag)

receptorpath = str(receptorpath)
glowpath = str(glowpath)
notepath = str(notepath)
judgepath = str(judgepath)

allreceptors = extract(receptorpath, 64, 64)
receptors = allreceptors[:3]
receptorsblink = allreceptors[4:7]
glow = extract(glowpath, 96, 96)
notes = extract(notepath, 64, 64)
judgements = extract(judgepath, 512, 86)

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
    x = max(((CONST.BPM * t) / 60) % 1, 0)
    return (1 - x)**2

def breakcombo():
    global combo
    if combo > 0:
        combo = 0

class Receptor(pygame.sprite.Sprite):
    def __init__(self, x, y, i, normimg, blinkimg, glowimg):
        super().__init__()
        self.i = i
        self.normimg = normimg
        self.blinkimg = blinkimg
        self.glowimg = glowimg
        self.image = pygame.Surface((96, 96), pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        
        receptor = self.normimg.copy()
        self.image.blit(receptor, (16, 16))
    
    def update(self, fade, hit):
        if fade > 0:
            blink_overlay = self.blinkimg.copy()
            blink_overlay.set_alpha(int(255 * fade))
            self.image.blit(blink_overlay, (16, 16))
        if hit[self.i] > 0:
            glow_overlay = self.glowimg.copy()
            glow_overlay.set_alpha(int(255 * hit[self.i]))
            self.image.blit(glow_overlay, (0, 0))

class Note(pygame.sprite.Sprite):
    def __init__(self, note, noteimg):
        super().__init__()
        self.note = note
        self.visible = True
        self.x = CONST.COLUMNX[self.note[1]]
        self.y = WINDOW_HEIGHT
        self.noteimg = noteimg
        # self.width = self.noteimg.get_width()
        self.height = self.noteimg.get_height()
        self.image = self.noteimg.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self, time):
        timediff = self.note[0] - time
        timediff /= 1000 / settings.scroll
        self.y = timediff + CONST.RECEPTORY
        if self.y < -self.height / 2:
            self.kill()
        if self.y > WINDOW_HEIGHT + self.height / 2:
            self.kill()
        self.rect = self.image.get_rect(center=(self.x, self.y))

class Judgement(pygame.sprite.Sprite):
    def __init__(self, result):
        super().__init__()
        self.judgement = judgements[result]
        self.scale = 1
        self.image = self.judgement.copy().convert_alpha()
        self.width = self.judgement.get_width()
        self.height = self.judgement.get_height()
        self.x = WINDOW_WIDTH / 2
        self.y = CONST.JUDGEY
        self.startfade = 1000
        self.endfade = 1500
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self, last, time):
        dt = time - last
        self.scale = 1 + 0.15 * max(0, min(1, 1 - dt / (1000 * 0.1)))
        self.image = pygame.transform.scale_by(self.judgement.convert_alpha(), self.scale)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        if dt > self.endfade:
            self.kill()
        elif dt > self.startfade:
            alpha = 255 * ((dt - self.endfade) / (self.startfade - self.endfade))
            self.image.set_alpha(alpha)

class ShowStep(pygame.sprite.Sprite):
    def __init__(self, x, y, isdouble, i, normimg, glowimg):
        super().__init__()
        self.i = i
        self.brightness = 1
        self.normimg = normimg
        self.glowimg = glowimg
        self.image = pygame.Surface((96, 96), pygame.SRCALPHA).convert_alpha()
        if isdouble:
            self.x = [x - 160, x - 160, x - 96, x - 32, x - 32, x + 32, x + 32, x + 96, x + 160, x + 160][i]
            self.y = ([y + 64, y - 64, y, y - 64, y + 64] * 2)[i]
        else:
            self.x = [x - 64, x - 64, x, x + 64, x + 64][i]
            self.y = [y + 64, y - 64, y, y - 64, y + 64] * 2[i]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        bgsurface = pygame.Surface((64, 64))
        bgsurface.fill((47, 47, 47))
        self.image.blit(bgsurface, (16, 16))
        receptor = self.normimg.copy()
        self.image.blit(receptor, (16, 16))
    def update(self, hit):
        if hit[self.i] > 0:
            glow_overlay = self.glowimg.copy()
            glow_overlay.set_alpha(int(255 * hit[self.i]))
            self.image.blit(glow_overlay, (0, 0))

monospace = pygame.font.SysFont('Monospace', 20)

running = True
hitlen = 0
if CONST.DOUBLE:
    hitlen = 10
else:
    hitlen = 5

hit = [0] * hitlen
totalnotes = len(CONST.BEATMAP)
combo = 0
maxcombo = 0
judgementlist = [0] * len(judgements)
lastjudgetime = None

judgegroup = pygame.sprite.Group()
notegroup = pygame.sprite.Group()
receptorgroup = pygame.sprite.Group()
showstepgroup = pygame.sprite.Group()

while running:
    dt = clock.tick() / 1000
    gametime = pygame.time.get_ticks() - settings.startdelay
    if gametime % 1000 < 10:
        pygame.mixer.music.play(start=(126.648 + gametime / 1000))
    rawbeat = (gametime * CONST.BPM) / 60000
    measure = rawbeat // 4
    for i in range(hitlen):
        hit[i] = hit[i] - dt * 6
        if hit[i] < 0:
            hit[i] = 0

    result = None
    scoremult = None

    combobreak = None
    
    lane = 10

    if settings.autostep:
        for note in beatmap:
            notetime = note[0]
            offset = gametime - notetime
            if offset > 0:
                keydownevent = pygame.event.Event(pygame.KEYDOWN, key=CONST.KEYS[note[1]])
                pygame.event.post(keydownevent)
                combo += 1
                lastjudgetime = gametime
                newjudge = Judgement(0)
                judgegroup.empty()
                judgegroup.add(newjudge)
                judgementlist[0] += 1
                if settings.notesounds:
                    clap.play()
                beatmap.remove(note)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in CONST.KEYS:
                lane = CONST.KEYS.index(event.key)
        if lane < hitlen:
            hit[lane] = 1
            if not settings.autostep:
                for note in beatmap:
                    if note[1] == lane:
                        notetime = note[0]
                        offset = gametime - notetime
                        if -144 < offset < 250:
                            judgetuple = judge(offset)
                            if not combobreak:
                                result, combobreak, scoremult = judgetuple
                                lastjudgetime = gametime
                                newjudge = Judgement(result)
                                judgegroup.empty()
                                judgegroup.add(newjudge)
                                judgementlist[result] += 1
                                if combobreak is False:
                                    combo += 1
                            if settings.notesounds:
                                clap.play()
                            beatmap.remove(note)
    
    if combo > maxcombo:
        maxcombo = combo
    for note in beatmap:
        notetime = note[0]
        offset = gametime - notetime
        if offset > 250:
            combobreak = True
            beatmap.remove(note)
            lastjudgetime = gametime
            newjudge = Judgement(4)
            judgegroup.empty()
            judgegroup.add(newjudge)
            judgementlist[4] += 1
    
    if combobreak:
        breakcombo()

    screen.fill((0, 0, 0))
    
    fade = fadecalc(gametime)
    
    receptorgroup.empty()
    notegroup.empty()
    showstepgroup.empty()
    
    for i in range(5):
        y = CONST.RECEPTORY
        if CONST.DOUBLE:
            x1 = CONST.COLUMNX[i]
            x2 = CONST.COLUMNX[i + 5]
            newrecep1 = Receptor(x1, y, i, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            newrecep2 = Receptor(x2, y, i + 5, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            receptorgroup.add(newrecep1)
            receptorgroup.add(newrecep2)
            if settings.showsteps:
                newshow1 = ShowStep(WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.75, True, i, lane_normimgs[i], lane_glowimgs[i])
                newshow2 = ShowStep(WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.75, True, i + 5, lane_normimgs[i], lane_glowimgs[i])
                showstepgroup.add(newshow1)
                showstepgroup.add(newshow2)
        else:
            x = CONST.COLUMNX[i]
            newrecep = Receptor(x, y, i, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            receptorgroup.add(newrecep)
    for note in beatmap:
        newnote = Note(note, lane_notes[note[1] % 5])
        notegroup.add(newnote)

    # rendering
    receptorgroup.update(fade, hit)
    receptorgroup.draw(screen)
    notegroup.update(gametime)
    notegroup.draw(screen)
    judgegroup.update(lastjudgetime, gametime)
    judgegroup.draw(screen)
    showstepgroup.update(hit)
    if settings.showsteps:
        if CONST.DOUBLE:
            frame = pygame.rect.Rect(0, 0, 416, 224)
            framepadding = pygame.rect.Rect(0, 0, 384, 192)
            frame.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.75)
            framepadding.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.75)
            pygame.draw.rect(screen, (51, 51, 51), frame)
            pygame.draw.rect(screen, (41, 41, 41), framepadding)
    showstepgroup.draw(screen)
    
    # pygame.draw.line(screen, (255, 255, 255), (0, CONST.RECEPTORY), (WINDOW_WIDTH, CONST.RECEPTORY))
    # pygame.draw.line(screen, (255, 255, 255), (WINDOW_WIDTH/2, 0), (WINDOW_WIDTH/2, WINDOW_HEIGHT))

    
    txtsurf = monospace.render(f'time: {gametime}\nbeat: {round(rawbeat % 4, 2)}\nmeas: {measure}\ncombo:{combo}', True, (255, 255, 255))
    screen.blit(txtsurf, (0, 0))

    # update display
    pygame.display.flip()

print(totalnotes, judgementlist, maxcombo)
score = (995000 * (judgementlist[0] + judgementlist[1] * 0.6 + judgementlist[2] * 0.2 + judgementlist[3] * 0.1) / totalnotes) + (5000 * maxcombo / totalnotes)

score = round(score)
ranklist = ['SSS+', 'SSS', 'SS+', 'SS', 'S+', 'S', 'AAA+', 'AAA', 'AA+', 'AA', 'A+', 'A', 'B', 'C', 'D', 'F']
rankscore = [995000, 990000, 985000, 980000, 975000, 970000, 960000, 950000, 925000, 900000, 825000, 750000, 650000, 550000, 450000]
rank = min(len(ranklist), len(rankscore) + 1) - 1

for i in range(rank):
    if score > rankscore[i]:
        rank = i
        break

rank = ranklist[rank]

print(f'score: {score} rank: {rank}')

pygame.quit()
sys.exit()