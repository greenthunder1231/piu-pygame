# import subprocess
# import os
# subprocess.run(['cls' if os.name == 'nt' else 'clear'], shell = True)

from modules.imports import *

from modules.autostep import *
from modules.const import _const
from modules.files import *
from modules.gameutils import *

print(bracketpriority(2, 4, 5, 7))

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

class _settings:
    def __init__(self):
        # visual
        self.startdelay = 4000 # how long it takes from open to first beat of beatmap
        self.scroll = 700 # note scroll speed
        self.autostep = True # automate beatmap
        self.noteskin = '.fallback'
        self.showsteps = True
        self.showfoot = True
        self.outlinefoot = True
        self.showstepscenter = (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.85)
        
        # sound
        self.volume = SimpleNamespace(hitsound=0.1, song=0.1)
        self.notesounds = False

settings = _settings()
CONST = _const()

# 1. Initialize all imported pygame modules
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
pygame.display.set_caption("Stupid It Up Prime")

# 3. Create a clock object to track and control frame rate
clock = pygame.time.Clock()

parentdir = Path(__file__).parent

receptorpath = parentdir / f'noteskin/{settings.noteskin}/receptors.png'
glowpath = parentdir / f'noteskin/{settings.noteskin}/glow.png'
notepath = parentdir / f'noteskin/{settings.noteskin}/notes.png'
judgepath = parentdir / f'noteskin/{settings.noteskin}/judgements.png'
clappath = parentdir / f'noteskin/{settings.noteskin}/clap.ogg'
panelpath = parentdir / f'noteskin/{settings.noteskin}/panels'
footpath = parentdir / f'assets/shoe.png'
outlinefootpath = parentdir / f'assets/shoe_outline.png'

song = None

for ext in  ['.mp3', '.ogg']:
    songpath = next(parentdir.rglob('*.ogg'), None)
    if songpath:
        songpath = Path(songpath)
        song = pygame.mixer.music.load(str(songpath))
        pygame.mixer.music.set_volume(settings.volume.song)
        print(f'Song file found: {songpath.name}')
        beatmappath = songpath.parent / next(parentdir.rglob('*.ogg'), None)
        if beatmappath:
            CONST.BEATMAP
            print(f'Beatmap synced with song file')
        break
if not songpath:
    print('No song file found.')

clap = None

noteskinflag = False

if not receptorpath.is_file() or noteskinflag:
    noteskinflag = True
    receptorpath = parentdir / f'noteskin/.fallback/receptors.png'
if not glowpath.is_file() or noteskinflag:
    noteskinflag = True
    glowpath = parentdir / f'noteskin/.fallback/glow.png'
if not notepath.is_file() or noteskinflag:
    noteskinflag = True
    notepath = parentdir / f'noteskin/.fallback/notes.png'
if not judgepath.is_file() or noteskinflag:
    noteskinflag = True
    judgepath = parentdir / f'noteskin/.fallback/judgements.png'
if not panelpath.is_dir() or noteskinflag:
    noteskinflag = True
    receptorpath = parentdir / f'noteskin/.fallback/receptors.png'

# extra things
if clappath.is_file():
    clap = pygame.Sound(str(clappath))
    clap.set_volume(settings.volume.hitsound)

if noteskinflag:
    print(f'Noteskin {settings.noteskin} does not contain required files, reverting to fallback')

noteskinflag = False

if settings.outlinefoot:
    if outlinefootpath.is_file():
        footimg = pygame.image.load(outlinefootpath)
    else:
        noteskinflag = True
else:
    if footpath.is_file():
        footimg = pygame.image.load(footpath)
    else:
        noteskinflag = True

if noteskinflag:
    print(f'{'Outlined foot' if settings.outlinefoot else 'Foot'} image could not load, switching')
    try:
        footimg = pygame.image.load(footpath if settings.outlinefoot else outlinefootpath)
    except FileNotFoundError:
        raise FileNotFoundError('No foot in assets folder')
del(noteskinflag)

try:
    panels = [
        pygame.image.load(panelpath / 'panel_ld.png'),
        pygame.image.load(panelpath / 'panel_lu.png'),
        pygame.image.load(panelpath / 'panel_cs.png'),
        pygame.image.load(panelpath / 'panel_ru.png'),
        pygame.image.load(panelpath / 'panel_rd.png')
    ]
except FileNotFoundError:
    raise FileNotFoundError(f'One or more files not found in {panelpath}\nMake sure panels have the correct names and are .png files.\nPanel names are (in the place that the panel is physically):\npanel_lu.png      panel_ru.png\n         panel_cs.png         \npanel_ld.png      panel_rd.png')

for i in range(len(panels)):
    if i == 2:
        panels[i] = pygame.transform.smoothscale(panels[i], (64, 64))
    else:
        panels[i] = pygame.transform.smoothscale(panels[i], (64, 6400/83))

receptorpath = str(receptorpath)
glowpath = str(glowpath)
notepath = str(notepath)
judgepath = str(judgepath)
panelpath = str(panelpath)

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
footimg = pygame.transform.smoothscale(footimg.convert_alpha(), (23.4, 60))

fade = 0

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
        self.image = self.judgement.convert_alpha()
        if self.scale > 1:
            self.image = pygame.transform.scale_by(self.image, self.scale)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        if dt > self.endfade:
            self.kill()
        elif dt > self.startfade:
            alpha = 255 * ((dt - self.endfade) / (self.startfade - self.endfade))
            self.image.set_alpha(alpha)

class ShowStep(pygame.sprite.Sprite):
    def __init__(self, i):
        super().__init__()
        self.i = i
        self.brightness = 1
        self.panelimg = panels[self.i % 5]
        self.width = self.panelimg.get_width()
        self.height = self.panelimg.get_height()
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        xlist = CONST.SHOWSTEPOFFSETX
        ylist = CONST.SHOWSTEPOFFSETY
        self.x = settings.showstepscenter[0] + xlist[i % 5]
        self.y = settings.showstepscenter[1] - ylist[i % 5]
        if CONST.DOUBLE:
            self.x += (96 + 64 / 11) * (2 * (i // 5) - 1)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.bgfill = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        self.bgfill.fill((0, 0, 0))
        self.image.blit(self.bgfill, (0, 0))
        self.panel = self.panelimg.copy()
        self.panel.set_alpha(100)
        self.image.blit(self.panel, (0, 0))
    def update(self, time, pressed, inputs):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        if pressed[self.i]:
            if settings.autostep:
                if pressed[self.i] > time - 60000 / (CONST.BPM * 4):
                    self.panel.set_alpha(255)
            else:
                if inputs[self.i]:
                    self.panel.set_alpha(255)
        self.image.blit(self.bgfill, (0, 0))
        self.image.blit(self.panel, (0, 0))

class ShowFoot(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, foot: int):
        super().__init__()
        self.foot = foot
        if not foot:
            self.footimgog = pygame.transform.flip(footimg, True, False)
        else:
            self.footimgog = footimg
        self.footimg = self.footimgog.copy()
        self.width = self.footimg.get_width()
        self.height = self.footimg.get_height()
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        self.x = x
        self.y = y
        self.image.blit(self.footimg)
        self.rect = self.image.get_rect(center=(settings.showstepscenter[0] + 17 * (2 * foot - 1), settings.showstepscenter[1]))
    def update(self, laststep, *panels, step = False):
        flag = False
        x = y = theta = None
        if self.foot == laststep:
            return
        else:
            if len(panels) == 1:
                b = 0 if panels[0] < 5 else 1
                x = CONST.SHOWSTEPOFFSETX[panels[0] % 5]
                y = CONST.SHOWSTEPOFFSETY[panels[0] % 5]
                theta = 0
                x += (96 + 64 / 11) * (2 * b - 1)
            else:
                brackets = bracketpriority(*panels)
                if not brackets:
                    print(f'Cannot bracket panels {panels}')
                    return
                curbracket = brackets[self.foot]
                x, y, theta = CONST.SHOWSTEPFOOTPTS[curbracket]
                print(curbracket)
                if isinstance(curbracket, (list, tuple)):
                    if not curbracket == (3, 6) and not curbracket == (4, 5):
                        b = 0 if all([i < 5 for i in curbracket]) else 1
                        x += (96 + 64 / 11) * (2 * b - 1)
                else:
                    b = 0 if curbracket < 5 else 1
                    x += (96 + 64 / 11) * (2 * b - 1)
            if x is not None and y is not None:
                self.footimg = pygame.transform.rotate(self.footimgog, theta)
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
                self.image.blit(self.footimg)
                self.rect = self.image.get_rect(center=(self.x + x, self.y - y))

monospace = pygame.font.SysFont('Monospace', 20)

running = True
hitlen = 0
if CONST.DOUBLE:
    hitlen = 10
else:
    hitlen = 5

beatmap = CONST.BEATMAP

laststep = 0
hit = [0] * hitlen
totalnotes = len(beatmap)
combo = 0
maxcombo = 0
judgementlist = [0] * len(judgements)
lastjudgetime = None

judgegroup = pygame.sprite.Group()
notegroup = pygame.sprite.Group()
receptorgroup = pygame.sprite.Group()
showstepgroup = pygame.sprite.Group()
if settings.showfoot:
    footgroup = pygame.sprite.Group()
    lfoot = ShowFoot(settings.showstepscenter[0], settings.showstepscenter[1], 0)
    rfoot = ShowFoot(settings.showstepscenter[0], settings.showstepscenter[1], 1)
    footgroup.add(lfoot)
    footgroup.add(rfoot)

pressed = [None] * hitlen
inputs = [False] * hitlen

while running:
    frameinputs = [False] * hitlen
    noteshit = []
    dt = clock.tick() / 1000
    gametime = pygame.time.get_ticks() + CONST.MEASUREOFFSET * 240000 / CONST.BPM - settings.startdelay
    if gametime % 1000 < 10:
        try:
            pygame.mixer.music.play(start=(-CONST.OFFSET + gametime / 1000))
        except:
            print('Song ended')
            break
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
        F = list(filter(lambda x: 0 <= gametime - x[0] <= 500, beatmap))
        if F:
            print(F)
        for note in F:
            notetime = note[0]
            offset = gametime - notetime
            pressed[note[1]] = gametime
            inputs[note[1]] = True
            frameinputs[note[1]] = True
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
            break
        elif event.type == pygame.KEYDOWN:
            if not settings.autostep:
                if event.key in CONST.KEYS:
                    lane = CONST.KEYS.index(event.key)
                    pressed[lane] = gametime
                    inputs[lane] = True
                    frameinputs[lane] = True
        elif event.type == pygame.KEYUP:
            if not settings.autostep:
                if event.key in CONST.KEYS:
                    inputs[CONST.KEYS.index(event.key)] = False

    for i in range(len(frameinputs)):
        frameinputsi = frameinputs[i]
        if i < hitlen and frameinputsi:
            hit[i] = 1
            if not settings.autostep:
                for note in beatmap:
                    if note[1] == i and not note[1] in noteshit:
                        noteshit.append(note[1])
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
        combo = 0

    screen.fill((0, 0, 0))
    
    fade = fadecalc(gametime, CONST.BPM)
    
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
                newshow1 = ShowStep(i)
                newshow2 = ShowStep(i + 5)
                showstepgroup.add(newshow1)
                showstepgroup.add(newshow2)
        else:
            x = CONST.COLUMNX[i]
            newrecep = Receptor(x, y, i, lane_normimgs[i], lane_blinkimgs[i], lane_glowimgs[i])
            receptorgroup.add(newrecep)
            if settings.showsteps:
                newshow = ShowStep(i)
                showstepgroup.add(newshow)
    for note in beatmap:
        newnote = Note(note, lane_notes[note[1] % 5])
        notegroup.add(newnote)

    # rendering
    # print(f'\r{[round(i) if i else -settings.startdelay for i in pressed]}', end = '')
    receptorgroup.update(fade, hit)
    receptorgroup.draw(screen)
    notegroup.update(gametime)
    notegroup.draw(screen)
    judgegroup.update(lastjudgetime, gametime)
    judgegroup.draw(screen)
    showstepgroup.update(gametime, pressed, inputs)
    if settings.showsteps:
        padding = pygame.rect.Rect(0, 0, (CONST.DOUBLE + 1) * (192 + 128 / 11), 192 + (128 / 11))
        padding.center = settings.showstepscenter
        pygame.draw.rect(screen, (41, 41, 41), padding)
    showstepgroup.draw(screen)
    if settings.showfoot:
        footgroupinput = []
        for i in range(len(frameinputs)):
            if frameinputs[i]:
                footgroupinput.append(i)
        if footgroupinput:
            flag = footgroup.update(laststep, *footgroupinput)
            if not flag:
                laststep = 1 - laststep
        footgroup.draw(screen)
    
    # pygame.draw.line(screen, (255, 255, 255), (0, CONST.RECEPTORY), (WINDOW_WIDTH, CONST.RECEPTORY))
    # pygame.draw.line(screen, (255, 255, 255), (WINDOW_WIDTH/2, 0), (WINDOW_WIDTH/2, WINDOW_HEIGHT))
    
    txtsurf = monospace.render(f'time: {round(gametime)}\nbeat: {round(rawbeat % 4, 2)}\nmeas: {measure}\ncombo:{combo}', True, (255, 255, 255))
    screen.blit(txtsurf, (0, 0))
    if any(frameinputs):
        print(''.join(['\N{FULL BLOCK}\N{FULL BLOCK}' if i else '  ' for i in frameinputs]))

    # update display
    pygame.display.flip()

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

print(f'score: {score}\nrank: {rank}')

pygame.quit()
sys.exit()